"""跑一格 case：拿觀察、套判準、回終態。**機械執行，不做政策判斷。**

這支住在 `基礎設施/裁定執行` 而不是 `權威/判準`，是分層閘逼出來的——
`外部測試框架.py` 需要跑 case，而 `基礎設施` 不得 import `權威`。
目錄名早就講清楚了：「裁定**執行**」是機械跑，「判準」是政策。
一格怎麼跑、算不算紅，是機械；三色矩陣合起來算不算通過，是政策。

四種獨立結果在這裡只是**照實回報**，不算負控成立——那個判斷在 `權威/判準` 那邊。
"""

from __future__ import annotations

import enum
from dataclasses import dataclass
from typing import Any, Protocol

from nova.基礎設施.裁定執行.參考執行封套 import 腳本失敗


class CaseTerminal(enum.Enum):
    """一格 case 的終態。ACCEPT 之外的每一種都與 `CaseFailureKind` 逐字對應。"""

    ACCEPT = "ACCEPT"
    CLAIM_REJECTED = "CLAIM_REJECTED"
    UNBOUND_SUBJECT = "UNBOUND_SUBJECT"
    UNSUPPORTED_ISOLATION = "UNSUPPORTED_ISOLATION"
    HARNESS_ERROR = "HARNESS_ERROR"
    HARNESS_LIMIT = "HARNESS_LIMIT"


獨立結果 = frozenset(
    {
        CaseTerminal.UNBOUND_SUBJECT,
        CaseTerminal.UNSUPPORTED_ISOLATION,
        CaseTerminal.HARNESS_ERROR,
        CaseTerminal.HARNESS_LIMIT,
    }
)


class 執行環境(Protocol):
    """交出一格 case 的觀察值，或交出一個獨立結果。它不做判斷。"""

    def 觀察(self, case: dict[str, Any]) -> dict[str, Any] | 腳本失敗:
        """回觀察值 dict，或回 腳本失敗 表示這一格根本沒驗到。"""
        ...


@dataclass(frozen=True, slots=True)
class CaseResult:
    """一格的結果。`failed_predicates` 是**直接紅的證據**，不得被上層改寫。"""

    case_id: str
    kind: str
    terminal: CaseTerminal
    failed_predicates: frozenset[str]
    細節: str = ""


def 比對(左: object, 運算: str, 右: object) -> bool:
    """封閉的運算集合。未知運算回 False 而不是當成通過。"""
    if 運算 == "EQUALS":
        return 左 == 右
    if 運算 == "NOT_EQUALS":
        return 左 != 右
    if 運算 == "LESS_THAN":
        return isinstance(左, int) and isinstance(右, int) and 左 < 右
    return False


def 取值(邊: dict[str, Any], 觀察: dict[str, Any]) -> object:
    """判準的一邊要嘛引用觀察，要嘛是字面值。"""
    if "observation" in 邊:
        return 觀察.get(str(邊["observation"]))
    return 邊.get("const")


def run_case(
    case: dict[str, Any], predicates: tuple[dict[str, Any], ...], runtime: 執行環境
) -> CaseResult:
    """跑一格：拿觀察、逐條套判準。獨立結果直接回，不進判準。"""
    出 = runtime.觀察(case)
    if isinstance(出, 腳本失敗):
        return CaseResult(
            case_id=str(case["case_id"]),
            kind=str(case["kind"]),
            terminal=CaseTerminal(出.種類.value),
            failed_predicates=frozenset(),
            細節="沒有驗到——這不是負控成立",
        )
    紅 = frozenset(
        str(條["predicate_id"])
        for 條 in predicates
        if not 比對(取值(條["left"], 出), str(條["operator"]), 取值(條["right"], 出))
    )
    return CaseResult(
        case_id=str(case["case_id"]),
        kind=str(case["kind"]),
        terminal=CaseTerminal.ACCEPT if not 紅 else CaseTerminal.CLAIM_REJECTED,
        failed_predicates=紅,
    )
