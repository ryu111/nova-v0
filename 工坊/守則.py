"""`工坊/` 的暫居守則：這一層存在的條件，寫成程式而不是文字。

**為什麼有這支**：T1 要讓 `工坊/` 成為受管轄的頂層，而 mypy 對空目錄回
`There are no .py[i] files in directory '工坊'`（exit 2）——**空目錄無法受管**。
所以這一層的第一個檔就是它自己的守則，不是佔位檔。

**這一層是暫居的**。退役條件與哨兵在 `工坊/退役.toml`（計畫 01C Task 4），
退役 checker 刻意住在 `架構/`——住在這裡的話它會跟著被刪掉。
"""

from __future__ import annotations

# 退役是**六處原子動作**，不是「刪目錄」一件事。少做任一件都有格會紅：
#
#   1. 刪 `工坊/`                     → 退役清冊排除格
#   2. 移除 `[[top_level]]`           → 退役清冊排除格
#   3. 移除 `[[placement]]`           → 退役清冊排除格
#   4. 移除 types 閘 argv             → 不得超出格
#   5. 移除 `.github/workflows/gates.yml` 的 types step  → test_CI_跑的是同一組閘
#   6. 移除計畫 01 Plan Exit Gate 的 mypy 範圍           → 逐字有序格
#
# 【實測】只刪目錄而不做第 4 件：`uv run mypy nova 架構 工具 工坊` 回 **exit 2**
# （`There are no .py[i] files in directory '工坊'`；目錄整個不見時是
# `Cannot read file`）——types 閘直接掛。
退役動作 = (
    "刪 工坊/",
    "移除 架構/目錄規則.toml 的 [[top_level]] dir = 工坊",
    "移除 架構/目錄規則.toml 的 [[placement]] glob = 工坊/**",
    "移除 架構/目錄規則.toml 的 types 閘 argv 裡的 工坊",
    "移除 .github/workflows/gates.yml 的 types step 裡的 工坊",
    "移除 docs/計畫/01-可執行保證語言.md 的 Plan Exit Gate 裡的 工坊",
)

# 三個角色的輸出一律是 observation／advice。**接受權只在 ClaimSpec 閘**——
# 殼不得取得 acceptance authority，這是 `工坊/驗工.py` 存在的理由。
角色們 = ("執行者", "裁定者", "第二審查者")


def 退役件數() -> int:
    """退役要同時做幾件事——由 `架構/test_工坊退役.py` 的矩陣逐件對照。"""
    return len(退役動作)
