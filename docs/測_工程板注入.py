"""工程板注入器的結構負控。

**存在理由**：這支注入器被 sol 退了四輪，每一輪都是同一個病的更深一層——
①跨列覆蓋 → ②跨卡覆蓋且**穩定成假綠** → ③錨在但內容格式壞掉而 0 命中 →
④`count=1` 讓重複錨抓不到、外層 `re.sub` 完全不驗「該遍歷的結構有沒有被遍歷」。

**每一輪我修的都是被回報的那個實例，而不是那個形狀。**
這個檔的存在就是為了讓形狀有牙：**下一個人改注入器時，這些格會替 sol 說話。**

八道閘裡的 `pytest` 會跑到這裡；另有 `board` 一閘直接跑 `--檢查`。
目前有十二格結構負控，再加上乾淨板面防恆真與三格同源正控。
"""

from __future__ import annotations

import copy
import importlib.util
import pathlib
import re
import sys
from collections.abc import Callable

import pytest

根 = pathlib.Path(__file__).resolve().parent.parent
規 = importlib.util.spec_from_file_location("工程板注入", 根 / "docs" / "工程板注入.py")
assert 規 and 規.loader
注入器 = importlib.util.module_from_spec(規)
sys.modules["工程板注入"] = 注入器
規.loader.exec_module(注入器)


@pytest.fixture(scope="module")
def 料() -> dict:
    """真實資料——負控要打在真板面上，不是打在簡化模型上。"""
    return 注入器.取資料()


@pytest.fixture
def 板文() -> str:
    """目前的板面內容。"""
    return (根 / "docs" / "工程板.html").read_text(encoding="utf-8")


def 測試_乾淨板面注入後不再改動(板文: str, 料: dict) -> None:
    """防恆真格：**沒有這格，下面每一格都能靠「永遠拒絕」通過。**"""
    assert 注入器.注入(板文, 料) == 板文


def 測試_分層資料的子模組無缺無重複(料: dict) -> None:
    """子模組不是另一套口徑：每層模組小計必須恰好等於層總數。"""
    for 名, 層 in 料["層"].items():
        assert sum(模["need"] for 模 in 層["modules"].values()) == 層["need"], 名
        assert sum(模["have"] for 模 in 層["modules"].values()) == 層["have"], 名
    assert "提示" in 料["層"]["領域"]["modules"]
    assert "評測" in 料["層"]["權威"]["modules"]


def 測試_分層圖的可計算事實全部同步(板文: str, 料: dict) -> None:
    """tooltip、子模組、邊框、進度條與全體小計必須與左側數字同源。"""
    新 = 注入器.注入(板文, 料)
    總已 = sum(層["have"] for 層 in 料["層"].values())
    總需 = sum(層["need"] for 層 in 料["層"].values())
    assert f"全體 <b>{總已}／{總需}</b>" in 新
    for 名, 層 in 料["層"].items():
        態 = 注入器.狀態字(層["have"], 層["need"])
        色 = "var(--綠)" if 態 == "done" else ("var(--琥)" if 態 == "ing" else "currentColor")
        assert f"計畫宣告 {層['need']} 個檔，已建立 {層['have']} 個" in 新
        assert re.search(
            rf'class="lay-{態}" data-layer="{re.escape(名)}".*?'
            rf'fill="{re.escape(色)}"[^>]*>{re.escape(名)}</text>',
            新,
            re.S,
        )
        寬 = 注入器.進度條寬(層["have"], 層["need"])
        assert re.search(
            rf'data-layer="{re.escape(名)}".*?class="bar-progress [^"]+"[^>]*width="{寬}"',
            新,
            re.S,
        )
        for 模名, 模 in 層["modules"].items():
            assert f"{名}／{模名}：計畫宣告 {模['need']} 個檔，已建立 {模['have']} 個" in 新
            模態 = 注入器.狀態字(模["have"], 模["need"])
            assert re.search(
                rf'class="[^"]*mod-{模態}[^"]*"[^>]*><title>{re.escape(名)}／{re.escape(模名)}：',
                新,
            )


def 測試_計畫列與詳細卡的事實由資料接管(板文: str, 料: dict) -> None:
    """名稱、前置、goal、task 標題與檔案存在狀態都可機械導出，不得留在策展半邊。"""
    改 = copy.deepcopy(料)
    計畫 = next(p for p in 改["計畫"] if p["id"] == "05")
    計畫["name"] = "測試計畫名"
    計畫["dep"] = "01 01B TEST"
    計畫["goal"] = "測試 goal 由資料注入"
    計畫["tasks"][0]["t"] = "測試 task 標題由資料注入"
    計畫["tasks"][0]["st"] = "done"
    計畫["tasks"][0]["have"] = 計畫["tasks"][0]["need"]
    計畫["done"] = 1
    新 = 注入器.注入(板文, 改)
    assert "測試計畫名" in 新
    assert "01 01B TEST" in 新
    assert "測試 goal 由資料注入" in 新
    assert "測試 task 標題由資料注入" in 新
    assert "宣告檔齊" in 新


@pytest.mark.parametrize(
    ("名", "壞掉"),
    [
        # ① 錨消失
        # 這格刻意**不寫死任務數**：第一版寫「194 任務」，計畫 01C 進來後變 198，
        # 於是 fixture 的替換不再命中、負控靜靜失效。壞的是 fixture 不是生產碼。
        ("頁首標籤改名", lambda s: re.sub(r"(子系統 · \d+) 任務 ·", r"\1 tasks ·", s, count=1)),
        (
            "統計卡標籤改名",
            # 用注入器**現在**管的任一標籤即可；不寫死已改名的舊標籤
            # ——2026-08-28「固定負控」正名成「有負控段的任務」時，
            # 這格的替換不再命中、負控靜靜失效。與「194 任務」那次同病。
            lambda s: s.replace("<span>子系統計畫</span>", "<span>子系統計畫們</span>", 1),
        ),
        # ② 錨重複——`count=1` 抓不到的那一類
        (
            "頁首錨重複",
            lambda s: (
                s[: s.index("</span>", s.index('<span class="sub">')) + 7]
                + s[
                    s.index('<span class="sub">') : s.index(
                        "</span>", s.index('<span class="sub">')
                    )
                    + 7
                ]
                + s[s.index("</span>", s.index('<span class="sub">')) + 7 :]
            ),
        ),
        # ③ owned 結構未被遍歷——外層 selector 或身分錨被改名
        (
            "Phase 身分錨改名",
            lambda s: s.replace('<td class="ph">Phase B</td>', '<td class="ph">Phase Z</td>', 1),
        ),
        (
            "計畫列 selector 改名",
            lambda s: s.replace('<td class="pid2">05</td>', '<td class="pid3">05</td>', 1),
        ),
        (
            "計畫卡 pid 改名",
            lambda s: s.replace('<span class="pid">08</span>', '<span class="pidx">08</span>', 1),
        ),
        (
            "計畫卡 pid 重複",
            lambda s: s.replace('<span class="pid">06</span>', '<span class="pid">05</span>', 1),
        ),
        # ④ **完整合法集合，另加一列非法**——擷取若過濾格式就抓不到「多出」
        (
            "額外 Phase Z 列",
            lambda s: (
                s[
                    : s.index("</tr>", s.index('<tr class="phase-row"><td class="ph">Phase D</td>'))
                    + 5
                ]
                + s[
                    s.index('<tr class="phase-row"><td class="ph">Phase D</td>') : s.index(
                        "</tr>", s.index('<tr class="phase-row"><td class="ph">Phase D</td>')
                    )
                    + 5
                ].replace("Phase D", "Phase Z")
                + s[
                    s.index("</tr>", s.index('<tr class="phase-row"><td class="ph">Phase D</td>'))
                    + 5 :
                ]
            ),
        ),
        (
            "額外 pid2=ZZ 列",
            lambda s: (
                s[: s.index("</tr>", s.index('<td class="pid2">20</td>')) + 5]
                + s[
                    s.rindex("<tr", 0, s.index('<td class="pid2">20</td>')) : s.index(
                        "</tr>", s.index('<td class="pid2">20</td>')
                    )
                    + 5
                ].replace(">20<", ">ZZ<")
                + s[s.index("</tr>", s.index('<td class="pid2">20</td>')) + 5 :]
            ),
        ),
        # ⑤ 錨在、內容格式壞掉——0 命中而靜默跳過的那一類
        (
            "pmeta 內容格式壞掉",
            lambda s: s.replace("</b> task · ", "</b> tasks · ", 1),
        ),
        (
            "分層子模組改名",
            lambda s: s.replace("權威／判準：", "權威／判定：", 1),
        ),
        (
            "分層進度條 selector 改名",
            lambda s: s.replace('class="bar-progress bar-ing"', 'class="bar-lost bar-ing"', 1),
        ),
    ],
)
def 測試_板面結構壞掉必須拒絕注入(板文: str, 料: dict, 名: str, 壞掉: Callable[[str], str]) -> None:
    """十二格結構負控。

    **每一格都必須 `SystemExit`，不能只是「注入後沒變」**——
    靜默不動正是這支工具前三輪的病：它會穩定成假綠。
    """
    with pytest.raises(SystemExit) as 誤:
        注入器.注入(壞掉(板文), 料)
    assert "拒絕注入" in str(誤.value), f"{名}：拒絕了但訊息沒說明原因"


# ── HTML 結構（sol 第四十五輪第 20 條） ─────────────────────────────
#
# **發作**：板面長期沒有 `<!doctype html><html><head>`，卻先出現 `</head>`；
# Google Fonts 的 `&` 未編碼。瀏覽器靠 quirks mode 容錯，所以**看起來正常**
# ——而「看起來正常」正是這塊板最不該有的性質：它是使用者唯一看得到的東西。
#
# sol 在第四十六輪的短設計裡說要「用 HTML 結構測試釘住 doctype/head/body
# 與標籤平衡」，但實作時沒做。**沒有負控的修法等於沒修**，所以補在這裡。

板面路徑 = pathlib.Path(__file__).resolve().parent / "工程板.html"


def test_板面是合法的_HTML_文件() -> None:
    """開頭四件與結尾兩件，缺一不可。"""
    文 = 板面路徑.read_text(encoding="utf-8")
    頭 = 文.lstrip()[:200]
    assert 頭.startswith("<!doctype html>"), "缺 doctype"
    assert "<html" in 頭 and "<head>" in 頭, "缺 html／head 開標籤"
    assert 文.index("<head>") < 文.index("</head>"), "</head> 出現在 <head> 之前"
    assert 文.index("</head>") < 文.index("<body>"), "<body> 出現在 </head> 之前"
    assert 文.rstrip().endswith("</html>"), "缺 </html>"


def test_未編碼的_and_不得出現在屬性值裡() -> None:
    """`&display=swap` 這種在 HTML 屬性裡是未定義實體參照。"""
    文 = 板面路徑.read_text(encoding="utf-8")
    壞 = re.findall(r'href="[^"]*&(?!amp;|lt;|gt;|quot;|#)[^"]*"', 文)
    assert not 壞, f"屬性值含未編碼的 &：{壞[:3]}"


def test_開關標籤數量平衡() -> None:
    """`div` 與 `details` 的開關數必須相等——多餘的 `</div>` 會靜默改變巢狀。"""
    文 = 板面路徑.read_text(encoding="utf-8")
    for 標 in ("div", "details", "table", "tbody", "section", "svg"):
        開 = len(re.findall(rf"<{標}[\s>]", 文))
        關 = len(re.findall(rf"</{標}>", 文))
        assert 開 == 關, f"<{標}> 開 {開} 個、關 {關} 個"
