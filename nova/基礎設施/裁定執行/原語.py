"""封閉的原語目錄：一個 claim 只能用目錄裡有的原語。

封閉的理由與 ClaimSpec schema 一樣：目錄外的原語代表「有人在測一件沒人審過的事」。
每個原語同時宣告它**產出什麼型別**與**它是不是外部效果**——後者決定這份 claim
需不需要交付契約，那個判斷不能靠原語名字的前綴猜。
"""

from __future__ import annotations

from dataclasses import dataclass

from nova.核心.摘要 import Sha256Ref, canonical_json_bytes, sha256_ref

內部 = "INTERNAL"
外部效果 = "EXTERNAL_EFFECT"


@dataclass(frozen=True, slots=True)
class 原語:
    """一個可被 stimulus 呼叫的動作：它的 id、種類，與它產出的觀察值型別。"""

    primitive_id: str
    kind: str
    produces: str


@dataclass(frozen=True, slots=True)
class 原語目錄:
    """一份具名的原語集合。digest 進 plan_digest，換目錄就是換題目。"""

    catalog_id: str
    原語們: tuple[原語, ...]

    def 查(self, primitive_id: str) -> 原語 | None:
        """找不到就回 None——呼叫端要把「找不到」當成 typed 失敗，不是當成沒有限制。"""
        for 項 in self.原語們:
            if 項.primitive_id == primitive_id:
                return 項
        return None

    @property
    def digest(self) -> Sha256Ref:
        """對 catalog_id 與全部原語取 canonical digest；順序不影響結果。"""
        主體 = {
            "catalog_id": self.catalog_id,
            "primitives": sorted([[項.primitive_id, 項.kind, 項.produces] for 項 in self.原語們]),
        }
        return sha256_ref(canonical_json_bytes(主體))
