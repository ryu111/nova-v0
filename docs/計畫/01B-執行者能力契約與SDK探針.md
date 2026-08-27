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
- Forbids: provider option names and unknown enum fallthrough。

**ClaimSpec:** 【推論】`execution.backend-capability.closed-vocabulary` 從紅轉綠。

**固定負控:** 【推論】加入 capability `MAGIC_TOOL_BYPASS`、tool class `OTHER`、usage scope `BEST_EFFORT` 或 outcome free string；schema/compiler 必須 direct red。

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

**固定負控:** 【推論】四個 named subjects 分別在 deny 後仍呼叫 handler、回 malformed structured output、越過 delegation depth、把 ROOT_ONLY 標成 tree total；各自指定 predicate direct red。

- [ ] **Step 1: 寫四個 faulty subjects 與 exact failed predicate red**
- [ ] **Step 2: 跑 `uv run pytest -q 驗收/執行者能力/測_工具輸出代理契約.py`**

Expected: 【推論】FAIL；至少四個 faulty subjects 尚未被 contract suite 拒絕。

- [ ] **Step 3: 寫 pure contract runner，不呼叫 SDK 或資料庫**
- [ ] **Step 4: 跑 tests 與 ClaimSpec，確認 reference subject PASS、四個 negatives direct red**
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

**ClaimSpec:** 【推論】`execution.backend-capability.evidence-fingerprint-ttl-bound` 從紅轉綠。

**固定負控:** 【推論】SDK/CLI/model/settings catalog 任一 digest 改變仍沿用舊 evidence，或 `now == expires_at` 仍 VALID；direct red。

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
