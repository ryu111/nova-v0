# 執行者能力契約與 SDK 探針 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:subagent-driven-development` (recommended) or `superpowers:executing-plans` to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 【推論】在任何 state owner、budget ledger 或付費 adapter 之前，先把執行者的工具授權、結構化輸出、子代理與成本證據能力做成可執行契約，並用 pinned Claude Agent SDK 的靜態探針與有界 live smoke 及早推翻錯誤假設。

**Architecture:** 【推論】本計畫只產生 provider-neutral schemas、pure contract fixtures、SDK surface probe 與 immutable CapabilityEvidence；不建立完整 Claude adapter、不開資料庫、不呼叫 application boundary。靜態 probe 是必跑 gate；live smoke 是 Claude admission gate。缺憑證或網路不阻塞 core，但只能得到 `NOT_ADMITTED`，不得宣稱 Claude supported。

**Tech Stack:** 【推論】CPython 3.14.7、JSON Schema 2020-12、pytest、Hypothesis、pinned `claude-agent-sdk`、ClaimSpec runner。

## Global Constraints

- 【推論】跨後端語義不得使用供應商 option 名；adapter 才能把 semantic capability 映到 SDK API。
- 【推論】capability 固定包含 `PRE_TOOL_DECISION`、`NATIVE_STRUCTURED_OUTPUT`、`DELEGATION`；缺能力必須 typed `UNSUPPORTED_CAPABILITY`，不得改成提示詞或 optimistic true。
- 【推論】工具類別固定 `READ_ONLY|EFFECT_INTENT_REQUIRED|LOCAL_WORKSPACE_MUTATION|DELEGATION`；本計畫只驗契約，EffectIntent 的權威 relay 由後續 effect plan 實作。
- 【推論】usage scope 固定 `ROOT_ONLY|DELEGATION_TREE_TOTAL|UNKNOWN`；`UNKNOWN` 不得冒充可核銷 tree total。
- 【推論】CapabilityEvidence 綁 exact backend fingerprint、probe revision、observed/expiry、named controls；靜態 surface evidence TTL 最長 7 天、live readiness evidence TTL 最長 24 小時，fingerprint 改變立即失效，過期不得沿用。
- 【推論】live smoke 有 wall time、turn、tool、output、spend 上限；不評模型聰明度，只驗可機械能力。
- 【推論】四層重播界線：spec→plan 編譯必須決定性；live invocation→response 不要求決定性；
  已完成 run→EvidenceBundle 必須 immutable；同 bundle→分析必須決定性。
  **錄製義務不因後端非決定而免除。**
- 【推論】輸出決定性家族封閉字彙：`SEEDED_REQUEST`、`SEEDED_OUTPUT_REPEATABILITY_OBSERVED`、
  `CONTRACTUAL_OUTPUT_DETERMINISM_CLAIMED`、`OUTPUT_DETERMINISM`，後三者預設 unsupported。
  `OUTPUT_DETERMINISM` 取中立名——純重播器不靠 seed 產生結果，seeded 語意只屬於
  「對外部後端帶 seed 觀測」那兩條。`OUTPUT_DETERMINISM` 只能由 mechanism evidence 取得，
  mechanism enum **v1 唯一成員 `PURE_REPLAYER`**（計畫 05 重播器）；evidence 必須引用
  `execution.backend.replayer-output-deterministic`（05 Task 7）的 **exact revision、
  claim digest 與已准入 predicate ids**，不得只引 `claim_id` 字串——一條沒有決定性負控的
  claim 撐不起決定性能力的名字。`PINNED_DETERMINISTIC_ENGINE` 與
  `BACKEND_CONTRACT_WITH_CONFORMANCE_SUITE` 不在 v1 可准入 enum——重入條件是各自具備
  獨立 admission schema、checker 與固定負控後，以擴充點（加蓋動作②）加入。
  外部 backend 目前最多取得 `SEEDED_OUTPUT_REPEATABILITY_OBSERVED` 或
  `CONTRACTUAL_OUTPUT_DETERMINISM_CLAIMED`；後者是契約主張，
  **不得滿足要求機械決定性的 claim 綁定**——有限 conformance suite 只證明 suite 範圍內
  符合契約，不證明未來所有輸出決定性。

## File Structure

```text
規格/執行/
├── BackendCapability.schema.json             — provider-neutral capability vocabulary。
├── ToolAuthorizationPolicy.schema.json        — semantic tool allow/deny/classification policy。
├── StructuredOutputContract.schema.json       — exact schema digest與native/fallback要求。
├── DelegationPolicy.schema.json               — 子代理數、深度、模型與每支上限。
├── UsageEvidence.schema.json                  — usage buckets、scope與source evidence。
├── CapabilityEvidence.schema.json             — exact fingerprint、TTL與controls。
└── 保證/能力/
    ├── 後端能力封閉.claim.json                — unknown capability/outcome direct red。
    ├── 工具輸出代理契約.claim.json            — deny/output/delegation/usage scope contract。
    ├── SDK靜態介面存在.claim.json             — pinned SDK surface不得漂移。
    ├── 能力證據不可沿用.claim.json            — fingerprint/TTL失效。
    └── Claude有界live探針.claim.json           — live evidence才能admit exact fingerprint。
nova/領域/執行/
├── 能力.py                                   — capability、tool class、typed outcome unions。
└── test_能力契約.py                           — provider-neutral property tests。
工具/
├── 探ClaudeSDK介面.py                         — pinned distribution靜態surface probe。
└── 跑ClaudeSDK煙霧.py                         — bounded opt-in live conformance probe。
驗收/執行者能力/
├── fixtures/假能力後端.py                    — named faulty capability subjects。
├── 測_工具輸出代理契約.py                    — pure shared contract suite。
├── 測_SDK靜態介面.py                         — option/type/hook surface probe。
├── 測_能力證據.py                            — fingerprint與TTL invalidation。
└── 測_Claude_live探針.py                     — fake transport與opt-in live admission。
```

## Dependency Gate

前置計畫：01

【推論】只依 plan 01：ClaimSpec runner、schema loader、named direct-red control 已綠。不得依 plan 02–20；若本計畫需要 state owner、budget ledger、application boundary 或完整 Claude adapter 才能測，表示契約切得太晚或偷做了後續實作。

---

### Task 1: 固定 provider-neutral capability、tool、output、delegation 與 usage schemas

**Files:**
- Create: `規格/執行/BackendCapability.schema.json`
- Create: `規格/執行/ToolAuthorizationPolicy.schema.json`
- Create: `規格/執行/StructuredOutputContract.schema.json`
- Create: `規格/執行/DelegationPolicy.schema.json`
- Create: `規格/執行/UsageEvidence.schema.json`
- Create: `nova/領域/執行/能力.py`
- Create: `nova/領域/執行/test_能力契約.py`
- Create: `規格/執行/保證/能力/後端能力封閉.claim.json`

**Interfaces:**
- Produces: closed capability/tool class/typed outcome/usage scope unions and immutable refs。
- Produces: 輸出決定性家族四條目（形狀見 Global Constraints）；`OUTPUT_DETERMINISM`
  的 mechanism enum v1 唯一成員 `PURE_REPLAYER`。
- Forbids: provider option names and unknown enum fallthrough。
- Forbids: repeatability／contractual evidence 鑄出 `OUTPUT_DETERMINISM`。

**ClaimSpec:** 【推論】`execution.backend-capability.closed-vocabulary` 從紅轉綠。

**ClaimSpec落點:** `execution.backend-capability.closed-vocabulary` → `規格/執行/保證/能力/後端能力封閉.claim.json`（本 task Create）

【推論】**`wrong-claim-ref` 不得實作成 claim-id 白名單**（審查條件，2026-08-28）——
白名單只回答「名字在不在清單裡」，回答不了「那條 claim 到底驗了什麼」。必須這樣執法：
①`PURE_REPLAYER` 的 capability policy **明確宣告所需的 predicate set**：
`replay_order_stable`、`same_script_same_canonical_event_bytes`、`replay_ignores_ambient_time`。
②resolver 從 `ProtectedClaimClosure` 解析出 **exact claim revision 與 digest**。
③resolved claim 的**已准入 predicate set 必須涵蓋**上述集合。
④`claim_id` 只是語義定位，**不能單獨取得資格**。
⑤capability policy 本身必須是封閉、版本化、內容定址的資料，
或由受保護程式碼連同它自己的 ClaimSpec 承載。

如此這格負控問的不是「名字對不對」，而是
**「這份已准入證據是否真的驗了能力要求的那三個 predicate」**。

**固定負控:** 【推論】加入 capability `MAGIC_TOOL_BYPASS`、tool class `OTHER`、usage scope `BEST_EFFORT`、outcome free string，或把 `PINNED_DETERMINISTIC_ENGINE` 填進 determinism mechanism enum；schema/compiler 必須 direct red。

- [ ] **Step 1: 寫 unknown enum 與缺 ref 的 schema red tests**
- [ ] **Step 2: 跑 `uv run pytest -q nova/領域/執行/test_能力契約.py`**

Expected: 【推論】FAIL；schemas/module 尚不存在，或 unknown enum 被接受。

- [ ] **Step 3: 寫六份 closed schemas 與 frozen Python unions**
- [ ] **Step 4: 跑 tests 與 `uv run python 工具/跑驗收.py --claim execution.backend-capability.closed-vocabulary`，確認 PASS**
- [ ] **Step 5: Commit**

```bash
git add 規格/執行/BackendCapability.schema.json 規格/執行/ToolAuthorizationPolicy.schema.json 規格/執行/StructuredOutputContract.schema.json 規格/執行/DelegationPolicy.schema.json 規格/執行/UsageEvidence.schema.json 規格/執行/保證/能力/後端能力封閉.claim.json nova/領域/執行/能力.py nova/領域/執行/test_能力契約.py
git commit -m "feat: 宣告執行者能力契約"
```

---

### Task 2: 建立 deny、structured output、delegation 與 usage scope 共用契約套件

**Files:**
- Create: `驗收/執行者能力/fixtures/假能力後端.py`
- Create: `驗收/執行者能力/測_工具輸出代理契約.py`
- Create: `規格/執行/保證/能力/工具輸出代理契約.claim.json`

**Interfaces:**
- Produces: `assert_capability_contract(subject, offer, request) -> ContractReport` pure suite。
- Observes: denied tool handler call count、schema validation、delegation bounds、usage scope honesty。

**ClaimSpec:** 【推論】`execution.backend-capability.tool-output-delegation-contract` 從紅轉綠。

**ClaimSpec落點:** `execution.backend-capability.tool-output-delegation-contract` → `規格/執行/保證/能力/工具輸出代理契約.claim.json`（本 task Create）

**固定負控:** 【推論】五個 named subjects 分別在 deny 後仍呼叫 handler、回 malformed structured output、越過 delegation depth、把 ROOT_ONLY 標成 tree total、
宣告 `SEEDED_REQUEST` 卻不忠實交付 seed；各自指定 predicate direct red。
第五格的 oracle 是 **seed-sensitive transport spy**，不是輸出：
spy 直接記錄 adapter 實際交付給後端的 canonical request；兩個不同 seed 送入，
斷言收到的 request **保留同值、同型別、同欄位位置**；spy 的輸出固定且與 seed
無關——**明確禁止用輸出是否相同作 oracle**（後端本來就決定性時，丟掉 seed
完全可能不紅；seed 的保證是「請求欄位被忠實交付」，不是「輸出因此改變」）。
faulty adapter 刪除／覆寫／固定 seed 時只紅在 `seeded_request_delivers_seed`。
防恆真半格：未宣告 `SEEDED_REQUEST` 的 adapter 不因此被要求接受 seed。
（R14 重做：R13-03 版把 `SEEDED_REQUEST` 與 repeatability 混成一格——
R2-03／R3-03 兩次踩過的形狀，第三次由 oracle 選錯重現。）

- [ ] **Step 1: 寫五個 faulty subjects（第五格用 transport spy）與 exact failed predicate red**
- [ ] **Step 2: 跑 `uv run pytest -q 驗收/執行者能力/測_工具輸出代理契約.py`**

Expected: 【推論】FAIL；至少四個 faulty subjects 尚未被 contract suite 拒絕。

- [ ] **Step 3: 寫 pure contract runner，不呼叫 SDK 或資料庫**
- [ ] **Step 4: 跑 tests 與 ClaimSpec，確認 reference subject PASS、五個 negatives direct red**
- [ ] **Step 5: Commit**

```bash
git add 驗收/執行者能力/fixtures/假能力後端.py 驗收/執行者能力/測_工具輸出代理契約.py 規格/執行/保證/能力/工具輸出代理契約.claim.json
git commit -m "test: 強制執行者能力契約"
```

---

### Task 3: 對 pinned Claude Agent SDK 做必跑靜態 surface probe

**Files:**
- Modify: `pyproject.toml`
- Modify: `uv.lock`
- Create: `工具/探ClaudeSDK介面.py`
- Create: `驗收/執行者能力/測_SDK靜態介面.py`
- Create: `規格/執行/保證/能力/SDK靜態介面存在.claim.json`

**Interfaces:**
- Produces: machine-readable surface report for options/types/hooks used by later adapter。
- Requires: pinned SDK exposes tool authorization hook, pre-tool hook, structured output, agent definition and result cost/usage surfaces selected by the adapter contract。

**ClaimSpec:** 【推論】`execution.backend-capability.claude-sdk-static-surface` 從紅轉綠。

**ClaimSpec落點:** `execution.backend-capability.claude-sdk-static-surface` → `規格/執行/保證/能力/SDK靜態介面存在.claim.json`（本 task Create）

**固定負控:** 【推論】fixture SDK 刪除 `can_use_tool`、`PreToolUse`、structured output 或 result total/tree usage 任一 surface；probe 必須 nonzero 且指出 exact missing semantic capability。

- [ ] **Step 1: 寫 one-surface-at-a-time missing SDK red**
- [ ] **Step 2: 跑 `uv run pytest -q 驗收/執行者能力/測_SDK靜態介面.py`**

Expected: 【推論】FAIL；probe 尚不存在，或缺 surface 的 fixture 被放行。

- [ ] **Step 3: pin SDK 並以 public inspect/type metadata 寫 exhaustive probe**
- [ ] **Step 4: 跑 tests、真 pinned package probe 與 ClaimSpec，確認 PASS**
- [ ] **Step 5: Commit**

```bash
git add pyproject.toml uv.lock 工具/探ClaudeSDK介面.py 驗收/執行者能力/測_SDK靜態介面.py 規格/執行/保證/能力/SDK靜態介面存在.claim.json
git commit -m "test: 釘住 Claude SDK 的能力面"
```

---

### Task 4: 讓 CapabilityEvidence 綁 exact fingerprint、controls 與 TTL

**Files:**
- Create: `規格/執行/CapabilityEvidence.schema.json`
- Modify: `nova/領域/執行/能力.py`
- Create: `驗收/執行者能力/測_能力證據.py`
- Create: `規格/執行/保證/能力/能力證據不可沿用.claim.json`

**Interfaces:**
- Produces: `validate_capability_evidence(evidence, exact_fingerprint, now) -> VALID|EXPIRED|FINGERPRINT_MISMATCH|CONTROL_INCOMPLETE`。
- Produces: repeatability evidence 必記 {`N`, 環境／backend fingerprint, request digest,
  全部 N 份輸出 digest, TTL}；determinism evidence 必記 {`mechanism = PURE_REPLAYER`,
  `claim_ref = {claim_id: execution.backend.replayer-output-deterministic, revision, digest,
  predicate_ids}`}——ref 缺 revision／digest／predicate ids 任一即 `CONTROL_INCOMPLETE`；
  contractual evidence 必記 {contract ref, conformance suite ref, pass record digest}。
- Forbids: repeatability 或 contractual evidence 升格為 determinism——N 次逐 byte 相同
  只證成「觀測到重複性」，第 N+1 次仍可能變。

**ClaimSpec:** 【推論】`execution.backend-capability.evidence-fingerprint-ttl-bound` 從紅轉綠。

**ClaimSpec落點:** `execution.backend-capability.evidence-fingerprint-ttl-bound` → `規格/執行/保證/能力/能力證據不可沿用.claim.json`（本 task Create）

**固定負控:** 【推論】SDK/CLI/model/settings catalog 任一 digest 改變仍沿用舊 evidence，或 `now == expires_at` 仍 VALID；direct red。
輸出決定性家族五格：`probe-upgraded-to-determinism`——把 N 次 probe evidence 直接寫成
`OUTPUT_DETERMINISM` supported 的 faulty capability mapper，必須紅在
`determinism_requires_mechanistic_evidence`。`nth-plus-one-differs`——`假能力後端.py`
增一個前 N 次輸出逐 byte 相同、第 N+1 次改變的變體，其 evidence 記為 repeatability，
faulty 檢查器據此讓要求 determinism 的綁定通過，必須紅在 `repeatability_is_not_determinism`。
`forged-mechanistic-ref`——mechanism 填 `PURE_REPLAYER` 但 claim_ref 缺 revision／digest
或指向不可驗來源的 evidence，必須紅在 `mechanistic_ref_must_resolve`。
`wrong-claim-ref`——claim_ref 指到 `execution.backend.replayer-contract-parity`
（一條負控只殺未知 event kind、沒有決定性負控的 claim）的 evidence，必須紅在
`mechanistic_ref_targets_determinism_claim`——引用 claim 時要往下看它的負控殺的是什麼。
`contract-claim-cannot-bind-mechanical`——持 `CONTRACTUAL_OUTPUT_DETERMINISM_CLAIMED`
（含合法 contract ref 與 suite pass record）的後端綁定要求 `OUTPUT_DETERMINISM`
的 claim，必須紅在 `contract_claim_is_not_mechanism`；fixture 內附 suite 外輸出改變的
見證（suite 全過而 suite 外同 seed 輸出漂移），釘死「suite 過」不等於「機械決定」。
防恆真格：計畫 05 純函式重播器以完整 `PURE_REPLAYER` claim_ref 取得
`OUTPUT_DETERMINISM` supported——拒絕不是無條件；帶合規 N 次 probe 的後端
取得 `SEEDED_OUTPUT_REPEATABILITY_OBSERVED` supported。

- [ ] **Step 1: 寫 fingerprint one-field mutation 與 TTL boundary red**
- [ ] **Step 2: 跑 `uv run pytest -q 驗收/執行者能力/測_能力證據.py`**

Expected: 【推論】FAIL；舊 evidence 尚會跨 fingerprint／expiry 被接受。

- [ ] **Step 3: 寫 canonical evidence validation 與 closed invalid reasons**
- [ ] **Step 4: 跑 tests 與 ClaimSpec，確認 PASS**
- [ ] **Step 5: Commit**

```bash
git add 規格/執行/CapabilityEvidence.schema.json nova/領域/執行/能力.py 驗收/執行者能力/測_能力證據.py 規格/執行/保證/能力/能力證據不可沿用.claim.json
git commit -m "feat: 把能力證據綁到執行期指紋"
```

---

### Task 5: 建立有界 live smoke 與 Claude NOT_ADMITTED 規則

**Files:**
- Create: `工具/跑ClaudeSDK煙霧.py`
- Create: `驗收/執行者能力/測_Claude_live探針.py`
- Create: `規格/執行/保證/能力/Claude有界live探針.claim.json`

**Interfaces:**
- Produces: live CapabilityEvidence for exact fingerprint or typed `NOT_ADMITTED(reason)`。
- Probes: deny tool nonexecution、structured output schema、delegation tree total、cancel convergence、outbound payload/manifest binding。

**ClaimSpec:** 【推論】`execution.backend-capability.claude-live-admission-bounded` 從紅轉綠。

**ClaimSpec落點:** `execution.backend-capability.claude-live-admission-bounded` → `規格/執行/保證/能力/Claude有界live探針.claim.json`（本 task Create）

**固定負控:** 【推論】fake live transport 在 deny 後碰 endpoint、漏 subagent cost、忽略 cancel、回錯 schema 或回顯不同 outbound digest；不得產生 admitted evidence。

- [ ] **Step 1: 寫五個 fake live failures 與 no-credential/no-network red**
- [ ] **Step 2: 跑 `uv run pytest -q 驗收/執行者能力/測_Claude_live探針.py`**

Expected: 【推論】FAIL；runner 尚不存在，或 failure/缺外部條件被誤標 supported。

- [ ] **Step 3: 寫 wall/turn/tool/output/spend 全有界 runner；缺外部條件回 NOT_ADMITTED**
- [ ] **Step 4: 跑 deterministic fake suite 與 ClaimSpec；有憑證環境另跑 opt-in live，確認 evidence 綁 fingerprint/TTL**
- [ ] **Step 5: Commit**

```bash
git add 工具/跑ClaudeSDK煙霧.py 驗收/執行者能力/測_Claude_live探針.py 規格/執行/保證/能力/Claude有界live探針.claim.json
git commit -m "test: 用有界真跑探針把關 Claude 准入"
```

## Plan Exit Gate

- 【推論】五份 provider-neutral schemas封閉且沒有供應商 option 名滲入。
- 【推論】deny/output/delegation/usage scope 的 pure contract suite 對 reference 綠、對 named faulty subjects direct red。
- 【推論】pinned SDK 靜態 surface probe 是必跑 gate；API 漂移立即紅。
- 【推論】CapabilityEvidence 跨 fingerprint 或 TTL 不可沿用。
- 【推論】無 live evidence 時 core 可續，但 Claude 明示 `NOT_ADMITTED`；只有 exact fingerprint 的有效 evidence 可宣稱 supported。

## Execution Handoff

【推論】本計畫完成後執行 plan 02–04；後續 plan 05 消費這些 schemas，plan 07擁有核銷規則，plan 14只做 Claude mapping，plan 20只組合 readiness。不得在本計畫提前建立第二套 ledger、state owner 或 production adapter。
