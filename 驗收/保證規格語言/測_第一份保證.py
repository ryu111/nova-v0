"""第一份不是在驗語言、而是在驗**行為**的 claim：wall limit 必須由外面強制。

前面幾份 claim 驗的都是 ClaimSpec 語言自己（封閉綱要、編譯決定性、三色敏感度）。
這一份不同——受測對象真的會去開一個子程序，而三個觀察值**全部由 verifier 在外面量**。

為什麼非得在外面量：合作式的監督者自報的終態字串與外部強制那一支**逐字相同**，
都是 `TIMED_OUT`。只看終態的話兩者無法區分，而「宣稱有把關卻沒有」正是這個 repo
最貴的一種失敗。差別只在兩處看得見：worker 過了寬限期還活著、外部量到的用時超界。
所以固定負控 `cooperative-timeout-subject` 必須恰好紅在 `elapsed_bound` 與
`worker_dead` 這兩條，一條都不能多、不能少——多一條代表判準寫鬆了讓別的東西也紅，
少一條代表那條判準根本沒有在守它宣稱守的東西。

被測者自報的時間不可能混進來：`保證規格編譯.驗觀察` 對 `source == "SUBJECT"` 的
DURATION_MS 直接回 `UNTRUSTED_OBSERVATION`，編都編不出 plan。

【已知限制，不是本 task 的範圍】原語目錄是 `compile_claim` 的第四個參數，由呼叫端
自備；repo 裡沒有一份被准入的正典目錄。所以下面這份目錄是這個測試自己給的，
它擋得住「claim 用了目錄外的原語」，擋不住「有人自備一份含新原語的目錄」。
待辦記在 `交接.md`。
"""

import json
import pathlib
from typing import Any

from nova.基礎設施.裁定執行.原語 import 內部, 原語, 原語目錄
from nova.基礎設施.裁定執行.參考執行封套 import 時限封套
from nova.權威.判準.保證規格執行 import CaseResult, CaseTerminal, PlanResult, run_plan
from nova.權威.判準.保證規格模型 import ClaimSpec, ClaimSpecLoader
from nova.權威.判準.保證規格編譯 import (
    CompileFailure,
    TestPlan,
    compile_claim,
    綁定清單,
    隔離供給,
)

專案根 = pathlib.Path(__file__).resolve().parent.parent.parent
保證檔 = 專案根 / "規格" / "執行" / "保證" / "外部時間上限.claim.json"
綁定檔 = 專案根 / "規格" / "執行" / "綁定" / "參考執行封套.binding.json"


def 讀(路徑: pathlib.Path) -> dict[str, Any]:
    """I/O 在驗收這一側做；權威層不碰檔案系統。"""
    出: dict[str, Any] = json.loads(路徑.read_text(encoding="utf-8"))
    return 出


def 載入保證() -> tuple[ClaimSpec, dict[str, Any]]:
    """走正式入口把 claim 檔載成 typed model，順便把原始 dict 交出去取 parameters。"""
    原始 = 讀(保證檔)
    載入器 = ClaimSpecLoader(
        meta_schema=讀(專案根 / "規格" / "語言" / "ClaimSpec.schema.json"),
        effect_schema=讀(專案根 / "規格" / "介面" / "效果契約.schema.json"),
    )
    規格 = 載入器.load(保證檔.read_bytes())
    assert isinstance(規格, ClaimSpec), 規格
    return 規格, 原始


def 讀綁定() -> 綁定清單:
    """binding 檔是資料；把它攤成 slot → capability digest。"""
    原始 = 讀(綁定檔)
    return 綁定清單(
        manifest_id=原始["manifest_id"],
        revision=原始["revision"],
        綁定={項["binding_slot"]: 項["capability_digest"] for 項 in 原始["bindings"]},
    )


def 編出計畫() -> tuple[TestPlan, dict[str, Any]]:
    """把 claim 檔編成 plan。編不出來就直接斷在這裡，不讓它偽裝成執行時的紅。"""
    規格, 原始 = 載入保證()
    出 = compile_claim(
        規格,
        原語目錄("execution-envelope.v1", (原語("envelope.run", 內部, "STRING"),)),
        讀綁定(),
        隔離供給(frozenset({"COOPERATIVE_PROCESS"})),
    )
    assert isinstance(出, TestPlan), 出
    return 出, 原始["parameters"]


def 跑保證檔() -> PlanResult:
    """唯一入口：讀檔、編譯、用真的會開 process 的封套跑三色。"""
    計畫, 參數 = 編出計畫()
    封套 = 時限封套(
        wall_ms=參數["wall_ms"],
        grace_ms=參數["grace_ms"],
        探測寬限_ms=參數["probe_extra_ms"],
    )
    return run_plan(計畫, 封套)


def 取負控(結果: PlanResult, control_id: str) -> CaseResult:
    """依 control_id 取那一格；取不到就斷，不回 None 讓斷言變成恆真。"""
    for 格 in 結果.negative:
        if 格.case_id == control_id:
            return 格
    raise AssertionError(f"沒有這一格負控：{control_id}")


def test_第一份保證由外部_runner_裁定() -> None:
    結果 = 跑保證檔()
    assert 結果.actual.terminal is CaseTerminal.ACCEPT, 結果.actual
    assert 結果.positive[0].terminal is CaseTerminal.ACCEPT, 結果.positive[0]
    assert 結果.通過, 結果.問題


def test_合作式監督恰好紅在用時與存活兩條() -> None:
    # 這一格是整份 claim 的重心：合作式監督自報的 TIMED_OUT 與真的一樣，
    # 所以 terminal_is_timed_out 必須仍然綠——紅的只能是那兩條在外面量的。
    格 = 取負控(跑保證檔(), "cooperative-timeout-subject")
    assert 格.terminal is CaseTerminal.CLAIM_REJECTED, 格
    assert 格.failed_predicates == frozenset({"elapsed_bound", "worker_dead"}), 格


def test_被測者自報的用時編不出計畫() -> None:
    # 把 elapsed_ms 的來源改成 SUBJECT，就是拿被測者自己的話證明外部期限。
    # 它必須在**編譯期**就被擋掉，而不是跑起來才紅——跑起來才紅代表那份 plan
    # 曾經被承認過一次。
    原始 = 讀(保證檔)
    for 觀 in 原始["observations"]:
        if 觀["observation_id"] == "elapsed_ms":
            觀["source"] = "SUBJECT"
    載入器 = ClaimSpecLoader(
        meta_schema=讀(專案根 / "規格" / "語言" / "ClaimSpec.schema.json"),
        effect_schema=讀(專案根 / "規格" / "介面" / "效果契約.schema.json"),
    )
    規格 = 載入器.load(json.dumps(原始, ensure_ascii=False).encode("utf-8"))
    assert isinstance(規格, ClaimSpec), 規格
    出 = compile_claim(
        規格,
        原語目錄("execution-envelope.v1", (原語("envelope.run", 內部, "STRING"),)),
        讀綁定(),
        隔離供給(frozenset({"COOPERATIVE_PROCESS"})),
    )
    assert isinstance(出, CompileFailure), 出
    assert 出.code == "UNTRUSTED_OBSERVATION", 出
