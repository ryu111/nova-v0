"""薄殼：呼叫 pytest 跑 ClaimSpec 的 case，**原樣透傳 exit code**。

存在理由（計畫 01 Task 9）：驗收要有一個固定的入口，讓「怎麼跑」不是每個人各自發明。
但它只是薄殼——`工具/` 的職責是組參數並呼叫，不做任何判斷。

**不改寫結果。** 它不吞 exit code、不重試、不把 error 降級成 warning。
pytest 回幾就回幾；判定在 `nova/權威/判準/保證規格執行.py`，顯示在
`nova/基礎設施/裁定執行/外部測試框架.py`，這裡兩者都不碰。
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

專案根 = Path(__file__).resolve().parent.parent
if str(專案根) not in sys.path:
    sys.path.insert(0, str(專案根))

from nova.基礎設施.裁定執行.外部測試框架 import ClaimCatalog  # noqa: E402

外掛 = "nova.基礎設施.裁定執行.外部測試框架"


@dataclass(frozen=True, slots=True)
class 跑驗收結果:
    """跑驗收的執行結果，帶 exit_code 與 failure code。"""

    exit_code: int
    code: str = "OK"
    細節: str = ""


def 跑驗收(
    參數: list[str],
    catalog: ClaimCatalog | None = None,
    專案根目錄: Path = 專案根,
) -> 跑驗收結果:
    """解析 --claim 與 --binding，走 ClaimCatalog 解析，並透傳呼叫 pytest。"""
    剖析器 = argparse.ArgumentParser(description="跑驗收", add_help=False)
    剖析器.add_argument("--claim", action="append", default=[], help="要跑的 claim id")
    剖析器.add_argument("--binding", action="append", default=[], help="要綁定的 binding id")
    已知, 其餘 = 剖析器.parse_known_args(參數)

    用目錄 = catalog if catalog is not None else ClaimCatalog.掃描(專案根目錄)
    for 目標 in 已知.claim:
        狀態, 路徑 = 用目錄.解析(目標)
        if 狀態 == "UNKNOWN_CLAIM_ID":
            print(f"UNKNOWN_CLAIM_ID: 查無 claim_id={目標}", file=sys.stderr)
            return 跑驗收結果(exit_code=1, code="UNKNOWN_CLAIM_ID", 細節=目標)
        if 狀態 == "CLAIM_FILE_MISSING":
            print(
                f"CLAIM_FILE_MISSING: claim_id={目標} 對應檔案不存在或不可讀: {路徑}",
                file=sys.stderr,
            )
            return 跑驗收結果(exit_code=1, code="CLAIM_FILE_MISSING", 細節=f"{目標}:{路徑}")

    if 已知.claim:
        print("UNSUPPORTED_CLAIM_EXECUTION: claim 執行尚未接線", file=sys.stderr)
        return 跑驗收結果(
            exit_code=1,
            code="UNSUPPORTED_CLAIM_EXECUTION",
            細節=",".join(已知.claim),
        )

    指令 = [sys.executable, "-m", "pytest", "-q", "-p", 外掛, *其餘]
    完成 = subprocess.run(指令, cwd=專案根目錄, check=False)
    return 跑驗收結果(
        exit_code=完成.returncode,
        code="OK" if 完成.returncode == 0 else "FAIL",
    )


def 跑(參數: list[str], catalog: ClaimCatalog | None = None) -> int:
    """把參數接到 pytest 後面，回它的 exit code。中間不做任何翻譯。"""
    return 跑驗收(參數, catalog=catalog).exit_code


if __name__ == "__main__":
    raise SystemExit(跑(sys.argv[1:]))
