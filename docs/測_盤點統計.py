"""盤點統計的判定規則負控。

**存在理由**：sol 2026-08-28 退回手寫的「表列數 74／成員數 116」，理由是
手算值不可驗，要「同一份 ledger 自動產生 subtotal」。我照做寫了 `盤點統計.py`，
**然後把它算出的數字當成唯一權威報出去**——但那支的第一版把兩種非裁定列
算成了裁定：

1. 檔頭第 16–18 行的**判定值圖例表**（定義 `FALSE_POSITIVE`／`MISSING`／
   `DECLARATION` 是什麼意思），被當成三筆裁定。
2. 票表裡「FP 5／MISSING 13」這種**散文提及**，被當成該列的判定。

代價：129 → 124，虛胖五筆。**而我在第一次跑就看到 `（批次前） 1 1 1` 那行，
沒有質疑它。** 手算值換成程式算不代表就對了——程式的判定規則一樣要負控，
否則只是把一個沒人驗過的數字換成另一個沒人驗過的數字。

這些格證明兩條排除規則真的在擋東西：拿掉任一條，對應的格就會綠掉。
"""

from __future__ import annotations

import importlib.util
import pathlib
import sys

模組路徑 = pathlib.Path(__file__).resolve().parent / "盤點統計.py"
規格 = importlib.util.spec_from_file_location("盤點統計", 模組路徑)
assert 規格 and 規格.loader
統計器 = importlib.util.module_from_spec(規格)
sys.modules["盤點統計"] = 統計器
規格.loader.exec_module(統計器)


def 算(文: str) -> int:
    """把整份文字跑過統計，回傳裁定成員總數。"""
    表 = 統計器.統計(文)
    return sum(數.get(判, 0) for 數 in 表.values() for 判 in 統計器.判定值)


圖例 = """| 判定 | 意義 |
|---|---|
| `FALSE_POSITIVE` | 掃描器誤報，成員有真殺手 |
| `MISSING` | 確認沒有命名殺手，要補 |
| `DECLARATION` | 刻意 record-only |
"""

真表 = """## 批次一：示例

| 成員 | 判定 | 依據 |
|---|---|---|
| `RAW` | `MISSING` | 只有宣告行 |
"""


def test_批次區段外的圖例表不算裁定():
    """圖例在第一個 `## 批次` 之前——那是判定值的定義，不是對某成員的裁定。"""
    assert 算(圖例) == 0
    assert 算(圖例 + 真表) == 1, "圖例被算進去了"


def test_散文裡提到判定值的票表列不算裁定():
    """票表的「FP 5／MISSING 13」是在講別批的統計，不是這一列的判定。"""
    票表 = 真表 + "| 2 | 13 份人工列舉接受，但以 FP 5／MISSING 13 入帳 |\n"
    assert 算(票表) == 1, "票表的散文提及被當成裁定"


def test_判定值獨占一格才算():
    """判定值必須是那一格的主體，可帶粗體、反引號、`×N`、括號補述。"""
    assert 統計器.獨占一格("| `A` | **`MISSING`（行為面）** ×2 | 依據 |", "MISSING")
    assert not 統計器.獨占一格("| 2 | 以 FP 5／MISSING 13 入帳 |", "MISSING")


def test_合併列依標記與名字展開():
    """一列可涵蓋多個成員——`×N` 優先，否則數成員欄的反引號名字。

    `EQ`／`NE` 是**兩字名字**：第一版的樣式要求三字以上，`ALLOWED_OPS` 的
    `EQ`／`NE`／`IN`／`LT`／`GT` 五個會一律漏數。這格就是為了釘住那個下限。"""
    倍 = "## 批次一：示例\n\n| 成員 | 判定 | 依據 |\n|---|---|---|\n| 全 | `MISSING` ×4 | 依據 |\n"
    多名 = "## 批次一：示例\n\n| 成員 | 判定 | 依據 |\n|---|---|---|\n| `EQ`／`NE`／`RAW` | `MISSING` | 依據 |\n"
    assert 算(倍) == 4
    assert 算(多名) == 3


def test_正常裁定列照算_防恆真():
    """兩條排除規則不得把真的判定列一起殺掉——否則上面每一格都會恆真。"""
    assert 算(真表) == 1
