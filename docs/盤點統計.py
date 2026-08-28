"""從封閉集合殺手盤點的判定表算出各項小計。

**存在理由（sol 2026-08-28 退回）**：我在盤點檔手寫「表列數 74、成員數 116」，
並宣稱「批次標題寫的是成員數」——**那句不成立**：批次九標 13 而表內實列 18、
批次十的 `ALLOWED_OPS` 一列本身就是 12 成員、批次十一的 5 是成員與窄格混算。

> **我寫了一條解釋數字的規則，卻沒驗那條規則描述得了資料。**

sol 的裁法：**同一份 ledger 自動產生 subtotal，否則手算值不可驗。**
所以這支是唯一的計數來源；盤點檔不再寫死任何總數。

**判定表的列格式**（本支認得的全集）：以 `| ` 開頭、含三個判定值之一。
成員數的展開規則兩條，缺一不可：

1. 明文 `×N` 標記優先（`` `MISSING` ×4 `` 代表四個成員）。
2. 否則數該列**成員欄**裡的反引號名字（`` `A`／`B`／`C` `` 是三個）。

**不認得的形式會被算成一個成員**——那是漏報方向，所以新增寫法時要一起改這裡。
"""

from __future__ import annotations

import collections
import pathlib
import re
import sys

判定值 = ("FALSE_POSITIVE", "MISSING", "DECLARATION")
盤點檔 = pathlib.Path(__file__).resolve().parent / "決策" / "封閉集合殺手盤點.md"
名字樣式 = re.compile(r"`[A-Z][A-Z0-9_]{2,}`")


def 成員數(列: str, 判: str) -> int:
    """一列代表幾個成員。"""
    if m := re.search(rf"{判}`?\s*(?:（[^）]*）)?\s*×(\d+)", 列):
        return int(m.group(1))
    欄 = [c.strip() for c in 列.strip("|").split("|")]
    名欄 = 欄[1] if len(欄) > 3 else 欄[0]
    return len(名字樣式.findall(名欄)) or 1


def 統計(文: str) -> dict[str, dict[str, int]]:
    """回傳 `{批次: {判定值: 成員數}}`，外加 `窄格` 與 `觀察` 兩個附帶計數。"""
    出: dict[str, dict[str, int]] = {}
    批 = "（批次前）"
    for 列 in 文.splitlines():
        if 列.startswith("## 批次"):
            批 = 列[3:].split("：")[0].strip()
            出.setdefault(批, collections.defaultdict(int))
            continue
        if not 列.startswith("| "):
            continue
        本 = 出.setdefault(批, collections.defaultdict(int))
        for 判 in 判定值:
            if 判 in 列:
                本[判] += 成員數(列, 判)
                break
        if "窄格" in 列:
            本["窄格"] += 1
        if "觀察" in 列 and "窄格" not in 列:
            本["觀察"] += 1
    return {k: dict(v) for k, v in 出.items() if v}


def main() -> int:
    """印出逐批小計與累計——**盤點檔引用這支的輸出，不自己寫數字**。"""
    表 = 統計(盤點檔.read_text(encoding="utf-8"))
    總: collections.Counter[str] = collections.Counter()
    print(f"{'批次':<14}{'FP':>5}{'MISSING':>9}{'DECL':>6}{'窄格':>6}{'觀察':>6}")
    for 批, 數 in 表.items():
        總.update(數)
        print(
            f"{批:<14}{數.get('FALSE_POSITIVE', 0):>5}{數.get('MISSING', 0):>9}"
            f"{數.get('DECLARATION', 0):>6}{數.get('窄格', 0):>6}{數.get('觀察', 0):>6}"
        )
    裁定成員 = sum(總[k] for k in 判定值)
    print(
        f"\n累計裁定成員 {裁定成員}"
        f"（FP {總['FALSE_POSITIVE']}／MISSING {總['MISSING']}／DECLARATION {總['DECLARATION']}）"
        f" · 窄格 {總['窄格']} · 觀察 {總['觀察']}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
