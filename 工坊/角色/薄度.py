"""AST 層的薄度檢查：殼不得長出 dispatch 邏輯。

**為什麼要自帶 import 檢查**：既有的 nova import checker **略過非 `nova.*` 模組**，
靠它抓不到 `import tenacity`。所以這裡用白名單制逐一檢查
`ast.Import`／`ImportFrom`。

**為什麼禁的是「迴圈內呼叫後端」而不是禁迴圈**（sol 第四十二輪接受的收窄）：
殼逐條驗 grant 本來就要純資料迴圈，**retry 的形狀是迴圈內呼叫後端**。
而且要涵蓋**經本檔 helper 的傳遞閉包**——迴圈裡呼叫 `_重試()`、
`_重試()` 內部才 `subprocess.run`，一樣是 retry。
"""

from __future__ import annotations

import ast
import hashlib
from pathlib import Path

行數上限 = 200
# 這些是 dispatch 的形狀，不是工具：裝上去就表示殼開始自己扛重試與排程。
凍結名單 = frozenset({"tenacity", "backoff", "asyncio", "threading", "sched", "concurrent"})
後端呼叫 = frozenset({"run", "Popen", "call", "check_output", "check_call"})


def 提示摘要(檔: Path) -> str:
    """提示是資料檔，取內容摘要——角色身分變更要可稽核。"""
    return hashlib.sha256(檔.read_bytes()).hexdigest()


def _頂層名(節點: ast.AST) -> str:
    while isinstance(節點, ast.Attribute):
        節點 = 節點.value
    return 節點.id if isinstance(節點, ast.Name) else ""


def _會碰後端的函式(樹: ast.Module) -> set[str]:
    """本檔內部**直接或間接**碰到後端的函式名——傳遞閉包，跑到不動為止。"""
    直接: set[str] = set()
    呼叫圖: dict[str, set[str]] = {}
    for 節點 in ast.walk(樹):
        if not isinstance(節點, ast.FunctionDef):
            continue
        呼叫圖[節點.name] = set()
        for 內 in ast.walk(節點):
            if not isinstance(內, ast.Call):
                continue
            if isinstance(內.func, ast.Attribute) and 內.func.attr in 後端呼叫:
                直接.add(節點.name)
            elif isinstance(內.func, ast.Name):
                呼叫圖[節點.name].add(內.func.id)
    會碰 = set(直接)
    變了 = True
    while 變了:
        變了 = False
        for 誰, 被叫 in 呼叫圖.items():
            if 誰 not in 會碰 and 被叫 & 會碰:
                會碰.add(誰)
                變了 = True
    return 會碰


def _查匯入(樹: ast.Module) -> list[str]:
    """白名單制逐一檢查——既有的 nova checker 略過非 `nova.*`，靠它抓不到。"""
    出: list[str] = []
    for 節點 in ast.walk(樹):
        if isinstance(節點, ast.Import):
            出 += [
                f"import 凍結名單模組 {別.name}"
                for 別 in 節點.names
                if 別.name.split(".")[0] in 凍結名單
            ]
        elif isinstance(節點, ast.ImportFrom) and (節點.module or "").split(".")[0] in 凍結名單:
            出.append(f"from 凍結名單模組 {節點.module} import")
    return 出


def _查迴圈內後端(樹: ast.Module) -> list[str]:
    """禁的是**迴圈體內呼叫後端**，不是禁迴圈——純資料迴圈合法。"""
    會碰 = _會碰後端的函式(樹)
    出: list[str] = []
    for 節點 in ast.walk(樹):
        if not isinstance(節點, ast.For | ast.While):
            continue
        for 內 in ast.walk(節點):
            if not isinstance(內, ast.Call):
                continue
            屬性名 = 內.func.attr if isinstance(內.func, ast.Attribute) else ""
            函式名 = 內.func.id if isinstance(內.func, ast.Name) else ""
            if 屬性名 in 後端呼叫 or 函式名 in 會碰:
                出.append(f"迴圈體內呼叫後端（{屬性名 or 函式名}）——那是 retry 的形狀")
    return 出


def _查睡與遞迴(樹: ast.Module) -> list[str]:
    出: list[str] = []
    for 節點 in ast.walk(樹):
        if (
            isinstance(節點, ast.Call)
            and isinstance(節點.func, ast.Attribute)
            and 節點.func.attr == "sleep"
        ):
            出.append("殼裡不得有 sleep")
        if isinstance(節點, ast.FunctionDef):
            出 += [
                f"遞迴呼叫 {節點.name}"
                for 內 in ast.walk(節點)
                if isinstance(內, ast.Call)
                and isinstance(內.func, ast.Name)
                and 內.func.id == 節點.name
            ]
    return 出


def 檢查(檔: Path) -> list[str]:
    """回傳問題清單；空清單代表這支殼還是薄的。"""
    源 = 檔.read_text(encoding="utf-8")
    樹 = ast.parse(源)
    超行 = [f"超過 {行數上限} 行絆線"] if len(源.splitlines()) > 行數上限 else []
    return 超行 + _查匯入(樹) + _查迴圈內後端(樹) + _查睡與遞迴(樹)
