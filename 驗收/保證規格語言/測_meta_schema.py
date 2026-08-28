"""ClaimSpec 0.2.0 封閉 meta-schema 的黑箱測試：六個事前固定的無效 instance。

這六個不是隨手挑的壞例子，是計畫在 Task 6 就寫死的固定負控——每一個都對應一種
「規格看起來還在，但保證已經被掏空」的寫法：自報 `passed`、把負控清空、把時限
寫成字串、外部效果沒有交付語意、非效果 claim 卻帶效果契約、宣告做不到的
`EXACTLY_ONCE`。
"""

import copy
import importlib.util
import json
import pathlib
import re
from typing import Any

import pytest

from nova.權威.判準.保證規格模型 import ClaimSpec, ClaimSpecLoader, ClaimSpecStructuralError

專案根 = pathlib.Path(__file__).resolve().parent.parent.parent
語言目錄 = 專案根 / "規格" / "語言"
效果契約檔 = 專案根 / "規格" / "介面" / "效果契約.schema.json"


def 取載入器() -> ClaimSpecLoader:
    """meta-schema 是資料，載入器只執行——I/O 在這裡做，權威層不碰檔案系統。"""
    return ClaimSpecLoader(
        meta_schema=json.loads((語言目錄 / "ClaimSpec.schema.json").read_text(encoding="utf-8")),
        effect_schema=json.loads(效果契約檔.read_text(encoding="utf-8")),
    )


def validate_claim(instance: dict[str, Any]) -> ClaimSpec | ClaimSpecStructuralError:
    """把 instance 編碼成 bytes 再走正式入口，不給測試走後門。"""
    return 取載入器().load(json.dumps(instance, ensure_ascii=False).encode("utf-8"))


def deep_merge(底: dict[str, Any], 變更: dict[str, Any]) -> dict[str, Any]:
    """把變更疊到底上；dict 遞迴合併，其餘直接覆蓋。"""
    出 = copy.deepcopy(底)
    for 鍵, 值 in 變更.items():
        if isinstance(值, dict) and isinstance(出.get(鍵), dict):
            出[鍵] = deep_merge(出[鍵], 值)
        else:
            出[鍵] = copy.deepcopy(值)
    return 出


def 有效_effect_contract() -> dict[str, Any]:
    """一份語意合法的效果交付契約——用來證明「合法但不該出現」也要被擋。"""
    return {
        "endpoint_id": "endpoint.example",
        "operation": "send",
        "semantics": "AT_LEAST_ONCE_IDEMPOTENT",
        "intent_schema": "規格/介面/意圖.schema.json",
        "idempotency_key": ["work_id", "attempt"],
        "attempt_policy": {"max_attempts": 3},
        "receipt_schema": "規格/介面/回條.schema.json",
        "success_postcondition": {"observation": "status", "const": "OK"},
        "duplicate_policy": "IGNORE",
        "uncertain_terminal": "UNCERTAIN",
    }


def 最小_判準() -> dict[str, Any]:
    """一條恆等判準：這份最小 claim 的用途是當負控的底，不是示範判準怎麼寫。"""
    return {
        "all_of": [
            {
                "predicate_id": "verdict_is_ok",
                "operator": "EQUALS",
                "left": {"observation": "code"},
                "right": {"const": "OK"},
            }
        ]
    }


def 最小_控制組() -> dict[str, Any]:
    """正控與負控各一項。兩邊都不得為空——空的負控等於沒有負控。"""
    return {
        "positive": [
            {
                "control_id": "repository-tree",
                "subject_binding": "REPOSITORY_SCAN",
                "expected_terminal": "ACCEPT",
            }
        ],
        "negative": [
            {
                "control_id": "broken-subject",
                "faulty_subject": "驗收/工具鏈/fixtures/錯置_repository.py",
                "expected_terminal": "CLAIM_REJECTED",
                "must_fail_exactly": ["verdict_is_ok"],
            }
        ],
    }


@pytest.fixture
def 最小_claim() -> dict[str, Any]:
    """一份會通過的最小 claim。每個負控都只在它身上動一處。"""
    return {
        "$schema": "../../語言/ClaimSpec.schema.json",
        "claimspec_version": "0.2.0",
        "claim_id": "example.minimal-claim",
        "revision": 1,
        "supersedes": None,
        "statement": "最小可通過的 claim，只為了讓負控每次只動一處。",
        "sources": [
            {"source_id": "plan.01.task.6", "kind": "PLAN_TASK", "locator": "docs/計畫/01"}
        ],
        "primitive_catalog": {"catalog_id": "architecture-checker.v1", "digest": None},
        "subject": {
            "contract": "engineering-checker.v1",
            "operation": "check-file",
            "binding_slot": "engineering-checker.repository",
        },
        "parameters": {},
        "setup": [],
        "stimulus": [{"primitive": "architecture.check_file", "arguments": {"path": "x"}}],
        "observations": [
            {
                "observation_id": "code",
                "source": "STIMULUS_RESULT",
                "path": "code",
                "type": "STRING",
            }
        ],
        "judge": 最小_判準(),
        "controls": 最小_控制組(),
        "run_limits": {"wall_ms": 60000, "max_output_bytes": 1048576},
        "isolation": "COOPERATIVE_PROCESS",
        "effect_delivery": None,
        "evidence": {"retain": ["code"], "record_kind": "CHECK_VERDICT"},
        "feedback": {"to_candidate": "NONE"},
        "cleanup": [],
    }


def 測試_最小_claim_本身要能過(最小_claim: dict[str, Any]) -> None:
    # 沒有這一格，六個負控可以靠「什麼都拒絕」全綠。
    結果 = validate_claim(最小_claim)
    assert isinstance(結果, ClaimSpec), 結果


@pytest.mark.parametrize(
    ("變更", "錯碼"),
    [
        ({"passed": True}, "UNKNOWN_FIELD"),
        ({"controls": {"positive": [], "negative": []}}, "MIN_ITEMS"),
        ({"run_limits": {"wall_ms": "500"}}, "TYPE_MISMATCH"),
        (
            {"stimulus": [{"primitive": "effect.send", "arguments": {}}], "effect_delivery": None},
            "EFFECT_DELIVERY_REQUIRED",
        ),
        ({"effect_delivery": 有效_effect_contract()}, "EFFECT_DELIVERY_FORBIDDEN"),
        (
            {"effect_delivery": deep_merge(有效_effect_contract(), {"semantics": "EXACTLY_ONCE"})},
            "UNSUPPORTED_DELIVERY_SEMANTICS",
        ),
    ],
)
def 測試_結構錯誤拒絕(最小_claim: dict[str, Any], 變更: dict[str, Any], 錯碼: str) -> None:
    結果 = validate_claim(deep_merge(最小_claim, 變更))
    assert isinstance(結果, ClaimSpecStructuralError), 結果
    assert 結果.code == 錯碼


def 測試_執行欄位改變摘要改變(最小_claim: dict[str, Any]) -> None:
    原 = validate_claim(最小_claim)
    assert isinstance(原, ClaimSpec)
    改 = validate_claim(deep_merge(最小_claim, {"run_limits": {"wall_ms": 60001}}))
    assert isinstance(改, ClaimSpec)
    assert 改.digest != 原.digest


def 測試_鍵順序不改摘要(最小_claim: dict[str, Any]) -> None:
    # digest 是 canonical bytes 的摘要，不是檔案位元組的摘要——換個鍵順序不算改規格。
    反 = dict(reversed(list(最小_claim.items())))
    原 = validate_claim(最小_claim)
    倒 = validate_claim(反)
    assert isinstance(原, ClaimSpec)
    assert isinstance(倒, ClaimSpec)
    assert 倒.digest == 原.digest


def 測試_已存在的三份工程_claim_都能載入() -> None:
    # 正控：schema 若寫得跟現實對不上，這一格會紅。
    載入器 = 取載入器()
    檔們 = sorted((專案根 / "規格").rglob("*.claim.json"))
    assert 檔們
    for 檔 in 檔們:
        結果 = 載入器.load(檔.read_bytes())
        assert isinstance(結果, ClaimSpec), f"{檔.name}: {結果}"


def 去掉(底: dict[str, Any], 路徑: tuple[str, ...]) -> dict[str, Any]:
    """回一份少了指定欄位的複本——deep_merge 只能疊加，刪不掉東西。"""
    出 = copy.deepcopy(底)
    節: Any = 出
    for 段 in 路徑[:-1]:
        節 = 節[段]
    del 節[路徑[-1]]
    return 出


@pytest.mark.parametrize(
    "路徑",
    [
        ("claim_id",),
        ("controls", "positive"),
        ("run_limits", "max_output_bytes"),
        ("judge", "all_of"),
    ],
)
def 測試_缺必填欄位會紅(最小_claim: dict[str, Any], 路徑: tuple[str, ...]) -> None:
    # required 不檢查的話，「少寫一段」與「寫對了」在這道閘看起來一樣。
    結果 = validate_claim(去掉(最小_claim, 路徑))
    assert isinstance(結果, ClaimSpecStructuralError), 結果
    assert 結果.code == "MISSING_FIELD"
    assert 結果.pointer.endswith(路徑[-1])


def 測試_布林不算整數(最小_claim: dict[str, Any]) -> None:
    # Python 的 bool 是 int 的子類別：不特判的話 wall_ms: true 會被當成合法的 1。
    結果 = validate_claim(deep_merge(最小_claim, {"run_limits": {"wall_ms": True}}))
    assert isinstance(結果, ClaimSpecStructuralError), 結果
    assert 結果.code == "TYPE_MISMATCH"


def 測試_陣列裡的項目也要逐一檢查(最小_claim: dict[str, Any]) -> None:
    壞 = deep_merge(最小_claim, {"sources": [{"source_id": "x", "kind": "PLAN_TASK"}]})
    結果 = validate_claim(壞)
    assert isinstance(結果, ClaimSpecStructuralError), 結果
    assert 結果.code == "MISSING_FIELD"
    assert 結果.pointer == "/sources/0/locator"


def 測試_負控為空是_MIN_ITEMS(最小_claim: dict[str, Any]) -> None:
    # 只清空負控。固定負控 2 同時清空正負兩邊，正控會先紅而蓋住這一格。
    結果 = validate_claim(deep_merge(最小_claim, {"controls": {"negative": []}}))
    assert isinstance(結果, ClaimSpecStructuralError), 結果
    assert 結果.code == "MIN_ITEMS"
    assert 結果.pointer == "/controls/negative"


def 測試_做不到的語意先於該不該有效果契約(最小_claim: dict[str, Any]) -> None:
    # 一份效果 claim 帶 EXACTLY_ONCE：兩條規則都可以說話，順序決定 code。
    # 不釘住的話，將來 must_fail_exactly 會無聲對錯。
    效果 = deep_merge(
        最小_claim,
        {
            "stimulus": [{"primitive": "effect.send", "arguments": {}}],
            "effect_delivery": deep_merge(有效_effect_contract(), {"semantics": "EXACTLY_ONCE"}),
        },
    )
    結果 = validate_claim(效果)
    assert isinstance(結果, ClaimSpecStructuralError), 結果
    assert 結果.code == "UNSUPPORTED_DELIVERY_SEMANTICS"


def 測試_合法的效果_claim_會過(最小_claim: dict[str, Any]) -> None:
    # 防恆真：效果那三條規則不能靠「凡是帶 effect_delivery 就拒絕」而全綠。
    合法 = deep_merge(
        最小_claim,
        {
            "stimulus": [{"primitive": "effect.send", "arguments": {}}],
            "effect_delivery": 有效_effect_contract(),
        },
    )
    結果 = validate_claim(合法)
    assert isinstance(結果, ClaimSpec), 結果
    assert 結果.effect_delivery is not None
    assert 結果.effect_delivery.semantics == "AT_LEAST_ONCE_IDEMPOTENT"


def 測試_claim_id_不合語義識別規則會紅(最小_claim: dict[str, Any]) -> None:
    結果 = validate_claim(deep_merge(最小_claim, {"claim_id": "工作.完成"}))
    assert isinstance(結果, ClaimSpecStructuralError), 結果
    assert 結果.code == "INVALID_SEMANTIC_ID"


# ── judge 常數必須有產生者（2026-08-28 新增） ──────────────────────────────
#
# 發作：`工具鏈首日探針.claim.json` 的四個 judge predicate 裡**三個是恆真格**。
# `TOOLCHAIN_VERSION_DRIFT` 與 `DISCOVERY_TRACK_MISSING` **全 repo 只出現在
# 那份 claim 自己裡，零產生者**；`mutation_tests_are_copied` 比對
# `MUTATION_TESTS_NOT_COPIED`，而探針實吐 `MUTATION_TESTS_NOT_COPIED:also_copy`
# ——差一個後綴，NOT_EQUALS 永遠成立。兩個負控宣告的那格都不可能紅。
#
# 這不是一份 claim 的問題：**十四份裡八份有孤兒常數**。它們今天不紅，因為
# （這行原本寫「七份」——那是原型跑出來的數字，名單長到八份後我沒更新，
# sol 2026-08-28 抓到。**數字寫進散文就會過期，權威是下面那份凍名單**。）
# `工具/跑驗收.py` 回 `UNSUPPORTED_CLAIM_EXECUTION`（01 Task 12 未接線）
# ——**`must_fail_exactly` 從來沒有被執行過**。等接線那天會一次全爆。
#
# 棘輪用**凍住的名單**不是數字（sol 2026-08-28 採納的量詞紀律：
# 量詞只能證明基數，不能證明成員身分）。名單只准縮：修好一份就從名單刪一份，
# **沒刪會紅**，所以不會有人修完債卻留著洞。

判準常數債 = {
    "claimspec.compiler.deterministic-typed-plan",
    "claimspec.controls.direct-red-preserved",
    "claimspec.framework.no-verdict-rewrite",
    "claimspec.mutation.named-control-only",
    "core.identity-and-digest.canonical",
    "engineering.gates.automatically-enforced",
    "engineering.named-mutation.repeatable",
    # toolchain.python-3-14.day-one-probe 已於 2026-08-28 修好（claim revision 2
    # 分面 observation 加上移除 catch-all），照棘輪方向從名單刪除。
}
產生者根 = ("nova", "工具", "架構", "驗收")
最短碼長 = 3  # `OK` 這種兩字的不是失敗碼，不進檢查


def _判準常數(規格: dict[str, Any]) -> set[str]:
    """judge 裡被當成字面值比對的失敗碼。只收全大寫、長度 > 3 的。"""
    出: set[str] = set()
    for 條 in 規格.get("judge", {}).get("all_of", []):
        for 邊 in (條.get("left", {}), 條.get("right", {})):
            值 = 邊.get("const")
            if isinstance(值, str) and 值.isupper() and len(值) > 最短碼長:
                出.add(值)
    return 出


def _有產生者(碼: str, 根: pathlib.Path) -> bool:
    """碼必須以**字面值**出現在某支 .py 裡（前面緊接引號），才算有產生者。

    **為什麼要求引號**：第一版只查「字串有沒有出現過」，結果我在這個檔上面
    寫的那段解釋缺陷的註解——裡面逐字列了 `TOOLCHAIN_VERSION_DRIFT` 與
    `DISCOVERY_TRACK_MISSING`——**自己變成了產生者**，於是偵測器判定
    工具鏈那份 claim 是乾淨的。**說明缺陷的文字把偵測器餵飽了。**

    要求前面緊接 `"` 或 `'` 就把註解與 markdown 反引號排除掉，
    而探針真正的 `return "CODE:..."`／`return f"CODE:..."` 兩種都收得到。

    **仍是寬鬆方向**：字面值存在不等於真的可達。可達性要等 01 Task 12
    接線後由執行器本身驗——那時 `must_fail_exactly` 才第一次被實際執行。
    """
    樣式 = re.compile(r"[\"']" + re.escape(碼))
    return any(
        樣式.search(檔.read_text(encoding="utf-8"))
        for 目錄 in 產生者根
        for 檔 in (根 / 目錄).rglob("*.py")
    )


def _髒的保證() -> set[str]:
    """回傳「有孤兒常數」的 claim_id 集合。"""
    根 = pathlib.Path(__file__).resolve().parents[2]
    髒 = set()
    for 檔 in sorted((根 / "規格").rglob("*.claim.json")):
        規格 = json.loads(檔.read_text(encoding="utf-8"))
        if any(not _有產生者(碼, 根) for 碼 in _判準常數(規格)):
            髒.add(str(規格["claim_id"]))
    return 髒


def 測試_沒有新的孤兒常數() -> None:
    """不在債名單裡的 claim，judge 常數必須都有產生者。"""
    新髒 = _髒的保證() - 判準常數債
    assert not 新髒, f"這些 claim 的 judge 常數零產生者，predicate 是恆真格：{sorted(新髒)}"


def 測試_債名單只准縮() -> None:
    """債修好了要從名單刪掉——留著會讓棘輪失去方向。"""
    已修 = 判準常數債 - _髒的保證()
    assert not 已修, f"這些 claim 已經不髒了，請從 判準常數債 刪掉：{sorted(已修)}"


def 測試_乾淨的保證不被誤殺_防恆真() -> None:
    """乾淨的 claim 必須不在髒集合裡——否則上面兩格都會恆真。

    **不寫份數**：份數是 14 減掉凍名單長度，會隨棘輪縮動而變。
    """
    根 = pathlib.Path(__file__).resolve().parents[2]
    髒 = _髒的保證()
    assert "engineering.placement.exactly-one-owner" not in 髒
    assert len(髒) < len(list((根 / "規格").rglob("*.claim.json")))


# ── must_fail_exactly 必須恰為會紅組（2026-08-28，claim revision 2 的驗收） ──
#
# 這格是整個 R14-01 缺陷的機械化。revision 1 的兩個負控都宣告
# `mutation_tests_are_copied`，而那格對兩個 faulty subject 都**不會紅**
# ——沒有人算過「宣告組」與「實際會紅組」是不是同一組，因為
# `工具/跑驗收.py` 回 `UNSUPPORTED_CLAIM_EXECUTION`（01 Task 12 未接線）。
#
# 這格不等執行鏈：直接拿探針的分面函式算出 faulty subject 的觀察，
# 套 claim 自己的 judge，比對 `must_fail_exactly`。**算出來，不是推出來。**

探針路徑 = pathlib.Path(__file__).resolve().parents[2] / "工具" / "驗工具鏈.py"
分面版本 = 2  # claim revision 2 起改用分面 observation
# 每個 faulty subject 實際會讓探針吐出的碼（出處為探針原始碼的 return 點）。
壞態產出 = {
    "nova/核心/工具鏈守衛.py::收窄[identity]": ["NAMED_MUTATION_SURVIVED:收窄"],
    "pyproject.toml::[tool.mutmut].also_copy[removed]": ["MUTATION_TESTS_NOT_COPIED:also_copy"],
}


def _載入探針() -> object:
    規 = importlib.util.spec_from_file_location("驗工具鏈", 探針路徑)
    assert 規 and 規.loader
    模 = importlib.util.module_from_spec(規)
    規.loader.exec_module(模)
    return 模


def _會紅的(judge: dict[str, Any], 觀察: dict[str, Any]) -> set[str]:
    """套 judge 的每個 predicate，回傳失敗的 predicate_id 集合。"""
    紅 = set()
    for 條 in judge["all_of"]:
        左 = 觀察.get(str(條["left"]["observation"]))
        右 = 條["right"]["const"]
        通 = (左 == 右) if 條["operator"] == "EQUALS" else (左 != 右)
        if not 通:
            紅.add(str(條["predicate_id"]))
    return 紅


def 測試_工具鏈保證的負控宣告恰為會紅組() -> None:
    """兩個負控的 `must_fail_exactly` 必須**精確等於**算出來的會紅組。

    執行器不容忍多一格也不容忍少一格（`保證規格執行.py` 比的是集合相等），
    所以 catch-all predicate 一存在，singleton 宣告就永遠不成立——
    這是 sol 指出而我原本沒看到的一層。
    """
    模 = _載入探針()
    根 = pathlib.Path(__file__).resolve().parents[2]
    規格 = json.loads((根 / "規格/工程/保證/工具鏈首日探針.claim.json").read_text(encoding="utf-8"))
    assert 規格["revision"] == 分面版本, "這格對的是分面 judge 的那一版"
    for 格 in 規格["controls"]["negative"]:
        碼們 = 壞態產出[格["faulty_subject"]]
        紅 = _會紅的(規格["judge"], 模.分面(list(碼們)))
        assert 紅 == set(格["must_fail_exactly"]), (
            f"{格['control_id']}：宣告 {sorted(格['must_fail_exactly'])}，實際會紅 {sorted(紅)}"
        )


def 測試_未知碼不得靜默通過() -> None:
    """分類表收不到的碼必須讓 `harness` 變 `HARNESS_ERROR`。

    sol 逐字：未知 producer code 必須成為 `HARNESS_ERROR`／typed independent
    result，**不能因為移除 catch-all 而靜默通過**。
    """
    模 = _載入探針()
    assert 模.分面(["SOMETHING_NOBODY_MAPPED:x"])["harness"] == "HARNESS_ERROR"
    assert 模.分面([])["harness"] == "OK"
