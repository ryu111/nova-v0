"""canonical JSON bytes 與 SHA-256 參照。

digest 的全部價值在於「同一個東西永遠得到同一串 bytes」。所以這支寧可拒絕
也不猜：非 NFC 的字串、float、NaN／Inf 一律不准進來，因為它們各自都能讓
同一個邏輯上的值產生兩份不同的 bytes。
"""

from __future__ import annotations

import hashlib
import json
import unicodedata
from dataclasses import dataclass

from nova.核心.錯誤 import TextNotCanonical, ValueNotCanonical


@dataclass(frozen=True, slots=True)
class Sha256Ref:
    """一段 bytes 的 SHA-256，永遠是 64 個小寫十六進位字元。"""

    hex: str


def sha256_ref(資料: bytes) -> Sha256Ref:
    """對 bytes 取 SHA-256。輸入已經是 bytes，這裡不做任何編碼決定。"""
    return Sha256Ref(hashlib.sha256(資料).hexdigest())


def 驗_canonical(值: object) -> None:
    """遞迴檢查一個值能不能有穩定的 canonical 表示，不能就帶 typed code 拒絕。

    float 全部拒絕而不只拒 NaN／Inf：`0.1 + 0.2` 與 `0.3` 的 repr 不同，
    跨平台與跨版本的 float 格式化也不保證一致——那是 digest 漂移的來源。
    需要小數的地方用整數的最小單位或字串表示。
    """
    if isinstance(值, str):
        if not unicodedata.is_normalized("NFC", 值):
            raise TextNotCanonical(值)
        return
    if isinstance(值, bool) or 值 is None or isinstance(值, int):
        return
    if isinstance(值, float):
        raise ValueNotCanonical(f"float 沒有穩定的 canonical 表示：{值!r}")
    if isinstance(值, dict):
        for 鍵, 子 in 值.items():
            if not isinstance(鍵, str):
                raise ValueNotCanonical(f"JSON object 的 key 必須是字串：{鍵!r}")
            驗_canonical(鍵)
            驗_canonical(子)
        return
    if isinstance(值, list | tuple):
        for 子 in 值:
            驗_canonical(子)
        return
    raise ValueNotCanonical(f"不是可序列化的 JSON 值：{type(值).__name__}")


def canonical_json_bytes(值: object) -> bytes:
    """把值轉成唯一的一串 bytes：key 排序、無多餘空白、UTF-8、中文不轉義。"""
    驗_canonical(值)
    return json.dumps(
        值,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")
