"""從計畫的 task 區段機械生成工單，並在消費時真的驗它還算不算數。

**存在理由（三個實測坑）**：手抄計畫內容必然腐化——claim instance 三處與實檔
不符、散文裡的過期份數，都是同一類。工單改由機械生成並綁住來源區段的
**位元組摘要**，手改一字就對不上。

**只印不驗等於沒驗**：`base_commit_sha` 放進工單而不在消費時比對，
**舊工單照樣能打新樹**。所以消費是三驗不是三欄。
"""

from __future__ import annotations

import hashlib
import re
from pathlib import Path
from typing import Any

SCHEMA_REVISION = 1

# ── failure code 全集 ─────────────────────────────────────────────────
#
# 這些**大寫碼是 claim 的 judge 真正比對的字面**，不是裝飾。
# 寫這一段的當下，`測_meta_schema.py` 的字面 producer 棘輪擋了我一次：
# claim 先寫好、產生者還不存在時，那四個 predicate 全是恆真格
# ——十四份 claim 裡八份犯過這個病。
# **有 claim 就要有吐得出那個碼的 subject**，否則 must_fail_exactly 釘不到東西。
碼_摘要不符 = "WORK_ORDER_DIGEST_MISMATCH"
碼_基準過期 = "STALE_BASE_COMMIT"
碼_綱要未知 = "UNKNOWN_SCHEMA_REVISION"
碼_範圍重疊 = "FILES_SCOPE_OVERLAP_IN_BATCH"
碼_已凍結 = "WORKSHOP_FROZEN"
通過 = "OK"
專案根 = Path(__file__).resolve().parent.parent
計畫目錄 = 專案根 / "docs" / "計畫"


class 工單不可用(Exception):
    """typed 拒用。訊息一律以 failure code 起頭，讓負控釘得住紅因。"""


def _區段(計畫: str, task: int) -> tuple[str, str]:
    """取出某個 task 的原始區段文字與標題。直接切 `### Task N:`，不從別處推。"""
    檔 = next(計畫目錄.glob(f"{計畫}-*.md"), None)
    if 檔 is None:
        raise 工單不可用(f"plan_not_found：{計畫}")
    塊 = re.split(r"(?m)^### Task ", 檔.read_text(encoding="utf-8"))[1:]
    for 塊文 in 塊:
        if 塊文.split(":", 1)[0].strip() == str(task):
            return 塊文, 塊文.split("\n", 1)[0].split(":", 1)[1].strip()
    raise 工單不可用(f"task_not_found：{計畫} Task {task}")


def _摘要(文: str) -> str:
    return hashlib.sha256(文.encode("utf-8")).hexdigest()


def 生成(
    計畫: str, task: int, *, 基準: str, files_scope: list[str] | None = None
) -> dict[str, Any]:
    """把一個 task 區段做成封閉的工單。**工單是動態產物，不寫進版控。**

    `工坊/凍結.md` 存在時 typed 拒跑——**放一份文件說已凍結不能永久繞過退役**，
    所以旗標由工具自己認，不是靠人記得。
    """
    if (Path(__file__).resolve().parent / "凍結.md").is_file():
        raise 工單不可用(f"workshop_frozen：{碼_已凍結}：工坊已凍結，改走產品介面")
    區段文, 標題 = _區段(計畫, task)
    return {
        "schema_revision": SCHEMA_REVISION,
        "計畫": 計畫,
        "task": task,
        "標題": 標題,
        "來源摘要": _摘要(區段文),
        "base_commit_sha": 基準,
        "files_scope": files_scope or [],
    }


def 消費(單: dict[str, Any], *, 工作樹基準: str) -> dict[str, Any]:
    """三驗：綱要版本、重讀重算摘要、工作樹基準。任一不符 typed 拒。"""
    if 單.get("schema_revision") != SCHEMA_REVISION:
        raise 工單不可用(f"unknown_schema_revision：{碼_綱要未知}：{單.get('schema_revision')}")
    區段文, 標題 = _區段(str(單["計畫"]), int(單["task"]))
    if _摘要(區段文) != 單.get("來源摘要") or 標題 != 單.get("標題"):
        raise 工單不可用(f"work_order_digest_mismatch：{碼_摘要不符}——工單與來源區段對不上")
    if 單.get("base_commit_sha") != 工作樹基準:
        raise 工單不可用(
            f"stale_base_commit：{碼_基準過期}："
            f"工單基準 {單.get('base_commit_sha')} ≠ 工作樹 {工作樹基準}"
        )
    return 單


def 檢查批次(批: list[dict[str, Any]]) -> None:
    """同一 batch 內 `files_scope` 不得重疊。

    **跨 batch／跨程序刻意不防**（sol 2026-08-28 接受）：active registry 加 owner
    與生命期**就是 lease 機制**，那是產品 Work 的地盤；殼長那個狀態就變成
    第二個 harness。`從簡:` 天花板是開發期由控制端逐批派工，batch 界即實用界。
    """
    已佔: set[str] = set()
    for 單 in 批:
        範圍 = {str(x) for x in 單.get("files_scope", [])}
        if 撞 := 範圍 & 已佔:
            raise 工單不可用(f"files_scope_overlap_in_batch：{碼_範圍重疊}：{sorted(撞)}")
        已佔 |= 範圍
