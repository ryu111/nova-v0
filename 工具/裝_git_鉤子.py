"""安裝 pre-commit hook。

`.git/` 不在版控裡，所以 hook 不能靠 clone 帶進來——必須有人跑這支裝。
這件事本身就是這道防線的上限：**hook 可以被 `--no-verify` 繞過，也可以根本沒裝**。
它只作快速回饋；權威執法點是 CI 的 required check。不得宣稱「不可能繞過」。
"""

from __future__ import annotations

import os
import stat
import subprocess
import sys
from pathlib import Path

專案根 = Path(__file__).resolve().parent.parent
預設入口 = 專案根 / "工具" / "驗全部.py"


def 乾淨環境() -> dict[str, str]:
    """剝掉所有 `GIT_*` 的一份 env。

    **git 鉤子執行時會設 `GIT_DIR`、`GIT_INDEX_FILE`、`GIT_PREFIX`；只要它們存在，
    `cwd` 就完全不算數**——每個 git 指令都會打到鉤子所屬的那個倉，不管你叫它去哪。

    【實測 2026-08-28】沒有這層剝除時，透過 pre-commit 鉤子跑測試會讓
    `安裝()` 把 hook 寫進**真 repo**（而不是傳進來的 `倉根`），
    連帶 `架構/test_工程規範.py` 的臨時倉測試在真 repo 上寫了 `user.email=t@t`
    與一個把整棵樹刪光的 commit。驗鉤子的東西透過鉤子跑時弄壞了 repo。
    """
    return {鍵: 值 for 鍵, 值 in os.environ.items() if not 鍵.startswith("GIT_")}


def 鉤子內容(直譯器: str, 入口: Path) -> str:
    """`exec` 讓 hook 的 exit code 就是入口的 exit code，中間不做任何翻譯。"""
    return f'#!/bin/sh\nexec "{直譯器}" "{入口}"\n'


def 安裝(倉根: Path, 入口: Path = 預設入口) -> Path:
    """把 pre-commit hook 寫進該倉的 hooks 目錄並給執行權。"""
    出 = subprocess.run(
        ["git", "rev-parse", "--git-path", "hooks"],
        cwd=倉根,
        capture_output=True,
        text=True,
        check=True,
        env=乾淨環境(),
    )
    目錄 = (倉根 / 出.stdout.strip()).resolve()
    目錄.mkdir(parents=True, exist_ok=True)
    鉤子 = 目錄 / "pre-commit"
    鉤子.write_text(鉤子內容(sys.executable, 入口), encoding="utf-8")
    鉤子.chmod(鉤子.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    return 鉤子


if __name__ == "__main__":
    print(f"已安裝：{安裝(專案根)}（可被 --no-verify 繞過；權威執法點是 CI）")
