"""工程規範 checker 的近身測試：每條規則都要有一個事前固定的錯誤 subject 把它打紅。"""

import json
import pathlib
from dataclasses import replace

from 架構.檢查工程規範 import check_fixture, 掃描倉庫, 檢查檔案, 載入規則

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
    "MIXED_SCRIPT_IDENTIFIER": "python_identifiers_single_script",
    "SCRIPT_NOT_IN_TWO_TRACKS": "identifiers_stay_in_two_tracks",
    "IDENTIFIER_NOT_NFC": "python_identifiers_are_nfc",
    "NON_ASCII_SHELL_NAME": "shell_names_are_ascii",
    "NON_ASCII_JSON_FIELD": "json_field_names_are_ascii",
    "NON_ASCII_SQL_NAME": "sql_identifiers_are_ascii",
    "DYNAMIC_SHELL_NAME_UNVERIFIABLE": "dynamic_shell_name_rejected",
}
宣告過的_claim = (
    "規格/工程/保證/檔案落點唯一.claim.json",
    "規格/工程/保證/識別字雙軌.claim.json",
)


def test_錯置與超長都被拒絕() -> None:
    assert check_fixture("錯置_repository.py").code == "PLACEMENT_LAYER_MISMATCH"
    assert check_fixture("超長函式.py").code == "FUNCTION_TOO_LARGE"


def test_雙軌命名負控() -> None:
    assert check_fixture("混script識別字.py").code == "MIXED_SCRIPT_IDENTIFIER"
    assert check_fixture("中文shell變數.sh").code == "NON_ASCII_SHELL_NAME"


def test_識別字要同時是_NFC_與_NFKC() -> None:
    # ast.parse 會先 NFKC 正規化才交出名字，全形 a（U+FF41）進 AST 已變成 ASCII a——
    # 所以這條只能靠 tokenize 讀原形，用 AST 檢查等於什麼都沒檢查。
    分解 = "\u0065\u0301"  # NFD 的 é
    for 壞名 in (f"值{分解}", "\uff41值"):
        結果 = 檢查檔案("nova/核心/x.py", f"{壞名} = 1\n", 載入規則(), 查計畫目錄=False)
        assert 結果.code == "IDENTIFIER_NOT_NFC", 壞名


def test_擴充區漢字也算_Han() -> None:
    # 用碼點區間（U+4E00 到 U+9FFF）判 Han 會把 CJK Ext B 的 U+20000 判成兩軌之外，
    # 於是一個純漢字識別字被誤殺。改用 unicodedata.name() 的 CJK 前綴才涵蓋得到。
    純漢字 = 檢查檔案("nova/核心/x.py", "工\U00020000 = 1\n", 載入規則(), 查計畫目錄=False)
    assert 純漢字.code == "OK"
    混寫 = 檢查檔案("nova/核心/x.py", "x\U00020000 = 1\n", 載入規則(), 查計畫目錄=False)
    assert 混寫.code == "MIXED_SCRIPT_IDENTIFIER"


def test_兩軌以外的_script_不是單一就放行() -> None:
    # allowed_scripts 若只是說明而沒人執行，純 Cyrillic 識別字會因為「單一 script」
    # 直接放行——宣告了卻沒人執行的規則比沒宣告更糟。
    結果 = 檢查檔案("nova/核心/x.py", "\u043f\u0440\u0438 = 1\n", 載入規則(), 查計畫目錄=False)
    assert 結果.code == "SCRIPT_NOT_IN_TWO_TRACKS"


def test_跨程序名的三種載體都要_ASCII() -> None:
    規則 = 載入規則()
    json_結果 = 檢查檔案("規格/工程/保證/x.claim.json", '{"欄位": 1}', 規則, 查計畫目錄=False)
    assert json_結果.code == "NON_ASCII_JSON_FIELD"
    sql_結果 = 檢查檔案("nova/狀態/x.sql", "CREATE TABLE 工作 (id TEXT);\n", 規則, 查計畫目錄=False)
    assert sql_結果.code == "NON_ASCII_SQL_NAME"
    綠 = 檢查檔案(
        "nova/狀態/x.sql",
        "-- 建表：工作\nCREATE TABLE work (note TEXT DEFAULT '中文');\n",
        規則,
        查計畫目錄=False,
    )
    assert 綠.code == "OK"


def test_算出來的_shell_名不得當成沒有名字() -> None:
    # 與動態 import 同一個坑：掃不到不等於沒有。
    for 原始碼 in ('declare "$前綴_值=1"\n', 'eval "$n=1"\n'):
        結果 = 檢查檔案("工具/x.sh", 原始碼, 載入規則(), 查計畫目錄=False)
        assert 結果.code == "DYNAMIC_SHELL_NAME_UNVERIFIABLE", 原始碼


def test_靜態寫法的違規邊會紅() -> None:
    原始碼 = "from nova.應用.調度 import 調度\n"
    結果 = 檢查檔案("nova/核心/洩漏.py", 原始碼, 載入規則(), 查計畫目錄=False)
    assert 結果.code == "LAYER_DEPENDENCY_VIOLATION"


def test_動態_import_的同一條違規邊也要被抓到() -> None:
    # docs/陷阱.md 記載的坑：掃描器只認 ast.Import 時，把違規邊改寫成
    # importlib.import_module("上層.X") 就完全不被認得，全綠通過。
    原始碼 = 'import importlib\n\nimportlib.import_module("nova.應用.調度")\n'
    結果 = 檢查檔案("nova/核心/洩漏.py", 原始碼, 載入規則(), 查計畫目錄=False)
    assert 結果.code == "LAYER_DEPENDENCY_VIOLATION"


def test_非_literal_的動態_import_不得當成沒有邊() -> None:
    原始碼 = "import importlib\n\n名稱 = '未知'\nimportlib.import_module(名稱)\n"
    結果 = 檢查檔案("nova/核心/洩漏.py", 原始碼, 載入規則(), 查計畫目錄=False)
    assert 結果.code == "DYNAMIC_IMPORT_UNVERIFIABLE"


def test_合法的下行依賴不被誤殺() -> None:
    原始碼 = "from nova.核心.識別 import SemanticId\n"
    結果 = 檢查檔案("nova/應用/調度.py", 原始碼, 載入規則(), 查計畫目錄=False)
    assert 結果.code == "OK"


def test_路徑必須恰命中一個落點_owner() -> None:
    規則 = 載入規則()
    重疊 = replace(規則, 落點=(("nova/*/**", "nova層"), ("nova/核心/**", "核心專屬")))
    assert 檢查檔案("nova/核心/x.py", "", 重疊, 查計畫目錄=False).code == "AMBIGUOUS_PLACEMENT"
    無人 = replace(規則, 落點=(("前端/**", "前端"),))
    assert 檢查檔案("nova/核心/x.py", "", 無人, 查計畫目錄=False).code == "NO_PLACEMENT_OWNER"


def test_未列在計畫_Create_清單的新檔被擋() -> None:
    結果 = 檢查檔案("nova/核心/沒人計畫過.py", '"""無。"""\n', 載入規則())
    assert 結果.code == "UNPLANNED_FILE"


def test_已列在計畫的檔不被誤殺() -> None:
    原始碼 = '"""最小守衛。"""\n\n\ndef 收窄(值: int) -> int:\n    """夾。"""\n    return 值\n'
    結果 = 檢查檔案("nova/核心/工具鏈守衛.py", 原始碼, 載入規則())
    assert 結果.code == "OK"


def test_claim_檔的固定負控與實際行為一致() -> None:
    for claim_路徑 in 宣告過的_claim:
        宣告 = json.loads(pathlib.Path(claim_路徑).read_text(encoding="utf-8"))
        for 負控 in 宣告["controls"]["negative"]:
            檔名 = pathlib.PurePosixPath(負控["faulty_subject"]).name
            結果 = check_fixture(檔名)
            assert {碼對照判準[結果.code]} == set(負控["must_fail_exactly"]), 檔名


def test_claim_檔的正控是整棵倉庫都綠() -> None:
    assert 掃描倉庫() == []
