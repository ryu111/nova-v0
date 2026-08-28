"""從封閉集合殺手盤點的判定表算出各項小計。

**存在理由（sol 2026-08-28 退回）**：我在盤點檔手寫「表列數 74、成員數 116」，
並宣稱「批次標題寫的是成員數」——**那句不成立**：批次九標 13 而表內實列 18、
批次十的 `ALLOWED_OPS` 一列本身就是 12 成員、批次十一的 5 是成員與窄格混算。

> **我寫了一條解釋數字的規則，卻沒驗那條規則描述得了資料。**

sol 的裁法：**同一份 ledger 自動產生 subtotal，否則手算值不可驗。**
所以這支是唯一的計數來源；盤點檔不再寫死任何總數。

**什麼算一列判定**（兩個條件都要，缺一就把雜訊算進去）：

1. **必須在某個 `## 批次` 區段內**——第 16–18 行的判定值圖例表不是裁定。
2. **判定值必須獨占一格**（可帶粗體、`×N`、括號補述）——票表那種
   「FP 5／MISSING 13」是散文裡提到，不是那一列的判定。

**這兩條是補的，不是原本就有。** 第一版只認「以 `| ` 開頭且含判定值」，
於是圖例三列與票表兩列被當成五筆裁定算進總數——**而我在第一次跑就看到
`（批次前） 1 1 1` 這行，沒有質疑它**，還把那個數字當成「唯一權威計數來源」報出去。
被退回的手算值換成程式算，不代表程式算的就對；**程式的判定規則一樣要負控。**
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
# 兩字名字要收得到：`ALLOWED_OPS` 的 `EQ`／`NE`／`IN`／`LT`／`GT` 都是兩字。
# 第一版寫 `{2,}`（三字以上），那五個一律漏數——那列目前靠 `×12` 標記才對，
# 換個人不寫標記就會少算，而且不會有任何跡象。
名字樣式 = re.compile(r"`[A-Z][A-Z0-9_]+`")


def 成員數(列: str, 判: str) -> int:
    """一列代表幾個成員。"""
    if m := re.search(rf"{判}`?\s*(?:（[^）]*）)?\s*×(\d+)", 列):
        return int(m.group(1))
    欄 = [c.strip() for c in 列.strip("|").split("|")]
    名欄 = 欄[1] if len(欄) > 3 else 欄[0]
    return len(名字樣式.findall(名欄)) or 1


def 獨占一格(列: str, 判: str) -> bool:
    """判定值是否獨占某一格——排除散文裡順口提到判定值的票表列。"""
    for 格 in 列.strip("|").split("|"):
        乾 = 格.replace("*", "").replace("`", "").strip()
        if 乾.startswith(判):
            return True
    return False


def 統計(文: str) -> dict[str, dict[str, int]]:
    """回傳 `{批次: {判定值: 成員數}}`，外加 `窄格` 與 `觀察` 兩個附帶計數。"""
    出: dict[str, dict[str, int]] = {}
    批 = None
    for 列 in 文.splitlines():
        if 列.startswith("## 批次"):
            批 = 列[3:].split("：")[0].strip()
            出.setdefault(批, collections.defaultdict(int))
            continue
        if 批 is None or not 列.startswith("| "):
            continue
        本 = 出.setdefault(批, collections.defaultdict(int))
        for 判 in 判定值:
            if 判 in 列 and 獨占一格(列, 判):
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
