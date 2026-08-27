"""bootstrap 用的參考受測對象：行為完全由資料決定的確定性封套。

它**刻意不是真的執行器**。ClaimSpec 語言要先能證明自己（三色矩陣、直接紅、
獨立結果不算負控成立），而那個證明不能依賴任何會變的東西——真的 LLM 後端、
真的子程序、真的時鐘都會讓「這次紅是因為判準還是因為環境」分不開。

所以這裡的觀察值是腳本寫死的。它與別的後端**同一份契約**（計畫 20 Task 4 的
五乘九矩陣要求 replayer 與四種真後端跑同一組），差別只在它不去外面。
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from nova.核心.錯誤 import CaseFailureKind

負控 = "NEGATIVE"


@dataclass(frozen=True, slots=True)
class 腳本失敗:
    """讓封套在某一格回一個獨立結果，而不是回觀察值。

    存在理由：`HARNESS_ERROR` 之類的東西**不是**「負控成功抓到錯」。
    要證明執行器分得清這兩件事，就得能製造出它們。
    """

    種類: CaseFailureKind


@dataclass(frozen=True, slots=True)
class 參考封套:
    """正常時 actual 與正控觀察到 OK；負控觀察到 BAD，於是判準直接紅。"""

    正常: bool = True
    負控狀況: 腳本失敗 | None = None

    def 觀察(self, case: dict[str, Any]) -> dict[str, Any] | 腳本失敗:
        """依 case 的 kind 交出觀察值；不做任何判斷，判斷是判準的事。"""
        if case["kind"] == 負控:
            if self.負控狀況 is not None:
                return self.負控狀況
            return {"code": "BAD"}
        return {"code": "OK" if self.正常 else "BAD"}
