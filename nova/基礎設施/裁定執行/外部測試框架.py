"""把 ClaimSpec 的 case 曝光成 pytest item——**只轉譯，不改判定**。

pytest 是外部工具：它可以決定怎麼顯示，不能決定什麼算通過。

兩條硬線寫在這裡而不是散在別處：

1. **四種獨立結果一律是 pytest 的 error，不是 fail、更不是 xfail。**
   xfail 的意思是「預期會失敗所以沒關係」，而 `HARNESS_ERROR` 的意思是「根本沒驗到」。
   把後者顯示成前者，就是把沒驗到說成驗過了。做法是**在 `setup()` 就丟例外**——
   pytest 只有 setup 期間的例外才算 error，runtest 期間的算 fail。這個位置是刻意的。
2. **negative 依宣告直接紅時，那一格對 pytest 是 pass**（它做了它該做的事），
   但證據裡必須留著 direct red。只看 pytest 綠而證據裡沒有紅過，等於沒有負控。

`判定` 這個枚舉裡**沒有 XFAIL**。不是「我們不回傳它」，是它不存在——
只要那個值存在，遲早有人在某個分支用到它。
"""

from __future__ import annotations

import enum
import json
from pathlib import Path
from typing import Any

import pytest

from nova.基礎設施.裁定執行.參考執行封套 import 參考封套, 腳本失敗
from nova.基礎設施.裁定執行.案例執行 import CaseResult, CaseTerminal, run_case, 獨立結果
from nova.核心.錯誤 import CaseFailureKind

負控 = "NEGATIVE"


class 判定(enum.Enum):
    """外部框架能表達的三種結果。刻意沒有 XFAIL。"""

    PASS = "PASS"
    FAIL = "FAIL"
    ERROR = "ERROR"


class 沒有驗到(Exception):
    """獨立結果：這一格根本沒驗到。在 setup 丟出，pytest 才會算成 error。"""


def 案例識別(claim_id: str, case: dict[str, Any]) -> str:
    """Pytest id 的三種形狀，逐字照計畫 01 Task 9 的 Interfaces。"""
    if case["kind"] == "ACTUAL":
        return f"{claim_id}::actual"
    return f"{claim_id}::{str(case['kind']).lower()}::{case['case_id']}"


def 轉譯(結果: CaseResult, 宣告: dict[str, Any]) -> 判定:
    """把 case 終態轉成外部框架的判定。這裡不做任何裁定，只做對照。"""
    if 結果.terminal in 獨立結果:
        return 判定.ERROR
    if 結果.kind == 負控:
        期望 = frozenset(宣告.get("must_fail_exactly", ()))
        對 = 結果.terminal is CaseTerminal.CLAIM_REJECTED and 結果.failed_predicates == 期望
        return 判定.PASS if 對 else 判定.FAIL
    return 判定.PASS if 結果.terminal is CaseTerminal.ACCEPT else 判定.FAIL


def 證據行(plan_digest: str, 結果: CaseResult) -> str:
    """一格一行 JSON。failed_predicates 排序後輸出，讓兩次跑的證據逐位元組相同。"""
    return json.dumps(
        {
            "plan_digest": plan_digest,
            "case_id": 結果.case_id,
            "kind": 結果.kind,
            "terminal": 結果.terminal.value,
            "failed_predicates": sorted(結果.failed_predicates),
        },
        ensure_ascii=False,
        sort_keys=True,
    )


def 組封套(設定: dict[str, Any]) -> 參考封套:
    """目前只有參考封套。真後端進來時這裡換成 registry，判定邏輯不動。"""
    狀況 = 設定.get("負控狀況")
    return 參考封套(
        正常=bool(設定.get("正常", True)),
        負控狀況=腳本失敗(CaseFailureKind(狀況)) if 狀況 else None,
    )


class ClaimCaseItem(pytest.Item):
    """一格 case 一個 pytest item。判定在 setup 就決定，runtest 只負責報告。"""

    def __init__(
        self, *, case: dict[str, Any], 計畫: dict[str, Any], name: str, parent: pytest.Collector
    ) -> None:
        """收下這一格與它所屬的計畫；執行推遲到 setup。"""
        super().__init__(name=name, parent=parent)
        self.case = case
        self.計畫 = 計畫
        self.結果: CaseResult | None = None

    def setup(self) -> None:
        """在這裡跑，因為獨立結果必須是 error——那只有 setup 期間的例外做得到。"""
        封套 = 組封套(self.計畫.get("runtime", {}))
        self.結果 = run_case(self.case, tuple(self.計畫["predicates"]), 封套)
        路徑 = self.config.getoption("--claim-evidence")
        if 路徑:
            with Path(str(路徑)).open("a", encoding="utf-8") as 檔:
                檔.write(證據行(str(self.計畫["plan_digest"]), self.結果) + "\n")
        if 轉譯(self.結果, self.case) is 判定.ERROR:
            raise 沒有驗到(f"{self.name}：{self.結果.terminal.value}——這不是負控成立")

    def runtest(self) -> None:
        """判定已經在 setup 決定；這裡只把 FAIL 變成 pytest 的失敗。"""
        assert self.結果 is not None
        if 轉譯(self.結果, self.case) is 判定.FAIL:
            raise AssertionError(
                f"{self.name}：終態 {self.結果.terminal.value}、"
                f"紅在 {sorted(self.結果.failed_predicates)}"
            )

    def reportinfo(self) -> tuple[Path, int, str]:
        """讓 pytest 顯示得出這一格屬於哪份計畫。"""
        return self.path, 0, self.name


class ClaimPlanFile(pytest.File):
    """一份 `.plan.json` 收成若干個 case item。"""

    def collect(self) -> list[ClaimCaseItem]:
        """逐格產生 item，id 用 claim_id 而不是檔名——換檔名不該換 case 身分。"""
        計畫 = json.loads(self.path.read_text(encoding="utf-8"))
        return [
            ClaimCaseItem.from_parent(
                self, name=案例識別(str(計畫["claim_id"]), 格), case=格, 計畫=計畫
            )
            for 格 in 計畫["cases"]
        ]


def pytest_addoption(parser: pytest.Parser) -> None:
    """`--claim-plan` 直接指定一份計畫；`--claim-evidence` 指定證據落盤位置。"""
    組 = parser.getgroup("claimspec")
    組.addoption("--claim-plan", action="append", default=[], help="要跑的 .plan.json")
    組.addoption("--claim-evidence", action="store", default=None, help="證據 JSONL 落點")


def pytest_collect_file(parent: pytest.Collector, file_path: Path) -> ClaimPlanFile | None:
    """副檔名是 `.plan.json` 的一律收；不是的回 None，不干擾別人的收集。"""
    if file_path.name.endswith(".plan.json"):
        return ClaimPlanFile.from_parent(parent, path=file_path)
    return None


def pytest_collection_modifyitems(
    session: pytest.Session, config: pytest.Config, items: list[pytest.Item]
) -> None:
    """把 `--claim-plan` 指定的計畫也收進來。"""
    for 路徑 in config.getoption("--claim-plan"):
        檔 = ClaimPlanFile.from_parent(session, path=Path(str(路徑)))
        items.extend(檔.collect())
