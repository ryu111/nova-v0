"""`工坊/` 的退役機制（計畫 01C Task 4）。

**這支刻意住在 `架構/` 而不是 `工坊/`**：退役的動作之一就是刪掉 `工坊/`，
checker 住在裡面的話會跟著被刪，退役條件從此無人執法。

**為什麼不驗「每個 `top_level.dir` 都實存」**（sol 2026-08-28 第四十四輪）：
`前端/` 是已宣告但尚未建立的頂層，那條會誤殺它；而「曾經有檔案落地」是
歷史性質、不是當前設定可直接判定的不變式，會迫使測試依賴 Git 歷史。
雙漏洞改由**退役清冊排除格**精準接住。
"""

from __future__ import annotations

import pathlib
import re
import tomllib

import pytest

from 工坊 import 出工單

專案根 = pathlib.Path(__file__).resolve().parent.parent
清冊路徑 = 專案根 / "工坊" / "退役.toml"
規則路徑 = 專案根 / "架構" / "目錄規則.toml"
計畫目錄 = 專案根 / "docs" / "計畫"
退役件數 = 6


# claim `workshop.retirement.is-atomic` 的 judge 比對這三個字面。
# **有 claim 就要有吐得出那個碼的 subject**——寫這段時字面 producer 棘輪
# 擋了我一次，訊息逐字報出三個孤兒常數。predicate 沒有產生者就是恆真格。
碼_已退役仍宣告 = "RETIRED_STILL_DECLARED"
碼_哨兵漂移 = "SENTINEL_PATH_DRIFTED"
碼_清冊不見 = "RETIREMENT_LEDGER_MISSING"
通過 = "OK"


def 檢查退役清冊() -> str:
    """把三格的判定做成帶失敗碼的產生者，供 claim 的 judge 比對。"""
    if (專案根 / "工坊").is_dir() and not 清冊路徑.is_file():
        return 碼_清冊不見
    帳 = 清冊()
    if set(帳.get("retired_dirs", [])) & _宣告的頂層():
        return 碼_已退役仍宣告
    宣告過 = set()
    for 檔 in 計畫目錄.glob("*.md"):
        宣告過 |= set(
            re.findall(r"^- (?:Create|Modify): `([^`]+)`", 檔.read_text(encoding="utf-8"), re.M)
        )
    if any(p not in 宣告過 for p in 帳["sentinels"]):
        return 碼_哨兵漂移
    return 通過


def test_退役清冊檢查在現況回_OK() -> None:
    """防恆真：三格都成立時必須回 `OK`，不能永遠回失敗碼。"""
    assert 檢查退役清冊() == 通過


def 清冊() -> dict[str, list[str]]:
    return tomllib.loads(清冊路徑.read_text(encoding="utf-8"))


def _宣告的頂層() -> set[str]:
    設定 = tomllib.loads(規則路徑.read_text(encoding="utf-8"))
    return {項["dir"] for 項 in 設定["top_level"]} | {
        項["glob"].split("/")[0] for 項 in 設定["placement"]
    }


def test_工坊尚在時退役清冊必須存在() -> None:
    """清冊被刪掉的話，退役條件就只剩沒人讀的散文。"""
    if (專案根 / "工坊").is_dir():
        assert 清冊路徑.is_file(), "retirement_ledger_missing：工坊還在而退役清冊不見了"


def test_已退役的目錄不得仍出現在宣告裡() -> None:
    """**退役清冊排除格**——雙漏洞唯一接得住的那一格。

    反例（sol 提，claude 實驗證）：刪掉 `工坊/`、正確移除 types argv／CI／fence，
    卻**同時漏移除** `top_level` 與 `placement`。此時集合相等格綠（兩邊都還有
    `工坊`）、子集格也綠（argv 已無 `工坊`）——**目錄已刪、宣告還在，八道全綠**。
    """
    殘留 = set(清冊().get("retired_dirs", [])) & _宣告的頂層()
    assert not 殘留, f"已退役卻仍在宣告裡：{sorted(殘留)}——退役沒做完"


def test_哨兵路徑必須出現在某計畫的建立清單() -> None:
    """**防漂移**：計畫改了入口檔名而清冊沒跟，哨兵會指到永遠不出現的路徑。

    那種失效是**靜默**的——退役永遠不會被觸發，而帳面上看起來有機制。
    這格讓漂移先紅，哨兵才不會靜默失明。
    """
    宣告過 = set()
    for 檔 in 計畫目錄.glob("*.md"):
        宣告過 |= set(
            re.findall(r"^- (?:Create|Modify): `([^`]+)`", 檔.read_text(encoding="utf-8"), re.M)
        )
    漂了 = [p for p in 清冊()["sentinels"] if p not in 宣告過]
    assert not 漂了, f"哨兵路徑不在任何計畫的 Create 清單裡：{漂了}"


def test_退役是六處原子動作() -> None:
    """清冊列的動作數必須與 `工坊/守則.py` 一致——兩處都寫就會漂。"""
    assert len(清冊()["retirement_steps"]) == 退役件數


@pytest.mark.parametrize(
    ("漏掉", "應紅在", "住哪"),
    [
        ("gates.yml", "test_CI_跑的是同一組閘", "架構/test_工程規範.py"),
        ("01 fence", "test_計畫入口與規則檔的型別範圍逐字有序相同", "架構/test_目錄規則.py"),
        ("types argv", "test_型別閘的目錄參數不得超出宣告的頂層", "架構/test_目錄規則.py"),
        ("top_level 與 placement", "test_已退役的目錄不得仍出現在宣告裡", "架構/test_工坊退役.py"),
    ],
)
def test_部分退役必紅矩陣_接住的那格必須真的存在(漏掉: str, 應紅在: str, 住哪: str) -> None:
    """四種漏法各自對到的那一格，**必須真的在那個檔裡**。

    第一版寫成 `assert 漏掉 and 應紅在`——兩個都是 parametrize 傳進來的非空
    字串，**恆真**。實測：把四個「應紅在」全部改成不存在的格名，四格照樣綠。
    它宣稱釘住對應關係，實際只斷言字串非空。

    現在改成解析目標檔、確認那個 `def` 真的在——格被改名或刪掉時這裡會紅，
    對應關係才有牙。
    """
    源 = (專案根 / 住哪).read_text(encoding="utf-8")
    assert f"def {應紅在}(" in 源, f"漏掉「{漏掉}」時該接住的 {應紅在} 不在 {住哪} 裡"


def test_凍結旗標存在時生成器必須拒跑(tmp_path: pathlib.Path) -> None:
    """`凍結.md` 存在時生成器與三殼必須 typed 拒跑。

    不然「放一份文件說已凍結」就能永久繞過退役——**文件不是機制**。

    第一版寫成 `if 凍結.is_file(): ...`，而那個檔平常不存在，
    **整格空跑**——條件永遠不成立的格等於沒有格。改成**真的造出凍結態**再驗。
    """
    凍結 = 專案根 / "工坊" / "凍結.md"
    已凍 = 凍結.is_file()
    if not 已凍:
        凍結.write_text("凍結中（測試造的）\n", encoding="utf-8")
    try:
        with pytest.raises(出工單.工單不可用) as e:
            出工單.生成("01C", 1, 基準="deadbeef")
        assert str(e.value).startswith("workshop_frozen")
    finally:
        if not 已凍:
            凍結.unlink()


def test_未凍結時照常生成_防恆真() -> None:
    """否則上一格會在任何情況下都紅，等於把工具永久關掉。"""
    assert not (專案根 / "工坊" / "凍結.md").is_file()
    assert 出工單.生成("01C", 1, 基準="deadbeef")["計畫"] == "01C"


def 該退役了(哨兵在: list[bool], 工坊還在: bool, 已凍結: bool) -> bool:
    """退役觸發條件做成**純函式**，才驗得到。

    第一版寫成 `if 到齊: assert ...`，而兩個哨兵目前都不存在
    （`nova/基礎設施/排程/worker.py` 與 `nova/啟動/後端登錄.py` 是未來的
    產品入口）——**`if` 永遠不成立，整格空跑**。實測：把裡面的斷言改成
    `assert False`，那格照樣綠。

    條件永遠不成立的格等於沒有格。這是同一個病在本檔的第二次發作
    ——凍結格我修了，這格沒修，因為我只修了被回報的那一處。
    """
    return all(哨兵在) and 工坊還在 and not 已凍結


@pytest.mark.parametrize(
    ("哨兵在", "工坊還在", "已凍結", "該退"),
    [
        ([True, True], True, False, True),  # 兩個都到齊而工坊還在沒凍 → 該退役
        ([True, True], True, True, False),  # 已凍結 → 不算違規
        ([True, True], False, False, False),  # 已刪 → 已退役
        ([True, False], True, False, False),  # 只到一個 → 還沒到條件
        ([False, False], True, False, False),  # 都沒到 → 現況
    ],
)
def test_退役觸發條件真值表(哨兵在: list[bool], 工坊還在: bool, 已凍結: bool, 該退: bool) -> None:
    """五種組合逐列釘死——**含「只到一個不觸發」那列的防恆真**。"""
    assert 該退役了(哨兵在, 工坊還在, 已凍結) is 該退


def test_現況不該退役_接到真實檔案() -> None:
    """真值表接回現實：兩個哨兵都還不存在，所以現在不該退役。"""
    在 = [(專案根 / p).exists() for p in 清冊()["sentinels"]]
    assert not 該退役了(在, (專案根 / "工坊").is_dir(), (專案根 / "工坊" / "凍結.md").is_file())
