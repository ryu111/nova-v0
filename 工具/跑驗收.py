"""薄殼：呼叫 pytest 跑 ClaimSpec 的 case，**原樣透傳 exit code**。

存在理由（計畫 01 Task 9）：驗收要有一個固定的入口，讓「怎麼跑」不是每個人各自發明。
但它只是薄殼——`工具/` 的職責是組參數並呼叫，不做任何判斷。

**不改寫結果。** 它不吞 exit code、不重試、不把 error 降級成 warning。
pytest 回幾就回幾；判定在 `nova/權威/判準/保證規格執行.py`，顯示在
`nova/基礎設施/裁定執行/外部測試框架.py`，這裡兩者都不碰。
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any

專案根 = Path(__file__).resolve().parent.parent
if str(專案根) not in sys.path:
    sys.path.insert(0, str(專案根))

from nova.基礎設施.裁定執行.原語 import 內部, 原語, 原語目錄  # noqa: E402
from nova.基礎設施.裁定執行.外部測試框架 import ClaimCatalog  # noqa: E402
from nova.核心.摘要 import sha256_ref  # noqa: E402
from nova.權威.判準.保證規格模型 import (  # noqa: E402
    ClaimSpec,
    ClaimSpecLoader,
    ClaimSpecStructuralError,
)
from nova.權威.判準.保證規格編譯 import (  # noqa: E402
    CompileFailure,
    TestPlan,
    compile_claim,
    綁定清單,
    隔離供給,
)

外掛 = "nova.基礎設施.裁定執行.外部測試框架"
測試支援 = {
    "claimspec.controls.direct-red-preserved": (
        "驗收/保證規格語言/測_敏感度.py::test_negative_必須由指定_predicate_拒絕"
    ),
    "claimspec.mutation.named-control-only": (
        "驗收/保證規格語言/測_指定突變.py::測試_防恆真_表面三分之一但具名守衛被殺則接受"
    ),
    "claimspec.framework.no-verdict-rewrite": (
        "nova/基礎設施/裁定執行/test_外部框架.py::test_判定裡根本沒有_xfail"
    ),
    "engineering.named-mutation.repeatable": (
        "架構/test_工程規範.py::test_突變相符時回零而且還原原檔"
    ),
    "engineering.gates.automatically-enforced": "架構/test_工程規範.py::test_閘清單本身不得縮水",
    "core.identity-and-digest.canonical": "nova/核心/test_值型別.py",
    "claimspec.language.closed-schema": "驗收/保證規格語言/測_meta_schema.py",
    "claimspec.language.effect-delivery-conditional": "驗收/保證規格語言/測_meta_schema.py",
    "claimspec.compiler.deterministic-typed-plan": "nova/權威/判準/test_保證規格語言.py",
    "workshop.toplevel.declared-equals-scanned": "架構/test_目錄規則.py",
}
實體提供者 = frozenset(
    {
        "claimspec-execution.pytest",
        "claimspec-runner.in-process",
        "claimspec-mutation.in-process",
        "claimspec-framework.pytest",
        "execution-envelope.reference",
        "toolchain-probe.repository",
        "directory-rules.repository",
        "engineering-config.repository",
        "named-mutation-runner.repository",
        "engineering-checker.repository",
        "gate-runner.repository",
        "core-values.in-process",
        "claimspec-loader.in-process",
        "claimspec-compiler.in-process",
    }
)


@dataclass(frozen=True, slots=True)
class 跑驗收結果:
    """跑驗收的執行結果，帶 exit_code 與 failure code。"""

    exit_code: int
    code: str = "OK"
    細節: str = ""


def 讀_json(路徑: Path) -> dict[str, Any]:
    """I/O 留在薄殼；typed model 與 compiler 都只收資料。"""
    內容 = json.loads(路徑.read_text(encoding="utf-8"))
    if not isinstance(內容, dict):
        raise ValueError("頂層不是 object")
    return 內容


def 載入_claim(路徑: Path, 根: Path) -> tuple[ClaimSpec | ClaimSpecStructuralError, dict[str, Any]]:
    """由正式 loader 解析 ClaimSpec，同時保留 runtime 需要的宣告資料。"""
    try:
        原始 = 讀_json(路徑)
    except (OSError, ValueError, json.JSONDecodeError) as 誤:
        return ClaimSpecStructuralError("MALFORMED_JSON", "/", str(誤)), {}
    載入器 = ClaimSpecLoader(
        meta_schema=讀_json(根 / "規格" / "語言" / "ClaimSpec.schema.json"),
        effect_schema=讀_json(根 / "規格" / "介面" / "效果契約.schema.json"),
    )
    return 載入器.load(路徑.read_bytes()), 原始


def 生產綁定(根: Path, binding_ids: list[str]) -> 綁定清單 | 跑驗收結果:
    """只收實際存在的 binding manifest 與本 task 在程序內提供的 execution runtime。"""
    清單: list[dict[str, Any]] = []
    for 路徑 in sorted(根.glob("規格/**/綁定/*.binding.json")):
        try:
            清單.append(讀_json(路徑))
        except OSError, ValueError, json.JSONDecodeError:
            continue
    if binding_ids:
        已知 = {str(項.get("manifest_id")): 項 for 項 in 清單}
        未知 = next((名 for 名 in binding_ids if 名 not in 已知), None)
        if 未知 is not None:
            return 跑驗收結果(1, "UNKNOWN_BINDING_ID", 未知)
        清單 = [已知[名] for 名 in binding_ids]
    綁定 = {
        slot: f"sha256:{sha256_ref(f'runtime-provider:{slot}'.encode()).hex}" for slot in 實體提供者
    }
    for manifest in 清單:
        for 項 in manifest.get("bindings", []):
            if isinstance(項, dict) and "binding_slot" in 項 and "capability_digest" in 項:
                綁定[str(項["binding_slot"])] = str(項["capability_digest"])
    return 綁定清單("claim-runner.production", 1, 綁定)


def 原語目錄_由宣告(原始: dict[str, Any], spec: ClaimSpec) -> 原語目錄:
    """Task 16 尚未提供 admitted catalog；本 task 先把 claim 宣告的 primitive 送進 compiler。"""
    catalog_id = str(原始.get("primitive_catalog", {}).get("catalog_id", "claim.runtime"))
    produces = str(spec.observations[0]["type"])
    primitive_ids = sorted({str(步["primitive"]) for 步 in spec.stimulus})
    return 原語目錄(catalog_id, tuple(原語(名, 內部, produces) for 名 in primitive_ids))


def _python_json(程式: str) -> list[str]:
    return [sys.executable, "-c", 程式]


def _工程檢查設定(spec: ClaimSpec) -> dict[str, Any]:
    基線程式 = (
        "import json;from 架構.檢查工程規範 import 掃描倉庫;"
        "r=掃描倉庫();print(json.dumps({'code':r[0].code if r else 'OK'}))"
    )
    負控 = {
        str(項["control_id"]): _python_json(
            "import json;from pathlib import PurePosixPath;"
            "from 架構.檢查工程規範 import check_fixture;"
            f"r=check_fixture(PurePosixPath({str(項['faulty_subject'])!r}).name);"
            "print(json.dumps({'code':r.code}))"
        )
        for 項 in spec.controls.negative
    }
    return {"kind": "command", "baseline": _python_json(基線程式), "negative": 負控}


def _工程設定_runtime(spec: ClaimSpec) -> dict[str, Any]:
    def command(path: str) -> list[str]:
        程式 = (
            "import json;from 驗收.工具鏈.測_工具鏈啟動 import validate_engineering_config as v;"
            f"r=v({path!r});print(json.dumps({{'code':r.code,'violations':list(r.違反)}}))"
        )
        return _python_json(程式)

    負控 = {
        str(項["control_id"]): command(str(項["faulty_subject"])) for 項 in spec.controls.negative
    }
    return {"kind": "command", "baseline": command("pyproject.toml"), "negative": 負控}


def _工具鏈_runtime(spec: ClaimSpec) -> dict[str, Any]:
    基底 = [sys.executable, "工具/驗工具鏈.py"]
    壞態產出 = {
        "guard-mutation-survives": ["NAMED_MUTATION_SURVIVED:收窄"],
        "also-copy-removed": ["MUTATION_TESTS_NOT_COPIED:also_copy"],
    }
    負控 = {
        str(項["control_id"]): _python_json(
            "import json;from 工具.驗工具鏈 import 分面;"
            f"print(json.dumps(分面({壞態產出[str(項['control_id'])]!r})))"
        )
        for 項 in spec.controls.negative
    }
    return {"kind": "command", "baseline": [*基底, "--分面輸出"], "negative": 負控}


def runtime_設定(spec: ClaimSpec, 原始: dict[str, Any]) -> dict[str, Any]:
    """TestPlan 綁到實際 runtime provider；沒有 provider 的 slot 不會走到這裡。"""
    slot = spec.subject.binding_slot.value
    if slot == "claimspec-execution.pytest":
        return {"kind": "claimspec-execution"}
    if slot == "execution-envelope.reference":
        return {"kind": "execution-envelope", **原始.get("parameters", {})}
    builders = {
        "toolchain-probe.repository": _工具鏈_runtime,
        "engineering-checker.repository": _工程檢查設定,
        "engineering-config.repository": _工程設定_runtime,
    }
    if slot in builders:
        return builders[slot](spec)
    if spec.claim_id.value in 測試支援:
        node = 測試支援[spec.claim_id.value]
        return {
            "kind": "command",
            "mode": "exit",
            "baseline": [sys.executable, "-m", "pytest", "-q", node],
        }
    return {"kind": "failure", "failure": "UNBOUND_SUBJECT"}


def 計畫資料(plan: TestPlan, runtime: dict[str, Any]) -> dict[str, Any]:
    """把 typed TestPlan 的封閉欄位交給 pytest plugin。"""
    return {
        "plan_digest": f"sha256:{plan.digest.hex}",
        "claim_id": plan.claim_id.value,
        "predicates": list(plan.predicates),
        "cases": list(plan.cases),
        "runtime": runtime,
    }


def 獨立失敗計畫(claim_id: str, code: str) -> dict[str, Any]:
    """編譯環境不足時仍交外框架產出一格 typed evidence，不冒充 CLAIM_REJECTED。"""
    return {
        "plan_digest": f"compile-failure:{claim_id}:{code}",
        "claim_id": claim_id,
        "predicates": [],
        "cases": [{"kind": "ACTUAL", "case_id": "actual"}],
        "runtime": {"kind": "failure", "failure": code},
    }


def 解析_claim_paths(
    claim_ids: list[str], catalog: ClaimCatalog
) -> list[tuple[str, Path]] | 跑驗收結果:
    """先解析全部 id，維持 UNKNOWN／MISSING 不被後續編譯錯誤掩蓋的優先序。"""
    出: list[tuple[str, Path]] = []
    for claim_id in claim_ids:
        狀態, 路徑 = catalog.解析(claim_id)
        if 狀態 == "UNKNOWN_CLAIM_ID":
            print(f"UNKNOWN_CLAIM_ID: 查無 claim_id={claim_id}", file=sys.stderr)
            return 跑驗收結果(1, "UNKNOWN_CLAIM_ID", claim_id)
        if 狀態 == "CLAIM_FILE_MISSING":
            print(
                f"CLAIM_FILE_MISSING: claim_id={claim_id} 對應檔案不存在或不可讀: {路徑}",
                file=sys.stderr,
            )
            return 跑驗收結果(1, "CLAIM_FILE_MISSING", f"{claim_id}:{路徑}")
        assert 路徑 is not None
        出.append((claim_id, 路徑))
    return 出


def 編譯計畫們(
    claim_paths: list[tuple[str, Path]], 根: Path, 綁定: 綁定清單
) -> tuple[list[dict[str, Any]], str] | 跑驗收結果:
    """ClaimSpec → TestPlan；環境不足另做獨立結果 plan，不壓成裁定。"""
    計畫們: list[dict[str, Any]] = []
    首個獨立結果 = ""
    for claim_id, 路徑 in claim_paths:
        規格, 原始 = 載入_claim(路徑, 根)
        if isinstance(規格, ClaimSpecStructuralError):
            print(f"{規格.code}: {claim_id}{規格.pointer}: {規格.細節}", file=sys.stderr)
            return 跑驗收結果(1, 規格.code, f"{claim_id}{規格.pointer}")
        編譯 = compile_claim(
            規格,
            原語目錄_由宣告(原始, 規格),
            綁定,
            隔離供給(frozenset({"COOPERATIVE_PROCESS"})),
        )
        if isinstance(編譯, CompileFailure):
            if 編譯.code not in {"UNBOUND_SUBJECT", "UNSUPPORTED_ISOLATION"}:
                print(f"{編譯.code}: {claim_id}: {編譯.細節}", file=sys.stderr)
                return 跑驗收結果(1, 編譯.code, f"{claim_id}:{編譯.細節}")
            首個獨立結果 = 首個獨立結果 or 編譯.code
            計畫們.append(獨立失敗計畫(claim_id, 編譯.code))
        else:
            計畫們.append(計畫資料(編譯, runtime_設定(規格, 原始)))
    return 計畫們, 首個獨立結果


def 呼叫計畫框架(計畫們: list[dict[str, Any]], 其餘: list[str], 根: Path) -> int:
    """把計畫寫進一次性目錄，經 --claim-plan 跑完並在刪除前輸出 evidence。"""
    with tempfile.TemporaryDirectory(prefix="nova-claim-") as 暫存:
        暫存根 = Path(暫存)
        證據 = 暫存根 / "evidence.jsonl"
        計畫路徑們: list[Path] = []
        for 序, 計畫 in enumerate(計畫們):
            計畫路徑 = 暫存根 / f"{序}.plan.json"
            計畫路徑.write_text(json.dumps(計畫, ensure_ascii=False), encoding="utf-8")
            計畫路徑們.append(計畫路徑)
        指令 = [
            sys.executable,
            "-m",
            "pytest",
            "-q",
            "-p",
            外掛,
            *其餘,
            *(str(路徑) for 路徑 in 計畫路徑們),
        ]
        for 計畫路徑 in 計畫路徑們:
            指令 += ["--claim-plan", str(計畫路徑)]
        指令 += ["--claim-evidence", str(證據)]
        完成 = subprocess.run(指令, cwd=根, check=False)
        if 證據.is_file():
            print(證據.read_text(encoding="utf-8"), end="")
        return 完成.returncode


def 跑驗收(
    參數: list[str],
    catalog: ClaimCatalog | None = None,
    專案根目錄: Path = 專案根,
) -> 跑驗收結果:
    """解析 --claim 與 --binding，走 ClaimCatalog 解析，並透傳呼叫 pytest。"""
    剖析器 = argparse.ArgumentParser(description="跑驗收", add_help=False)
    剖析器.add_argument("--claim", action="append", default=[], help="要跑的 claim id")
    剖析器.add_argument("--binding", action="append", default=[], help="要綁定的 binding id")
    已知, 其餘 = 剖析器.parse_known_args(參數)

    用目錄 = catalog if catalog is not None else ClaimCatalog.掃描(專案根目錄)
    claim_paths = 解析_claim_paths(list(已知.claim), 用目錄)
    if isinstance(claim_paths, 跑驗收結果):
        return claim_paths
    if 已知.claim:
        綁定 = 生產綁定(專案根目錄, list(已知.binding))
        if isinstance(綁定, 跑驗收結果):
            print(f"{綁定.code}: {綁定.細節}", file=sys.stderr)
            return 綁定
        編譯結果 = 編譯計畫們(claim_paths, 專案根目錄, 綁定)
        if isinstance(編譯結果, 跑驗收結果):
            return 編譯結果
        計畫們, 首個獨立結果 = 編譯結果
        exit_code = 呼叫計畫框架(計畫們, 其餘, 專案根目錄)
        code = 首個獨立結果 or ("OK" if exit_code == 0 else "FAIL")
        return 跑驗收結果(exit_code, code, ",".join(已知.claim))

    指令 = [sys.executable, "-m", "pytest", "-q", "-p", 外掛, *其餘]
    完成 = subprocess.run(指令, cwd=專案根目錄, check=False)
    return 跑驗收結果(
        exit_code=完成.returncode,
        code="OK" if 完成.returncode == 0 else "FAIL",
    )


def 跑(參數: list[str], catalog: ClaimCatalog | None = None) -> int:
    """把參數接到 pytest 後面，回它的 exit code。中間不做任何翻譯。"""
    return 跑驗收(參數, catalog=catalog).exit_code


if __name__ == "__main__":
    raise SystemExit(跑(sys.argv[1:]))
