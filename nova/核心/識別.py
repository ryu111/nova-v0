"""跨程序、會被持久化的識別字。

這些值會進 DB、進事件、被別的程序與別的版本比對，所以一律 ASCII——
CLAUDE.md 的語言例外正是為這一類存在的。中文可以是檔名與 Python 識別字，
但不能是這裡的 value。
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from nova.核心.摘要 import Sha256Ref
from nova.核心.錯誤 import InvalidSemanticId

語義識別樣式 = re.compile(r"[a-z][a-z0-9]*(?:[.-][a-z0-9]+)*")


@dataclass(frozen=True, slots=True)
class SemanticId:
    """一個持久的語義識別，例如 `claim.naming-two-tracks.v1`。"""

    value: str

    @classmethod
    def parse(cls, raw: str) -> SemanticId:
        """解析持久 semantic id；不合樣式一律 INVALID_SEMANTIC_ID，不做任何清洗。"""
        if 語義識別樣式.fullmatch(raw) is None:
            raise InvalidSemanticId(raw)
        return cls(raw)


@dataclass(frozen=True, slots=True)
class BindingSlot:
    """subject binding 的槽位名，與 semantic id 同一套字元規則。"""

    value: str

    @classmethod
    def parse(cls, raw: str) -> BindingSlot:
        """解析 binding slot 名稱。"""
        if 語義識別樣式.fullmatch(raw) is None:
            raise InvalidSemanticId(raw)
        return cls(raw)


@dataclass(frozen=True, slots=True)
class ClaimRef:
    """指向某一版 ClaimSpec 的不可變參照：id、版次與該版的 digest 三者同時固定。"""

    claim_id: SemanticId
    revision: int
    digest: Sha256Ref

    def __post_init__(self) -> None:
        """版次從 1 起算；0 或負數代表有人在拿沒准入過的東西當參照。"""
        if self.revision < 1:
            raise ValueError(f"revision 必須從 1 起算：{self.revision}")
