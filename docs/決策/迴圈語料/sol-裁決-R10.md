codex
我會重跑合套閘，並特別區分兩種問題：R10-04 是「有 schema」還是「真的能驗 approval authority」；R10-05 是現況缺陷還是尚未實作介面的預防性負控。這兩者不能用同一種嚴重性措辭。
exec
/bin/zsh -lc "UV_CACHE_DIR=/private/tmp/nova-uv-cache uv run python /private/tmp/fable-R10-mock/docs/計畫複驗.py /private/tmp/fable-R10-mock/docs/計畫 && rg -n -C 5 'RevealApproval|approval_envelope|unapproved-reveal|prefix-zero-match|--prefix|TOOL_CALL_LIMITED|backend-vanishes-mid-run|all-null-transition-row' /private/tmp/fable-R10-mock/docs/計畫/{01-可執行保證語言.md,03-權威狀態與事件日誌.md,05-執行封套與重播器.md,06-判準評估與隔離回饋.md}" in /Users/sbu/nova
 succeeded in 0ms:
計畫 22 份 · Create 路徑 771 個 · task 191 個 · ClaimSpec 落點未遷移 131 個 · 實存 claim 檔 13 份
  01 ← （無前置）
  01B ← ['01']
  02 ← ['01']
  03 ← ['01', '02']
  04 ← ['03']
  05 ← ['01', '01B', '02', '03', '04']
  06 ← ['01', '02', '03', '04', '05']
  06B ← ['01', '02', '03', '04', '05', '06']
  07 ← ['01', '02', '03', '04', '05']
  08 ← ['01', '02', '03', '04', '05', '06', '07']
  09 ← ['01', '02', '03', '04', '05', '06', '07', '08']
  10 ← ['01', '02', '03', '04', '09']
  11 ← ['01', '02', '03', '04', '05', '06', '07', '08', '09']
  12 ← ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11']
  13 ← ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']
  14 ← ['01B', '05', '06', '07', '12', '13']
  15 ← ['05', '06', '07', '11', '12', '13']
  16 ← ['05', '06', '07', '11', '12', '13']
  17 ← ['04', '05', '06', '07', '11', '12', '13']
  18 ← ['02', '03', '07', '09', '12', '13']
  19 ← ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13']
  20 ← ['01', '01B', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19']

I1 檔案所有權 · I2 依賴無環 · I3 編號即拓撲序 · I4 任務完整 · I5 修改方向 · I6 任務口徑 · I7 引用可解析 · I8 命名可通過 · I9 訊息用中文 · I10 宣告與落點一對一 · I11 檔內id相符　全部成立
/private/tmp/fable-R10-mock/docs/計畫/05-執行封套與重播器.md-12-
/private/tmp/fable-R10-mock/docs/計畫/05-執行封套與重播器.md-13-## Global Constraints
/private/tmp/fable-R10-mock/docs/計畫/05-執行封套與重播器.md-14-
/private/tmp/fable-R10-mock/docs/計畫/05-執行封套與重播器.md-15-- 【推論】後端事件中的 `done`、`success`、文字「完成」都只是觀測，不是權威終態。
/private/tmp/fable-R10-mock/docs/計畫/05-執行封套與重播器.md-16-- 【推論】wall time、回合、輸出 bytes、工具呼叫與核准花費的計數器由封套持有；後端拿不到可寫 reference。
/private/tmp/fable-R10-mock/docs/計畫/05-執行封套與重播器.md:17:- 【推論】每次執行恰有一個終態：`SUCCEEDED`、`FAILED`、`TIMED_OUT`、`ROUND_LIMITED`、`OUTPUT_LIMITED`、`TOOL_CALL_LIMITED`、`SPEND_LIMITED`、`CANCELLED`、`BACKEND_LOST`、`UNSUPPORTED_CAPABILITY`、`INTERNAL_FAULT`。
/private/tmp/fable-R10-mock/docs/計畫/05-執行封套與重播器.md-18-- 【推論】程序型後端必須以 argv 啟動，禁止 shell string；終止需覆蓋孫程序且有 kill escalation。
/private/tmp/fable-R10-mock/docs/計畫/05-執行封套與重播器.md-19-- 【推論】重播器與付費後端接受相同 `ExecutionRequest`、產生相同 `BackendEvent` union，不另開測試捷徑。
/private/tmp/fable-R10-mock/docs/計畫/05-執行封套與重播器.md-20-- 【推論】`ExecutionRequest` 引用 plan 01B 的 `ToolAuthorizationPolicyRef`、`StructuredOutputContractRef`、`DelegationPolicyRef`；manifest 以 `PRE_TOOL_DECISION|NATIVE_STRUCTURED_OUTPUT|DELEGATION` 宣告能力，缺 required capability 只回 typed `UNSUPPORTED_CAPABILITY`。
/private/tmp/fable-R10-mock/docs/計畫/05-執行封套與重播器.md-21-- 【推論】工具操作分成 `READ_ONLY|EFFECT_INTENT_REQUIRED|LOCAL_WORKSPACE_MUTATION|DELEGATION`；`EFFECT_INTENT_REQUIRED` handler 只能呼叫 EffectIntent port，不得直接碰外部 endpoint。
/private/tmp/fable-R10-mock/docs/計畫/05-執行封套與重播器.md-22-- 【推論】usage observation 必帶 `ROOT_ONLY|DELEGATION_TREE_TOTAL|UNKNOWN` scope；封套不得把 root usage 升格成 tree total。
--
/private/tmp/fable-R10-mock/docs/計畫/05-執行封套與重播器.md-121-    SUCCEEDED = "SUCCEEDED"
/private/tmp/fable-R10-mock/docs/計畫/05-執行封套與重播器.md-122-    FAILED = "FAILED"
/private/tmp/fable-R10-mock/docs/計畫/05-執行封套與重播器.md-123-    TIMED_OUT = "TIMED_OUT"
/private/tmp/fable-R10-mock/docs/計畫/05-執行封套與重播器.md-124-    ROUND_LIMITED = "ROUND_LIMITED"
/private/tmp/fable-R10-mock/docs/計畫/05-執行封套與重播器.md-125-    OUTPUT_LIMITED = "OUTPUT_LIMITED"
/private/tmp/fable-R10-mock/docs/計畫/05-執行封套與重播器.md:126:    TOOL_CALL_LIMITED = "TOOL_CALL_LIMITED"
/private/tmp/fable-R10-mock/docs/計畫/05-執行封套與重播器.md-127-    SPEND_LIMITED = "SPEND_LIMITED"
/private/tmp/fable-R10-mock/docs/計畫/05-執行封套與重播器.md-128-    CANCELLED = "CANCELLED"
/private/tmp/fable-R10-mock/docs/計畫/05-執行封套與重播器.md-129-    BACKEND_LOST = "BACKEND_LOST"
/private/tmp/fable-R10-mock/docs/計畫/05-執行封套與重播器.md-130-    UNSUPPORTED_CAPABILITY = "UNSUPPORTED_CAPABILITY"
/private/tmp/fable-R10-mock/docs/計畫/05-執行封套與重播器.md-131-    INTERNAL_FAULT = "INTERNAL_FAULT"
--
/private/tmp/fable-R10-mock/docs/計畫/05-執行封套與重播器.md-405-- Produces: `TerminalClassifier.classify(exit_evidence, counters, cancellation, protocol_fault) -> ExecutionTerminal`。
/private/tmp/fable-R10-mock/docs/計畫/05-執行封套與重播器.md-406-
/private/tmp/fable-R10-mock/docs/計畫/05-執行封套與重播器.md-407-**ClaimSpec:** 【推論】`execution.terminal.external-authority` 從紅轉綠。
/private/tmp/fable-R10-mock/docs/計畫/05-執行封套與重播器.md-408-
/private/tmp/fable-R10-mock/docs/計畫/05-執行封套與重播器.md-409-**固定負控:** 【推論】後端在非零退出前輸出 `{"kind":"COMPLETED","success":true}`；權威終態必須是 `FAILED`，不是 `SUCCEEDED`。
/private/tmp/fable-R10-mock/docs/計畫/05-執行封套與重播器.md:410:`backend-vanishes-mid-run`：後端程序消失、無 exit evidence——權威終態必須是
/private/tmp/fable-R10-mock/docs/計畫/05-執行封套與重播器.md-411-`BACKEND_LOST`，不得因缺 exit code 誤判 `FAILED` 或 `INTERNAL_FAULT`。
/private/tmp/fable-R10-mock/docs/計畫/05-執行封套與重播器.md-412-（R10 覆蓋審修正：分類器宣稱 total，但 precedence 表原本沒有 `backend_lost` 與
/private/tmp/fable-R10-mock/docs/計畫/05-執行封套與重播器.md-413-`tool_call_limit` 兩列——十一個終態裡兩個沒有來源行。`UNSUPPORTED_CAPABILITY`
/private/tmp/fable-R10-mock/docs/計畫/05-執行封套與重播器.md-414-是 admission-time 終態、分類器不經手，此為明文而非缺口。）
/private/tmp/fable-R10-mock/docs/計畫/05-執行封套與重播器.md-415-
--
/private/tmp/fable-R10-mock/docs/計畫/05-執行封套與重播器.md-567-- Modify: `驗收/執行封套/假後端.py`
/private/tmp/fable-R10-mock/docs/計畫/05-執行封套與重播器.md-568-- Modify: `驗收/執行封套/測_外部上限.py`
/private/tmp/fable-R10-mock/docs/計畫/05-執行封套與重播器.md-569-
/private/tmp/fable-R10-mock/docs/計畫/05-執行封套與重播器.md-570-**Interfaces:**
/private/tmp/fable-R10-mock/docs/計畫/05-執行封套與重播器.md-571-- Produces: `max_tool_calls` 計數器的邊界判定——第 N+1 個工具呼叫不得 dispatch，
/private/tmp/fable-R10-mock/docs/計畫/05-執行封套與重播器.md:572:  終態 `TOOL_CALL_LIMITED`。
/private/tmp/fable-R10-mock/docs/計畫/05-執行封套與重播器.md-573-- **為什麼獨立一格**：Global Constraints 列五個計數器（wall／rounds／output／
/private/tmp/fable-R10-mock/docs/計畫/05-執行封套與重播器.md-574-  tool calls／spend），四個各有 claim 與負控，`max_tool_calls` 原本**零殺手**、
/private/tmp/fable-R10-mock/docs/計畫/05-執行封套與重播器.md-575-  連對應終態都缺席（R10 覆蓋審發現）。枚舉的每個成員要有自己的殺手。
/private/tmp/fable-R10-mock/docs/計畫/05-執行封套與重播器.md-576-
/private/tmp/fable-R10-mock/docs/計畫/05-執行封套與重播器.md-577-**ClaimSpec:** 【推論】`execution.limit.tool-calls.externally-enforced` 從紅轉綠。
/private/tmp/fable-R10-mock/docs/計畫/05-執行封套與重播器.md-578-
/private/tmp/fable-R10-mock/docs/計畫/05-執行封套與重播器.md-579-**ClaimSpec落點:** `execution.limit.tool-calls.externally-enforced` → `規格/執行/保證/外部工具呼叫上限.claim.json`（本 task Create）
/private/tmp/fable-R10-mock/docs/計畫/05-執行封套與重播器.md-580-
/private/tmp/fable-R10-mock/docs/計畫/05-執行封套與重播器.md-581-**固定負控:** 【推論】假後端連發 N+1 個工具呼叫請求；第 N+1 個不得取得 grant，
/private/tmp/fable-R10-mock/docs/計畫/05-執行封套與重播器.md:582:必須紅在 `tool_call_grant_bounded`，終態恰為 `TOOL_CALL_LIMITED`。
/private/tmp/fable-R10-mock/docs/計畫/05-執行封套與重播器.md-583-防恆真格：N-1／N 個呼叫照常放行，terminal 不觸發。
/private/tmp/fable-R10-mock/docs/計畫/05-執行封套與重播器.md-584-
/private/tmp/fable-R10-mock/docs/計畫/05-執行封套與重播器.md-585-- [ ] **Step 1: 寫 N-1/N/N+1 boundary red**
/private/tmp/fable-R10-mock/docs/計畫/05-執行封套與重播器.md-586-
/private/tmp/fable-R10-mock/docs/計畫/05-執行封套與重播器.md-587-```python
/private/tmp/fable-R10-mock/docs/計畫/05-執行封套與重播器.md:588:@pytest.mark.parametrize(("seen", "limit", "terminal"), [(2, 3, None), (3, 3, None), (4, 3, "TOOL_CALL_LIMITED")])
/private/tmp/fable-R10-mock/docs/計畫/05-執行封套與重播器.md-589-def test_tool_call_boundary(seen: int, limit: int, terminal: str | None) -> None:
/private/tmp/fable-R10-mock/docs/計畫/05-執行封套與重播器.md-590-    assert decide_tool_call_limit(seen=seen, limit=limit).terminal == terminal
/private/tmp/fable-R10-mock/docs/計畫/05-執行封套與重播器.md-591-```
/private/tmp/fable-R10-mock/docs/計畫/05-執行封套與重播器.md-592-
/private/tmp/fable-R10-mock/docs/計畫/05-執行封套與重播器.md-593-- [ ] **Step 2: 跑紅測確認第 N+1 個呼叫仍放行**
--
/private/tmp/fable-R10-mock/docs/計畫/06-判準評估與隔離回饋.md-34-├── 揭露帳.machine.json                       — ReserveDisclosure／Recorded／Exhausted。
/private/tmp/fable-R10-mock/docs/計畫/06-判準評估與隔離回饋.md-35-├── CriterionDefinition.schema.json           — guidance/sealed refs 與 admission metadata。
/private/tmp/fable-R10-mock/docs/計畫/06-判準評估與隔離回饋.md-36-├── DisclosureLedger.schema.json              — lineage、disclosure_id、digest、ordinal。
/private/tmp/fable-R10-mock/docs/計畫/06-判準評估與隔離回饋.md-37-├── FeedbackPolicy.schema.json                 — clause-level reducer policy。
/private/tmp/fable-R10-mock/docs/計畫/06-判準評估與隔離回饋.md-38-├── IsolationCapability.schema.json            — requirement/offer capability vocabulary。
/private/tmp/fable-R10-mock/docs/計畫/06-判準評估與隔離回饋.md:39:├── RevealApproval.schema.json                 — 揭露核准的封閉形狀；核准者由 attestation 承載。
/private/tmp/fable-R10-mock/docs/計畫/06-判準評估與隔離回饋.md-40-└── 保證/
/private/tmp/fable-R10-mock/docs/計畫/06-判準評估與隔離回饋.md-41-    ├── sealed內容不進候選.claim.json          — projection/env/argv 都不含 sealed refs。
/private/tmp/fable-R10-mock/docs/計畫/06-判準評估與隔離回饋.md-42-    ├── 隔離不得靜默降級.claim.json            — unsupported capability typed terminal。
/private/tmp/fable-R10-mock/docs/計畫/06-判準評估與隔離回饋.md-43-    ├── 回饋經reducer.claim.json               — assertion repr 不逐字外洩。
/private/tmp/fable-R10-mock/docs/計畫/06-判準評估與隔離回饋.md-44-    ├── 揭露即燒掉.claim.json                  — revealed case cannot be reused。
--
/private/tmp/fable-R10-mock/docs/計畫/06-判準評估與隔離回饋.md-362-
/private/tmp/fable-R10-mock/docs/計畫/06-判準評估與隔離回饋.md-363-### Task 6: 實作「揭露即燒掉」且 crash-safe
/private/tmp/fable-R10-mock/docs/計畫/06-判準評估與隔離回饋.md-364-
/private/tmp/fable-R10-mock/docs/計畫/06-判準評估與隔離回饋.md-365-**Files:**
/private/tmp/fable-R10-mock/docs/計畫/06-判準評估與隔離回饋.md-366-- Create: `nova/權威/判準/案例治理.py`
/private/tmp/fable-R10-mock/docs/計畫/06-判準評估與隔離回饋.md:367:- Create: `規格/判準/RevealApproval.schema.json`
/private/tmp/fable-R10-mock/docs/計畫/06-判準評估與隔離回饋.md-368-- Modify: `nova/權威/判準/定義.py`
/private/tmp/fable-R10-mock/docs/計畫/06-判準評估與隔離回饋.md-369-- Modify: `nova/應用/執行判準.py`
/private/tmp/fable-R10-mock/docs/計畫/06-判準評估與隔離回饋.md-370-- Create: `驗收/判準/測_揭露燒毀.py`
/private/tmp/fable-R10-mock/docs/計畫/06-判準評估與隔離回饋.md-371-- Create: `規格/判準/保證/揭露即燒掉.claim.json`
/private/tmp/fable-R10-mock/docs/計畫/06-判準評估與隔離回饋.md-372-
/private/tmp/fable-R10-mock/docs/計畫/06-判準評估與隔離回饋.md-373-**Interfaces:**
/private/tmp/fable-R10-mock/docs/計畫/06-判準評估與隔離回饋.md:374:- Produces: `authorize_reveal(case_ref, approval_envelope) -> RevealReceipt`。
/private/tmp/fable-R10-mock/docs/計畫/06-判準評估與隔離回饋.md:375:- Produces: `RevealApproval`（approval_envelope 的封閉形狀）——`approver_attestation_ref`、
/private/tmp/fable-R10-mock/docs/計畫/06-判準評估與隔離回饋.md-376-  `reason_code`、`scope`（單一 case_ref）、`issued_at`。核准者身分由 attestation 承載
/private/tmp/fable-R10-mock/docs/計畫/06-判準評估與隔離回饋.md-377-  不自報；權威閘的完整治理屬計畫 12，本 task 只釘「envelope 有封閉形狀且缺有效
/private/tmp/fable-R10-mock/docs/計畫/06-判準評估與隔離回饋.md:378:  approval 一律拒絕」。（R10 覆蓋審修正：approval_envelope 原本無宣告主體。）
/private/tmp/fable-R10-mock/docs/計畫/06-判準評估與隔離回饋.md-379-- Produces: atomic `CaseBurned` event before raw reveal bytes are returned。
/private/tmp/fable-R10-mock/docs/計畫/06-判準評估與隔離回饋.md-380-
/private/tmp/fable-R10-mock/docs/計畫/06-判準評估與隔離回饋.md-381-**ClaimSpec:** 【推論】`criterion.sealed-case.reveal-burns-before-release` 從紅轉綠。
/private/tmp/fable-R10-mock/docs/計畫/06-判準評估與隔離回饋.md-382-
/private/tmp/fable-R10-mock/docs/計畫/06-判準評估與隔離回饋.md-383-**固定負控:** 【推論】在 `CaseBurned` commit 前／後 SIGKILL；commit 前不得收到 raw detail，commit 後重啟不得再次選中該 case。
/private/tmp/fable-R10-mock/docs/計畫/06-判準評估與隔離回饋.md:384:`unapproved-reveal`：無 approval、或 `approver_attestation_ref` 指向不可驗來源的
/private/tmp/fable-R10-mock/docs/計畫/06-判準評估與隔離回饋.md-385-envelope，`authorize_reveal` 必須拒絕，紅在 `reveal_requires_valid_approval`。
/private/tmp/fable-R10-mock/docs/計畫/06-判準評估與隔離回饋.md-386-
/private/tmp/fable-R10-mock/docs/計畫/06-判準評估與隔離回饋.md-387-- [ ] **Step 1: 寫 ordering 與兩 crash points red**
/private/tmp/fable-R10-mock/docs/計畫/06-判準評估與隔離回饋.md-388-
/private/tmp/fable-R10-mock/docs/計畫/06-判準評估與隔離回饋.md-389-```python
--
/private/tmp/fable-R10-mock/docs/計畫/06-判準評估與隔離回饋.md-413-Expected: 【推論】PASS；named reuse negative direct red。
/private/tmp/fable-R10-mock/docs/計畫/06-判準評估與隔離回饋.md-414-
/private/tmp/fable-R10-mock/docs/計畫/06-判準評估與隔離回饋.md-415-- [ ] **Step 5: Commit**
/private/tmp/fable-R10-mock/docs/計畫/06-判準評估與隔離回饋.md-416-
/private/tmp/fable-R10-mock/docs/計畫/06-判準評估與隔離回饋.md-417-```bash
/private/tmp/fable-R10-mock/docs/計畫/06-判準評估與隔離回饋.md:418:git add nova/權威/判準 規格/判準/RevealApproval.schema.json nova/應用/執行判準.py 驗收/判準/測_揭露燒毀.py 規格/判準/保證/揭露即燒掉.claim.json
/private/tmp/fable-R10-mock/docs/計畫/06-判準評估與隔離回饋.md-419-git commit -m "feat: 封存 case 揭露前先燒掉"
/private/tmp/fable-R10-mock/docs/計畫/06-判準評估與隔離回饋.md-420-```
/private/tmp/fable-R10-mock/docs/計畫/06-判準評估與隔離回饋.md-421-
/private/tmp/fable-R10-mock/docs/計畫/06-判準評估與隔離回饋.md-422----
/private/tmp/fable-R10-mock/docs/計畫/06-判準評估與隔離回饋.md-423-
--
/private/tmp/fable-R10-mock/docs/計畫/03-權威狀態與事件日誌.md-163-**固定負控:** 【推論】application 直接 insert `ready→secret-pass` 即使關掉 Python transition guard，也必須 SQLite constraint red。
/private/tmp/fable-R10-mock/docs/計畫/03-權威狀態與事件日誌.md-164-NULL 語意五格（CHECK 綁 `event_kind`，不是裸的全有全無）：
/private/tmp/fable-R10-mock/docs/計畫/03-權威狀態與事件日誌.md-165-`partial-null-transition-row`：TRANSITION 列 `machine_digest` 設值、`transition_id` 留
/private/tmp/fable-R10-mock/docs/計畫/03-權威狀態與事件日誌.md-166-NULL 直插，必須 IntegrityError——**SQLite composite FK 一律按 `MATCH SIMPLE`，
/private/tmp/fable-R10-mock/docs/計畫/03-權威狀態與事件日誌.md-167-任一欄 NULL 即整條不檢查**（官方文件：不執行 `MATCH FULL`）。
/private/tmp/fable-R10-mock/docs/計畫/03-權威狀態與事件日誌.md:168:`all-null-transition-row`：TRANSITION 列四欄**全 NULL** 直插，必須 IntegrityError——
/private/tmp/fable-R10-mock/docs/計畫/03-權威狀態與事件日誌.md-169-裸的「全有全無」CHECK 仍放行這條，繞過 FK 的孔沒補完；綁 `event_kind` 才封死。
/private/tmp/fable-R10-mock/docs/計畫/03-權威狀態與事件日誌.md-170-`non-transition-smuggles-tuple`：非 TRANSITION 列偷帶完整 transition tuple，
/private/tmp/fable-R10-mock/docs/計畫/03-權威狀態與事件日誌.md-171-必須 IntegrityError——反向也封。
/private/tmp/fable-R10-mock/docs/計畫/03-權威狀態與事件日誌.md-172-防恆真兩格：合法 TRANSITION 列（四欄齊、tuple 在 admitted_transition）照常提交；
/private/tmp/fable-R10-mock/docs/計畫/03-權威狀態與事件日誌.md-173-合法非 TRANSITION 列（四欄全 NULL）照常提交。
--
/private/tmp/fable-R10-mock/docs/計畫/01-可執行保證語言.md-653-- Create: `nova/基礎設施/裁定執行/案例執行.py`
/private/tmp/fable-R10-mock/docs/計畫/01-可執行保證語言.md-654-
/private/tmp/fable-R10-mock/docs/計畫/01-可執行保證語言.md-655-**Interfaces:**
/private/tmp/fable-R10-mock/docs/計畫/01-可執行保證語言.md-656-- Produces: pytest ids `<claim_id>::actual`、`::positive::<id>`、`::negative::<id>`。
/private/tmp/fable-R10-mock/docs/計畫/01-可執行保證語言.md-657-- Produces: JSON evidence line with `plan_digest`、case id、typed terminal、failed predicates。
/private/tmp/fable-R10-mock/docs/計畫/01-可執行保證語言.md:658:- Produces: `工具/跑驗收.py --prefix <字首>`——跑所有 claim_id 以該字首開頭的 claim；
/private/tmp/fable-R10-mock/docs/計畫/01-可執行保證語言.md-659-  **0 命中必須 exit 非零並明講**，不得靜默全綠——「入口永遠回零」的驗收版。
/private/tmp/fable-R10-mock/docs/計畫/01-可執行保證語言.md:660:  （R10 覆蓋審修正：`--prefix` 有 11 份計畫在消費、零宣告；改名一個 namespace
/private/tmp/fable-R10-mock/docs/計畫/01-可執行保證語言.md-661-  就會讓某份計畫的 Exit Gate 靜默跑零條 claim 而綠。）
/private/tmp/fable-R10-mock/docs/計畫/01-可執行保證語言.md-662-
/private/tmp/fable-R10-mock/docs/計畫/01-可執行保證語言.md-663-**ClaimSpec:** 【推論】`claimspec.framework.no-verdict-rewrite` 從紅轉綠。
/private/tmp/fable-R10-mock/docs/計畫/01-可執行保證語言.md-664-
/private/tmp/fable-R10-mock/docs/計畫/01-可執行保證語言.md-665-**ClaimSpec落點:** `claimspec.framework.no-verdict-rewrite` → `規格/判準/保證/框架不得改寫裁定.claim.json`（本 task Create）
/private/tmp/fable-R10-mock/docs/計畫/01-可執行保證語言.md-666-
/private/tmp/fable-R10-mock/docs/計畫/01-可執行保證語言.md-667-**固定負控:** 【推論】plugin 把 `HARNESS_ERROR` 改成 xfail 或把 negative direct red 改成 actual PASS 時，meta-test 必須紅。
/private/tmp/fable-R10-mock/docs/計畫/01-可執行保證語言.md:668:`prefix-zero-match`：`--prefix 不存在的字首.` 必須 exit 非零並回報 0 命中，
/private/tmp/fable-R10-mock/docs/計畫/01-可執行保證語言.md-669-不得靜默通過。
/private/tmp/fable-R10-mock/docs/計畫/01-可執行保證語言.md-670-
/private/tmp/fable-R10-mock/docs/計畫/01-可執行保證語言.md-671-- [ ] **Step 1: 寫 pytest item／exit-code contract test**
/private/tmp/fable-R10-mock/docs/計畫/01-可執行保證語言.md-672-
/private/tmp/fable-R10-mock/docs/計畫/01-可執行保證語言.md-673-```python

codex
我重跑合套閘：22 份計畫、771 個 Create、191 tasks、未遷移 131，I1–I11 全綠。

## 逐條裁決

| 決議 | 裁決 | 理由 |
|---|---|---|
| R10-00 | APPROVE | causal 欄位與對應殺手已從 R9-07 解耦，可獨立落地。 |
| R10-01 | APPROVE | CHECK 現在綁定 `event_kind`，同時封住 partial-NULL、all-NULL transition 與反向偷帶 tuple。 |
| R10-02 | APPROVE | 改用 pytest 原生 parameterization，移除了不存在的 plugin 指涉與無必要依賴。 |
| R10-03 | APPROVE | `max_tool_calls` 取得外部 grant 邊界、typed terminal 與負控；terminal classifier 的 `BACKEND_LOST` 缺口也補齊。 |
| R10-04 | REJECT `NOT_TESTABLE` | schema 只證明 approval envelope 長得對，沒有任何已存在的 authority/verifier 能判斷 `approver_attestation_ref` 是否「有效」。 |
| R10-05 | REJECT `INVARIANT_BREAK` | plan 01 Task 9 已交付且其 ClaimSpec 已准入；把新介面與鄰接性質塞回已完成 task，既不會安排新的實作工作，也會逼人改動既有 claim。 |

## APPROVE 項目的寫入條件

### R10-00

保留上一輪條件：

- root event 可使用 typed root/null causation；
- derived event 必須有可解析的 cause；
- 不得填假 sentinel 只為通過 required-field schema。

### R10-01

SQL constraint 必須使用明確的 event-kind 等價關係，而不是兩條互不相干的 CHECK。五格測試應直接走 SQL insert，不能只驗 Python validator。

### R10-03

工具呼叫計數點必須在外部 grant 前：

```text
收到 tool request
→ 外部計數／判限
→ 未超限才簽發 grant
→ adapter 才能執行
```

若先執行再計數，第 N+1 次即使最後得到 `TOOL_CALL_LIMITED`，保證仍已失敗。固定負控應觀察 fake tool handler 的 invocation count 恰為 N。

`BACKEND_LOST` 也要與以下情況分開：

- 有可信非零 exit evidence → `FAILED`
- supervisor／protocol 自己壞掉 → `INTERNAL_FAULT`
- 後端消失且無可信 exit evidence → `BACKEND_LOST`

## R10-04 最小重提修改

`RevealApproval` 必須有解析與驗證主體，不能只新增 schema。

最小形狀：

- 新增 `RevealApprovalVerifier` port：

  ```text
  verify(
      approval,
      criterion_revision,
      case_ref,
      requested_action
  ) -> VerifiedRevealApproval | ApprovalFailure
  ```

- approval 至少綁：

  - criterion revision/digest
  - exact case ref
  - requested action=`REVEAL_RAW_CASE`
  - approver attestation ref
  - authority revision/digest
  - issued_at
  - expiry或明確 one-shot 語意
  - nonce／approval id

- 無 production verifier binding 時一律：

  ```text
  APPROVAL_AUTHORITY_UNAVAILABLE
  ```

- plan 12 後續提供 production authority binding；在此之前只能完成拒絕路徑，不能真的 reveal。
- 固定負控至少包括：

  - 不可解析 attestation；
  - approval 綁另一個 case；
  - approval 綁另一 criterion revision；
  - approval 核准別的 action；
  - approval 重播；
  - verifier unavailable。

若只想在 Task 6 建立形狀，claim 必須降名為 `reveal.requires-closed-approval-envelope`，不得使用 `valid_approval`。但由於 raw reveal 是安全邊界，我建議現在就建立 verifier port 並 fail-closed。

## R10-05 最小重提修改

這個能力應新增獨立 task，不得回填已完成的 Task 9。

建議：

- 新 Task 19（或目前下一個可用序號）。
- Modify：

  - `工具/跑驗收.py`
  - runner 對應測試檔

- Create：

  - `規格/判準/保證/字首驗收不得空跑.claim.json`

- 新 claim：

  ```text
  claimspec.runner.prefix-selection-nonempty
  ```

- 固定負控：

  - 不存在 prefix → exit 非零且報 0 matches；
  - prefix parser 被改成空集合回零 → 指定 predicate 紅；
  - prefix 命中多份 claim → 每份都執行；
  - 任一匹配 claim 紅 → 整體非零；
  - exact prefix boundary，避免 `resource.a` 意外匹配另一 namespace。

- 防恆真：

  - 已知 prefix 至少命中一份且全部綠時 exit 0；
  - 不使用 `--prefix` 的既有單 claim 路徑行為不變。

這也避免把 prefix selection 塞進語意不相干的 `claimspec.framework.no-verdict-rewrite`。

## R10-05 的嚴重性宣稱

是，原文強過證據。

目前能證明的是：

- `--prefix` 有多份計畫消費；
- 它尚未被宣告或實作；
- 現有 `-k` 與 pytest 零命中回 exit 5；
- 未來若 naive implementation 對空集合回零，就會形成靜默全綠。

目前不能說：

> `--prefix` 0 命中已經靜默全綠。

因為該旗標根本不存在；現在更可能是 argument parsing 直接非零。正確措辭應是：

> `--prefix` 是 11 份 Exit Gate 依賴但尚未存在的介面。若未事前釘住 zero-match 非零語意，未來以「先篩選、再遍歷」實作時，空集合可能自然回零，使 namespace 漂移靜默跳過整組驗收。

嚴重性仍然高，因為影響 11 份計畫的 Exit Gate；但它是高影響的設計缺口與可預見失敗模式，不是已實測存在的 silent-green bug。兩者必須分開記錄。
tokens used
21,153
我重跑合套閘：22 份計畫、771 個 Create、191 tasks、未遷移 131，I1–I11 全綠。

## 逐條裁決

| 決議 | 裁決 | 理由 |
|---|---|---|
| R10-00 | APPROVE | causal 欄位與對應殺手已從 R9-07 解耦，可獨立落地。 |
| R10-01 | APPROVE | CHECK 現在綁定 `event_kind`，同時封住 partial-NULL、all-NULL transition 與反向偷帶 tuple。 |
| R10-02 | APPROVE | 改用 pytest 原生 parameterization，移除了不存在的 plugin 指涉與無必要依賴。 |
| R10-03 | APPROVE | `max_tool_calls` 取得外部 grant 邊界、typed terminal 與負控；terminal classifier 的 `BACKEND_LOST` 缺口也補齊。 |
| R10-04 | REJECT `NOT_TESTABLE` | schema 只證明 approval envelope 長得對，沒有任何已存在的 authority/verifier 能判斷 `approver_attestation_ref` 是否「有效」。 |
| R10-05 | REJECT `INVARIANT_BREAK` | plan 01 Task 9 已交付且其 ClaimSpec 已准入；把新介面與鄰接性質塞回已完成 task，既不會安排新的實作工作，也會逼人改動既有 claim。 |

## APPROVE 項目的寫入條件

### R10-00

保留上一輪條件：

- root event 可使用 typed root/null causation；
- derived event 必須有可解析的 cause；
- 不得填假 sentinel 只為通過 required-field schema。

### R10-01

SQL constraint 必須使用明確的 event-kind 等價關係，而不是兩條互不相干的 CHECK。五格測試應直接走 SQL insert，不能只驗 Python validator。

### R10-03

工具呼叫計數點必須在外部 grant 前：

```text
收到 tool request
→ 外部計數／判限
→ 未超限才簽發 grant
→ adapter 才能執行
```

若先執行再計數，第 N+1 次即使最後得到 `TOOL_CALL_LIMITED`，保證仍已失敗。固定負控應觀察 fake tool handler 的 invocation count 恰為 N。

`BACKEND_LOST` 也要與以下情況分開：

- 有可信非零 exit evidence → `FAILED`
- supervisor／protocol 自己壞掉 → `INTERNAL_FAULT`
- 後端消失且無可信 exit evidence → `BACKEND_LOST`

## R10-04 最小重提修改

`RevealApproval` 必須有解析與驗證主體，不能只新增 schema。

最小形狀：

- 新增 `RevealApprovalVerifier` port：

  ```text
  verify(
      approval,
      criterion_revision,
      case_ref,
      requested_action
  ) -> VerifiedRevealApproval | ApprovalFailure
  ```

- approval 至少綁：

  - criterion revision/digest
  - exact case ref
  - requested action=`REVEAL_RAW_CASE`
  - approver attestation ref
  - authority revision/digest
  - issued_at
  - expiry或明確 one-shot 語意
  - nonce／approval id

- 無 production verifier binding 時一律：

  ```text
  APPROVAL_AUTHORITY_UNAVAILABLE
  ```

- plan 12 後續提供 production authority binding；在此之前只能完成拒絕路徑，不能真的 reveal。
- 固定負控至少包括：

  - 不可解析 attestation；
  - approval 綁另一個 case；
  - approval 綁另一 criterion revision；
  - approval 核准別的 action；
  - approval 重播；
  - verifier unavailable。

若只想在 Task 6 建立形狀，claim 必須降名為 `reveal.requires-closed-approval-envelope`，不得使用 `valid_approval`。但由於 raw reveal 是安全邊界，我建議現在就建立 verifier port 並 fail-closed。

## R10-05 最小重提修改

這個能力應新增獨立 task，不得回填已完成的 Task 9。

建議：

- 新 Task 19（或目前下一個可用序號）。
- Modify：

  - `工具/跑驗收.py`
  - runner 對應測試檔

- Create：

  - `規格/判準/保證/字首驗收不得空跑.claim.json`

- 新 claim：

  ```text
  claimspec.runner.prefix-selection-nonempty
  ```

- 固定負控：

  - 不存在 prefix → exit 非零且報 0 matches；
  - prefix parser 被改成空集合回零 → 指定 predicate 紅；
  - prefix 命中多份 claim → 每份都執行；
  - 任一匹配 claim 紅 → 整體非零；
  - exact prefix boundary，避免 `resource.a` 意外匹配另一 namespace。

- 防恆真：

  - 已知 prefix 至少命中一份且全部綠時 exit 0；
  - 不使用 `--prefix` 的既有單 claim 路徑行為不變。

這也避免把 prefix selection 塞進語意不相干的 `claimspec.framework.no-verdict-rewrite`。

## R10-05 的嚴重性宣稱

是，原文強過證據。

目前能證明的是：

- `--prefix` 有多份計畫消費；
- 它尚未被宣告或實作；
- 現有 `-k` 與 pytest 零命中回 exit 5；
- 未來若 naive implementation 對空集合回零，就會形成靜默全綠。

目前不能說：

> `--prefix` 0 命中已經靜默全綠。

因為該旗標根本不存在；現在更可能是 argument parsing 直接非零。正確措辭應是：

> `--prefix` 是 11 份 Exit Gate 依賴但尚未存在的介面。若未事前釘住 zero-match 非零語意，未來以「先篩選、再遍歷」實作時，空集合可能自然回零，使 namespace 漂移靜默跳過整組驗收。

嚴重性仍然高，因為影響 11 份計畫的 Exit Gate；但它是高影響的設計缺口與可預見失敗模式，不是已實測存在的 silent-green bug。兩者必須分開記錄。
