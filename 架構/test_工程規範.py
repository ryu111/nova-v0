"""工程規範 checker 的近身測試：每條規則都要有一個事前固定的錯誤 subject 把它打紅。"""

import json
import pathlib
from dataclasses import replace

from 架構.檢查工程規範 import check_fixture, 掃描repo, 檢查檔案, 載入規則

碼對照判準 = {
    "AMBIGUOUS_PLACEMENT": "placement_owner_is_unique",
    "NO_PLACEMENT_OWNER": "placement_owner_is_unique",
    "PLACEMENT_LAYER_MISMATCH": "placement_matches_content",
    "FUNCTION_TOO_LARGE": "function_within_size_limit",
    "MODULE_TOO_LARGE": "module_and_class_within_size_limit",
    "CLASS_TOO_LARGE": "module_and_class_within_size_limit",
    "LAYER_DEPENDENCY_VIOLATION": "imports_only_go_downward",
    "DYNAMIC_IMPORT_UNVERIFIABLE": "no_unverifiable_dynamic_import",
    "UNPLANNED_FILE": "file_is_declared_in_a_plan",
}


def test_錯置與超長都被拒絕() -> None:
    assert check_fixture("錯置_repository.py").code == "PLACEMENT_LAYER_MISMATCH"
    assert check_fixture("超長函式.py").code == "FUNCTION_TOO_LARGE"


def test_靜態寫法的違規邊會紅() -> None:
    原始碼 = "from nova.應用.調度 import 調度\n"
    結果 = 檢查檔案("nova/核心/洩漏.py", 原始碼, 載入規則(), 查計畫目錄=False)
    assert 結果.code == "LAYER_DEPENDENCY_VIOLATION"


def test_動態import的同一條違規邊也要被抓到() -> None:
    # docs/陷阱.md 記載的坑：掃描器只認 ast.Import 時，把違規邊改寫成
    # importlib.import_module("上層.X") 就完全不被認得，全綠通過。
    原始碼 = 'import importlib\n\nimportlib.import_module("nova.應用.調度")\n'
    結果 = 檢查檔案("nova/核心/洩漏.py", 原始碼, 載入規則(), 查計畫目錄=False)
    assert 結果.code == "LAYER_DEPENDENCY_VIOLATION"


def test_非literal的動態import不得當成沒有邊() -> None:
    原始碼 = "import importlib\n\n名稱 = '未知'\nimportlib.import_module(名稱)\n"
    結果 = 檢查檔案("nova/核心/洩漏.py", 原始碼, 載入規則(), 查計畫目錄=False)
    assert 結果.code == "DYNAMIC_IMPORT_UNVERIFIABLE"


def test_合法的下行依賴不被誤殺() -> None:
    原始碼 = "from nova.核心.識別 import SemanticId\n"
    結果 = 檢查檔案("nova/應用/調度.py", 原始碼, 載入規則(), 查計畫目錄=False)
    assert 結果.code == "OK"


def test_路徑必須恰命中一個落點owner() -> None:
    規則 = 載入規則()
    重疊 = replace(規則, 落點=(("nova/*/**", "nova層"), ("nova/核心/**", "核心專屬")))
    assert 檢查檔案("nova/核心/x.py", "", 重疊, 查計畫目錄=False).code == "AMBIGUOUS_PLACEMENT"
    無人 = replace(規則, 落點=(("前端/**", "前端"),))
    assert 檢查檔案("nova/核心/x.py", "", 無人, 查計畫目錄=False).code == "NO_PLACEMENT_OWNER"


def test_未列在計畫Create清單的新檔被擋() -> None:
    結果 = 檢查檔案("nova/核心/沒人計畫過.py", '"""無。"""\n', 載入規則())
    assert 結果.code == "UNPLANNED_FILE"


def test_已列在計畫的檔不被誤殺() -> None:
    原始碼 = '"""最小守衛。"""\n\n\ndef 收窄(值: int) -> int:\n    """夾。"""\n    return 值\n'
    結果 = 檢查檔案("nova/核心/工具鏈守衛.py", 原始碼, 載入規則())
    assert 結果.code == "OK"


def test_claim檔的固定負控與實際行為一致() -> None:
    宣告 = json.loads(
        pathlib.Path("規格/工程/保證/檔案落點唯一.claim.json").read_text(encoding="utf-8")
    )
    for 負控 in 宣告["controls"]["negative"]:
        檔名 = pathlib.PurePosixPath(負控["faulty_subject"]).name
        結果 = check_fixture(檔名)
        assert {碼對照判準[結果.code]} == set(負控["must_fail_exactly"]), 檔名


def test_claim檔的正控是整棵repo都綠() -> None:
    assert 掃描repo() == []
