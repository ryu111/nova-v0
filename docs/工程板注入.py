"""把 `工程板資料.py` 的輸出注入 `工程板.html` 的數字欄位。

**存在理由（2026-08-28 實測）**：交接 §二十二 記著「JSON→HTML 注入仍是手動」。
計畫 01 拆分改號那次正好證明手動會漏——工程板變成改號前的**第二個真相**
（頁首寫 188 任務、計畫 01 寫 18 task、閘列成 Task 13、缺新 Task 12），
而七道閘全綠，沒有任何機制會說。

**這支不會宣稱它涵蓋整個板面。** 它只換**算得出來的數字**：

- 頁首 `N 子系統 · N 任務 · 已交付 N／N · 生成自 ... @ <commit>`
- 統計卡九格
- 進度表的 Phase 小計與各計畫列
- 各計畫詳細卡的 `pmeta`（task／step／負控）
- Phase 進度 chip 的分母

**不碰的（明講，因為漏報比誤報糟）**：各 task 的精選敘述與負控文字是**策展**，
不是全集——它挑重點講，不逐條列。改號時要人自己同步，這支不會提醒你。
散文段落（`note`、`dep`）同理。

用法：`uv run python docs/工程板注入.py`；`--檢查` 只回報差異不寫檔。
"""

from __future__ import annotations

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


def 取資料() -> dict:
    """跑 `工程板資料.py`。**它自己會在不變式紅時拋**，所以這裡不必再驗一次。"""
    出 = subprocess.run(
        [sys.executable, str(根 / "docs" / "工程板資料.py")],
        capture_output=True,
        text=True,
        check=False,
    )
    if 出.returncode != 0:
        raise SystemExit(f"工程板資料.py 非零，拒絕注入：\n{出.stderr}")
    return json.loads(出.stdout)


def 注入(文: str, 料: dict) -> str:
    """逐欄替換。每一條都用**具名的錨**，不做全域數字取代。"""
    表 = {p["id"]: p for p in 料["計畫"]}
    統 = 料["統"]

    文 = re.sub(
        r'(<span class="sub">)\d+ 子系統 · \d+ 任務 · 已交付 \d+／\d+ · 生成自 ([^@]*)@ \w+',
        rf"\g<1>{統['計畫']} 子系統 · {統['task']} 任務 · "
        rf"已交付 {統['交付']}／{統['task']} · 生成自 \g<2>@ {料['head']}",
        文,
    )

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

    # **逐 `<tr>` 處理。** 第一版用全域正則，結果 Phase A 與計畫 01 的 `done` 都是 12，
    # `進行中 12／N` 的分母被跨列覆蓋（計畫 01 的 20 被寫成 Phase A 的 49）。
    # 同一份文件裡兩個結構共用一種樣式時，全域錨一定會撞。
    def 換階(m: re.Match[str]) -> str:
        列 = m.group(0)
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

    文 = re.sub(r'<tr class="phase-row">.*?</tr>', 換階, 文, flags=re.S)

    def 換列(m: re.Match[str]) -> str:
        列 = m.group(0)
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

    文 = re.sub(r'<tr(?! class="phase-row").*?</tr>', 換列, 文, flags=re.S)

    # **逐 `<details class="plan">` 處理，並斷言結構完整。**
    # 第一版用 `pid` 加 `.*?` 找下一個 `pmeta`，**沒有以卡為邊界**——
    # sol 實測把 05 的錨改壞後，05 的數字被寫進 06，而**第二次注入不再改動、
    # `--檢查` 判成一致：穩定的假綠**。那比一次性寫錯更糟。
    # 這是「全域替換不看結構邊界」在本檔的第二次發作（第一次是 `進行中 N／M`
    # 的分母被跨列覆蓋），所以這裡除了收邊界，還要**驗結構本身**。
    卡們 = re.findall(r'<details class="plan">.*?</details>', 文, flags=re.S)
    if len(卡們) != len(表):
        raise SystemExit(
            f"工程板有 {len(卡們)} 張計畫卡，資料有 {len(表)} 份計畫——結構不符，拒絕注入"
        )
    見過: set[str] = set()

    def 換卡(m: re.Match[str]) -> str:
        卡 = m.group(0)
        ids = re.findall(r'<span class="pid">([0-9]{2}[A-Z]?)</span>', 卡)
        metas = re.findall(r'<span class="pmeta">', 卡)
        if len(ids) != 1 or len(metas) != 1:
            raise SystemExit(
                f"一張卡有 {len(ids)} 個 pid、{len(metas)} 個 pmeta——結構不符，拒絕注入"
            )
        pid = ids[0]
        if pid in 見過:
            raise SystemExit(f"計畫 {pid} 出現在兩張卡——結構不符，拒絕注入")
        見過.add(pid)
        if pid not in 表:
            raise SystemExit(f"卡上的計畫 {pid} 不在資料裡——結構不符，拒絕注入")
        p = 表[pid]
        return re.sub(
            r'<span class="pmeta"><b>\d+</b> task · <b>\d+</b> step · <b>\d+</b> 負控</span>',
            f'<span class="pmeta"><b>{len(p["tasks"])}</b> task · '
            f"<b>{p['步']}</b> step · <b>{p['neg']}</b> 負控</span>",
            卡,
            count=1,
        )

    文 = re.sub(r'<details class="plan">.*?</details>', 換卡, 文, flags=re.S)
    缺 = set(表) - 見過
    if 缺:
        raise SystemExit(f"這些計畫沒有卡：{sorted(缺)}——結構不符，拒絕注入")
    return 文


def main() -> int:
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
    print(f"已注入：{統['task']} task · {統['步']} step · {統['負控']} 負控 · @ {料['head']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
