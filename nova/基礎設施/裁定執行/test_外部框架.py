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

from nova.基礎設施.裁定執行.外部測試框架 import (
    ClaimCatalog,
    判定,
    已知目錄,
    案例識別,
    證據行,
    轉譯,
)
from nova.基礎設施.裁定執行.案例執行 import CaseResult, CaseTerminal, 比對
from nova.核心.錯誤 import CaseFailureKind
from 工具.跑驗收 import 跑驗收, 跑驗收結果

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


def test_比對支援_not_in_not_contains_disjoint() -> None:
    assert 比對("甲", "NOT_IN", ["乙", "丙"]) is True, "NOT_IN 正例應為 True"
    assert 比對("甲", "NOT_IN", ["甲", "乙"]) is False, "NOT_IN 反例應為 False"
    assert 比對("甲乙", "NOT_CONTAINS", "丙") is True, "NOT_CONTAINS 正例應為 True"
    assert 比對("甲乙", "NOT_CONTAINS", "乙") is False, "NOT_CONTAINS 反例應為 False"
    assert 比對({"甲"}, "DISJOINT", {"乙"}) is True, "DISJOINT 正例應為 True"
    assert 比對({"甲"}, "DISJOINT", {"甲"}) is False, "DISJOINT 反例應為 False"
    assert 比對("甲", "NOT_IN", 1) is False, "NOT_IN 右側非容器不得通過"
    assert 比對(1, "NOT_CONTAINS", "甲") is False, "NOT_CONTAINS 左側非字串／集合不得通過"
    assert 比對({"甲"}, "DISJOINT", "乙") is False, "DISJOINT 兩側非集合不得通過"
    assert 比對("甲", "SOUNDS_LIKE", "乙") is False, "未知運算必須 fail closed"


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


def 吞缺檔_跑驗收(參數: list[str], catalog: ClaimCatalog | None = None) -> 跑驗收結果:
    """壞 runner（受測負控 subject）：只吞 CLAIM_FILE_MISSING 這一個 code。"""
    結果 = 跑驗收(參數, catalog=catalog)
    if 結果.code == "CLAIM_FILE_MISSING":
        return 跑驗收結果(exit_code=0, code="OK", 細節="吞掉缺檔")
    return 結果


def test_runner_cli_可重複指定_claim_與_binding(tmp_path: Path) -> None:
    檔1 = tmp_path / "c1.claim.json"
    檔2 = tmp_path / "c2.claim.json"
    檔1.write_text("{}", encoding="utf-8")
    檔2.write_text("{}", encoding="utf-8")
    目錄 = 已知目錄({"claim.one": 檔1, "claim.two": 檔2})

    結果 = 跑驗收(
        ["--claim", "claim.one", "--claim", "claim.two", "--binding", "b1", "--binding", "b2"],
        catalog=目錄,
    )
    assert 結果.exit_code == 1
    assert 結果.code == "UNKNOWN_BINDING_ID"
    assert 結果.細節 == "b1"

    目錄_缺一 = 已知目錄({"claim.one": 檔1, "claim.two": tmp_path / "deleted.claim.json"})
    結果_缺 = 跑驗收(["--claim", "claim.one", "--claim", "claim.two"], catalog=目錄_缺一)
    assert 結果_缺.exit_code != 0
    assert 結果_缺.code == "CLAIM_FILE_MISSING"

    結果_未知 = 跑驗收(["--claim", "claim.one", "--claim", "claim.unknown"], catalog=目錄)
    assert 結果_未知.exit_code != 0
    assert 結果_未知.code == "UNKNOWN_CLAIM_ID"


def test_合法_claim_會編譯計畫並呼叫_subprocess(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """接通後合法 id 必須走 --claim-plan 呼叫外框架。"""
    根 = Path(__file__).resolve().parents[3]
    檔 = 根 / "規格" / "判準" / "保證" / "執行鏈可執行.claim.json"
    目錄 = 已知目錄({"claimspec.execution.chain-is-runnable": 檔})

    呼叫次數 = 0

    def 假_subprocess_run(*args: object, **kwargs: object) -> subprocess.CompletedProcess[str]:
        nonlocal 呼叫次數
        呼叫次數 += 1
        return subprocess.CompletedProcess(args=[], returncode=0)

    monkeypatch.setattr(subprocess, "run", 假_subprocess_run)

    結果 = 跑驗收(["--claim", "claimspec.execution.chain-is-runnable"], catalog=目錄)
    assert 結果.exit_code == 0
    assert 結果.code == "OK"
    assert 呼叫次數 == 1


def test_合法與查無混用_不被提前掩蓋_回_unknown_claim_id(tmp_path: Path) -> None:
    """必加測試格 2：合法 id + 查無 id 不得被提前回 unsupported 掩掉，仍回 UNKNOWN_CLAIM_ID。"""
    檔 = tmp_path / "valid.claim.json"
    檔.write_text("{}", encoding="utf-8")
    目錄 = 已知目錄({"valid.claim": 檔})

    結果1 = 跑驗收(["--claim", "valid.claim", "--claim", "unknown.claim"], catalog=目錄)
    assert 結果1.exit_code == 1
    assert 結果1.code == "UNKNOWN_CLAIM_ID"
    assert 結果1.細節 == "unknown.claim"

    結果2 = 跑驗收(["--claim", "unknown.claim", "--claim", "valid.claim"], catalog=目錄)
    assert 結果2.exit_code == 1
    assert 結果2.code == "UNKNOWN_CLAIM_ID"
    assert 結果2.細節 == "unknown.claim"


def test_合法與缺檔混用_不被提前掩蓋_回_claim_file_missing(tmp_path: Path) -> None:
    """必加測試格 3：合法 id + 缺檔 entry 仍回 CLAIM_FILE_MISSING。"""
    檔 = tmp_path / "valid.claim.json"
    檔.write_text("{}", encoding="utf-8")
    缺檔 = tmp_path / "missing.claim.json"
    目錄 = 已知目錄({"valid.claim": 檔, "missing.claim": 缺檔})

    結果1 = 跑驗收(["--claim", "valid.claim", "--claim", "missing.claim"], catalog=目錄)
    assert 結果1.exit_code == 1
    assert 結果1.code == "CLAIM_FILE_MISSING"

    結果2 = 跑驗收(["--claim", "missing.claim", "--claim", "valid.claim"], catalog=目錄)
    assert 結果2.exit_code == 1
    assert 結果2.code == "CLAIM_FILE_MISSING"


def test_負控_舊版把_claim_json_當_positional_傳給_pytest_必被抓到(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """必加測試格 5：負控 claim-json-as-pytest-positional 證明壞變體必被特定斷言抓到。"""
    根 = Path(__file__).resolve().parents[3]
    檔 = 根 / "規格" / "判準" / "保證" / "執行鏈可執行.claim.json"
    目錄 = 已知目錄({"claimspec.execution.chain-is-runnable": 檔})

    呼叫次數 = 0
    實際指令: list[str] = []

    def 假_subprocess_run(*args: object, **kwargs: object) -> subprocess.CompletedProcess[str]:
        nonlocal 呼叫次數
        呼叫次數 += 1
        實際指令.extend(args[0])  # type: ignore[arg-type]
        return subprocess.CompletedProcess(args=[], returncode=4)

    monkeypatch.setattr(subprocess, "run", 假_subprocess_run)

    結果 = 跑驗收(["--claim", "claimspec.execution.chain-is-runnable"], catalog=目錄)

    assert 結果.code == "FAIL"
    assert 呼叫次數 == 1
    assert "--claim-plan" in 實際指令
    assert str(檔) not in 實際指令


def test_合法_claim_接通後不得再回_unsupported() -> None:
    """合法 claim 必須進入執行鏈，不得停在尚未接線。"""
    根 = Path(__file__).resolve().parents[3]
    檔 = 根 / "規格" / "判準" / "保證" / "執行鏈可執行.claim.json"
    目錄 = 已知目錄({"claimspec.execution.chain-is-runnable": 檔})

    結果 = 跑驗收(["--claim", "claimspec.execution.chain-is-runnable"], catalog=目錄)

    assert 結果.code != "UNSUPPORTED_CLAIM_EXECUTION"


def test_claim_catalog_生產綁定掃描與測試注入() -> None:
    專案根 = Path(__file__).resolve().parents[3]
    目錄 = ClaimCatalog.掃描(專案根)
    assert "toolchain.python-3-14.day-one-probe" in 目錄.條目
    assert 目錄.條目["toolchain.python-3-14.day-one-probe"].is_file()

    狀態, 路徑 = 目錄.解析("toolchain.python-3-14.day-one-probe")
    assert 狀態 == "OK"
    assert 路徑 is not None and 路徑.is_file()

    假目錄 = 已知目錄({"custom.claim": Path("/nonexistent/custom.claim.json")})
    assert "custom.claim" in 假目錄.條目
    狀態假, _ = 假目錄.解析("custom.claim")
    assert 狀態假 == "CLAIM_FILE_MISSING"


def test_catalog_查無_id_回_unknown_claim_id_且_exit_非零() -> None:
    目錄 = 已知目錄({"existing.claim": Path("/tmp/some_file.json")})
    結果 = 跑驗收(["--claim", "nonexistent.claim"], catalog=目錄)
    assert 結果.exit_code != 0
    assert 結果.code == "UNKNOWN_CLAIM_ID"


def test_catalog_有_entry_但檔案缺失回_claim_file_missing_且_exit_非零(tmp_path: Path) -> None:
    缺失路徑 = tmp_path / "missing.claim.json"
    目錄 = 已知目錄({"missing.claim": 缺失路徑})
    結果 = 跑驗收(["--claim", "missing.claim"], catalog=目錄)
    assert 結果.exit_code != 0
    assert 結果.code == "CLAIM_FILE_MISSING"


def test_交叉斷言_查無_id_不能回_claim_file_missing() -> None:
    目錄 = 已知目錄({"existing.claim": Path("/tmp/nonexistent_12345.json")})
    結果 = 跑驗收(["--claim", "未知id"], catalog=目錄)
    assert 結果.code == "UNKNOWN_CLAIM_ID"
    assert 結果.code != "CLAIM_FILE_MISSING"


def test_交叉斷言_檔案缺失不能回_unknown_claim_id(tmp_path: Path) -> None:
    缺失路徑 = tmp_path / "nonexistent_12345.json"
    目錄 = 已知目錄({"已存在.claim": 缺失路徑})
    結果 = 跑驗收(["--claim", "已存在.claim"], catalog=目錄)
    assert 結果.code == "CLAIM_FILE_MISSING"
    assert 結果.code != "UNKNOWN_CLAIM_ID"


def test_交叉斷言_反向變體必紅(tmp_path: Path) -> None:
    缺失路徑 = tmp_path / "nonexistent_12345.json"
    目錄 = 已知目錄({"已存在.claim": 缺失路徑})

    def 誤回缺檔_跑驗收(參數: list[str], catalog: ClaimCatalog | None = None) -> 跑驗收結果:
        結果 = 跑驗收(參數, catalog=catalog)
        if 結果.code == "UNKNOWN_CLAIM_ID":
            return 跑驗收結果(exit_code=1, code="CLAIM_FILE_MISSING", 細節=結果.細節)
        return 結果

    def 誤回未知_跑驗收(參數: list[str], catalog: ClaimCatalog | None = None) -> 跑驗收結果:
        結果 = 跑驗收(參數, catalog=catalog)
        if 結果.code == "CLAIM_FILE_MISSING":
            return 跑驗收結果(exit_code=1, code="UNKNOWN_CLAIM_ID", 細節=結果.細節)
        return 結果

    甲結果 = 誤回缺檔_跑驗收(["--claim", "未知id"], catalog=目錄)
    assert 甲結果.code != "UNKNOWN_CLAIM_ID"

    乙結果 = 誤回未知_跑驗收(["--claim", "已存在.claim"], catalog=目錄)
    assert 乙結果.code != "CLAIM_FILE_MISSING"


def test_缺檔被吞負控(tmp_path: Path) -> None:
    假檔 = tmp_path / "已刪除.claim.json"
    目錄 = 已知目錄({"測試.已刪檔": 假檔})

    正常結果 = 跑驗收(["--claim", "測試.已刪檔"], catalog=目錄)
    assert 正常結果.exit_code != 0
    assert 正常結果.code == "CLAIM_FILE_MISSING"

    壞結果 = 吞缺檔_跑驗收(["--claim", "測試.已刪檔"], catalog=目錄)
    assert 壞結果.exit_code == 0
    assert 壞結果.code == "OK"

    查無結果 = 吞缺檔_跑驗收(["--claim", "根本不存在的id"], catalog=目錄)
    assert 查無結果.exit_code != 0
    assert 查無結果.code == "UNKNOWN_CLAIM_ID"

    assert 壞結果.exit_code != 正常結果.exit_code


def test_保留既有_positional_pytest_路徑與_exit_code_透傳() -> None:
    結果 = 跑驗收(["nova/基礎設施/裁定執行/test_外部框架.py", "-k", "test_判定裡根本沒有_xfail"])
    assert 結果.exit_code == 0
    assert 結果.code == "OK"
