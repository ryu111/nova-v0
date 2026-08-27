"""ClaimSpec 0.2.0 的 typed model 與封閉 meta-schema 的執行器。

meta-schema 住在 `規格/語言/ClaimSpec.schema.json`，是資料；這支只執行它，不解釋它。
這一層不碰檔案系統——schema bytes 與 claim bytes 都由呼叫端交進來。

封閉的意思是 `additionalProperties` 一律 false。`status`／`admitted_by`／`passed`
這類自報欄位不在 schema 裡，多寫一個就是 UNKNOWN_FIELD：接受權不在被測者手上。
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

from nova.基礎設施.裁定執行.案例執行 import CaseResult, CaseTerminal
from nova.核心.摘要 import Sha256Ref, canonical_json_bytes, sha256_ref
from nova.核心.識別 import SemanticId
from nova.核心.錯誤 import 核心錯誤

型別對照: dict[str, type | tuple[type, ...]] = {
    "object": dict,
    "array": list,
    "string": str,
    "integer": int,
    "boolean": bool,
    "null": type(None),
}


@dataclass(frozen=True, slots=True)
class ClaimSpecStructuralError:
    """一份 claim 沒能成為 ClaimSpec 的原因，帶跨程序的 ASCII code 與出錯位置。"""

    code: str
    pointer: str
    細節: str


@dataclass(frozen=True, slots=True)
class SubjectContract:
    """題目指定物件的唯一住址：契約、操作與 binding slot 三者都是持久 semantic id。"""

    contract: SemanticId
    operation: SemanticId
    binding_slot: SemanticId


@dataclass(frozen=True, slots=True)
class RunLimits:
    """由外部強制的執行上限。被測者改不動它，所以它不在 subject 手上。"""

    wall_ms: int
    max_output_bytes: int


@dataclass(frozen=True, slots=True)
class EffectDelivery:
    """外部效果的交付語意。v1 只認兩種，`EXACTLY_ONCE` 是做不到的宣稱。"""

    endpoint_id: str
    operation: str
    semantics: str
    原始: dict[str, Any]


@dataclass(frozen=True, slots=True)
class ControlSet:
    """正控與負控。兩邊都至少要有一項——負控是空的等於沒有負控。"""

    positive: tuple[dict[str, Any], ...]
    negative: tuple[dict[str, Any], ...]


@dataclass(frozen=True, slots=True)
class ClaimSpec:
    """一份已通過結構與條件檢查的 claim。digest 是 canonical bytes 的摘要。"""

    claim_id: SemanticId
    revision: int
    subject: SubjectContract
    stimulus: tuple[dict[str, Any], ...]
    observations: tuple[dict[str, Any], ...]
    judge_all_of: tuple[dict[str, Any], ...]
    controls: ControlSet
    run_limits: RunLimits
    isolation: str
    effect_delivery: EffectDelivery | None
    canonical_bytes: bytes
    digest: Sha256Ref


def 合型別(值: object, 宣告: object) -> bool:
    """檢查值符不符合 schema 宣告的型別；bool 先於 int 判，否則 True 會被當成 1。"""
    名們 = 宣告 if isinstance(宣告, list) else [宣告]
    for 名 in 名們:
        期望 = 型別對照[str(名)]
        if 期望 is int and isinstance(值, bool):
            continue
        if isinstance(值, 期望):
            return True
    return False


def 驗_物件(
    值: dict[str, Any], schema: dict[str, Any], 指標: str
) -> ClaimSpecStructuralError | None:
    """物件專屬：必填、未知欄位與逐欄遞迴。"""
    性質: dict[str, Any] = schema.get("properties", {})
    for 必 in schema.get("required", []):
        if 必 not in 值:
            return ClaimSpecStructuralError("MISSING_FIELD", f"{指標}/{必}", "缺必填欄位")
    if schema.get("additionalProperties") is False:
        for 鍵 in 值:
            if 鍵 not in 性質:
                return ClaimSpecStructuralError(
                    "UNKNOWN_FIELD", f"{指標}/{鍵}", "封閉物件不接受未知欄位"
                )
    for 鍵, 子_schema in 性質.items():
        if 鍵 in 值 and (壞 := 驗_結構(值[鍵], 子_schema, f"{指標}/{鍵}")) is not None:
            return 壞
    return None


def 驗_結構(值: object, schema: dict[str, Any], 指標: str = "") -> ClaimSpecStructuralError | None:
    """對照 schema 遞迴檢查一個值，回第一個結構錯誤；全過回 None。"""
    if "type" in schema and not 合型別(值, schema["type"]):
        return ClaimSpecStructuralError("TYPE_MISMATCH", 指標 or "/", f"期望 {schema['type']}")
    if (允許 := schema.get("enum")) is not None and 值 not in 允許:
        return ClaimSpecStructuralError("ENUM_MISMATCH", 指標 or "/", f"只准 {允許}")
    if isinstance(值, dict):
        return 驗_物件(值, schema, 指標)
    if isinstance(值, list):
        下限 = schema.get("minItems")
        if 下限 is not None and len(值) < 下限:
            return ClaimSpecStructuralError("MIN_ITEMS", 指標 or "/", f"至少要 {下限} 項")
        子_schema = schema.get("items")
        if isinstance(子_schema, dict):
            for i, 項 in enumerate(值):
                if (壞 := 驗_結構(項, 子_schema, f"{指標}/{i}")) is not None:
                    return 壞
    return None


class ClaimSpecLoader:
    """把 claim bytes 變成 ClaimSpec，或變成一個帶 typed code 的結構錯誤。"""

    def __init__(self, meta_schema: dict[str, Any], effect_schema: dict[str, Any]) -> None:
        """收下兩份 schema。它們是資料，由呼叫端讀進來——權威層不做 I/O。"""
        self.meta_schema = meta_schema
        self.effect_schema = effect_schema

    def 驗_效果(self, 資料: dict[str, Any]) -> ClaimSpecStructuralError | None:
        """效果交付三條條件規則。順序被釘住：語意先於「該不該有」。

        宣告一個做不到的語意（`EXACTLY_ONCE`）與「這份 claim 根本不該帶效果契約」
        是兩件不同的錯，回同一個 code 會讓 must_fail_exactly 對不上。
        """
        契約 = 資料.get("effect_delivery")
        if 契約 is not None:
            if (壞 := 驗_結構(契約, self.effect_schema, "/effect_delivery")) is not None:
                return 壞
            允許 = self.effect_schema["allowed_semantics"]
            if 契約["semantics"] not in 允許:
                return ClaimSpecStructuralError(
                    "UNSUPPORTED_DELIVERY_SEMANTICS", "/effect_delivery/semantics", f"只准 {允許}"
                )
        前綴 = tuple(self.meta_schema["effect_primitive_prefixes"])
        是效果 = any(str(步["primitive"]).startswith(前綴) for 步 in 資料["stimulus"])
        if 是效果 and 契約 is None:
            return ClaimSpecStructuralError(
                "EFFECT_DELIVERY_REQUIRED", "/effect_delivery", "外部效果原語必須明示交付語意"
            )
        if not 是效果 and 契約 is not None:
            return ClaimSpecStructuralError(
                "EFFECT_DELIVERY_FORBIDDEN", "/effect_delivery", "非效果 claim 不得帶效果契約"
            )
        return None

    def 組(self, 資料: dict[str, Any]) -> ClaimSpec:
        """結構與條件都過了才組成 typed model；這裡不再做任何檢查。"""
        契約 = 資料.get("effect_delivery")
        位元組 = canonical_json_bytes(資料)
        return ClaimSpec(
            claim_id=SemanticId.parse(資料["claim_id"]),
            revision=資料["revision"],
            stimulus=tuple(資料["stimulus"]),
            observations=tuple(資料["observations"]),
            judge_all_of=tuple(資料["judge"]["all_of"]),
            isolation=資料["isolation"],
            subject=SubjectContract(
                contract=SemanticId.parse(資料["subject"]["contract"]),
                operation=SemanticId.parse(資料["subject"]["operation"]),
                binding_slot=SemanticId.parse(資料["subject"]["binding_slot"]),
            ),
            controls=ControlSet(
                positive=tuple(資料["controls"]["positive"]),
                negative=tuple(資料["controls"]["negative"]),
            ),
            run_limits=RunLimits(**資料["run_limits"]),
            effect_delivery=None
            if 契約 is None
            else EffectDelivery(
                endpoint_id=契約["endpoint_id"],
                operation=契約["operation"],
                semantics=契約["semantics"],
                原始=契約,
            ),
            canonical_bytes=位元組,
            digest=sha256_ref(位元組),
        )

    def load(self, 資料: bytes) -> ClaimSpec | ClaimSpecStructuralError:
        """唯一入口：bytes 進，ClaimSpec 或 typed 結構錯誤出，不丟例外給呼叫端。"""
        try:
            物件 = json.loads(資料)
        except json.JSONDecodeError as 誤:
            return ClaimSpecStructuralError("MALFORMED_JSON", "/", str(誤))
        if not isinstance(物件, dict):
            return ClaimSpecStructuralError("TYPE_MISMATCH", "/", "頂層必須是 object")
        if (壞 := 驗_結構(物件, self.meta_schema)) is not None:
            return 壞
        if (壞 := self.驗_效果(物件)) is not None:
            return 壞
        try:
            return self.組(物件)
        except 核心錯誤 as 誤:
            # InvalidSemanticId 也是 核心錯誤 的子類別：一條 except 就夠，
            # 而且 code 直接沿用，不在這裡再翻譯一次。
            return ClaimSpecStructuralError(誤.code, "/", 誤.細節)


@dataclass(frozen=True, slots=True)
class MutationControlRef:
    """事前命名的突變負控參照，帶內容定址與精確期望失敗判準。"""

    control_id: str
    subject_digest: Sha256Ref | str
    semantic_anchor: str
    must_fail_exactly: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class MutationSweepEvidence:
    """突變掃描證據：具名驗收負控與純診斷用的掃描結果分開保存。

    封閉設計：
    - 不得提供 passed、kill_rate_passed、minimum_kill_rate 等自報欄位。
    - decision_basis 留在 evidence 中，由外部裁定器檢驗。
    """

    named_controls: tuple[MutationControlRef, ...]
    named_control_results: dict[str, Any]
    killed_diagnostic_ids: tuple[str, ...]
    survived_diagnostic_ids: tuple[str, ...]
    decision_basis: str


def _驗_dict_結果(control: MutationControlRef, res: dict[str, Any]) -> bool:
    """檢查 dict 格式的突變執行結果。"""
    if "subject_digest" in res:
        期望 = (
            control.subject_digest.hex
            if isinstance(control.subject_digest, Sha256Ref)
            else str(control.subject_digest)
        )
        實際 = (
            res["subject_digest"].hex
            if isinstance(res["subject_digest"], Sha256Ref)
            else str(res["subject_digest"])
        )
        if 實際 != 期望:
            return False
    if "semantic_anchor" in res and res["semantic_anchor"] != control.semantic_anchor:
        return False
    if "killed" in res and not res["killed"]:
        return False
    if "terminal" in res:
        t = res["terminal"]
        t_val = t.value if isinstance(t, CaseTerminal) else str(t)
        if t_val != "CLAIM_REJECTED":
            return False
    return not (
        "failed_predicates" in res
        and set(res["failed_predicates"]) != set(control.must_fail_exactly)
    )


def _驗_具名結果(control: MutationControlRef, res: object) -> bool:
    """檢查單一具名突變的執行結果是否相符且取得直接紅。"""
    if isinstance(res, dict):
        return _驗_dict_結果(control, res)
    if isinstance(res, CaseResult):
        return res.terminal is CaseTerminal.CLAIM_REJECTED and res.failed_predicates == frozenset(
            control.must_fail_exactly
        )
    return res is True


def evaluate_named_controls(evidence: MutationSweepEvidence) -> CaseResult:
    """以事前命名的負控裁定突變驗收結果，禁止以 raw mutation score 作為依據。

    約束：
    - 不得計算除法、百分比或 threshold。
    - decision_basis 合法值只能是 NAMED_CONTROLS，違規回 acceptance_authority_is_named_controls。
    - named control 未取得指定 direct red 或 digest／anchor 不符回 named_control_killed。
    """
    失敗: list[str] = []

    # 1. 檢驗裁定權限依據：只有 NAMED_CONTROLS 具備驗收權
    if evidence.decision_basis != "NAMED_CONTROLS":
        失敗.append("acceptance_authority_is_named_controls")

    # 2. 檢驗每一條事前命名的 control 是否確實取得指定 direct red
    for control in evidence.named_controls:
        if control.control_id not in evidence.named_control_results:
            失敗.append("named_control_killed")
            break
        res = evidence.named_control_results[control.control_id]
        if not _驗_具名結果(control, res):
            失敗.append("named_control_killed")
            break

    if 失敗:
        return CaseResult(
            case_id="mutation.evaluate_named_controls",
            kind="MUTATION_EVALUATION",
            terminal=CaseTerminal.CLAIM_REJECTED,
            failed_predicates=frozenset(失敗),
        )

    return CaseResult(
        case_id="mutation.evaluate_named_controls",
        kind="MUTATION_EVALUATION",
        terminal=CaseTerminal.ACCEPT,
        failed_predicates=frozenset(),
    )
