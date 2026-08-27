"""核心的封閉錯誤集合。

每個 failure 都帶一個跨程序的 ASCII `code`：那是會被寫進 evidence、被別的程序比對的
identity，所以不能是中文訊息。中文只出現在給人看的細節裡。
"""

from __future__ import annotations

import enum


class 核心錯誤(Exception):
    """所有核心錯誤的根。子類別必須宣告自己的 ASCII failure code。"""

    code: str

    def __init__(self, 細節: str) -> None:
        """訊息一律是 `CODE: 細節`——code 給程式比對，細節給人看。"""
        super().__init__(f"{self.code}: {細節}")
        self.細節 = 細節


class InvalidSemanticId(核心錯誤):
    """持久 semantic id 不合規：只准小寫 ASCII、數字、`.` 與 `-`。"""

    code = "INVALID_SEMANTIC_ID"


class TextNotCanonical(核心錯誤):
    """字串不是 NFC。同形不同碼會讓同一個「東西」產生兩份 digest。"""

    code = "TEXT_NOT_NFC"


class ValueNotCanonical(核心錯誤):
    """值本身無法有穩定的 canonical 表示（例如 float）。"""

    code = "VALUE_NOT_CANONICAL"


class CaseFailureKind(enum.Enum):
    """一個 case 沒有 ACCEPT 時，只可能是這五種之一。

    後四種是**獨立結果**，不是「負控成功抓到錯」：subject 沒綁、隔離能力不足、
    harness 自己爆掉、harness 撞到上限——把它們當成負控成立就是把沒驗到說成驗過了。
    """

    CLAIM_REJECTED = "CLAIM_REJECTED"
    UNBOUND_SUBJECT = "UNBOUND_SUBJECT"
    UNSUPPORTED_ISOLATION = "UNSUPPORTED_ISOLATION"
    HARNESS_ERROR = "HARNESS_ERROR"
    HARNESS_LIMIT = "HARNESS_LIMIT"
