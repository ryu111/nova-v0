"""三個角色薄殼的固定負控（計畫 01C Task 3）。

**冒煙格為什麼不能用 `--help`**：殼自己的 `--help` **完全不碰後端 PATH**，
那條路徑綠了也不代表殼能啟動後端——sol 第四十一輪逐字指出它「仍是原來那個假綠」。
工坊六角色殼的原始教訓正是「PATH 斷而測試全綠」。
所以正面格要**真的經 PATH 找到假後端**，核對它收到的 exact argv、stdin 工單與
prompt digest，並要求殼原樣帶回 sentinel。

**薄度格為什麼要自帶 import 檢查**：既有的 nova import checker **略過非 `nova.*`
模組**，靠它抓不到 `import tenacity`。而 200 行絆線也抓不到
`for ...: subprocess.run(...)` 這種純 stdlib retry——所以還要禁**迴圈體內的
後端呼叫**（含經本檔 helper 的傳遞閉包）。
"""

from __future__ import annotations

import os
import stat
from pathlib import Path

import pytest

from 工坊 import 出工單
from 工坊.角色 import 執行者, 第二審查者, 薄度, 裁定者

SENTINEL = "WORKSHOP_FAKE_BACKEND_SENTINEL"
命令找不到 = 127  # POSIX：executable 缺席


def _假後端(目錄: Path, 名: str = "claude") -> Path:
    """造一個會把收到的東西寫下來、並吐出 sentinel 的假後端。"""
    路徑 = 目錄 / 名
    路徑.write_text(
        "#!/bin/sh\n"
        f'printf "%s" "$*" > "$(dirname "$0")/argv.txt"\n'
        f'cat > "$(dirname "$0")/stdin.txt"\n'
        f"echo {SENTINEL}\n",
        encoding="utf-8",
    )
    路徑.chmod(路徑.stat().st_mode | stat.S_IEXEC)
    return 路徑


def _工單() -> dict[str, object]:
    return 出工單.生成("01C", 3, 基準="deadbeef")


def test_正面_經路徑啟動假後端並原樣帶回哨符(tmp_path: Path) -> None:
    """**這格才是冒煙**：殼真的 resolve、真的執行、真的把輸出帶回來。"""
    _假後端(tmp_path)
    環境 = dict(os.environ, PATH=f"{tmp_path}:{os.environ['PATH']}")
    出 = 執行者.派工(_工單(), model="claude-opus-5", 環境=環境)
    assert 出["exit"] == 0
    assert SENTINEL in str(出["輸出"]), "殼沒有原樣帶回後端輸出"
    收到參數 = (tmp_path / "argv.txt").read_text(encoding="utf-8")
    assert "--model claude-opus-5" in 收到參數, f"後端收到的 argv 不對：{收到參數}"
    收到輸入 = (tmp_path / "stdin.txt").read_text(encoding="utf-8")
    assert "01C" in 收到輸入 and str(出["prompt_digest"]) in 收到輸入


def test_負面_後端不在路徑上時恰回一二七(tmp_path: Path) -> None:
    """**恰為 127**，不是「非零」——壞態本身就非零時 `!= 0` 是恆真 oracle。"""
    環境 = dict(os.environ, PATH=str(tmp_path))
    出 = 執行者.派工(_工單(), model="claude-opus-5", 環境=環境)
    assert 出["exit"] == 命令找不到, f"缺席應恰回 {命令找不到}，實際 {出['exit']}"


def test_殼記下後端的絕對路徑與摘要(tmp_path: Path) -> None:
    """resolve 後以絕對路徑執行並記 digest——語法被接受不等於跑到對的東西。"""
    _假後端(tmp_path)
    環境 = dict(os.environ, PATH=f"{tmp_path}:{os.environ['PATH']}")
    出 = 執行者.派工(_工單(), model="claude-opus-5", 環境=環境)
    assert str(出["executable"]).startswith("/"), "沒有 resolve 成絕對路徑"
    assert 出["executable_digest"]


def test_不合法的授權必須具型別拒絕(tmp_path: Path) -> None:
    """探針值取 `edit`——**實案原字**：它不是 agy 的合法 action，
    而整場派工無寫檔權卻無人知，燒掉一整輪。"""
    _假後端(tmp_path)
    環境 = dict(os.environ, PATH=f"{tmp_path}:{os.environ['PATH']}")
    with pytest.raises(執行者.不得派工) as e:
        執行者.派工(dict(_工單(), grant=["edit"]), model="claude-opus-5", 環境=環境)
    assert str(e.value).startswith("grant_not_in_binary_capability_set")


def test_授權宣告了但沒生效也要拒(tmp_path: Path) -> None:
    """**語法被接受不等於路徑匹配生效**——canary 沒出現就不准派。"""
    _假後端(tmp_path)
    環境 = dict(os.environ, PATH=f"{tmp_path}:{os.environ['PATH']}")
    with pytest.raises(執行者.不得派工) as e:
        執行者.派工(
            dict(_工單(), grant=["write_file"]), model="claude-opus-5", 環境=環境, canary="從未出現"
        )
    assert str(e.value).startswith("grant_not_effective")


def test_合法授權照常派工_防恆真(tmp_path: Path) -> None:
    _假後端(tmp_path)
    環境 = dict(os.environ, PATH=f"{tmp_path}:{os.environ['PATH']}")
    出 = 執行者.派工(dict(_工單(), grant=["write_file"]), model="claude-opus-5", 環境=環境)
    assert 出["exit"] == 0


@pytest.mark.parametrize("殼", ["執行者", "裁定者", "第二審查者"])
def test_薄度_殼裡不得長出派工邏輯(殼: str) -> None:
    """禁 import 凍結名單、禁 sleep、禁遞迴、**禁迴圈體內呼叫後端**、200 行絆線。

    最後一項含**經本檔 helper 的傳遞閉包**：迴圈裡呼叫 `_重試()`、
    而 `_重試()` 內部才 `subprocess.run`，一樣要抓到——那正是 retry 的形狀。
    """

    問題 = 薄度.檢查(Path(__file__).resolve().parent / "角色" / f"{殼}.py")
    assert 問題 == [], f"{殼} 長出了 dispatch 邏輯：{問題}"


def test_薄度格抓得到傳遞閉包的重試(tmp_path: Path) -> None:
    """防恆真的另一半：**造一個真的壞殼，薄度格必須抓到**。"""

    壞 = tmp_path / "壞殼.py"
    # **兩層**：迴圈 → `_重試` → `_送` → subprocess。第一版只有一層
    # （迴圈 → `_重試` → subprocess），而那已經被「直接呼叫」那組涵蓋
    # ——**閉包計算根本沒被用到，那格是恆真的**。關掉閉包重跑照樣綠，
    # 是這樣才發現的。
    壞.write_text(
        "import subprocess\n\n\n"
        "def _送(cmd):\n    return subprocess.run(cmd, check=False)\n\n\n"
        "def _重試(cmd):\n    return _送(cmd)\n\n\n"
        "def 派工(cmd):\n    for _ in range(3):\n        _重試(cmd)\n",
        encoding="utf-8",
    )
    問題 = 薄度.檢查(壞)
    assert any("迴圈" in x for x in 問題), f"沒抓到迴圈內的傳遞呼叫：{問題}"


def test_純資料迴圈不被誤殺_防恆真(tmp_path: Path) -> None:
    """殼逐條驗 grant 本來就要迴圈——**禁的是迴圈內呼叫後端，不是禁迴圈**。"""

    好 = tmp_path / "好殼.py"
    好.write_text(
        "def 驗(grants):\n"
        "    出 = []\n"
        "    for g in grants:\n"
        "        出.append(g.strip())\n"
        "    return 出\n",
        encoding="utf-8",
    )
    assert 薄度.檢查(好) == []


def test_提示檔取摘要且三個角色各一份() -> None:
    """prompt 是**資料檔**不是字串常數——改了要能被看見。"""

    for 名 in ("執行者", "裁定者", "第二審查者"):
        檔 = Path(__file__).resolve().parent / "角色" / "提示" / f"{名}.md"
        assert 檔.is_file(), f"缺提示檔 {名}"
        assert 薄度.提示摘要(檔)


def test_角色不得取得接受權(tmp_path: Path) -> None:
    """三個殼的輸出一律 observation／advice——**看實際回傳值，不是看識別字**。

    第一版只掃 `ast.Name` 裡有沒有英文 `accept`。fable 覆蓋審 M3 實測：
    讓殼回傳 `kind="ACCEPTANCE"`（字串常數不是 `Name`）**42 格全綠**
    ——那格掃的是命名習慣，不是行為。
    """
    _假後端(tmp_path)
    環境 = dict(os.environ, PATH=f"{tmp_path}:{os.environ['PATH']}")
    for 殼 in (執行者, 裁定者, 第二審查者):
        出 = 殼.派工(_工單(), model="claude-opus-5", 環境=環境)
        assert 出["kind"] == "OBSERVATION", f"{殼.角色名} 回了 {出['kind']}，不是 observation"


def test_薄度抓得到凍結名單的匯入(tmp_path: Path) -> None:
    """`import tenacity` 那類——**既有的 nova checker 略過非 `nova.*`，靠它抓不到**。

    fable 覆蓋審 M1 實測：把整段 import 檢查關掉，42 格全綠——**零 fixture**。
    """
    壞 = tmp_path / "壞殼.py"
    壞.write_text("import tenacity\n\n\ndef 派工():\n    return 1\n", encoding="utf-8")
    assert any("凍結名單" in x for x in 薄度.檢查(壞))


def test_薄度抓得到睡眠與遞迴(tmp_path: Path) -> None:
    """含 `from time import sleep` 之後的**裸呼叫**——那是 `ast.Name` 不是 `Attribute`。

    fable 覆蓋審 M2 實測：把 sleep／遞迴檢查整支關掉，42 格全綠。
    """
    睡 = tmp_path / "睡殼.py"
    睡.write_text("from time import sleep\n\n\ndef 派工():\n    sleep(1)\n", encoding="utf-8")
    assert any("sleep" in x for x in 薄度.檢查(睡))

    遞 = tmp_path / "遞殼.py"
    遞.write_text("def 派工(n):\n    return 派工(n - 1)\n", encoding="utf-8")
    assert any("遞迴" in x for x in 薄度.檢查(遞))
