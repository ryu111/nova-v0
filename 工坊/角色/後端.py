"""每個 CLI 後端的**非互動呼叫形狀**，封閉列舉。

**發作（2026-08-28 實跑）**：殼原本寫死 `[路徑, "--model", model]`——
那是**互動模式**的形狀。真的派工單給 codex 時 exit 1、輸出空，
`codex --model X` 直接回 `Error: stdin is not a terminal`。

**為什麼冒煙格沒抓到**：01C Task 3 的正面格用的是假後端（一支吃任何參數
都吐 sentinel 的 sh 腳本），所以那格綠、真後端跑不起來。
**假後端驗的是殼有沒有正確傳遞，不是真的能不能啟動。**
sol 條件四說過「三家 resume 介面不同」，我把 `--model` 分欄做對了，
卻把呼叫形狀當成三家一樣。

**`claude` 的傳輸是 subagent 不是 CLI**——但它**照樣走殼**。
第一版我讓它整個不走殼、typed 拒，使用者指出那毀掉殼存在的理由：
殼是統一介面，三家共用「讀 prompt、驗工單、驗 grant、記 digest」那一段，
踢掉一家那一段就要在別處重寫一次。

實體限制是真的——殼是 Python subprocess，**呼叫不到 Agent 工具**。
所以差別只落在「誰執行那一步」：CLI 傳輸在殼內 subprocess，
subagent 傳輸由 main agent 跑完再 `收工()` 交回來。
"""

from __future__ import annotations

碼_子代理傳輸 = "TRANSPORT_IS_SUBAGENT"
碼_未知後端 = "UNKNOWN_BACKEND"
# **模型隨時可換**：model 一律由呼叫端傳入，這裡只決定「怎麼呼叫」不決定「呼叫誰」。
命令列後端 = ("codex", "agy")
子代理後端 = ("claude",)


class 不是命令列後端(Exception):
    """typed 拒。訊息以 failure code 起頭，讓負控釘得住紅因。"""


def 傳輸(backend: str) -> str:
    """這個後端由誰執行——`CLI`（殼內 subprocess）或 `SUBAGENT`（主控跑）。"""
    if backend in 子代理後端:
        return "SUBAGENT"
    if backend in 命令列後端:
        return "CLI"
    raise 不是命令列後端(f"unknown_backend：{碼_未知後端}：{backend}")


def 形狀(
    backend: str, model: str, prompt: str, *, effort: str = "high"
) -> tuple[list[str], str | None]:
    """回 `(除了 executable 之外的參數, 要餵進 stdin 的東西)`。

    stdin 為 `None` 表示 prompt 已經在參數裡（agy 那種）。
    """
    if backend in 子代理後端:
        raise 不是命令列後端(
            f"transport_is_subagent：{碼_子代理傳輸}：{backend} 由主控以 subagent 執行，"
            f"殼只負責備工與收工"
        )
    if backend == "codex":
        # 非互動子命令是 `exec`；prompt 走 stdin。
        return ["exec", "--model", model], prompt
    if backend == "agy":
        # **`-p` 會吃掉下一個參數**——實測 `agy -p --output-format json` 會把
        # `--output-format` 當成 prompt 本身。所以 prompt 用 `-p=` 貼著給，
        # 而 `--output-format` 必須排在 `-p` **之前**。
        # **`--model` 必須配 `--effort`**——實測不給會回
        # `invalid model selection (... --effort ""): 需要 low|medium|high`。
        # 這次它誠實回了 `status:"ERROR"`，不是那個 `SUCCESS` 零產出陷阱。
        return (
            ["--model", model, "--effort", effort, "--output-format", "json", f"-p={prompt}"],
            None,
        )
    raise 不是命令列後端(f"unknown_backend：{碼_未知後端}：{backend}")
