"""指定突變而非擊殺率的驗收測試。

只有事前命名、內容定址且帶 must_fail_exactly 的 control 能決定驗收結果。
raw mutation sweep 的 killed／survived 數量只能成為診斷 evidence。
不得計算或使用 mutation kill rate 作為 ACCEPT／CLAIM_REJECTED 的依據。
"""

import json
import pathlib
from dataclasses import FrozenInstanceError

import pytest

from nova.基礎設施.裁定執行.案例執行 import CaseResult, CaseTerminal
from nova.核心.摘要 import sha256_ref
from nova.權威.判準.保證規格模型 import (
    ClaimSpec,
    ClaimSpecLoader,
    MutationControlRef,
    MutationSweepEvidence,
    evaluate_named_controls,
)

預期最小負控數 = 2


def 建立_守衛_control() -> MutationControlRef:
    """建立一個標準的具名守衛突變參照。"""
    return MutationControlRef(
        control_id="guard-mutation-narrow",
        subject_digest=sha256_ref("def 收窄(值): return 值".encode()),
        semantic_anchor="nova/核心/工具鏈守衛.py::收窄",
        must_fail_exactly=("mutation_tests_are_copied",),
    )


def 以_raw_mutation_rate_裁定(
    evidence: MutationSweepEvidence,
    門檻: float = 0.8,
) -> CaseResult:
    """壞 evaluator（受測負控 subject）：越權以 raw mutation rate 比例裁定。

    真的讀取 killed_diagnostic_ids 與 survived_diagnostic_ids 計算擊殺率比例，
    完全無視事前命名的 named_controls。
    若擊殺率達門檻則給 ACCEPT，未達則給 CLAIM_REJECTED。
    """
    已殺數 = len(evidence.killed_diagnostic_ids)
    存活數 = len(evidence.survived_diagnostic_ids)
    總數 = 已殺數 + 存活數
    擊殺率 = (已殺數 / 總數) if 總數 > 0 else 0.0
    if 擊殺率 >= 門檻:
        return CaseResult(
            case_id="mutation.evaluate_by_raw_mutation_rate",
            kind="MUTATION_EVALUATION",
            terminal=CaseTerminal.ACCEPT,
            failed_predicates=frozenset(),
        )
    return CaseResult(
        case_id="mutation.evaluate_by_raw_mutation_rate",
        kind="MUTATION_EVALUATION",
        terminal=CaseTerminal.CLAIM_REJECTED,
        failed_predicates=frozenset({"acceptance_authority_is_named_controls"}),
    )


def 判定_裁定器違規(
    受測結果: CaseResult,
    期望結果: CaseResult,
) -> set[str]:
    """比對受測 evaluator 的終態與標準期望，抓出裁定權限違規。"""
    違規 = set()
    if 受測結果.terminal != 期望結果.terminal:
        違規.add("acceptance_authority_is_named_controls")
    return 違規


def 測試_防恆真_表面三分之一但具名守衛被殺則接受() -> None:
    """防恆真一：1 個 named guard mutation 正確被殺、2 個 diagnostic mutants 存活，必須 ACCEPT。"""
    守衛 = 建立_守衛_control()
    證據 = MutationSweepEvidence(
        named_controls=(守衛,),
        named_control_results={
            "guard-mutation-narrow": {
                "killed": True,
                "terminal": CaseTerminal.CLAIM_REJECTED,
                "failed_predicates": frozenset({"mutation_tests_are_copied"}),
                "subject_digest": 守衛.subject_digest,
                "semantic_anchor": 守衛.semantic_anchor,
            }
        },
        killed_diagnostic_ids=("diag-1",),
        survived_diagnostic_ids=("diag-2", "diag-3"),
        decision_basis="NAMED_CONTROLS",
    )
    結果 = evaluate_named_controls(證據)
    assert 結果.terminal is CaseTerminal.ACCEPT
    assert 結果.failed_predicates == frozenset()


def 測試_防恆真_診斷全滅為零比三但具名守衛被殺仍接受() -> None:
    """防恆真二：named control 正確被殺，即使 diagnostic sweep 為 0/3，仍必須 ACCEPT。"""
    守衛 = 建立_守衛_control()
    證據 = MutationSweepEvidence(
        named_controls=(守衛,),
        named_control_results={
            "guard-mutation-narrow": {
                "killed": True,
                "terminal": CaseTerminal.CLAIM_REJECTED,
                "failed_predicates": frozenset({"mutation_tests_are_copied"}),
                "subject_digest": 守衛.subject_digest,
                "semantic_anchor": 守衛.semantic_anchor,
            }
        },
        killed_diagnostic_ids=(),
        survived_diagnostic_ids=("diag-1", "diag-2", "diag-3"),
        decision_basis="NAMED_CONTROLS",
    )
    結果 = evaluate_named_controls(證據)
    assert 結果.terminal is CaseTerminal.ACCEPT
    assert 結果.failed_predicates == frozenset()


def 測試_防恆真_診斷全殺為三比三但具名守衛未殺則拒絕() -> None:
    """防恆真三：named control 未取得 direct red，即使 sweep 3/3 仍須 CLAIM_REJECTED。"""
    守衛 = 建立_守衛_control()
    證據 = MutationSweepEvidence(
        named_controls=(守衛,),
        named_control_results={
            "guard-mutation-narrow": {
                "killed": False,
                "terminal": CaseTerminal.ACCEPT,
                "failed_predicates": frozenset(),
                "subject_digest": 守衛.subject_digest,
                "semantic_anchor": 守衛.semantic_anchor,
            }
        },
        killed_diagnostic_ids=("diag-1", "diag-2", "diag-3"),
        survived_diagnostic_ids=(),
        decision_basis="NAMED_CONTROLS",
    )
    結果 = evaluate_named_controls(證據)
    assert 結果.terminal is CaseTerminal.CLAIM_REJECTED
    assert 結果.failed_predicates == frozenset({"named_control_killed"})


def 測試_固定負控一_三分之一門檻拒絕為越權() -> None:
    """固定負控一：one-of-three-threshold-rejects。

    情境一：named control 已殺、raw sweep 1/3。
    正確 reference 結果為 ACCEPT；
    壞 evaluator 以 1/3 未達門檻（0.8）越權判定 CLAIM_REJECTED。
    違規判準 exact fail: acceptance_authority_is_named_controls。
    """
    守衛 = 建立_守衛_control()
    證據 = MutationSweepEvidence(
        named_controls=(守衛,),
        named_control_results={
            "guard-mutation-narrow": {
                "killed": True,
                "terminal": CaseTerminal.CLAIM_REJECTED,
                "failed_predicates": frozenset({"mutation_tests_are_copied"}),
                "subject_digest": 守衛.subject_digest,
                "semantic_anchor": 守衛.semantic_anchor,
            }
        },
        killed_diagnostic_ids=("diag-1",),
        survived_diagnostic_ids=("diag-2", "diag-3"),
        decision_basis="NAMED_CONTROLS",
    )
    參考結果 = evaluate_named_controls(證據)
    assert 參考結果.terminal is CaseTerminal.ACCEPT

    壞結果 = 以_raw_mutation_rate_裁定(證據)
    assert 壞結果.terminal is CaseTerminal.CLAIM_REJECTED
    assert 壞結果.terminal != 參考結果.terminal

    違規 = 判定_裁定器違規(壞結果, 參考結果)
    assert 違規 == {"acceptance_authority_is_named_controls"}


def 測試_固定負控二_三比三分數核准為越權() -> None:
    """固定負控二：three-of-three-score-grants。

    情境二：named control 未殺、raw sweep 3/3。
    正確 reference 結果為 CLAIM_REJECTED（named_control_killed）；
    壞 evaluator 以 3/3 = 100% 達標越權判定 ACCEPT。
    違規判準 exact fail: acceptance_authority_is_named_controls。
    """
    守衛 = 建立_守衛_control()
    證據 = MutationSweepEvidence(
        named_controls=(守衛,),
        named_control_results={
            "guard-mutation-narrow": {
                "killed": False,
                "terminal": CaseTerminal.ACCEPT,
                "failed_predicates": frozenset(),
                "subject_digest": 守衛.subject_digest,
                "semantic_anchor": 守衛.semantic_anchor,
            }
        },
        killed_diagnostic_ids=("diag-1", "diag-2", "diag-3"),
        survived_diagnostic_ids=(),
        decision_basis="NAMED_CONTROLS",
    )
    參考結果 = evaluate_named_controls(證據)
    assert 參考結果.terminal is CaseTerminal.CLAIM_REJECTED
    assert 參考結果.failed_predicates == frozenset({"named_control_killed"})

    壞結果 = 以_raw_mutation_rate_裁定(證據)
    assert 壞結果.terminal is CaseTerminal.ACCEPT
    assert 壞結果.terminal != 參考結果.terminal

    違規 = 判定_裁定器違規(壞結果, 參考結果)
    assert 違規 == {"acceptance_authority_is_named_controls"}


def 測試_附屬防護_自報_raw_mutation_score_被拒絕() -> None:
    """附加 metadata guard：decision_basis 若為 RAW_MUTATION_SCORE 必須被拒絕。"""
    守衛 = 建立_守衛_control()
    證據 = MutationSweepEvidence(
        named_controls=(守衛,),
        named_control_results={
            "guard-mutation-narrow": {
                "killed": True,
                "terminal": CaseTerminal.CLAIM_REJECTED,
                "failed_predicates": frozenset({"mutation_tests_are_copied"}),
                "subject_digest": 守衛.subject_digest,
                "semantic_anchor": 守衛.semantic_anchor,
            }
        },
        killed_diagnostic_ids=("diag-1",),
        survived_diagnostic_ids=(),
        decision_basis="RAW_MUTATION_SCORE",
    )
    結果 = evaluate_named_controls(證據)
    assert 結果.terminal is CaseTerminal.CLAIM_REJECTED
    assert 結果.failed_predicates == frozenset({"acceptance_authority_is_named_controls"})


def 測試_摘要與錨點不符不能通過() -> None:
    """subject_digest 與 semantic_anchor 不符時不能只靠相同 control_id 通過。"""
    守衛 = 建立_守衛_control()
    證據_錯摘要 = MutationSweepEvidence(
        named_controls=(守衛,),
        named_control_results={
            "guard-mutation-narrow": {
                "killed": True,
                "terminal": CaseTerminal.CLAIM_REJECTED,
                "failed_predicates": frozenset({"mutation_tests_are_copied"}),
                "subject_digest": sha256_ref(b"wrong digest content"),
                "semantic_anchor": 守衛.semantic_anchor,
            }
        },
        killed_diagnostic_ids=(),
        survived_diagnostic_ids=(),
        decision_basis="NAMED_CONTROLS",
    )
    結果_錯摘要 = evaluate_named_controls(證據_錯摘要)
    assert 結果_錯摘要.terminal is CaseTerminal.CLAIM_REJECTED
    assert 結果_錯摘要.failed_predicates == frozenset({"named_control_killed"})

    證據_錯錨點 = MutationSweepEvidence(
        named_controls=(守衛,),
        named_control_results={
            "guard-mutation-narrow": {
                "killed": True,
                "terminal": CaseTerminal.CLAIM_REJECTED,
                "failed_predicates": frozenset({"mutation_tests_are_copied"}),
                "subject_digest": 守衛.subject_digest,
                "semantic_anchor": "other/path.py::other_func",
            }
        },
        killed_diagnostic_ids=(),
        survived_diagnostic_ids=(),
        decision_basis="NAMED_CONTROLS",
    )
    結果_錯錨點 = evaluate_named_controls(證據_錯錨點)
    assert 結果_錯錨點.terminal is CaseTerminal.CLAIM_REJECTED
    assert 結果_錯錨點.failed_predicates == frozenset({"named_control_killed"})


def 測試_證據形狀不可有自報欄位() -> None:
    """MutationSweepEvidence 不得出現 passed / kill_rate 等越權欄位。"""
    欄位名們 = MutationSweepEvidence.__match_args__
    assert "passed" not in 欄位名們
    assert "kill_rate_passed" not in 欄位名們
    assert "minimum_kill_rate" not in 欄位名們


def 測試_參照物件不可變() -> None:
    """MutationControlRef 必須是 frozen dataclass。"""
    守衛 = 建立_守衛_control()
    with pytest.raises(FrozenInstanceError):
        守衛.control_id = "other"  # type: ignore[misc]


def 測試_指定突變_claim_檔符合結構且可載入() -> None:
    """確保新增的指定突變 claim 檔能被 ClaimSpecLoader 載入為合法的 ClaimSpec。"""
    專案根 = pathlib.Path(__file__).resolve().parent.parent.parent
    載入器 = ClaimSpecLoader(
        meta_schema=json.loads(
            (專案根 / "規格" / "語言" / "ClaimSpec.schema.json").read_text(encoding="utf-8")
        ),
        effect_schema=json.loads(
            (專案根 / "規格" / "介面" / "效果契約.schema.json").read_text(encoding="utf-8")
        ),
    )
    claim_路徑 = 專案根 / "規格" / "判準" / "保證" / "指定突變而非擊殺率.claim.json"
    結果 = 載入器.load(claim_路徑.read_bytes())
    assert isinstance(結果, ClaimSpec), f"載入失敗：{結果}"
    assert 結果.claim_id.value == "claimspec.mutation.named-control-only"
    assert len(結果.controls.negative) >= 預期最小負控數


def 測試_claim_負控定位點可解析並執行() -> None:
    """確保 claim 宣告的每一個 negative locator 都能被解析為真實 callable 並執行成功。"""
    專案根 = pathlib.Path(__file__).resolve().parent.parent.parent
    claim_路徑 = 專案根 / "規格" / "判準" / "保證" / "指定突變而非擊殺率.claim.json"
    claim_資料 = json.loads(claim_路徑.read_text(encoding="utf-8"))
    負控清單 = claim_資料["controls"]["negative"]
    assert len(負控清單) >= 預期最小負控數

    for 負控 in 負控清單:
        locator = 負控["faulty_subject"]
        檔案路徑字串, 符號名 = locator.split("::")
        assert (專案根 / 檔案路徑字串).exists(), f"負控檔案不存在：{檔案路徑字串}"

        目標函式 = globals().get(符號名)
        assert callable(目標函式), f"負控定位點不可執行或不存在：{locator}"

        # 真正執行該負控函式
        目標函式()
