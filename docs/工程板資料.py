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
「計畫是自洽的」，若 I1-I14 沒過，那句話就是假的，寧可不出。
"""

from __future__ import annotations

import importlib.util
import json
import pathlib
import re
import subprocess
import sys
import types

根 = pathlib.Path(__file__).resolve().parent.parent

# 橫軸是圖的架構策展，數字不是。每條規則只描述一格包哪些 Create 路徑；
# 總數、已建數、建立計畫與顯示狀態全由下方的封閉分類算出。`*` 是本層剩餘路徑。
分層模組規則: dict[str, dict[str, tuple[str, ...]]] = {
    "介面": {
        "命令列": ("nova/介面/命令列/",),
        "程式介面": ("nova/介面/程式介面/",),
        "HTTP": ("nova/介面/HTTP/",),
        "MCP": ("nova/介面/MCP/",),
    },
    "應用": {
        "處理（CommandBus）": (
            "nova/應用/處理/",
            "nova/應用/命令.py",
            "nova/應用/登錄.py",
            "nova/應用/邊界.py",
            "nova/應用/test_邊界.py",
        ),
        "工作單元": ("*",),
    },
    "領域": {
        "工作": ("nova/領域/工作/",),
        "追求": ("nova/領域/追求/",),
        "執行": ("nova/領域/執行/",),
        "提示": ("nova/領域/提示/",),
    },
    "權威": {
        "判準": ("nova/權威/判準/",),
        "資源": ("nova/權威/資源/",),
        "效果": ("nova/權威/效果/",),
        "知識": ("nova/權威/知識/",),
        "評測": ("nova/權威/評測/",),
    },
    "維護": {
        "複雜度訊號": ("nova/維護/複雜度訊號.py", "nova/維護/test_訊號與提案.py"),
        "審查提案": ("nova/維護/審查提案.py",),
    },
    "狀態機": {
        "編譯": tuple(
            f"nova/狀態機/{x}"
            for x in (
                "編譯.py",
                "載入.py",
                "模型.py",
                "檢查.py",
                "test_檢查.py",
                "遷移.py",
                "決策表.py",
            )
        ),
        "轉移目錄": tuple(
            f"nova/狀態機/{x}" for x in ("目錄.py", "test_目錄.py", "執行.py", "test_執行.py")
        ),
        "GraphIR": ("nova/狀態機/組圖.py",),
    },
    "約束": {
        "公開契約": ("nova/約束/公開契約.py",),
        "載入": ("nova/約束/載入.py",),
        "範圍": ("nova/約束/範圍.py",),
        "編譯": ("nova/約束/編譯.py", "nova/約束/test_語言.py"),
    },
    "介接": {
        "執行者後端": ("nova/介接/執行者後端/",),
        "效果端點": ("nova/介接/效果端點/",),
    },
    "基礎設施": {
        名: (f"nova/基礎設施/{名}/",)
        for 名 in (
            "狀態庫",
            "事件流",
            "內容庫",
            "知識索引",
            "排程",
            "效果轉送",
            "備份",
            "裁定執行",
            "系統",
        )
    },
    "內容庫": {
        "參照": ("nova/內容庫/參照.py", "nova/內容庫/test_契約.py"),
        "端口": ("nova/內容庫/端口.py",),
    },
    "證據庫": {
        "紀錄": ("nova/證據庫/紀錄.py", "nova/證據庫/test_不可覆寫.py"),
        "端口": ("nova/證據庫/端口.py",),
    },
    "核心": {
        "識別": ("nova/核心/識別.py", "nova/核心/test_值型別.py"),
        "摘要": ("nova/核心/摘要.py",),
        "時間": ("nova/核心/時間.py",),
        "錯誤": ("nova/核心/錯誤.py",),
        "工具鏈守衛": ("nova/核心/工具鏈守衛.py",),
        "事件": ("nova/核心/事件.py",),
    },
    "啟動": {"組裝根": ("*",), "規格目錄": ()},
}


def 載入複驗() -> types.ModuleType:
    """Import 執法器本身，讓「哪些檔算計畫」只有一個定義。"""
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
    統計行 = next(行 for 行 in 出.stdout.splitlines() if 行.startswith("統計 "))
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


def 抽計畫(複驗: types.ModuleType) -> list[dict]:
    """逐份計畫抽 task、步驟、負控與交付狀態。

    **這裡算的是 `files_present`，不是驗收。** 兩者不可互相冒充——
    sol 2026-08-28 指出：只要宣告的 Create 檔全存在就算交付，等於把
    「東西在」當成「東西對」。而本檔自己的下一句就寫著「不看任何人的自報」
    ——**檔案存在也是一種自報**，只是報的人是檔案系統。

    真正的驗收是 ClaimSpec 閘，而它至今零執行（`跑驗收.py` 回
    `UNSUPPORTED_CLAIM_EXECUTION`，01 Task 12 未接線）。所以板面
    只能說「宣告的檔都在」，不能說「驗收過了」。
    不看 commit 訊息、不看任何人的自報——那正是這個專案不接受的東西。
    """
    出 = []
    for f in sorted(複驗.計畫檔(), key=lambda x: 複驗.序位(複驗.編號(x))):
        s = pathlib.Path(f).read_text(encoding="utf-8")
        編 = 複驗.編號(f)
        # **Goal 可能跨多行**：`06B` 的目標寫了三行，而第一版的 `(.+)$` 只抓一行
        # ——板面於是顯示成一句逗號結尾的殘句（sol 第四十五輪第 11 條）。
        # 抓到下一個空行為止，再把換行併成單行。
        目標 = re.search(r"^\*\*Goal:\*\*\s*(?:【推論】)?(.+?)(?=\n\n)", s, re.M | re.S)
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
                    "st": (
                        "na"
                        if not 建
                        else ("done" if 有 == len(建) else ("part" if 有 else "todo"))
                    ),
                }
            )
        出.append(
            {
                "id": 編,
                "name": pathlib.Path(f).name[len(編) + 1 : -3],
                "goal": " ".join(目標.group(1).split()) if 目標 else "",
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
    樣 = (
        r"\| (R\d+-\d+)\(\w+\)([^|]*)\|\s*(APPROVE|REJECT)\s*\|"
        r"\s*(APPROVE|REJECT)\s*\|\s*\*?\*?(\w+)"
    )
    return [
        {"id": m[0], "t": m[1].strip().strip("|").strip(), "c": m[2], "s": m[3], "r": m[4]}
        for m in re.findall(樣, 帳)
    ]


def 範圍說明(層: str, 規則: tuple[str, ...]) -> str:
    """把模組分類規則轉成 tooltip 的人可讀範圍；數字不從這句話解析。"""
    if not 規則:
        return "沒有對應的 nova/ 檔"
    if 規則 == ("*",):
        return "該層其餘檔案"
    前綴 = f"nova/{層}/"
    return "、".join(x.removeprefix(前綴) for x in 規則)


def 抽層() -> dict[str, dict]:
    """每個 nova 第一層目錄與子模組的「已建／宣告要建」。

    **為什麼要機械算**：分層圖的 `0/N` 原本是手寫的，沒有任何程式在管。
    2026-08-28 對照發現四層過期，其中兩層是**已建的檔沒被算進去**
    （權威 1/44 而實際 4/52、基礎設施 0/45 而實際 5/46）——
    板面把已完成的工作顯示成沒做。

    分母是計畫的 `Create:` 條目數，分子是那些路徑目前真的存在。
    直接列舉 `nova/` 開頭的 Create 條目，不從別的型別推。橫軸每條路徑也必須
    恰好落在一個模組；漏分、重複分類或圖漏一層都拒絕出資料。
    """
    建: list[tuple[str, str]] = []
    for f in sorted((根 / "docs" / "計畫").glob("*.md")):
        編 = f.name.split("-", 1)[0]
        建 += [(編, x) for x in re.findall(r"^- Create: `(nova/[^`]+)`", f.read_text(), re.M)]
    層們 = {x.split("/")[1] for _, x in 建}
    if 層們 != set(分層模組規則):
        raise SystemExit(
            f"分層圖與 Create 層集合不符：漏 {sorted(層們 - 分層模組規則.keys())}、"
            f"多 {sorted(分層模組規則.keys() - 層們)}"
        )
    出: dict[str, dict] = {}
    for 層, 模規則 in 分層模組規則.items():
        本層 = {p: pid for pid, p in 建 if p.split("/")[1] == 層}
        未分 = set(本層)
        模們: dict[str, dict] = {}
        for 模名, 規則 in 模規則.items():
            if 規則 == ("*",):
                命中 = sorted(未分)
            else:
                命中 = sorted(
                    p
                    for p in 本層
                    if any(p.startswith(x) if x.endswith("/") else p == x for x in 規則)
                )
            重 = set(命中) - 未分
            if 重:
                raise SystemExit(f"分層圖 {層}／{模名} 重複分到 {sorted(重)}")
            if 規則 and not 命中:
                raise SystemExit(f"分層圖 {層}／{模名} 的分類規則沒有對應 Create 路徑")
            未分 -= set(命中)
            已 = sum((根 / p).exists() for p in 命中)
            模們[模名] = {
                "have": 已,
                "need": len(命中),
                "plans": sorted({本層[p] for p in 命中}),
                "scope": 範圍說明(層, 規則),
            }
        if 未分:
            raise SystemExit(f"分層圖 {層} 有未分入模組的 Create 路徑：{sorted(未分)}")
        出[層] = {
            "have": sum(x["have"] for x in 模們.values()),
            "need": sum(x["need"] for x in 模們.values()),
            "plans": sorted(set(本層.values())),
            "modules": 模們,
        }
    return 出


def 主() -> None:
    """組合所有資料，以單一 JSON 物件輸出給注入器。"""
    複驗 = 載入複驗()
    統計, _ = 跑執法器()
    計畫 = 抽計畫(複驗)
    統計["步"] = sum(p["步"] for p in 計畫)
    統計["負控"] = sum(p["neg"] for p in 計畫)
    統計["交付"] = sum(p["done"] for p in 計畫)
    # 「待建」是尚未存在的那些，不是 Create 路徑總數——sol 2026-08-28 指出
    # 板上把 803 標成「待建檔案」，而其中 76 個已經建好了。
    統計["待建"] = sum(t["need"] - t["have"] for p in 計畫 for t in p["tasks"])
    統計["有負控段"] = sum(p["neg"] for p in 計畫)
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
