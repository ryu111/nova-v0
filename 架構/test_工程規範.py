"""工程規範 checker 的近身測試：每條規則都要有一個事前固定的錯誤 subject 把它打紅。"""

import contextlib
import functools
import json
import pathlib
import re
import subprocess
import tomllib
from dataclasses import replace

import pytest

from 工具.裝_git_鉤子 import 乾淨環境
from 工具.裝_git_鉤子 import 安裝 as 安裝鉤子
from 工具.跑指定突變 import 跑批次
from 工具.驗全部 import 跑, 閘清單
from 架構.檢查工程規範 import (
    check_fixture,
    命名規則檔,
    宣稱落點樣式,
    專案根,
    掃描倉庫,
    檢查檔案,
    讀正規化式,
    載入規則,
)

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
    "INVALID_SHELL_NAME": "shell_names_are_valid_bash_names",
    "NON_ASCII_JSON_FIELD": "json_field_names_are_ascii",
    "NON_ASCII_TOML_KEY": "toml_keys_are_ascii",
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


def test_段規則管到最後一段() -> None:
    # 只驗第一段的實作會讓 `x_claim狀態` 整個溜過去——閘只擋得住單段名字。
    結果 = 檢查檔案("nova/核心/x.py", "x_claim狀態 = 1\n", 載入規則(), 查計畫目錄=False)
    assert 結果.code == "MIXED_SCRIPT_IDENTIFIER"


def test_識別字帶數字不被誤殺() -> None:
    # 數字是 NEUTRAL：不扣掉它，`值1` 會被當成兩個 script 而誤殺。
    結果 = 檢查檔案("nova/核心/x.py", "值1 = 1\n", 載入規則(), 查計畫目錄=False)
    assert 結果.code == "OK"


def test_相容漢字也算_Han() -> None:
    # U+FA0E 是少數 NFC／NFKC 都穩定的 CJK COMPATIBILITY IDEOGRAPH，
    # 只認 "CJK UNIFIED" 前綴會把它踢出兩軌，純漢字識別字被誤殺。
    結果 = 檢查檔案("nova/核心/x.py", "\u5de5\ufa0e = 1\n", 載入規則(), 查計畫目錄=False)
    assert 結果.code == "OK"


def test_兩種毛病並存時回哪個_code_要釘住() -> None:
    # 混軌與「兩軌之外」可以同時成立。誰先回若沒被釘住，
    # 將來 must_fail_exactly 會無聲對錯。約定：兩軌之外優先。
    結果 = 檢查檔案("nova/核心/x.py", "x\u043f\u0440\u0438 = 1\n", 載入規則(), 查計畫目錄=False)
    assert 結果.code == "SCRIPT_NOT_IN_TWO_TRACKS"


def test_每種_shell_宣告形式都掃得到() -> None:
    規則 = 載入規則()
    形式 = (
        "本次路徑=/tmp/x\n",
        "export 本次路徑=/tmp/x\n",
        "readonly 本次路徑=/tmp/x\n",
        "local 本次路徑=/tmp/x\n",
        "declare -r 本次路徑=/tmp/x\n",
        "for 本次路徑 in a b; do :; done\n",
        "本次路徑() { :; }\n",
        "function 本次路徑 { :; }\n",
        'alias 本次路徑="echo ok"\n',
        "read 本次路徑\n",
        "select 本次路徑 in a b; do :; done\n",
        'getopts "x" 本次路徑\n',
        'printf -v 本次路徑 "%s" t\n',
        "let 本次路徑=1+1\n",
        "typeset 本次路徑=/tmp/x\n",
    )
    for 原始碼 in 形式:
        assert (
            檢查檔案("工具/x.sh", 原始碼, 規則, 查計畫目錄=False).code == "NON_ASCII_SHELL_NAME"
        ), 原始碼
    # 註解不剝乾淨的話，`#本次路徑=x` 會被當成一條賦值——誤殺。
    註解 = "#本次路徑=/tmp/x\n# 本次路徑=/tmp/x 只是說明\ntarget_dir=/tmp/x\n"
    assert 檢查檔案("工具/x.sh", 註解, 規則, 查計畫目錄=False).code == "OK"
    # 全 ASCII 但 bash 不接受的 name，回「非 ASCII」會是假話。
    數字開頭 = 檢查檔案("工具/x.sh", "1abc=/tmp/x\n", 規則, 查計畫目錄=False)
    assert 數字開頭.code == "INVALID_SHELL_NAME"


def test_五種算出來的名字都不當成沒有名字() -> None:
    規則 = 載入規則()
    for 原始碼 in (
        'declare "$前綴_值=1"\n',
        'eval "$n=1"\n',
        "export `printf x`=1\n",
        "readonly '$q'=1\n",
        "declare ${前綴}_值=1\n",
        "declare $x=1\n",
    ):
        碼 = 檢查檔案("工具/x.sh", 原始碼, 規則, 查計畫目錄=False).code
        assert 碼 == "DYNAMIC_SHELL_NAME_UNVERIFIABLE", 原始碼


def test_巢狀與陣列裡的_json_欄位也要查() -> None:
    規則 = 載入規則()
    for 原始碼 in ('{"a": {"欄位": 1}}', '{"a": [{"欄位": 1}]}'):
        assert 檢查檔案("規格/x.claim.json", 原始碼, 規則, 查計畫目錄=False).code == (
            "NON_ASCII_JSON_FIELD"
        ), 原始碼


def test_壞掉的_json_不當成通過() -> None:
    結果 = 檢查檔案("規格/x.claim.json", "{不是 json", 載入規則(), 查計畫目錄=False)
    assert 結果.code == "MALFORMED_JSON"


def test_sql_跨行註解與字串裡的中文不算識別字() -> None:
    規則 = 載入規則()
    綠 = "/* 建表\n   工作 */\nCREATE TABLE work (note TEXT DEFAULT '中文');\n"
    assert 檢查檔案("nova/狀態/x.sql", 綠, 規則, 查計畫目錄=False).code == "OK"
    紅 = "/* 說明 */\nCREATE TABLE 工作 (id TEXT);\n"
    assert 檢查檔案("nova/狀態/x.sql", 紅, 規則, 查計畫目錄=False).code == "NON_ASCII_SQL_NAME"


def test_沒宣告落點的_fixture_不算負控() -> None:
    # fixture 少了「宣稱落點:」就沒有被檢查的位置，必須明講而不是靜靜通過。
    assert check_fixture("錯誤工具設定.toml").code == "FIXTURE_MISSING_CLAIMED_PATH"


def test_未知的正規化式直接炸() -> None:
    with pytest.raises(ValueError, match="未知的正規化式"):
        讀正規化式(["NFC", "NFX"])


def test_claim_的_faulty_subject_必須指向自己宣告的落點() -> None:
    # claim.json 的 claimed_path 與 fixture 檔內的「宣稱落點:」是兩份拷貝；
    # 沒有人比對，兩邊可以無聲漂移，負控就不再驗證規格宣告的那個位置。
    for claim_路徑 in 宣告過的_claim:
        宣告 = json.loads(pathlib.Path(claim_路徑).read_text(encoding="utf-8"))
        for 負控 in 宣告["controls"]["negative"]:
            原始碼 = pathlib.Path(負控["faulty_subject"]).read_text(encoding="utf-8")
            配對 = 宣稱落點樣式.search(原始碼)
            assert 配對 is not None, 負控["faulty_subject"]
            assert 配對.group(1) == 負控["claimed_path"], 負控["control_id"]


def test_命名規則宣告的每個_failure_code_都有人執行() -> None:
    # [failure_code] 那張表若沒人讀，它就只是第二份拷貝——宣告了卻沒人執行。
    with 命名規則檔.open("rb") as 檔:
        宣告的 = set(tomllib.load(檔)["failure_code"].values())
    assert 宣告的 <= set(碼對照判準), 宣告的 - set(碼對照判準)


def 造臨時倉(根: pathlib.Path, 入口回傳: int) -> pathlib.Path:
    """造一個最小 git repo，裡面放一個回傳指定 exit code 的假入口。"""
    subprocess.run(["git", "init", "-q"], cwd=根, check=True, env=乾淨環境())
    subprocess.run(["git", "config", "user.email", "t@t"], cwd=根, check=True, env=乾淨環境())
    subprocess.run(["git", "config", "user.name", "t"], cwd=根, check=True, env=乾淨環境())
    假入口 = 根 / "假入口.py"
    假入口.write_text(f"import sys\n\nsys.exit({入口回傳})\n", encoding="utf-8")
    (根 / "檔.txt").write_text("x\n", encoding="utf-8")
    安裝鉤子(根, 假入口)
    subprocess.run(["git", "add", "-A"], cwd=根, check=True, env=乾淨環境())
    return 根


def test_入口跑完每一道閘且任一紅就非零(capsys: pytest.CaptureFixture[str]) -> None:
    # 「跑到第一個紅就停」會讓後面的閘從此沒人跑過；而只回報不回非零等於沒有閘。
    碼 = 跑((("先", ("true",)), ("壞", ("false",)), ("後", ("true",))))
    印出 = capsys.readouterr().out
    assert 碼 != 0
    for 名 in ("先", "壞", "後"):
        assert 名 in 印出


def test_入口全綠回零(capsys: pytest.CaptureFixture[str]) -> None:
    # 防恆真：一個永遠回非零的入口也能讓上一格通過。
    assert 跑((("甲", ("true",)), ("乙", ("true",)))) == 0


def test_宣告的閘不是空的() -> None:
    名們 = {名 for 名, _ in 閘清單()}
    assert {"format", "lint", "types", "placement", "plans", "tests"} <= 名們


def test_CI_跑的是同一組閘() -> None:
    # 【實測 2026-08-27】檔名一定要 ASCII：叫 驗收.yml 時 GitHub 會註冊成功、
    # 顯示 active、workflow_dispatch 也跑得起來，但 push／pull_request **一次都不觸發**。
    # UI 上完全看不出異常。改成 gates.yml 之後 push 立刻觸發。
    文 = (專案根 / ".github" / "workflows" / "gates.yml").read_text(encoding="utf-8")
    for 名, argv in 載入規則().閘們:
        assert " ".join(argv) in 文, 名


def test_git_鉤子把非零_exit_傳出去(tmp_path: pathlib.Path) -> None:
    # 鉤子裝了卻不把紅傳出去，等於裝了一個永遠說好的門禁。
    倉 = 造臨時倉(tmp_path, 入口回傳=1)
    結果 = subprocess.run(
        ["git", "commit", "-m", "壞的"], cwd=倉, capture_output=True, env=乾淨環境()
    )
    assert 結果.returncode != 0


def test_閘全綠時鉤子不擋正常_commit(tmp_path: pathlib.Path) -> None:
    # 防恆真：一個永遠擋下來的鉤子也能讓上一格通過。
    倉 = 造臨時倉(tmp_path, 入口回傳=0)
    結果 = subprocess.run(
        ["git", "commit", "-m", "好的"], cwd=倉, capture_output=True, env=乾淨環境()
    )
    assert 結果.returncode == 0, 結果.stderr.decode()


def test_臨時倉不得被繼承的_GIT_環境變數帶去污染真倉(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """負控：git 鉤子會設 `GIT_DIR`／`GIT_INDEX_FILE`，那時 cwd 完全不算數。

    **這一格是實測踩出來的，不是想像。** 2026-08-28 agy 在 worktree 裡跑 `git commit`，
    pre-commit 鉤子啟動、跑七道閘、跑到本檔的鉤子測試——`造臨時倉` 的 `git init`／
    `git config`／`git add -A` 與測試的 `git commit` 全部繼承了鉤子環境裡的 `GIT_DIR`，
    於是打到真 repo：`user.email=t@t` 寫進 `.git/config`、pre-commit 被換成指向
    pytest 暫存目錄的假入口、`實作/01-T11` 上多了一個訊息「好的」、內容是刪光整個
    repo 只留兩個檔的 commit。**驗鉤子的測試，透過鉤子跑的時候把 repo 弄壞了。**

    誘餌倉扮演「真 repo」。`造臨時倉` 若不隔離環境，誘餌會拿到 commit、
    `user.email`、以及被覆寫的 hook。
    """
    誘餌 = tmp_path / "誘餌"
    工作 = tmp_path / "工作"
    誘餌.mkdir()
    工作.mkdir()
    subprocess.run(["git", "init", "-q"], cwd=誘餌, check=True, env=乾淨環境())

    monkeypatch.setenv("GIT_DIR", str(誘餌 / ".git"))
    monkeypatch.setenv("GIT_INDEX_FILE", str(誘餌 / ".git" / "index"))

    造臨時倉(工作, 入口回傳=0)

    誘餌設定 = (誘餌 / ".git" / "config").read_text(encoding="utf-8")
    assert "t@t" not in 誘餌設定, "誘餌倉的 config 被污染了"
    assert not (誘餌 / ".git" / "hooks" / "pre-commit").exists(), "誘餌倉的 hook 被覆寫了"
    誘餌_HEAD = subprocess.run(
        ["git", "rev-parse", "--verify", "HEAD"],
        cwd=誘餌,
        capture_output=True,
        env=乾淨環境(),
    )
    assert 誘餌_HEAD.returncode != 0, "誘餌倉被寫進了 commit"


def test_臨時倉不得把共用設定翻成_bare(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """負控：`GIT_DIR` **指向連結工作樹的 git dir** 加 `git init` 會翻掉共用 config 的 bare。

    **「連結工作樹」那半不能省。** nova-ea 的對照實驗（各三跑）夾出的是一個合取：

    | 條件 | `core.bare` |
    |---|---|
    | `GIT_DIR` = **worktree** git dir 加 `git init` | **true** |
    | `GIT_DIR` = 主 `.git` 加 `git init` | false |
    | cwd 在工作樹、不設 env 加 `git init` | false |
    | `GIT_DIR` = worktree 加 只跑 `git config` | false（身分照樣被污染） |

    所以誘餌**必須有連結工作樹**、`GIT_DIR` 必須指向那個工作樹的 git dir。
    用普通 repo 加 `GIT_DIR=誘餌/.git` 寫這一格，assert 會永遠綠——
    看起來守住了 bare，實際上守不住，而且沒有任何格會告訴你。
    （2026-08-28 我第一版就是那樣寫的，被 nova-ea 指出來。）

    真實鏈路：agy 在 `實作/01-T11` 這個**連結工作樹**裡 commit，
    鉤子把 `GIT_DIR` 設成 `.git/worktrees/T11`，`造臨時倉` 的 `git init -q` 繼承它，
    於是主 repo 的 `core.bare` 被翻成 true、`git status` 從此回
    `fatal: this operation must be run in a work tree`。
    """
    誘餌 = tmp_path / "誘餌"
    工作 = tmp_path / "工作"
    誘餌.mkdir()
    工作.mkdir()
    跑 = functools.partial(subprocess.run, check=True, env=乾淨環境())
    跑(["git", "init", "-q"], cwd=誘餌)
    (誘餌 / "種.txt").write_text("x\n", encoding="utf-8")
    跑(["git", "add", "-A"], cwd=誘餌)
    跑(["git", "-c", "user.email=種@種", "-c", "user.name=種", "commit", "-qm", "種"], cwd=誘餌)
    跑(["git", "worktree", "add", "-q", str(tmp_path / "連結"), "-b", "連結分支"], cwd=誘餌)

    工作樹_git_目錄 = 誘餌 / ".git" / "worktrees" / "連結"
    assert 工作樹_git_目錄.is_dir(), "連結工作樹沒建起來，這一格會退化成恆真"
    monkeypatch.setenv("GIT_DIR", str(工作樹_git_目錄))

    # 隔離失效時 `git init` 先翻掉 bare，後面的 `git config` 才炸成 exit 128。
    # 不吞掉那個例外的話，這一格會紅在 CalledProcessError 而不是紅在下面那句斷言
    # ——「紅在別的地方」等於這一格沒驗到它宣稱要驗的東西。
    with contextlib.suppress(subprocess.CalledProcessError):
        造臨時倉(工作, 入口回傳=0)

    共用設定 = (誘餌 / ".git" / "config").read_text(encoding="utf-8")
    assert "bare = true" not in 共用設定, "共用 config 被翻成 bare"


def 造批次(
    根: pathlib.Path, 目標: pathlib.Path, 期望: str, 舊: str, 新: str, 檢查字: str | None = None
) -> pathlib.Path:
    """寫一份最小的突變批次宣告。指令檢查的字串與被突變的字串是**兩件事**——

    兩者相同時突變必然被殺，那樣的測試證明不了工具會不會分辨宣告與實際。
    """
    批 = 根 / "批.toml"
    檢查器 = 根 / "檢查器.py"
    找 = 檢查字 or 舊
    檢查器.write_text(
        "import pathlib, sys\n"
        f"文 = pathlib.Path({str(目標)!r}).read_text(encoding='utf-8')\n"
        f"sys.exit(0 if {找!r} in 文 else 1)\n",
        encoding="utf-8",
    )
    指令 = ["python3", str(檢查器)]
    批.write_text(
        f"command = {json.dumps(指令, ensure_ascii=False)}\n\n"
        f'[[mutation]]\nname = "試"\nfile = {json.dumps(str(目標), ensure_ascii=False)}\n'
        f"old = {json.dumps(舊, ensure_ascii=False)}\nnew = {json.dumps(新, ensure_ascii=False)}\n"
        f"expect = {json.dumps(期望, ensure_ascii=False)}\n",
        encoding="utf-8",
    )
    return 批


def test_突變宣告殺掉卻存活要回非零(tmp_path: pathlib.Path) -> None:
    # 換掉的字串不影響指令 → 指令仍綠 → 該突變存活；宣告說殺掉，所以必須回非零。
    目標 = tmp_path / "標.txt"
    目標.write_text("關鍵字 與 無關字\n", encoding="utf-8")
    批 = 造批次(tmp_path, 目標, "殺掉", 舊="無關字", 新="別的字", 檢查字="關鍵字")
    assert 跑批次(批) != 0


def test_突變宣告存活卻被殺也要回非零(tmp_path: pathlib.Path) -> None:
    目標 = tmp_path / "標.txt"
    目標.write_text("關鍵字\n", encoding="utf-8")
    assert 跑批次(造批次(tmp_path, 目標, "存活", "關鍵字", "改掉了")) != 0


def test_突變相符時回零而且還原原檔(tmp_path: pathlib.Path) -> None:
    # 防恆真：一個永遠回非零的工具也能讓上面兩格通過。
    目標 = tmp_path / "標.txt"
    原文 = "關鍵字\n"
    目標.write_text(原文, encoding="utf-8")
    assert 跑批次(造批次(tmp_path, 目標, "殺掉", "關鍵字", "改掉了")) == 0
    assert 目標.read_text(encoding="utf-8") == 原文


def test_突變目標字串不存在要明講(tmp_path: pathlib.Path) -> None:
    # 「找不到就跳過」會讓一條負控從此靜默消失，而且報告上還是綠的。
    目標 = tmp_path / "標.txt"
    目標.write_text("關鍵字\n", encoding="utf-8")
    assert 跑批次(造批次(tmp_path, 目標, "殺掉", "根本沒有這段", "x")) != 0


def test_中文_toml_鍵要被擋() -> None:
    # 同一個 session 踩三次：[頂層]、dependency-groups 的 開發、突變批次的 指令。
    # TOMLDecodeError 只會說 "Invalid statement"，不會告訴你是中文 key。
    規則 = 載入規則()
    for 原始碼 in ("指令 = [1]\n", "[頂層]\nx = 1\n", '[a]\n開發 = ["b"]\n'):
        結果 = 檢查檔案("架構/x.toml", 原始碼, 規則, 查計畫目錄=False)
        assert 結果.code == "NON_ASCII_TOML_KEY", 原始碼
    綠 = '# 中文註解沒問題\nname = "中文值也沒問題"\n[[gate]]\nargv = ["架構/檢查工程規範.py"]\n'
    assert 檢查檔案("架構/x.toml", 綠, 規則, 查計畫目錄=False).code == "OK"


def test_gitignore_涵蓋宣告的產物目錄() -> None:
    # generated_dirs 宣告在 目錄規則.toml，.gitignore 是第二份拷貝——
    # 兩處各留一份，遲早有一處漏掉而把工具產物推上去。
    忽略 = (專案根 / ".gitignore").read_text(encoding="utf-8")
    行們 = {
        行.strip().rstrip("/") for 行 in 忽略.splitlines() if 行.strip() and not 行.startswith("#")
    }
    for 目錄 in 載入規則().產物目錄:
        assert 目錄.rstrip("/") in 行們, 目錄


@pytest.mark.parametrize(
    "路徑",
    [".env", ".env.local", "私鑰.pem", "id_rsa", "秘密.json", "credentials.json", ".DS_Store"],
)
def test_不該上傳的樣式真的被忽略(路徑: str) -> None:
    # 用 git 自己回答，不是自己解析 .gitignore——解析錯了會給假的安心。
    結果 = subprocess.run(["git", "check-ignore", "-q", 路徑], cwd=專案根, check=False)
    assert 結果.returncode == 0, f"{路徑} 沒有被忽略"


def test_版控裡沒有憑證樣式的檔() -> None:
    出 = subprocess.run(["git", "ls-files"], cwd=專案根, capture_output=True, text=True, check=True)
    壞 = [
        f
        for f in 出.stdout.splitlines()
        if re.search(r"(^|/)(\.env|.*\.pem|.*\.key|id_rsa|秘密.*\.json|credentials.*\.json)$", f)
    ]
    assert not 壞, 壞
