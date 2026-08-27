codex
這一輪需要外部查證。我會用 ongoing brainstorming 的架構路徑，把每個缺口收斂成「權威來源→落點→固定負控→核心判定」，並特別檢查兩個信任根：原語目錄的建立權，以及 admitted claim closure 的不可改寫性。
web search: 
web search: site:platform.openai.com/docs prompt versioning prompt id versions official ...
web search: 
web search: site:platform.openai.com/docs/guides prompt management version prompts official OpenAI ...
web search: 
web search: W3C PROV recommendation provenance entities activities agents official ...
web search: 
web search: OpenAI reusable prompts dashboard version prompt_id variables official documentation ...
web search: 
web search: site:platform.openai.com/docs/guides/evals best practices graders human feedback official ...
web search: 
web search: SLSA provenance build artifacts official specification trusted builder provenance ...
exec
/bin/zsh -lc "rg -n '"'^### Task|RankingSchema|rank|score|FeedbackPacket|CaseBurn|PrimitiveCatalog|原語目錄'"' docs/計畫/06-判準評估與隔離回饋.md docs/計畫/08-目標追求生命週期.md docs/計畫/09-持久工作協調與選拔.md docs/計畫/01-可執行保證語言.md docs/計畫/12-可宣告約束與權威閘.md docs/計畫/20-整體組裝與跨系統驗收.md | sed -n '1,520p'" in /Users/sbu/nova
 succeeded in 0ms:
docs/計畫/20-整體組裝與跨系統驗收.md:71:│   ├── 四策略工作.json                      — four Pursuits、replayer scripts與ranking facts。
docs/計畫/20-整體組裝與跨系統驗收.md:103:### Task 1: 建立 exact-digest spec catalog 與 bootstrap closure
docs/計畫/20-整體組裝與跨系統驗收.md:171:### Task 2: 組裝 production process roots 並禁止 fake 注入
docs/計畫/20-整體組裝與跨系統驗收.md:240:### Task 3: 將Application與CLI接到同一production root
docs/計畫/20-整體組裝與跨系統驗收.md:297:### Task 4: 對五種 ExecutorBackend 跑同一契約矩陣
docs/計畫/20-整體組裝與跨系統驗收.md:360:### Task 5: 跑一個四策略 Work 的三層可信收斂
docs/計畫/20-整體組裝與跨系統驗收.md:418:### Task 6: 對全部程序做 total SIGKILL 與持久重建矩陣
docs/計畫/20-整體組裝與跨系統驗收.md:481:### Task 7: 驗外部效果 crash gaps 與 backend update 誠實能力
docs/計畫/20-整體組裝與跨系統驗收.md:537:### Task 8: 驗判準、知識、約束、資源跨面不靜默降級
docs/計畫/20-整體組裝與跨系統驗收.md:591:### Task 9: 實測 admission caps、soak、burst與事件發布 SLO
docs/計畫/20-整體組裝與跨系統驗收.md:656:### Task 10: 驗 checkpoint／segment／tail／backup 的跨層連續
docs/計畫/20-整體組裝與跨系統驗收.md:714:### Task 11: 驗 browser 只靠 GraphBundle＋跨層事件流重建
docs/計畫/20-整體組裝與跨系統驗收.md:770:### Task 12: 建立不會恆綠的 release gate 與交付證據
docs/計畫/20-整體組裝與跨系統驗收.md:846:### Task 13: 組合 core deployability 與 exact-backend live readiness
docs/計畫/12-可宣告約束與權威閘.md:112:### Task 1: 寫 ConstraintSpec 1.0.0 schema 與 neutral kernel
docs/計畫/12-可宣告約束與權威閘.md:171:### Task 2: Admission 必須閉合到事前 direct-red evidence
docs/計畫/12-可宣告約束與權威閘.md:225:### Task 3: 各 owner 擁有自己的 ENFORCED lifecycle且不自動續期
docs/計畫/12-可宣告約束與權威閘.md:284:### Task 4: 建立 owner-specific gates與 capability fail-closed
docs/計畫/12-可宣告約束與權威閘.md:344:### Task 5: capability不足時強制fail closed
docs/計畫/12-可宣告約束與權威閘.md:395:### Task 6: 把 ADVISORY constraint納入知識治理與16條 overlap cap
docs/計畫/12-可宣告約束與權威閘.md:450:### Task 7: 在Execution前精確計量、pack並拒絕required overflow
docs/計畫/12-可宣告約束與權威閘.md:504:### Task 8: 三處揭露省略與真compaction重掛
docs/計畫/12-可宣告約束與權威閘.md:554:### Task 9: snapshot失效後必須顯式rebase
docs/計畫/12-可宣告約束與權威閘.md:602:### Task 10: 只能提案，啟用要10分鐘one-use ApprovalEnvelope
docs/計畫/12-可宣告約束與權威閘.md:659:### Task 11: 有界偵測重複失敗並只建立普通authoring Work
docs/計畫/12-可宣告約束與權威閘.md:711:### Task 12: 機械驗證owner/path/gate與禁止中央約束桶
docs/計畫/01-可執行保證語言.md:24:- 【推論】Python識別字可全中文或全ASCII，必須NFC，禁止同一identifier混用Han與Latin以免同形／規約漂移；dunder與前導underscore不計script。跨程序semantic id、event/schema field、DB table/column、CLI executable、failure code與shell variable/function name一律ASCII。Python允許Unicode identifiers並在解析時做NFKC normalization；Bash name只接受字母、數字、underscore且不能以數字開頭，因此shell不適用中文命名。
docs/計畫/01-可執行保證語言.md:29:【推論】輸入是 immutable ClaimSpec bytes、PrimitiveCatalog digest、BindingManifest digest、IsolationOffer digest；輸出是 immutable TestPlan 與 typed CaseResult。statement 只供人讀，沒有判定權。
docs/計畫/01-可執行保證語言.md:107:### Task 1: 固定 CPython 與中文測試／mutation 工具鏈
docs/計畫/01-可執行保證語言.md:170:### Task 2: 建立格式、lint、docstring與strict型別閘
docs/計畫/01-可執行保證語言.md:219:### Task 3: 建立唯一落點、依賴與規模閘
docs/計畫/01-可執行保證語言.md:271:### Task 4: 建立Python Unicode與跨程序ASCII雙軌閘
docs/計畫/01-可執行保證語言.md:323:### Task 5: 建立 canonical identity、digest 與 typed failure union
docs/計畫/01-可執行保證語言.md:400:### Task 6: 封閉 ClaimSpec 0.2.0 meta-schema、效果條件與 typed model
docs/計畫/01-可執行保證語言.md:490:### Task 7: 確定性編譯 PrimitiveCatalog、predicate 與 TestPlan
docs/計畫/01-可執行保證語言.md:500:- Consumes: `ClaimSpec`、`PrimitiveCatalog`、`BindingManifest`、`IsolationOffer`。
docs/計畫/01-可執行保證語言.md:513:def test_相同輸入編譯成相同_plan_digest(有效_claim: ClaimSpec, catalog: PrimitiveCatalog) -> None:
docs/計畫/01-可執行保證語言.md:529:def compile_claim(spec: ClaimSpec, catalog: PrimitiveCatalog, binding: BindingManifest, offer: IsolationOffer) -> TestPlan:
docs/計畫/01-可執行保證語言.md:560:### Task 8: 執行 actual／positive／negative 並保留 direct red
docs/計畫/01-可執行保證語言.md:628:### Task 9: 讓外部 pytest framework 只轉譯、不改判定
docs/計畫/01-可執行保證語言.md:692:### Task 10: 寫第一份 wall-limit ClaimSpec 並真的紅／綠
docs/計畫/01-可執行保證語言.md:763:### Task 11: 禁止 raw mutation score 取得驗收權
docs/計畫/01-可執行保證語言.md:833:### Task 12: 補跑 Tasks 1–4 的工程 ClaimSpec 閘
docs/計畫/01-可執行保證語言.md:872:### Task 13: 把工程閘接上自動執行點
docs/計畫/01-可執行保證語言.md:934:### Task 14: 把「跑一批指定突變」包成有測試的工具
docs/計畫/09-持久工作協調與選拔.md:5:**Goal:** 【推論】建立跨程序、跨崩潰的 Work portfolio：持久排程最多八個 Pursuit、在明確 cutoff 前收集合格候選、以釘版 ranking schema 確定性選最好，並在 7 天／8,192 operational events／總預算等界線內必然終止。
docs/計畫/09-持久工作協調與選拔.md:7:**Architecture:** 【推論】Work 是第三個垂直生命週期與父聚合，擁有目標、child set、portfolio budget、pinned criterion/knowledge/allocation/ranking refs、cutoff 與 SelectionRecord。它只建立／取消 Pursuit，不直接建立 Execution。排程拓撲固定是持久佇列加顯式父子；禁止 child-to-child prerequisite、跨 Work join 與 arbitrary DAG edge。選拔以 `cutoff_global_seq` 封住晚到 verdict，再以 schema-defined ordered dimensions 與 digest tie-break 確定結果。
docs/計畫/09-持久工作協調與選拔.md:25:【推論】`RankingSchema` 是 ordered nonempty dimensions：每維必填 `score_id`、`value_type=INTEGER|DECIMAL`、`direction=ASC|DESC`、`missing=REJECT_CANDIDATE`；維度全相同時以 candidate digest ASCII ascending tie-break。自由文字不能參與 comparator。
docs/計畫/09-持久工作協調與選拔.md:27:【推論】SelectionRecord 固定保存 eligible candidate refs、每維 normalized values、excluded reason、ranking schema digest、cutoff seq 與 winner ref；Work 只能在 record append 成功後進 terminal。
docs/計畫/09-持久工作協調與選拔.md:36:├── 最佳截止前.policy.json                    — cutoff、ranking、cancel grace policy。
docs/計畫/09-持久工作協調與選拔.md:37:├── RankingSchema.schema.json                 — ordered typed score dimensions。
docs/計畫/09-持久工作協調與選拔.md:53:├── 選拔.py                                   — deterministic ranking comparator/record。
docs/計畫/09-持久工作協調與選拔.md:57:└── test_選拔.py                              — rank/cutoff/tie/missing-score tests。
docs/計畫/09-持久工作協調與選拔.md:84:### Task 1: 宣告 Work machine、bounds 與 pinned creation contract
docs/計畫/09-持久工作協調與選拔.md:99:- Pins: criterion/ranking/knowledge/allocation/machine/attempt-policy digests and total budget ref。
docs/計畫/09-持久工作協調與選拔.md:147:### Task 2: 用 FlowSpec 封死父子基數並拒絕一般 DAG
docs/計畫/09-持久工作協調與選拔.md:197:### Task 3: 實作 portfolio fan-out 與原子 budget slicing
docs/計畫/09-持久工作協調與選拔.md:250:### Task 4: 建立 deterministic BEST_BEFORE_DEADLINE 選拔
docs/計畫/09-持久工作協調與選拔.md:254:- Create: `規格/工作/RankingSchema.schema.json`
docs/計畫/09-持久工作協調與選拔.md:262:- Produces: `rank_candidates(schema, verdicts, cutoff_seq) -> SelectionRecord`。
docs/計畫/09-持久工作協調與選拔.md:272:def test_selection_uses_rank_not_arrival_order() -> None:
docs/計畫/09-持久工作協調與選拔.md:273:    result = rank_candidates(schema_desc("quality"), [accepted("early", 10, seq=5), accepted("late", 20, seq=7)], cutoff_seq=7)
docs/計畫/09-持久工作協調與選拔.md:286:rank_key = tuple(normalize(score[dim.score_id], dim) for dim in schema.dimensions) + (candidate.digest.value,)
docs/計畫/09-持久工作協調與選拔.md:298:git add 規格/工作/最佳截止前.policy.json 規格/工作/RankingSchema.schema.json 規格/工作/保證/最佳截止前選拔.claim.json nova/領域/工作/選拔.py nova/領域/工作/test_選拔.py nova/領域/工作/決策.py 驗收/三層流程/測_選拔截止.py
docs/計畫/09-持久工作協調與選拔.md:304:### Task 5: 固定 cutoff、取消 losers 與 5 秒 kill grace
docs/計畫/09-持久工作協調與選拔.md:356:### Task 6: 強制 7 天 absolute deadline 與 8,192 event terminal reserve
docs/計畫/09-持久工作協調與選拔.md:412:### Task 7: 實作持久佇列、公平租約與全程序恢復
docs/計畫/09-持久工作協調與選拔.md:468:### Task 8: 讓健康缺陷只能提案普通維護 Work
docs/計畫/09-持久工作協調與選拔.md:532:【推論】Task 4 需由新審查者用反序、同分、missing score、late seq 四種資料重算 winner。Task 7 必須真的起子程序並 SIGKILL，不接受 mock restart。完成此 plan 才能把知識、效果、介面與前端接到穩定 Work lifecycle。
docs/計畫/08-目標追求生命週期.md:26:【推論】每次 retry 的輸入由 `checkpoint_ref + FeedbackPacket ref + next Execution selection` 組成；raw verdict 或 sealed evidence 不可進 execution input。
docs/計畫/08-目標追求生命週期.md:70:### Task 1: 宣告 Pursuit machine、identity 與 terminal union
docs/計畫/08-目標追求生命週期.md:135:### Task 2: 固定 attempt policy 與單調停止 measure
docs/計畫/08-目標追求生命週期.md:195:### Task 3: 串起 Execution、CandidateBundle 與外部 Evaluation
docs/計畫/08-目標追求生命週期.md:208:- Consumes: `ExecutionTerminalRecord`、`CandidateBundleRef`、`Verdict`、`FeedbackPacketRef`。
docs/計畫/08-目標追求生命週期.md:261:### Task 4: 暫停、checkpoint 與換後端接手
docs/計畫/08-目標追求生命週期.md:321:### Task 5: 固定 identity 變更矩陣與 supersedes 逃生路徑
docs/計畫/08-目標追求生命週期.md:372:### Task 6: 隔離平行 Pursuit 的 workspace 與 evidence lineage
docs/計畫/08-目標追求生命週期.md:424:### Task 7: 讓 Pursuit lease/replay 在 crash 後不多生 attempt
docs/計畫/06-判準評估與隔離回饋.md:25:【推論】`Verdict` 是 evaluation authority 的產物，包含每條 claim 的 typed result與 evidence refs；它不包含 ClaimSpec source bytes。`FeedbackPacket` 是衍生物，不是 verdict 本體。
docs/計畫/06-判準評估與隔離回饋.md:46:├── 回饋閘.py                                 — raw result -> FeedbackPacket reducer。
docs/計畫/06-判準評估與隔離回饋.md:73:### Task 1: 宣告 CriterionDefinition 與 Evaluation lifecycle
docs/計畫/06-判準評估與隔離回饋.md:139:### Task 2: 建立 isolation capability 協商且拒絕降級
docs/計畫/06-判準評估與隔離回饋.md:192:### Task 3: 產生互斥 candidate/evaluator projection
docs/計畫/06-判準評估與隔離回饋.md:247:### Task 4: 產生 typed verdict 並區分 harness fault
docs/計畫/06-判準評估與隔離回饋.md:303:### Task 5: 只輸出 clause-level gated feedback
docs/計畫/06-判準評估與隔離回饋.md:313:- Produces: `reduce_feedback(verdict, policy) -> FeedbackPacket`。
docs/計畫/06-判準評估與隔離回饋.md:318:**固定負控:** 【推論】raw assertion 為 `expected SECRET-ANSWER-441, got 0`；FeedbackPacket canonical bytes 不得含 `SECRET`、`ANSWER`、`441` 或 raw repr，但要含失敗 `clause_id`。
docs/計畫/06-判準評估與隔離回饋.md:339:return FeedbackPacket(items=tuple(FeedbackItem(clause_id=r.clause_id, outcome_class=map_outcome(r), location_bucket=map_location(r), retryability=map_retry(r)) for r in verdict.results))
docs/計畫/06-判準評估與隔離回饋.md:357:### Task 6: 實作「揭露即燒掉」且 crash-safe
docs/計畫/06-判準評估與隔離回饋.md:368:- Produces: atomic `CaseBurned` event before raw reveal bytes are returned。
docs/計畫/06-判準評估與隔離回饋.md:372:**固定負控:** 【推論】在 `CaseBurned` commit 前／後 SIGKILL；commit 前不得收到 raw detail，commit 後重啟不得再次選中該 case。
docs/計畫/06-判準評估與隔離回饋.md:379:    assert trace.committed("CaseBurned")
docs/計畫/06-判準評估與隔離回饋.md:389:- [ ] **Step 3: 先 append-once `CaseBurned`，再從 CAS 釋出 raw bytes**
docs/計畫/06-判準評估與隔離回饋.md:411:### Task 7: 驗證目前威脅聲明沒有越界
docs/計畫/06-判準評估與隔離回饋.md:463:- 【推論】raw assertion repr 不進 FeedbackPacket；clause id 與 retry class 保留最小梯度。

codex
先給排序結論：

1. `ProtectedClaimClosure` 與受信原語目錄：先補。這是 ClaimSpec 信任根本身的洞。
2. Prompt artifact：再補。現有 Pursuit identity 固定負控正在測不存在的物件。
3. Score provenance：必須在 plan 09 Task 4 前補。
4. Feedback information budget：必須在 plan 06 放出第一份 FeedbackPacket 前補。
5. Visual evaluation：核心保留通用 evaluator／primitive admission；視覺實作是必裝外掛，不混進最小核心。

我判定遺失的第五份報告最可能對應「受信擴充目錄／admission root」，不是一般 metrics。理由是它同時穿過工具、輸出解析、錯誤處理與驗證：目前 caller 能自行定義「系統認得哪些原語」，等於 caller 能擴張 ClaimSpec 語言。

---

# 缺口一：Prompt artifact 懸空

## (a) 業界既有做法

業界名稱是：

- Prompt Management
- Versioned Prompt Template／Prompt Artifact
- Prompt ID + Version + Variables

AWS Bedrock Prompt Management 將 prompt 做成可儲存、測試、比較、版本化及部署的 artifact；版本包含 messages、system prompt、模型／推論設定與工具設定。[Amazon Bedrock Prompt Management](https://docs.aws.amazon.com/bedrock/latest/userguide/prompt-management.html)

OpenAI Agents SDK 的 `Prompt` 也明確是：

```text
id
version
variables
```

而不是呼叫端隨手拼出的字串。[OpenAI Agents SDK Prompts](https://openai.github.io/openai-agents-python/ref/prompts/)

【設計判斷】nova 不應照搬任一 provider 的 prompt resource，但應採相同原則：prompt family 是有版本、有內容摘要、可解析成 exact outbound segments 的 artifact。

## (b) nova 落點

這個缺口有三段，不能塞進同一 task。

### 1. plan 08：PromptFamily 的 identity 語義

位置：plan 08 Task 1 之後、現 Task 2 之前。原因是 Task 1 已把 `prompt_family_ref` 放進 Pursuit identity，而 Task 5 才驗 identity change，定義必須先於比較。

Create：

```text
規格/追求/PromptFamily.schema.json
nova/領域/追求/提示身分.py
nova/領域/追求/test_提示身分.py
驗收/追求/測_提示內容身分.py
規格/追求/保證/提示身分依有效內容.claim.json
```

`PromptFamilyRef` 必須包含：

```text
prompt_family_id
revision
source_digest
effective_prompt_digest
segment_contract_digest
variable_schema_digest
tool_policy_ref
```

identity change 比較：

```text
effective_prompt_digest
+ segment_contract_digest
+ variable_schema_digest
+ tool_policy_ref digest
```

不能比較裸 `prompt_family_id`。

因此：

- 不同 id、相同 effective bytes與相同 contracts：`SAME_PURSUIT`，但留下 ref changed audit event。
- 同一 id、digest 不同：拒絕 floating ref，或 `NEW_PURSUIT_REQUIRED`。
- `latest`：schema admission red。

### 2. plan 10：PromptFamily 的治理與 admission

位置：plan 10 的 assertion admission/DAG 已成立後、KnowledgeSnapshot resolve 前。

Create：

```text
規格/知識/PromptFamilyAdmission.schema.json
nova/權威/知識/提示族治理.py
nova/權威/知識/test_提示族治理.py
驗收/知識/測_提示族准入與撤銷.py
規格/知識/保證/提示族內容不可漂移.claim.json
```

【設計判斷】可重用 PromptFamily 屬於「怎麼做」的制度知識，因此治理權歸 Knowledge Authority；Pursuit只 pin exact ref，不能自行 activate。

PromptFamily 內容至少涵蓋：

```text
segments[]
variables schema
canonical ordering
required tool policy
static document refs
serialization policy
minimum delivery capabilities
```

### 3. plan 12：PromptPlan 與完整前綴

位置：Task 6 之後、Task 7 context packing 之前，獨立 task。

Create：

```text
規格/執行/PromptPlan.schema.json
規格/執行/PromptDeliveryPolicy.schema.json
nova/領域/執行/提示計畫.py
nova/領域/執行/test_提示計畫.py
驗收/約束/測_完整提示前綴.py
規格/執行/保證/提示前綴逐位元組固定.claim.json
```

`PromptPlan` 必須包含有序 segments：

```text
system_policy
tool_contract
fixed_documents
task_intent
knowledge
advisory_constraints
checkpoint
reduced_feedback
```

每段帶：

```text
content_ref
semantic_role
authority_source
delivery_requirement
canonical_order
```

最終 `InvocationEnvelope` 必須記：

```text
prompt_plan_ref
effective_prompt_digest
actual_outbound_payload_digest
segment_delivery_manifest
```

KV cache hit/miss驗的是最終 outbound payload，而不只 knowledge serialization 後段。

## (c) 固定負控

至少四個：

1. 不同 refs 指向完全相同 effective bytes，classifier 回 `NEW_PURSUIT_REQUIRED`。

   必須紅在：

   ```text
   prompt_identity_uses_effective_digest
   ```

2. 同一 semantic id 下 source bytes 漂移，但 classifier 回 `SAME_PURSUIT`。

   必須紅在：

   ```text
   floating_prompt_ref_is_rejected
   ```

3. 工具清單或固定文件順序改變，但 `effective_prompt_digest` 不變。

   必須紅在：

   ```text
   effective_prompt_digest_covers_full_prefix
   ```

4. cache hit 與 miss 的 knowledge bytes 相同，但 system/tool prefix 不同，整體 claim仍綠。

   必須紅在：

   ```text
   cached_and_uncached_outbound_payloads_are_byte_identical
   ```

## (d) 核心或外掛

【設計判斷】核心。

按控制端給的判準，整份拿掉後，plan 08 的 prompt-family identity 固定負控仍會對裸字串分類器「正常紅／綠」，卻完全不能辨識實際內容漂移；也就是負控退化成只驗欄位名稱，對真正錯誤恆真。

具體 prompt templates、遊戲 prompt family、elicitation prompt則是外掛／受治理知識。

---

# 缺口二：Ranking score 沒有來源守衛

## (a) 業界既有做法

名稱是：

- Evaluation lineage／ML metadata
- Metric provenance
- Evaluation run metadata
- Grounded／calibrated evaluator

W3C PROV 的核心是 Entity、Activity、Agent，並以 `used`、`wasGeneratedBy`、`wasDerivedFrom`、`wasAttributedTo` 表達資料如何產生以及誰負責；用途正包含評估品質、可靠性與可信度。[W3C PROV Overview](https://www.w3.org/TR/prov-overview/)

Google Vertex ML Metadata明確要求記錄：

- 哪版模型；
- 哪份 evaluation data；
- 哪段 code；
- 哪些參數；
- 哪個 run；
- 產生了哪些 metrics。

目的包括重跑 workflow 與判斷哪個版本產生某項分數。[Vertex ML Metadata](https://cloud.google.com/vertex-ai/docs/ml-metadata/introduction)

對 model judge，Google官方做法是拿 human ratings 當 ground truth，計算 balanced accuracy、F1與 confusion matrix校準 judge，而不是把模型吐出的數字直接當真。[Evaluate a judge model](https://docs.cloud.google.com/vertex-ai/generative-ai/docs/models/evaluate-judge-model)

## (b) nova 落點

位置：plan 09 新增一個 task，放在現 Task 3 之後、Task 4 ranking comparator 之前。

Create：

```text
規格/判準/ScoreEvidence.schema.json
規格/工作/ScoreSourcePolicy.schema.json
nova/權威/判準/分數證據.py
nova/權威/判準/test_分數證據.py
驗收/三層流程/測_分數來源.py
規格/工作/保證/選拔分數有准入來源.claim.json
```

Modify：

```text
規格/工作/RankingSchema.schema.json
nova/領域/工作/選拔.py
```

不要讓 comparator 接：

```python
dict[score_id, Decimal]
```

改接：

```text
ScoreEvidence
├── score_id
├── value
├── value_type
├── candidate_digest
├── criterion_revision_ref
├── evaluator_kind
├── evaluator_revision_ref
├── evaluator_fingerprint
├── metric_or_rubric_ref
├── evaluation_run_ref
├── evidence_refs[]
├── calibration_ref?
└── produced_by_authority
```

`RankingDimension` 新增：

```text
score_source_policy_ref
```

`ScoreSourcePolicy` 明確列出：

```text
allowed_evaluator_kinds
allowed_evaluator_refs
minimum_calibration?
required_evidence_kinds
allow_candidate_self_report = false
```

SelectionRecord 保存的不是裸 normalized number，而是：

```text
normalized_value
score_evidence_ref
score_source_policy_ref
```

## (c) 固定負控

1. candidate／LLM output直接提供 `{"quality": 7.5}`。

   必須回：

   ```text
   UNTRUSTED_SCORE_SOURCE
   ```

   紅在：

   ```text
   ranking_score_has_admitted_provenance
   ```

2. ScoreEvidence 的 candidate digest 指向 A，卻拿去排 B。

   紅在：

   ```text
   score_is_bound_to_ranked_candidate
   ```

3. score 綁 criterion revision 4，Work pin revision 5。

   紅在：

   ```text
   score_uses_work_pinned_criterion
   ```

4. LLM judge有 evaluator ref但沒有有效 calibration，policy要求 calibrated。

   紅在：

   ```text
   model_score_meets_calibration_policy
   ```

5. comparator在 provenance validation失敗後仍使用 numeric value。

   紅在：

   ```text
   invalid_score_is_rejected_not_ranked
   ```

## (d) 核心或外掛

【設計判斷】核心。

刪掉後，現有「自由文字不參與 comparator」負控仍會紅，但任何來源的 numeric值都能通過；`INTEGER|DECIMAL` 會變成「只要會輸出數字就可信」的恆真洞。

具體 score producer，例如某個 VLM judge、人工試玩分數或遊戲 telemetry evaluator，是外掛；`ScoreEvidence` 與來源守衛是核心。

---

# 缺口三：Feedback 沒有資訊預算

## (a) 業界／權威做法

名稱是：

- Adaptive Data Analysis
- Reusable Holdout
- Differential Privacy composition／privacy accountant
- Holdout query budget

Dwork 等人的 Reusable Holdout 研究處理的正是：後續分析會根據先前 holdout 回覆調整，因此反覆查詢會破壞統計有效性。論文提出以 privacy-preserving mechanisms 安全地重用 holdout，而不是假定每次 query獨立。[IBM Research：The Reusable Holdout](https://research.ibm.com/publications/the-reusable-holdout-preserving-validity-in-adaptive-data-analysis)、[Generalization in Adaptive Data Analysis and Holdout Reuse](https://arxiv.org/abs/1506.02629)

【設計判斷】控制端指出的問題成立：`CaseBurned` 只保護 raw reveal，不保護由多次 reduced feedback組成的 adaptive transcript。

但 nova v1 不應假裝實作了完整 differential privacy。先做保守、可證明的 transcript budget；未來要宣稱 reusable holdout/DP，再加入正式 ε/δ accountant。

## (b) nova 落點

### 1. plan 06：在 FeedbackPacket release 前執法

位置：Task 5「只輸出 clause-level gated feedback」之後、Task 6「揭露即燒掉」之前。

Create：

```text
規格/判準/FeedbackDisclosurePolicy.schema.json
規格/判準/FeedbackDisclosureLedger.schema.json
nova/權威/判準/資訊預算.py
nova/權威/判準/test_資訊預算.py
驗收/判準/測_適應性回饋預算.py
規格/判準/保證/封存回饋有累積上限.claim.json
```

Modify：

```text
nova/權威/判準/回饋閘.py
nova/應用/執行判準.py
```

Ledger key不能是 Pursuit id；否則開八個 Pursuit即可洗掉額度。至少綁：

```text
criterion_revision
sealed_pool_revision
feedback_policy_revision
adaptive_lineage_root
```

`adaptive_lineage_root` 必須跨：

- 同 Work 的所有 Pursuits；
- superseding Pursuits；
- 使用先前 feedback/checkpoint 衍生出的後續 Work。

若 lineage 共享先前 feedback，就共享 disclosure ledger。

### 2. plan 08：消費 typed exhaustion

位置：Task 3 criterion feedback loop附近，獨立小 task。

Create：

```text
驗收/追求/測_回饋額度耗盡.py
規格/追求/保證/回饋耗盡不得重設.claim.json
```

Modify：

```text
nova/領域/追求/決策.py
nova/領域/追求/公開契約.py
```

typed result：

```text
FEEDBACK_DISCLOSURE_BUDGET_EXHAUSTED
```

它不能被當成 criterion failure，也不能另建 Pursuit重設。政策可以：

- 繼續無 feedback執行；
- pause等待新 criterion pool；
- 或 `NO_PROGRESS`／policy stop。

不能靜默再放一包。

### v1 budget 形狀

【設計判斷】

```text
FeedbackDisclosurePolicy
├── max_packets
├── max_items
├── max_releases_per_clause
├── max_releases_per_sealed_pool
├── field_release_costs
├── composition_scope
├── exhaustion_action
└── policy_digest
```

v1成本名稱應叫 `disclosure_units`，不要冒稱資訊 bits：

```text
clause_id            = 1 unit
outcome_class         = 1 unit
location_bucket       = 1 unit
retryability          = 1 unit
presence/omission     = 1 unit
```

這只保證 transcript 有硬上限，不宣稱統計 generalization。

未來新增：

```text
mechanism = DP_REUSABLE_HOLDOUT
epsilon
delta
accountant_revision
```

在沒有已驗證 accountant primitive前必須：

```text
UNSUPPORTED_DISCLOSURE_MECHANISM
```

## (c) 固定負控

1. 同 Work 開八個 Pursuit，各取得新的 feedback budget。

   紅在：

   ```text
   feedback_budget_composes_across_sibling_pursuits
   ```

2. 建 superseding Pursuit後 ledger 歸零。

   紅在：

   ```text
   feedback_budget_follows_adaptive_lineage
   ```

3. budget只計 packet數，不計 packet中的多個 clause items。

   紅在：

   ```text
   every_released_feedback_field_is_accounted
   ```

4. ledger已耗盡，reducer仍回 FeedbackPacket。

   紅在：

   ```text
   exhausted_feedback_budget_releases_nothing
   ```

5. 回 `FEEDBACK_DISCLOSURE_BUDGET_EXHAUSTED`，上層把它當「candidate fail」並扣錯 clause。

   紅在：

   ```text
   disclosure_exhaustion_is_not_candidate_failure
   ```

6. Case沒有 raw reveal，所以即使 transcript超額仍宣稱 sealed protection成立。

   紅在：

   ```text
   sealed_validity_requires_disclosure_budget
   ```

## (d) 核心或外掛

【設計判斷】核心，而且比視覺更優先。

刪掉後，`sealed內容不進候選` 與 `回饋經reducer` 的固定負控仍可逐次轉紅，但攻擊者能以合法的 repeated reduced packets重建鑑別資訊；既有保證會在組合下變成恆真。

DP accountant是後續可插拔、需獨立 admission 的 mechanism；「任何 feedback release 都必須進全域 composition ledger」是核心。

---

# 缺口四：視覺判準為空

## (a) 業界既有做法

名稱是：

- Visual Regression Testing
- Golden／Baseline Screenshot Testing
- Snapshot Testing
- Perceptual Image Comparison

Playwright官方提供 `toHaveScreenshot()`，以 baseline screenshot與後續 capture比較；同時明確警告 OS、browser version、hardware、headless mode與 fonts都會改變 rendering，因此 baseline與測試應在相同環境執行。[Playwright Visual Comparisons](https://playwright.dev/docs/next/test-snapshots)

Playwright也提供：

- `maxDiffPixels`
- `maxDiffPixelRatio`
- perceptual color threshold
- mask／stylePath
- platform/project-specific snapshots

但這些 threshold 都是測試定義的一部分，不能在看到 candidate後臨場調高。[Playwright Snapshot Assertions](https://playwright.dev/docs/next/api/class-snapshotassertions)

## (b) nova 落點

按控制端的核心判準，分兩部分。

### 核心：視覺 evaluator 的通用擴充契約

位置：plan 06 Task 3 隔離 projection之後、Task 4 verdict之前。

Create：

```text
規格/判準/VisualCase.schema.json
規格/判準/VisualEvaluationProtocol.schema.json
nova/權威/判準/視覺契約.py
nova/權威/判準/test_視覺契約.py
驗收/判準/測_視覺案例隔離.py
規格/判準/保證/視覺協定事前固定.claim.json
```

`VisualEvaluationProtocol`：

```text
capture_kind
candidate_build_ref
scenario/input_trace_ref
renderer_fingerprint_policy
viewport
color_space
frame_selection
baseline_refs
mask_refs
comparator_primitive_ref
thresholds
replication_policy
stability_class
```

sealed baseline、mask、threshold與expected clause outcomes只進 evaluator projection。

### 外掛：實際 capture/comparator

建議另立 visual evaluator plugin；若暫時仍放同 repo，落在 `nova/介接/`，不能放 Criterion Authority：

```text
nova/介接/視覺評估/playwright_capture.py
nova/介接/視覺評估/pixelmatch.py
驗收/視覺/fixtures/
驗收/視覺/測_固定環境截圖.py
規格/判準/保證/視覺評估重播.claim.json
```

遊戲 renderer adapter另做：

```text
nova/介接/視覺評估/遊戲捕獲.py
```

它輸出 capture evidence，不寫 verdict。

### plan 18 的既有文件性裁決

在 plan 18 建獨立 task，不混入一般 browser UI task：

```text
驗收/前端/測_GraphBundle語義快照.py
規格/前端/保證/流程圖驗語義非像素.claim.json
```

規則：

- Graph node/edge ids與bundle digest用 semantic assertions。
- 截圖只能驗樣式／layout。
- pinned font缺失回 `VISUAL_ENVIRONMENT_UNSUPPORTED` 或 build failure。
- 不得以放寬 pixel threshold把缺字型變綠。

## (c) 固定負控

1. candidate評估失敗後，把 `maxDiffPixels` 從10改1000再重跑。

   紅在：

   ```text
   visual_threshold_is_pinned_before_candidate
   ```

2. baseline產生於 renderer fingerprint A，實際跑 B，仍套同 baseline。

   紅在：

   ```text
   visual_environment_matches_protocol
   ```

3. 缺 pinned font時畫 fallback font，但結果仍進 comparator。

   紅在：

   ```text
   missing_visual_dependency_fails_before_comparison
   ```

4. 同一 captured image bytes與同一 protocol digest得到不同 verdict。

   紅在：

   ```text
   evaluation_replay_is_deterministic
   ```

5. sealed golden或mask出現在 candidate workspace。

   紅在：

   ```text
   sealed_visual_assets_absent_from_candidate_projection
   ```

6. Graph node id錯誤但 screenshot仍在 pixel tolerance內，UI claim通過。

   紅在：

   ```text
   graph_semantics_are_not_proved_by_pixels
   ```

## (d) 核心或外掛

【設計判斷】通用 evaluator protocol與primitive admission是核心；Playwright、pixelmatch、VLM、特定遊戲renderer是外掛。

若完全刪掉視覺 plugin，現有規則式 claims仍 fail-closed，不會自行變成恆真；因此按控制端給的嚴格判準，具體 visual implementation沒有核心資格。

但遊戲 product profile可把 visual capability標為 REQUIRED。未安裝時不是「跳過視覺測試後整體綠」，而是：

```text
UNSUPPORTED_REQUIRED_EVALUATOR
```

整個遊戲 Work不得宣稱驗收完成。

---

# 缺口五：受信 Primitive Catalog／擴充 admission root 不存在

## 判定

【設計判斷】第五個缺口就是這個。它比一般 observability更根本。

現在 `compile_claim(spec, catalog, binding, offer)` 的 `catalog` 由 caller提供。只要 caller自帶：

```text
pixel.compare
llm.judge
always.pass
```

編譯器就會把它當成合法語言。digest不同只能證明「這次用了另一份目錄」，不能證明「這份目錄有權存在」。

這跨越：

- 工具：新 primitive可能呼叫工具；
- 輸出解析：primitive定義 observation type；
- 錯誤處理：primitive定義 terminal mapping；
- 驗證：primitive定義 predicate可觀察什麼；
- 安全：primitive可能有外部效果或讀 sealed資料。

## (a) 業界既有做法

名稱是：

- Trusted Root／Root of Trust
- Allowlisted Registry
- Signed Attestation／Provenance
- Trusted Builder／Verifier

SLSA要求 provenance綁定可信 builder identity，consumer只接受指定 signer-builder pairs；外部參數與 resolved dependencies都必須記錄並下游驗證。[SLSA Build Provenance](https://github.com/slsa-framework/slsa/blob/main/spec/build-provenance.md)

OWASP對agent tools明確建議 backend enforcement與verified allowlist registry，而不是讓模型或呼叫端宣告自己能用什麼。[OWASP AI Agent Security controls](https://github.com/OWASP/www-project-ai-security-and-privacy-guide/blob/main/content/ai_exchange/content/docs/1_general_controls.md)

## (b) nova 落點

位置：plan 01 Task 7 compiler旁邊新增一個「catalog admission」task；因 Task 10已交付，執行順序上應立即插入下一個 task，先於任何新增 primitive及plan 02。

Create：

```text
規格/語言/PrimitiveCatalog.schema.json
規格/語言/PrimitiveAdmission.schema.json
規格/語言/原語目錄.bootstrap.json
nova/權威/判準/原語目錄.py
nova/權威/判準/test_原語目錄.py
架構/test_原語目錄信任根.py
規格/判準/保證/原語目錄來源受信.claim.json
```

Production API不得是：

```python
run_claim(claim, caller_supplied_catalog)
```

應是：

```python
run_claim(claim_ref, admitted_catalog_ref)
```

application runner只可透過 `PrimitiveCatalogResolver` 解析 exact admitted ref。

`PrimitiveAdmission` 至少：

```text
primitive_id
revision
implementation_ref
implementation_digest
input_type
observation_type
effect_kind
required_isolation
authority_owner
fixed_controls[]
approval_attestation_ref
supersedes?
```

新 pixel或LLM-judge primitive必須：

1. 提案新 catalog revision；
2. 跑 primitive自己的正控／固定負控；
3. 確認 effect/isolation；
4. 由 Definition Authority admit；
5. 下游 ClaimSpec才可引用。

plan 20 Task 1 不再「bootstrap時自由組 catalog」，只能驗 exact admitted catalog closure。

## (c) 固定負控

1. caller自建 catalog加入 `always.pass`，compile成功。

   application gate必須回：

   ```text
   UNADMITTED_PRIMITIVE_CATALOG
   ```

   紅在：

   ```text
   production_uses_only_admitted_catalog
   ```

2. 同 catalog id、不同 digest。

   紅在：

   ```text
   primitive_catalog_ref_is_content_bound
   ```

3. 新 primitive有 implementation但沒有自己的 fixed controls。

   紅在：

   ```text
   primitive_admission_requires_named_controls
   ```

4. `pixel.compare` 未宣告會讀 sealed baseline。

   紅在：

   ```text
   primitive_effect_and_isolation_are_declared
   ```

5. `llm.judge` 未聲明 external call、budget與sampling evidence。

   紅在：

   ```text
   model_judge_primitive_has_complete_capability_contract
   ```

6. PR同時修改 catalog resolver，讓任意 digest被接受。

   必須由 trusted-base verifier抓住，紅在：

   ```text
   catalog_admission_root_not_candidate_controlled
   ```

## (d) 核心或外掛

【設計判斷】核心。

刪掉它後，`UNKNOWN_PRIMITIVE` 固定負控只會證明「caller自己準備的清單內有沒有該名字」。caller可把任何新能力加入清單，原負控仍綠，實際上已退化成恆真。

具體 primitives是外掛；「只有 admitted primitive能進 production catalog」是核心。

---

# ProtectedClaimClosure：確切落點

## (a) 業界既有做法

名稱是：

- Protected branch＋required status checks
- Immutable provenance／attestation
- Trusted verifier
- Software integrity protection

GitHub官方說 required status checks未成功前不能合併到 protected branch，且可限定由特定 GitHub App提供該 check。[GitHub Protected Branches](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches)

NIST SSDF要求保護 release integrity verification information及provenance，建議與release files分開或簽章，並讓接收者可驗 provenance完整性。[NIST SSDF SP 800-218](https://nvlpubs.nist.gov/nistpubs/specialpublications/nist.sp.800-218.pdf)

SLSA則要求 artifact digest、builder identity、inputs與dependencies均進可驗 attestation。[SLSA Build Requirements](https://slsa.dev/spec/v1.2/build-requirements)

## (b) nova 落點

位置：plan 01 立即新增獨立 task，排在 Primitive Catalog admission之後、任何後續 plan之前。不能等 plan 19；plan 19是正式Definition Authority的演化流程，bootstrap保護現在就需要。

Create：

```text
規格/判準/ProtectedClaimClosure.schema.json
規格/判準/ClaimAdmissionManifest.schema.json
規格/判準/已准入保證.manifest.json
架構/檢查已准入保證.py
架構/test_已准入保證.py
規格/工程/保證/已准入保證不可原地改弱.claim.json
```

Modify：

```text
架構/目錄規則.toml
.github/workflows/gates.yml
```

仍控制在一個 task十檔內。

### Manifest 形狀

```text
ClaimAdmissionManifest
├── manifest_version
├── generated_from_base_commit
├── entries[]
└── manifest_digest
```

每個 entry：

```text
ProtectedClaimClosure
├── claim_ref
│   ├── claim_id
│   ├── revision
│   └── source_digest
├── status = ADMITTED
├── protected_artifacts[]
│   ├── role
│   ├── path_or_content_ref
│   └── digest
├── primitive_catalog_ref
├── binding_contract_ref
├── test_plan_digest
├── actual_evidence_ref
├── positive_evidence_refs[]
├── negative_evidence_refs[]
├── admitted_at
├── admitted_by
├── approval_attestation_ref
└── supersedes?
```

`protected_artifacts.role`封閉為：

```text
CLAIM_SOURCE
ORACLE
FIXED_NEGATIVE
MUTATION_RECIPE
PREDICATE_DEFINITION
FIXTURE
PRIMITIVE_CATALOG
BINDING_CONTRACT
HARNESS_COMPONENT
```

### CI 信任方向

不能讓 PR head自己提供 verifier或baseline：

```text
protected main 的 verifier
+ protected main 的 admitted manifest
+ PR head workspace
→ closure comparison
```

若 workflow執行 PR版本的 `檢查已准入保證.py`，實作者可先把 checker改成永遠0。required CI仍會綠。

因此 required check必須使用：

- base branch中的 verifier；或
- pinned external verifier action／GitHub App。

不要在 `pull_request_target` 中執行 PR的任意 code；只讀檔、算digest、比manifest。

### 新 claim 如何進場？

```text
DRAFT claim commit
→ red evidence
→ independent admission exact commit/digest
→ manifest entry
→ production implementation commits
```

後續 implementation commits可改 production subject，不能改 protected closure。

完整 runtime ledger到plan 06/19時，再把bootstrap manifest遷入Definition Authority；語義不變。

## (c) 固定負控

1. 把 wall-limit claim 的：

```text
must_fail_exactly = ["elapsed_bound", "worker_dead"]
```

縮成：

```text
["terminal_is_timed_out"]
```

即使 cooperative subject自報 `TIMED_OUT`，必須紅在：

```text
admitted_claim_source_is_byte_identical
```

2. claim不動，修改 cooperative-timeout fixture讓 worker真的自行退出。

紅在：

```text
admitted_fixed_negative_is_unchanged
```

3. claim與fixture不動，改 predicate讓 `worker_dead`永遠true。

紅在：

```text
admitted_predicate_definition_is_unchanged
```

4. PR同步修改 manifest中的digest。

紅在：

```text
candidate_cannot_rewrite_admission_baseline
```

5. PR同步修改 checker成 `return 0`。

trusted-base verifier仍須抓到，紅在：

```text
admission_verifier_is_not_loaded_from_candidate
```

6. 新增 claim檔但沒有 admission entry。

允許保持 DRAFT，但不得被 production binding、Work或release gate引用；若引用，紅在：

```text
only_admitted_claims_can_authorize_acceptance
```

## (d) 核心或外掛

【設計判斷】核心，且是最先補。

如果刪掉，所有既有固定負控都仍可「紅得起來」，但實作者可以先改 `must_fail_exactly`、fixture或predicate，再讓它按新答案紅。這不是單一 claim失守，是整個 ClaimSpec語言的 meta-guarantee變成恆真。

---

# 第三個複驗事實：wall-limit claim 的處置

【設計判斷】這份 claim應成為第一個 `ProtectedClaimClosure` bootstrap entry，因為它已經具備最清楚的差異證據：

```text
actual:
    external supervisor真正在elapsed bound內kill process tree

negative:
    cooperative-timeout-subject只自報TIMED_OUT
```

固定失敗集合必須永久釘住：

```text
elapsed_bound
worker_dead
```

而：

```text
terminal_is_timed_out
```

在負控中保持綠，正是它有辨識力的證據。

這個 shape 不只保護一份 claim；它也是 ProtectedClaimClosure 自己的第一個固定負控。若有人把驗收退化成「看到 TIMED_OUT字串就算」，closure gate必須先於 wall-limit runner把變更擋掉。

---

# 最終優先順序與編排

| 順序 | 能力 | 落點 | 必須先於 |
|---:|---|---|---|
| 1 | 受信 Primitive Catalog | plan 01 Task 7附近，現在補做 | 任何新 primitive、plan 02 |
| 2 | ProtectedClaimClosure | plan 01，緊接 catalog admission | 所有後續 ClaimSpec被當成已准入 |
| 3 | PromptFamily content identity | plan 08 Task 1後 | plan 08 Task 5 identity matrix |
| 4 | PromptFamily governance | plan 10 snapshot resolve前 | 正式可重用prompt啟用 |
| 5 | PromptPlan完整前綴 | plan 12 Task 7前 | 任一真backend收到完整context |
| 6 | ScoreEvidence provenance | plan 09 Task 4前 | RankingSchema與winner comparator綠 |
| 7 | Feedback disclosure ledger | plan 06 Task 5後、release前 | 第一份FeedbackPacket離開Evaluation Authority |
| 8 | Pursuit消費feedback exhaustion | plan 08 Task 3附近 | retry loop正式啟用 |
| 9 | Visual evaluator protocol | plan 06 isolation後 | 第一個visual criterion |
| 10 | Playwright／遊戲capture plugin | 外掛 | 第一個遊戲Work宣稱視覺驗收完成 |

最危險的不是「沒有視覺能力」。沒有視覺目前會 fail-closed。

最危險的是前三項：

- caller能自行發明 primitive；
-實作者能修改已准入答案；
- Pursuit identity正在比較不存在的 prompt artifact。

這三項都會讓帳面保持綠色，同時實際保證已經不存在。
tokens used
220,032
先給排序結論：

1. `ProtectedClaimClosure` 與受信原語目錄：先補。這是 ClaimSpec 信任根本身的洞。
2. Prompt artifact：再補。現有 Pursuit identity 固定負控正在測不存在的物件。
3. Score provenance：必須在 plan 09 Task 4 前補。
4. Feedback information budget：必須在 plan 06 放出第一份 FeedbackPacket 前補。
5. Visual evaluation：核心保留通用 evaluator／primitive admission；視覺實作是必裝外掛，不混進最小核心。

我判定遺失的第五份報告最可能對應「受信擴充目錄／admission root」，不是一般 metrics。理由是它同時穿過工具、輸出解析、錯誤處理與驗證：目前 caller 能自行定義「系統認得哪些原語」，等於 caller 能擴張 ClaimSpec 語言。

---

# 缺口一：Prompt artifact 懸空

## (a) 業界既有做法

業界名稱是：

- Prompt Management
- Versioned Prompt Template／Prompt Artifact
- Prompt ID + Version + Variables

AWS Bedrock Prompt Management 將 prompt 做成可儲存、測試、比較、版本化及部署的 artifact；版本包含 messages、system prompt、模型／推論設定與工具設定。[Amazon Bedrock Prompt Management](https://docs.aws.amazon.com/bedrock/latest/userguide/prompt-management.html)

OpenAI Agents SDK 的 `Prompt` 也明確是：

```text
id
version
variables
```

而不是呼叫端隨手拼出的字串。[OpenAI Agents SDK Prompts](https://openai.github.io/openai-agents-python/ref/prompts/)

【設計判斷】nova 不應照搬任一 provider 的 prompt resource，但應採相同原則：prompt family 是有版本、有內容摘要、可解析成 exact outbound segments 的 artifact。

## (b) nova 落點

這個缺口有三段，不能塞進同一 task。

### 1. plan 08：PromptFamily 的 identity 語義

位置：plan 08 Task 1 之後、現 Task 2 之前。原因是 Task 1 已把 `prompt_family_ref` 放進 Pursuit identity，而 Task 5 才驗 identity change，定義必須先於比較。

Create：

```text
規格/追求/PromptFamily.schema.json
nova/領域/追求/提示身分.py
nova/領域/追求/test_提示身分.py
驗收/追求/測_提示內容身分.py
規格/追求/保證/提示身分依有效內容.claim.json
```

`PromptFamilyRef` 必須包含：

```text
prompt_family_id
revision
source_digest
effective_prompt_digest
segment_contract_digest
variable_schema_digest
tool_policy_ref
```

identity change 比較：

```text
effective_prompt_digest
+ segment_contract_digest
+ variable_schema_digest
+ tool_policy_ref digest
```

不能比較裸 `prompt_family_id`。

因此：

- 不同 id、相同 effective bytes與相同 contracts：`SAME_PURSUIT`，但留下 ref changed audit event。
- 同一 id、digest 不同：拒絕 floating ref，或 `NEW_PURSUIT_REQUIRED`。
- `latest`：schema admission red。

### 2. plan 10：PromptFamily 的治理與 admission

位置：plan 10 的 assertion admission/DAG 已成立後、KnowledgeSnapshot resolve 前。

Create：

```text
規格/知識/PromptFamilyAdmission.schema.json
nova/權威/知識/提示族治理.py
nova/權威/知識/test_提示族治理.py
驗收/知識/測_提示族准入與撤銷.py
規格/知識/保證/提示族內容不可漂移.claim.json
```

【設計判斷】可重用 PromptFamily 屬於「怎麼做」的制度知識，因此治理權歸 Knowledge Authority；Pursuit只 pin exact ref，不能自行 activate。

PromptFamily 內容至少涵蓋：

```text
segments[]
variables schema
canonical ordering
required tool policy
static document refs
serialization policy
minimum delivery capabilities
```

### 3. plan 12：PromptPlan 與完整前綴

位置：Task 6 之後、Task 7 context packing 之前，獨立 task。

Create：

```text
規格/執行/PromptPlan.schema.json
規格/執行/PromptDeliveryPolicy.schema.json
nova/領域/執行/提示計畫.py
nova/領域/執行/test_提示計畫.py
驗收/約束/測_完整提示前綴.py
規格/執行/保證/提示前綴逐位元組固定.claim.json
```

`PromptPlan` 必須包含有序 segments：

```text
system_policy
tool_contract
fixed_documents
task_intent
knowledge
advisory_constraints
checkpoint
reduced_feedback
```

每段帶：

```text
content_ref
semantic_role
authority_source
delivery_requirement
canonical_order
```

最終 `InvocationEnvelope` 必須記：

```text
prompt_plan_ref
effective_prompt_digest
actual_outbound_payload_digest
segment_delivery_manifest
```

KV cache hit/miss驗的是最終 outbound payload，而不只 knowledge serialization 後段。

## (c) 固定負控

至少四個：

1. 不同 refs 指向完全相同 effective bytes，classifier 回 `NEW_PURSUIT_REQUIRED`。

   必須紅在：

   ```text
   prompt_identity_uses_effective_digest
   ```

2. 同一 semantic id 下 source bytes 漂移，但 classifier 回 `SAME_PURSUIT`。

   必須紅在：

   ```text
   floating_prompt_ref_is_rejected
   ```

3. 工具清單或固定文件順序改變，但 `effective_prompt_digest` 不變。

   必須紅在：

   ```text
   effective_prompt_digest_covers_full_prefix
   ```

4. cache hit 與 miss 的 knowledge bytes 相同，但 system/tool prefix 不同，整體 claim仍綠。

   必須紅在：

   ```text
   cached_and_uncached_outbound_payloads_are_byte_identical
   ```

## (d) 核心或外掛

【設計判斷】核心。

按控制端給的判準，整份拿掉後，plan 08 的 prompt-family identity 固定負控仍會對裸字串分類器「正常紅／綠」，卻完全不能辨識實際內容漂移；也就是負控退化成只驗欄位名稱，對真正錯誤恆真。

具體 prompt templates、遊戲 prompt family、elicitation prompt則是外掛／受治理知識。

---

# 缺口二：Ranking score 沒有來源守衛

## (a) 業界既有做法

名稱是：

- Evaluation lineage／ML metadata
- Metric provenance
- Evaluation run metadata
- Grounded／calibrated evaluator

W3C PROV 的核心是 Entity、Activity、Agent，並以 `used`、`wasGeneratedBy`、`wasDerivedFrom`、`wasAttributedTo` 表達資料如何產生以及誰負責；用途正包含評估品質、可靠性與可信度。[W3C PROV Overview](https://www.w3.org/TR/prov-overview/)

Google Vertex ML Metadata明確要求記錄：

- 哪版模型；
- 哪份 evaluation data；
- 哪段 code；
- 哪些參數；
- 哪個 run；
- 產生了哪些 metrics。

目的包括重跑 workflow 與判斷哪個版本產生某項分數。[Vertex ML Metadata](https://cloud.google.com/vertex-ai/docs/ml-metadata/introduction)

對 model judge，Google官方做法是拿 human ratings 當 ground truth，計算 balanced accuracy、F1與 confusion matrix校準 judge，而不是把模型吐出的數字直接當真。[Evaluate a judge model](https://docs.cloud.google.com/vertex-ai/generative-ai/docs/models/evaluate-judge-model)

## (b) nova 落點

位置：plan 09 新增一個 task，放在現 Task 3 之後、Task 4 ranking comparator 之前。

Create：

```text
規格/判準/ScoreEvidence.schema.json
規格/工作/ScoreSourcePolicy.schema.json
nova/權威/判準/分數證據.py
nova/權威/判準/test_分數證據.py
驗收/三層流程/測_分數來源.py
規格/工作/保證/選拔分數有准入來源.claim.json
```

Modify：

```text
規格/工作/RankingSchema.schema.json
nova/領域/工作/選拔.py
```

不要讓 comparator 接：

```python
dict[score_id, Decimal]
```

改接：

```text
ScoreEvidence
├── score_id
├── value
├── value_type
├── candidate_digest
├── criterion_revision_ref
├── evaluator_kind
├── evaluator_revision_ref
├── evaluator_fingerprint
├── metric_or_rubric_ref
├── evaluation_run_ref
├── evidence_refs[]
├── calibration_ref?
└── produced_by_authority
```

`RankingDimension` 新增：

```text
score_source_policy_ref
```

`ScoreSourcePolicy` 明確列出：

```text
allowed_evaluator_kinds
allowed_evaluator_refs
minimum_calibration?
required_evidence_kinds
allow_candidate_self_report = false
```

SelectionRecord 保存的不是裸 normalized number，而是：

```text
normalized_value
score_evidence_ref
score_source_policy_ref
```

## (c) 固定負控

1. candidate／LLM output直接提供 `{"quality": 7.5}`。

   必須回：

   ```text
   UNTRUSTED_SCORE_SOURCE
   ```

   紅在：

   ```text
   ranking_score_has_admitted_provenance
   ```

2. ScoreEvidence 的 candidate digest 指向 A，卻拿去排 B。

   紅在：

   ```text
   score_is_bound_to_ranked_candidate
   ```

3. score 綁 criterion revision 4，Work pin revision 5。

   紅在：

   ```text
   score_uses_work_pinned_criterion
   ```

4. LLM judge有 evaluator ref但沒有有效 calibration，policy要求 calibrated。

   紅在：

   ```text
   model_score_meets_calibration_policy
   ```

5. comparator在 provenance validation失敗後仍使用 numeric value。

   紅在：

   ```text
   invalid_score_is_rejected_not_ranked
   ```

## (d) 核心或外掛

【設計判斷】核心。

刪掉後，現有「自由文字不參與 comparator」負控仍會紅，但任何來源的 numeric值都能通過；`INTEGER|DECIMAL` 會變成「只要會輸出數字就可信」的恆真洞。

具體 score producer，例如某個 VLM judge、人工試玩分數或遊戲 telemetry evaluator，是外掛；`ScoreEvidence` 與來源守衛是核心。

---

# 缺口三：Feedback 沒有資訊預算

## (a) 業界／權威做法

名稱是：

- Adaptive Data Analysis
- Reusable Holdout
- Differential Privacy composition／privacy accountant
- Holdout query budget

Dwork 等人的 Reusable Holdout 研究處理的正是：後續分析會根據先前 holdout 回覆調整，因此反覆查詢會破壞統計有效性。論文提出以 privacy-preserving mechanisms 安全地重用 holdout，而不是假定每次 query獨立。[IBM Research：The Reusable Holdout](https://research.ibm.com/publications/the-reusable-holdout-preserving-validity-in-adaptive-data-analysis)、[Generalization in Adaptive Data Analysis and Holdout Reuse](https://arxiv.org/abs/1506.02629)

【設計判斷】控制端指出的問題成立：`CaseBurned` 只保護 raw reveal，不保護由多次 reduced feedback組成的 adaptive transcript。

但 nova v1 不應假裝實作了完整 differential privacy。先做保守、可證明的 transcript budget；未來要宣稱 reusable holdout/DP，再加入正式 ε/δ accountant。

## (b) nova 落點

### 1. plan 06：在 FeedbackPacket release 前執法

位置：Task 5「只輸出 clause-level gated feedback」之後、Task 6「揭露即燒掉」之前。

Create：

```text
規格/判準/FeedbackDisclosurePolicy.schema.json
規格/判準/FeedbackDisclosureLedger.schema.json
nova/權威/判準/資訊預算.py
nova/權威/判準/test_資訊預算.py
驗收/判準/測_適應性回饋預算.py
規格/判準/保證/封存回饋有累積上限.claim.json
```

Modify：

```text
nova/權威/判準/回饋閘.py
nova/應用/執行判準.py
```

Ledger key不能是 Pursuit id；否則開八個 Pursuit即可洗掉額度。至少綁：

```text
criterion_revision
sealed_pool_revision
feedback_policy_revision
adaptive_lineage_root
```

`adaptive_lineage_root` 必須跨：

- 同 Work 的所有 Pursuits；
- superseding Pursuits；
- 使用先前 feedback/checkpoint 衍生出的後續 Work。

若 lineage 共享先前 feedback，就共享 disclosure ledger。

### 2. plan 08：消費 typed exhaustion

位置：Task 3 criterion feedback loop附近，獨立小 task。

Create：

```text
驗收/追求/測_回饋額度耗盡.py
規格/追求/保證/回饋耗盡不得重設.claim.json
```

Modify：

```text
nova/領域/追求/決策.py
nova/領域/追求/公開契約.py
```

typed result：

```text
FEEDBACK_DISCLOSURE_BUDGET_EXHAUSTED
```

它不能被當成 criterion failure，也不能另建 Pursuit重設。政策可以：

- 繼續無 feedback執行；
- pause等待新 criterion pool；
- 或 `NO_PROGRESS`／policy stop。

不能靜默再放一包。

### v1 budget 形狀

【設計判斷】

```text
FeedbackDisclosurePolicy
├── max_packets
├── max_items
├── max_releases_per_clause
├── max_releases_per_sealed_pool
├── field_release_costs
├── composition_scope
├── exhaustion_action
└── policy_digest
```

v1成本名稱應叫 `disclosure_units`，不要冒稱資訊 bits：

```text
clause_id            = 1 unit
outcome_class         = 1 unit
location_bucket       = 1 unit
retryability          = 1 unit
presence/omission     = 1 unit
```

這只保證 transcript 有硬上限，不宣稱統計 generalization。

未來新增：

```text
mechanism = DP_REUSABLE_HOLDOUT
epsilon
delta
accountant_revision
```

在沒有已驗證 accountant primitive前必須：

```text
UNSUPPORTED_DISCLOSURE_MECHANISM
```

## (c) 固定負控

1. 同 Work 開八個 Pursuit，各取得新的 feedback budget。

   紅在：

   ```text
   feedback_budget_composes_across_sibling_pursuits
   ```

2. 建 superseding Pursuit後 ledger 歸零。

   紅在：

   ```text
   feedback_budget_follows_adaptive_lineage
   ```

3. budget只計 packet數，不計 packet中的多個 clause items。

   紅在：

   ```text
   every_released_feedback_field_is_accounted
   ```

4. ledger已耗盡，reducer仍回 FeedbackPacket。

   紅在：

   ```text
   exhausted_feedback_budget_releases_nothing
   ```

5. 回 `FEEDBACK_DISCLOSURE_BUDGET_EXHAUSTED`，上層把它當「candidate fail」並扣錯 clause。

   紅在：

   ```text
   disclosure_exhaustion_is_not_candidate_failure
   ```

6. Case沒有 raw reveal，所以即使 transcript超額仍宣稱 sealed protection成立。

   紅在：

   ```text
   sealed_validity_requires_disclosure_budget
   ```

## (d) 核心或外掛

【設計判斷】核心，而且比視覺更優先。

刪掉後，`sealed內容不進候選` 與 `回饋經reducer` 的固定負控仍可逐次轉紅，但攻擊者能以合法的 repeated reduced packets重建鑑別資訊；既有保證會在組合下變成恆真。

DP accountant是後續可插拔、需獨立 admission 的 mechanism；「任何 feedback release 都必須進全域 composition ledger」是核心。

---

# 缺口四：視覺判準為空

## (a) 業界既有做法

名稱是：

- Visual Regression Testing
- Golden／Baseline Screenshot Testing
- Snapshot Testing
- Perceptual Image Comparison

Playwright官方提供 `toHaveScreenshot()`，以 baseline screenshot與後續 capture比較；同時明確警告 OS、browser version、hardware、headless mode與 fonts都會改變 rendering，因此 baseline與測試應在相同環境執行。[Playwright Visual Comparisons](https://playwright.dev/docs/next/test-snapshots)

Playwright也提供：

- `maxDiffPixels`
- `maxDiffPixelRatio`
- perceptual color threshold
- mask／stylePath
- platform/project-specific snapshots

但這些 threshold 都是測試定義的一部分，不能在看到 candidate後臨場調高。[Playwright Snapshot Assertions](https://playwright.dev/docs/next/api/class-snapshotassertions)

## (b) nova 落點

按控制端的核心判準，分兩部分。

### 核心：視覺 evaluator 的通用擴充契約

位置：plan 06 Task 3 隔離 projection之後、Task 4 verdict之前。

Create：

```text
規格/判準/VisualCase.schema.json
規格/判準/VisualEvaluationProtocol.schema.json
nova/權威/判準/視覺契約.py
nova/權威/判準/test_視覺契約.py
驗收/判準/測_視覺案例隔離.py
規格/判準/保證/視覺協定事前固定.claim.json
```

`VisualEvaluationProtocol`：

```text
capture_kind
candidate_build_ref
scenario/input_trace_ref
renderer_fingerprint_policy
viewport
color_space
frame_selection
baseline_refs
mask_refs
comparator_primitive_ref
thresholds
replication_policy
stability_class
```

sealed baseline、mask、threshold與expected clause outcomes只進 evaluator projection。

### 外掛：實際 capture/comparator

建議另立 visual evaluator plugin；若暫時仍放同 repo，落在 `nova/介接/`，不能放 Criterion Authority：

```text
nova/介接/視覺評估/playwright_capture.py
nova/介接/視覺評估/pixelmatch.py
驗收/視覺/fixtures/
驗收/視覺/測_固定環境截圖.py
規格/判準/保證/視覺評估重播.claim.json
```

遊戲 renderer adapter另做：

```text
nova/介接/視覺評估/遊戲捕獲.py
```

它輸出 capture evidence，不寫 verdict。

### plan 18 的既有文件性裁決

在 plan 18 建獨立 task，不混入一般 browser UI task：

```text
驗收/前端/測_GraphBundle語義快照.py
規格/前端/保證/流程圖驗語義非像素.claim.json
```

規則：

- Graph node/edge ids與bundle digest用 semantic assertions。
- 截圖只能驗樣式／layout。
- pinned font缺失回 `VISUAL_ENVIRONMENT_UNSUPPORTED` 或 build failure。
- 不得以放寬 pixel threshold把缺字型變綠。

## (c) 固定負控

1. candidate評估失敗後，把 `maxDiffPixels` 從10改1000再重跑。

   紅在：

   ```text
   visual_threshold_is_pinned_before_candidate
   ```

2. baseline產生於 renderer fingerprint A，實際跑 B，仍套同 baseline。

   紅在：

   ```text
   visual_environment_matches_protocol
   ```

3. 缺 pinned font時畫 fallback font，但結果仍進 comparator。

   紅在：

   ```text
   missing_visual_dependency_fails_before_comparison
   ```

4. 同一 captured image bytes與同一 protocol digest得到不同 verdict。

   紅在：

   ```text
   evaluation_replay_is_deterministic
   ```

5. sealed golden或mask出現在 candidate workspace。

   紅在：

   ```text
   sealed_visual_assets_absent_from_candidate_projection
   ```

6. Graph node id錯誤但 screenshot仍在 pixel tolerance內，UI claim通過。

   紅在：

   ```text
   graph_semantics_are_not_proved_by_pixels
   ```

## (d) 核心或外掛

【設計判斷】通用 evaluator protocol與primitive admission是核心；Playwright、pixelmatch、VLM、特定遊戲renderer是外掛。

若完全刪掉視覺 plugin，現有規則式 claims仍 fail-closed，不會自行變成恆真；因此按控制端給的嚴格判準，具體 visual implementation沒有核心資格。

但遊戲 product profile可把 visual capability標為 REQUIRED。未安裝時不是「跳過視覺測試後整體綠」，而是：

```text
UNSUPPORTED_REQUIRED_EVALUATOR
```

整個遊戲 Work不得宣稱驗收完成。

---

# 缺口五：受信 Primitive Catalog／擴充 admission root 不存在

## 判定

【設計判斷】第五個缺口就是這個。它比一般 observability更根本。

現在 `compile_claim(spec, catalog, binding, offer)` 的 `catalog` 由 caller提供。只要 caller自帶：

```text
pixel.compare
llm.judge
always.pass
```

編譯器就會把它當成合法語言。digest不同只能證明「這次用了另一份目錄」，不能證明「這份目錄有權存在」。

這跨越：

- 工具：新 primitive可能呼叫工具；
- 輸出解析：primitive定義 observation type；
- 錯誤處理：primitive定義 terminal mapping；
- 驗證：primitive定義 predicate可觀察什麼；
- 安全：primitive可能有外部效果或讀 sealed資料。

## (a) 業界既有做法

名稱是：

- Trusted Root／Root of Trust
- Allowlisted Registry
- Signed Attestation／Provenance
- Trusted Builder／Verifier

SLSA要求 provenance綁定可信 builder identity，consumer只接受指定 signer-builder pairs；外部參數與 resolved dependencies都必須記錄並下游驗證。[SLSA Build Provenance](https://github.com/slsa-framework/slsa/blob/main/spec/build-provenance.md)

OWASP對agent tools明確建議 backend enforcement與verified allowlist registry，而不是讓模型或呼叫端宣告自己能用什麼。[OWASP AI Agent Security controls](https://github.com/OWASP/www-project-ai-security-and-privacy-guide/blob/main/content/ai_exchange/content/docs/1_general_controls.md)

## (b) nova 落點

位置：plan 01 Task 7 compiler旁邊新增一個「catalog admission」task；因 Task 10已交付，執行順序上應立即插入下一個 task，先於任何新增 primitive及plan 02。

Create：

```text
規格/語言/PrimitiveCatalog.schema.json
規格/語言/PrimitiveAdmission.schema.json
規格/語言/原語目錄.bootstrap.json
nova/權威/判準/原語目錄.py
nova/權威/判準/test_原語目錄.py
架構/test_原語目錄信任根.py
規格/判準/保證/原語目錄來源受信.claim.json
```

Production API不得是：

```python
run_claim(claim, caller_supplied_catalog)
```

應是：

```python
run_claim(claim_ref, admitted_catalog_ref)
```

application runner只可透過 `PrimitiveCatalogResolver` 解析 exact admitted ref。

`PrimitiveAdmission` 至少：

```text
primitive_id
revision
implementation_ref
implementation_digest
input_type
observation_type
effect_kind
required_isolation
authority_owner
fixed_controls[]
approval_attestation_ref
supersedes?
```

新 pixel或LLM-judge primitive必須：

1. 提案新 catalog revision；
2. 跑 primitive自己的正控／固定負控；
3. 確認 effect/isolation；
4. 由 Definition Authority admit；
5. 下游 ClaimSpec才可引用。

plan 20 Task 1 不再「bootstrap時自由組 catalog」，只能驗 exact admitted catalog closure。

## (c) 固定負控

1. caller自建 catalog加入 `always.pass`，compile成功。

   application gate必須回：

   ```text
   UNADMITTED_PRIMITIVE_CATALOG
   ```

   紅在：

   ```text
   production_uses_only_admitted_catalog
   ```

2. 同 catalog id、不同 digest。

   紅在：

   ```text
   primitive_catalog_ref_is_content_bound
   ```

3. 新 primitive有 implementation但沒有自己的 fixed controls。

   紅在：

   ```text
   primitive_admission_requires_named_controls
   ```

4. `pixel.compare` 未宣告會讀 sealed baseline。

   紅在：

   ```text
   primitive_effect_and_isolation_are_declared
   ```

5. `llm.judge` 未聲明 external call、budget與sampling evidence。

   紅在：

   ```text
   model_judge_primitive_has_complete_capability_contract
   ```

6. PR同時修改 catalog resolver，讓任意 digest被接受。

   必須由 trusted-base verifier抓住，紅在：

   ```text
   catalog_admission_root_not_candidate_controlled
   ```

## (d) 核心或外掛

【設計判斷】核心。

刪掉它後，`UNKNOWN_PRIMITIVE` 固定負控只會證明「caller自己準備的清單內有沒有該名字」。caller可把任何新能力加入清單，原負控仍綠，實際上已退化成恆真。

具體 primitives是外掛；「只有 admitted primitive能進 production catalog」是核心。

---

# ProtectedClaimClosure：確切落點

## (a) 業界既有做法

名稱是：

- Protected branch＋required status checks
- Immutable provenance／attestation
- Trusted verifier
- Software integrity protection

GitHub官方說 required status checks未成功前不能合併到 protected branch，且可限定由特定 GitHub App提供該 check。[GitHub Protected Branches](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches)

NIST SSDF要求保護 release integrity verification information及provenance，建議與release files分開或簽章，並讓接收者可驗 provenance完整性。[NIST SSDF SP 800-218](https://nvlpubs.nist.gov/nistpubs/specialpublications/nist.sp.800-218.pdf)

SLSA則要求 artifact digest、builder identity、inputs與dependencies均進可驗 attestation。[SLSA Build Requirements](https://slsa.dev/spec/v1.2/build-requirements)

## (b) nova 落點

位置：plan 01 立即新增獨立 task，排在 Primitive Catalog admission之後、任何後續 plan之前。不能等 plan 19；plan 19是正式Definition Authority的演化流程，bootstrap保護現在就需要。

Create：

```text
規格/判準/ProtectedClaimClosure.schema.json
規格/判準/ClaimAdmissionManifest.schema.json
規格/判準/已准入保證.manifest.json
架構/檢查已准入保證.py
架構/test_已准入保證.py
規格/工程/保證/已准入保證不可原地改弱.claim.json
```

Modify：

```text
架構/目錄規則.toml
.github/workflows/gates.yml
```

仍控制在一個 task十檔內。

### Manifest 形狀

```text
ClaimAdmissionManifest
├── manifest_version
├── generated_from_base_commit
├── entries[]
└── manifest_digest
```

每個 entry：

```text
ProtectedClaimClosure
├── claim_ref
│   ├── claim_id
│   ├── revision
│   └── source_digest
├── status = ADMITTED
├── protected_artifacts[]
│   ├── role
│   ├── path_or_content_ref
│   └── digest
├── primitive_catalog_ref
├── binding_contract_ref
├── test_plan_digest
├── actual_evidence_ref
├── positive_evidence_refs[]
├── negative_evidence_refs[]
├── admitted_at
├── admitted_by
├── approval_attestation_ref
└── supersedes?
```

`protected_artifacts.role`封閉為：

```text
CLAIM_SOURCE
ORACLE
FIXED_NEGATIVE
MUTATION_RECIPE
PREDICATE_DEFINITION
FIXTURE
PRIMITIVE_CATALOG
BINDING_CONTRACT
HARNESS_COMPONENT
```

### CI 信任方向

不能讓 PR head自己提供 verifier或baseline：

```text
protected main 的 verifier
+ protected main 的 admitted manifest
+ PR head workspace
→ closure comparison
```

若 workflow執行 PR版本的 `檢查已准入保證.py`，實作者可先把 checker改成永遠0。required CI仍會綠。

因此 required check必須使用：

- base branch中的 verifier；或
- pinned external verifier action／GitHub App。

不要在 `pull_request_target` 中執行 PR的任意 code；只讀檔、算digest、比manifest。

### 新 claim 如何進場？

```text
DRAFT claim commit
→ red evidence
→ independent admission exact commit/digest
→ manifest entry
→ production implementation commits
```

後續 implementation commits可改 production subject，不能改 protected closure。

完整 runtime ledger到plan 06/19時，再把bootstrap manifest遷入Definition Authority；語義不變。

## (c) 固定負控

1. 把 wall-limit claim 的：

```text
must_fail_exactly = ["elapsed_bound", "worker_dead"]
```

縮成：

```text
["terminal_is_timed_out"]
```

即使 cooperative subject自報 `TIMED_OUT`，必須紅在：

```text
admitted_claim_source_is_byte_identical
```

2. claim不動，修改 cooperative-timeout fixture讓 worker真的自行退出。

紅在：

```text
admitted_fixed_negative_is_unchanged
```

3. claim與fixture不動，改 predicate讓 `worker_dead`永遠true。

紅在：

```text
admitted_predicate_definition_is_unchanged
```

4. PR同步修改 manifest中的digest。

紅在：

```text
candidate_cannot_rewrite_admission_baseline
```

5. PR同步修改 checker成 `return 0`。

trusted-base verifier仍須抓到，紅在：

```text
admission_verifier_is_not_loaded_from_candidate
```

6. 新增 claim檔但沒有 admission entry。

允許保持 DRAFT，但不得被 production binding、Work或release gate引用；若引用，紅在：

```text
only_admitted_claims_can_authorize_acceptance
```

## (d) 核心或外掛

【設計判斷】核心，且是最先補。

如果刪掉，所有既有固定負控都仍可「紅得起來」，但實作者可以先改 `must_fail_exactly`、fixture或predicate，再讓它按新答案紅。這不是單一 claim失守，是整個 ClaimSpec語言的 meta-guarantee變成恆真。

---

# 第三個複驗事實：wall-limit claim 的處置

【設計判斷】這份 claim應成為第一個 `ProtectedClaimClosure` bootstrap entry，因為它已經具備最清楚的差異證據：

```text
actual:
    external supervisor真正在elapsed bound內kill process tree

negative:
    cooperative-timeout-subject只自報TIMED_OUT
```

固定失敗集合必須永久釘住：

```text
elapsed_bound
worker_dead
```

而：

```text
terminal_is_timed_out
```

在負控中保持綠，正是它有辨識力的證據。

這個 shape 不只保護一份 claim；它也是 ProtectedClaimClosure 自己的第一個固定負控。若有人把驗收退化成「看到 TIMED_OUT字串就算」，closure gate必須先於 wall-limit runner把變更擋掉。

---

# 最終優先順序與編排

| 順序 | 能力 | 落點 | 必須先於 |
|---:|---|---|---|
| 1 | 受信 Primitive Catalog | plan 01 Task 7附近，現在補做 | 任何新 primitive、plan 02 |
| 2 | ProtectedClaimClosure | plan 01，緊接 catalog admission | 所有後續 ClaimSpec被當成已准入 |
| 3 | PromptFamily content identity | plan 08 Task 1後 | plan 08 Task 5 identity matrix |
| 4 | PromptFamily governance | plan 10 snapshot resolve前 | 正式可重用prompt啟用 |
| 5 | PromptPlan完整前綴 | plan 12 Task 7前 | 任一真backend收到完整context |
| 6 | ScoreEvidence provenance | plan 09 Task 4前 | RankingSchema與winner comparator綠 |
| 7 | Feedback disclosure ledger | plan 06 Task 5後、release前 | 第一份FeedbackPacket離開Evaluation Authority |
| 8 | Pursuit消費feedback exhaustion | plan 08 Task 3附近 | retry loop正式啟用 |
| 9 | Visual evaluator protocol | plan 06 isolation後 | 第一個visual criterion |
| 10 | Playwright／遊戲capture plugin | 外掛 | 第一個遊戲Work宣稱視覺驗收完成 |

最危險的不是「沒有視覺能力」。沒有視覺目前會 fail-closed。

最危險的是前三項：

- caller能自行發明 primitive；
-實作者能修改已准入答案；
- Pursuit identity正在比較不存在的 prompt artifact。

這三項都會讓帳面保持綠色，同時實際保證已經不存在。
