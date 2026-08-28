"""`架構/目錄規則.toml` 自身的一致性：宣告與宣告之間不得互相矛盾。

**與 `test_工程規範.py` 的分工**：那一份的受測物是**檢查器行為**
（給原始碼 → 判 code）；這一份的受測物是**規則檔自身**
（給宣告 → 判宣告之間相等／完備）。受測物不同型，一檔一個改變理由。
拆出來的直接原因是 `test_工程規範.py` 已達 `MODULE_TOO_LARGE` 上限
（實測 411/400），而規則明寫「超過不是加 ignore，是拆責任」。

**存在理由（sol 2026-08-28 第四十一輪實查）**：`top_level` 在
`架構/檢查工程規範.py` 裡**一次都沒有被載入**，掃描根是從 `[[placement]]`
的 glob 推出來的。所以「加一個 `[[top_level]]` 就等於納入管轄」是錯的
——那是**宣告有、掃描無**。

第一版修法（claude 提）正是這個形狀：我為了防「宣告有掃描無」而提的辦法，
本身就是宣告有掃描無。這個檔就是那次的產物。

**不驗「每個 `top_level.dir` 都實存」**（sol 第四十四輪裁定）：`前端/` 是
已宣告但尚未建立的頂層，加了那條會誤殺它；而且「曾經有檔案落地」是歷史性質、
不是當前設定可直接判定的不變式，會迫使測試依賴 Git 歷史。
退役漏改由 `架構/test_工坊退役.py` 的**退役清冊排除格**精準接住。
"""

from __future__ import annotations

import pathlib
import re
import tomllib

專案根 = pathlib.Path(__file__).resolve().parent.parent
規則檔 = 專案根 / "架構" / "目錄規則.toml"
計畫01 = 專案根 / "docs" / "計畫" / "01-可執行保證語言.md"


def 規則() -> dict[str, list[dict[str, str]]]:
    return tomllib.loads(規則檔.read_text(encoding="utf-8"))


def _型別閘參數() -> list[str]:
    """從 `[[gate]]` 裡取出 types 那道的 argv。"""
    for 閘 in 規則()["gate"]:
        if "mypy" in 閘["argv"]:
            return list(閘["argv"])
    raise AssertionError("目錄規則.toml 裡找不到跑 mypy 的閘")


def 檢查一致性() -> str:
    """把三格的判定做成**帶失敗碼的產生者**，供 claim 的 judge 比對。

    **為什麼要有這支**：`規格/工程/保證/工坊落點受管.claim.json` 的三個
    predicate 各比對一個常數，而**沒有任何 subject 會吐出那些碼的話，
    那三個 predicate 就是恆真格**——十四份 claim 裡八份犯過這個病
    （`驗收/保證規格語言/測_meta_schema.py` 的字面 producer 棘輪擋著）。
    寫這支的當下棘輪就擋了我一次，訊息逐字報出三個孤兒常數。
    """
    設定 = 規則()
    宣告 = {項["dir"] for 項 in 設定["top_level"]}
    掃描根 = {項["glob"].split("/")[0] for 項 in 設定["placement"]}
    if 宣告 != 掃描根:
        return "TOPLEVEL_NOT_SCANNED"
    參數 = {a for a in _型別閘參數() if a not in {"uv", "run", "mypy"} and not a.startswith("-")}
    if not 參數 <= 宣告:
        return "TYPES_ARGV_UNDECLARED"
    期望 = " ".join(_型別閘參數())
    if not any(期望 in 行 for 行 in 計畫01.read_text(encoding="utf-8").splitlines()):
        return "FENCE_SCOPE_DRIFT"
    return "OK"


def test_一致性檢查在現況回_OK() -> None:
    """防恆真：三格都成立時 `檢查一致性()` 必須回 `OK`，不能永遠回失敗碼。"""
    assert 檢查一致性() == "OK"


def test_宣告的頂層與實際掃描根一一相等() -> None:
    """`[[top_level]]` 宣告的目錄，必須恰好等於 `[[placement]]` 推出的掃描根。

    掃描根是 `頂層們 = sorted({glob.split("/")[0] for glob, _ in 用規則.落點})`
    ——**`top_level` 完全沒參與**。兩邊各自維護就會漂：加了 `[[top_level]]`
    而忘記加 `[[placement]]`，那個目錄會帶著 duty 宣告躺在閘外，
    帳面上看起來受管。這格是那個維持者。
    """
    設定 = 規則()
    宣告 = {項["dir"] for 項 in 設定["top_level"]}
    掃描根 = {項["glob"].split("/")[0] for 項 in 設定["placement"]}
    assert 宣告 == 掃描根, (
        f"宣告有而掃不到 {sorted(宣告 - 掃描根)}；掃得到而沒宣告 {sorted(掃描根 - 宣告)}"
    )


def test_型別閘的目錄參數不得超出宣告的頂層() -> None:
    """mypy 的目標目錄必須都是宣告過的頂層——否則它在檢查沒人管轄的東西。"""
    宣告 = {項["dir"] for 項 in 規則()["top_level"]}
    目錄參數 = {
        a for a in _型別閘參數() if a not in {"uv", "run", "mypy"} and not a.startswith("-")
    }
    assert 目錄參數 <= 宣告, f"types 閘掃了未宣告的頂層 {sorted(目錄參數 - 宣告)}"


def test_計畫入口與規則檔的型別範圍逐字有序相同() -> None:
    """同一串範圍字面活在多處，改一處不改其他處，宣稱就變假或閘就掛。

    **`main=e1984ec` 修改前的遷移盤點**：該字面共九處，其中活動來源三處
    （01 fence、TOML argv、`gates.yml`），說明副本兩處（TOML 註解、工程板策展文字），
    凍結快照四處（`docs/決策/迴圈語料/`，不改也不同步）。
    這格管的是 01 fence ↔ TOML argv；TOML argv ↔ `gates.yml` 由
    `test_工程規範.py` 既有的 `test_CI_跑的是同一組閘` 管。**兩格合起來成閉環。**

    九處是**遷移盤點的基線**，不是「日後永遠九處」——說明副本消除之後，
    活動來源只剩三處。
    """
    期望 = " ".join(_型別閘參數())
    命中 = [
        行
        for 行 in 計畫01.read_text(encoding="utf-8").splitlines()
        if re.search(r"\bmypy\b", 行) and "Plan Exit Gate" not in 行
    ]
    assert 命中, "計畫 01 的 fence 裡找不到 mypy 那一段"
    assert any(期望 in 行 for 行 in 命中), (
        f"01 fence 沒有逐字有序的 `{期望}`；實際命中行：{[行[:80] for 行 in 命中]}"
    )
