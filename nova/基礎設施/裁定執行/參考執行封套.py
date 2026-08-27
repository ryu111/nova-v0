"""bootstrap 用的參考受測對象：行為完全由資料決定的確定性封套。

它**刻意不是真的執行器**。ClaimSpec 語言要先能證明自己（三色矩陣、直接紅、
獨立結果不算負控成立），而那個證明不能依賴任何會變的東西——真的 LLM 後端、
真的子程序、真的時鐘都會讓「這次紅是因為判準還是因為環境」分不開。

所以這裡的觀察值是腳本寫死的。它與別的後端**同一份契約**（計畫 20 Task 4 的
五乘九矩陣要求 replayer 與四種真後端跑同一組），差別只在它不去外面。
"""

from __future__ import annotations

import contextlib
import os
import signal
import subprocess
import sys
import time
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from nova.核心.錯誤 import CaseFailureKind

負控 = "NEGATIVE"


@dataclass(frozen=True, slots=True)
class 腳本失敗:
    """讓封套在某一格回一個獨立結果，而不是回觀察值。

    存在理由：`HARNESS_ERROR` 之類的東西**不是**「負控成功抓到錯」。
    要證明執行器分得清這兩件事，就得能製造出它們。
    """

    種類: CaseFailureKind


@dataclass(frozen=True, slots=True)
class 參考封套:
    """正常時 actual 與正控觀察到 OK；負控觀察到 BAD，於是判準直接紅。"""

    正常: bool = True
    負控狀況: 腳本失敗 | None = None

    def 觀察(self, case: dict[str, Any]) -> dict[str, Any] | 腳本失敗:
        """依 case 的 kind 交出觀察值；不做任何判斷，判斷是判準的事。"""
        if case["kind"] == 負控:
            if self.負控狀況 is not None:
                return self.負控狀況
            return {"code": "BAD"}
        return {"code": "OK" if self.正常 else "BAD"}


# ── 以下是第一份「真的去外面」的受測對象（計畫 01 Task 10）──
#
# 上面那個 參考封套 是腳本寫死的，它證明的是語言自己會不會分色。
# 這一段不一樣：它真的開一個子程序，而且**判定的三個觀察值全部由 verifier 在外面量**。
# 被測者自報的 DURATION_MS 連編譯都過不了——`保證規格編譯.驗觀察` 會回
# UNTRUSTED_OBSERVATION。這正是這份 claim 存在的理由。


def 沉睡指令(秒: int = 30) -> tuple[str, ...]:
    """一個不會自己收手的 worker。它存在的意義就是「叫它停它不停」。"""
    return (sys.executable, "-c", f"import time; time.sleep({秒})")


@dataclass(frozen=True, slots=True)
class 監督結果:
    """監督者交出來的東西：它自報的終態，加上那個 worker 的把手。

    **把手是關鍵**：終態是被測者說的，把手才讓 verifier 自己去看 worker 死了沒。
    只收終態的話，合作式與外部強制的監督者交出來的東西一模一樣。
    """

    terminal: str
    程序: subprocess.Popen[bytes]


監督者 = Callable[[tuple[str, ...], int, int], 監督結果]


def 合作式監督(argv: tuple[str, ...], wall_ms: int, grace_ms: int) -> 監督結果:
    """固定負控 `cooperative-timeout-subject`：等不到就回報逾時，**但不動手殺**。

    它自報的 `TIMED_OUT` 與外部強制那一支逐字相同，所以 `terminal_is_timed_out`
    照樣綠。會紅的只有 `elapsed_bound` 與 `worker_dead`——那兩條都得在封套外面量。
    """
    del grace_ms  # 它根本沒有 grace 這個概念：不殺，就沒有寬限期可言。
    程序 = subprocess.Popen(argv, start_new_session=True, close_fds=True)
    try:
        程序.wait(timeout=wall_ms / 1000)
    except subprocess.TimeoutExpired:
        return 監督結果("TIMED_OUT", 程序)
    return 監督結果("COMPLETED", 程序)


def run_with_wall_limit(argv: tuple[str, ...], wall_ms: int, grace_ms: int) -> 監督結果:
    """牆鐘到期就從外面把整個 process group 殺掉，不問 worker 的意見。

    `start_new_session=True` 是必要的：worker 可能自己再 fork，只殺 pid 會留下孫子。
    殺完仍要 `wait`，否則 zombie 還掛在 process table 上，`poll()` 會說它活著——
    那會讓 `worker_dead` 在被測者其實已經被殺掉時誤判成紅。
    """
    程序 = subprocess.Popen(argv, start_new_session=True, close_fds=True)
    try:
        程序.wait(timeout=wall_ms / 1000)
    except subprocess.TimeoutExpired:
        with contextlib.suppress(ProcessLookupError, PermissionError):
            os.killpg(os.getpgid(程序.pid), signal.SIGKILL)
        with contextlib.suppress(subprocess.TimeoutExpired):
            程序.wait(timeout=grace_ms / 1000)
        return 監督結果("TIMED_OUT", 程序)
    return 監督結果("COMPLETED", 程序)


def 收屍(程序: subprocess.Popen[bytes]) -> None:
    """不管判定是什麼，都不准留下孤兒 process。負控會刻意留一個活的。"""
    if 程序.poll() is None:
        with contextlib.suppress(ProcessLookupError, PermissionError):
            os.killpg(os.getpgid(程序.pid), signal.SIGKILL)
    with contextlib.suppress(subprocess.TimeoutExpired):
        程序.wait(timeout=5)


@dataclass(frozen=True, slots=True)
class 時限封套:
    """真的開 process，然後由 verifier 量到 worker 消失為止。

    `探測寬限_ms` 是**量測上限**不是判準：worker 一直不死時要有個停手點，
    否則負控那一格會掛在那裡。停手點刻意大於 `elapsed_bound`，
    這樣「一直沒死」量出來的用時必然超界，而不是剛好卡在界上。
    """

    wall_ms: int
    grace_ms: int
    探測寬限_ms: int
    正常監督: 監督者 = run_with_wall_limit

    def 觀察(self, case: dict[str, Any]) -> dict[str, Any] | 腳本失敗:
        """負控走合作式，其餘走正式監督。兩邊量法完全相同，差別只在誰去殺。"""
        監督 = 合作式監督 if case["kind"] == 負控 else self.正常監督
        return self.量(監督)

    def 量(self, 監督: 監督者) -> dict[str, Any]:
        """從送出到 worker 真的消失為止，全部由 verifier 這一側計時。"""
        起 = time.monotonic()
        結 = 監督(沉睡指令(), self.wall_ms, self.grace_ms)
        截止 = 起 + (self.wall_ms + self.grace_ms + self.探測寬限_ms) / 1000
        try:
            while 結.程序.poll() is None and time.monotonic() < 截止:
                time.sleep(0.01)
            return {
                "terminal": 結.terminal,
                "elapsed_ms": int((time.monotonic() - 起) * 1000),
                "worker_alive_after_grace": 結.程序.poll() is None,
            }
        finally:
            收屍(結.程序)
