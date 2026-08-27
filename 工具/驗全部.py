"""單一本地入口：依序跑宣告清單裡的每一道閘。

存在理由（實測 2026-08-27）：在一份拋棄式的 repo 複本上同時弄壞 claim 檔的 `claim_id`、
一個測試函式名與檔案落點，`git commit` **exit 0 照樣接受**，而三道閘實際上全是 exit 1。
閘存在不等於閘會被執行；沒有任何執行路徑強制呼叫它們時，它們只是可選工具。

清單住在 `架構/目錄規則.toml` 的 `[[gate]]`，本檔、pre-commit hook 與 CI 都讀同一份，
不各自維護——三處各留一份，遲早有一處漏掉而沒人發現。

**跑完每一道才回報，不在第一個紅就停**：先停會讓後面的閘從此沒人跑過。
"""

from __future__ import annotations

import subprocess
import sys
import tomllib
from pathlib import Path

專案根 = Path(__file__).resolve().parent.parent
規則檔 = 專案根 / "架構" / "目錄規則.toml"

閘 = tuple[str, tuple[str, ...]]


def 閘清單() -> tuple[閘, ...]:
    """從 目錄規則.toml 讀出宣告的閘。這裡不解釋規則，只執行。"""
    with 規則檔.open("rb") as 檔:
        原始 = tomllib.load(檔)
    return tuple((項["name"], tuple(項["argv"])) for 項 in 原始["gate"])


def 跑(閘們: tuple[閘, ...]) -> int:
    """依序跑完每一道閘，回非零表示至少一道紅。"""
    紅 = []
    for 名, argv in 閘們:
        結果 = subprocess.run(argv, cwd=專案根, check=False)
        記 = "綠" if 結果.returncode == 0 else "紅"
        print(f"[{記}] {名}：{' '.join(argv)}", flush=True)
        if 結果.returncode != 0:
            紅.append(名)
    if 紅:
        print(f"\n紅了 {len(紅)} 道：{'、'.join(紅)}", file=sys.stderr)
    return 1 if 紅 else 0


if __name__ == "__main__":
    raise SystemExit(跑(閘清單()))
