#!/usr/bin/env python3
"""檢查 R15 migration debt 與 01 Task 13 的阻塞條件。"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

固定債 = frozenset(
    {
        "claimspec.controls.direct-red-preserved",
        "claimspec.mutation.named-control-only",
        "claimspec.framework.no-verdict-rewrite",
        "engineering.named-mutation.repeatable",
        "naming.unicode-python-ascii-boundaries",
        "engineering.gates.automatically-enforced",
        "core.identity-and-digest.canonical",
        "claimspec.language.closed-schema",
        "claimspec.language.effect-delivery-conditional",
        "claimspec.compiler.deterministic-typed-plan",
    }
)


def 讀_json(路徑: Path) -> dict[str, Any]:
    """讀取一份 JSON object，非 object 直接視為閘錯。"""
    值 = json.loads(路徑.read_text(encoding="utf-8"))
    if not isinstance(值, dict):
        raise ValueError(f"不是 object：{路徑}")
    return 值


def has_catch_all(裁定: Any) -> bool:  # noqa: ANN401
    """找出同 observation 的 EQUALS／NOT_EQUALS catch-all 配對。"""
    if isinstance(裁定, dict):
        all_of = 裁定.get("all_of")
        if isinstance(all_of, list):
            equals = {
                項.get("left", {}).get("observation")
                for 項 in all_of
                if isinstance(項, dict) and 項.get("operator") == "EQUALS"
            }
            not_equals = {
                項.get("left", {}).get("observation")
                for 項 in all_of
                if isinstance(項, dict) and 項.get("operator") == "NOT_EQUALS"
            }
            if equals & not_equals:
                return True
        return any(has_catch_all(v) for v in 裁定.values())
    if isinstance(裁定, list):
        return any(has_catch_all(v) for v in 裁定)
    return False


def 檢查(根目錄: Path) -> list[str]:
    """回傳所有 R15 gate violations；空清單代表通過。"""
    manifest_path = 根目錄 / "規格/判準/保證/R15-01-migration-debt.json"
    manifest = 讀_json(manifest_path)
    baseline = frozenset(manifest.get("frozen_baseline", []))
    debt = frozenset(manifest.get("debt", []))
    state = manifest.get("t13_state")
    readiness = {
        名稱: manifest.get(名稱) for 名稱 in ("typed_result_ready", "string_set_compiler_ready")
    }
    errors: list[str] = []
    if baseline != 固定債:
        errors.append("frozen_baseline 與 R15 決議的 10 份 claim 不符")
    if not debt <= baseline:
        errors.append("migration debt 只能從固定基線縮減，不得新增成員")
    if any(not isinstance(值, bool) for 值 in readiness.values()):
        errors.append("T13 readiness 必須是布林值")
    typed_result_ready = readiness["typed_result_ready"] is True
    string_set_compiler_ready = readiness["string_set_compiler_ready"] is True
    migration_debt_empty = not debt
    predicate = typed_result_ready and string_set_compiler_ready and migration_debt_empty
    expected_state = "UNBLOCKED" if predicate else "BLOCKED"
    if state != expected_state:
        errors.append(f"T13 狀態 {state!r} 與三項 predicate 不一致，應為 {expected_state}")
    for path in sorted((根目錄 / "規格").rglob("*.claim.json")):
        claim = 讀_json(path)
        claim_id = claim.get("claim_id")
        if has_catch_all(claim.get("judge")) and claim_id not in debt:
            errors.append(f"新 claim 含 catch-all：{claim_id}")
    return errors


def main() -> int:
    """執行 R15 gate 並以非零表示阻塞。"""
    根目錄 = Path(__file__).resolve().parent.parent
    errors = 檢查(根目錄)
    if errors:
        for error in errors:
            print(f"R15-T13 紅：{error}", file=sys.stderr)
        return 1
    state = 讀_json(根目錄 / "規格/判準/保證/R15-01-migration-debt.json")["t13_state"]
    print(f"R15-T13 綠：T13 狀態 {state}；三項 readiness 與 migration debt 均有效")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
