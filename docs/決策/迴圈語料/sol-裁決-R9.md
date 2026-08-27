codex
我會先重跑合套閘，再用 SQLite 官方文件複核 partial-NULL；其餘逐條只問兩件事：新負控是否真的殺到 claim 的那一半，以及「刪掉」是否縮減了可執行保證。最後我會補上覆蓋清單漏掉的前八輪缺陷形狀。
web search: 
web search: site:sqlite.org foreign keys composite child key NULL no requirement corresponding row parent table
exec
/bin/zsh -lc "UV_CACHE_DIR=/private/tmp/nova-uv-cache uv run python /private/tmp/fable-R9-mock/docs/計畫複驗.py /private/tmp/fable-R9-mock/docs/計畫 && rg -n -C 3 'claim-ref|cardinality|require_output|LocaleCatalog|missing-causal-fields|partial-null-transition-row|recorded_at|pytest-repeat|delete-old-row|admission-past-hard-point' /private/tmp/fable-R9-mock/docs/計畫/{02-狀態機宣告與編譯.md,03-權威狀態與事件日誌.md,04-內容定址證據與保存.md}" in /Users/sbu/nova
 exited 2 in 0ms:
計畫 22 份 · Create 路徑 769 個 · task 190 個 · ClaimSpec 落點未遷移 131 個 · 實存 claim 檔 13 份
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
rg: /private/tmp/fable-R9-mock/docs/計畫/02-狀態機宣告與編譯.md: No such file or directory (os error 2)
rg: /private/tmp/fable-R9-mock/docs/計畫/04-內容定址證據與保存.md: No such file or directory (os error 2)
/private/tmp/fable-R9-mock/docs/計畫/03-權威狀態與事件日誌.md-6-
/private/tmp/fable-R9-mock/docs/計畫/03-權威狀態與事件日誌.md-7-**Architecture:** 【推論】`權威狀態.sqlite3` 用 one process／one connection／rollback／FULL，所有 worker 只送 typed command；同一 transaction append event、更新 head、寫 owner ledgers。commit 後 single publisher 按 global_seq 冪等複製到 `尾隨事件.sqlite3` WAL；tail 可砍，權威 journal 不可由 reader 寫。
/private/tmp/fable-R9-mock/docs/計畫/03-權威狀態與事件日誌.md-8-
/private/tmp/fable-R9-mock/docs/計畫/03-權威狀態與事件日誌.md:9:**Tech Stack:** 【推論】CPython 3.14.7、stdlib sqlite3、multiprocessing／Unix socket、SQLite foreign keys、rollback journal、WAL tail、pytest subprocess SIGKILL、pytest-repeat（`--count` 重複矩陣）、ClaimSpec runner。
/private/tmp/fable-R9-mock/docs/計畫/03-權威狀態與事件日誌.md-10-
/private/tmp/fable-R9-mock/docs/計畫/03-權威狀態與事件日誌.md-11-**Spec:** 【查證】本檔「子系統規格」、[第三輪 runtime 三道硬閘與事件](../sol-新局-第三輪.md#27-執行時禁止未宣告轉移三道硬閘)、[第二輪 workload envelope](../sol-新局-第二輪.md#32-建議的-v1-design-envelope)。第五輪 archive／prune 由 Plan 04 承接。
/private/tmp/fable-R9-mock/docs/計畫/03-權威狀態與事件日誌.md-12-
--
/private/tmp/fable-R9-mock/docs/計畫/03-權威狀態與事件日誌.md-48-├── 發布器.py                                  — global_seq idempotent copy。
/private/tmp/fable-R9-mock/docs/計畫/03-權威狀態與事件日誌.md-49-├── 尾隨庫.py                                  — WAL range/read-only subscription。
/private/tmp/fable-R9-mock/docs/計畫/03-權威狀態與事件日誌.md-50-├── test_發布器.py                             — duplicate／gap／restart。
/private/tmp/fable-R9-mock/docs/計畫/03-權威狀態與事件日誌.md:51:└── 遷移/0001_尾隨事件.sql                     — event bytes、digest、recorded_at、cursor。
/private/tmp/fable-R9-mock/docs/計畫/03-權威狀態與事件日誌.md-52-nova/啟動/狀態擁有者.py                        — 唯一 state DB composition root。
/private/tmp/fable-R9-mock/docs/計畫/03-權威狀態與事件日誌.md-53-架構/
/private/tmp/fable-R9-mock/docs/計畫/03-權威狀態與事件日誌.md-54-├── 依賴規則.toml                              — sqlite import allowlist。
--
/private/tmp/fable-R9-mock/docs/計畫/03-權威狀態與事件日誌.md-84-**ClaimSpec:** 【推論】`event.envelope.causal-and-canonical` 從紅轉綠。
/private/tmp/fable-R9-mock/docs/計畫/03-權威狀態與事件日誌.md-85-
/private/tmp/fable-R9-mock/docs/計畫/03-權威狀態與事件日誌.md-86-**固定負控:** 【推論】TRANSITION 缺 machine digest、aggregate_seq 跳號、inline payload 65,537 bytes 都在進 DB 前 direct red。
/private/tmp/fable-R9-mock/docs/計畫/03-權威狀態與事件日誌.md:87:`missing-causal-fields`：缺 causation／correlation／reason／schema digest 任一的 event，
/private/tmp/fable-R9-mock/docs/計畫/03-權威狀態與事件日誌.md-88-必須紅在 `envelope_requires_causal_fields`——Global Constraints 要求所有 committed event
/private/tmp/fable-R9-mock/docs/計畫/03-權威狀態與事件日誌.md-89-帶這四欄、claim 名為 causal-and-canonical，causal 半邊要有自己的殺手。
/private/tmp/fable-R9-mock/docs/計畫/03-權威狀態與事件日誌.md-90-（R9 覆蓋審修正：原 envelope fence 漏列四欄且 causal 零負控。）
--
/private/tmp/fable-R9-mock/docs/計畫/03-權威狀態與事件日誌.md-161-**ClaimSpec:** 【推論】`storage.transition.foreign-key-declared-only` 從紅轉綠。
/private/tmp/fable-R9-mock/docs/計畫/03-權威狀態與事件日誌.md-162-
/private/tmp/fable-R9-mock/docs/計畫/03-權威狀態與事件日誌.md-163-**固定負控:** 【推論】application 直接 insert `ready→secret-pass` 即使關掉 Python transition guard，也必須 SQLite constraint red。
/private/tmp/fable-R9-mock/docs/計畫/03-權威狀態與事件日誌.md:164:`partial-null-transition-row`：`machine_digest` 設值、`transition_id` 留 NULL 的直插，
/private/tmp/fable-R9-mock/docs/計畫/03-權威狀態與事件日誌.md-165-必須 IntegrityError——**SQLite 的 composite FK 任一欄 NULL 即整條不檢查**，
/private/tmp/fable-R9-mock/docs/計畫/03-權威狀態與事件日誌.md-166-沒有「全有全無」CHECK 時這是繞過 FK 的靜默孔。
/private/tmp/fable-R9-mock/docs/計畫/03-權威狀態與事件日誌.md-167-（R9 覆蓋審修正：CHECK 已入上方 migration。）
--
/private/tmp/fable-R9-mock/docs/計畫/03-權威狀態與事件日誌.md-446-
/private/tmp/fable-R9-mock/docs/計畫/03-權威狀態與事件日誌.md-447-**ClaimSpec:** 【推論】`event.tail.byte-identical-idempotent` 從紅轉綠。
/private/tmp/fable-R9-mock/docs/計畫/03-權威狀態與事件日誌.md-448-
/private/tmp/fable-R9-mock/docs/計畫/03-權威狀態與事件日誌.md:449:**固定負控:** 【推論】publisher 重啟重送同 seq、改寫 recorded_at、跳過一個 seq 都必須 red；duplicate transport可接受但 stored row 唯一。
/private/tmp/fable-R9-mock/docs/計畫/03-權威狀態與事件日誌.md-450-
/private/tmp/fable-R9-mock/docs/計畫/03-權威狀態與事件日誌.md-451-- [ ] **Step 1: 寫 duplicate／gap／byte drift tests**
/private/tmp/fable-R9-mock/docs/計畫/03-權威狀態與事件日誌.md-452-

exec
/bin/zsh -lc "rg --files /private/tmp/fable-R9-mock/docs/計畫 | rg '/(02|04)-'" in /Users/sbu/nova
 succeeded in 0ms:
/private/tmp/fable-R9-mock/docs/計畫/04-內容證據與分層儲存.md
/private/tmp/fable-R9-mock/docs/計畫/02-宣告式狀態機.md

exec
/bin/zsh -lc "rg -n -C 5 'output_id|payload_digest|LocaleCatalog|digest-over-raw-bytes|arith-operator|limit-boundary|claim-ref|cardinality' /private/tmp/fable-R9-mock/docs/計畫/02-宣告式狀態機.md; rg -n -C 5 'delete-old-row|admission-past-hard-point|pytest-repeat|recorded_at' /private/tmp/fable-R9-mock/docs/計畫/04-內容證據與分層儲存.md" in /Users/sbu/nova
 succeeded in 0ms:
18-- 【推論】Guard limits：depth 8、nodes 64、ALL／ANY children 2–16、set 1–32、facts 32、proof cells 4,096。
19-- 【推論】CustomDecisionProducer 不在 Guard AST；上限為每 machine 1、全域 3、依賴 edges `max(1,floor(N/5))`。
20-
21-## 子系統規格
22-
23:【推論】MachineSpec 擁有單一 aggregate 的 state／trigger／guard／edge／terminal／**output（`output_id`＋`payload_digest`，由 transition 的 `emits` 引用）**；FlowSpec 只綁既有 output→trigger與 parent cardinality；GraphIR 只供 view。每個 entity 永久釘 machine digest，升版只能走顯式 MachineMigration。
24-
25-【推論】compiler 對每個 `(state, trigger)` 建 finite proof cells：BOOL 兩格、ENUM 每 symbol、BOUNDED_INT 依 literal 切 interval／point；每 cell 恰一 edge，0 是 `GUARD_NOT_EXHAUSTIVE`，2+ 是 `GUARD_OVERLAP`，並回最小 witness。
26-
27-## File Structure
28-
--
41-    ├── 圖與宣告同源.claim.json             — artifact drift red。
42-    └── 非法轉移拒絕.claim.json             — undeclared edge red。
43-nova/狀態機/
44-├── 模型.py                                — MachineSpec／Guard／FlowSpec／GraphIR types。
45-├── 載入.py                                — schema、canonical bytes、digest、refs。
46:├── 檢查.py                                — structural、guard、cardinality lints。
47-├── 編譯.py                                — MachinePlan／FlowPlan／GraphIR compiler。
48-├── 執行.py                                — total transition interpreter。
49-├── 決策表.py                              — finite table compiler；無 callback。
50-├── 遷移.py                                — explicit MachineMigration validation。
51-├── 組圖.py                                — GraphIR→DOT／SVG。
--
82-
83-**Interfaces:**
84-- Produces: `load_machine(bytes) -> MachineSpec`
85-- Produces: `load_flow(bytes) -> FlowSpec`
86-- Both carry canonical bytes and SHA-256 digest。
87:- Produces: MachineSpec 宣告 `outputs`（每條 `output_id`＋`payload_digest`），
88:  transition 以 `emits` 引用 `output_id`——Task 6 FlowSpec 綁定的 `from_output`
89-  指涉物在此宣告，`machines.require_output` 才有東西可查。
90-
91-**ClaimSpec:** 【推論】`machine.spec.closed-and-digested` 從紅轉綠。
92-
93-**固定負控:** 【推論】MachineSpec 加 `x/color/progress_percent`、payload digest 不合法、
94:transition `emits` 引用未宣告的 `output_id`，都 admission red。
95:`digest-over-raw-bytes`：改成對原始 bytes 取 digest 的變體——鍵序不同的等價 JSON
96-得到不同 digest，必須紅在 `canonical_digest_key_order_insensitive`；
97-防恆真半格：內容不同必須異 digest。
98-（R9 覆蓋審修正：原「FlowSpec 發明 state」一格移除——該檢查的介面是 Task 6 的
99-`compile_flow(flow, machines)`，load 層沒有 machine catalog 可對，在本 task 是
100-不可執行的負控；Task 6 既有同格。）
--
170-- Produces: `partition_guards(edges, facts) -> GuardPartition | GuardFailure`
171-
172-**ClaimSpec:** 【推論】`machine.guard.closed-ast`、`machine.guard.partition-total-exclusive` 從紅轉綠。
173-
174-**固定負控:** 【推論】`CALL(module.fn)`、重疊 `x<=5`/`x>=5`、enum 漏值、4,097 cells 分別回 typed red＋witness。
175:`arith-operator`：把 `ARITH` 加進 `ALLOWED_OPS` 的字彙擴張變體，必須紅在
176-`guard_vocabulary_closed`——只殺 CALL 殺不掉字彙擴張。
177:`limit-boundary`：depth 9／facts 33 的 guard，必須紅在 `GUARD_LIMIT_EXCEEDED`——
178-五個上限（depth 8、nodes 64、children 2–16、set 1–32、facts 32）各有一個越界
179-witness 屬本格 fixture 集，只有 cells 一個邊界負控撐不起五個上限的宣稱。
180-
181-- [ ] **Step 1: 寫四個固定紅例**
182-
--
184-@pytest.mark.parametrize("fixture,code", [
185-    ("callback-operator", "UNSUPPORTED_GUARD"),
186-    ("overlap-at-five", "GUARD_OVERLAP"),
187-    ("enum-hole", "GUARD_NOT_EXHAUSTIVE"),
188-    ("cell-4097", "GUARD_DOMAIN_TOO_LARGE"),
189:    ("arith-operator", "UNSUPPORTED_GUARD"),
190-    ("depth-nine", "GUARD_LIMIT_EXCEEDED"),
191-])
192-def test_guard_負控(fixture: str, code: str) -> None:
193-    assert compile_fixture(fixture).failure.code == code
194-```
--
244-
245-**Interfaces:**
246-- Produces: `lint_machine(spec) -> tuple[LintFailure, ...]`
247-- Failure ids 封閉五個（每個都有負控）：dangling／unreachable／
248-  nonterminal-without-edge／no-terminal-path／terminal-outgoing。
249:  （R9 覆蓋審修正：原列的 `cardinality` 屬 FlowSpec 綁定層——Task 6 的
250:  child-to-child／owns-child cycle 負控覆蓋；`claim-ref` 移除——整份計畫無定義、
251-  無負控、無消費端，宣告了驗收意圖不等於安排了可執行驗收。）
252-
253-**ClaimSpec:** 【推論】`machine.structure.closed-reachable-terminal` 從紅轉綠。
254-
255-**固定負控:** 【推論】懸空 target、不可達 state、非終態無 outgoing、無 reverse terminal path、terminal 有 outgoing 各自 direct red。
--
449-**固定負控:** 【推論】Flow 發明新 state、child-to-child edge、payload digest mismatch、owns-child cycle 都 admission red。
450-
451-- [ ] **Step 1: 寫 cross-reference tests**
452-
453-```python
454:def test_payload_digest_不等不得_binding(flow: FlowSpec, machines: MachineCatalog) -> None:
455-    result = compile_flow(flow_with_mismatched_digest(flow), machines)
456-    assert result.failure.code == "FLOW_PAYLOAD_DIGEST_MISMATCH"
457-```
458-
459-- [ ] **Step 2: 跑紅測**
--
466-
467-```python
468-def bind_output(binding: BindingDef, machines: MachineCatalog) -> CompiledBinding:
469-    output = machines.require_output(binding.from_output)
470-    trigger = machines.require_trigger(binding.to_trigger)
471:    if output.payload_digest != trigger.payload_digest:
472-        raise FlowPayloadDigestMismatch(binding.id)
473-    return CompiledBinding(binding, output, trigger)
474-```
475-
476-- [ ] **Step 4: 跑 FlowSpec tests**
--
505-- Create: `工具/生流程圖.py`
506-- Modify: `工具/驗規格.py`
507-
508-**Interfaces:**
509-- Produces: `render_dot(GraphIR) -> bytes`——顯示文字＝semantic id 逐字。
510:  （R9 覆蓋審修正：原簽名的 `LocaleCatalog` 在整份計畫無 schema、無 Create、
511-  無來源——是懸空指涉物。本地化屬 view 層（計畫 18），屆時帶自己的 claim 與負控；
512-  v1 圖語意不含 locale。）
513-- Produces: SVG data attributes `data-node-id`、`data-edge-id`、`machine-bundle-digest`。
514-- Produces: `validate_migration(old, new, spec) -> MigrationPlan`。
515-
4-
5-**Goal:** 【推論】建立 domain-neutral CAS、不可覆寫 EvidenceRecord、hot／warm／cold retention、recovery checkpoint與可驗 backup，使 hot SQLite 可 prune 而 event truth、active Work replay與稽核證據不變弱。
6-
7-**Architecture:** 【推論】大 bytes blob-first 寫 CAS、metadata second 寫 state-owner transaction；event archive 先寫且驗 segment，再 commit SegmentManifest，checkpoint＋suffix 等價 full replay後才可在 24h overlap後 prune。CAS 可物理去重，但 recovery／operational／audit／raw／artifact pin ledgers分開。
8-
9:**Tech Stack:** 【推論】CPython 3.14.7、filesystem CAS（atomic rename＋SHA-256）、SQLite state owner port、immutable segments、Hypothesis state machines、subprocess SIGKILL、pytest-repeat（`--count` 重複矩陣）。
10-
11-**Spec:** 【查證】本檔「子系統規格」、[第五輪 tiered storage](../sol-新局-第五輪.md#2-envelope-與儲存你的乘法成立第三輪必須翻案)、[第二輪 backup SLO](../sol-新局-第二輪.md#32-建議的-v1-design-envelope)。
12-
13-## Global Constraints
14-
--
162-- Produces: `correct(old_id, new_record) -> EvidenceId`；沒有 update/delete。
163-
164-**ClaimSpec:** 【推論】`evidence.record.append-only-correction` 從紅轉綠。
165-
166-**固定負控:** 【推論】UPDATE old row、correction 不指 old id、metadata 指不存在 CAS ref 都必須 transaction red。
167:`delete-old-row`：DELETE 既有 evidence row 必須被 DB 層擋下（trigger），紅在
168-`evidence_rows_undeletable`——append-only 只殺 UPDATE 殺不掉 DELETE。
169-（R9 覆蓋審修正。）
170-
171-- [ ] **Step 1: 寫 no-update API／SQL tests**
172-
--
423-- Typed error: `STORAGE_HARD_POINT`。
424-
425-**ClaimSpec:** 【推論】`storage.operational-event.retention-tiered`、`storage.retention.no-early-delete-at-cap` 從紅轉綠。
426-
427-**固定負控:** 【推論】operational pin到90d但audit仍活時刪 blob、capacity20GiB提早縮成89d都 red。
428:`admission-past-hard-point`：到 hard point 後 ordinary admission 仍被接受的 subject，
429-必須紅在 `hard_point_stops_admission`——「不早刪」與「停收」是兩個半邊，各要有殺手。
430-（R9 覆蓋審修正。）
431-
432-- [ ] **Step 1: 寫 fake-clock pin與cursor tests**
433-

exec
/bin/zsh -lc "sed -n '13,100p' /private/tmp/fable-R9-mock/docs/計畫/03-權威狀態與事件日誌.md; sed -n '130,180p' /private/tmp/fable-R9-mock/docs/計畫/03-權威狀態與事件日誌.md; sed -n '400,445p' /private/tmp/fable-R9-mock/docs/計畫/04-內容證據與分層儲存.md" in /Users/sbu/nova
 succeeded in 0ms:
## Global Constraints

- 【推論】Plan 01、02 必須綠；DB 只存 admitted machine digest／transition tuple，不能自己補 edge。
- 【推論】只有 state-owner composition root 能 import concrete sqlite adapter；CLI、HTTP、UI、backend、evaluator 不得取得 DB path。
- 【推論】event payload inline hard max 64 KiB；大 bytes 在 Plan 04 先進 CAS，再只記 digest。
- 【推論】single transaction event hard max 32；所有 committed event 有 global_seq、aggregate_seq、causation／correlation、reason與 schema digest。
- 【推論】lease 30 秒、每 10 秒 renew；takeover 才增 fencing epoch，舊 epoch 永遠不能 commit。

## 子系統規格

【推論】state owner API 接 `CommandEnvelope(command_id, entity_id, expected_seq, trigger_id, payload)`，載入 entity 已釘 MachinePlan，取得唯一 transition，再在一筆 transaction 寫 event＋head。command idempotency key 重送回同 result，不重跑 decision。

【推論】tail publisher 的 truth 是 state-owner read port，不是直接另開權威 SQLite reader；它按 cursor 取 committed canonical event bytes，寫 WAL cache並更新 durable publisher cursor。UI subscriber只拿 range／live event port。

## File Structure

```text
規格/語言/事件.schema.json                    — event tagged-union envelope。
規格/儲存/保證/權威交易崩潰重建.claim.json     — state-owner persisted-only restart。
規格/介面/保證/事件流獨立.claim.json           — reader 不碰 owner transaction。
nova/核心/事件.py                              — EventEnvelope value／canonical bytes。
nova/應用/
├── 工作單元.py                                — state-owner port，不暴露 SQL。
└── test_工作單元.py                           — fake/real contract。
nova/基礎設施/狀態庫/sqlite/
├── 擁有者.py                                  — one connection command loop／IPC。
├── 工作單元.py                                — BEGIN／append／head／commit。
├── 機器目錄.py                                — admitted transition catalog。
├── 租約.py                                    — lease／renew／takeover fencing。
├── 讀取埠.py                                  — publisher/recovery bounded range port。
├── test_工作單元.py                           — adapter contract。
└── 遷移/
    ├── 0001_事件與機器目錄.sql                — journal、catalog、head、idempotency。
    └── 0002_租約.sql                          — lease owner／expiry／epoch。
nova/基礎設施/事件流/sqlite/
├── 發布器.py                                  — global_seq idempotent copy。
├── 尾隨庫.py                                  — WAL range/read-only subscription。
├── test_發布器.py                             — duplicate／gap／restart。
└── 遷移/0001_尾隨事件.sql                     — event bytes、digest、recorded_at、cursor。
nova/啟動/狀態擁有者.py                        — 唯一 state DB composition root。
架構/
├── 依賴規則.toml                              — sqlite import allowlist。
├── 檢查後端依賴.py                            — AST import graph checker。
└── test_依賴規則.py                           — direct DB bypass fixture。
驗收/儲存/
├── 測_非法轉移資料庫負控.py                   — composite FK 第二道紅。
├── 測_強制終止矩陣.py                         — boundary SIGKILL。
├── 測_租約回收.py                             — fencing epoch。
└── 測_事件流獨立.py                           — long tail 不持 owner transaction。
```

## Dependency Gate

前置計畫：01 02

【推論】Plan 01 提供 executable claims；Plan 02 提供 MachinePlan、transition catalog rows與 illegal-edge decision。缺 02 時 SQLite 只能存自由 state string，DB 負控沒有 oracle。

---

### Task 1: 固定事件 envelope 與 canonical bytes

**Files:**
- Create: `規格/語言/事件.schema.json`
- Create: `nova/核心/事件.py`
- Create: `nova/應用/工作單元.py`
- Create: `nova/應用/test_工作單元.py`

**Interfaces:**
- Produces: `EventEnvelope.to_canonical_bytes() -> bytes`
- Produces: `StateUnitOfWork.execute(CommandEnvelope) -> CommandResult`

**ClaimSpec:** 【推論】`event.envelope.causal-and-canonical` 從紅轉綠。

**固定負控:** 【推論】TRANSITION 缺 machine digest、aggregate_seq 跳號、inline payload 65,537 bytes 都在進 DB 前 direct red。
`missing-causal-fields`：缺 causation／correlation／reason／schema digest 任一的 event，
必須紅在 `envelope_requires_causal_fields`——Global Constraints 要求所有 committed event
帶這四欄、claim 名為 causal-and-canonical，causal 半邊要有自己的殺手。
（R9 覆蓋審修正：原 envelope fence 漏列四欄且 causal 零負控。）

- [ ] **Step 1: 寫 event schema 負控 tests**

```python
def test_transition_缺_machine_digest_拒絕(transition_event: dict[str, object]) -> None:
    del transition_event["machine_digest"]
    assert validate_event(transition_event).code == "MISSING_TRANSITION_FIELD"
```

- [ ] **Step 2: 跑紅測**
Run: `uv run pytest -q nova/應用/test_工作單元.py -k event`

Expected: 【推論】PASS。

- [ ] **Step 5: 跑 canonical bytes designated mutation**

Run: `uv run python 工具/跑驗收.py --claim event.envelope.causal-and-canonical`

Expected: 【推論】拿掉 sort_keys 的 subject direct red。

- [ ] **Step 6: Commit**

```bash
git add 規格/語言/事件.schema.json nova/核心/事件.py nova/應用/工作單元.py nova/應用/test_工作單元.py
git commit -m "feat: 定義 canonical 的領域事件封套"
```

---

### Task 2: 建 SQLite migration 與 declared-transition composite FK

**Files:**
- Create: `nova/基礎設施/狀態庫/sqlite/遷移/0001_事件與機器目錄.sql`
- Create: `nova/基礎設施/狀態庫/sqlite/機器目錄.py`
- Create: `nova/基礎設施/狀態庫/sqlite/test_工作單元.py`
- Create: `驗收/儲存/測_非法轉移資料庫負控.py`

**Interfaces:**
- Produces: `MachineCatalogStore.admit(MachinePlan) -> MachineDigest`
- DB FK key: `(machine_digest, transition_id, from_state, to_state)`。

**ClaimSpec:** 【推論】`storage.transition.foreign-key-declared-only` 從紅轉綠。

**固定負控:** 【推論】application 直接 insert `ready→secret-pass` 即使關掉 Python transition guard，也必須 SQLite constraint red。
`partial-null-transition-row`：`machine_digest` 設值、`transition_id` 留 NULL 的直插，
必須 IntegrityError——**SQLite 的 composite FK 任一欄 NULL 即整條不檢查**，
沒有「全有全無」CHECK 時這是繞過 FK 的靜默孔。
（R9 覆蓋審修正：CHECK 已入上方 migration。）

- [ ] **Step 1: 寫直接 SQL bypass test**

```python
def test_非法_tuple_無法提交(db: sqlite3.Connection, admitted_machine: MachinePlan) -> None:
    admit_machine(db, admitted_machine)
    with pytest.raises(sqlite3.IntegrityError):
        insert_transition_event(db, machine=admitted_machine.digest, transition="secret", from_state="ready", to_state="secret-pass")
```

- [ ] **Step 2: 跑紅測**

Run: `uv run pytest -q 驗收/儲存/測_非法轉移資料庫負控.py`

Run: `uv run pytest -q 驗收/儲存/測_封存崩潰間隙.py -k prune_restart --count=10`

Expected: 【推論】PASS，無 missing/duplicate logical seq。

- [ ] **Step 6: Commit**

```bash
git add nova/基礎設施/狀態庫/sqlite/事件封存.py 驗收/儲存/測_封存崩潰間隙.py 規格/儲存/保證/先發布後修剪.claim.json
git commit -m "feat: 只裁剪完全歸檔過的事件區間"
```

---

### Task 6: retention pins 與 capacity hard stops

**Files:**
- Create: `規格/儲存/保證/事件分層.claim.json`
- Create: `規格/儲存/保證/容量不得早刪.claim.json`
- Create: `驗收/儲存/測_事件分層.py`

**Interfaces:**
- Produces: `RetentionClass` policies and `PinLedger`。
- Typed error: `STORAGE_HARD_POINT`。

**ClaimSpec:** 【推論】`storage.operational-event.retention-tiered`、`storage.retention.no-early-delete-at-cap` 從紅轉綠。

**固定負控:** 【推論】operational pin到90d但audit仍活時刪 blob、capacity20GiB提早縮成89d都 red。
`admission-past-hard-point`：到 hard point 後 ordinary admission 仍被接受的 subject，
必須紅在 `hard_point_stops_admission`——「不早刪」與「停收」是兩個半邊，各要有殺手。
（R9 覆蓋審修正。）

- [ ] **Step 1: 寫 fake-clock pin與cursor tests**

```python
def test_audit_pin_阻止九十天_GC(pin_ledger: PinLedger, blob: ContentRef, clock: FakeClock) -> None:
    pin_ledger.pin(blob, RetentionClass.OPERATIONAL, days=90)
    pin_ledger.pin(blob, RetentionClass.AUDIT, days=365)
    clock.advance(days=91)
    assert blob not in pin_ledger.gc_candidates(clock.now())
```

- [ ] **Step 2: 跑紅測**

Run: `uv run pytest -q 驗收/儲存/測_事件分層.py`


codex
我重跑合套閘：22 份計畫、769 個 Create、190 tasks、未遷移 131，I1–I11 全綠。

## 逐條裁決

| 決議 | 裁決 | 理由 |
|---|---|---|
| R9-00 | APPROVE | 單成員 assembly policy 現在只驗可達的解析、內容綁定與封閉字彙，沒有再冒稱已驗過不存在的第二政策。 |
| R9-01 | APPROVE | MachineSpec 終於宣告 FlowSpec 要引用的 output，`require_output` 不再查一個不存在的 catalog 成員。 |
| R9-02 | APPROVE | `LocaleCatalog` 在狀態機編譯層沒有主體與必要性，刪除懸空參數比就地發明另一個權威正確。 |
| R9-03 | APPROVE | canonical digest 現在有直接 mutation；錯層的 FlowSpec 負控回到真正擁有 machine catalog 的 Task 6。 |
| R9-04 | APPROVE | closed vocabulary 與各項資源上限都有自己的越界 witness，Hypothesis 測試也取得明確檔案落點。 |
| R9-05 | APPROVE | `claim-ref` 沒有語意、消費端或負控，刪掉的是空 failure id，不是可執行保證。 |
| R9-06 | APPROVE | causal 半邊取得直接負控，fence 也與 Global Constraints 對齊。 |
| R9-07 | REJECT `WEAKENS_GUARANTEE` | 「四欄全 NULL 或全 NOT NULL」仍允許 `TRANSITION` event 四欄全 NULL，繼續繞過 composite FK。 |
| R9-08 | REJECT `NOT_TESTABLE` | 只把 `pytest-repeat` 寫進 Tech Stack 不會安裝 plugin；`--count` 仍可能是不可達命令。 |
| R9-09 | APPROVE | append-only 現在同時攔 UPDATE 與 DELETE，不再只保護一半。 |
| R9-10 | APPROVE | capacity hard stop 的「停止 ordinary admission」取得直接殺手，不再只驗不早刪。 |

## APPROVE 項目的寫入條件

### R9-01

`payload_digest` 必須明定為 payload contract/schema digest，不是某次 runtime payload bytes 的 digest。建議直接命名 `payload_contract_digest`，避免下一輪再產生語意歧義。

負控至少包含：

- transition `emits` 未宣告 output；
- output 與 trigger 的 contract digest 不同；
- 同 `output_id` 對應兩個不同 contract digest。

### R9-04

五類 guard 上限必須各有一個實際 fixture，不能只在散文中說「fixture 集」：

- depth 9
- nodes 65
- children 1 與 17
- set size 33
- facts 33

另保留既有 4,097 proof cells。每格都應確認只紅在自己的 limit predicate。

### R9-06

「欄位存在」與「存在因果」必須分開：

- root event 可以有 typed root/null causation；
- derived event 必須有可解析的 `causation_id`；
- `correlation_id` 必須維持跨流程關聯；
- 不得為通過 required-field schema 而填假的 sentinel id。

建議增加：

- `derived-event-null-causation`  
  → `derived_event_requires_cause`
- 防恆真：root event 使用明確 `ROOT_CAUSE`／nullable root 形狀仍合法。

### R9-10

hard point 不得用「全部操作一律拒絕」取得假綠。到達 hard point 後仍必須允許：

- GC／prune
- checkpoint
- archive／backup
- repair／capacity recovery
- 已開始交易的安全收束

固定負控之外補防恆真：ordinary new admission 被拒，但能解除 hard point 的 maintenance command 仍可執行。

## R9-07 最小重提修改

SQLite 官方明確規定：composite child key 任一欄為 `NULL`，就不要求存在對應 parent row；而且 SQLite 對外鍵一律按 `MATCH SIMPLE` 處理，不執行 `MATCH FULL`。[SQLite Foreign Key Support](https://www.sqlite.org/foreignkeys.html)

所以你的實測與 fable 的知識宣稱都正確。但提案的 CHECK 還少 event kind 關聯。

需要改成等價於：

```sql
CHECK (
    (
        event_kind = 'TRANSITION'
        AND machine_digest IS NOT NULL
        AND transition_id IS NOT NULL
        AND from_state IS NOT NULL
        AND to_state IS NOT NULL
    )
    OR
    (
        event_kind <> 'TRANSITION'
        AND machine_digest IS NULL
        AND transition_id IS NULL
        AND from_state IS NULL
        AND to_state IS NULL
    )
)
```

若某些非 transition event 合法攜帶 machine digest，就應拆成另一組明確欄位規則，不能使用模糊的 all-or-none。

固定負控至少要有：

- partial-NULL transition；
- all-NULL transition；
- non-transition event 偷帶完整 transition tuple；
- 合法 transition tuple；
- 合法 non-transition event。

前兩者都必須失敗，否則 `foreign-key-declared-only` 仍有旁路。

## R9-08 最小重提修改

`recorded_at` 補進 tail schema 可以保留。`pytest-repeat` 二選一：

1. 在一個明確 task 中：

   - Modify `pyproject.toml`
   - Modify `uv.lock`
   - pin `pytest-repeat`
   - 固定負控證明缺 plugin 時 gate 失敗

2. 更小的做法：完全不用 plugin，把重複次數寫進 pytest parameterization／測試內迴圈，並移除所有 `--count`。

我建議選第二種。這些矩陣只有 10／20 次，不值得增加一個工具鏈依賴。

## R9-05 的刪除確認

同意刪除。

這次刪除沒有構成 `WEAKENS_GUARANTEE`，因為 `claim-ref` 同時缺少：

- schema 定義；
- producer；
- consumer；
- failure trigger；
- 固定負控；
- 正控。

它只是 failure-id 列表中的字串，沒有保護任何可觀測行為。保留它反而會製造「清單裡有，所以系統有驗」的假象。

`cardinality` 也不是消失，而是回到持有 FlowSpec 與 machine catalog 的 Task 6。這是責任歸位。

## 04 Task 8 撤案

撤案正確。

計畫 04 驗 backup／restore mechanism，計畫 20 的 backup worker 擁有五分鐘排程與 release 驗收；兩層責任都有落點。硬把 scheduler 再塞進 04 會形成第二個擁有者。

## 覆蓋審清單

原五條必要，但不夠。它們主要抓「局部 task 文字與檔案是否對齊」，前八輪另外踩過四類跨邊界問題。

建議擴成十條：

1. 負控殺的是宣稱性質，還是隔壁性質。
2. 介面／enum 每個成員是否有殺手。
3. 負控每個名詞是否有已宣告主體。
4. `Run:` 的檔案、參數、plugin 與環境是否可達。
5. fence、schema、Global Constraints 是否一致。
6. **負控主體是否可達且原本合法**：不能用非法 enum 測 identity change。
7. **是否有防恆真正控**：閘不能靠拒絕所有輸入通過。
8. **引用的 claim 是否真的包含所需 predicate**：不能只驗 claim id/revision 存在。
9. **跨層組合是否形成循環、TOCTOU 或 crash gap**：receipt self-reference、release-before-commit、並行 nonce 雙花都屬此類。
10. **內容身分是否覆蓋交付鏈下一站**：source artifact、resolve、assembly、effective output 必須逐層問「下一站變了，誰會紅」。

再補一條資料庫專用子問句：

> nullable 欄位、三值邏輯、deferred constraint、並行交易與直接 SQL bypass，是否能繞過 application 層假設？

R9-07 正是這條抓出的。

這十一條比原五條更接近真正的「定案覆蓋」；I1–I11 繼續負責結構，它們不能替代這份語意清單。
tokens used
25,507
我重跑合套閘：22 份計畫、769 個 Create、190 tasks、未遷移 131，I1–I11 全綠。

## 逐條裁決

| 決議 | 裁決 | 理由 |
|---|---|---|
| R9-00 | APPROVE | 單成員 assembly policy 現在只驗可達的解析、內容綁定與封閉字彙，沒有再冒稱已驗過不存在的第二政策。 |
| R9-01 | APPROVE | MachineSpec 終於宣告 FlowSpec 要引用的 output，`require_output` 不再查一個不存在的 catalog 成員。 |
| R9-02 | APPROVE | `LocaleCatalog` 在狀態機編譯層沒有主體與必要性，刪除懸空參數比就地發明另一個權威正確。 |
| R9-03 | APPROVE | canonical digest 現在有直接 mutation；錯層的 FlowSpec 負控回到真正擁有 machine catalog 的 Task 6。 |
| R9-04 | APPROVE | closed vocabulary 與各項資源上限都有自己的越界 witness，Hypothesis 測試也取得明確檔案落點。 |
| R9-05 | APPROVE | `claim-ref` 沒有語意、消費端或負控，刪掉的是空 failure id，不是可執行保證。 |
| R9-06 | APPROVE | causal 半邊取得直接負控，fence 也與 Global Constraints 對齊。 |
| R9-07 | REJECT `WEAKENS_GUARANTEE` | 「四欄全 NULL 或全 NOT NULL」仍允許 `TRANSITION` event 四欄全 NULL，繼續繞過 composite FK。 |
| R9-08 | REJECT `NOT_TESTABLE` | 只把 `pytest-repeat` 寫進 Tech Stack 不會安裝 plugin；`--count` 仍可能是不可達命令。 |
| R9-09 | APPROVE | append-only 現在同時攔 UPDATE 與 DELETE，不再只保護一半。 |
| R9-10 | APPROVE | capacity hard stop 的「停止 ordinary admission」取得直接殺手，不再只驗不早刪。 |

## APPROVE 項目的寫入條件

### R9-01

`payload_digest` 必須明定為 payload contract/schema digest，不是某次 runtime payload bytes 的 digest。建議直接命名 `payload_contract_digest`，避免下一輪再產生語意歧義。

負控至少包含：

- transition `emits` 未宣告 output；
- output 與 trigger 的 contract digest 不同；
- 同 `output_id` 對應兩個不同 contract digest。

### R9-04

五類 guard 上限必須各有一個實際 fixture，不能只在散文中說「fixture 集」：

- depth 9
- nodes 65
- children 1 與 17
- set size 33
- facts 33

另保留既有 4,097 proof cells。每格都應確認只紅在自己的 limit predicate。

### R9-06

「欄位存在」與「存在因果」必須分開：

- root event 可以有 typed root/null causation；
- derived event 必須有可解析的 `causation_id`；
- `correlation_id` 必須維持跨流程關聯；
- 不得為通過 required-field schema 而填假的 sentinel id。

建議增加：

- `derived-event-null-causation`  
  → `derived_event_requires_cause`
- 防恆真：root event 使用明確 `ROOT_CAUSE`／nullable root 形狀仍合法。

### R9-10

hard point 不得用「全部操作一律拒絕」取得假綠。到達 hard point 後仍必須允許：

- GC／prune
- checkpoint
- archive／backup
- repair／capacity recovery
- 已開始交易的安全收束

固定負控之外補防恆真：ordinary new admission 被拒，但能解除 hard point 的 maintenance command 仍可執行。

## R9-07 最小重提修改

SQLite 官方明確規定：composite child key 任一欄為 `NULL`，就不要求存在對應 parent row；而且 SQLite 對外鍵一律按 `MATCH SIMPLE` 處理，不執行 `MATCH FULL`。[SQLite Foreign Key Support](https://www.sqlite.org/foreignkeys.html)

所以你的實測與 fable 的知識宣稱都正確。但提案的 CHECK 還少 event kind 關聯。

需要改成等價於：

```sql
CHECK (
    (
        event_kind = 'TRANSITION'
        AND machine_digest IS NOT NULL
        AND transition_id IS NOT NULL
        AND from_state IS NOT NULL
        AND to_state IS NOT NULL
    )
    OR
    (
        event_kind <> 'TRANSITION'
        AND machine_digest IS NULL
        AND transition_id IS NULL
        AND from_state IS NULL
        AND to_state IS NULL
    )
)
```

若某些非 transition event 合法攜帶 machine digest，就應拆成另一組明確欄位規則，不能使用模糊的 all-or-none。

固定負控至少要有：

- partial-NULL transition；
- all-NULL transition；
- non-transition event 偷帶完整 transition tuple；
- 合法 transition tuple；
- 合法 non-transition event。

前兩者都必須失敗，否則 `foreign-key-declared-only` 仍有旁路。

## R9-08 最小重提修改

`recorded_at` 補進 tail schema 可以保留。`pytest-repeat` 二選一：

1. 在一個明確 task 中：

   - Modify `pyproject.toml`
   - Modify `uv.lock`
   - pin `pytest-repeat`
   - 固定負控證明缺 plugin 時 gate 失敗

2. 更小的做法：完全不用 plugin，把重複次數寫進 pytest parameterization／測試內迴圈，並移除所有 `--count`。

我建議選第二種。這些矩陣只有 10／20 次，不值得增加一個工具鏈依賴。

## R9-05 的刪除確認

同意刪除。

這次刪除沒有構成 `WEAKENS_GUARANTEE`，因為 `claim-ref` 同時缺少：

- schema 定義；
- producer；
- consumer；
- failure trigger；
- 固定負控；
- 正控。

它只是 failure-id 列表中的字串，沒有保護任何可觀測行為。保留它反而會製造「清單裡有，所以系統有驗」的假象。

`cardinality` 也不是消失，而是回到持有 FlowSpec 與 machine catalog 的 Task 6。這是責任歸位。

## 04 Task 8 撤案

撤案正確。

計畫 04 驗 backup／restore mechanism，計畫 20 的 backup worker 擁有五分鐘排程與 release 驗收；兩層責任都有落點。硬把 scheduler 再塞進 04 會形成第二個擁有者。

## 覆蓋審清單

原五條必要，但不夠。它們主要抓「局部 task 文字與檔案是否對齊」，前八輪另外踩過四類跨邊界問題。

建議擴成十條：

1. 負控殺的是宣稱性質，還是隔壁性質。
2. 介面／enum 每個成員是否有殺手。
3. 負控每個名詞是否有已宣告主體。
4. `Run:` 的檔案、參數、plugin 與環境是否可達。
5. fence、schema、Global Constraints 是否一致。
6. **負控主體是否可達且原本合法**：不能用非法 enum 測 identity change。
7. **是否有防恆真正控**：閘不能靠拒絕所有輸入通過。
8. **引用的 claim 是否真的包含所需 predicate**：不能只驗 claim id/revision 存在。
9. **跨層組合是否形成循環、TOCTOU 或 crash gap**：receipt self-reference、release-before-commit、並行 nonce 雙花都屬此類。
10. **內容身分是否覆蓋交付鏈下一站**：source artifact、resolve、assembly、effective output 必須逐層問「下一站變了，誰會紅」。

再補一條資料庫專用子問句：

> nullable 欄位、三值邏輯、deferred constraint、並行交易與直接 SQL bypass，是否能繞過 application 層假設？

R9-07 正是這條抓出的。

這十一條比原五條更接近真正的「定案覆蓋」；I1–I11 繼續負責結構，它們不能替代這份語意清單。
