"""裁定者殼：讀 prompt、收工單、驗 grant、呼叫後端、原樣收輸出。

**這支刻意很短**，而且不准變長：dispatch 邏輯（retry／cascade／收斂）是產品
Work／Pursuit 的地盤，在殼裡長就是第二個 harness。`薄度.檢查()` 釘住這條。

**輸出是 observation／advice**，不是接受。接受權只在 ClaimSpec 閘。
"""

from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
from pathlib import Path
from typing import Any

from 工坊.角色 import 後端, 薄度

提示目錄 = Path(__file__).resolve().parent / "提示"
角色名 = "裁定者"
碼_授權不合法 = "GRANT_NOT_IN_BINARY_CAPABILITY_SET"
碼_授權未生效 = "GRANT_NOT_EFFECTIVE"
碼_已凍結 = "WORKSHOP_FROZEN"
# 【實測】`edit` 不是 agy 的合法 action——整場派工無寫檔權而無人知，燒掉一整輪。
合法授權 = frozenset({"write_file", "read_file", "command", "list_directory"})


class 不得派工(Exception):
    """typed 拒派。訊息以 failure code 起頭，讓負控釘得住紅因。"""


def _摘要(路徑: Path) -> str:
    return hashlib.sha256(路徑.read_bytes()).hexdigest()


def 派工(
    請求: dict[str, Any], *, 環境: dict[str, str], canary: str | None = None
) -> dict[str, Any]:
    """執行一個**已備好的請求**——只服務 CLI 傳輸。

    收請求物件而不是逐欄轉發：規模閘擋下 7 個參數時那是它在說「該收斂」，
    而 `**kwargs` 轉發過不了型別閘——**兩道閘一起把設計推到對的形狀**。
    subagent 傳輸要改用 `備工()` 加 `收工()`。
    """
    backend = 請求["backend"]
    if 請求["傳輸"] != "CLI":
        raise 不得派工(
            f"transport_is_subagent：{後端.碼_子代理傳輸}：{backend} 由主控執行，"
            f"請用 備工() 取請求、跑完再 收工()"
        )
    摘要 = 請求["prompt_digest"]
    路徑 = shutil.which(backend, path=環境.get("PATH"))
    if 路徑 is None:
        # **恰回 127**，不是「非零」：壞態本身就非零時 `!= 0` 是恆真 oracle。
        return {"exit": 127, "輸出": "", "executable": None, "prompt_digest": 摘要}
    內容 = json.dumps({**請求["工單"], "prompt_digest": 摘要}, ensure_ascii=False)
    # **呼叫形狀三家各不相同**，由 `後端.形狀()` 封閉決定；model 一律由呼叫端傳入
    # ——這裡只決定「怎麼呼叫」，不決定「呼叫誰」，模型隨時可換。
    尾, 進標準輸入 = 後端.形狀(backend, 請求["model"], 內容, effort=請求["effort"])
    參數 = [路徑, *尾]
    if 請求["sid"]:
        參數 += ["--resume", str(請求["sid"])]
    出 = subprocess.run(
        參數,
        input=進標準輸入 or "",
        capture_output=True,
        text=True,
        env=環境,
        check=False,
    )
    if canary is not None and canary not in 出.stdout:
        # **語法被接受不等於路徑匹配生效**——canary 沒出現就不算 grant 生效。
        raise 不得派工(f"grant_not_effective：{碼_授權未生效}：canary 未出現")
    return {
        "exit": 出.returncode,
        "輸出": 出.stdout,
        "executable": 路徑,
        "executable_digest": _摘要(Path(路徑)),
        "prompt_digest": 摘要,
        "kind": "OBSERVATION",
    }


def 備工(
    工單: dict[str, Any],
    *,
    model: str,
    effort: str = "high",
    backend: str = "codex",
    sid: str | None = None,
) -> dict[str, Any]:
    """**純驗證，不執行**：驗 grant、載 prompt 取 digest、標傳輸方式。

    三家後端到這一步完全一樣——**這正是殼存在的理由**。
    不 resolve PATH、不起 subprocess，所以 grant 驗證可以被單獨測，
    不必透過假後端間接驗。

    `model` 與 `effort` 是**兩個維度**：`luna-max` 看起來像模型名，
    實際是 `gpt-5.6-luna` 加上 effort `max`——當成一個字串傳給 `--model`
    會讓 CLI 查不到 metadata、**落到 fallback 但照樣跑**，警告只在 stderr。
    """
    if (Path(__file__).resolve().parent.parent / "凍結.md").is_file():
        raise 不得派工(f"workshop_frozen：{碼_已凍結}：工坊已凍結，改走產品介面")
    for g in 工單.get("grant", []):
        if g not in 合法授權:
            raise 不得派工(f"grant_not_in_binary_capability_set：{碼_授權不合法}：{g}")
    提示 = 提示目錄 / f"{角色名}.md"
    return {
        "角色": 角色名,
        "工單": 工單,
        "backend": backend,
        "model": model,
        "effort": effort,
        "sid": sid,
        "傳輸": 後端.傳輸(backend),
        "prompt_digest": 薄度.提示摘要(提示),
    }


def 收工(請求: dict[str, Any], 輸出: str, *, 離開碼: int) -> dict[str, Any]:
    """把主控跑完的 subagent 結果記回來。

    **輸出一律是 observation／advice**——接受權只在 ClaimSpec 閘，
    不論是誰跑的、跑得多好。
    """
    return {
        "exit": 離開碼,
        "輸出": 輸出,
        "executable": None,
        "prompt_digest": 請求["prompt_digest"],
        "kind": "OBSERVATION",
    }
