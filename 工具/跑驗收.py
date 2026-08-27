"""薄殼：呼叫 pytest 跑 ClaimSpec 的 case，**原樣透傳 exit code**。

存在理由（計畫 01 Task 9）：驗收要有一個固定的入口，讓「怎麼跑」不是每個人各自發明。
但它只是薄殼——`工具/` 的職責是組參數並呼叫，不做任何判斷。

**不改寫結果。** 它不吞 exit code、不重試、不把 error 降級成 warning。
pytest 回幾就回幾；判定在 `nova/權威/判準/保證規格執行.py`，顯示在
`nova/基礎設施/裁定執行/外部測試框架.py`，這裡兩者都不碰。
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

專案根 = Path(__file__).resolve().parent.parent
外掛 = "nova.基礎設施.裁定執行.外部測試框架"


def 跑(參數: list[str]) -> int:
    """把參數接到 pytest 後面，回它的 exit code。中間不做任何翻譯。"""
    指令 = [sys.executable, "-m", "pytest", "-q", "-p", 外掛, *參數]
    return subprocess.run(指令, cwd=專案根, check=False).returncode


if __name__ == "__main__":
    raise SystemExit(跑(sys.argv[1:]))
