"""帶型別的時間量。

裸 int 會讓「毫秒」與「秒」在同一個算式裡相加而沒有任何人發現，所以時距與時點
各有自己的型別。這一層**沒有時鐘**：現在幾點是外部世界的事，由 port 注入。
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Duration:
    """一段時距，單位毫秒，不得為負。"""

    millis: int

    @classmethod
    def from_millis(cls, 值: int) -> Duration:
        """從毫秒建立時距；負值直接拒絕而不是靜靜夾成 0。"""
        if 值 < 0:
            raise ValueError(f"millis 不得為負：{值}")
        return cls(值)


@dataclass(frozen=True, slots=True)
class Instant:
    """一個時點，UTC epoch 毫秒。時區與格式化是顯示層的事，不在這裡。"""

    epoch_millis: int

    @classmethod
    def from_epoch_millis(cls, 值: int) -> Instant:
        """從 UTC epoch 毫秒建立時點。"""
        return cls(值)
