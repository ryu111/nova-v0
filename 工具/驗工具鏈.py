"""day-one 工具鏈探針薄殼。

確認鎖定的 CPython／pytest／Hypothesis／xdist／mutmut 真的在線，並以兩個事前固定的
錯誤 subject 證明這條工具鏈有牙——守衛突變會被殺、缺測試不會被當成功。
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import tempfile
import tomllib
from pathlib import Path

專案根 = Path(__file__).resolve().parent.parent
守衛路徑 = 專案根 / "nova" / "核心" / "工具鏈守衛.py"
測試路徑 = 專案根 / "驗收" / "工具鏈" / "測_工具鏈啟動.py"

通過 = "OK"
應鎖定的版本 = {"pytest": "9.1.1", "pytest-xdist": "3.8.0", "mutmut": "3.7.0"}
臨時專案設定 = """\
[tool.pytest.ini_options]
python_files = ["測_*.py", "test_*.py"]
python_functions = ["測試_*", "test_*"]
python_classes = ["測_*", "Test*"]
pythonpath = ["."]

[tool.mutmut]
source_paths = ["nova/核心"]
tests_dir = ["驗收/工具鏈"]
use_git_change_detection = false
"""


def 取節(設定: object, *鍵路徑: str) -> dict[str, object]:
    """沿鍵路徑取出巢狀 TOML 表；任一層不是表就回空表，讓缺節與型別錯一律落入既有 failure code。"""
    目前: object = 設定
    for 鍵 in 鍵路徑:
        if not isinstance(目前, dict):
            return {}
        目前 = 目前.get(鍵, {})
    return 目前 if isinstance(目前, dict) else {}


def 讀專案設定() -> dict[str, object]:
    """讀出 repo 根的 pyproject.toml，作為所有設定形狀檢查的唯一來源。"""
    with (專案根 / "pyproject.toml").open("rb") as 檔:
        return tomllib.load(檔)


def 檢查python版本() -> str:
    """確認直譯器恰為 .python-version 指定的版本；不接受相近的 minor／patch。"""
    期望 = (專案根 / ".python-version").read_text(encoding="utf-8").strip()
    實際 = ".".join(str(數) for 數 in sys.version_info[:3])
    return 通過 if 實際 == 期望 else f"PYTHON_VERSION_MISMATCH:{實際}!={期望}"


def 檢查鎖定版本() -> str:
    """確認已安裝的測試工具版本與 uv.lock 的鎖定值一致，缺套件與版本漂移分開報。"""
    from importlib import metadata

    for 名稱, 期望 in 應鎖定的版本.items():
        try:
            實際 = metadata.version(名稱)
        except metadata.PackageNotFoundError:
            return f"TOOL_NOT_INSTALLED:{名稱}"
        if 實際 != 期望:
            return f"TOOL_VERSION_MISMATCH:{名稱}:{實際}!={期望}"
    try:
        metadata.version("hypothesis")
    except metadata.PackageNotFoundError:
        return "TOOL_NOT_INSTALLED:hypothesis"
    return 通過


def 檢查探索設定(設定: object) -> str:
    """確認 pytest 同時 discover 中文與英文的檔名、函式名與類別名，且 pythonpath 含 repo 根。"""
    節 = 取節(設定, "tool", "pytest", "ini_options")
    應含 = {
        "python_files": {"測_*.py", "test_*.py"},
        "python_functions": {"測試_*", "test_*"},
        "python_classes": {"測_*", "Test*"},
        "pythonpath": {"."},
    }
    for 鍵, 值集 in 應含.items():
        值 = 節.get(鍵)
        if not isinstance(值, list) or not 值集 <= set(值):
            return f"PYTEST_DISCOVERY_NOT_CONFIGURED:{鍵}"
    return 通過


def 檢查突變設定(設定: object) -> str:
    """確認 mutmut 的 tests_dir 與 also_copy 是 list 型別，且 also_copy 真的帶上測試樹。"""
    節 = 取節(設定, "tool", "mutmut")
    for 鍵 in ("source_paths", "tests_dir", "also_copy"):
        if not isinstance(節.get(鍵), list):
            return f"MUTMUT_CONFIG_NOT_LIST:{鍵}"
    複製清單 = 節.get("also_copy")
    if not isinstance(複製清單, list) or "驗收" not in 複製清單:
        return "MUTATION_TESTS_NOT_COPIED:also_copy"
    return 通過


def 建臨時專案(根: Path, 守衛原始碼: str, 額外設定: str = "") -> None:
    """在臨時目錄組出一份最小可跑專案，用來隔離執行事前固定的錯誤 subject。"""
    (根 / "nova" / "核心").mkdir(parents=True)
    (根 / "驗收" / "工具鏈").mkdir(parents=True)
    (根 / "nova" / "核心" / "工具鏈守衛.py").write_text(守衛原始碼, encoding="utf-8")
    shutil.copy(測試路徑, 根 / "驗收" / "工具鏈" / "測_工具鏈啟動.py")
    (根 / "pyproject.toml").write_text(臨時專案設定 + 額外設定, encoding="utf-8")


def 驗指定守衛突變() -> str:
    """負控一：把 `收窄` 換成直接回傳輸入，property test 必須直接紅；活下來就是探針失敗。"""
    突變原始碼 = (
        '"""事前固定的錯誤 subject：拿掉夾取，直接回傳輸入。"""\n\n\n'
        "def 收窄(值: int) -> int:\n"
        '    """直接回傳輸入。"""\n'
        "    return 值\n"
    )
    with tempfile.TemporaryDirectory() as 暫存:
        根 = Path(暫存)
        建臨時專案(根, 突變原始碼)
        完成 = subprocess.run(
            [sys.executable, "-m", "pytest", "-q", "驗收/工具鏈"],
            cwd=根,
            capture_output=True,
            text=True,
            check=False,
        )
    if 完成.returncode == 0:
        return "NAMED_MUTATION_SURVIVED:收窄"
    if "測試_守衛確實限制值" not in 完成.stdout + 完成.stderr:
        return "NAMED_MUTATION_KILLED_BY_WRONG_TEST"
    return 通過


def 驗拿掉also_copy() -> str:
    """負控二：mutmut 少了 also_copy 時測試沒被複製進 mutants 樹，必須是 typed 失敗而非成功。"""
    with tempfile.TemporaryDirectory() as 暫存:
        根 = Path(暫存)
        建臨時專案(根, 守衛路徑.read_text(encoding="utf-8"))
        工具目錄 = Path(sys.executable).parent
        環境 = dict(os.environ, PATH=f"{工具目錄}{os.pathsep}{os.environ['PATH']}")
        完成 = subprocess.run(
            [str(工具目錄 / "mutmut"), "run"],
            cwd=根,
            capture_output=True,
            text=True,
            check=False,
            env=環境,
        )
    if 完成.returncode == 0:
        return "MUTATION_MISSING_TESTS_TREATED_AS_SUCCESS"
    if "BadTestExecutionCommandsException" not in 完成.stdout + 完成.stderr:
        return f"MUTATION_FAILED_FOR_OTHER_REASON:{完成.returncode}"
    return 通過


def 跑基線() -> list[str]:
    """跑不需要子程序的四項設定與版本檢查，回傳所有 failure code。"""
    設定 = 讀專案設定()
    結果 = [檢查python版本(), 檢查鎖定版本(), 檢查探索設定(設定), 檢查突變設定(設定)]
    return [碼 for 碼 in 結果 if 碼 != 通過]


def 主(引數: list[str] | None = None) -> int:
    """組參數、依旗標跑對應檢查，把每個 failure code 印到 stderr 後以 0／1 回報。"""
    剖析器 = argparse.ArgumentParser(description="day-one 工具鏈探針")
    剖析器.add_argument("--驗指定守衛突變", action="store_true")
    剖析器.add_argument("--負控-拿掉-also-copy", dest="拿掉also_copy", action="store_true")
    參數 = 剖析器.parse_args(引數)

    失敗 = 跑基線()
    if 參數.驗指定守衛突變 and (碼 := 驗指定守衛突變()) != 通過:
        失敗.append(碼)
    if 參數.拿掉also_copy and (碼 := 驗拿掉also_copy()) != 通過:
        失敗.append(碼)

    for 碼 in 失敗:
        print(碼, file=sys.stderr)
    return 1 if 失敗 else 0


if __name__ == "__main__":
    raise SystemExit(主())
