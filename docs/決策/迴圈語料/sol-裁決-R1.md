codex
我會依已提交決議逐條審，不替 fable 補意圖。特別會把「提案方向合理」和「這個版本可直接寫入計畫」分開：只要固定負控殺不到它宣稱的缺口，或把相鄰研究超譯成地基，我會直接 REJECT 並給可重提的最小修改。
exec
/bin/zsh -lc "sed -n '1,260p' docs/決策/計畫修訂決議.md && sed -n '130,210p' docs/計畫/08-目標追求生命週期.md && sed -n '245,305p' docs/計畫/09-持久工作協調與選拔.md && sed -n '1,130p' docs/計畫/01B-執行者能力契約與SDK探針.md" in /Users/sbu/nova
 succeeded in 0ms:
# 計畫修訂決議帳本

2026-08-27 控制端裁定的三方迴圈。**這份是帳本，不是討論記錄**——
每一條決議的狀態必須看得出來，討論過程進各自的回覆檔。

## 協定

```
        ┌──────────────────────────────────────────────┐
        │                                              │
        ▼                                              │
   ┌─────────┐    提案     ┌──────────┐              │
   │  fable  │────────────▶│  決議池   │              │
   │ （提案者）│             └────┬─────┘              │
   └─────────┘                  │                    │
                        ┌───────┴────────┐           │
                        ▼                ▼           │
                  ┌──────────┐    ┌──────────┐      │
                  │  claude  │    │   sol    │      │
                  │ （審查者）│    │ （審查者）│      │
                  └────┬─────┘    └────┬─────┘      │
                       │               │             │
                       └───────┬───────┘             │
                               ▼                     │
                    兩邊都 APPROVE？                  │
                       │           │                 │
                    是 │           │ 否 ── 帶理由退回 ┘
                       ▼
                 寫進 docs/計畫/
                 六道閘全綠才 commit
```

**三個角色的權限，寫死在這裡：**

| 角色 | 能做 | 不能做 |
|---|---|---|
| fable | 提案修改整份企劃 | **不能自己批准**；不能直接改檔 |
| claude | 審查、查證、寫檔 | **不能單方通過**；不能改 fable 的提案內容（要改就退回） |
| sol | 審查、提供原意與地基出處 | **不能宣告接受產品**；不能改已准入的 ClaimSpec |

**一條決議要生效，`claude` 與 `sol` 都必須 APPROVE。** 任一方 REJECT 就退回 fable，
**必須附理由**。無理由的 REJECT 不算 REJECT。

**這不推翻既有的接受權。** 唯一的產品接受權仍在 ClaimSpec 閘（見 CLAUDE.md）。
本迴圈決定的是**計畫文字**要怎麼改，不是「哪個 task 算完成」。

## 決議編號與狀態

編號 `R<輪次>-<序號>`，例如 `R1-03`。狀態封閉為五種：

| 狀態 | 意思 |
|---|---|
| `PROPOSED` | fable 提出，尚未有人審 |
| `CLAUDE_OK` / `SOL_OK` | 單邊通過，等另一邊 |
| `APPROVED` | 兩邊都過，可以寫進計畫 |
| `APPLIED` | 已寫進 `docs/計畫/` 且六道閘綠 |
| `REJECTED` | 至少一方退回，**理由必填** |

## 每條決議必須填的欄位

fable 的提案不符這個形狀就直接退回，不進審查：

1. **改什麼**：哪一份計畫、哪個 task 附近、Create／Modify 哪些檔（完整路徑）
2. **為什麼**：不改的後果——具體到「哪一條保證會在帳面上維持綠色」
3. **地基**：官方出處（URL／標準編號）＋權威出處（DOI／arXiv）。
   **引不出來就寫「無地基，這是 nova 的拆解決定」**，不准含糊
4. **加蓋**：nova 多出來的那一條拒絕是什麼？有沒有改到地基的介面？
   （合法動作只有兩種，見 CLAUDE.md 最高原則第 4 條）
5. **固定負控**：control_id、faulty_subject、`must_fail_exactly` 要哪幾條 predicate，
   外加防恆真格
6. **不變式檢查**：會不會撞到 I1–I11（一個 task ≤2 條 claim、≤10 檔、恰好 1 個 commit 步、
   要有 `**ClaimSpec落點:**` 行、要有 `Expected:` 的先紅步）

## 審查者的否決理由（封閉列舉，避免「感覺不對」）

- `NO_FOUNDATION`：宣稱有地基但引不出出處
- `FOUNDATION_MISREAD`：出處存在但不支撐這句話的強度
- `WEAKENS_GUARANTEE`：讓既有保證變弱，即使表面結果一樣
- `CHANGES_INTERFACE`：加蓋改到了地基的介面（那叫分叉不叫加蓋）
- `DOMAIN_LEAK`：把具體產品領域寫進了規格
- `NOT_TESTABLE`：寫不成會 fail 的測試，卻被當成機制
- `INVARIANT_BREAK`：撞到 I1–I11
- `SCOPE_TOO_BIG`：口徑大到一次做不完（CLAUDE.md 明列的不可機械化判斷）
- `ALREADY_TRUE`：repo 現況已經如此，這條是空的

## 帳本

<!-- 每輪的決議表接在這裡，最新的在最上面 -->

（尚未開始）
git commit -m "feat: 宣告追求生命週期"
```

---

### Task 2: 固定 attempt policy 與單調停止 measure

**Files:**
- Create: `規格/追求/AttemptPolicy.schema.json`
- Modify: `nova/領域/追求/模型.py`
- Modify: `nova/領域/追求/決策.py`
- Modify: `nova/領域/追求/test_追求決策.py`
- Create: `驗收/追求/測_有界反覆.py`
- Create: `規格/追求/保證/有界反覆.claim.json`

**Interfaces:**
- Produces: `AttemptPolicy(max_executions<=16, max_paid_calls<=128, absolute_deadline, budget_slice_ref)`。
- Produces: `next_action(measure, resource_fact) -> StartExecution|Wait|Terminal`。

**ClaimSpec:** 【推論】`pursuit.retry.bounded-liveness` 從紅轉綠。

**固定負控:** 【推論】第 17 次 Execution、pause 後把 deadline 向後延、或第 129 次 paid call；三者必須在建立 Execution 前 terminal/reject。

- [ ] **Step 1: 寫 N-1/N/N+1 與 paused-clock table red**

```python
@pytest.mark.parametrize(("attempts", "may_start"), [(15, True), (16, False), (17, False)])
def test_attempt_bound(attempts: int, may_start: bool) -> None:
    assert can_start_attempt(completed_attempts=attempts, limit=16) is may_start
```

- [ ] **Step 2: 跑 fake-time tests 確認 pause 延長 deadline 或第 17 次通過**

Run: `uv run pytest -q 驗收/追求/測_有界反覆.py`

Expected: 【推論】FAIL。

- [ ] **Step 3: 寫 immutable absolute deadline 與 lexicographic measure**

```python
def may_start_execution(state: PursuitAggregate, now: Instant) -> bool:
    return now < state.policy.absolute_deadline and state.execution_count < 16 and state.paid_call_count < 128 and not state.budget_permanently_exhausted
```

- [ ] **Step 4: 跑 property test：任意 event sequence 最多 16 次 start**

Run: `uv run pytest -q nova/領域/追求/test_追求決策.py 驗收/追求/測_有界反覆.py`

Expected: 【推論】PASS；temporary quota wait 不直接成 `EXHAUSTED`。

- [ ] **Step 5: 跑 ClaimSpec**

Run: `uv run python 工具/跑驗收.py --claim pursuit.retry.bounded-liveness`

Expected: 【推論】actual green；三個 boundary negatives direct red。

- [ ] **Step 6: Commit**

```bash
git add 規格/追求/AttemptPolicy.schema.json 規格/追求/保證/有界反覆.claim.json nova/領域/追求 驗收/追求/測_有界反覆.py
git commit -m "feat: 限住追求的重試"
```

---

### Task 3: 串起 Execution、CandidateBundle 與外部 Evaluation

**Files:**
- Create: `nova/領域/追求/端口.py`
- Modify: `nova/領域/追求/公開契約.py`
- Modify: `nova/領域/追求/模型.py`
- Modify: `nova/領域/追求/決策.py`
- Create: `nova/應用/推進追求.py`
- Create: `nova/應用/test_追求服務.py`
- Create: `驗收/追求/測_判準回饋迴圈.py`
- Create: `規格/追求/保證/判準裁定才提交.claim.json`

**Interfaces:**
- Consumes: `ExecutionTerminalRecord`、`CandidateBundleRef`、`Verdict`、`FeedbackPacketRef`。
- Produces: commands `RequestExecution`／`RequestEvaluation` and events `CandidateNominated`／`FeedbackAccepted`／`PursuitSubmitted`。

git commit -m "feat: 展開有界的追求組合"
```

---

### Task 4: 建立 deterministic BEST_BEFORE_DEADLINE 選拔

**Files:**
- Create: `規格/工作/最佳截止前.policy.json`
- Create: `規格/工作/RankingSchema.schema.json`
- Create: `nova/領域/工作/選拔.py`
- Create: `nova/領域/工作/test_選拔.py`
- Modify: `nova/領域/工作/決策.py`
- Create: `驗收/三層流程/測_選拔截止.py`
- Create: `規格/工作/保證/最佳截止前選拔.claim.json`

**Interfaces:**
- Produces: `rank_candidates(schema, verdicts, cutoff_seq) -> SelectionRecord`。
- Produces: cutoff reasons `DEADLINE|ALL_CHILDREN_TERMINAL|PERMANENT_RESOURCE_EXHAUSTION`。

**ClaimSpec:** 【推論】`work.selection.best-before-deadline` 從紅轉綠。

**固定負控:** 【推論】第一個 ACCEPT 不是最高分、相同分數 input iteration order 不同、verdict 在 cutoff seq 後才落盤；winner 必須仍是 cutoff 前依 schema 最佳者，晚到者 excluded。

- [ ] **Step 1: 寫 first-acceptable、tie、late-verdict red**

```python
def test_selection_uses_rank_not_arrival_order() -> None:
    result = rank_candidates(schema_desc("quality"), [accepted("early", 10, seq=5), accepted("late", 20, seq=7)], cutoff_seq=7)
    assert result.winner_ref == candidate_ref("late")
```

- [ ] **Step 2: 跑 tests 確認 arrival order 決定 winner**

Run: `uv run pytest -q nova/領域/工作/test_選拔.py 驗收/三層流程/測_選拔截止.py`

Expected: 【推論】FAIL。

- [ ] **Step 3: 寫 typed normalization、ordered comparator、digest tie-break**

```python
rank_key = tuple(normalize(score[dim.score_id], dim) for dim in schema.dimensions) + (candidate.digest.value,)
```

- [ ] **Step 4: 跑 permutation property tests 與 ClaimSpec**

Run: `uv run pytest -q nova/領域/工作/test_選拔.py 驗收/三層流程/測_選拔截止.py && uv run python 工具/跑驗收.py --claim work.selection.best-before-deadline`

Expected: 【推論】PASS；任意 input permutation 同 SelectionRecord digest。

- [ ] **Step 5: Commit**

```bash
git add 規格/工作/最佳截止前.policy.json 規格/工作/RankingSchema.schema.json 規格/工作/保證/最佳截止前選拔.claim.json nova/領域/工作/選拔.py nova/領域/工作/test_選拔.py nova/領域/工作/決策.py 驗收/三層流程/測_選拔截止.py
git commit -m "feat: 在截止前選出最佳候選"
```

---

### Task 5: 固定 cutoff、取消 losers 與 5 秒 kill grace

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

**ClaimSpec落點:** `execution.backend-capability.closed-vocabulary` → `規格/執行/保證/能力/後端能力封閉.claim.json`（本 task Create）

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

**ClaimSpec落點:** `execution.backend-capability.tool-output-delegation-contract` → `規格/執行/保證/能力/工具輸出代理契約.claim.json`（本 task Create）

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


web search: 
web search: "League Tables and Their Limitations" Goldstein Spiegelhalter DOI ...
web search: 
web search: https://doi.org/10.1111/j.1467-985X.1996.tb00086.x
codex
## 裁決總表

| 決議 | 我的票 | 理由碼 |
|---|---|---|
| R1-01 | APPROVE | — |
| R1-02 | REJECT | `FOUNDATION_MISREAD`, `NOT_TESTABLE` |
| R1-03 | APPROVE | — |
| R1-04 | REJECT | `WEAKENS_GUARANTEE`, `FOUNDATION_MISREAD` |
| R1-05 | REJECT | `FOUNDATION_MISREAD` |
| R1-06 | REJECT | `NOT_TESTABLE`, `WEAKENS_GUARANTEE` |
| R1-07 | REJECT | `WEAKENS_GUARANTEE` |
| R1-08 | REJECT | `INVARIANT_BREAK`, `NOT_TESTABLE` |

---

### R1-01 — APPROVE

內容定址 ref 補掉了目前的恆真格，Task 1／5 的檔案與 claim 口徑也在 I1–I11 內。

寫入時必須保持一個細節：identity classifier 比較的是 `effective_content_digest`，不是僅含間接引用的 manifest source digest；完整 `{semantic_id, revision, digest}` 仍應留在記錄中供稽核。

---

### R1-02 — REJECT

理由碼：`FOUNDATION_MISREAD`, `NOT_TESTABLE`

一句話：分數來源准入是對的，但提案把物理量測的 GUM 義務擴張到所有 ranking score，並用不可機械驗證的 `DECLARED_NEGLIGIBLE + justification_ref` 冒充不確定度證據。

DOI 查證結果：

- Goldstein & Spiegelhalter 該文可驗證的 DOI 是 [`10.2307/2983325`](https://doi.org/10.2307/2983325)。
- `10.1111/j.1467-985X.1996.tb00086.x` 我無法驗證為該文的有效 DOI；目前不能放進地基欄。

fable 要這樣改才會過：

1. 把 `ScoreEvidence` 分成兩類：

   - `EXACT_BY_DEFINITION`：必須帶 deterministic verifier／primitive revision 與 evidence digest，不用虛構 uncertainty。
   - `ESTIMATED`：必須帶 estimator、sampling unit、interval procedure、level、sample size 與 analysis digest。

2. 刪除只有散文 ref 的 `DECLARED_NEGLIGIBLE`；若保留「可忽略」，必須由准入 primitive 機械判定，而非任意 justification。
3. `winner_separation` 必須由 interval 機械推導，呼叫端不得自填。
4. 固定負控增加：

   - 不確定分數冒充 `EXACT_BY_DEFINITION`；
   - 填一個 justification ref 就把 uncertainty 略掉；
   - evaluator revision/candidate digest 不匹配。

5. 地基改用正確 DOI，並明講 GUM 只支撐 measurement-result uncertainty 原則，不支撐所有抽象分數。

---

### R1-03 — APPROVE

這不是改弱保證，而是把尚未准入、且 oracle 從未證成 liveness 的 claim 名稱縮回實際證據強度。

`bounded-liveness` 原名本身才是錯題；改成 `bounded-exhaustion` 不改 judge、負控或接受集合，因此不構成 `WEAKENS_GUARANTEE`。

---

### R1-04 — REJECT

理由碼：`WEAKENS_GUARANTEE`, `FOUNDATION_MISREAD`

一句話：連續相同 digest 只能偵測「完全重複」，不能取得 `NO_PROGRESS` 這個較強名稱的保證。

它確實漏掉：

```text
A → B → A → B
```

也漏掉：

```text
candidate bytes 每次不同
clause verdict vector 永遠沒有改善
```

兩者都可以跑滿 16 次而不觸發提案的 `NO_PROGRESS`。SPIN non-progress cycle 與 disjunctively well-founded transition invariant 恰好說明不能只檢查相鄰狀態相等；引用它們反而暴露了提案判準太弱。

fable 要二選一：

1. 最小版：把 claim 改名為  
   `pursuit.retry.exact-repeat-stagnation-typed`，terminal reason 改成 `EXACT_REPEAT`，並明講它不完成 `NO_PROGRESS` 缺口。

2. 完整版：保留 `NO_PROGRESS`，但加入 frozen `ProgressMeasureSpec`：

   - measure 至少綁 criterion revision 與逐 clause verdict vector；
   - attempt 只有嚴格改善 `best_so_far` 才重置窗口；
   - A→B→A→B 不得因與上一輪不同而算進展；
   - changing bytes、same verdict 必須算無改善；
   - comparator/order 必須事前宣告且 well-founded；
   - property test 要覆蓋遞移閉包與循環。

另外，`max_stagnant_attempts=2` 沒有地基，也未和 `max_executions`／探索空間連動；不得在同一提案中偷偷定成全域預設。

---

### R1-05 — REJECT

理由碼：`FOUNDATION_MISREAD`

一句話：有限次逐 byte 相同的 probe 只能證成「觀測到重複性」，不能證成名為 `SEEDED_OUTPUT_DETERMINISM` 的能力。

N 次一致後第 N+1 次仍可能改變；TTL 與 fingerprint 只限定觀測範圍，不能把抽樣證據升格成普遍決定性。

fable 要這樣改才會過：

- 保留 `SEEDED_REQUEST`。
- 把有限 probe 的能力改名為：

  ```text
  SEEDED_OUTPUT_REPEATABILITY_OBSERVED
  ```

  evidence 必須記 N、環境、fingerprint、request digest、輸出 digests 與 TTL。

- 若仍需要 `SEEDED_OUTPUT_DETERMINISM`，它必須要求 mechanistic／contractual evidence，例如：

  - 純函式 replayer；
  - pinned deterministic engine；
  - backend 明確契約與相應 conformance suite。

不能只靠 N 次 smoke 取得該名稱。

固定負控另加「前 N 次相同、第 N+1 次不同」，證明 observed repeatability 不會被誤判為 determinism。

---

### R1-06 — REJECT

理由碼：`NOT_TESTABLE`, `WEAKENS_GUARANTEE`

一句話：`certified_by != executed_by` 只能證明兩個字串不同；同一主體填兩個 id 就會綠，無法證明提案宣稱的職責分離。

`identity_source` 可偽造時只標 `SELF_CERTIFIED`、仍讓 admission 通過，也與「不得靜默降級」不相容。

此外，`executed_by` 語意不清：它可能指執行測試的 CI runner，也可能指修改 subject 的實作者；Clark–Wilson 要分離的是 certifier 與可改變受保護實體的主體，不是禁止獨立 CI 執行檢查。

fable 要這樣改才會過：

1. 拆清角色：

   ```text
   subject_changed_by
   criterion_authored_by
   admission_decided_by
   evidence_executed_by
   ```

2. 真正約束至少是：

   ```text
   admission_decided_by != subject_changed_by
   ```

3. 身分必須來自 verifier 信任的外部 attestation，例如 protected CI actor、OIDC claim、簽章 key 或控制端准入記錄；PR 自填欄位不得取得分離保證。
4. 無可信 identity source 時必須拒絕需要 SoD 的 admission，或回 typed `UNVERIFIED_ROLE_SEPARATION`；不能只顯示報告後繼續綠。
5. 固定負控加入「同一簽章／同一可信 actor 使用兩個文字 id」。

---

### R1-07 — REJECT

理由碼：`WEAKENS_GUARANTEE`

一句話：提案宣稱 append-only、跨 run 的揭露帳，但 Create 清單沒有任何持久 owner、repository、event 或 crash-recovery 落點；程序重啟即可把 cap 洗掉。

`nova/權威/判準/揭露帳本.py` 又受 `allow_io=false` 約束，因此它本身不能完成持久化。現有固定負控只測同一程序內的第 `cap+1` 次，不會殺掉「SIGKILL 後從零開始」的錯誤實作。

fable 要這樣改才會過：

1. ledger 必須成為 state owner 管理的持久 aggregate／事件，而非單純權威層記憶體物件。
2. key 必須使用 sealed pool lineage，而不只 `(criterion revision, sealed case set)`；換 revision、建立 sibling／superseding Pursuit 不得重置。
3. disclosure 必須採「先持久記帳，再釋出」；crash gap 必須明講。
4. at-least-once 重送只能重送同一 packet digest／disclosure id，不能重複消耗或產生新資訊。
5. 固定負控至少增加：

   - `cap` 前 SIGKILL、重啟後繼續釋出；
   - sibling／superseding Pursuit 洗額度；
   - 換 criterion revision 但沿用相同 sealed lineage；
   - ledger commit 前就把 feedback 送出去。

Theorem 17 可以留，但只能支撐「有限 transcript range 產生有限 max-information 上界」；不能用來證明目前 cap 數值足以維持統計有效性。

---

### R1-08 — REJECT

理由碼：`INVARIANT_BREAK`, `NOT_TESTABLE`

一句話：Task 2 宣稱「釘版外部統計套件」，卻沒有列出任何 dependency／lockfile 修改，也沒有指定套件與版本；照寫不是沒有釘版，就是要做未宣告的跨計畫 Modify。

這確實是把架構決定藏在 task 散文裡。`allow_io=false` 本身不是衝突：純統計套件可以在無 I/O 的權威函式中運算；問題是依賴與 supply-chain 身分完全沒進 Files／fingerprint。

fable 要這樣改才會過：

1. Task 2 增加：

   ```text
   Modify: pyproject.toml
   Modify: uv.lock
   ```

2. 明確指定採用的統計套件與 API，先確認 CPython 3.14.7 支援；不能只寫「外部套件」。
3. `架構/目錄規則.toml` 必須明確允許 `nova/權威/評測/分析.py` 引用該 pure-compute dependency；若 Task 1 的 Modify 要承載此規則，文字需明寫。
4. analysis fingerprint 必須綁：

   ```text
   package name
   package version
   locked artifact/hash
   analysis function/revision
   parameters
   analysis seed
   ```

5. 增加固定負控：

   - 相同 evidence 但換統計套件版本；
   - lock artifact 改變；
   - analysis fingerprint 漏 package digest。

6. `INCONCLUSIVE` 與 `REJECTED` 的分界必須事前寫死：

   - 證據不足／區間過寬：`INCONCLUSIVE`；
   - 證據足以顯示超出允許 margin：`REJECTED`；
   - protocol／pair 缺失：`INVALIDATED`。

補完後，06B 的分層、編號、三個 task 口徑與領域中立性本身可以通過。
tokens used
48,834
## 裁決總表

| 決議 | 我的票 | 理由碼 |
|---|---|---|
| R1-01 | APPROVE | — |
| R1-02 | REJECT | `FOUNDATION_MISREAD`, `NOT_TESTABLE` |
| R1-03 | APPROVE | — |
| R1-04 | REJECT | `WEAKENS_GUARANTEE`, `FOUNDATION_MISREAD` |
| R1-05 | REJECT | `FOUNDATION_MISREAD` |
| R1-06 | REJECT | `NOT_TESTABLE`, `WEAKENS_GUARANTEE` |
| R1-07 | REJECT | `WEAKENS_GUARANTEE` |
| R1-08 | REJECT | `INVARIANT_BREAK`, `NOT_TESTABLE` |

---

### R1-01 — APPROVE

內容定址 ref 補掉了目前的恆真格，Task 1／5 的檔案與 claim 口徑也在 I1–I11 內。

寫入時必須保持一個細節：identity classifier 比較的是 `effective_content_digest`，不是僅含間接引用的 manifest source digest；完整 `{semantic_id, revision, digest}` 仍應留在記錄中供稽核。

---

### R1-02 — REJECT

理由碼：`FOUNDATION_MISREAD`, `NOT_TESTABLE`

一句話：分數來源准入是對的，但提案把物理量測的 GUM 義務擴張到所有 ranking score，並用不可機械驗證的 `DECLARED_NEGLIGIBLE + justification_ref` 冒充不確定度證據。

DOI 查證結果：

- Goldstein & Spiegelhalter 該文可驗證的 DOI 是 [`10.2307/2983325`](https://doi.org/10.2307/2983325)。
- `10.1111/j.1467-985X.1996.tb00086.x` 我無法驗證為該文的有效 DOI；目前不能放進地基欄。

fable 要這樣改才會過：

1. 把 `ScoreEvidence` 分成兩類：

   - `EXACT_BY_DEFINITION`：必須帶 deterministic verifier／primitive revision 與 evidence digest，不用虛構 uncertainty。
   - `ESTIMATED`：必須帶 estimator、sampling unit、interval procedure、level、sample size 與 analysis digest。

2. 刪除只有散文 ref 的 `DECLARED_NEGLIGIBLE`；若保留「可忽略」，必須由准入 primitive 機械判定，而非任意 justification。
3. `winner_separation` 必須由 interval 機械推導，呼叫端不得自填。
4. 固定負控增加：

   - 不確定分數冒充 `EXACT_BY_DEFINITION`；
   - 填一個 justification ref 就把 uncertainty 略掉；
   - evaluator revision/candidate digest 不匹配。

5. 地基改用正確 DOI，並明講 GUM 只支撐 measurement-result uncertainty 原則，不支撐所有抽象分數。

---

### R1-03 — APPROVE

這不是改弱保證，而是把尚未准入、且 oracle 從未證成 liveness 的 claim 名稱縮回實際證據強度。

`bounded-liveness` 原名本身才是錯題；改成 `bounded-exhaustion` 不改 judge、負控或接受集合，因此不構成 `WEAKENS_GUARANTEE`。

---

### R1-04 — REJECT

理由碼：`WEAKENS_GUARANTEE`, `FOUNDATION_MISREAD`

一句話：連續相同 digest 只能偵測「完全重複」，不能取得 `NO_PROGRESS` 這個較強名稱的保證。

它確實漏掉：

```text
A → B → A → B
```

也漏掉：

```text
candidate bytes 每次不同
clause verdict vector 永遠沒有改善
```

兩者都可以跑滿 16 次而不觸發提案的 `NO_PROGRESS`。SPIN non-progress cycle 與 disjunctively well-founded transition invariant 恰好說明不能只檢查相鄰狀態相等；引用它們反而暴露了提案判準太弱。

fable 要二選一：

1. 最小版：把 claim 改名為  
   `pursuit.retry.exact-repeat-stagnation-typed`，terminal reason 改成 `EXACT_REPEAT`，並明講它不完成 `NO_PROGRESS` 缺口。

2. 完整版：保留 `NO_PROGRESS`，但加入 frozen `ProgressMeasureSpec`：

   - measure 至少綁 criterion revision 與逐 clause verdict vector；
   - attempt 只有嚴格改善 `best_so_far` 才重置窗口；
   - A→B→A→B 不得因與上一輪不同而算進展；
   - changing bytes、same verdict 必須算無改善；
   - comparator/order 必須事前宣告且 well-founded；
   - property test 要覆蓋遞移閉包與循環。

另外，`max_stagnant_attempts=2` 沒有地基，也未和 `max_executions`／探索空間連動；不得在同一提案中偷偷定成全域預設。

---

### R1-05 — REJECT

理由碼：`FOUNDATION_MISREAD`

一句話：有限次逐 byte 相同的 probe 只能證成「觀測到重複性」，不能證成名為 `SEEDED_OUTPUT_DETERMINISM` 的能力。

N 次一致後第 N+1 次仍可能改變；TTL 與 fingerprint 只限定觀測範圍，不能把抽樣證據升格成普遍決定性。

fable 要這樣改才會過：

- 保留 `SEEDED_REQUEST`。
- 把有限 probe 的能力改名為：

  ```text
  SEEDED_OUTPUT_REPEATABILITY_OBSERVED
  ```

  evidence 必須記 N、環境、fingerprint、request digest、輸出 digests 與 TTL。

- 若仍需要 `SEEDED_OUTPUT_DETERMINISM`，它必須要求 mechanistic／contractual evidence，例如：

  - 純函式 replayer；
  - pinned deterministic engine；
  - backend 明確契約與相應 conformance suite。

不能只靠 N 次 smoke 取得該名稱。

固定負控另加「前 N 次相同、第 N+1 次不同」，證明 observed repeatability 不會被誤判為 determinism。

---

### R1-06 — REJECT

理由碼：`NOT_TESTABLE`, `WEAKENS_GUARANTEE`

一句話：`certified_by != executed_by` 只能證明兩個字串不同；同一主體填兩個 id 就會綠，無法證明提案宣稱的職責分離。

`identity_source` 可偽造時只標 `SELF_CERTIFIED`、仍讓 admission 通過，也與「不得靜默降級」不相容。

此外，`executed_by` 語意不清：它可能指執行測試的 CI runner，也可能指修改 subject 的實作者；Clark–Wilson 要分離的是 certifier 與可改變受保護實體的主體，不是禁止獨立 CI 執行檢查。

fable 要這樣改才會過：

1. 拆清角色：

   ```text
   subject_changed_by
   criterion_authored_by
   admission_decided_by
   evidence_executed_by
   ```

2. 真正約束至少是：

   ```text
   admission_decided_by != subject_changed_by
   ```

3. 身分必須來自 verifier 信任的外部 attestation，例如 protected CI actor、OIDC claim、簽章 key 或控制端准入記錄；PR 自填欄位不得取得分離保證。
4. 無可信 identity source 時必須拒絕需要 SoD 的 admission，或回 typed `UNVERIFIED_ROLE_SEPARATION`；不能只顯示報告後繼續綠。
5. 固定負控加入「同一簽章／同一可信 actor 使用兩個文字 id」。

---

### R1-07 — REJECT

理由碼：`WEAKENS_GUARANTEE`

一句話：提案宣稱 append-only、跨 run 的揭露帳，但 Create 清單沒有任何持久 owner、repository、event 或 crash-recovery 落點；程序重啟即可把 cap 洗掉。

`nova/權威/判準/揭露帳本.py` 又受 `allow_io=false` 約束，因此它本身不能完成持久化。現有固定負控只測同一程序內的第 `cap+1` 次，不會殺掉「SIGKILL 後從零開始」的錯誤實作。

fable 要這樣改才會過：

1. ledger 必須成為 state owner 管理的持久 aggregate／事件，而非單純權威層記憶體物件。
2. key 必須使用 sealed pool lineage，而不只 `(criterion revision, sealed case set)`；換 revision、建立 sibling／superseding Pursuit 不得重置。
3. disclosure 必須採「先持久記帳，再釋出」；crash gap 必須明講。
4. at-least-once 重送只能重送同一 packet digest／disclosure id，不能重複消耗或產生新資訊。
5. 固定負控至少增加：

   - `cap` 前 SIGKILL、重啟後繼續釋出；
   - sibling／superseding Pursuit 洗額度；
   - 換 criterion revision 但沿用相同 sealed lineage；
   - ledger commit 前就把 feedback 送出去。

Theorem 17 可以留，但只能支撐「有限 transcript range 產生有限 max-information 上界」；不能用來證明目前 cap 數值足以維持統計有效性。

---

### R1-08 — REJECT

理由碼：`INVARIANT_BREAK`, `NOT_TESTABLE`

一句話：Task 2 宣稱「釘版外部統計套件」，卻沒有列出任何 dependency／lockfile 修改，也沒有指定套件與版本；照寫不是沒有釘版，就是要做未宣告的跨計畫 Modify。

這確實是把架構決定藏在 task 散文裡。`allow_io=false` 本身不是衝突：純統計套件可以在無 I/O 的權威函式中運算；問題是依賴與 supply-chain 身分完全沒進 Files／fingerprint。

fable 要這樣改才會過：

1. Task 2 增加：

   ```text
   Modify: pyproject.toml
   Modify: uv.lock
   ```

2. 明確指定採用的統計套件與 API，先確認 CPython 3.14.7 支援；不能只寫「外部套件」。
3. `架構/目錄規則.toml` 必須明確允許 `nova/權威/評測/分析.py` 引用該 pure-compute dependency；若 Task 1 的 Modify 要承載此規則，文字需明寫。
4. analysis fingerprint 必須綁：

   ```text
   package name
   package version
   locked artifact/hash
   analysis function/revision
   parameters
   analysis seed
   ```

5. 增加固定負控：

   - 相同 evidence 但換統計套件版本；
   - lock artifact 改變；
   - analysis fingerprint 漏 package digest。

6. `INCONCLUSIVE` 與 `REJECTED` 的分界必須事前寫死：

   - 證據不足／區間過寬：`INCONCLUSIVE`；
   - 證據足以顯示超出允許 margin：`REJECTED`；
   - protocol／pair 缺失：`INVALIDATED`。

補完後，06B 的分層、編號、三個 task 口徑與領域中立性本身可以通過。
