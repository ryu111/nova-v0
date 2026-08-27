"""外部框架只轉譯、不改判定。

pytest 是**外部工具**。它可以決定怎麼顯示，不能決定什麼算通過。
兩條硬線：
1. 四種獨立結果一律是 pytest 的 **error**，不是 fail、更不是 xfail——
   xfail 的意思是「預期會失敗所以沒關係」，而 HARNESS_ERROR 的意思是「根本沒驗到」。
   把後者顯示成前者，就是把沒驗到說成驗過了。
2. negative 依宣告直接紅時，那一格對 pytest 是 **pass**（它做了它該做的事），
   但**證據裡必須留著 direct red**——只看 pytest 綠而證據裡沒有紅過，等於沒有負控。
"""

import json
import subprocess
import sys
from pathlib import Path

import pytest

from nova.基礎設施.裁定執行.外部測試框架 import 判定, 案例識別, 證據行, 轉譯
from nova.基礎設施.裁定執行.案例執行 import CaseResult, CaseTerminal
from nova.核心.錯誤 import CaseFailureKind

外掛 = "nova.基礎設施.裁定執行.外部測試框架"


def 結果(terminal: CaseTerminal, kind: str = "NEGATIVE", 紅: set[str] | None = None) -> CaseResult:
    return CaseResult(
        case_id="n1", kind=kind, terminal=terminal, failed_predicates=frozenset(紅 or set())
    )


@pytest.mark.parametrize(
    "種",
    [
        CaseFailureKind.UNBOUND_SUBJECT,
        CaseFailureKind.UNSUPPORTED_ISOLATION,
        CaseFailureKind.HARNESS_ERROR,
        CaseFailureKind.HARNESS_LIMIT,
    ],
)
def test_harness_error_不能變成_xfail(種: CaseFailureKind) -> None:
    出 = 轉譯(結果(CaseTerminal(種.value)), {"must_fail_exactly": ["p"]})
    assert 出 is 判定.ERROR


def test_判定裡根本沒有_xfail() -> None:
    # 光是「不回傳 xfail」不夠：只要那個值存在，就有人會在某個分支用到它。
    assert {項.name for 項 in 判定} == {"PASS", "FAIL", "ERROR"}


def test_negative_依宣告直接紅是_pass() -> None:
    出 = 轉譯(結果(CaseTerminal.CLAIM_REJECTED, 紅={"p"}), {"must_fail_exactly": ["p"]})
    assert 出 is 判定.PASS


def test_negative_紅錯地方是_fail() -> None:
    出 = 轉譯(結果(CaseTerminal.CLAIM_REJECTED, 紅={"別的"}), {"must_fail_exactly": ["p"]})
    assert 出 is 判定.FAIL


def test_negative_被接受是_fail() -> None:
    出 = 轉譯(結果(CaseTerminal.ACCEPT), {"must_fail_exactly": ["p"]})
    assert 出 is 判定.FAIL


def test_actual_被拒是_fail_不是_xfail() -> None:
    出 = 轉譯(結果(CaseTerminal.CLAIM_REJECTED, kind="ACTUAL", 紅={"p"}), {})
    assert 出 is 判定.FAIL


def test_證據行留著_direct_red() -> None:
    # 只看 pytest 綠而證據裡沒有紅過，等於沒有負控。
    行 = 證據行("sha256:abc", 結果(CaseTerminal.CLAIM_REJECTED, 紅={"p"}))
    紀錄 = json.loads(行)
    assert 紀錄["plan_digest"] == "sha256:abc"
    assert 紀錄["terminal"] == "CLAIM_REJECTED"
    assert 紀錄["failed_predicates"] == ["p"]


def test_案例識別的三種形狀() -> None:
    assert 案例識別("a.b", {"kind": "ACTUAL", "case_id": "actual"}) == "a.b::actual"
    assert 案例識別("a.b", {"kind": "POSITIVE", "case_id": "p1"}) == "a.b::positive::p1"
    assert 案例識別("a.b", {"kind": "NEGATIVE", "case_id": "n1"}) == "a.b::negative::n1"


def 寫計畫(根: Path, 正常: bool = True, 負控狀況: str | None = None) -> Path:
    計畫 = {
        "plan_digest": "sha256:test",
        "claim_id": "example.framework",
        "predicates": [
            {
                "predicate_id": "verdict_is_ok",
                "operator": "EQUALS",
                "left": {"observation": "code"},
                "right": {"const": "OK"},
            }
        ],
        "cases": [
            {"kind": "ACTUAL", "case_id": "actual"},
            {"kind": "POSITIVE", "case_id": "p1", "subject_binding": "REFERENCE"},
            {
                "kind": "NEGATIVE",
                "case_id": "n1",
                "faulty_subject": "x",
                "must_fail_exactly": ["verdict_is_ok"],
            },
        ],
        "runtime": {"kind": "reference", "正常": 正常, "負控狀況": 負控狀況},
    }
    檔 = 根 / "x.plan.json"
    檔.write_text(json.dumps(計畫, ensure_ascii=False), encoding="utf-8")
    return 檔


def 跑_pytest(檔: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "pytest", "-q", "-p", 外掛, str(檔)],
        capture_output=True,
        text=True,
        check=False,
        cwd=Path(__file__).resolve().parents[3],
    )


def test_三色計畫在_pytest_下是三個_item(tmp_path: Path) -> None:
    出 = 跑_pytest(寫計畫(tmp_path))
    assert 出.returncode == 0, 出.stdout + 出.stderr
    assert "3 passed" in 出.stdout


def test_harness_error_在_pytest_下是_error_不是_xfail(tmp_path: Path) -> None:
    出 = 跑_pytest(寫計畫(tmp_path, 負控狀況="HARNESS_ERROR"))
    assert 出.returncode != 0
    assert "error" in 出.stdout.lower()
    assert "xfail" not in 出.stdout.lower()
