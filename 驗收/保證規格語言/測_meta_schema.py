"""ClaimSpec 0.2.0 封閉 meta-schema 的黑箱測試：六個事前固定的無效 instance。

這六個不是隨手挑的壞例子，是計畫在 Task 6 就寫死的固定負控——每一個都對應一種
「規格看起來還在，但保證已經被掏空」的寫法：自報 `passed`、把負控清空、把時限
寫成字串、外部效果沒有交付語意、非效果 claim 卻帶效果契約、宣告做不到的
`EXACTLY_ONCE`。
"""

import copy
import json
import pathlib
from typing import Any

import pytest

from nova.權威.判準.保證規格模型 import ClaimSpec, ClaimSpecLoader, ClaimSpecStructuralError

專案根 = pathlib.Path(__file__).resolve().parent.parent.parent
語言目錄 = 專案根 / "規格" / "語言"
效果契約檔 = 專案根 / "規格" / "介面" / "效果契約.schema.json"


def 取載入器() -> ClaimSpecLoader:
    """meta-schema 是資料，載入器只執行——I/O 在這裡做，權威層不碰檔案系統。"""
    return ClaimSpecLoader(
        meta_schema=json.loads((語言目錄 / "ClaimSpec.schema.json").read_text(encoding="utf-8")),
        effect_schema=json.loads(效果契約檔.read_text(encoding="utf-8")),
    )


def validate_claim(instance: dict[str, Any]) -> ClaimSpec | ClaimSpecStructuralError:
    """把 instance 編碼成 bytes 再走正式入口，不給測試走後門。"""
    return 取載入器().load(json.dumps(instance, ensure_ascii=False).encode("utf-8"))


def deep_merge(底: dict[str, Any], 變更: dict[str, Any]) -> dict[str, Any]:
    """把變更疊到底上；dict 遞迴合併，其餘直接覆蓋。"""
    出 = copy.deepcopy(底)
    for 鍵, 值 in 變更.items():
        if isinstance(值, dict) and isinstance(出.get(鍵), dict):
            出[鍵] = deep_merge(出[鍵], 值)
        else:
            出[鍵] = copy.deepcopy(值)
    return 出


def 有效_effect_contract() -> dict[str, Any]:
    """一份語意合法的效果交付契約——用來證明「合法但不該出現」也要被擋。"""
    return {
        "endpoint_id": "endpoint.example",
        "operation": "send",
        "semantics": "AT_LEAST_ONCE_IDEMPOTENT",
        "intent_schema": "規格/介面/意圖.schema.json",
        "idempotency_key": ["work_id", "attempt"],
        "attempt_policy": {"max_attempts": 3},
        "receipt_schema": "規格/介面/回條.schema.json",
        "success_postcondition": {"observation": "status", "const": "OK"},
        "duplicate_policy": "IGNORE",
        "uncertain_terminal": "UNCERTAIN",
    }


def 最小_判準() -> dict[str, Any]:
    """一條恆等判準：這份最小 claim 的用途是當負控的底，不是示範判準怎麼寫。"""
    return {
        "all_of": [
            {
                "predicate_id": "verdict_is_ok",
                "operator": "EQUALS",
                "left": {"observation": "code"},
                "right": {"const": "OK"},
            }
        ]
    }


def 最小_控制組() -> dict[str, Any]:
    """正控與負控各一項。兩邊都不得為空——空的負控等於沒有負控。"""
    return {
        "positive": [
            {
                "control_id": "repository-tree",
                "subject_binding": "REPOSITORY_SCAN",
                "expected_terminal": "ACCEPT",
            }
        ],
        "negative": [
            {
                "control_id": "broken-subject",
                "faulty_subject": "驗收/工具鏈/fixtures/錯置_repository.py",
                "expected_terminal": "CLAIM_REJECTED",
                "must_fail_exactly": ["verdict_is_ok"],
            }
        ],
    }


@pytest.fixture
def 最小_claim() -> dict[str, Any]:
    """一份會通過的最小 claim。每個負控都只在它身上動一處。"""
    return {
        "$schema": "../../語言/ClaimSpec.schema.json",
        "claimspec_version": "0.2.0",
        "claim_id": "example.minimal-claim",
        "revision": 1,
        "supersedes": None,
        "statement": "最小可通過的 claim，只為了讓負控每次只動一處。",
        "sources": [
            {"source_id": "plan.01.task.6", "kind": "PLAN_TASK", "locator": "docs/計畫/01"}
        ],
        "primitive_catalog": {"catalog_id": "architecture-checker.v1", "digest": None},
        "subject": {
            "contract": "engineering-checker.v1",
            "operation": "check-file",
            "binding_slot": "engineering-checker.repository",
        },
        "parameters": {},
        "setup": [],
        "stimulus": [{"primitive": "architecture.check_file", "arguments": {"path": "x"}}],
        "observations": [
            {
                "observation_id": "code",
                "source": "STIMULUS_RESULT",
                "path": "code",
                "type": "STRING",
            }
        ],
        "judge": 最小_判準(),
        "controls": 最小_控制組(),
        "run_limits": {"wall_ms": 60000, "max_output_bytes": 1048576},
        "isolation": "COOPERATIVE_PROCESS",
        "effect_delivery": None,
        "evidence": {"retain": ["code"], "record_kind": "CHECK_VERDICT"},
        "feedback": {"to_candidate": "NONE"},
        "cleanup": [],
    }


def 測試_最小_claim_本身要能過(最小_claim: dict[str, Any]) -> None:
    # 沒有這一格，六個負控可以靠「什麼都拒絕」全綠。
    結果 = validate_claim(最小_claim)
    assert isinstance(結果, ClaimSpec), 結果


@pytest.mark.parametrize(
    ("變更", "錯碼"),
    [
        ({"passed": True}, "UNKNOWN_FIELD"),
        ({"controls": {"positive": [], "negative": []}}, "MIN_ITEMS"),
        ({"run_limits": {"wall_ms": "500"}}, "TYPE_MISMATCH"),
        (
            {"stimulus": [{"primitive": "effect.send", "arguments": {}}], "effect_delivery": None},
            "EFFECT_DELIVERY_REQUIRED",
        ),
        ({"effect_delivery": 有效_effect_contract()}, "EFFECT_DELIVERY_FORBIDDEN"),
        (
            {"effect_delivery": deep_merge(有效_effect_contract(), {"semantics": "EXACTLY_ONCE"})},
            "UNSUPPORTED_DELIVERY_SEMANTICS",
        ),
    ],
)
def 測試_結構錯誤拒絕(最小_claim: dict[str, Any], 變更: dict[str, Any], 錯碼: str) -> None:
    結果 = validate_claim(deep_merge(最小_claim, 變更))
    assert isinstance(結果, ClaimSpecStructuralError), 結果
    assert 結果.code == 錯碼


def 測試_執行欄位改變摘要改變(最小_claim: dict[str, Any]) -> None:
    原 = validate_claim(最小_claim)
    assert isinstance(原, ClaimSpec)
    改 = validate_claim(deep_merge(最小_claim, {"run_limits": {"wall_ms": 60001}}))
    assert isinstance(改, ClaimSpec)
    assert 改.digest != 原.digest


def 測試_鍵順序不改摘要(最小_claim: dict[str, Any]) -> None:
    # digest 是 canonical bytes 的摘要，不是檔案位元組的摘要——換個鍵順序不算改規格。
    反 = dict(reversed(list(最小_claim.items())))
    原 = validate_claim(最小_claim)
    倒 = validate_claim(反)
    assert isinstance(原, ClaimSpec)
    assert isinstance(倒, ClaimSpec)
    assert 倒.digest == 原.digest


def 測試_已存在的三份工程_claim_都能載入() -> None:
    # 正控：schema 若寫得跟現實對不上，這一格會紅。
    載入器 = 取載入器()
    檔們 = sorted((專案根 / "規格").rglob("*.claim.json"))
    assert 檔們
    for 檔 in 檔們:
        結果 = 載入器.load(檔.read_bytes())
        assert isinstance(結果, ClaimSpec), f"{檔.name}: {結果}"


def 去掉(底: dict[str, Any], 路徑: tuple[str, ...]) -> dict[str, Any]:
    """回一份少了指定欄位的複本——deep_merge 只能疊加，刪不掉東西。"""
    出 = copy.deepcopy(底)
    節: Any = 出
    for 段 in 路徑[:-1]:
        節 = 節[段]
    del 節[路徑[-1]]
    return 出


@pytest.mark.parametrize(
    "路徑",
    [
        ("claim_id",),
        ("controls", "positive"),
        ("run_limits", "max_output_bytes"),
        ("judge", "all_of"),
    ],
)
def 測試_缺必填欄位會紅(最小_claim: dict[str, Any], 路徑: tuple[str, ...]) -> None:
    # required 不檢查的話，「少寫一段」與「寫對了」在這道閘看起來一樣。
    結果 = validate_claim(去掉(最小_claim, 路徑))
    assert isinstance(結果, ClaimSpecStructuralError), 結果
    assert 結果.code == "MISSING_FIELD"
    assert 結果.pointer.endswith(路徑[-1])


def 測試_布林不算整數(最小_claim: dict[str, Any]) -> None:
    # Python 的 bool 是 int 的子類別：不特判的話 wall_ms: true 會被當成合法的 1。
    結果 = validate_claim(deep_merge(最小_claim, {"run_limits": {"wall_ms": True}}))
    assert isinstance(結果, ClaimSpecStructuralError), 結果
    assert 結果.code == "TYPE_MISMATCH"


def 測試_陣列裡的項目也要逐一檢查(最小_claim: dict[str, Any]) -> None:
    壞 = deep_merge(最小_claim, {"sources": [{"source_id": "x", "kind": "PLAN_TASK"}]})
    結果 = validate_claim(壞)
    assert isinstance(結果, ClaimSpecStructuralError), 結果
    assert 結果.code == "MISSING_FIELD"
    assert 結果.pointer == "/sources/0/locator"


def 測試_負控為空是_MIN_ITEMS(最小_claim: dict[str, Any]) -> None:
    # 只清空負控。固定負控 2 同時清空正負兩邊，正控會先紅而蓋住這一格。
    結果 = validate_claim(deep_merge(最小_claim, {"controls": {"negative": []}}))
    assert isinstance(結果, ClaimSpecStructuralError), 結果
    assert 結果.code == "MIN_ITEMS"
    assert 結果.pointer == "/controls/negative"


def 測試_做不到的語意先於該不該有效果契約(最小_claim: dict[str, Any]) -> None:
    # 一份效果 claim 帶 EXACTLY_ONCE：兩條規則都可以說話，順序決定 code。
    # 不釘住的話，將來 must_fail_exactly 會無聲對錯。
    效果 = deep_merge(
        最小_claim,
        {
            "stimulus": [{"primitive": "effect.send", "arguments": {}}],
            "effect_delivery": deep_merge(有效_effect_contract(), {"semantics": "EXACTLY_ONCE"}),
        },
    )
    結果 = validate_claim(效果)
    assert isinstance(結果, ClaimSpecStructuralError), 結果
    assert 結果.code == "UNSUPPORTED_DELIVERY_SEMANTICS"


def 測試_合法的效果_claim_會過(最小_claim: dict[str, Any]) -> None:
    # 防恆真：效果那三條規則不能靠「凡是帶 effect_delivery 就拒絕」而全綠。
    合法 = deep_merge(
        最小_claim,
        {
            "stimulus": [{"primitive": "effect.send", "arguments": {}}],
            "effect_delivery": 有效_effect_contract(),
        },
    )
    結果 = validate_claim(合法)
    assert isinstance(結果, ClaimSpec), 結果
    assert 結果.effect_delivery is not None
    assert 結果.effect_delivery.semantics == "AT_LEAST_ONCE_IDEMPOTENT"


def 測試_claim_id_不合語義識別規則會紅(最小_claim: dict[str, Any]) -> None:
    結果 = validate_claim(deep_merge(最小_claim, {"claim_id": "工作.完成"}))
    assert isinstance(結果, ClaimSpecStructuralError), 結果
    assert 結果.code == "INVALID_SEMANTIC_ID"
