"""工具鏈 day-one 探針：確認 CPython 3.14／pytest／Hypothesis／xdist／mutmut 真的可用，
並確認格式、lint、docstring 與 strict 型別四個工程閘沒有被放寬。"""

import json
import pathlib
import tomllib
from dataclasses import dataclass

from hypothesis import given
from hypothesis import strategies as st

from nova.核心.工具鏈守衛 import 收窄

必要的_RUFF_規則 = frozenset(
    {"E", "F", "W", "I", "UP", "B", "SIM", "C4", "PIE"}
    | {"RUF", "ANN", "ASYNC", "DTZ", "D", "C90", "PLR"}
)
規定行寬 = 100
規定目標版本 = "py314"
規模上限 = (
    ("mccabe", "max-complexity", 10, "COMPLEXITY_LIMIT_RAISED"),
    ("pylint", "max-args", 6, "ARGS_LIMIT_RAISED"),
    ("pylint", "max-branches", 12, "BRANCHES_LIMIT_RAISED"),
    ("pylint", "max-statements", 60, "STATEMENTS_LIMIT_RAISED"),
)
MYPY_必開 = (
    ("strict", "MYPY_STRICT_DISABLED"),
    ("warn_unreachable", "MYPY_WARN_UNREACHABLE_DISABLED"),
    ("show_error_codes", "MYPY_ERROR_CODES_HIDDEN"),
)


違反對照判準 = {
    "MYPY_STRICT_DISABLED": "mypy_strict_enabled",
    "MYPY_WARN_UNREACHABLE_DISABLED": "mypy_strict_enabled",
    "MYPY_ERROR_CODES_HIDDEN": "mypy_strict_enabled",
    "RUFF_DOCSTRING_RULES_DISABLED": "ruff_docstring_rules_enabled",
    "COMPLEXITY_LIMIT_RAISED": "complexity_limit_at_10",
    "RUFF_RULES_DISABLED": "ruff_required_rules_selected",
    "RUFF_TARGET_VERSION_MISMATCH": "ruff_required_rules_selected",
    "RUFF_LINE_LENGTH_MISMATCH": "ruff_required_rules_selected",
    "ARGS_LIMIT_RAISED": "size_limits_at_declared_values",
    "BRANCHES_LIMIT_RAISED": "size_limits_at_declared_values",
    "STATEMENTS_LIMIT_RAISED": "size_limits_at_declared_values",
}


@dataclass(frozen=True, slots=True)
class 工程閘結果:
    code: str
    違反: tuple[str, ...]


def _檢_ruff(設定: dict[str, object]) -> list[str]:
    ruff = 設定.get("tool", {}).get("ruff", {})
    lint = ruff.get("lint", {})
    違反: list[str] = []
    if ruff.get("target-version") != 規定目標版本:
        違反.append("RUFF_TARGET_VERSION_MISMATCH")
    if ruff.get("line-length") != 規定行寬:
        違反.append("RUFF_LINE_LENGTH_MISMATCH")
    選取 = set(lint.get("select", []))
    if "D" not in 選取:
        違反.append("RUFF_DOCSTRING_RULES_DISABLED")
    if not (必要的_RUFF_規則 - {"D"}) <= 選取:
        違反.append("RUFF_RULES_DISABLED")
    for 節, 鍵, 上限, 碼 in 規模上限:
        if lint.get(節, {}).get(鍵) != 上限:
            違反.append(碼)
    return 違反


def _檢_mypy(設定: dict[str, object]) -> list[str]:
    mypy = 設定.get("tool", {}).get("mypy", {})
    return [碼 for 鍵, 碼 in MYPY_必開 if mypy.get(鍵) is not True]


def 由違反推出失敗判準(結果: 工程閘結果) -> set[str]:
    """把設定違反碼映成 ClaimSpec 的 predicate id，讓 must_fail_exactly 可被機械比對。"""
    失敗 = {違反對照判準[碼] for 碼 in 結果.違反}
    if 結果.code != "OK":
        失敗.add("gate_verdict_is_ok")
    return 失敗


def validate_engineering_config(路徑: str) -> 工程閘結果:
    with open(路徑, "rb") as 檔:
        設定 = tomllib.load(檔)
    違反 = tuple(_檢_ruff(設定) + _檢_mypy(設定))
    return 工程閘結果("ENGINEERING_GATE_WEAKENED" if 違反 else "OK", 違反)


@given(st.integers(min_value=-10_000, max_value=10_000))
def 測試_守衛確實限制值(值: int) -> None:
    assert 收窄(值) in range(-100, 101)


def 測試_工程閘不可被放寬() -> None:
    結果 = validate_engineering_config("驗收/工具鏈/fixtures/錯誤工具設定.toml")
    assert 結果.code == "ENGINEERING_GATE_WEAKENED"
    assert set(結果.違反) == {
        "MYPY_STRICT_DISABLED",
        "RUFF_DOCSTRING_RULES_DISABLED",
        "COMPLEXITY_LIMIT_RAISED",
    }


def 測試_工程閘的正控是本專案設定() -> None:
    assert validate_engineering_config("pyproject.toml").code == "OK"


def 測試_claim_檔的固定負控與實際違反一致() -> None:
    宣告 = json.loads(
        pathlib.Path("規格/工程/保證/工程規範首日起效.claim.json").read_text(encoding="utf-8")
    )
    負控 = 宣告["controls"]["negative"][0]
    結果 = validate_engineering_config(負控["faulty_subject"])
    assert 由違反推出失敗判準(結果) == set(負控["must_fail_exactly"])


def 測試_claim_檔的正控真的綠() -> None:
    宣告 = json.loads(
        pathlib.Path("規格/工程/保證/工程規範首日起效.claim.json").read_text(encoding="utf-8")
    )
    正控 = 宣告["controls"]["positive"][0]
    結果 = validate_engineering_config(正控["subject_binding"])
    assert 由違反推出失敗判準(結果) == set()
