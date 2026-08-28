"""第二審查者殼：讀 prompt、收工單、驗 grant、呼叫後端、原樣收輸出。

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
角色名 = "第二審查者"
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
    工單: dict[str, Any],
    *,
    model: str,
    環境: dict[str, str],
    backend: str = "claude",
    sid: str | None = None,
    canary: str | None = None,
) -> dict[str, Any]:
    """**backend／model／sid／grant 分欄**，不混成一個字串。

    `sid` 缺省即 fresh session——第二審查者的 sid 用法見 01C，續存是控制端自用。
    """
    if (Path(__file__).resolve().parent.parent / "凍結.md").is_file():
        # **凍結檢查不能只在生成器**：凍結前生成的舊工單，凍結後照樣可派
        # ——fable 覆蓋審抓到。三殼各自認旗標。
        raise 不得派工(f"workshop_frozen：{碼_已凍結}：工坊已凍結，改走產品介面")
    for g in 工單.get("grant", []):
        if g not in 合法授權:
            raise 不得派工(f"grant_not_in_binary_capability_set：{碼_授權不合法}：{g}")
    提示 = 提示目錄 / f"{角色名}.md"
    摘要 = 薄度.提示摘要(提示)
    路徑 = shutil.which(backend, path=環境.get("PATH"))
    if 路徑 is None:
        # **恰回 127**，不是「非零」：壞態本身就非零時 `!= 0` 是恆真 oracle。
        return {"exit": 127, "輸出": "", "executable": None, "prompt_digest": 摘要}
    內容 = json.dumps({**工單, "prompt_digest": 摘要}, ensure_ascii=False)
    # **呼叫形狀三家各不相同**，由 `後端.形狀()` 封閉決定；model 一律由呼叫端傳入
    # ——這裡只決定「怎麼呼叫」，不決定「呼叫誰」，模型隨時可換。
    尾, 進標準輸入 = 後端.形狀(backend, model, 內容)
    參數 = [路徑, *尾]
    if sid:
        參數 += ["--resume", sid]
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
