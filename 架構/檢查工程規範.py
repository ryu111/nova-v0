"""repo 自身的靜態工程規範執法器。

規則全部住在 `架構/目錄規則.toml`；這支只負責機械執行：路徑恰命中一個 owner、
檔案落點與內容一致、出現在某份 active plan 的 `Create:`／`Modify:` 清單裡、
沒有超過規模上限、import 只往下走。

【實測，原 docs/陷阱.md 條目，已轉化為機制】舊 nova 的分層依賴掃描器只認
`ast.Import`／`ast.ImportFrom`。同一條違反分層的邊，寫成 `from 上層 import X`
立刻紅；改寫成 `importlib.import_module("上層.X")` 就**完全不被掃描器認得，全綠**。
代價是掃描器報全綠時違規邊仍然存在——比沒有掃描器更糟，因為讀的人會以為已經檢查過。

所以這支不只走 `ast.Import`／`ast.ImportFrom`：literal 的 `importlib.import_module`
與 `__import__` 解析成普通 dependency edge，非 literal 的 module target 一律回
`DYNAMIC_IMPORT_UNVERIFIABLE`——抓不到的動態 import 不是「沒有邊」。
負控見 `架構/test_工程規範.py::test_動態_import_的同一條違規邊也要被抓到`；
拿掉 `ast.Call` 那一支會讓它與另一個測試一起轉紅。
（正解仍然是把共用知識往下搬，不是把違規邊藏好。）
"""

from __future__ import annotations

import ast
import fnmatch
import io
import json
import re
import sys
import tokenize
import tomllib
import unicodedata
from dataclasses import dataclass
from pathlib import Path
from typing import Literal, cast

專案根 = Path(__file__).resolve().parent.parent
規則檔 = 專案根 / "架構" / "目錄規則.toml"
命名規則檔 = 專案根 / "架構" / "命名規則.toml"
fixture_目錄 = 專案根 / "驗收" / "工具鏈" / "fixtures"
計畫目錄 = 專案根 / "docs" / "計畫"
宣稱落點樣式 = re.compile(r"^#?\s*宣稱落點:\s*(\S+)\s*$", re.MULTILINE)
計畫條目樣式 = re.compile(r"^- (?:Create|Modify): `([^`]+)`", re.MULTILINE)

通過 = "OK"
nova_路徑最少段數 = 3
模組路徑最少段數 = 2


@dataclass(frozen=True, slots=True)
class 檢查結果:
    """一次檢查的 typed 結果；code 為 OK 以外的值時 細節 說明是哪一條打紅的。"""

    code: str
    路徑: str = ""
    細節: str = ""


正規化式 = Literal["NFC", "NFD", "NFKC", "NFKD"]


def 讀正規化式(值: list[str]) -> tuple[正規化式, ...]:
    """把 TOML 讀到的字串收成 unicodedata 認得的四種正規化式，別的直接炸。"""
    合法 = ("NFC", "NFD", "NFKC", "NFKD")
    if 壞 := [式 for 式 in 值 if 式 not in 合法]:
        raise ValueError(f"未知的正規化式：{壞}")
    return cast("tuple[正規化式, ...]", tuple(值))


@dataclass(frozen=True, slots=True)
class 規則集:
    """目錄規則.toml 的 in-memory 形狀，checker 的唯一規則來源。"""

    落點: tuple[tuple[str, str], ...]
    產生物目錄: frozenset[str]
    層序: dict[str, int]
    允許_IO: frozenset[str]
    規模上限: dict[str, int]
    IO_模組: frozenset[str]
    識別字正規化: tuple[正規化式, ...]
    閘們: tuple[tuple[str, tuple[str, ...]], ...]
    產物目錄: tuple[str, ...]
    允許_script: frozenset[str]
    段分隔: str


def 載入規則(路徑: Path = 規則檔) -> 規則集:
    """把目錄規則.toml 讀成 規則集；缺欄位就讓 KeyError 直接炸，不做預設值補洞。"""
    with 路徑.open("rb") as 檔:
        原始 = tomllib.load(檔)
    with 命名規則檔.open("rb") as 檔:
        命名 = tomllib.load(檔)
    層 = 原始["nova_layer"]
    return 規則集(
        落點=tuple((項["glob"], 項["owner"]) for 項 in 原始["placement"]),
        產生物目錄=frozenset(原始["generated_dirs"]["list"]),
        層序={項["name"]: 項["order"] for 項 in 層},
        允許_IO=frozenset(項["name"] for 項 in 層 if 項["allow_io"]),
        規模上限=原始["size_limits"],
        IO_模組=frozenset(原始["io_modules"]["list"]),
        識別字正規化=讀正規化式(命名["python_identifier"]["normalization"]),
        段分隔=命名["python_identifier"]["segment_separator"],
        允許_script=frozenset(命名["python_identifier"]["allowed_scripts"]),
        閘們=tuple((項["name"], tuple(項["argv"])) for 項 in 原始["gate"]),
        產物目錄=tuple(原始["generated_dirs"]["list"]),
    )


def 計畫已宣告的路徑() -> frozenset[str]:
    """列舉全部計畫檔的 Create:／Modify: 條目；直接列舉 .md 檔，不從別的型別推導。"""
    宣告: set[str] = set()
    for 檔 in sorted(計畫目錄.iterdir()):
        if 檔.is_file() and 檔.suffix == ".md":
            宣告 |= set(計畫條目樣式.findall(檔.read_text(encoding="utf-8")))
    return frozenset(宣告)


def 找落點(路徑: str, 規則: 規則集) -> 檢查結果:
    """路徑必須恰命中一條落點規則；零條是沒有 owner，兩條以上是有兩個變更原因。"""
    命中 = [owner for glob, owner in 規則.落點 if fnmatch.fnmatch(路徑, glob)]
    if not 命中:
        return 檢查結果("NO_PLACEMENT_OWNER", 路徑, "沒有任何落點規則命中")
    if len(命中) > 1:
        return 檢查結果("AMBIGUOUS_PLACEMENT", 路徑, f"命中 {len(命中)} 條：{命中}")
    return 檢查結果(通過, 路徑, 命中[0])


def 取_nova_層(路徑: str, 規則: 規則集) -> str | None:
    """回傳 nova/<層>/… 的層名；不是 nova 樹下、或層名未宣告時回 None。"""
    段 = 路徑.split("/")
    if len(段) < nova_路徑最少段數 or 段[0] != "nova":
        return None
    return 段[1] if 段[1] in 規則.層序 else None


def 收集匯入(樹: ast.Module) -> tuple[list[tuple[str, int]], list[檢查結果]]:
    """走一遍 AST 取出所有 module target 與立即可判的 import 違規。"""
    邊: list[tuple[str, int]] = []
    違規: list[檢查結果] = []
    頂層 = {id(節點) for 節點 in 樹.body}
    for 節點 in ast.walk(樹):
        if isinstance(節點, ast.Import):
            if id(節點) not in 頂層:
                違規.append(檢查結果("NON_TOPLEVEL_IMPORT", 細節=str(節點.lineno)))
            邊 += [(別名.name, 節點.lineno) for 別名 in 節點.names]
        elif isinstance(節點, ast.ImportFrom):
            if id(節點) not in 頂層:
                違規.append(檢查結果("NON_TOPLEVEL_IMPORT", 細節=str(節點.lineno)))
            if 節點.level:
                違規.append(檢查結果("RELATIVE_IMPORT", 細節=str(節點.lineno)))
            if any(別名.name == "*" for 別名 in 節點.names):
                違規.append(檢查結果("WILDCARD_IMPORT", 細節=str(節點.lineno)))
            邊.append((節點.module or "", 節點.lineno))
        elif isinstance(節點, ast.Call):
            動態 = 解析動態匯入(節點)
            if 動態 is not None:
                邊.append(動態) if 動態[0] else 違規.append(
                    檢查結果("DYNAMIC_IMPORT_UNVERIFIABLE", 細節=str(節點.lineno))
                )
    return 邊, 違規


def 解析動態匯入(節點: ast.Call) -> tuple[str, int] | None:
    """把 literal 的 import_module／__import__ 解析成普通 edge；非 literal 回空字串代表無法查核。"""
    名稱 = ""
    if isinstance(節點.func, ast.Attribute) and 節點.func.attr == "import_module":
        名稱 = "importlib.import_module"
    elif isinstance(節點.func, ast.Name) and 節點.func.id == "__import__":
        名稱 = "__import__"
    if not 名稱:
        return None
    第一引數 = 節點.args[0] if 節點.args else None
    if isinstance(第一引數, ast.Constant) and isinstance(第一引數.value, str):
        return (第一引數.value, 節點.lineno)
    return ("", 節點.lineno)


def 檢查內容落點(路徑: str, 邊: list[tuple[str, int]], 規則: 規則集) -> 檢查結果:
    """不允許 I/O 的層一旦 import 了 I/O 模組，就是落點與內容不一致。"""
    層 = 取_nova_層(路徑, 規則)
    if 層 is None or 層 in 規則.允許_IO:
        return 檢查結果(通過, 路徑)
    for 模組, 行 in 邊:
        if 模組.split(".")[0] in 規則.IO_模組:
            return 檢查結果("PLACEMENT_LAYER_MISMATCH", 路徑, f"{層} 層第 {行} 行 import {模組}")
    return 檢查結果(通過, 路徑)


def 檢查層序(路徑: str, 邊: list[tuple[str, int]], 規則: 規則集) -> 檢查結果:
    """上層可用下層，下層不得知道上層；啟動是 composition root，只出不進。"""
    層 = 取_nova_層(路徑, 規則)
    if 層 is None:
        return 檢查結果(通過, 路徑)
    我序 = 規則.層序[層]
    for 模組, 行 in 邊:
        段 = 模組.split(".")
        if len(段) < 模組路徑最少段數 or 段[0] != "nova" or 段[1] not in 規則.層序:
            continue
        if 段[1] == "啟動":
            return 檢查結果("LAYER_DEPENDENCY_VIOLATION", 路徑, f"第 {行} 行 import 啟動")
        if 層 != "啟動" and 規則.層序[段[1]] < 我序:
            return 檢查結果("LAYER_DEPENDENCY_VIOLATION", 路徑, f"第 {行} 行 {層}→{段[1]}")
    return 檢查結果(通過, 路徑)


帶_docstring_的節點 = ast.Module | ast.ClassDef | ast.FunctionDef | ast.AsyncFunctionDef


def 邏輯行數(節點: 帶_docstring_的節點, 行們: list[str]) -> int:
    """數不含空行、純註解行與 docstring 的行；這是規模上限唯一認可的量法。"""
    起 = 1 if isinstance(節點, ast.Module) else 節點.lineno
    迄 = (節點.end_lineno or 起) if not isinstance(節點, ast.Module) else len(行們)
    扣除 = 0
    if ast.get_docstring(節點, clean=False) is not None and 節點.body:
        首 = 節點.body[0]
        扣除 = (首.end_lineno or 首.lineno) - 首.lineno + 1
    有效 = [行 for 行 in 行們[起 - 1 : 迄] if 行.strip() and not 行.strip().startswith("#")]
    return len(有效) - 扣除


def 字的_script(字元: str) -> str:
    """把一個字元分成 ASCII_LATIN／HAN／NEUTRAL／OTHER。

    【實測】用碼點區間判 Han 會漏 CJK Ext B（`𠀀` U+20000）；改看
    `unicodedata.name()` 的 CJK 前綴，Ext B 與相容漢字自動涵蓋。
    數字與底線是 NEUTRAL，不參與 script 判定；兩軌以外的一律 OTHER，由呼叫端拒絕。
    """
    if 字元.isascii():
        return "ASCII_LATIN" if 字元.isalpha() else "NEUTRAL"
    try:
        名 = unicodedata.name(字元)
    except ValueError:
        return "OTHER"
    return "HAN" if 名.startswith(("CJK UNIFIED", "CJK COMPATIBILITY")) else "OTHER"


def 檢查識別字(路徑: str, 原始碼: str, 規則: 規則集) -> 檢查結果:
    """識別字必須 NFC，且每個 lexical segment 只能是單一 script。

    【實測】`ast.parse` 交出來的名字已被 NFKC 正規化——NFD 的 e+U+0301 變成 NFC 的 é、
    全形 a（U+FF41）變成 ASCII `a`。所以原始 source 的正規化狀態**看不到**，必須走 tokenize。

    判定單位是以 `_` 分隔的 segment 而非整個識別字。逐識別字判會把
    `test_工作決策`、`測試_守衛確實限制值` 這類計畫自己宣告的名字判紅，
    逼實作者放寬檢查——那正好毀掉這道閘。dunder 與前導底線因此自然不計 script。
    """
    try:
        名字們 = [
            記號.string
            for 記號 in tokenize.generate_tokens(io.StringIO(原始碼).readline)
            if 記號.type == tokenize.NAME
        ]
    except tokenize.TokenError, SyntaxError, IndentationError:
        return 檢查結果(通過, 路徑)
    for 名 in 名字們:
        for 式 in 規則.識別字正規化:
            if not unicodedata.is_normalized(式, 名):
                return 檢查結果("IDENTIFIER_NOT_NFC", 路徑, f"{名} 非 {式}")
        for 段 in 名.split(規則.段分隔):
            見到 = {字的_script(c) for c in 段} - {"NEUTRAL"}
            if 外 := 見到 - 規則.允許_script:
                return 檢查結果("SCRIPT_NOT_IN_TWO_TRACKS", 路徑, f"{名} 的 {段}：{sorted(外)}")
            if len(見到) > 1:
                return 檢查結果("MIXED_SCRIPT_IDENTIFIER", 路徑, f"{名} 的 {段}：{sorted(見到)}")
    return 檢查結果(通過, 路徑)


ASCII_NAME = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
SHELL_宣告 = (
    re.compile(r"^\s*(?P<n>[^\s=<>|&;]+)="),
    re.compile(r"^\s*(?:export|readonly|local|declare|typeset)\s+(?:-\w+\s+)*(?P<n>[^\s=]+)"),
    re.compile(r"^\s*for\s+(?P<n>\S+)\s+in\b"),
    re.compile(r"^\s*(?:function\s+)?(?P<n>[^\s()]+)\s*\(\s*\)"),
    re.compile(r"^\s*function\s+(?P<n>[^\s({]+)"),
    re.compile(r"^\s*alias\s+(?P<n>[^\s=]+)="),
    re.compile(r"^\s*(?:read|select|getopts)\s+(?:-\w+\s+|\"[^\"]*\"\s+)*(?P<n>[^\s=]+)"),
    re.compile(r"^\s*printf\s+-v\s+(?P<n>[^\s=]+)"),
    re.compile(r"^\s*let\s+(?P<n>[^\s=]+)="),
)
動態記號 = ("$", "`", '"', "'", "{")


def 判_shell_名(名: str) -> str:
    """一個不合格的 shell name 是三種毛病之一，回哪一種要分清楚。

    全 ASCII 但以數字開頭（`1abc`）既不是非 ASCII 也不是算出來的，回
    NON_ASCII_SHELL_NAME 會是假話——bash 拒絕它的理由是 name 規則不是字元集。
    """
    if any(記 in 名 for 記 in 動態記號):
        return "DYNAMIC_SHELL_NAME_UNVERIFIABLE"
    return "INVALID_SHELL_NAME" if 名.isascii() else "NON_ASCII_SHELL_NAME"


def 檢查_shell_名(路徑: str, 原始碼: str) -> 檢查結果:
    """Shell 的變數與函式名一律 ASCII；名字本身是算出來的一律拒絕。

    【實測 bash 3.2.57】`本次路徑=/tmp/x` 不是賦值而是命令名，script 仍然 **exit 0**——
    只看 exit code 的 CI 會放行，所以這裡靜態掃文字形式而不靠執行。
    `丁() { :; }` bash 給 rc=0：非 ASCII 函式名在 bash 合法，擋它的是我們的跨程序規矩。
    掃不到的動態宣告（`declare "$x=1"`、`eval "$n=1"`）回
    DYNAMIC_SHELL_NAME_UNVERIFIABLE，與動態 import 同一個理由：掃不到不等於沒有。
    """
    for 行 in 原始碼.splitlines():
        if not (淨 := 行.split("#", 1)[0].strip()):
            continue
        if 淨.startswith("eval "):
            return 檢查結果("DYNAMIC_SHELL_NAME_UNVERIFIABLE", 路徑, 淨)
        for 樣式 in SHELL_宣告:
            if (配對 := 樣式.match(淨)) is None:
                continue
            名 = 配對.group("n")
            if ASCII_NAME.match(名):
                break
            return 檢查結果(判_shell_名(名), 路徑, 名)
    return 檢查結果(通過, 路徑)


def 檢查_json_欄位(路徑: str, 原始碼: str) -> 檢查結果:
    """JSON 欄位名跨程序、跨版本被比對，一律 ASCII；值可以是中文。"""
    try:
        待: list[object] = [json.loads(原始碼)]
    except json.JSONDecodeError as 誤:
        return 檢查結果("MALFORMED_JSON", 路徑, str(誤))
    while 待:
        節 = 待.pop()
        if isinstance(節, dict):
            for 鍵, 值 in 節.items():
                if not 鍵.isascii():
                    return 檢查結果("NON_ASCII_JSON_FIELD", 路徑, 鍵)
                待.append(值)
        elif isinstance(節, list):
            待.extend(節)
    return 檢查結果(通過, 路徑)


TOML_鍵 = re.compile(r"^\s*(?:\[+\s*)?([^\s=\]\[#]+)\s*(?:=|\])", re.MULTILINE)


def 檢查_toml_鍵(路徑: str, 原始碼: str) -> 檢查結果:
    """TOML 的 bare key 只接受 ASCII——寫成中文不是風格問題，是**解析不了**。

    【實測 2026-08-27】同一個 session 踩三次：`架構/目錄規則.toml` 的 `[頂層]`、
    pyproject 的 `[dependency-groups] 開發`、突變批次的 `指令 =`，
    每次都是 `TOMLDecodeError: Invalid statement (at line 1, column 1)`——
    訊息不會告訴你是中文 key 的問題。這正是 CLAUDE.md 把 schema 欄位名列為
    ASCII 例外的理由；`識別字雙軌` 那條 claim 也早就承諾了，只是閘先前只查 .json。
    """
    for 配對 in TOML_鍵.finditer(原始碼):
        鍵 = 配對.group(1).strip().strip('"').strip("'")
        if not 鍵.isascii():
            return 檢查結果("NON_ASCII_TOML_KEY", 路徑, 鍵)
    return 檢查結果(通過, 路徑)


SQL_字串或註解 = re.compile(r"'(?:[^']|'')*'|--[^\n]*|/\*.*?\*/", re.DOTALL)


def 檢查_sql_識別字(路徑: str, 原始碼: str) -> 檢查結果:
    """DB table／column 一律 ASCII：先挖掉字串常量與註解，剩下還有非 ASCII 就是識別字。"""
    骨 = SQL_字串或註解.sub(" ", 原始碼)
    for 字元 in 骨:
        if not 字元.isascii():
            return 檢查結果("NON_ASCII_SQL_NAME", 路徑, 字元)
    return 檢查結果(通過, 路徑)


def 檢查規模(路徑: str, 樹: ast.Module, 原始碼: str, 規則: 規則集) -> 檢查結果:
    """模組 400、類別 250、函式 60 行 logical code；超過不是加 ignore，是拆責任。"""
    行們 = 原始碼.splitlines()
    if 邏輯行數(樹, 行們) > 規則.規模上限["module_logical_lines"]:
        return 檢查結果("MODULE_TOO_LARGE", 路徑, str(邏輯行數(樹, 行們)))
    for 節點 in ast.walk(樹):
        if isinstance(節點, ast.ClassDef):
            數 = 邏輯行數(節點, 行們)
            if 數 > 規則.規模上限["class_logical_lines"]:
                return 檢查結果("CLASS_TOO_LARGE", 路徑, f"{節點.name}={數}")
        elif isinstance(節點, ast.FunctionDef | ast.AsyncFunctionDef):
            數 = 邏輯行數(節點, 行們)
            if 數 > 規則.規模上限["function_logical_lines"]:
                return 檢查結果("FUNCTION_TOO_LARGE", 路徑, f"{節點.name}={數}")
    return 檢查結果(通過, 路徑)


非_python_掃描器 = (
    (".sh", 檢查_shell_名),
    (".json", 檢查_json_欄位),
    (".toml", 檢查_toml_鍵),
    (".sql", 檢查_sql_識別字),
)


def 檢查_python_內容(路徑: str, 原始碼: str, 規則: 規則集) -> 檢查結果:
    """.py 專屬：內容落點、層序、匯入可查核性、識別字與規模，回第一個失敗。"""
    樹 = ast.parse(原始碼)
    邊, 匯入違規 = 收集匯入(樹)
    for 組 in (檢查內容落點(路徑, 邊, 規則), 檢查層序(路徑, 邊, 規則)):
        if 組.code != 通過:
            return 組
    if 匯入違規:
        return 檢查結果(匯入違規[0].code, 路徑, 匯入違規[0].細節)
    if (命名 := 檢查識別字(路徑, 原始碼, 規則)).code != 通過:
        return 命名
    return 檢查規模(路徑, 樹, 原始碼, 規則)


def 檢查檔案(路徑: str, 原始碼: str, 規則: 規則集, *, 查計畫目錄: bool = True) -> 檢查結果:
    """對單一檔案依序跑落點、內容、跨程序命名與計畫目錄四組檢查，回第一個失敗。"""
    if (落點 := 找落點(路徑, 規則)).code != 通過:
        return 落點
    if 路徑.endswith(".py") and (內容 := 檢查_python_內容(路徑, 原始碼, 規則)).code != 通過:
        return 內容
    for 副檔名, 掃描器 in 非_python_掃描器:
        if 路徑.endswith(副檔名) and (名 := 掃描器(路徑, 原始碼)).code != 通過:
            return 名
    if 查計畫目錄 and 路徑 not in 計畫已宣告的路徑():
        return 檢查結果("UNPLANNED_FILE", 路徑, "未出現在任何計畫的 Create:／Modify: 清單")
    return 檢查結果(通過, 路徑)


def check_fixture(名稱: str, 規則: 規則集 | None = None) -> 檢查結果:
    """把 fixture 依它自己宣告的「宣稱落點」當成那個位置來檢查；fixture 不查計畫目錄。"""
    原始碼 = (fixture_目錄 / 名稱).read_text(encoding="utf-8")
    配對 = 宣稱落點樣式.search(原始碼)
    if 配對 is None:
        return 檢查結果("FIXTURE_MISSING_CLAIMED_PATH", 名稱)
    return 檢查檔案(配對.group(1), 原始碼, 規則 or 載入規則(), 查計畫目錄=False)


def 掃描倉庫(規則: 規則集 | None = None) -> list[檢查結果]:
    """列舉六頂層底下的全部檔案逐一檢查；直接列舉目錄，不從別的型別推導。"""
    用規則 = 規則 or 載入規則()
    頂層們 = sorted({glob.split("/")[0] for glob, _ in 用規則.落點})
    失敗: list[檢查結果] = []
    for 頂層 in 頂層們:
        根 = 專案根 / 頂層
        if not 根.is_dir():
            continue
        for 檔 in sorted(根.rglob("*")):
            if not 檔.is_file() or fixture_目錄 in 檔.parents:
                continue
            if {段.name for 段 in 檔.parents} & 用規則.產生物目錄:
                continue
            相對 = 檔.relative_to(專案根).as_posix()
            結果 = 檢查檔案(相對, 檔.read_text(encoding="utf-8"), 用規則)
            if 結果.code != 通過:
                失敗.append(結果)
    return 失敗


def 主() -> int:
    """掃描整個 repo，把每個違規印到 stderr 後以 0／1 回報。"""
    失敗 = 掃描倉庫()
    for 結果 in 失敗:
        print(f"{結果.code}\t{結果.路徑}\t{結果.細節}", file=sys.stderr)
    return 1 if 失敗 else 0


if __name__ == "__main__":
    raise SystemExit(主())


def 讀_CI_步驟() -> list[tuple[str, str]]:
    """把 gates.yml 的 steps 讀成 `(name, run)` 序列。

    **不能用一般的 YAML 載入器。** YAML 遇到重複鍵時**靜默取最後一個**，
    而那正是 2026-08-28 實際發生的事：我把 `board` 塞成 `selftest` step 的
    第二個 `run:`，解析後 `計畫複驗.py --自測` **在 CI 裡根本沒跑**，
    而當時的測試只做字串比對，`--自測` 那串字仍在檔案裡，所以**照樣綠**。
    所以這裡逐行掃，**每個 step 的 `run:` 出現兩次就是錯**。
    """
    步驟: list[tuple[str, str]] = []
    名 = None
    次數 = 0
    for 行 in (
        (專案根 / ".github" / "workflows" / "gates.yml").read_text(encoding="utf-8").splitlines()
    ):
        m = re.match(r"\s*- name:\s*(\S+)\s*$", 行)
        if m:
            if 名 is not None and 次數 != 1:
                raise AssertionError(f"CI step {名} 有 {次數} 個 run:（應恰好 1）")
            名, 次數 = m.group(1), 0
            continue
        r = re.match(r"\s*run:\s*(.+?)\s*$", 行)
        if r and 名 is not None:
            次數 += 1
            步驟.append((名, r.group(1)))
    if 名 is not None and 次數 != 1:
        raise AssertionError(f"CI step {名} 有 {次數} 個 run:（應恰好 1）")
    return 步驟
