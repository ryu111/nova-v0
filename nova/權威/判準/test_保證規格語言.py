"""ClaimSpec 編譯器的近身測試：每一類 compile error 都要有自己的 code 與自己的負控。

**這裡不碰檔案系統**：`權威` 是 `allow_io = false` 的層，而編譯器的輸入本來就是
`ClaimSpec` 物件不是 bytes——要讀 schema 檔才組得出受測對象，表示測試搭錯層了。
loader 那一段的驗證在 `驗收/保證規格語言/測_meta_schema.py`。
"""

from dataclasses import replace

import pytest

from nova.基礎設施.裁定執行.原語 import 內部, 原語, 原語目錄, 外部效果
from nova.核心.摘要 import sha256_ref
from nova.核心.識別 import SemanticId
from nova.權威.判準.保證規格模型 import ClaimSpec, ControlSet, RunLimits, SubjectContract
from nova.權威.判準.保證規格編譯 import (
    CompileFailure,
    TestPlan,
    compile_claim,
    綁定清單,
    隔離供給,
)

預期案數 = 3


def 底(
    stimulus: tuple[dict[str, object], ...] | None = None,
    observations: tuple[dict[str, object], ...] | None = None,
    judge_all_of: tuple[dict[str, object], ...] | None = None,
) -> ClaimSpec:
    """一份會編得過的最小 ClaimSpec；每個負控只在它身上動一處。"""
    基 = ClaimSpec(
        claim_id=SemanticId.parse("example.compile-base"),
        revision=1,
        subject=SubjectContract(
            contract=SemanticId.parse("reference-envelope.v1"),
            operation=SemanticId.parse("run"),
            binding_slot=SemanticId.parse("execution-envelope.reference"),
        ),
        stimulus=({"primitive": "envelope.run", "arguments": {}},),
        observations=(
            {
                "observation_id": "code",
                "source": "STIMULUS_RESULT",
                "path": "code",
                "type": "STRING",
            },
        ),
        judge_all_of=(
            {
                "predicate_id": "verdict_is_ok",
                "operator": "EQUALS",
                "left": {"observation": "code"},
                "right": {"const": "OK"},
            },
        ),
        controls=ControlSet(
            positive=(
                {"control_id": "p1", "subject_binding": "REFERENCE", "expected_terminal": "ACCEPT"},
            ),
            negative=(
                {
                    "control_id": "n1",
                    "faulty_subject": "驗收/工具鏈/fixtures/超長函式.py",
                    "expected_terminal": "CLAIM_REJECTED",
                    "must_fail_exactly": ["verdict_is_ok"],
                },
            ),
        ),
        run_limits=RunLimits(wall_ms=60000, max_output_bytes=1048576),
        isolation="COOPERATIVE_PROCESS",
        effect_delivery=None,
        canonical_bytes=b"{}",
        digest=sha256_ref(b"example.compile-base"),
    )
    return replace(
        基,
        stimulus=stimulus if stimulus is not None else 基.stimulus,
        observations=observations if observations is not None else 基.observations,
        judge_all_of=judge_all_of if judge_all_of is not None else 基.judge_all_of,
    )


def 編(
    spec: ClaimSpec,
    catalog: 原語目錄 | None = None,
    binding: 綁定清單 | None = None,
    offer: 隔離供給 | None = None,
) -> TestPlan | CompileFailure:
    """走正式入口編成 plan，需要時覆寫 catalog／binding／offer。"""
    目錄 = catalog or 原語目錄(
        "test-catalog.v1",
        (
            原語("envelope.run", 內部, "STRING"),
            原語("envelope.elapsed", 內部, "DURATION_MS"),
            原語("envelope.output_size", 內部, "BYTES"),
            原語("mailer.send", 外部效果, "STRING"),
        ),
    )
    綁定 = binding or 綁定清單(
        "test-manifest", 1, {"execution-envelope.reference": "sha256:deadbeef"}
    )
    return compile_claim(spec, 目錄, 綁定, offer or 隔離供給(frozenset({"COOPERATIVE_PROCESS"})))


def 碼(結果: TestPlan | CompileFailure) -> str:
    assert isinstance(結果, CompileFailure), 結果
    return 結果.code


def test_相同輸入編譯成相同_plan_digest() -> None:
    甲, 乙 = 編(底()), 編(底())
    assert isinstance(甲, TestPlan)
    assert isinstance(乙, TestPlan)
    assert 甲.digest.hex == 乙.digest.hex


def test_plan_digest_涵蓋四個輸入() -> None:
    # digest 只綁 claim 的話，換 catalog／binding／isolation 都不改 digest——
    # 那等於宣稱「在別的環境上編出來的是同一個 plan」，而那句話沒人證明過。
    基準 = 編(底())
    assert isinstance(基準, TestPlan)
    別的目錄 = 原語目錄("other-catalog.v1", (原語("envelope.run", 內部, "STRING"),))
    別的綁定 = 綁定清單("other", 1, {"execution-envelope.reference": "sha256:cafe"})
    別的供給 = 隔離供給(frozenset({"COOPERATIVE_PROCESS", "CONTAINER"}))
    for 標, 變 in (
        ("catalog", 編(底(), catalog=別的目錄)),
        ("binding", 編(底(), binding=別的綁定)),
        ("offer", 編(底(), offer=別的供給)),
    ):
        assert isinstance(變, TestPlan), 標
        assert 變.digest.hex != 基準.digest.hex, 標


def test_型別不符的比較被擋() -> None:
    # DURATION_MS 與 BYTES 都是整數，不擋的話「跑了 5000 毫秒」會等於「輸出 5000 位元組」。
    壞 = 底(
        observations=(
            {"observation_id": "用時", "source": "VERIFIER", "path": "e", "type": "DURATION_MS"},
            {"observation_id": "大小", "source": "STIMULUS_RESULT", "path": "s", "type": "BYTES"},
        ),
        judge_all_of=(
            {
                "predicate_id": "wrong",
                "operator": "EQUALS",
                "left": {"observation": "用時"},
                "right": {"observation": "大小"},
            },
        ),
    )
    assert 碼(編(壞)) == "TYPE_MISMATCH"


def test_未知原語被擋() -> None:
    壞 = 底(stimulus=({"primitive": "沒這個.原語", "arguments": {}},))
    assert 碼(編(壞)) == "UNKNOWN_PRIMITIVE"


def test_subject_time_不能證外部期限() -> None:
    # 被測者自報「我只跑了 3 秒」不能拿來證明外部時限——那是把裁定權交回給被測者。
    壞 = 底(
        observations=(
            {"observation_id": "用時", "source": "SUBJECT", "path": "e", "type": "DURATION_MS"},
        ),
        judge_all_of=(
            {
                "predicate_id": "within_wall",
                "operator": "LESS_THAN",
                "left": {"observation": "用時"},
                "right": {"const": 60000},
            },
        ),
    )
    assert 碼(編(壞)) == "UNTRUSTED_OBSERVATION"


def test_verifier_報的時間可以證外部期限() -> None:
    # 防恆真：把所有 DURATION_MS 都擋掉也能讓上一格通過。差別只在 source。
    好 = 底(
        observations=(
            {"observation_id": "用時", "source": "VERIFIER", "path": "e", "type": "DURATION_MS"},
        ),
        judge_all_of=(
            {
                "predicate_id": "within_wall",
                "operator": "LESS_THAN",
                "left": {"observation": "用時"},
                "right": {"const": 60000},
            },
        ),
    )
    assert isinstance(編(好), TestPlan)


def test_外部效果原語沒有交付契約被擋() -> None:
    # 刻意用 mailer.send 而不是 effect.send：loader 靠 schema 宣告的 effect. 前綴判斷，
    # 這裡要證明編譯器看的是**目錄宣告的種類**——前綴騙得過 loader，騙不過目錄。
    壞 = 底(stimulus=({"primitive": "mailer.send", "arguments": {}},))
    assert 碼(編(壞)) == "EFFECT_DELIVERY_REQUIRED"


def test_subject_沒綁定是獨立結果() -> None:
    # UNBOUND_SUBJECT 不是「負控成功抓到錯」，是根本沒驗到。
    assert 碼(編(底(), binding=綁定清單("empty", 1, {}))) == "UNBOUND_SUBJECT"


def test_隔離能力不足是獨立結果() -> None:
    assert 碼(編(底(), offer=隔離供給(frozenset()))) == "UNSUPPORTED_ISOLATION"


def test_三類編譯錯誤不被壓成同一字串() -> None:
    碼們 = {
        碼(編(底(stimulus=({"primitive": "沒這個.原語", "arguments": {}},)))),
        碼(編(底(), binding=綁定清單("empty", 1, {}))),
        碼(編(底(), offer=隔離供給(frozenset()))),
    }
    assert len(碼們) == 預期案數, 碼們


def test_合法的_claim_編得出_plan() -> None:
    # 防恆真：一個永遠回 CompileFailure 的編譯器也能讓上面每一格通過。
    出 = 編(底())
    assert isinstance(出, TestPlan)
    assert 出.claim_id.value == "example.compile-base"
    assert 出.案數 == 預期案數


@pytest.mark.parametrize("欄", ["catalog_digest", "binding_digest", "isolation_digest"])
def test_plan_記下三個輸入的_digest(欄: str) -> None:
    出 = 編(底())
    assert isinstance(出, TestPlan)
    assert getattr(出, 欄)
