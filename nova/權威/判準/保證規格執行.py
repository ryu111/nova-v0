"""跑一份 TestPlan 的三色矩陣，並且**保留 negative 的直接紅**。

兩層顏色不能混：外層 meta-test 綠，代表**內層的 negative 真的紅過**、而且紅在
指定的 predicate 上。外層綠而內層沒紅過，等於什麼都沒驗到。

四種獨立結果（`UNBOUND_SUBJECT`／`UNSUPPORTED_ISOLATION`／`HARNESS_ERROR`／
`HARNESS_LIMIT`）**一律不算負控成立**。negative subject 自己爆掉不是「成功抓到錯」，
是根本沒驗到——把它算成成功，就是把沒驗到說成驗過了。
"""

from __future__ import annotations

import enum
from dataclasses import dataclass
from typing import Any, Protocol

from nova.基礎設施.裁定執行.參考執行封套 import 腳本失敗
from nova.權威.判準.保證規格編譯 import TestPlan

實際 = "ACTUAL"
正控 = "POSITIVE"
負控 = "NEGATIVE"


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


@dataclass(frozen=True, slots=True)
class PlanResult:
    """整份計畫的三色結果。`通過` 只有三色都對才成立。"""

    actual: CaseResult
    positive: tuple[CaseResult, ...]
    negative: tuple[CaseResult, ...]
    問題: tuple[str, ...]

    @property
    def 通過(self) -> bool:
        """有任何一條問題就不通過——不看比例，不看多數。"""
        return not self.問題


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


def 查三色(
    actual: CaseResult,
    positive: tuple[CaseResult, ...],
    negative: tuple[CaseResult, ...],
    negative_cases: tuple[dict[str, Any], ...],
) -> tuple[str, ...]:
    """三色矩陣的判定。每一種不對都要說清楚是哪一種，不壓成一句「失敗」。"""
    問題: list[str] = []
    if actual.terminal is not CaseTerminal.ACCEPT:
        問題.append(f"actual 必須 ACCEPT，實際 {actual.terminal.value}")
    for 格 in positive:
        if 格.terminal is not CaseTerminal.ACCEPT:
            問題.append(f"positive {格.case_id} 必須 ACCEPT，實際 {格.terminal.value}")
    for 格, 宣告 in zip(negative, negative_cases, strict=True):
        期望 = frozenset(宣告["must_fail_exactly"])
        if 格.terminal in 獨立結果:
            問題.append(f"negative {格.case_id} 回 {格.terminal.value}——那是獨立結果，不算負控成立")
        elif 格.terminal is not CaseTerminal.CLAIM_REJECTED:
            問題.append(f"negative {格.case_id} 必須直接紅，實際 {格.terminal.value}")
        elif 格.failed_predicates != 期望:
            問題.append(
                f"negative {格.case_id} 紅在 {sorted(格.failed_predicates)}，"
                f"宣告的是 {sorted(期望)}"
            )
    return tuple(問題)


def run_plan(plan: TestPlan, runtime: 執行環境) -> PlanResult:
    """唯一入口：跑完三色再判定。判定不看比例，任一格不對就不通過。"""
    跑 = {
        kind: [run_case(格, plan.predicates, runtime) for 格 in plan.取(kind)]
        for kind in (實際, 正控, 負控)
    }
    actual = 跑[實際][0]
    positive = tuple(跑[正控])
    negative = tuple(跑[負控])
    return PlanResult(
        actual=actual,
        positive=positive,
        negative=negative,
        問題=查三色(actual, positive, negative, plan.取(負控)),
    )
