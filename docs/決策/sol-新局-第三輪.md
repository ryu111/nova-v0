# 新局第三輪：宣告式狀態機、權威目錄與零未決定案

## 0. 讀取邊界與總裁決

【查證】本輪只讀了《[需求：前端控制面](./需求-前端控制.md)》、《[架構草案](./架構草案.md)》、自己的《[第一輪](./sol-新局-第一輪.md)》與《[第二輪](./sol-新局-第二輪.md)》；沒有讀取既有實作、既有測試、交接、其他設計文件或遷移筆記。（來源：本輪工具讀取紀錄與題目禁令。）

【推論】總形狀定為：**三個垂直生命週期層（Work → Pursuit → Execution）＋四個橫向權威面（判準、資源、效果、知識）＋不在組合軸上的內容定址儲存與證據索引**。應用服務是進入這些權威的唯一邊界；它不是第五個權威，也不擁有領域真相。

【推論】本輪結束時未決條目數是 **0**。本文出現的「反轉條件」是日後需求改變時重開決策的客觀觸發器，不是現在把選項留著不選。

【查證】新增需求要求：流程圖由狀態機宣告生成、view 由事件流純函式重建、UI 讀者不碰狀態擁有者交易、後端額度必須帶新鮮度、分配政策要版本化、CLI 更新不得讓在途 Pursuit 靜默換指紋。（來源：[需求-前端控制.md](./需求-前端控制.md)。）

## 1. 先判決你在題目第二節的五個選擇

| 你的選擇 | 判決 | 必要的精確化 |
|---|---|---|
| SQLite single-owner／rollback | 【推論】採用，沒有理由翻案。 | 【推論】這只裁定**權威狀態庫**。可重建的尾隨事件庫是另一個讀取資料面，採一 writer＋多 reader 的 SQLite WAL；它壞了可由權威日誌重建，不會取得領域權威。 |
| 持久佇列＋父子，不做一般 DAG | 【推論】採用；拆出 Pursuit 後仍成立。 | 【推論】固定關係是 `Work 1→0..8 Pursuit 1→0..16 Execution`。Work 對子 Pursuit 做集合 fold 與選拔，這是父擁有子的 fan-out／fan-in，不是任意 child-to-child 邊、跨父依賴或一般 join。 |
| v1 只防無意洩漏，ClaimSpec 宣告 isolation capability | 【推論】採用；這正是第二輪 4.7 的建議。 | 【推論】標準名稱固定為 `COOPERATIVE_PROCESS`。任何 ClaimSpec 要求 `RESTRICTED_OS` 或 `HOSTILE_VM` 時，當前 host 必須回 `UNSUPPORTED_ISOLATION`，禁止降級執行、禁止把 skip 算綠。 |
| 雙池＋clause-level gated feedback＋揭露即燒掉 | 【推論】採用。 | 【推論】一旦輸入、expected、diff 或足以重建答案的反例被揭露，該 hidden case 立即撤銷最終裁定資格並轉 Guidance；舊 verdict 仍保留來源，但不能再授予新 candidate。 |
| endpoint 語意進 ClaimSpec | 【推論】採用，而且只寫文件或 adapter 註解不算。 | 【推論】凡會觸發外部效果的 ClaimSpec 都必填 `effect_delivery`；語言不提供 `EXACTLY_ONCE` 這個假選項。完整欄位與 v1 endpoint 值見 4.4。 |

【推論】Pursuit 拆層沒有推翻「父子而非 DAG」。它只把原來隱藏在 Work 欄位裡的搜尋生命週期升成明確 child。只有出現「一個 Pursuit 的可執行性依賴另一個 Pursuit 的指定終態」、「跨 Work join」或「任意拓撲補償」時，才命中一般 DAG 的反轉條件。

---

## 2. Q1：狀態機是資料，不是帶著狀態名稱的程式碼

### 2.1 三種資料，各自只有一種權力

【推論】狀態機來源分成三種，不准混成一個萬能 JSON：

1. 【推論】`MachineSpec` 擁有**單一權威物件**的狀態、觸發、guard、轉移、終態與輸出；它是執行時合法轉移的唯一來源。
2. 【推論】`FlowSpec` 只把多個 `MachineSpec` 的既有輸出與既有觸發接起來，宣告父子基數與跨權威訊息；它不能發明狀態或邊。
3. 【推論】`GraphIR` 是前兩者的確定性編譯產物；DOT／SVG 與 UI 都只讀它。`GraphIR` 沒有獨立編輯入口，也不進入領域寫入路徑。

【推論】這個分法守住「model 不為 view 讓步」：狀態與轉移屬於 model；跨層契約屬於組合 model；中文標籤、顏色、座標與展開方式屬於 view。MachineSpec 和領域事件裡**沒有** `x`、`y`、`color`、`progress_percent` 或 UI 專用欄位。

【查證】JSON Schema Draft 2020-12 提供 meta-schema、結構驗證與 compound schema bundling；它能驗資料形狀，不能替代 guard 語義或可達性分析。[JSON Schema Draft 2020-12](https://json-schema.org/draft/2020-12)。

### 2.2 `MachineSpec 1.0` 的完整 top-level

【推論】所有 object 一律 `additionalProperties: false`；所有持久語義 id 使用 ASCII lower-kebab／dot namespace，中文 source identifier 與翻譯不進 MachineSpec。以下欄位就是 v1，沒有自由擴充袋：

| 欄位 | 型別 | 必填 | 機械作用 |
|---|---|---:|---|
| `$schema` | absolute URI | 是 | 【推論】固定 `urn:nova:schema:machine:1`；未知 schema 直接拒絕。 |
| `spec_version` | literal `1.0.0` | 是 | 【推論】選擇編譯語義。 |
| `machine_id` | SemanticId | 是 | 【推論】例如 `work`、`pursuit`、`execution`；永不拿章節編號當 id。 |
| `revision` | integer ≥ 1 | 是 | 【推論】不可變版本；內容一 byte 改變就產生新 revision 與 digest。 |
| `supersedes` | MachineRef 或 null | 是 | 【推論】revision 1 為 null；後續 revision 明指被取代 digest，不靠「最新檔名」猜。 |
| `authority` | AuthorityId | 是 | 【推論】唯一可承諾這台 machine 終態的權威。 |
| `entity_type` | SemanticId | 是 | 【推論】事件與 repository binding 的 aggregate 型別。 |
| `initial_state` | StateId | 是 | 【推論】必須指到且只能指到一個非終態 state。 |
| `states` | `StateDef[]`，min 2 | 是 | 【推論】宣告節點與終態分類。 |
| `triggers` | `TriggerDef[]`，min 1 | 是 | 【推論】封閉觸發集合；任意字串事件不能驅動轉移。 |
| `fact_schema` | JSON Schema ref＋digest | 是 | 【推論】guard 可讀的權威事實快照；禁止 guard 自己 I/O。 |
| `guard_language` | catalog ref＋digest | 是 | 【推論】只允許有限、總函式的 boolean／enum／有界 integer predicate AST。 |
| `guards` | `GuardDef[]` | 是，可空 | 【推論】具名 pure predicates；每個 guard 附至少一個 true witness 與一個 false witness。 |
| `imports` | `MachineImport[]` | 是，可空 | 【推論】跨層 machine contract、角色與父子基數；只准引用 immutable revision＋digest。 |
| `transitions` | `TransitionDef[]`，min 1 | 是 | 【推論】唯一合法邊集合。 |
| `reason_codes` | `ReasonCodeDef[]` | 是 | 【推論】轉移原因的封閉碼表；每項含 `id` 與 `claim_ref`，自由文字只能進 CAS evidence。 |
| `invariant_claims` | ClaimRef[]，min 1 | 是 | 【推論】把此 machine 的結構／行為保證綁到可執行 ClaimSpec。 |
| `upgrade_policy` | literal `PINNED` | 是 | 【推論】既有 entity 永遠按建立時 digest 重播；啟用新 revision 不會偷改在途物件。 |

【推論】巢狀型別固定如下：

| 型別 | 必填欄位 | 規則 |
|---|---|---|
| `StateDef` | `id`, `terminal` | 【推論】`terminal=null` 表示非終態；否則為 `{outcome, class, restartable:false, claim_ref}`。終態不得有 outgoing edge；人讀標籤由 view 依 `machine_id/state_id` 翻譯。 |
| `TriggerDef` | `id`, `kind`, `payload_schema`, `payload_digest` | 【推論】`kind` 只可為 `COMMAND`、`TIMER`、`CHILD_EVENT`、`AUTHORITY_EVENT`、`RECOVERY`；payload 必須型別化。 |
| `GuardDef` | `id`, `predicate`, `true_witness`, `false_witness` | 【推論】predicate 不得包含 function name、module path、shell、clock、random 或 I/O；時間必須先成為 fact。 |
| `MachineImport` | `alias`, `machine_ref`, `relation`, `cardinality` | 【推論】`relation` 只可為 `OWNS_CHILD` 或 `OBSERVES_AUTHORITY`；v1 的 owns 關係必須是無環樹。 |
| `TransitionDef` | `id`, `from`, `on`, `guard`, `to`, `reason_code`, `emits`, `requests` | 【推論】`guard` 為 guard id 或 `ALWAYS`；`emits` 至少一個 domain transition event；`requests` 只產生 typed intent，不直接做副作用。 |
| `OutputDef` | `id`, `kind`, `payload_schema`, `payload_digest`, `target`, `claim_ref` | 【推論】`kind` 只可為 `DOMAIN_EVENT`、`CHILD_COMMAND`、`RESOURCE_INTENT`、`EFFECT_INTENT`、`KNOWLEDGE_PROPOSAL`；跨 machine 只能靠這些窄訊息。 |
| `ReasonCodeDef` | `id`, `claim_ref` | 【推論】讓每個「為什麼」都能回到 executable guarantee，而不是只有中文說明。 |

【推論】終態 `class` 固定為 `SUCCESS`、`DEPLETED`、`CANCELLED`、`FAULT`、`QUARANTINE` 五類，但各 machine 保留具體 outcome。Execution 的 `SUCCEEDED` 只屬 `SUCCESS`，仍不等於 Work 的 `SATISFIED`。

### 2.3 一份真的宣告長什麼樣

【推論】下面不是完整 Work machine，而是完整展示 schema 形狀的最小片段；真正檔案必須列完所有 state／edge，不得用省略符進 admission：

```json
{
  "$schema": "urn:nova:schema:machine:1",
  "spec_version": "1.0.0",
  "machine_id": "work",
  "revision": 1,
  "supersedes": null,
  "authority": "work",
  "entity_type": "work-item",
  "initial_state": "ready",
  "states": [
    {"id": "ready", "terminal": null},
    {"id": "running", "terminal": null},
    {"id": "satisfied",
      "terminal": {"outcome": "SATISFIED", "class": "SUCCESS", "restartable": false,
                   "claim_ref": "work.terminal.external-verdict@1#sha256:…"}},
    {"id": "exhausted",
      "terminal": {"outcome": "EXHAUSTED", "class": "DEPLETED", "restartable": false,
                   "claim_ref": "work.terminal.bounded-exhaustion@1#sha256:…"}}
  ],
  "triggers": [
    {"id": "command.start", "kind": "COMMAND",
      "payload_schema": "urn:nova:event:work-start:1", "payload_digest": "sha256:…"},
    {"id": "pursuit.verdict-observed", "kind": "CHILD_EVENT",
      "payload_schema": "urn:nova:event:pursuit-verdict:1", "payload_digest": "sha256:…"}
  ],
  "fact_schema": {"ref": "urn:nova:facts:work:1", "digest": "sha256:…"},
  "guard_language": {"ref": "urn:nova:guard-catalog:1", "digest": "sha256:…"},
  "guards": [
    {"id": "accepted-candidate-exists",
      "predicate": {"op": "GT", "left": {"fact": "eligible_candidate_count"},
                    "right": {"literal": {"type": "INT", "value": 0}}},
      "true_witness": {"eligible_candidate_count": 1},
      "false_witness": {"eligible_candidate_count": 0}}
  ],
  "imports": [
    {"alias": "search", "machine_ref": "pursuit@1#sha256:…",
      "relation": "OWNS_CHILD", "cardinality": {"min": 0, "max": 8}}
  ],
  "transitions": [
    {"id": "start-portfolio", "from": "ready", "on": "command.start", "guard": "ALWAYS",
      "to": "running", "reason_code": "work.accepted",
      "emits": [{"id": "work.started", "kind": "DOMAIN_EVENT",
                  "payload_schema": "urn:nova:event:work-started:1", "payload_digest": "sha256:…",
                  "target": "SELF", "claim_ref": "work.transition.declared@1#sha256:…"}],
      "requests": [{"id": "pursuit.create-requested", "kind": "CHILD_COMMAND",
                     "payload_schema": "urn:nova:command:pursuit-create:1", "payload_digest": "sha256:…",
                     "target": "search", "claim_ref": "work.child.cardinality@1#sha256:…"}]},
    {"id": "accept-best", "from": "running", "on": "pursuit.verdict-observed",
      "guard": "accepted-candidate-exists", "to": "satisfied",
      "reason_code": "work.best-selected",
      "emits": [{"id": "work.satisfied", "kind": "DOMAIN_EVENT",
                  "payload_schema": "urn:nova:event:work-satisfied:1", "payload_digest": "sha256:…",
                  "target": "SELF", "claim_ref": "work.terminal.external-verdict@1#sha256:…"}],
      "requests": []}
  ],
  "reason_codes": [
    {"id": "work.accepted", "claim_ref": "work.transition.declared@1#sha256:…"},
    {"id": "work.best-selected", "claim_ref": "work.terminal.external-verdict@1#sha256:…"}
  ],
  "invariant_claims": [
    "work.transition.declared@1#sha256:…",
    "work.terminal.external-verdict@1#sha256:…"
  ],
  "upgrade_policy": "PINNED"
}
```

【推論】同一個 `(from, trigger)` 若有多條 guarded edge，guard domain 必須可由有限 enum／有界整數分割（guard 讀到的每個 integer fact 都必須在 `fact_schema` 有 min／max），compiler 必須證明**互斥且完備**；不接受靠陣列順序偷偷決勝。做不到這項證明的需求必須先被改寫成一個由權威產生的 typed decision fact，再讓 machine 對該 enum 分支。

### 2.4 `FlowSpec 1.0` 與跨三層的表示

【推論】`FlowSpec` top-level 固定為 `$schema`、`spec_version`、`flow_id`、`revision`、`supersedes`、`root`、`participants[]`、`bindings[]`、`invariant_claims[]`。participant 含 `alias`、`machine_ref`、`axis`、`parent_alias`、`cardinality`；binding 含 `from_output`、`to_trigger`、`delivery` 與 payload digest equality。

【推論】三層組合檔的核心資料是：

```json
{
  "$schema": "urn:nova:schema:flow:1",
  "spec_version": "1.0.0",
  "flow_id": "software-engineering-work",
  "revision": 1,
  "supersedes": null,
  "root": "work",
  "participants": [
    {"alias": "work", "machine_ref": "work@1#sha256:…", "axis": "LIFECYCLE",
     "parent_alias": null, "cardinality": {"min": 1, "max": 1}},
    {"alias": "pursuit", "machine_ref": "pursuit@1#sha256:…", "axis": "LIFECYCLE",
     "parent_alias": "work", "cardinality": {"min": 0, "max": 8}},
    {"alias": "execution", "machine_ref": "execution@1#sha256:…", "axis": "LIFECYCLE",
     "parent_alias": "pursuit", "cardinality": {"min": 0, "max": 16}},
    {"alias": "evaluation", "machine_ref": "evaluation@1#sha256:…", "axis": "AUTHORITY",
     "parent_alias": null, "cardinality": {"min": 0, "max": 128}}
  ],
  "bindings": [
    {"from_output": "work:pursuit.create-requested", "to_trigger": "pursuit:command.create",
     "delivery": "DURABLE_COMMAND", "payload_digest": "sha256:…"},
    {"from_output": "pursuit:execution.start-requested", "to_trigger": "execution:command.start",
     "delivery": "DURABLE_COMMAND", "payload_digest": "sha256:…"},
    {"from_output": "execution:execution.terminal", "to_trigger": "pursuit:execution.terminal-observed",
     "delivery": "DURABLE_EVENT", "payload_digest": "sha256:…"},
    {"from_output": "evaluation:verdict.recorded", "to_trigger": "work:pursuit.verdict-observed",
     "delivery": "DURABLE_EVENT", "payload_digest": "sha256:…"}
  ],
  "invariant_claims": [
    "flow.parent-child.no-dag@1#sha256:…",
    "view.fold.three-layers@1#sha256:…"
  ]
}
```

【推論】一條跨層「流動」不會假裝成跨三個 authority 的原子狀態跳躍。圖上：cluster／泳道代表 machine；實線代表 machine 內 transition；虛線訊息節點代表 durable command／event binding。Work 發 child command、Pursuit 自己轉；Execution 結束後發 event、Pursuit 自己轉。權威邊界因而在圖上可見。

【推論】靜態圖只畫每種狀態一次；執行時每個 Work／Pursuit／Execution 是一枚帶 entity id 的 token，放在對應 template node 上。多個 Pursuit 或 Execution 同時活著時，節點顯示 token 數與終態分布，展開後按 parent id 分列。UI 不會為每個 instance 重新發明一份 machine。

### 2.5 圖的確定性生成

【推論】生成管線固定為：

```text
MachineSpec bytes
  → JSON Schema 驗證
  → digest／reference resolution
  → machine lint
FlowSpec bytes
  → cross-reference lint
  → canonical GraphIR（穩定 node_id／edge_id／cluster_id）
GraphIR + locale catalog
  → Graphviz DOT（純生成；catalog 只供文字，不得增刪 node／edge）
  → SVG（每個元素保留 data-node-id／data-edge-id／machine-bundle-digest／locale-digest）
```

【推論】`GraphIR` 與 SVG 都是 build artifact，不是 source；不得手改、不得讓人提交一張替代圖。CI 從 source specs 重生兩次，要求 GraphIR canonical bytes 與 digest 相同，並檢查 SVG 內嵌的 machine bundle／locale digests。改翻譯可以改 layout，但不能改 node／edge 集合；renderer layout 變了不影響語義，MachineSpec／FlowSpec 改變才是領域規格變更。

【查證】Graphviz 的 `charset` 預設是 UTF-8，可以接收中文 label；輸入 encoding 與 charset 不符會產生異常輸出。[Graphviz charset](https://graphviz.org/docs/attrs/charset/)。

### 2.6 同一份宣告產生的 lint，能證明與不能證明的東西

【推論】admission 時一次跑完以下 lint；任何一項失敗，整個 machine／flow revision 不得 ACTIVE：

1. 【推論】schema 完整、未知欄位拒絕、所有 id 在自己的 namespace 唯一。
2. 【推論】`initial_state`、所有 `from/to/on/guard/import/output/trigger` 引用存在，payload schema digest 完全相等；因此沒有懸空邊。
3. 【推論】從 initial 做 forward DFS，所有 state 都可達；不可達 state 是死文件。
4. 【推論】每個非終態 out-degree ≥ 1；每個終態 out-degree = 0，且 `restartable=false`。
5. 【推論】從所有終態做 reverse DFS，必須涵蓋所有 state；因此每個 state 在**忽略環境是否真的提供某個 trigger**時，結構上都有終態路徑。
6. 【推論】同 `(state, trigger)` 的 guards 互斥且完備；每條 guard 的 true／false witness 都由 interpreter 實際跑過。
7. 【推論】`OWNS_CHILD` imports 無環，基數不超 envelope；FlowSpec 不得出現 child-to-child 或跨 root dependency。
8. 【推論】每條 transition 至少 emit 一個帶 transition id 的 domain event；每個 reason code、terminal outcome、event schema 都有 ClaimSpec reference。

【推論】第 5 項只是**結構可達性**，不是「現實世界一定會送來 trigger」的 liveness 證明。一定停止仍由可單調耗盡的 deadline／attempt／spend reservation 與 bounded-liveness ClaimSpec 證明；把 reverse DFS 宣稱成活性證明是在造假。

### 2.7 執行時禁止未宣告轉移：三道硬閘

【推論】第一道是 pure engine：command 帶 `entity_id`、`expected_aggregate_seq`、`trigger_id` 與 typed payload；engine 從該 entity 已釘住的 machine digest 找唯一 edge。找不到回 `ILLEGAL_TRANSITION`，找到多條代表 spec admission 有 bug，回 `MACHINE_AMBIGUOUS` 並 quarantine，兩者都不寫事件。

【推論】第二道是 transaction invariant：state owner 在同一筆權威交易內 append event 並更新可重建的 head cache。事件必填 `machine_digest`、`transition_id`、`from_state`、`to_state`、`aggregate_seq`；資料庫以 `(machine_digest, transition_id, from_state, to_state)` composite foreign key 指向 admitted transition catalog。就算 application bug 直接組 event，非法 tuple 仍提交不了。

【推論】第三道是 topology：只有 state-owner process 持有權威 SQLite 路徑與 writer connection；worker、evaluator、CLI、HTTP 與 UI 只能送 application command。依賴檢查禁止領域／介面 import SQLite adapter，啟動測試故意加一條旁路時必須轉紅。

【推論】權威日誌是唯一歷史；`aggregate_head` 只是 transaction-local optimistic-concurrency cache，可以整張刪掉後由日誌 fold 重建。UI 永不讀它。每個 entity 永久釘住建立時的 machine digest；新 revision 只影響新 entity，舊 entity 若要升版必須走有來源／目標 digest 的顯式 migration event，且 migration 自己有正負控。

### 2.8 領域事件 envelope 與獨立尾隨

【推論】事件 schema 用 tagged union；`TRANSITION`、`OBSERVATION`、`LEDGER`、`EFFECT` 共用下列 envelope，但只有 `TRANSITION` 必填 machine transition 區塊：

```text
event_id              UUIDv7，重送去重鍵
global_seq            state owner 單調配置的 uint64，唯一游標
event_kind            TRANSITION | INTENT | LEDGER   ← 2026-08-28 取代原四成員
event_type/version     語義事件型別與 schema version
aggregate_type/id/seq  aggregate 內 optimistic ordering
work_id/pursuit_id/execution_id  可空的因果 lineage，不是 UI join 欄位
machine_id/revision/digest       TRANSITION 必填
transition_id/from_state/to_state TRANSITION 必填
occurred_at/recorded_at          deadline 語義時間／權威落盤時間
causation_id/correlation_id      命令與跨層因果
actor_type/actor_id              誰提出，不代表誰有驗收權
reason_code                      封閉碼；必要的細節進 evidence
payload_schema/payload_digest    inline ≤64 KiB，否則只放 CAS ref
evidence_refs[]/ledger_refs[]    只引用不可變紀錄
```

【推論】這些欄位各自由重播、樂觀併發、期限、核銷、溯源或權威邊界證成；事件裡不放畫面座標、顏色、已格式化句子、百分比或「目前總數」之類 view 欄位。

【推論】儲存拓撲固定為兩個 SQLite 檔：

```text
權威狀態.sqlite3   single-owner／single connection／rollback／FULL
尾隨事件.sqlite3   rebuildable replica／single publisher／WAL／read-only tailers
```

【推論】state owner 在權威交易中先配置 `global_seq` 並 append 原始 event；commit 後 publisher 按 seq 把**完全相同的 envelope**冪等複製到尾隨庫。publisher crash 就從最後 durable cursor 補送；尾隨庫以 `global_seq UNIQUE` 去重。它可以整檔砍掉重建，因此不是第二份領域真相。

【查證】SQLite WAL 允許 readers 與單一 writer 同時進行，但仍只有一個 writer，並額外需要 checkpoint；這正符合「可重建、單 publisher、多 tailer」而不是權威 command store 的 workload。[SQLite WAL](https://sqlite.org/wal.html)。

【推論】UI、CLI subscription 與 HTTP stream server 只開尾隨庫的 read-only connection，永遠不開權威庫。批次 catch-up 用 `after_global_seq`，live tail 用 SSE，SSE 的 `id` 就是 `global_seq`；相同事件可以 at-least-once 重送，client reducer 以 event id／seq 冪等 fold。

【查證】WHATWG Server-Sent Events 定義 `id` 與重連時的 `Last-Event-ID`，正好提供 transport-level 的續讀線索；它本身不保證 server 有耐久歷史，所以耐久性仍由本系統尾隨庫提供。[HTML Standard: Server-sent events](https://html.spec.whatwg.org/dev/server-sent-events.html)。

【推論】發布 SLO 定為事件權威 commit 後 p95 1 秒內可讀；SSE 每 5 秒送只含 tail cursor 的 transport heartbeat。state owner 每 10 秒產生有領域理由的 `component.heartbeat` operational event，30 秒未更新時 UI 以本地 `now` 標成 STALE；publisher 一旦斷掉，這個 event 也不會抵達，所以 UI 不會把「SSE socket 還活著」誤當「資料仍新鮮」。

【推論】v1 **不 compact／delete 領域事件**；第二輪的 90 天是最低可用保證，不是第 91 天自動清除命令。raw executor logs／CAS payload 仍可按 30／365 天各自變 `GONE`，但 event envelope 與 digest 留著。1,000 個非終態 Work 名額固定保留 1 個給 maintenance；權威狀態庫或尾隨庫到 10 GiB review point 時，系統先用該 slot 建立維護 Work，再暫停普通新 Work。在新的 compaction ClaimSpec 通過前，不拿「節省空間」當理由製造只有 head、沒有 history 的第二份真相。

【推論】這是對第二輪 envelope 的一處必要收緊：若把「operational events 90 天」解讀成第 91 天硬刪，它會直接違反本輪已接受的「日誌是唯一來源、位置只由 fold 得到」。本輪把它定義成**至少 90 天且 v1 不自動刪**；不是把 data retention 留成未選選項。

【推論】event protocol 仍保留 typed `CURSOR_EXPIRED(retention_floor)`，供日後有版本的 retention policy 或從有限備份還原時使用；v1 正常運行的 floor 是 0。UI 畫面是 `fold(GraphBundle(machine digests), events[0..cursor], now)`；`now` 只用來把過期觀測標成 STALE，不向領域補查詢。

---

## 3. Q2：定案目錄樹

### 3.1 切目錄的主規則

【推論】第一切按**權威與生命週期**，因為這決定誰能寫、誰能宣告終態、崩潰後誰恢復；第二切才按 change axis，把同一權威內會一起改的 machine、model、decision、port 與近身測試放在一起。不能為了「常一起改」把判準、資源、效果與 Work 混成一個 feature folder，那會把不同的筆塞回同一個權限邊界。

【推論】跨權威必然一起改的東西以 immutable schema／semantic id／digest 相接，並由 impact manifest 列出受影響測試；**共同改動不等於共同所有權**。這是本樹拒絕按 controller／service／repository 水平大桶切分的原因。

【推論】後端採 CPython 3.14 package，前端採 TypeScript＋原生 Web Components＋SVG，build 用 Vite，流程 layout 用固定版本 Graphviz。UI 沒有自己的領域查詢 client，只有 application command client、GraphBundle client 與 event-stream client。框架可替換性由這三個協定邊界承載，React／Vue 不進 v1。

### 3.2 Source tree（規格到最小職責檔案）

【推論】下列是定案的 source tree。所有 Python package 都有空的 `__init__.py`，樹中省略重複列出；`產物/`、cache、SQLite 與 candidate workspace 不進 Git。

```text
.
├── pyproject.toml                         — Python 版本、依賴、pytest discovery 與所有工具入口。
├── uv.lock                                — Python dependency 的完整可重現鎖定。
├── .python-version                        — 固定 CPython 3.14 minor line。
│
├── 規格/                                  — 所有可執行宣告的 source；不含 runtime verdict 或 mutable status。
│   ├── 目錄.json                           — 列出每份 ACTIVE bootstrap spec 的 semantic id、revision、path 與 digest。
│   ├── 語言/                               — 跨權威宣告語言的 meta-schema；改語言才動這裡。
│   │   ├── ClaimSpec.schema.json           — ClaimSpec v0 的 Draft 2020-12 結構與 effect_delivery 擴充。
│   │   ├── 狀態機.schema.json               — MachineSpec 1.0 的結構封閉集合。
│   │   ├── 組合流程.schema.json             — FlowSpec 1.0 與跨 machine binding 規則。
│   │   ├── 狀態機遷移.schema.json           — source／target digest、state mapping、precondition 與正負控引用。
│   │   ├── 事件.schema.json                 — 領域事件 tagged-union envelope。
│   │   ├── 綁定清單.schema.json             — subject binding slot 到實作 capability 的 digest 綁定。
│   │   ├── 隔離能力.schema.json             — IsolationRequirement／IsolationOffer 與 subset 語義。
│   │   ├── 後端能力.schema.json             — 執行、額度觀測、固定版本更新與 fingerprint capability manifest。
│   │   └── 效果契約.schema.json             — endpoint operation、交付語意、idempotency key 與 receipt schema。
│   ├── 執行/                               — Execution 生命週期的宣告與保證。
│   │   ├── 執行.machine.json                — Execution 的狀態、外部限額終態與 backend observation 觸發。
│   │   └── 保證/
│   │       ├── 外部時間上限.claim.json       — 第一份 repo-owned 行為檔；外部 kill＋typed timeout＋正負控。
│   │       ├── 外部回合上限.claim.json       — 回合耗盡不受 executor 自報影響。
│   │       ├── 外部花費上限.claim.json       — 先 reserve、拒絕超支、settle 不越 reserve。
│   │       └── 型別化終態.claim.json         — supervisor 與 backend fault 不被壓成普通失敗。
│   ├── 追求/                               — Pursuit 搜尋生命週期與獨立性宣告。
│   │   ├── 追求.machine.json                — pause／resume、evaluation loop、submitted／exhausted 終態。
│   │   └── 保證/
│   │       ├── 有界反覆.claim.json           — Execution 次數／總成本耗盡使 Pursuit 必停。
│   │       └── 獨立證據面.claim.json         — 平行 Pursuit 的 workspace、evidence scope 與 lineage 不互踩。
│   ├── 工作/                               — Work portfolio、選拔與全域終止宣告。
│   │   ├── 工作.machine.json                — Work 的 child portfolio、selection 與封閉終態。
│   │   ├── 最佳截止前.policy.json           — BEST_BEFORE_DEADLINE 的確定停止與 deterministic ranking 規則。
│   │   └── 保證/
│   │       ├── 崩潰重建.claim.json           — 全程序 SIGKILL 後只靠持久事件恢復非終態工作。
│   │       ├── 備份還原.claim.json           — host-loss RPO 5 分鐘、RTO 30 分鐘與 CAS inventory 完整性。
│   │       ├── 父子非任意圖.claim.json       — 子終態不越權終結父、禁止 child-to-child dependency。
│   │       └── 自我維護提案.claim.json       — health fault 只能產生有證據的維護 Work，不得自行改 production。
│   ├── 判準/                               — 判準面兩支筆的 machine 與 feedback／隔離保證。
│   │   ├── 判準版本.machine.json            — immutable CriterionVersion 的 proposed／active／superseded 生命週期。
│   │   ├── 評估.machine.json                — Evaluation 的 prepared／running／verdict／harness-fault 生命週期。
│   │   ├── 雙測試池.policy.json             — guidance／sealed 分池、query cap、clause reducer、揭露燒毀規則。
│   │   └── 保證/
│   │       ├── 判準內容隔離.claim.json       — COOPERATIVE_PROCESS 能力與 sentinel 無意洩漏負控。
│   │       ├── 回饋降維.claim.json           — raw repr／stack／expected 不穿過 reducer。
│   │       └── 揭露即撤銷.claim.json         — revealed case 不再能授予 final verdict。
│   ├── 資源/                               — 預算、供應商額度觀測與後端分配政策。
│   │   ├── 資源保留.machine.json            — requested／reserved／settled／released／denied 狀態。
│   │   ├── 初始後端分配.policy.json          — v1 basis-point soft weights 的 immutable bootstrap version。
│   │   ├── 初始計價.policy.json              — backend usage units 到最壞成本的 immutable RateCardVersion。
│   │   └── 保證/
│   │       ├── 先保留後花費.claim.json       — 所有付費點都先 reserve。
│   │       ├── 後端成本一致.claim.json       — 每個 backend 以同一 reserve／settle contract 核銷。
│   │       ├── 額度缺席保守.claim.json       — missing／stale quota 不得當充足。
│   │       └── 政策版本釘住.claim.json       — 在途 Work 不因啟用新 ratio policy 漂移。
│   ├── 效果/                               — effect intent、relay 與 endpoint delivery 的宣告。
│   │   ├── 效果意圖.machine.json            — pending／leased／delivered／abandoned／uncertain 狀態。
│   │   ├── 後端更新.machine.json            — 效果面擁有的 backend drain／update／verify／quarantine phase。
│   │   └── 保證/
│   │       ├── 外送匣原子性.claim.json       — 領域事件與 effect intent 同一權威交易落盤。
│   │       ├── 至少一次重送.claim.json       — crash gap 可重送且目的端以固定 key 收斂。
│   │       └── 後端更新不偷換.claim.json     — 進行中 Execution 排空且 Pursuit fingerprint 不漂移。
│   ├── 知識/                               — KnowledgeAssertion 的准入、過期、撤銷與快照宣告。
│   │   ├── 知識主張.machine.json            — proposed／active／review-required／expired／revoked／superseded。
│   │   └── 保證/
│   │       ├── 來源與撤銷.claim.json         — 來源撤銷沿 derivation 傳播污染。
│   │       └── 快照可重播.claim.json         — 相同 snapshot digest 永遠解析到相同 assertion revisions。
│   ├── 組合/                               — 只連接已宣告 machine output／trigger 的跨層流程。
│   │   ├── 軟體工程工作.flow.json           — Work→Pursuit→Execution＋evaluation 的主組合圖。
│   │   ├── 後端更新.flow.json               — 更新 Work、效果 relay、能力指紋與 Pursuit interlock 組合圖。
│   │   └── 自我維護.flow.json               — health observation→evidence→maintenance proposal→普通 Work 的流向。
│   └── 介面/                               — application boundary 與純事件 view 的 wire contracts。
│       ├── 應用服務.openapi.yaml            — CLI gateway／HTTP／前端共用命令與錯誤協定。
│       ├── 事件流.schema.json               — catch-up／SSE data、cursor、heartbeat 與 CURSOR_EXPIRED。
│       ├── 圖形交換.schema.json             — canonical GraphIR 與 machine bundle digest。
│       └── 保證/
│           ├── 視圖純歸約.claim.json         — view 只能由 GraphBundle＋events＋now 重建。
│           └── 事件流獨立.claim.json         — UI 長讀不開權威狀態交易。
│
├── nova/                                  — 後端 Python package；production code 不含可編輯規格複本。
│   ├── 核心/                               — 所有內層可共用、但不含業務決策的值型別。
│   │   ├── 識別.py                         — SemanticId、UUIDv7、aggregate sequence 與 idempotency key 型別。
│   │   ├── 摘要.py                         — canonical JSON 與 SHA-256 content reference。
│   │   ├── 時間.py                         — wall／monotonic time value；實際 clock 由 port 注入。
│   │   ├── 事件.py                         — typed event envelope 與 schema reference。
│   │   ├── 錯誤.py                         — 全系統封閉 failure union，禁止裸字串失敗。
│   │   └── test_值型別.py                  — id／digest／時間／錯誤的 unit 與 property tests。
│   ├── 狀態機/                             — 不知道 Work 語義的 generic compiler／interpreter。
│   │   ├── 模型.py                         — MachineSpec／FlowSpec／GraphIR immutable typed model。
│   │   ├── 載入.py                         — schema 驗證、canonicalization、digest 與 reference resolution。
│   │   ├── 檢查.py                         — dangling／reachability／terminal／guard／cross-ref lints。
│   │   ├── 編譯.py                         — spec 到 immutable MachinePlan／GraphIR。
│   │   ├── 執行.py                         — `(state, trigger, facts) → transition | typed error` 總函式。
│   │   ├── 遷移.py                         — 顯式 MachineMigration plan；沒有 implicit latest-version upgrade。
│   │   ├── 組圖.py                         — GraphIR 到 DOT，並附穩定 data ids 與 bundle digest。
│   │   ├── test_檢查.py                    — 每項 lint 的正例與一個固定反例。
│   │   └── test_執行.py                    — 未宣告／歧義／終態轉移必拒絕。
│   ├── 領域/                               — 三個垂直生命週期；高層只看下一層公開契約。
│   │   ├── 執行/
│   │   │   ├── 公開契約.py                 — Execution command、result、backend port 與 terminal union。
│   │   │   ├── 模型.py                     — Execution aggregate 與 machine binding。
│   │   │   ├── 決策.py                     — 外部 limit、supervisor observation 與 terminal decision。
│   │   │   ├── 端口.py                     — resource gate、workspace、backend、event append 的 consumer-owned ports。
│   │   │   ├── test_決策.py                — backend 自報完成／延長期限不得越權。
│   │   │   └── test_重播.py                — event fold 與 head rebuild 等價。
│   │   ├── 追求/
│   │   │   ├── 公開契約.py                 — Pursuit command／checkpoint／candidate／terminal union。
│   │   │   ├── 模型.py                     — Pursuit aggregate、identity manifest 與 pinned fingerprint requirement。
│   │   │   ├── 決策.py                     — attempt loop、pause／resume、evaluation feedback 與停止。
│   │   │   ├── 獨立性.py                   — evidence scope、workspace、model／prompt lineage 的可驗 independence score。
│   │   │   ├── 端口.py                     — Execution launcher、evaluation、budget slice 的 consumer ports。
│   │   │   └── test_決策.py                — child terminal 不終結 Work、換後端保留 lineage。
│   │   └── 工作/
│   │       ├── 公開契約.py                 — Work command／portfolio／selection／terminal union。
│   │       ├── 模型.py                     — Work aggregate、policy digests、child set 與 deadline。
│   │       ├── 決策.py                     — child fan-out、聚合、取消與封閉終態。
│   │       ├── 選拔.py                     — BEST_BEFORE_DEADLINE deterministic candidate ranking。
│   │       ├── 維護提案.py                 — 系統 fault evidence 到普通 Work proposal；沒有直接修復權。
│   │       ├── 端口.py                     — Pursuit coordinator、criterion、effect 與 knowledge snapshot ports。
│   │       ├── test_選拔.py                — deadline／全終態／無合格候選的精確結果。
│   │       └── test_決策.py                — 一個 Pursuit 結束不封閉 Work。
│   ├── 權威/                               — 四個橫向面；彼此不能代寫，應用服務負責編排。
│   │   ├── 判準/
│   │   │   ├── 定義.py                     — CriterionVersion admission、supersede 與 sealed/guidance membership。
│   │   │   ├── 評估.py                     — candidate×criterion×runner 產生 EvidenceRecord／Verdict。
│   │   │   ├── 保證規格模型.py             — ClaimSpec、TestPlan、control 與 typed result。
│   │   │   ├── 保證規格編譯.py             — 封閉 primitive catalog 的確定性 compiler。
│   │   │   ├── 保證規格執行.py             — 外部框架 adapter 之前的 typed plan interpreter。
│   │   │   ├── 回饋閘.py                   — raw evidence 到固定 clause bucket，並執行洩漏預算。
│   │   │   ├── 隔離協商.py                 — requirement subset offer；不足只回 UNSUPPORTED_ISOLATION。
│   │   │   ├── test_分權.py                — evaluator 更新 criterion 的反例必被拒。
│   │   │   └── test_保證規格語言.py        — meta-schema、正控、負控、錯誤分類與 deterministic digest。
│   │   ├── 資源/
│   │   │   ├── 預算帳.py                   — authoritative reserve／settle／release ledger。
│   │   │   ├── 計價.py                     — immutable rate card、usage normalization 與 worst-case reservation。
│   │   │   ├── 額度觀測.py                 — provider remaining quota 的 timestamp／valid-until／UNKNOWN。
│   │   │   ├── 分配政策.py                 — immutable 10,000 basis-point weights 與 Work pinning。
│   │   │   ├── 資格閘.py                   — 預算、額度、update state、capability、isolation、model 的 live hard gate。
│   │   │   ├── 加權排程.py                 — 每 policy revision 的 deterministic deficit round-robin。
│   │   │   └── test_資源.py                — 超支、stale quota、policy drift 與 weight-zero 反例。
│   │   ├── 效果/
│   │   │   ├── 意圖.py                     — domain transaction 內建立 immutable effect intent。
│   │   │   ├── 交付.py                     — at-least／at-most state decision，不執行 endpoint I/O。
│   │   │   ├── 回執.py                     — receipt／postcondition／uncertain outcome 的 append-only record。
│   │   │   └── test_語意.py                — send 前後 crash gap 的 duplicate／loss matrix。
│   │   └── 知識/
│   │       ├── 主張.py                     — KnowledgeAssertion immutable revision 與 admission state。
│   │       ├── 准入.py                     — provenance、TTL、taint、revocation propagation 決策。
│   │       ├── 檢索.py                     — scope／source／tag 的 deterministic query policy；結果再封成 snapshot。
│   │       ├── 快照.py                     — assertion revisions 到 deterministic KnowledgeSnapshot digest。
│   │       └── test_治理.py                — executor 只能 propose、二階衍生撤銷與 snapshot replay。
│   ├── 內容庫/                             — CAS 的 domain-neutral contract；不判斷內容是否可信。
│   │   ├── 參照.py                         — algorithm／digest／size／media type value object。
│   │   ├── 端口.py                         — put／get／verify／pin／garbage-candidate protocol。
│   │   └── test_契約.py                    — 相同 bytes 同 ref、不同 bytes 不碰撞、缺 blob typed error。
│   ├── 證據庫/                             — append-only EvidenceRecord contract；不是第五個 authority。
│   │   ├── 紀錄.py                         — producer、method、subject、criterion、time、visibility 與 blob refs。
│   │   ├── 端口.py                         — append／按 immutable id 取回；沒有 update API。
│   │   └── test_不可覆寫.py                — 更正只能新增 record。
│   ├── 應用/                               — CLI／program API／HTTP／UI 唯一共用的 use-case boundary。
│   │   ├── 邊界.py                         — `execute(command)`、`subscribe(after)`、`get_graph_bundle(digest)` 三類 public API。
│   │   ├── 命令.py                         — typed command union 與 idempotency envelope。
│   │   ├── 工作單元.py                     — state owner transaction port；不暴露 SQL／repository 給 client。
│   │   ├── 排程.py                         — 編排垂直層與四權威，不自行宣告終態。
│   │   ├── 處理/
│   │   │   ├── 建立工作.py                 — 建立 Work 並釘 criterion／knowledge／allocation／machine digests。
│   │   │   ├── 建立維護工作.py             — admit 有 evidence 的 maintenance proposal 為普通 Work。
│   │   │   ├── 控制追求.py                 — pause／resume／cancel 的單一路徑。
│   │   │   ├── 調整後端比例.py             — admit 新 immutable policy；只影響新 Work。
│   │   │   └── 要求後端更新.py             — 建立 backend-update Work，不直接跑 package manager。
│   │   ├── 訂閱事件.py                     — 對事件 tail port 的 catch-up＋live abstraction。
│   │   ├── 規格服務.py                     — 只按 digest 供應 immutable GraphBundle／public schema。
│   │   └── test_邊界.py                    — 所有 client command 得到相同 decision／error／event。
│   ├── 基礎設施/                           — domain ports 的可替換實作；只有這裡碰 DB、程序、檔案與網路。
│   │   ├── 狀態庫/sqlite/
│   │   │   ├── 擁有者.py                   — single process／connection command loop、backpressure 與 fencing。
│   │   │   ├── 工作單元.py                 — transaction、event append、head cache 與 repositories。
│   │   │   ├── 機器目錄.py                 — admitted machine／transition composite-FK catalog。
│   │   │   ├── 證據索引.py                 — append-only EvidenceRecord metadata tables。
│   │   │   └── 遷移/
│   │   │       ├── 0001_事件與機器目錄.sql  — authoritative journal、spec catalog、head cache。
│   │   │       ├── 0002_三層生命週期.sql    — Work／Pursuit／Execution aggregate metadata 與 lease。
│   │   │       ├── 0003_四權威.sql          — criterion／resource／effect／knowledge ledgers。
│   │   │       └── 0004_外送匣與證據.sql    — effect outbox 與 append-only evidence index。
│   │   ├── 事件流/sqlite/
│   │   │   ├── 發布器.py                   — 從 state owner API 按 global_seq 冪等複製 committed envelope。
│   │   │   ├── 尾隨庫.py                   — WAL append、range read、retention floor 與 read-only tail port。
│   │   │   └── 遷移/0001_尾隨事件.sql       — global_seq primary key、event bytes、digest 與 publisher metadata。
│   │   ├── 內容庫/檔案系統.py              — blob-first、atomic rename、sha256 分層路徑與 verify。
│   │   ├── 知識索引/sqlite.py              — 由 ACTIVE assertion events 重建的查找索引；可砍，不擁有 admission state。
│   │   ├── 備份/
│   │   │   ├── 清單.py                     — 綁定 state snapshot、event tail cursor 與 retained CAS refs 的 backup manifest。
│   │   │   ├── 建立.py                     — 經 state owner 取得一致 checkpoint，複製 DB／CAS 並驗 digest。
│   │   │   └── 還原.py                     — 只向空資料根還原、驗 inventory 後才允許 state owner 啟動。
│   │   ├── 裁定執行/
│   │   │   ├── 程序隔離.py                 — COOPERATIVE_PROCESS workspace／env／FD／process-tree cleanup。
│   │   │   ├── 原語.py                     — trusted timer、process probe、typed observer primitive implementations。
│   │   │   └── 外部測試框架.py             — 將 immutable TestPlan 註冊成 actual／positive／negative cases。
│   │   ├── 效果轉送/
│   │   │   ├── relay.py                    — lease intent、按語意送達、記 receipt、crash 後重掃。
│   │   │   └── test_崩潰間隙.py            — before-send／after-send-before-receipt 的精確 delivery 行為。
│   │   └── 系統/                           — production clock、process supervisor、filesystem 與 health observation。
│   │       ├── 時鐘.py                     — trusted wall／monotonic clock adapter。
│   │       └── 健康.py                     — 把 component heartbeat／fault 轉成 typed observation event。
│   ├── 介接/                               — 外部 executor／endpoint plugin；每個供應商能力放同一 folder。
│   │   ├── 執行者後端/
│   │   │   ├── 共用/
│   │   │   │   ├── manifest.py             — capability／fingerprint／quota／update 的共同 manifest model。
│   │   │   │   └── 程序監督.py             — CLI argv、stdout cap、process group 與 cancellation adapter helper。
│   │   │   ├── claude_agent_sdk/
│   │   │   │   ├── manifest.py             — Claude SDK 可提供的精確 capabilities 與版本 fingerprint。
│   │   │   │   ├── 執行.py                 — SDK observation 到 Execution backend protocol。
│   │   │   │   ├── 額度.py                 — 可取得時產生 timestamped quota observation。
│   │   │   │   └── test_契約.py            — 共用 backend contract suite。
│   │   │   ├── codex_cli/
│   │   │   │   ├── manifest.py             — Codex CLI capabilities、model list 與 update support。
│   │   │   │   ├── 執行.py                 — argv adapter；不解析自由 shell string。
│   │   │   │   ├── 額度.py                 — quota observer 或明確 UNKNOWN。
│   │   │   │   ├── 更新.py                 — 固定 target version 的 convergent install＋fingerprint verify。
│   │   │   │   └── test_契約.py            — run／quota／update／idempotency contract suite。
│   │   │   ├── agy_cli/                    — 與 codex_cli 同五個最小職責檔案。
│   │   │   ├── 本地模型/                   — manifest、執行、test_契約；quota 宣告 NOT_APPLICABLE。
│   │   │   └── 重播器/                     — manifest、執行、test_契約；純函式、零外部花費。
│   │   └── 效果端點/
│   │       └── 後端更新.py                 — effect relay 到指定 backend 的 update capability，不含 policy decision。
│   ├── 介面/                               — 純協定轉換；只可 import 應用.邊界。
│   │   ├── 命令列/main.py                  — `nova` ASCII executable 的 argv／exit-code adapter。
│   │   ├── 程式介面/api.py                 — Python caller 的 typed facade。
│   │   └── HTTP/
│   │       ├── server.py                   — command、GraphBundle 與 event catch-up route wiring。
│   │       ├── 事件串流.py                 — Last-Event-ID、heartbeat、backpressure 與 typed cursor errors。
│   │       └── test_協定.py                — OpenAPI／event schema conformance，禁止 domain bypass。
│   └── 啟動/                               — 唯一允許 import concrete infrastructure 的 composition roots。
│       ├── 狀態擁有者.py                   — 組裝 state owner process。
│       ├── 應用服務.py                     — 組裝 HTTP／program boundary 與 read-only event tail。
│       ├── 效果轉送.py                     — 組裝 outbox relay process。
│       ├── 備份.py                         — 組裝五分鐘週期的 backup worker 與 maintenance events。
│       └── evaluator.py                    — 組裝 ClaimSpec compiler、isolation offer 與 trusted observers。
│
├── 前端/                                  — 可整個替換的 visual-log client；沒有 domain repository。
│   ├── package.json                        — TypeScript、Vite、test 與 GraphBundle schema validator scripts。
│   ├── package-lock.json                   — npm dependency lock。
│   ├── tsconfig.json                       — strict mode、UTF-8 source 與 build target。
│   ├── vite.config.ts                      — build／dev-server；不代理任何私有 domain query。
│   ├── index.html                          — 唯一 browser shell。
│   └── src/
│       ├── 入口.ts                         — 組裝 Web Components、command client、GraphBundle 與 event stream。
│       ├── 應用服務客戶端.ts               — 只實作 OpenAPI commands 與 immutable spec fetch。
│       ├── 事件流/
│       │   ├── 連線.ts                     — catch-up 後以 EventSource／Last-Event-ID 續讀。
│       │   ├── 歸約.ts                     — `(bundle, prior view, event, now) → next view` pure reducer。
│       │   └── 歸約.test.ts                — replay prefix、duplicate、out-of-order reject、無 domain query。
│       ├── 流程圖/
│       │   ├── 載入.ts                     — 驗 GraphIR／SVG bundle digest 與 stable ids。
│       │   ├── 高亮.ts                     — entity tokens 到 node／edge class 的 pure mapping。
│       │   └── 高亮.test.ts                — 三層多 instance 與 terminal overlay。
│       ├── 畫面/
│       │   ├── nova-flow.ts                — SVG 流程與 visual log Web Component。
│       │   ├── 系統狀況.ts                 — 只從 reducer state 呈現 backlog／stale／fault。
│       │   ├── 後端額度.ts                 — 顯示 KNOWN／STALE／UNKNOWN／NOT_APPLICABLE 與 observed_at。
│       │   └── 低頻控制.ts                 — ratio policy 與 CLI update command forms。
│       ├── 文字/zh-TW.json                 — 由 machine／state／reason semantic id 對應繁中；改文字不改 machine digest。
│       └── 樣式.css                        — view-only style；無 state 名稱硬編碼。
│
├── 架構/                                  — 可執行邊界規則，不是給人背的文件。
│   ├── 依賴規則.toml                       — Python package globs、允許邊、禁用標準庫與唯一 composition root。
│   ├── 檢查後端依賴.py                     — 用 AST 建 import graph 並套用規則。
│   ├── 檢查規格引用.py                     — digest、FlowSpec binding、ClaimRef 與 impact closure。
│   ├── 檢查字元正規化.py                   — path NFC、identifier NFKC-stable、casefold／confusable collision。
│   ├── test_依賴規則.py                    — 每條 allow／deny 規則都有固定非法 import 反例。
│   └── test_字元規則.py                    — composed／decomposed 與 compatibility-character 反例。
│
├── 驗收/                                  — 跨兩個以上權威、不能合理貼在單一 package 的 executable guarantees。
│   ├── 保證規格語言/
│   │   ├── test_meta_schema.py             — 必填／未知欄位、typed AST、primitive 封閉性。
│   │   ├── test_敏感度.py                  — constant true／false 讓正負控 meta-test 轉紅。
│   │   └── test_隔離協商.py                — capability 缺席只得 UNSUPPORTED_ISOLATION。
│   ├── 狀態機/
│   │   ├── test_所有宣告.py                — 編譯目錄內每份 machine／flow 並跑全 lint。
│   │   ├── test_圖同源.py                  — GraphIR／SVG digest 與 source bundle 一致。
│   │   └── test_非法轉移負控.py            — engine 與 DB FK 兩道都拒絕臨時狀態。
│   ├── 儲存/
│   │   ├── test_envelope.py                — 50 tx/s、200 tx/s burst、250 ms read 與 p99 門檻。
│   │   ├── test_強制終止矩陣.py            — 每個 transaction boundary 前後 kill／restart／reclaim。
│   │   ├── test_備份還原.py                — RPO／RTO 與所有 retained CAS refs 可取。
│   │   └── test_事件流獨立.py              — 尾隨長讀時 state command 仍過 deadline。
│   ├── 三層流程/
│   │   ├── test_平行追求.py                — 四 Pursuit 獨立 scope、budget slice 與 selection。
│   │   ├── test_暫停換後端.py              — 同 Pursuit lineage 與新 Execution backend；fingerprint 不漂移。
│   │   ├── test_一定停止.py                — deadline／budget／attempt exhaustion 的所有 terminal。
│   │   └── test_自我維護.py                — 注入 component fault 會提案 Work，但不能繞過判準直接部署修法。
│   ├── 外部效果/
│   │   ├── test_outbox.py                  — intent 與 domain transition 原子、relay at-least-once。
│   │   └── test_後端更新.py                — drain、固定版本重試、verify、quarantine 與新 Pursuit lineage。
│   └── 前端契約/
│       ├── test_純事件重建.py              — 禁止 view domain query，事件 prefix 可回放。
│       ├── test_游標續讀.py                — disconnect／duplicate／retention floor。
│       └── test_額度與政策.py              — stale quota 與 policy version 在畫面／派工一致。
│
└── 工具/                                  — build／developer 命令薄殼；不能承載領域規則。
    ├── 驗規格.py                           — 執行 schema、machine、flow、ClaimSpec admission checks。
    ├── 生流程圖.py                         — canonical GraphIR→DOT→SVG；Graphviz 版本與字型寫入 evidence。
    ├── 驗架構.py                           — 聚合 Python／TypeScript／spec／Unicode dependency checks。
    └── 跑驗收.py                           — 呼叫外部測試框架並保留 typed red evidence；不重寫判定。
```

【推論】`agy_cli/` 與 `本地模型/` 等樹中用一行表示的 package 仍必須遵守同一最小單位：`manifest.py`、`執行.py`、適用時的 `額度.py`／`更新.py`、`test_契約.py`。這不是允許把它們做成單一大檔。

### 3.3 Runtime data tree（不是 source tree）

【推論】部署資料根固定由一個 application-owned absolute path 注入；candidate 的 argv／env／cwd 不含此根。其形狀是：

```text
資料根/
├── 狀態/權威狀態.sqlite3                  — 唯一權威 writer DB；rollback journal。
├── 事件流/尾隨事件.sqlite3                — 可砍可重建的 WAL read replica。
├── 內容/sha256/ab/cd/<完整摘要>            — CAS blobs；先 blob 後 metadata。
├── 工作區/<execution-id>/                 — 一次性 candidate 可見範圍，Execution 終態後回收。
├── evaluator/<evaluation-id>/             — raw hidden evidence；COOPERATIVE 下只是不傳入 candidate。
├── 備份/<backup-id>/                      — DB＋CAS inventory 的一致備份集合。
└── 鎖/state-owner.lock                    — 防第二個權威 writer 啟動；不是 hostile security boundary。
```

【推論】同 UID 下，隨機路徑與 file mode 不能抵抗主動竊取；這個 runtime tree 只實現 `COOPERATIVE_PROCESS` 的「正常能力不暴露」。ClaimSpec 若聲稱更強，就應在 host offer 不足時硬回 unsupported，而不是拿此目錄配置冒充 sandbox。

### 3.4 明確依賴方向

【推論】production import 的允許圖固定如下；箭頭表示「左邊可以 import 右邊」：

```text
核心 → ∅
狀態機 → 核心
領域.執行 → 核心 + 狀態機
領域.追求 → 核心 + 狀態機 + 領域.執行.公開契約
領域.工作 → 核心 + 狀態機 + 領域.追求.公開契約
四權威中的每一個 → 核心 + 狀態機 + 內容庫／證據庫公開契約（不得互 import）
內容庫／證據庫 → 核心
應用 → 三層公開契約／決策 + 四權威 + 內容庫／證據庫 ports
基礎設施 → 它所實作的 consumer-owned port + 核心（不得被領域反向 import）
介接 → Execution／Resource／Effect 的公開 port（不得 import 應用處理器）
介面 → 僅能引用 應用.邊界
啟動 → 全部（唯一 composition root）
前端 → 規格.介面的生成型別；不可能 import Python 領域 package
```

【推論】機械執法不是一個 linter 名字：

1. 【推論】`架構/依賴規則.toml` 對 package glob 列 `allow_imports`／`deny_imports`；Python AST checker 解析 absolute／relative import，遇 dynamic import、`importlib` 或 module-path string 一律只准在啟動／plugin loader 白名單。
2. 【推論】只有 `nova/基礎設施/狀態庫/sqlite/` 可 import `sqlite3`、知道權威 DB path 或出現 SQL；只有 `nova/基礎設施/` 與 `nova/介接/` 可 import subprocess／socket／HTTP client。
3. 【推論】只有 `nova/啟動/` 可同時 import domain port 與 concrete adapter。應用測試以 fakes 組裝，不准偷 import SQLite。
4. 【推論】TypeScript checker 用 TypeScript compiler API 解析 imports；前端只能 import 自己 package、generated wire types 與純 view dependencies，字串中若出現 domain query route 也由 OpenAPI allowlist check 拒絕。
5. 【推論】spec checker 驗 machine／flow／ClaimRef digest closure；任何未列入 `規格/目錄.json` 的 production spec 不可被啟動器載入。
6. 【推論】每條禁止規則有一個 `.txt` 形式的固定非法 source fixture，meta-test 把它交給 checker 並要求非零；否則架構檢查自己可能恆綠。

### 3.5 哪些東西會一起改

| 變更 | 必須同一變更集出現 | 為何沒有全塞同一目錄 |
|---|---|---|
| 加一個 state／edge | 【推論】所屬 `*.machine.json`、對應 decision／reducer、至少一條 ClaimSpec 正負控、圖同源 sensitivity test；若跨層再改 FlowSpec。 | 【推論】machine 是權威 source，code 是 interpreter consumer，圖是產物；合併目錄只會讓產物取得修改權。 |
| 改 ClaimSpec 語言 | 【推論】`ClaimSpec.schema.json`、模型／compiler／interpreter、primitive catalog digest、語言 meta-suite。 | 【推論】全住判準語言的同一 change axis；既有 claim 不自動升版，需逐份顯式 re-admit。 |
| 新增 executor backend | 【推論】同一 backend folder 的 manifest、執行、quota、update、fingerprint 與共用 contract test；再把 manifest digest 加入 registry。 | 【推論】供應商特性一起變，所以按 backend 垂直放；不能把所有 `執行.py`、所有 `額度.py` 分成水平桶。 |
| 改事件 schema | 【推論】`事件.schema.json`、核心 event type、state migration、publisher、前端 reducer 與 replay/compatibility tests。 | 【推論】這是刻意昂貴的跨權威變更；schema digest＋impact checker 迫使每個 consumer 表態，不能靠共址掩蓋。 |
| 改後端比例語義 | 【推論】資源面的 policy／scheduler／gate、application command、UI form 與 policy ClaimSpecs。 | 【推論】UI 只是命令 adapter；把它和資源決策共址會讓 controller 取得 policy 權。 |
| 加一個外部 endpoint | 【推論】endpoint adapter、EffectContract、帶 `effect_delivery` 的 ClaimSpec、relay crash-gap tests。 | 【推論】adapter 負責 I/O、效果面負責 delivery truth、判準負責驗收；三支筆不得合併。 |
| 改中文名稱 | 【推論】source identifier／filename、translation key 或 display text 所屬檔，以及 Unicode lint；semantic wire id 不跟著翻譯。 | 【推論】領域中文命名與跨版本 id 解耦，避免改字詞就破壞重播。 |

### 3.6 中文檔名與識別字：可以用，但不准裝作沒有成本

【查證】Python 3.14 允許 non-ASCII identifiers，並在 parsing 時把 identifiers 正規化為 NFKC；runtime 以字串查 name 時不會替你做同樣正規化。[Python lexical analysis](https://docs.python.org/3/reference/lexical_analysis.html#names-identifiers-and-keywords)。

【查證】ECMAScript identifiers 使用 Unicode `ID_Start`／`ID_Continue`，但 canonically equivalent 的兩個 identifier 若 code points 不同，並不因此相等。[ECMAScript lexical grammar](https://tc39.es/ecma262/multipage/ecmascript-language-lexical-grammar.html#sec-names-and-keywords)。

【查證】Git 在 macOS 提供 `core.precomposeUnicode=true`，用來反轉 macOS 對 filename 的 Unicode decomposition，方便與 Linux／Windows 共用 repository；case-insensitive filesystem 另有 `core.ignoreCase` 行為。[Git config: core.precomposeUnicode](https://git-scm.com/docs/git-config#Documentation/git-config.txt-coreprecomposeUnicode)。

【推論】因此命名政策定為：

1. 【推論】Python／TypeScript 的領域 class、function、module 與 source filename 可以使用繁體中文；所有 source file UTF-8。
2. 【推論】filename 必須 NFC；identifier 必須同時 `NFC(s)==s` 且 `NFKC(s)==s`。compatibility ideograph、全形英數、零寬字元、bidi control、同一 lexical segment 內不同 script 黏寫與 casefold collision 全拒絕；`test_值型別.py` 這種由 `_`／`-`／`.` 分隔的 ASCII 工具前綴可由 allowlist 明准。
3. 【推論】跨程序／持久化 semantic ids、JSON field names、DB table／column、event type、Claim id、CLI executable 與 canonical flags 使用 ASCII。中文檔名、source identifier 與 view 文字可以改；翻譯以 semantic id 為 key，不改持久 identity。
4. 【推論】所有 subprocess 一律傳 argv array，不拼 shell string；中文 path 由 OS API 直接傳遞。工具若只接受 shell fragment，該 adapter 不 admission。
5. 【推論】macOS checkout 設 `core.precomposeUnicode=true`，CI 同時在 case-sensitive Linux 跑 NFC／casefold collision；不能只信開發機。
6. 【推論】Graphviz 輸入顯式 `charset="UTF-8"`，版本與 `Noto Sans CJK TC` font fingerprint 寫進 graph evidence；語義測試比 node／edge ids，不做跨平台 pixel snapshot。

【推論】最大工具鏈風險不是「中文不能 import」，而是 Python 會 NFKC、ECMAScript 不替你正規化、macOS path 可能分解、字型會改 layout。若不做 repository-wide Unicode collision lint，中文命名就是把同形異碼 bug 寫進 import graph。

### 3.7 題目指定物件的唯一住址

| 指定物件 | 唯一 source owner／位置 |
|---|---|
| Execution／Pursuit／Work 三層 | 【推論】`nova/領域/執行/`、`nova/領域/追求/`、`nova/領域/工作/`；對應宣告在 `規格/執行/`、`規格/追求/`、`規格/工作/`。 |
| 判準／資源／效果／知識四面 | 【推論】`nova/權威/判準/`、`資源/`、`效果/`、`知識/`；machine／policy／claim 同名置於 `規格/` 各 owner 目錄。 |
| 內容定址儲存 | 【推論】contract 在 `nova/內容庫/`，檔案實作在 `nova/基礎設施/內容庫/檔案系統.py`，runtime bytes 在 `資料根/內容/sha256/`。 |
| 證據索引 | 【推論】contract 在 `nova/證據庫/`，SQLite append-only 實作在 `nova/基礎設施/狀態庫/sqlite/證據索引.py`；CAS 只存 bytes，不替它准信。 |
| 狀態機宣告／組合宣告／生成圖 | 【推論】source 分別是各 `規格/*/*.machine.json` 與 `規格/組合/*.flow.json`；compiler 在 `nova/狀態機/`；GraphIR／SVG 只在 build artifact。 |
| ClaimSpec 語言／instances | 【推論】meta-schema 在 `規格/語言/ClaimSpec.schema.json`，compiler／runner semantic 在 `nova/權威/判準/`，每條 instance 跟其保證 owner 放在 `規格/<owner>/保證/`。 |
| 權威事件日誌／可尾隨事件流 | 【推論】權威 append 在 state SQLite migration／工作單元；read replica 在 `nova/基礎設施/事件流/sqlite/`；wire schema 在 `規格/介面/事件流.schema.json`。 |
| 前端 | 【推論】全部在 `前端/`；只消費 OpenAPI commands、GraphBundle 與 event stream。 |
| 共用應用服務邊界 | 【推論】`nova/應用/邊界.py`；CLI／Python API／HTTP 只能經 `nova/介面/` adapter 進入。 |
| executor backend adapters | 【推論】`nova/介接/執行者後端/<backend>/`，每個 backend 的 run／quota／update／fingerprint／contract tests 同址。 |
| 測試 | 【推論】單一 owner 的 unit/property tests 與 owner 同址；跨權威、crash、architecture、ClaimSpec meta tests 在 `驗收/`；ClaimSpec instances 本身是 executable guarantees，不複製成人寫 assertion。 |

---

## 4. Q3：把歷史待決與本輪新增政策全部封口

### 4.1 平行搜尋的結束政策

【推論】固定選 `BEST_BEFORE_DEADLINE`，不做 FIRST_ACCEPTABLE，也不等固定 N 全部跑滿。Work 建立時釘住 `portfolio_deadline`、總預算、最多 Pursuit 數與 criterion ranking schema；cutoff 是「deadline 到」、「所有 Pursuit 封閉」，或「所有 active reservation 已 settle／release、沒有 RUNNING Execution，且 Resource Authority 證明連最小下一步也永遠 reserve 不到」三者先到者。暫時 quota UNKNOWN 只讓 Work 等到 deadline，不冒充永久 budget exhaustion。

【推論】cutoff 發生時立刻固定 `cutoff_global_seq`，拒絕新 Execution reservation，對仍在跑的 Execution 發外部 cancel／kill；只有 `verdict.recorded.global_seq ≤ cutoff_global_seq` 的合格 candidate 進選拔。取消與 kill 最多 5 秒，超過由 supervisor 強制終止並寫 typed terminal；不能讓最慢分支把 Work 變成無界等待。

【推論】ranking 由 CriterionVersion 提供有序 typed score tuple（方向、null policy、rounding 都固定），最後同分以 candidate digest byte order 決勝。沒有合格 verdict 且存在正常 reject 時為 `EXHAUSTED`；所有評估都因 evaluator fault 無有效 verdict 時為 `FAILED_FINAL`；證據完整性或隔離聲明破裂時為 `QUARANTINED`。v1 不做「看起來領先就提早停」的 adaptive marginal rule。

【推論】每個 Execution 最多 nominate 一個 `CandidateBundle`，bundle 可用 CAS refs 包住多個檔案；每個 candidate digest × criterion version 最多一個有效 final verdict。8 Pursuit × 每 Pursuit 16 Execution 因而給單一 Work 最多 128 個 evaluation lifecycle，額外重跑只能是同一 Evaluation 的 bounded attempt，不能偽裝成第 129 個候選。

### 4.2 後端比例、硬資格與額度觀測

【推論】`AllocationPolicyVersion` 是 immutable data：`policy_id`、`revision`、`weights_basis_points`、`effective_at`、`source_command_id`、digest；weight 總和必須是 10,000。Work 建立時釘住 active policy digest，所有 child Pursuit 繼承；啟用新 policy **只影響之後建立的 Work**，既有 Work 沒有 live reread 或 in-place rebase。

【推論】比例是**軟目標**：按 policy revision 維護 deterministic deficit round-robin，使長期 dispatch 向 weights 收斂；小樣本不承諾精確百分比。weight=0 表示一般 weighted dispatch 不選該 backend，但不是安全禁令；明確、已釘住的 backend requirement 仍可選它。真正的 hard gate 是另一份 live `BackendEligibility`，每次建立 Execution 前都重讀。

【推論】hard gate 依序要求：本地預算 reserve 成功、backend update state 為 AVAILABLE、Claim isolation/capability subset 成立、Pursuit 的 immutable backend/model policy 接受目前 fingerprint、provider quota observation 為可用且未過期。任一失敗都不靠 weight fallback；回 typed `WAITING_RESOURCE`、`UNSUPPORTED_CAPABILITY` 或 `BACKEND_INELIGIBLE`。

【推論】AllocationPolicy 跟 Work 釘住，但 RateCard 不跟 Work 釘住。每次付費 Execution reserve 時讀當下 ACTIVE `RateCardVersion`，以該版 worst-case price 保留 Work 的貨幣預算，reservation event 永久記 rate-card digest；計價升版只影響之後的 reservation。缺 rate card 或無法把 backend usage 換成最壞貨幣上限時，該 paid backend 不 eligible。這避免舊 Work 用過期低價突破硬總額，又保留逐筆核銷。

【推論】遠端付費 backend 的 quota observation 必填 `observed_at`、`valid_until`、`remaining`、`unit`、`reset_at?`、`source`、`confidence`。v1 的 `valid_until` 不得晚於 `observed_at + 5 minutes`；缺席或過期統一為 `UNKNOWN`，**不建立新的付費 Execution**。本地模型與純重播器可明確宣告 `NOT_APPLICABLE`，不能用 `UNKNOWN` 偽裝免費。

【推論】這個 zero-dispatch fallback 很保守，也會讓沒有 quota observation 能力的付費 adapter 無法自動派工；這是刻意成本，不是 bug。反轉它需要一條新的產品政策明講「UNKNOWN 時願意冒多少白卷風險」，並把 canary 次數／金額寫成硬上限與 ClaimSpec；在那之前不自行猜。

### 4.3 CLI 更新的精確互鎖

【推論】UI 的「更新」只送 command，application 建立一件普通 `backend-update` Work；該 Work 仍走通用 Work machine。它所編排的**效果面 backend phase**固定為 `REQUESTED → DRAINING → UPDATING → VERIFYING → AVAILABLE`，錯誤終態為 `UPDATE_FAILED` 或 `QUARANTINED`；這不是第四個垂直層，按鈕本身也不執行 package manager。

【推論】進入 DRAINING 時，resource hard gate 立即禁止該 backend 接新 Execution；已 RUNNING 的 Execution 依自己的外部 limit 結束或被 supervisor 終止。所有 active Execution terminal 後才可送 update effect。v1 不保留 side-by-side 舊 binary，也不在更新中把新舊 fingerprint 混跑。

【推論】Pursuit 釘的是 immutable backend/model policy；每個 Execution 再記 exact capability fingerprint。暫停後換另一 backend，可以在同一 Pursuit 內發生，前提是新 backend 本來就在該 pinned policy 中，而且建立的是一個有明確 backend-selection event 的新 Execution。CLI 更新若改變同一 backend 的 fingerprint，受影響 Pursuit 進 `PAUSED_CAPABILITY_CHANGED`；v1 不原地 rebase，而是由 Work 建立 `supersedes_pursuit_id` 的新 Pursuit。Work 不終結，lineage 不消失，舊 Pursuit 不偷換。

【推論】update effect 只能指定精確 `target_version`，不能寫 `latest`。adapter 必須證明重複執行「install target version」是收斂操作，成功後重新列 capabilities 並比對 expected fingerprint；任何無法固定 target 或驗 postcondition 的 updater 在 v1 是 `UNSUPPORTED_UPDATE`。

### 4.4 外部效果在 ClaimSpec 的必填形態

【推論】ClaimSpec v0 的定案版號是 `claimspec_version=0.2.0`；第二輪紙上例子的 0.1.0 尚未 admission，直接由 0.2.0 取代，不做假 migration。top-level 新增 `effect_delivery: EffectDelivery | null` 且仍 `additionalProperties=false`。只要 setup／stimulus／cleanup 解析到任何 external-effect primitive，此欄不得為 null；沒有外部效果時必須為 null，避免到處塞假 delivery policy。第一份外部時間上限 claim 的值就是 null，因為殺 candidate process 是 runner 資源控制，不是對外 endpoint 效果。

| `EffectDelivery` 欄位 | 型別 | v1 規則 |
|---|---|---|
| `endpoint_id` | SemanticId | 【推論】綁定 endpoint adapter manifest，不接受任意 URL 當身份。 |
| `operation` | SemanticId | 【推論】一個 endpoint 的不同效果逐 operation 裁定。 |
| `semantics` | `AT_LEAST_ONCE_IDEMPOTENT` \| `AT_MOST_ONCE` | 【推論】必填；schema 不含 EXACTLY_ONCE。 |
| `intent_schema`／`intent_digest` | schema ref＋digest | 【推論】outbox bytes 與 Claim plan 使用同一 immutable shape。 |
| `idempotency_key` | typed expression | 【推論】AT_LEAST_ONCE 必填，且只可由 immutable intent fields canonicalize／hash。 |
| `attempt_policy` | max attempts、absolute deadline、backoff vector | 【推論】兩種語意都有限；不能無界 retry。 |
| `receipt_schema` | schema ref＋digest | 【推論】endpoint observation 的 typed receipt；raw stdout 不是 receipt schema。 |
| `success_postcondition` | Predicate AST | 【推論】由 verifier observation 判定目的端是否達到預期 state。 |
| `duplicate_policy` | enum | 【推論】AT_LEAST_ONCE 固定 `DESTINATION_DEDUP_OR_CONVERGE`；AT_MOST_ONCE 固定 `LOSS_OVER_DUPLICATE`。 |
| `uncertain_terminal` | literal `DELIVERY_UNCERTAIN` | 【推論】network timeout 不能擅自算成功或失敗。 |

【推論】endpoint admission 規則已定，不是逐案再吵一次：目的端有 atomic idempotency key，或 operation 是「收斂到 pinned target」時，選 `AT_LEAST_ONCE_IDEMPOTENT`；否則只能選 `AT_MOST_ONCE`。前者在 send 後、receipt 前 crash 會重送；後者在 send 前先持久標記 attempt，該 crash gap 可能漏送但不重送。

【推論】v1 的 CLI updater 值固定為：`endpoint_id=backend-cli-updater`、`operation=install-pinned-version`、`semantics=AT_LEAST_ONCE_IDEMPOTENT`、key=`sha256(backend_id,target_version,request_id)`、最多 5 attempts、backoff `[1s,5s,30s,120s]`、absolute deadline 15 minutes，postcondition 是實際 installed version 與完整 capability fingerprint 等於 expected；逾期或不一致把 backend 留在 QUARANTINED。

### 4.5 歷史待決清零表

【查證】第一輪的歷史待決集中在一般 DAG、SQLite topology／engine、workload envelope、hidden feedback、threat model 與 endpoint delivery；第二輪另留平行搜尋終止、儲存 A／B／C、隔離 A／B／C。（來源：[第一輪第 5 節](./sol-新局-第一輪.md#5-需要現在裁定的最小清單)與[第二輪](./sol-新局-第二輪.md)。）

| 歷史問題 | 狀態與建議值 | 理由 | 判斷會反轉的明確條件 |
|---|---|---|---|
| 第三層一般 DAG 或父子 | 【推論】**已裁定：持久佇列＋顯式父子；不做一般 DAG。** | 【推論】Work→Pursuit→Execution 已涵蓋已知 fan-out／selection；Pursuit 拆層沒有產生任意依賴。 | 【推論】首個必需 child-to-child prerequisite、跨 Work join 或拓撲補償出現並有 ClaimSpec 時反轉。 |
| 平行搜尋何時結束 | 【推論】**已裁定：BEST_BEFORE_DEADLINE。** | 【推論】同時滿足「判官選最好」與硬成本／latency；FIRST_ACCEPTABLE 與產品要求衝突。 | 【推論】產品要求每個策略都必須跑完以證明覆蓋時改 BEST_OF_N；候選完全無品質排序且時間壓倒一切時才改 FIRST_ACCEPTABLE。 |
| 權威 SQLite journal／connection | 【推論】**已裁定：專用 state owner、1 connection、rollback、FULL。** | 【推論】一台 writer、短 command transaction；讓唯一寫入者由拓撲而非 lock retry 承載。 | 【推論】持續 >50 tx/s、owner p99 超 envelope、必須有 direct read pool 或第二台 writer 時重選。 |
| 儲存前進 A／B／C | 【查證】**已裁定：使用者選 A，接受第二輪 v1 envelope。** | 【推論】沒有跨主機／HA 需求，並已有 admission cap 與淘汰測試，不必等 production。 | 【推論】跨主機 writer、host-loss RPO=0、讀交易壓不進 250 ms 或 SQLite 合成 suite 失敗時反轉。 |
| PostgreSQL | 【推論】**已裁定：v1 不選。** | 【推論】當前沒有 client/server concurrency／HA 硬需求，先付服務維運稅無對應保證。 | 【推論】第二 control-plane writer、同步遠端複寫或 single owner 經量測淘汰時，成為第一替代。 |
| SQLite per-work／tenant 分片 | 【推論】**已裁定：v1 不選。** | 【推論】全域預算、後端 allocation 與 Work portfolio 需要單一交易域；分片會先製造跨片帳。 | 【推論】工作域成為無共享預算／無跨域選拔的天然 tenant，且單檔 contention 已量測成立時反轉。 |
| FoundationDB | 【推論】**已裁定：v1 不選。** | 【推論】跨機強交易與水平擴張均非需求，資料模型／維運成本沒有收益對象。 | 【推論】跨機水平交易成硬需求、PostgreSQL 單 primary 又被相同 envelope 淘汰時才重開。 |
| Durable Object／actor-per-work | 【推論】**已裁定：v1 不選。** | 【推論】部署不是 edge actor runtime，且全域資源帳與 selection 不能自然落在單 object。 | 【推論】產品本身遷入該 runtime，且 authority 可按 Work 完全分區時反轉。 |
| Temporal 類 durable workflow | 【推論】**已裁定：v1 不選。** | 【推論】它不能替代 criterion secrecy、budget truth 或 endpoint idempotency，現階段只增加另一個服務。 | 【推論】團隊已營運該平台，或 timer／workflow versioning 複雜度實測超過領域本身時反轉。 |
| LMDB／MDBX／RocksDB 類 KV | 【推論】**已裁定：v1 不選。** | 【推論】會失去 SQL constraint／migration／診斷，卻不消除 lease／outbox／state-machine 工作。 | 【推論】profile 證明瓶頸是 SQLite SQL／B-tree 而非 owner topology，且 KV adapter 通過同一 crash suite 時反轉。 |
| 尾隨事件資料面 | 【推論】**已裁定：獨立、可重建 SQLite WAL replica。** | 【推論】這是 single publisher＋many tailer；與權威 DB 的 single owner workload 不同，UI 永不搶權威交易。 | 【推論】事件量／保留使 WAL checkpoint 或單檔 range read 失敗，或需要跨主機 stream service 時，換 segment/object log；不連動改權威 store。 |
| 領域事件 90 天後怎麼辦 | 【推論】**已裁定：90 天是最低保證；v1 不自動刪，10 GiB 時停 admission 並提 maintenance Work。** | 【推論】沒有已驗 compaction snapshot 時刪事件，會讓 head 變第二份真相並破壞純 fold。 | 【推論】只有新的 compaction／retention ClaimSpec 對重播、cursor、crash 與負控全綠，才啟用有版本的刪除政策。 |
| workload envelope 是等量測或先訂 | 【推論】**已裁定：先訂三類 envelope，再做合成驗證。** | 【推論】需求／SLO與 policy cap 不能量出；p99、恢復與 burst 才是候選要量的結果。 | 【推論】不反轉方法；只在新產品需求到來時升版數值並重新跑 selection suite。 |
| 判準 threat profile | 【查證】**已裁定：使用者選 COOPERATIVE_PROCESS。** | 【推論】當前同機同 UID 無 OS security boundary，誠實聲明只防正常路徑無意洩漏。 | 【推論】candidate 有竊取動機、第三方 code 進場、hidden case 高價且不可再生時，先升 RESTRICTED_OS／HOSTILE_VM 才能驗那些 claims。 |
| 中間隔離形態 | 【推論】**已裁定：每個 ClaimSpec 宣告 requirement，host offer 做 subset。** | 【推論】輕 claim 可立即跑，強 claim fail closed；安全等級跟保證走，不是整個產品一句模糊口號。 | 【推論】若所有 production claims 都升到同一強 profile，可把它改成 deployment-wide minimum，但仍不取消 per-claim declaration。 |
| hidden feedback A／B／C | 【查證】**已裁定：使用者選 A，雙池＋clause gated＋揭露即燒掉。** | 【推論】保留比 pass/fail 更強的修正梯度，同時不透傳 raw expected。 | 【推論】candidate 轉 hostile 或 sealed case 不可再生時縮到 B；所有案例本來就公開且另有 held-out property generator 時才放寬到 C。 |
| 外部 endpoint delivery | 【推論】**已裁定：ClaimSpec 必填二選一；無 exactly-once。** | 【推論】崩潰間隙的 duplicate／loss 必須在 executable contract 內，不准留在 prose。 | 【推論】目的端新增／撤銷 atomic idempotency capability 時，該 operation 升 ClaimSpec revision 重裁；舊 receipt 不改寫。 |
| ratio policy 對在途 Work | 【推論】**已裁定：Work 建立時釘版本；不重讀。** | 【推論】保持重播、成本歸因與平行比較一致；UI 改 ratio 只影響新 Work。 | 【推論】產品要求緊急重分配在途 portfolio 時，新增顯式 Work rebase transition＋新 policy digest＋前後成本 ClaimSpec；不得改成暗中 reread。 |
| ratio 是硬或軟 | 【推論】**已裁定：比例是 soft weighted target；資格另有 live hard gate。** | 【推論】優惠偏好與安全／額度禁令失敗模式不同，混成 weight 會讓 fallback 越權。 | 【推論】若某份合約要求精確流量承諾，另建 hard quota／window policy；不把一般 ratio 偷換語義。 |
| 計價版本何時生效 | 【推論】**已裁定：每筆 reservation 釘當下 RateCardVersion，不跟 Work 固定。** | 【推論】硬貨幣上限必須用最新已知 worst-case，逐筆 digest 又可重播核銷。 | 【推論】只有供應商提供事前固定整件 Work 報價且目的端承諾不變，才可改成 Work-level rate pin。 |
| quota 缺席／過期 | 【推論】**已裁定：5 分鐘上限，UNKNOWN 時零新付費 Execution。** | 【推論】把未知當充足會直接產生白卷；local/replay 必須明講 NOT_APPLICABLE。 | 【推論】產品明示願承擔 bounded canary 風險，且給出次數／金額上限與反例時，才新增 UNKNOWN fallback policy。 |
| CLI 更新 interlock | 【推論】**已裁定：drain execution、pinned target at-least-once、verify fingerprint；不保留舊 binary。** | 【推論】操作簡單、可重試、在途 process 不換 executable；Pursuit 以新 lineage 接新 fingerprint。 | 【推論】更新頻率或長時 Pursuit 使 drain／新 Pursuit 成本不可接受，且有能力安全保留／驗證 side-by-side binary 時，才改為雙版本。 |
| 狀態機與圖 | 【推論】**已裁定：MachineSpec＋FlowSpec 是 source，GraphIR／SVG 純生成。** | 【推論】同一 digest 同時限制 runtime 與 view，消滅手畫圖漂移。 | 【推論】不反轉同源原則；圖形 renderer 可換，但仍只能消費 GraphIR。 |
| 前端模型 | 【推論】**已裁定：TypeScript 原生 Web Components＋SVG，純 event fold。** | 【推論】目前是窄、讀多寫少的 visual log；不需先引入 framework state store 或第二份 read model。 | 【推論】多頁協作、複雜 local editing 或 accessibility component 規模使原生元件維護成本被量測否決時可換 view framework；domain／event contracts 不動。 |
| 中文命名 | 【推論】**已裁定：source 可中文；wire／DB／semantic ids ASCII；NFC＋NFKC-stable lint。** | 【推論】取得領域可讀性，同時封住 Python／ECMAScript／macOS normalization 差異。 | 【推論】若必須支援不接受 Unicode path 的核心工具，adapter 可建立 ASCII staging path；不反向禁止領域 source 中文。 |

【推論】沒有任何一條仍需要額外產品資訊才能給 v1 值。未來若命中表中反轉條件，那是新需求觸發新 revision，不是本輪漏答。

---

## 5. Q4：定案自檢

### 5.1 未決數

【推論】未決條目數：**0**。沒有卡住的產品資訊，也沒有以「稍後看情況」逃掉的語意。尚未量到的 SQLite p99、crash recovery、Graphviz layout 與 adapter capability 是**驗證工作**；它們有明確通過／淘汰條件，不是設計選項仍未選。

【推論】本輪定案並不宣稱實作已通過。SQLite 只有「被選為要實作並接受 envelope suite 的 adapter」，ClaimSpec 與 state-machine language 也只有「schema／出口已定」；在正控、負控、kill matrix 真的轉對顏色前，不得把架構定案偷換成行為已驗收。

### 5.2 互相依賴的決定

| 改動其中一個 | 必須連動重開的決定 | 原因 |
|---|---|---|
| Work→Pursuit→Execution 基數 | 【推論】父子非 DAG、portfolio budget、BEST_BEFORE_DEADLINE、FlowSpec、event lineage。 | 【推論】selection 與停止都是對 child 集合的函式；少一層會改終態所有權。 |
| 一般 DAG 成為需求 | 【推論】machine import relation、scheduler、cycle lint、join／cancel／compensation terminal、資料 migration。 | 【推論】不是多一張 edge 表；它改了可執行性與部分失敗語義。 |
| state DB 不再 single owner | 【推論】journal mode、claim／lease fencing、transaction API、backup、event publisher 與 architecture rule。 | 【推論】目前所有 command 原子性與 global_seq 都倚賴單 writer。 |
| UI 不再是純 visual log | 【推論】讀模型權威、事件 schema理由、query service、storage topology與 consistency ClaimSpecs。 | 【推論】一旦允許補查詢，就重新出現第二份真相與讀寫互阻；不能只加 endpoint。 |
| MachineSpec versioning | 【推論】event envelope、GraphBundle digest、runtime FK catalog、replay reducer、migration ClaimSpec。 | 【推論】圖與 runtime 同源靠的就是同一 machine digest。 |
| ratio policy改為 live reread | 【推論】Work replay、cost attribution、parallel comparability、UI command語意與 policy tests。 | 【推論】一次 Work 中途換權重會讓相同事件 prefix 得不到相同 dispatch decision。 |
| quota UNKNOWN 改可派工 | 【推論】hard gate、canary budget、Work terminal、UI risk state 與額度 ClaimSpec。 | 【推論】這不是顯示偏好，而是新增一條會花錢且可能拿白卷的產品政策。 |
| CLI 更新改 side-by-side | 【推論】backend manifest、binary CAS、fingerprint selection、Pursuit resume、cleanup／supply-chain tests。 | 【推論】保留舊 executable 會引入另一個內容、簽章與回收生命週期。 |
| threat profile 升強 | 【推論】runner deployment、filesystem／PID／network isolation、raw evidence viewer、timing feedback 與可驗 claims。 | 【推論】同 UID process layout 不可能靠多幾個 Python check 變成 hostile boundary。 |
| endpoint delivery 改語意 | 【推論】ClaimSpec revision、outbox state machine、relay crash gap、idempotency key、receipt 與舊 intent migration。 | 【推論】at-least 與 at-most 在 crash gap 選的是相反損失，不能 runtime 自動切換。 |
| 中文／ASCII 邊界改變 | 【推論】Unicode lint、wire compatibility、DB migration、Graph labels 與 code generation。 | 【推論】source rename 可局部；semantic id rename 是持久協定破壞。 |

### 5.3 最可能在第一次實作就打臉的地方

| 風險，按先撞機率排序 | 為何容易錯 | 第一個應該讓它打臉的測試 |
|---|---|---|
| Guard DSL 的互斥／完備證明 | 【推論】第一個真 guard 很可能同時需要 deadline、budget、child verdict 與故障分類；若偷塞 arbitrary Python，宣告式 machine 立即破功。 | 【推論】用兩條重疊 interval guard 與一個未覆蓋 enum 值，admission 都必須紅；再做一個真 Work selection decision table。 |
| `MachineSpec` 與 event-sourced aggregate 的接縫 | 【推論】generic engine 很容易只驗 `to_state`，漏驗 expected seq、machine digest 或 reason；DB head 也容易被誤當真相。 | 【推論】直接繞 application 寫錯 transition tuple、刪 head 全重建、重送同 command 三個負控。 |
| 權威日誌→尾隨庫的 crash gap | 【推論】publisher 在 insert 前／後 crash、cursor 先進、duplicate global_seq、retention 同時跑，最容易造成 UI 漏格。 | 【推論】在 read／insert／cursor commit 每一步 kill，要求 tail 最終是權威 seq 的無洞前綴；duplicate 可有，hole 不可有。 |
| SQLite rollback＋FULL 的實機 p99 | 【推論】50 tx/s 假設可能被實際磁碟 fsync、CAS metadata、同秒 lease storm 打穿；目前只有 envelope，沒有測量。 | 【推論】先做最薄 state owner＋真磁碟 benchmark，不先堆 domain；若 p99／drain fail，立刻按表反轉。 |
| 額度觀測能力不存在 | 【推論】CLI 後端未必提供可機械讀、可靠且五分鐘內更新的剩餘額度；零派工 fallback 可能讓付費 backend 全部不可用。 | 【推論】每個 adapter 的第一個 contract test 不是 run，而是產生 KNOWN／UNKNOWN／STALE 三態；缺 API 時 UI 與 scheduler 必須誠實停住。 |
| CLI `target_version` 不真可重入 | 【推論】某些 updater 只有「升到 latest」、會改全域 config、或成功 receipt 不等於新 process 實際使用同 fingerprint。 | 【推論】連續送相同 idempotency key 兩次、在 install 後 kill、重啟後重新 probe；最終只有一個 verified fingerprint。 |
| Pursuit 的「換 backend」與「保持獨立 identity」 | 【推論】backend family、model、prompt、evidence scope 哪個變化構成新 Pursuit，第一個 adapter 很可能逼出模糊地帶。 | 【推論】建立矩陣並固定預期：只換到 pinned policy 已允許的 backend＝同 Pursuit／新 Execution；換 model family、換 evidence scope、CLI fingerprint 變化＝新 Pursuit 並保留 supersedes lineage。 |
| COOPERATIVE hidden leakage | 【推論】test discovery、exception hook、telemetry、inherited FD 或 workspace copy 任一條都可能把 sentinel 帶回；同 UID 又無真正保密邊界。 | 【推論】把不同 sentinel 放進 path、env、stack、stdout、raw report 與 open FD，executor-visible bytes 必須零命中；這仍不能升格成 hostile 保證。 |
| 中文 path／identifier 正規化 | 【推論】Python NFKC 與 TypeScript code-point equality 不同，macOS checkout 又可能分解 filename；本機單平台綠最會騙人。 | 【推論】在 macOS 與 case-sensitive Linux 各跑 composed／decomposed、全形、compatibility ideograph、casefold collision fixture。 |
| Graphviz 中文字型與 stable SVG ids | 【推論】UTF-8 能讀不代表字型存在；renderer version／font metrics 會改 layout，SVG optimizer 還可能吃掉 ids。 | 【推論】用固定中文 graph fixture 驗 node／edge ids 與 bundle digest，而非像素；缺 pinned font 必須 typed build failure。 |

【推論】最先實作的順序因此不能從 UI 開始：先讓 `規格/執行/保證/外部時間上限.claim.json` 在外部 runner 對正控綠、對固定反例紅；再讓最小 MachineSpec compiler／illegal-transition negative control 成立；接著做 state owner＋event publisher kill matrix。這三個信任根沒站住，後面的漂亮流程圖只是會動的謊話。

### 5.4 最終一致性核對

【推論】三層的終態權沒有回流給 executor：Execution supervisor、Pursuit policy、Work selection 各自寫自己的 terminal；executor observation 只是輸入。

【推論】四個橫向面沒有被 application service 吞掉：Definition／Evaluation 仍分筆，資源先 reserve，效果 intent／relay 分離，知識只讓 Work 綁 snapshot；CAS 與證據索引沒有被誤叫成權威。

【推論】前端要求沒有反向污染 model：事件欄位都有領域不變式理由，view 只能 fold immutable GraphBundle＋event prefix，所有 writes 回同一 application boundary。

【推論】使用者第二節五個選擇全部保留；唯一補充是**權威 DB 的 rollback 決策不等於禁止可重建尾隨庫使用 WAL**。若把兩個 workload 強行共用一個 journal profile，才會重新讓 UI 讀取與權威寫入互相牽制。

【推論】定案完成：沒有未選選項、沒有等待產品回答的欄位、沒有手畫圖、沒有未聲明的 delivery 語意，也沒有一條可在 isolation 不足時悄悄 skip 的保證。
