"""把工程板要顯示的數字從 repo 抽出來，**不讓任何一個數字是手打的**。

存在理由：工程板原本是手工烘的快照。2026-08-28 實測，它停在
`21 子系統／177 任務／941 步驟／702 待建檔案`，而當時實際是 22／188／1000／761——
四個數字全錯，`06B` 整份計畫在板上命中 0，**而板子看起來完全正常**。
那是 CLAUDE.md 那條「只以文件形式存在的規範等於不存在」的展示版本：
只靠人記得要更新的快照，過期時沒有任何跡象。

**這支不重寫 `計畫複驗.py` 的算法，它 import 它。** 兩份拷貝遲早漂移，
而這個 repo 已經為此付過代價（claim.json 的 `claimed_path` 從頭到尾沒人讀，
真正被檢查的位置在別的檔案裡，兩份可以無聲不一致）。

**不變式紅就不出資料。** 這不是保守，是這支存在的意義：板上的數字宣稱
「計畫是自洽的」，若 I1–I11 沒過，那句話就是假的，寧可不出。
"""

from __future__ import annotations

import importlib.util
import json
import pathlib
import re
import subprocess
import sys

根 = pathlib.Path(__file__).resolve().parent.parent


def 載入複驗():
    """import 執法器本身，讓「哪些檔算計畫」只有一個定義。"""
    規 = importlib.util.spec_from_file_location("計畫複驗", 根 / "docs/計畫複驗.py")
    模 = importlib.util.module_from_spec(規)
    assert 規.loader is not None
    規.loader.exec_module(模)
    return 模


def 跑執法器() -> tuple[dict[str, int], str]:
    """跑一次 `計畫複驗.py`。**非零就拋**——不變式紅時不准出資料。"""
    出 = subprocess.run(
        [sys.executable, str(根 / "docs/計畫複驗.py")], capture_output=True, text=True, cwd=根
    )
    if 出.returncode != 0:
        raise SystemExit(
            "不變式沒過，拒絕產生工程板資料——板上的數字宣稱計畫是自洽的，"
            f"那句話現在是假的：\n{出.stdout}\n{出.stderr}"
        )
    統計行 = next(l for l in 出.stdout.splitlines() if l.startswith("統計 "))
    # 讀 key=value 的機器行，**不掃散文**。原本掃散文的 `\d+` 會被標籤裡的數字
    # 騙走（「I12 旗標債」的 12），整排位移一格——每個數字都錯、都合理、
    # 板上沒有任何跡象。改成具名之後，加新統計不會動到既有欄位。
    統計 = {}
    for 段 in 統計行.removeprefix("統計 ").split():
        鍵名, _, 值 = 段.partition("=")
        統計[鍵名] = int(值)
    缺 = {"計畫", "建", "task", "未遷移", "claim"} - 統計.keys()
    if 缺:
        raise SystemExit(f"統計行缺欄位 {sorted(缺)}——計畫複驗.py 改了輸出格式")
    return 統計, 出.stdout


def 抽計畫(複驗) -> list[dict]:
    """逐份計畫抽 task、步驟、負控與交付狀態。

    交付判定是**機械的**：該 task 宣告要 Create 的檔案全部存在才算 done。
    不看 commit 訊息、不看任何人的自報——那正是這個專案不接受的東西。
    """
    出 = []
    for f in sorted(複驗.計畫檔(), key=lambda x: 複驗.序位(複驗.編號(x))):
        s = pathlib.Path(f).read_text(encoding="utf-8")
        編 = 複驗.編號(f)
        目標 = re.search(r"^\*\*Goal:\*\*\s*(?:【推論】)?(.+)$", s, re.M)
        前置 = re.search(r"^前置計畫：(.+)$", s, re.M)
        ts, 步總 = [], 0
        for i, b in enumerate(re.split(r"^### Task ", s, flags=re.M)[1:], 1):
            標 = b.split("\n")[0].split(":", 1)
            建 = re.findall(r"^\s*-\s*Create:\s*`([^`]+)`", b, re.M)
            步 = len(re.findall(r"^- \[ \] \*\*Step ", b, re.M))
            步總 += 步
            有 = sum(1 for p in 建 if (根 / p).exists())
            ts.append(
                {
                    "n": i,
                    "t": (標[1] if len(標) > 1 else 標[0]).strip(),
                    "have": 有,
                    "need": len(建),
                    "st": "done" if 建 and 有 == len(建) else ("part" if 有 else "todo"),
                }
            )
        出.append(
            {
                "id": 編,
                "name": pathlib.Path(f).name[len(編) + 1 : -3],
                "goal": 目標.group(1).strip() if 目標 else "",
                "dep": 前置.group(1).strip() if 前置 else "無",
                "tasks": ts,
                "步": 步總,
                "neg": len(re.findall(r"\*\*固定負控:\*\*", s)),
                "done": sum(1 for t in ts if t["st"] == "done"),
            }
        )
    return 出


def 抽決議() -> list[dict]:
    """從決議帳本的表格列抽三方迴圈的票。帳本是資料，這裡只讀不解釋。"""
    帳 = (根 / "docs/決策/計畫修訂決議.md").read_text(encoding="utf-8")
    樣 = r"\| (R\d+-\d+)\(\w+\)([^|]*)\|\s*(APPROVE|REJECT)\s*\|\s*(APPROVE|REJECT)\s*\|\s*\*?\*?(\w+)"
    return [
        {"id": m[0], "t": m[1].strip().strip("|").strip(), "c": m[2], "s": m[3], "r": m[4]}
        for m in re.findall(樣, 帳)
    ]


def 抽層() -> dict[str, str]:
    """每個 nova 第一層目錄的「已建／宣告要建」。

    **為什麼要機械算**：分層圖的 `0/N` 原本是手寫的，沒有任何程式在管。
    2026-08-28 對照發現四層過期，其中兩層是**已建的檔沒被算進去**
    （權威 1/44 而實際 4/52、基礎設施 0/45 而實際 5/46）——
    板面把已完成的工作顯示成沒做。

    分母是計畫的 `Create:` 條目數，分子是那些路徑目前真的存在。
    直接列舉 `nova/` 開頭的 Create 條目，不從別的型別推。
    """
    建: list[str] = []
    for f in sorted((根 / "docs" / "計畫").glob("*.md")):
        建 += re.findall(r"^- Create: `(nova/[^`]+)`", f.read_text(encoding="utf-8"), re.M)
    層: dict[str, list[str]] = {}
    for 路徑 in 建:
        層.setdefault(路徑.split("/")[1], []).append(路徑)
    return {名: f"{sum(1 for x in 們 if (根 / x).exists())}/{len(們)}" for 名, 們 in 層.items()}


def 主() -> None:
    複驗 = 載入複驗()
    統計, _ = 跑執法器()
    計畫 = 抽計畫(複驗)
    統計["步"] = sum(p["步"] for p in 計畫)
    統計["負控"] = sum(p["neg"] for p in 計畫)
    統計["交付"] = sum(p["done"] for p in 計畫)
    print(
        json.dumps(
            {
                "統": 統計,
                "層": 抽層(),
                "計畫": 計畫,
                "決議": 抽決議(),
                "head": subprocess.run(
                    ["git", "rev-parse", "--short", "HEAD"],
                    capture_output=True,
                    text=True,
                    cwd=根,
                ).stdout.strip(),
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    主()
