"""把 ClaimSpec 編譯成帶型別的 TestPlan，或編不出來時給一個 typed 失敗。

`plan_digest` 綁的是**四個輸入**：claim、原語目錄、綁定清單、隔離供給。
只綁 claim 的話，換一份 catalog 或換一台機器編出來的 plan 會有相同 digest——
那等於宣稱「在別的環境上驗的是同一件事」，而那句話沒有人證明過。

編不出來的原因**不壓成同一個字串**。`UNBOUND_SUBJECT` 與 `UNSUPPORTED_ISOLATION`
是**獨立結果**不是「負控成功抓到錯」：前者是根本沒綁到受測對象，後者是這台機器
做不到宣告的隔離。把它們跟 `TYPE_MISMATCH` 混成一個 code，就分不出「規格寫錯」
與「這裡驗不了」。
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from nova.基礎設施.裁定執行.原語 import 原語目錄, 外部效果
from nova.核心.摘要 import Sha256Ref, canonical_json_bytes, sha256_ref
from nova.核心.識別 import SemanticId
from nova.權威.判準.保證規格模型 import ClaimSpec

值型別 = frozenset({"STRING", "INTEGER", "BOOLEAN", "DURATION_MS", "BYTES"})
數值型別 = frozenset({"INTEGER", "DURATION_MS", "BYTES"})
被測者 = "SUBJECT"


@dataclass(frozen=True, slots=True)
class CompileFailure:
    """編不出 plan 的原因。code 跨程序，細節給人看。"""

    code: str
    細節: str


@dataclass(frozen=True, slots=True)
class 綁定清單:
    """binding slot → 確切的 capability digest。沒有這一份就不知道在測誰。"""

    manifest_id: str
    revision: int
    綁定: dict[str, str]

    @property
    def digest(self) -> Sha256Ref:
        """Digest 進 plan_digest：換一份綁定就是換受測對象。"""
        主體 = {
            "manifest_id": self.manifest_id,
            "revision": self.revision,
            "bindings": sorted(self.綁定.items()),
        }
        return sha256_ref(canonical_json_bytes(主體))


@dataclass(frozen=True, slots=True)
class 隔離供給:
    """這台機器實際做得到的隔離模式。做不到就回 typed 拒絕，不得靜默降級。"""

    模式: frozenset[str]

    @property
    def digest(self) -> Sha256Ref:
        """Digest 進 plan_digest：隔離條件不同，驗到的就不是同一件事。"""
        return sha256_ref(canonical_json_bytes({"modes": sorted(self.模式)}))


@dataclass(frozen=True, slots=True)
class TestPlan:
    """編好的計畫。digest 綁四個輸入，重編兩次必須相同。"""

    claim_id: SemanticId
    revision: int
    catalog_digest: str
    binding_digest: str
    isolation_digest: str
    cases: tuple[dict[str, Any], ...]
    canonical_bytes: bytes
    digest: Sha256Ref

    @property
    def 案數(self) -> int:
        """Actual 一格，加上每個正控與負控各一格。"""
        return len(self.cases)


def 查原語(spec: ClaimSpec, 目錄: 原語目錄) -> CompileFailure | None:
    """Stimulus 用到的每個原語都要在目錄裡；目錄外的原語是沒人審過的動作。"""
    for 步 in spec.stimulus:
        if 目錄.查(str(步["primitive"])) is None:
            return CompileFailure("UNKNOWN_PRIMITIVE", str(步["primitive"]))
    return None


def 驗效果條件(spec: ClaimSpec, 目錄: 原語目錄) -> CompileFailure | None:
    """外部效果與交付契約互為條件——這裡由**目錄宣告的種類**決定，不猜原語名字。"""
    有效果 = any(
        (項 := 目錄.查(str(步["primitive"]))) is not None and 項.kind == 外部效果
        for 步 in spec.stimulus
    )
    if 有效果 and spec.effect_delivery is None:
        return CompileFailure("EFFECT_DELIVERY_REQUIRED", "外部效果原語必須明示交付語意")
    if not 有效果 and spec.effect_delivery is not None:
        return CompileFailure("EFFECT_DELIVERY_FORBIDDEN", "非效果 claim 不得帶效果契約")
    return None


def 驗觀察(spec: ClaimSpec) -> CompileFailure | None:
    """觀察的型別要在封閉集合裡；被測者自報的時間量不能拿來證外部期限。"""
    for 觀 in spec.observations:
        型 = str(觀["type"])
        if 型 not in 值型別:
            return CompileFailure("UNKNOWN_OBSERVATION_TYPE", f"{觀['observation_id']}:{型}")
        if str(觀["source"]) == 被測者 and 型 == "DURATION_MS":
            return CompileFailure(
                "UNTRUSTED_OBSERVATION",
                f"{觀['observation_id']} 由被測者自報，不能證明外部期限",
            )
    return None


def 常量型別(值: object) -> str:
    """字面值的型別。數字刻意回 INTEGER 並與其他數值型別相容——`< 60000` 是合法的時間比較。"""
    if isinstance(值, bool):
        return "BOOLEAN"
    if isinstance(值, int):
        return "INTEGER"
    return "STRING"


def 相容(甲: str, 乙: str) -> bool:
    """同型別相容；數值型別之間**只有一邊是字面值時**才相容。"""
    return 甲 == 乙 or ({甲, 乙} <= 數值型別 and "INTEGER" in {甲, 乙})


def 邊的型別(邊: dict[str, Any], 型們: dict[str, str]) -> str | CompileFailure:
    """判準的一邊要嘛引用觀察，要嘛是字面值；引用不存在的觀察是編譯錯誤。"""
    if "observation" in 邊:
        名 = str(邊["observation"])
        if 名 not in 型們:
            return CompileFailure("UNKNOWN_OBSERVATION", 名)
        return 型們[名]
    return 常量型別(邊.get("const"))


def 驗判準型別(spec: ClaimSpec) -> CompileFailure | None:
    """兩邊型別不相容就擋——DURATION_MS 與 BYTES 都是整數，不擋就會相等。"""
    型們 = {str(觀["observation_id"]): str(觀["type"]) for 觀 in spec.observations}
    for 條 in spec.judge_all_of:
        左 = 邊的型別(條["left"], 型們)
        右 = 邊的型別(條["right"], 型們)
        for 邊 in (左, 右):
            if isinstance(邊, CompileFailure):
                return 邊
        assert isinstance(左, str)
        assert isinstance(右, str)
        if not 相容(左, 右):
            return CompileFailure("TYPE_MISMATCH", f"{條['predicate_id']}：{左} vs {右}")
    return None


def 組案(spec: ClaimSpec) -> tuple[dict[str, Any], ...]:
    """一份 plan 恰有一格 actual，加上每個正控與負控各一格。"""
    案: list[dict[str, Any]] = [{"kind": "ACTUAL", "case_id": "actual"}]
    案 += [
        {
            "kind": "POSITIVE",
            "case_id": str(項["control_id"]),
            "subject_binding": str(項["subject_binding"]),
        }
        for 項 in spec.controls.positive
    ]
    案 += [
        {
            "kind": "NEGATIVE",
            "case_id": str(項["control_id"]),
            "faulty_subject": str(項["faulty_subject"]),
            "must_fail_exactly": sorted(項["must_fail_exactly"]),
        }
        for 項 in spec.controls.negative
    ]
    return tuple(案)


def compile_claim(
    spec: ClaimSpec, catalog: 原語目錄, binding: 綁定清單, offer: 隔離供給
) -> TestPlan | CompileFailure:
    """唯一入口。任一檢查不過就回 typed 失敗，不丟例外也不壓成同一個 code。"""
    if spec.subject.binding_slot.value not in binding.綁定:
        return CompileFailure("UNBOUND_SUBJECT", spec.subject.binding_slot.value)
    if spec.isolation not in offer.模式:
        return CompileFailure("UNSUPPORTED_ISOLATION", spec.isolation)
    for 檢 in (查原語(spec, catalog), 驗效果條件(spec, catalog), 驗觀察(spec), 驗判準型別(spec)):
        if 檢 is not None:
            return 檢
    案 = 組案(spec)
    主體 = {
        "claim": spec.digest.hex,
        "catalog": catalog.digest.hex,
        "binding": binding.digest.hex,
        "isolation": offer.digest.hex,
        "cases": list(案),
    }
    位元組 = canonical_json_bytes(主體)
    return TestPlan(
        claim_id=spec.claim_id,
        revision=spec.revision,
        catalog_digest=catalog.digest.hex,
        binding_digest=binding.digest.hex,
        isolation_digest=offer.digest.hex,
        cases=案,
        canonical_bytes=位元組,
        digest=sha256_ref(位元組),
    )
