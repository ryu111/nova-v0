"""跑一份 TestPlan 的三色矩陣，並且**保留 negative 的直接紅**。

兩層顏色不能混：外層 meta-test 綠，代表**內層的 negative 真的紅過**、而且紅在
指定的 predicate 上。外層綠而內層沒紅過，等於什麼都沒驗到。

四種獨立結果（`UNBOUND_SUBJECT`／`UNSUPPORTED_ISOLATION`／`HARNESS_ERROR`／
`HARNESS_LIMIT`）**一律不算負控成立**。negative subject 自己爆掉不是「成功抓到錯」，
是根本沒驗到——把它算成成功，就是把沒驗到說成驗過了。
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from nova.基礎設施.裁定執行.案例執行 import (
    CaseResult,
    CaseTerminal,
    run_case,
    執行環境,
    獨立結果,
)
from nova.權威.判準.保證規格編譯 import TestPlan

實際 = "ACTUAL"
正控 = "POSITIVE"
負控 = "NEGATIVE"

__all__ = ["CaseResult", "CaseTerminal", "PlanResult", "run_case", "run_plan", "執行環境"]


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
