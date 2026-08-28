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


def test_手改一字必須被拒() -> None:
    """消費三驗之一：重讀來源、重算摘要。"""
    單 = dict(一張工單())
    單["標題"] = str(單["標題"]) + "。"
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
    """`zsh -euo pipefail`：管線中段失敗不得被末段的成功蓋掉。"""
    出 = subprocess.run(
        ["zsh", "-euo", "pipefail", "-c", "false | cat"], check=False, capture_output=True
    )
    assert 出.returncode != 0, "沒有 pipefail 的話這行會回 0"
