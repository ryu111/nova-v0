"""三色矩陣的外層 meta-test：actual 綠、positive 綠、**negative 必須直接紅**。

這裡的「綠」與「紅」是兩層：**外層這些測試綠**，代表**內層的 negative 真的紅了**、
而且紅在指定的 predicate 上。外層綠而內層沒紅過，等於什麼都沒驗到——
那正是這個 repo 說的「宣稱有把關而沒有」。

四種獨立結果（UNBOUND_SUBJECT／UNSUPPORTED_ISOLATION／HARNESS_ERROR／HARNESS_LIMIT）
**不算負控成立**。negative subject 自己爆掉不是「成功抓到錯」，是根本沒驗到。
"""

import pytest

from nova.基礎設施.裁定執行.原語 import 內部, 原語, 原語目錄
from nova.基礎設施.裁定執行.參考執行封套 import 參考封套, 腳本失敗
from nova.核心.摘要 import sha256_ref
from nova.核心.識別 import SemanticId
from nova.核心.錯誤 import CaseFailureKind
from nova.權威.判準.保證規格執行 import CaseTerminal, run_plan
from nova.權威.判準.保證規格模型 import ClaimSpec, ControlSet, RunLimits, SubjectContract
from nova.權威.判準.保證規格編譯 import TestPlan, compile_claim, 綁定清單, 隔離供給


def 編出計畫(恆真: bool = False, 負控預期: list[str] | None = None) -> TestPlan:
    """把一份最小 claim 編成 plan。恆真時判準永遠成立，用來模擬 constant-true。"""
    判準 = {
        "predicate_id": "verdict_is_ok",
        "operator": "EQUALS" if not 恆真 else "NOT_EQUALS",
        "left": {"observation": "code"},
        "right": {"const": "OK" if not 恆真 else "這個值永遠不會出現"},
    }
    規格 = ClaimSpec(
        claim_id=SemanticId.parse("example.sensitivity"),
        revision=1,
        subject=SubjectContract(
            contract=SemanticId.parse("reference-envelope.v1"),
            operation=SemanticId.parse("run"),
            binding_slot=SemanticId.parse("execution-envelope.reference"),
        ),
        stimulus=({"primitive": "envelope.run", "arguments": {}},),
        observations=(
            {
                "observation_id": "code",
                "source": "STIMULUS_RESULT",
                "path": "code",
                "type": "STRING",
            },
        ),
        judge_all_of=(判準,),
        controls=ControlSet(
            positive=(
                {"control_id": "p1", "subject_binding": "REFERENCE", "expected_terminal": "ACCEPT"},
            ),
            negative=(
                {
                    "control_id": "n1",
                    "faulty_subject": "驗收/工具鏈/fixtures/超長函式.py",
                    "expected_terminal": "CLAIM_REJECTED",
                    "must_fail_exactly": 負控預期 or ["verdict_is_ok"],
                },
            ),
        ),
        run_limits=RunLimits(wall_ms=60000, max_output_bytes=1048576),
        isolation="COOPERATIVE_PROCESS",
        effect_delivery=None,
        canonical_bytes=b"{}",
        digest=sha256_ref(b"example.sensitivity"),
    )
    出 = compile_claim(
        規格,
        原語目錄("ref.v1", (原語("envelope.run", 內部, "STRING"),)),
        綁定清單("ref", 1, {"execution-envelope.reference": "sha256:ref"}),
        隔離供給(frozenset({"COOPERATIVE_PROCESS"})),
    )
    assert isinstance(出, TestPlan), 出
    return 出


def test_negative_必須由指定_predicate_拒絕() -> None:
    計畫 = 編出計畫()
    結果 = run_plan(計畫, 參考封套(正常=True))
    assert 結果.actual.terminal is CaseTerminal.ACCEPT
    assert 結果.positive[0].terminal is CaseTerminal.ACCEPT
    assert 結果.negative[0].terminal is CaseTerminal.CLAIM_REJECTED
    assert 結果.negative[0].failed_predicates == frozenset({"verdict_is_ok"})
    assert 結果.通過


def test_constant_true_判準讓敏感度轉紅() -> None:
    # 固定負控一：判準恆真時 negative 會變成 ACCEPT，三色矩陣就塌了。
    計畫 = 編出計畫(恆真=True)
    結果 = run_plan(計畫, 參考封套(正常=True))
    assert 結果.negative[0].terminal is CaseTerminal.ACCEPT
    assert not 結果.通過
    assert any("negative" in 句 for 句 in 結果.問題)


def test_negative_自己爆掉不算抓到錯() -> None:
    # 固定負控二：subject crash 是 HARNESS_ERROR，不是負控成立。
    計畫 = 編出計畫()
    結果 = run_plan(計畫, 參考封套(正常=True, 負控狀況=腳本失敗(CaseFailureKind.HARNESS_ERROR)))
    assert 結果.negative[0].terminal is CaseTerminal.HARNESS_ERROR
    assert not 結果.通過


@pytest.mark.parametrize(
    "種",
    [
        CaseFailureKind.UNBOUND_SUBJECT,
        CaseFailureKind.UNSUPPORTED_ISOLATION,
        CaseFailureKind.HARNESS_LIMIT,
    ],
)
def test_四種獨立結果都不算負控成立(種: CaseFailureKind) -> None:
    計畫 = 編出計畫()
    結果 = run_plan(計畫, 參考封套(正常=True, 負控狀況=腳本失敗(種)))
    assert 結果.negative[0].terminal.value == 種.value
    assert not 結果.通過


def test_actual_紅了整份就不通過() -> None:
    計畫 = 編出計畫()
    結果 = run_plan(計畫, 參考封套(正常=False))
    assert 結果.actual.terminal is CaseTerminal.CLAIM_REJECTED
    assert not 結果.通過


def test_negative_紅錯_predicate_不算通過() -> None:
    # 紅了但紅在別的地方，等於這條負控沒有守住它宣稱守住的東西。
    計畫 = 編出計畫(負控預期=["另一條"])
    結果 = run_plan(計畫, 參考封套(正常=True))
    assert 結果.negative[0].terminal is CaseTerminal.CLAIM_REJECTED
    assert not 結果.通過


def test_終態_union_與核心的失敗種類同源() -> None:
    # 兩份枚舉各自維護，遲早有一邊多一個而沒人發現。
    assert {項.value for 項 in CaseTerminal} == {"ACCEPT"} | {項.value for 項 in CaseFailureKind}
