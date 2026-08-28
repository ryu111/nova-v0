from __future__ import annotations

import json
from pathlib import Path

from 架構.檢查第十五第十三閘 import 固定債, 檢查


def 寫清單(根: Path, **覆寫: object) -> None:
    (根 / "規格/判準/保證").mkdir(parents=True)
    manifest: dict[str, object] = {
        "frozen_baseline": sorted(固定債),
        "debt": [],
        "t13_state": "UNBLOCKED",
        "typed_result_ready": True,
        "string_set_compiler_ready": True,
    }
    manifest.update(覆寫)
    (根 / "規格/判準/保證/R15-01-migration-debt.json").write_text(
        json.dumps(manifest), encoding="utf-8"
    )


def 測試_正常三項條件通過(tmp_path: Path) -> None:
    寫清單(tmp_path)
    assert 檢查(tmp_path) == []


def 測試_新增捕獲全部必須紅(tmp_path: Path) -> None:
    寫清單(tmp_path)
    claim = {
        "claim_id": "new.claim.with.catch-all",
        "judge": {
            "all_of": [
                {"operator": "EQUALS", "left": {"observation": "code"}},
                {"operator": "NOT_EQUALS", "left": {"observation": "code"}},
            ]
        },
    }
    (tmp_path / "規格/判準/保證/新.claim.json").write_text(json.dumps(claim), encoding="utf-8")
    assert any("新 claim 含 catch-all" in error for error in 檢查(tmp_path))


def 測試_清單債務擴張必須紅(tmp_path: Path) -> None:
    寫清單(tmp_path, debt=["not-in-baseline"], t13_state="BLOCKED")
    assert any("不得新增成員" in error for error in 檢查(tmp_path))


def 測試_阻塞解阻與債務狀態不一致必須紅(tmp_path: Path) -> None:
    寫清單(tmp_path, t13_state="BLOCKED")
    assert any("三項 predicate 不一致" in error for error in 檢查(tmp_path))


def 測試_就緒不足時解阻必須紅(tmp_path: Path) -> None:
    寫清單(tmp_path, typed_result_ready=False)
    assert any("三項 predicate 不一致" in error for error in 檢查(tmp_path))
