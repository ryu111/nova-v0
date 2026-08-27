"""逐條套用**事前命名**的突變，跑宣告的指令，比對每條的宣告結果。

存在理由（2026-08-27 實測）：同一個動作我臨時手寫過六次，每次細節不同；其中一次的
計數腳本算錯了數字（206 而非 204）並且直接進了報告。臨時手寫的東西沒有測試、
沒有型別、不受任何閘管轄——`工具/` 的職責本來就是「薄入口」，不是每次重寫一遍。

**沒有擊殺率。** 輸出是逐條的名字與相符與否。等價突變讓百分比不可用，
唯一有意義的是「事前命名的這一條，實際結果與宣告的一樣嗎」——與計畫 01 Task 11 同一條原則。

**目標字串不存在要明講**：靜靜跳過會讓一條負控從此消失，而報告上還是綠的。
"""

from __future__ import annotations

import subprocess
import sys
import tomllib
from dataclasses import dataclass
from pathlib import Path

專案根 = Path(__file__).resolve().parent.parent
殺掉, 存活 = "殺掉", "存活"


@dataclass(frozen=True, slots=True)
class 一條:
    """一條事前命名的突變：改哪個檔的哪段字，以及**宣告**它會被殺還是存活。"""

    name: str
    file: Path
    old: str
    new: str
    expect: str


def 讀批次(路徑: Path) -> tuple[tuple[str, ...], tuple[一條, ...]]:
    """批次是資料：一行指令，加上若干條事前命名的突變。

    TOML bare key 只接受 ASCII，所以欄位名是 command／mutation／name／file／old／new／expect——
    那正是 CLAUDE.md 把 schema 欄位名列為 ASCII 例外的原因。
    """
    with 路徑.open("rb") as 檔:
        原始 = tomllib.load(檔)
    條們 = []
    for 項 in 原始["mutation"]:
        if 項["expect"] not in (殺掉, 存活):
            raise ValueError(f"{項['name']} 的 expect 只能是 {殺掉} 或 {存活}：{項['expect']}")
        條們.append(一條(項["name"], Path(項["file"]), 項["old"], 項["new"], 項["expect"]))
    return tuple(原始["command"]), tuple(條們)


def 工作樹乾淨() -> bool:
    """開跑前確認沒有未提交的改動——還原失敗時才看得出來是工具留下的。"""
    出 = subprocess.run(
        ["git", "status", "--porcelain"], cwd=專案根, capture_output=True, text=True, check=False
    )
    return 出.returncode == 0 and not 出.stdout.strip()


def 套一條(條: 一條, 指令: tuple[str, ...]) -> str:
    """套用、跑、還原。回實際結果（殺掉／存活）。還原走 finally，跑到一半爆掉也會還原。"""
    原文 = 條.file.read_text(encoding="utf-8")
    if 條.old not in 原文:
        raise LookupError(f"{條.name}：{條.file} 裡找不到目標字串——負控會靜默消失")
    條.file.write_text(原文.replace(條.old, 條.new, 1), encoding="utf-8")
    try:
        結果 = subprocess.run(指令, cwd=專案根, capture_output=True, check=False)
    finally:
        條.file.write_text(原文, encoding="utf-8")
    return 殺掉 if 結果.returncode != 0 else 存活


def 跑批次(批次檔: Path) -> int:
    """跑完整批，逐條印出宣告與實際，任一條不符即回非零。"""
    指令, 條們 = 讀批次(批次檔)
    倉內 = any(專案根 in 條.file.resolve().parents for 條 in 條們)
    if 倉內 and not 工作樹乾淨():
        print("工作樹不乾淨，先提交或還原再跑——否則分不出哪些改動是這支留下的", file=sys.stderr)
        return 2
    不符 = []
    for 條 in 條們:
        try:
            實際 = 套一條(條, 指令)
        except LookupError as 誤:
            print(f"[缺目標] {條.name}：{誤}", file=sys.stderr)
            不符.append(條.name)
            continue
        記 = "相符" if 實際 == 條.expect else "不符"
        print(f"[{記}] {條.name}：宣告 {條.expect}，實際 {實際}")
        if 實際 != 條.expect:
            不符.append(條.name)
    if 不符:
        print(f"\n{len(不符)} 條與宣告不符：{'、'.join(不符)}", file=sys.stderr)
    return 1 if 不符 else 0


if __name__ == "__main__":
    raise SystemExit(跑批次(Path(sys.argv[1])))
