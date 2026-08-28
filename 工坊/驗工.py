"""獨立的、非 LLM 的驗工入口。

**存在理由**：三個角色的輸出一律是 observation／advice，**不得取得 acceptance
authority**。而只收後端的 exit code 與 log 也不夠——**agy 實測會在權限被拒、
零產出時回 `"status":"SUCCESS"`**（見 `docs/陷阱.md`）。

所以驗收由這支跑：宣告的驗收命令逐條執行、逐條記 argv 與 exit、
**失敗與未執行都明列**、全部 exit 0 才輸出 green。

**shell 用 `sh` 不用 `zsh`**：第一版寫死 `zsh -euo pipefail`，本機（macOS）全綠
而 **CI 的 Linux runner 沒有 zsh**，`FileNotFoundError: 'zsh'` 讓整道 tests 閘掛。
「換個情境跑綠」不能判定假紅——這次是反面：換個情境才發現本機的綠是環境給的。
`sh` 是 POSIX 保證存在的那一個；`pipefail` 不在 POSIX 裡，所以由本檔
`嚴格旗標()` 探測後決定加不加。
"""

from __future__ import annotations

import json
import subprocess
from typing import Any

碼_驗收命令多義 = "AMBIGUOUS_ACCEPTANCE_COMMAND"


class 無法驗收(Exception):
    """typed fail-closed。**不自行猜**哪一條是最終 PASS 命令。"""


def 後端自報可信(輸出: str) -> bool:
    """後端自報的成功是否可以採信——**答案永遠是否**。

    保留這支不是為了留一個開關，是為了讓「不採信」這件事有個具名的位置，
    負控釘得住。agy 的 `{"status":"SUCCESS","response":""}` 就是實案。
    """
    try:
        json.loads(輸出)
    except json.JSONDecodeError, TypeError:
        return False
    return False


def 嚴格旗標() -> list[str]:
    """探測這台機器的 `sh` 支不支援 `pipefail`——**不假設，實測**。

    `pipefail` 是 bash／zsh 的擴充，POSIX `sh` 不保證有。假設它存在就會
    在沒有的機器上讓每一條命令都掛掉，而那種掛法看起來像「測試失敗」。
    """
    試 = subprocess.run(["sh", "-c", "set -o pipefail"], check=False, capture_output=True)
    return ["-euo", "pipefail"] if 試.returncode == 0 else ["-eu"]


def 跑(命令們: list[str]) -> dict[str, Any]:
    """逐條跑，第一條非零之後的都記成未執行（`exit` 為 `None`）。"""
    if not 命令們:
        raise 無法驗收(f"ambiguous_acceptance_command：{碼_驗收命令多義}：零個驗收命令，不猜")
    逐條: list[dict[str, Any]] = []
    停了 = False
    for 條 in 命令們:
        if 停了:
            逐條.append({"命令": 條, "exit": None, "說明": "未執行"})
            continue
        出 = subprocess.run(
            ["sh", *嚴格旗標(), "-c", 條], check=False, capture_output=True, text=True
        )
        逐條.append({"命令": 條, "exit": 出.returncode})
        if 出.returncode != 0:
            停了 = True
    return {"green": all(格["exit"] == 0 for 格 in 逐條), "逐條": 逐條}
