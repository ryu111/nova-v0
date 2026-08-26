"""事前固定的錯誤 subject：一個 SQLite repository 被宣稱放在 nova/應用/。

宣稱落點: nova/應用/工作倉庫.py

repository 是 DB port implementation，落點必須是 nova/基礎設施/；放進 nova/應用/
會讓 use-case choreography 這一層直接持有 I/O，checker 必須回 PLACEMENT_LAYER_MISMATCH。
"""

import sqlite3


class 工作倉庫:
    """以 SQLite 持久化 Work aggregate 的 repository。"""

    def __init__(self, 連線: sqlite3.Connection) -> None:
        """記住外部注入的連線。"""
        self._連線 = 連線

    def 讀取(self, 識別: str) -> tuple[object, ...] | None:
        """依主鍵讀回一列，找不到時回 None。"""
        游標 = self._連線.execute("SELECT * FROM work WHERE work_id = ?", (識別,))
        return 游標.fetchone()
