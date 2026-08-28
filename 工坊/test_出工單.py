"""出工單與驗工入口的固定負控（計畫 01C Task 2）。

**這些格對的是實測踩過的三個坑**，不是想像的壞況：

1. **工單手抄腐化**——claim instance 三處與實檔不符、散文裡的過期份數，
   都是「人抄了計畫內容」這一類。機械生成加上 digest 綁定消滅它。
2. **只印不驗等於沒驗**——把 `base_commit_sha` 放進工單而不在消費時比對，
   舊工單照樣能打新樹。
3. **驗收報告假綠**——`grep …; echo 全綠` 無條件執行、agy 零產出回
   `"status":"SUCCESS"`。驗工入口只收 exit code 不夠，必須逐條記並全綠才 green。
"""

from __future__ import annotations

import json
import subprocess
from typing import Any

import pytest

from 工坊 import 出工單, 驗工


def 一張工單() -> dict[str, Any]:
    return 出工單.生成("01C", 1, 基準="deadbeef")


def test_工單帶來源區段的位元組摘要() -> None:
    """工單不是「照抄一段文字」，是**綁住那段文字的位元組**。"""
    單 = 一張工單()
    assert 單["來源摘要"], "工單沒有來源區段摘要，等於沒綁"
    assert 單["schema_revision"] == 出工單.SCHEMA_REVISION


def test_工單自身欄位被改必須被拒() -> None:
    """**整單摘要**：`grant` 與 `files_scope` 是殼的授權輸入，不能事後塞。

    第一版只有 `來源摘要`（綁計畫的 task 區段），實測生成後塞
    `grant=["command"]`、把 `files_scope` 放大成 `["nova/**"]`，**消費照樣接受**
    ——「工單封閉」對最要緊的那一欄不成立。fable 覆蓋審 M4 抓到。
    """
    for 欄, 值 in (("grant", ["command"]), ("files_scope", ["nova/**"]), ("標題", "改過")):
        單 = dict(一張工單())
        單[欄] = 值
        with pytest.raises(出工單.工單不可用) as e:
            出工單.消費(單, 工作樹基準="deadbeef")
        assert str(e.value).startswith("work_order_tampered"), f"{欄} 被改卻沒被擋"


def test_來源區段被改必須被拒() -> None:
    """另一半：**整單摘要對得上、但計畫的來源區段變了**。

    這種情況整單摘要驗不出來（工單自己沒被動），要靠重讀來源重算。
    兩個摘要各驗各的，缺一邊就有一整類改動溜過去。
    """
    單 = dict(一張工單())
    單["來源摘要"] = "0" * 64
    單["整單摘要"] = 出工單._整單摘要(單)
    with pytest.raises(出工單.工單不可用) as e:
        出工單.消費(單, 工作樹基準="deadbeef")
    assert str(e.value).startswith("work_order_digest_mismatch")


def test_舊工單打新樹必須被拒() -> None:
    """消費三驗之二：**只印不驗等於沒驗**。"""
    with pytest.raises(出工單.工單不可用) as e:
        出工單.消費(一張工單(), 工作樹基準="cafe1234")
    assert str(e.value).startswith("stale_base_commit")


def test_未知綱要版本必須被拒() -> None:
    """消費三驗之三。"""
    單 = dict(一張工單())
    單["schema_revision"] = 999
    with pytest.raises(出工單.工單不可用) as e:
        出工單.消費(單, 工作樹基準="deadbeef")
    assert str(e.value).startswith("unknown_schema_revision")


def test_同批次內範圍重疊的第二張必須被拒() -> None:
    """`files_scope` 重疊**只約束同一 batch**——跨 batch 明講不防。"""
    甲 = dict(一張工單(), files_scope=["工坊/出工單.py"])
    乙 = dict(一張工單(), files_scope=["工坊/出工單.py", "工坊/驗工.py"])
    with pytest.raises(出工單.工單不可用) as e:
        出工單.檢查批次([甲, 乙])
    assert str(e.value).startswith("files_scope_overlap_in_batch")


def test_不重疊的批次照發_防恆真() -> None:
    甲 = dict(一張工單(), files_scope=["工坊/出工單.py"])
    乙 = dict(一張工單(), files_scope=["工坊/驗工.py"])
    出工單.檢查批次([甲, 乙])


def test_合法工單照常消費_防恆真() -> None:
    """三驗都過時必須回工單本身，不能永遠拒。"""
    assert 出工單.消費(一張工單(), 工作樹基準="deadbeef")["計畫"] == "01C"


def test_零個或多義的驗收命令必須_fail_closed() -> None:
    """驗工入口**不自行猜**哪一條是最終 PASS 命令。"""
    with pytest.raises(驗工.無法驗收) as e:
        驗工.跑([])
    assert str(e.value).startswith("ambiguous_acceptance_command")


def test_逐條記錄且全綠才輸出_green() -> None:
    報告 = 驗工.跑(["true"])
    assert 報告["green"] is True
    assert 報告["逐條"][0]["exit"] == 0


def test_未執行的那條不得被當成通過() -> None:
    """`green` 必須是「**每一條都 exit 0**」，不是「最後一條 exit 0」。

    這格繞了一圈才寫對。第一版 fixture 是 `["true", "false", "true"]`：
    fail-fast 讓最後一條記成未執行（`exit` 為 `None`），於是把實作改成
    「只看最後一條」時**這格照樣過**——它是恆真的。第二版加 `["false"]`
    也一樣，單條時最後一條就是那條。

    **fail-fast 之下不可能造出「中段失敗而末條成功」的排列**，所以真正能區分
    兩種實作的形狀不是排列，是**未執行那條的處置**：`None` 不是 0，
    任何把它當成通過的寫法都必須紅。
    """
    報告 = 驗工.跑(["true", "false", "true"])
    assert 報告["green"] is False
    逐條 = 報告["逐條"]
    assert [格["exit"] for 格 in 逐條] == [0, 1, None], "未執行的那條要明列成 None"
    assert 逐條[-1]["exit"] is None, "末條未執行"
    assert not all(格["exit"] == 0 for 格 in 逐條), "未執行不算通過"


def test_後端自報成功而零產出時不得_green() -> None:
    """**agy 實案機械化**：它在權限被拒、零產出時回 `"status":"SUCCESS"`。

    只看後端自報就會把那次派工當成功——驗工入口必須看**宣告的驗收命令**，
    而不是後端說了什麼。
    """
    自報 = json.dumps({"status": "SUCCESS", "response": ""})
    assert 驗工.後端自報可信(自報) is False


def test_嚴格模式真的生效() -> None:
    """管線中段失敗不得被末段的成功蓋掉——**且不假設這台機器有 zsh**。

    第一版寫死 `zsh`，本機（macOS）全綠而 CI 的 Linux runner 沒有 zsh，
    `FileNotFoundError: 'zsh'` 讓整道閘掛。這格改成用 `驗工.嚴格旗標()`
    探測到的那組旗標，並在**沒有 pipefail 的機器上明講這個上限**。
    """
    旗標 = 驗工.嚴格旗標()
    出 = subprocess.run(["sh", *旗標, "-c", "false | cat"], check=False, capture_output=True)
    if "pipefail" in 旗標:
        assert 出.returncode != 0, "有 pipefail 卻沒擋住管線中段失敗"
    else:
        assert 出.returncode == 0, "沒有 pipefail 時管線末段成功就是 0——這是已知上限"
