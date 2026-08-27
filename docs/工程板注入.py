"""把 `工程板資料.py` 的輸出注入 `工程板.html` 的數字欄位。

**存在理由（2026-08-28 實測）**：交接 §二十二 記著「JSON→HTML 注入仍是手動」。
計畫 01 拆分改號那次正好證明手動會漏——工程板變成改號前的**第二個真相**
（頁首寫 188 任務、計畫 01 寫 18 task、閘列成 Task 13、缺新 Task 12），
而七道閘全綠，沒有任何機制會說。

**這支只換算得出來的數字**：頁首、統計卡九格、Phase 小計與 chip 分母、
各計畫列、22 張詳細卡的 `pmeta`。

**它明講不碰的**：各 task 的精選敘述與負控文字是**策展**不是全集——
它挑重點講、不逐條列，改號時要人自己同步。這句寫在這裡是因為漏報比誤報糟。

## 這支自己踩過的三個坑，都寫成了機制

1. **全域錨跨結構覆蓋。** `進行中 N／M` 的分母被跨列覆蓋（Phase A 與計畫 01 的
   `done` 都是 12），`pmeta` 被跨卡覆蓋（把 05 的數字寫進 06）。
   **同一份文件裡兩個結構共用一種樣式時，全域錨一定會撞。** 現在逐 `<tr>`、
   逐 `<details class="plan">` 處理，並驗結構本身。
2. **穩定的假綠。** 跨卡覆蓋後**第二次注入不再改動、`--檢查` 判成一致**——
   寫錯之後自我認證為正確，比一次性寫錯貴得多。
3. **驗存在不驗執法。** 只確認 `pmeta` 錨出現一次，沒確認 `re.sub` 真的命中——
   把 `task` 改成 `tasks` 而保留 class，注入器靜默不動、`--檢查` 說一致。
   現在用 `subn` 斷言替換數恰為 1。

**期望值不能自我指涉。** 頁首原本記 git HEAD，而 commit 板面又會改變 HEAD——
`--檢查` 在乾淨的 committed tip 上**必定紅**，那個檢查在設計上永遠不可能綠。
改用來源內容摘要：計畫沒變它就不變，板面 commit 幾次都一樣。

用法：`uv run python docs/工程板注入.py`；`--檢查` 只回報差異不寫檔。
"""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

根 = Path(__file__).resolve().parent.parent
板 = 根 / "docs" / "工程板.html"

階段成員 = {
    "Phase A": ["01", "01B", "02", "03", "04"],
    "Phase B": ["05", "06", "06B", "07", "08", "09", "10", "11", "12"],
    "Phase C": ["13", "14", "15", "16", "17", "18"],
    "Phase D": ["19", "20"],
}

卡樣式 = r'<details class="plan">.*?</details>'
片樣式 = r'<span class="pmeta"><b>\d+</b> task · <b>\d+</b> step · <b>\d+</b> 負控</span>'


def 來源摘要() -> str:
    """`docs/計畫/*.md` 內容的摘要前七碼——**不用 git HEAD**（見模組 docstring）。"""
    h = hashlib.sha256()
    for f in sorted((根 / "docs" / "計畫").glob("*.md")):
        h.update(f.read_bytes())
    return h.hexdigest()[:7]


def 取資料() -> dict:
    """跑 `工程板資料.py`。**它自己會在不變式紅時拋**，這裡不必再驗一次。"""
    出 = subprocess.run(
        [sys.executable, str(根 / "docs" / "工程板資料.py")],
        capture_output=True,
        text=True,
        check=False,
    )
    if 出.returncode != 0:
        raise SystemExit(f"工程板資料.py 非零，拒絕注入：\n{出.stderr}")
    return json.loads(出.stdout)


def 換頁首(文: str, 統: dict) -> str:
    """頁首那一行。"""
    return re.sub(
        r'(<span class="sub">)\d+ 子系統 · \d+ 任務 · 已交付 \d+／\d+ · 生成自 ([^@]*)@ \w+',
        rf"\g<1>{統['計畫']} 子系統 · {統['task']} 任務 · "
        rf"已交付 {統['交付']}／{統['task']} · 生成自 \g<2>@ {來源摘要()}",
        文,
    )


def 換統計卡(文: str, 統: dict) -> str:
    """統計卡九格：以中文標籤當錨，不做全域數字取代。"""
    for 值, 標 in [
        (統["計畫"], "子系統計畫"),
        (統["task"], "任務"),
        (統["步"], "步驟"),
        (統["建"], "待建檔案"),
        (統["交付"], "已交付任務"),
        (統["負控"], "固定負控"),
        (統["claim"], "實存 claim 檔"),
        (統["未遷移"], "落點未遷移"),
    ]:
        文 = re.sub(rf"<b>\d+</b><span>{re.escape(標)}</span>", f"<b>{值}</b><span>{標}</span>", 文)
    return 文


def 換階段列(列: str, 表: dict) -> str:
    """Phase 小計與 chip 分母。**以整列為界**——全域錨會跨列覆蓋。"""
    名 = re.search(r'<td class="ph">(Phase [A-D])</td>', 列)
    if not 名 or 名.group(1) not in 階段成員:
        return 列
    成員 = 階段成員[名.group(1)]
    t = sum(len(表[i]["tasks"]) for i in 成員)
    b = sum(表[i]["步"] for i in 成員)
    列 = re.sub(
        r'<td class="num">\d+</td><td class="num">\d+</td>',
        f'<td class="num">{t}</td><td class="num">{b}</td>',
        列,
        count=1,
    )
    return re.sub(r"(進行中 \d+／)\d+", rf"\g<1>{t}", 列)


def 換計畫列(列: str, 表: dict) -> str:
    """進度表的計畫列。**以整列為界**，理由同上。"""
    pid = re.search(r'<td class="pid2">([0-9]{2}[A-Z]?)</td>', 列)
    if not pid or pid.group(1) not in 表:
        return 列
    p = 表[pid.group(1)]
    列 = re.sub(
        r'<td class="num">\d+</td><td class="num">\d+</td>',
        f'<td class="num">{len(p["tasks"])}</td><td class="num">{p["步"]}</td>',
        列,
        count=1,
    )
    return re.sub(r"(進行中 \d+／)\d+", rf"\g<1>{len(p['tasks'])}", 列)


def 換卡(卡: str, 表: dict, 見過: set[str]) -> str:
    """一張計畫詳細卡。**同時驗結構**——結構不符就拒絕，不猜。"""
    ids = re.findall(r'<span class="pid">([0-9]{2}[A-Z]?)</span>', 卡)
    metas = re.findall(r'<span class="pmeta">', 卡)
    if len(ids) != 1 or len(metas) != 1:
        raise SystemExit(f"一張卡有 {len(ids)} 個 pid、{len(metas)} 個 pmeta——結構不符，拒絕注入")
    pid = ids[0]
    if pid in 見過:
        raise SystemExit(f"計畫 {pid} 出現在兩張卡——結構不符，拒絕注入")
    見過.add(pid)
    if pid not in 表:
        raise SystemExit(f"卡上的計畫 {pid} 不在資料裡——結構不符，拒絕注入")
    p = 表[pid]
    新卡, n = re.subn(
        片樣式,
        f'<span class="pmeta"><b>{len(p["tasks"])}</b> task · '
        f"<b>{p['步']}</b> step · <b>{p['neg']}</b> 負控</span>",
        卡,
        count=1,
    )
    if n != 1:
        raise SystemExit(f"計畫 {pid} 的 pmeta 錨在、但內容格式不符，替換 0 命中——拒絕注入")
    return 新卡


def 注入(文: str, 料: dict) -> str:
    """逐欄替換。每一條都以**結構為界**，不做全域數字取代。"""
    表 = {p["id"]: p for p in 料["計畫"]}
    卡數 = len(re.findall(卡樣式, 文, flags=re.S))
    if 卡數 != len(表):
        raise SystemExit(f"工程板有 {卡數} 張計畫卡，資料有 {len(表)} 份——結構不符，拒絕注入")

    文 = 換頁首(文, 料["統"])
    文 = 換統計卡(文, 料["統"])
    文 = re.sub(
        r'<tr class="phase-row">.*?</tr>', lambda m: 換階段列(m.group(0), 表), 文, flags=re.S
    )
    文 = re.sub(
        r'<tr(?! class="phase-row").*?</tr>', lambda m: 換計畫列(m.group(0), 表), 文, flags=re.S
    )
    見過: set[str] = set()
    文 = re.sub(卡樣式, lambda m: 換卡(m.group(0), 表, 見過), 文, flags=re.S)
    缺 = set(表) - 見過
    if 缺:
        raise SystemExit(f"這些計畫沒有卡：{sorted(缺)}——結構不符，拒絕注入")
    return 文


def main() -> int:
    """入口：注入，或以 `--檢查` 只回報板面是否落後。"""
    料 = 取資料()
    舊 = 板.read_text(encoding="utf-8")
    新 = 注入(舊, 料)
    if "--檢查" in sys.argv[1:]:
        if 舊 == 新:
            print("工程板數字與資料一致")
            return 0
        print("工程板數字落後於資料——跑 `uv run python docs/工程板注入.py`", file=sys.stderr)
        return 1
    板.write_text(新, encoding="utf-8")
    統 = 料["統"]
    print(f"已注入：{統['task']} task · {統['步']} step · {統['負控']} 負控 · @ {來源摘要()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
