"""工程板注入器的結構負控。

**存在理由**：這支注入器被 sol 退了四輪，每一輪都是同一個病的更深一層——
①跨列覆蓋 → ②跨卡覆蓋且**穩定成假綠** → ③錨在但內容格式壞掉而 0 命中 →
④`count=1` 讓重複錨抓不到、外層 `re.sub` 完全不驗「該遍歷的結構有沒有被遍歷」。

**每一輪我修的都是被回報的那個實例，而不是那個形狀。**
這個檔的存在就是為了讓形狀有牙：**下一個人改注入器時，這些格會替 sol 說話。**

八道閘裡的 `pytest` 會跑到這裡；另有 `board` 一閘直接跑 `--檢查`。
"""

from __future__ import annotations

import importlib.util
import pathlib
import re
import sys

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


@pytest.mark.parametrize(
    ("名", "壞掉"),
    [
        # ① 錨消失
        # 這格刻意**不寫死任務數**：第一版寫「194 任務」，計畫 01C 進來後變 198，
        # 於是 fixture 的替換不再命中、負控靜靜失效。壞的是 fixture 不是生產碼。
        ("頁首標籤改名", lambda s: re.sub(r"(子系統 · \d+) 任務 ·", r"\1 tasks ·", s, count=1)),
        (
            "統計卡標籤改名",
            lambda s: s.replace("<span>固定負控</span>", "<span>固定負控們</span>", 1),
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
    ],
)
def 測試_板面結構壞掉必須拒絕注入(板文: str, 料: dict, 名: str, 壞掉) -> None:
    """八格結構負控。

    **每一格都必須 `SystemExit`，不能只是「注入後沒變」**——
    靜默不動正是這支工具前三輪的病：它會穩定成假綠。
    """
    with pytest.raises(SystemExit) as 誤:
        注入器.注入(壞掉(板文), 料)
    assert "拒絕注入" in str(誤.value), f"{名}：拒絕了但訊息沒說明原因"
