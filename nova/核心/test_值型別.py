"""核心值型別的近身測試：識別、摘要、時間、錯誤四支各自帶事前固定的負控。"""

import pytest
from hypothesis import given
from hypothesis import strategies as st

from nova.核心.摘要 import Sha256Ref, canonical_json_bytes, sha256_ref
from nova.核心.時間 import Duration, Instant
from nova.核心.識別 import BindingSlot, ClaimRef, SemanticId
from nova.核心.錯誤 import (
    CaseFailureKind,
    InvalidSemanticId,
    TextNotCanonical,
    ValueNotCanonical,
)

十六進位長度 = 64
一點五秒 = 1500
分解的中文 = "e\u0301"  # NFD 的 é：與 NFC 的 é（U+00E9）同形不同碼


def test_鍵順序不改摘要() -> None:
    assert canonical_json_bytes({"b": 2, "a": 1}) == canonical_json_bytes({"a": 1, "b": 2})


@given(st.lists(st.tuples(st.text(alphabet="abcdefg", min_size=1), st.integers()), max_size=8))
def test_任何鍵順序都同摘要(對們: list[tuple[str, int]]) -> None:
    正 = dict(對們)
    反 = dict(reversed(list(正.items())))
    assert canonical_json_bytes(正) == canonical_json_bytes(反)


def test_中文不得成為持久語義識別() -> None:
    with pytest.raises(InvalidSemanticId) as 收:
        SemanticId.parse("工作.完成")
    assert 收.value.code == "INVALID_SEMANTIC_ID"


def test_合法的語義識別不被誤殺() -> None:
    assert SemanticId.parse("claim.naming-two-tracks.v1").value == "claim.naming-two-tracks.v1"
    assert BindingSlot.parse("engineering-checker.repository").value == (
        "engineering-checker.repository"
    )


def test_NFD_碰撞必須拒絕而不是產生第二份摘要() -> None:
    # 同形不同碼的兩個 key 會產生兩份不同的 bytes，於是同一個「東西」有兩個 digest。
    with pytest.raises(TextNotCanonical) as 收:
        canonical_json_bytes({分解的中文: 1})
    assert 收.value.code == "TEXT_NOT_NFC"
    with pytest.raises(TextNotCanonical):
        canonical_json_bytes({"值": 分解的中文})


def test_摘要是穩定的十六進位() -> None:
    參 = sha256_ref(b"nova")
    assert isinstance(參, Sha256Ref)
    assert 參.hex == sha256_ref(b"nova").hex
    assert len(參.hex) == 十六進位長度
    assert 參.hex != sha256_ref(b"novb").hex


def test_浮點不得進入摘要() -> None:
    # 拒的不只是 NaN：float 的 repr 與精度本身就是 digest 漂移的來源。
    for 值 in (float("nan"), 0.1 + 0.2):
        with pytest.raises(ValueNotCanonical):
            canonical_json_bytes({"值": 值})


def test_claim_參照帶版次與摘要() -> None:
    參 = ClaimRef(
        claim_id=SemanticId.parse("naming.unicode-python-ascii-boundaries"),
        revision=1,
        digest=sha256_ref(b"x"),
    )
    assert 參.revision == 1
    with pytest.raises(ValueError, match="revision"):
        ClaimRef(claim_id=SemanticId.parse("a.b"), revision=0, digest=sha256_ref(b"x"))


def test_時間是帶型別的而不是裸數字() -> None:
    assert Duration.from_millis(一點五秒).millis == 一點五秒
    assert Instant.from_epoch_millis(0).epoch_millis == 0
    with pytest.raises(ValueError, match="millis"):
        Duration.from_millis(-1)


def test_case_失敗種類是封閉的() -> None:
    assert {種.value for 種 in CaseFailureKind} == {
        "CLAIM_REJECTED",
        "UNBOUND_SUBJECT",
        "UNSUPPORTED_ISOLATION",
        "HARNESS_ERROR",
        "HARNESS_LIMIT",
    }


def test_語義識別只准小寫() -> None:
    # 大小寫在不同 DB 與檔案系統的比對規則不同，允許大寫就是允許同名不同物。
    for 壞 in ("Work.done", "work.Done"):
        with pytest.raises(InvalidSemanticId):
            SemanticId.parse(壞)


def test_語義識別要整串符合而不是開頭符合() -> None:
    # match 只看開頭：`work.done 還有別的` 會被當成合法而把後面整段吞掉。
    for 壞 in ("work.done 還有別的", "work.done!", "work.done\n"):
        with pytest.raises(InvalidSemanticId):
            SemanticId.parse(壞)


def test_陣列裡的值也要遞迴檢查() -> None:
    with pytest.raises(TextNotCanonical):
        canonical_json_bytes([分解的中文])
    with pytest.raises(TextNotCanonical):
        canonical_json_bytes({"值": [{"內": 分解的中文}]})


def test_摘要的位元組是中文原樣且無多餘空白() -> None:
    # ensure_ascii=True 會把中文變成 \u 逃逸，separators 用預設會多出空白——
    # 兩者都讓同一個值有第二種寫法，也就是第二個 digest。
    assert canonical_json_bytes({"b": 2, "a": "中"}) == '{"a":"中","b":2}'.encode()
