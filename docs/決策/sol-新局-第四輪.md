# 新局第四輪：可宣告約束、不可觀測額度與最終零未決

## 0. 邊界與總判決

【查證】本輪讀取範圍只有《[需求：可宣告的約束](./需求-約束注入.md)》、《[需求：前端控制面](./需求-前端控制.md)》、[架構草案](./架構草案.md)與自己的[第一輪](./sol-新局-第一輪.md)、[第二輪](./sol-新局-第二輪.md)、[第三輪](./sol-新局-第三輪.md)；沒有讀取既有實作、既有測試、交接、其他設計文件或遷移筆記。（來源：本輪工具讀取紀錄與題目禁令。）

【推論】併入後的形狀仍是：**Work → Pursuit → Execution 三個垂直生命週期層＋判準、資源、效果、知識四個橫向權威面＋CAS／證據索引**。約束是共用宣告語言，不是第五個權威面；每一條可執行規則仍由被限制的既有權威持有。

【推論】題目提出的「告知／強制」分線方向正確，但有三個必須當場改掉的錯字級錯誤：

1. 【推論】**閘是執法位置，不是規則的擁有者。**把所有強制規則籠統寫成「歸執行封套或判準面」會讓資源面、效果面與知識面失去自己的政策寫權。
2. 【推論】同 UID、`COOPERATIVE_PROCESS` 下，自己的 Python gate 只能攔住**必經該 gate 的操作**；它攔不住候選直接發 syscall、讀 `/proc` 或開 socket。沒有不可繞過的 mediation capability，就不得把規則 admit 成「做不到」。
3. 【推論】「壓縮後讓 LLM 正確覆述」測到的是模型表現，不是注入邊界。系統能保證的是壓縮後的實際輸入仍逐 byte 帶著那版文字；不能保證不可靠執行者理解或背得出來。

【推論】供應商若根本不提供可靠剩餘額度，原句「看到各 LLM 剩餘額度」**不可能照字面驗收**。本輪不偽造數字：UI 改為顯示「可觀測性＋可得時的剩餘值＋本地預算＋斷路／探針狀態」；派工採有界盲派。這會撤銷第三輪那條過寬的「所有 UNKNOWN 都永久零派工」，但不動本地花費硬上限。

【推論】本輪結束時未決條目數為 **0**。實測會決定某個 backend manifest 落在哪個已定義分支；它不會再要求產品臨時發明語意。

---

## 1. Q1：分線判決與權威歸屬

### 1.1 先糾正判準數量

【查證】[第一輪](./sol-新局-第一輪.md)的 1.1 與[架構草案](./架構草案.md)第三節記的是四條**垂直層資格**，不是「五條成域判準」。（來源：兩份文件原文。）

【推論】拿垂直層判準直接判一個橫向政策型別是類別錯誤。本輪固定以下五條**權威成域判準**；五條要一起看，不是中一條就開新面：

| 成域判準 | 要問的硬問題 |
|---|---|
| 1. 唯一真相 | 【推論】它能獨占回答哪一個別人不得代答的問題？ |
| 2. 唯一寫者 | 【推論】誰能 admit／改版／撤銷；誰只能 propose？ |
| 3. 自有生命週期 | 【推論】它是否有穩定 identity、版本、有效、過期、撤銷與封閉狀態，而不是借用別人的 status？ |
| 4. 自有恢復與失敗語意 | 【推論】全程序死掉後，誰從持久狀態重建它；它壞掉是否有不可壓進鄰域錯誤的型別？ |
| 5. 窄契約與 change axis | 【推論】消費者是否只經一個可替換契約使用它，而且它的規則、測試與資料是否形成自己的共同變更軸？ |

【推論】這五條判斷的是「要不要新增權威域」。它與四條垂直層資格不衝突：前者切寫權與真相，後者再問該域是否位於 Work→Pursuit→Execution 的組合軸上。

### 1.2 跨工作的告知型約束：確實歸知識，不是方便塞法

| 五條判準 | 告知型約束的答案 | 判決 |
|---|---|---|
| 唯一真相 | 【推論】唯一可宣告的是「這版文字目前獲准供哪些工作取用」，不是「執行者會遵守」。 | 【推論】與 KnowledgeAssertion 的 admitted truth 完全相同。 |
| 唯一寫者 | 【推論】執行者、自我維護 observer、Work 與使用者輸入都只能 propose；知識權威才可 ACTIVE／REVOKED／SUPERSEDED。 | 【推論】與知識准入寫權相同。 |
| 自有生命週期 | 【推論】PROPOSED→ACTIVE→REVIEW_REQUIRED／EXPIRED／REVOKED／SUPERSEDED。 | 【推論】沒有第二套生命週期；它就是 KnowledgeAssertion 的 profile。 |
| 恢復與失敗 | 【推論】由知識事件、來源鏈、TTL 與 KnowledgeSnapshot 重建；過期與撤銷沿既有 signal 傳播。 | 【推論】沒有獨立 recovery owner。 |
| 窄契約／change axis | 【推論】仍經 deterministic retrieval→snapshot→context plan；一起改的是准入、範圍、TTL、撤銷與檢索。 | 【推論】change axis 與知識重合。 |

【推論】因此，**可跨工作重用的告知型約束**固定為 `KnowledgeAssertion.profile=ADVISORY_CONSTRAINT`，歸知識治理面。這不是因為兩者都有 metadata，而是五條權威邊界逐條重合；另開域只會複製同一支筆。

【推論】不是所有塞進 prompt 的文字都因此變成知識。單一 Work 的目標、使用者本次輸入與一次性限制仍是 immutable `WorkDefinition`；它們不進跨工作約束目錄，也不取得 TTL 後自動污染別的 Work。要跨工作重用，必須另提案成 `ADVISORY_CONSTRAINT` 並走知識准入。

### 1.3 強制型約束：不歸一個萬能「約束面」，也不全部歸判準面

【推論】把所有強制型約束視為單一新域，五條會直接失敗：它沒有單一真相、單一寫者、單一故障型別或單一恢復責任。禁止超支由資源權威回答；禁止非法狀態轉移由該 aggregate 的權威回答；禁止重送非冪等效果由效果權威回答。共同的只有語法，**共用語法不是共同權威**。

【推論】固定的三角關係是：

```text
目標權威持有 ConstraintSpec
          │ 編譯成 owner-specific decision plan
          ▼
自己的不可繞過閘 ──── DENY／TERMINATE／QUARANTINE ────► 受控操作
          ▲
          │ ClaimSpec 正控＋固定負控觀察
判準面只裁定「這道閘是否真的有效」
```

【推論】判準面擁有**證明**，不因此擁有 runtime 規則。只有當禁令本身限制的是 CriterionVersion admission、evaluation 或 feedback，規則才因目標權威就是判準面而住在判準面。

【推論】強制約束按下表唯一歸戶；`owner` 與 `gate_ref` 不匹配時，ConstraintSpec admission 直接失敗：

| 被限制的操作 | 規則 owner | 必經執法點 |
|---|---|---|
| 啟動／停止 candidate、受 broker 控制的工具、workspace、上下文組裝 | 【推論】Execution | 【推論】`execution.invocation-gate`／`execution.operation-gate`，在 backend adapter 之前。 |
| attempt、pause／resume、feedback 使用與 checkpoint | 【推論】Pursuit | 【推論】`pursuit.transition-gate`，在 Pursuit decision 寫事件之前。 |
| child fan-out、portfolio cutoff、selection、Work 終態 | 【推論】Work | 【推論】`work.transition-gate`，在 Work decision 寫事件之前。 |
| Criterion admission、evaluation、hidden feedback | 【推論】Criterion | 【推論】`criterion.definition-gate`、`criterion.evaluation-gate`、`criterion.feedback-gate`。 |
| reserve／settle、backend eligibility、rate／quota policy | 【推論】Resource | 【推論】`resource.admission-gate`，在任何付費 Execution 建立之前。 |
| effect intent 與 relay attempt | 【推論】Effect | 【推論】`effect.intent-gate`／`effect.delivery-gate`，在落 intent 或外送之前。 |
| assertion admission、snapshot、撤銷與上下文選擇 | 【推論】Knowledge | 【推論】`knowledge.admission-gate`／`knowledge.use-gate`。 |

【推論】後端原生 hook 可列在 `defense_in_depth[]`，但不能填 `gate_ref`，也不能滿足 `enforcement_claim_ref`。新增 backend 時，所有 scope 命中的強制約束 contract suite 必須重跑；不能只測最常用 backend。

【推論】「強制」還要再過一條不可繞過性檢查：`required_capabilities ⊆ host/backend offer`，且 ClaimSpec 必須對旁路固定反例轉紅。當前 `COOPERATIVE_PROCESS` 可以保證「經本系統工具 broker 的外部 API 呼叫被擋」；不能保證敵意 candidate 不直接開 socket。後者的 ConstraintSpec 必須要求 `NETWORK_NAMESPACE_DENY`／`RESTRICTED_OS` 或 `HOSTILE_VM`；能力不足回 `UNSUPPORTED_CONSTRAINT_ENFORCEMENT`，不得降成告知、不得假 PASS。

### 1.4 對題目三條推導的逐條判決

| 題目推導 | 判決 |
|---|---|
| 強制執法在自己的閘，後端 hook 只作內層防線 | 【推論】**採用，但把「自己的閘」擴成目標權威自己的 system-owned gate，不只 Execution gate。**另外必須證明該操作無旁路；同 UID 不能靠命名把可繞過的 function 變安全邊界。 |
| 每條有 semantic id、明示 scope、強度、理由／證據、負控、有效期／複審 | 【推論】**採用並加嚴。**負控不是一個檔名欄位；引用的 ClaimSpec 必須已對指定 negative control 產生 direct red evidence，否則只能 PROPOSED。 |
| 告知歸知識、強制歸閘、不新增面 | 【推論】**前半正確、後半措辭錯。**告知是知識型別；強制規則歸目標權威，閘只是它的 PEP。結論「不新增權威面」保留。 |

【推論】需求檔的第 4 個出口「壓縮後仍能正確覆述」必須改成兩格：`constraint.advisory.reasserted-after-compaction` 證明 trusted observer 在壓縮後輸入看到 exact digest；`executor.advisory.recall` 若要存在，只是候選品質判準，不能冒充系統邊界。

【推論】自我維護閉環保留：重複 failure 只能建立普通 `constraint-authoring` Work；該 Work 的 accepted candidate 才能成為 `ConstraintProposal(PROPOSED)`。proposal 即使附了綠證據，也不能發 `constraint.activate`；啟用是另一個 target-authority command，需 executor 不持有的 `CONSTRAINT_APPROVER` capability。資料庫 command ACL 與 FlowSpec 都不提供 proposal→ACTIVE 的自動邊；在 hostile threat model 下若 approver channel 不能與同 UID candidate 隔離，這條 claim 必須回 `UNSUPPORTED_ISOLATION`，不能拿 cooperative ACL 冒充安全邊界。

【推論】「一直發生」的 v1 detector 也定死：相同 `failure_signature` 在滾動 **7 天**內至少出現 **3 次**，且橫跨至少 **2 個 Work id**，才建立一件 proposal Work；同一 signature **30 天**內最多一件非終態／已完成 proposal Work。signature 是 `sha256(owner, operation_id, reason_code, backend_fingerprint_or_na, sorted_failed_predicate_ids)`，不納入自由錯誤文字或 Work id。這只控制提案噪音，不提高 constraint 的證據權重。

【推論】v1 activation 必須附一次性 `ApprovalEnvelope(proposal_ref, constraint_digest, evidence_digest, nonce, issued_at, expires_at)`；nonce 只在本機人類 review route 經明確確認後簽發，**10 分鐘**過期且只能消耗一次。任何 Work／Execution／backend primitive 都沒有 mint port。這在 `COOPERATIVE_PROCESS` 下防自動流與誤接線；它不抵抗同 UID hostile candidate，後者仍按上一段回 unsupported。

---

## 2. Q2：宣告、執法與注入的精確住址

### 2.1 `ConstraintSpec 1.0` 的固定形狀

【推論】不把約束欄位塞進 ClaimSpec。`ConstraintSpec` 說「哪條政策何時適用」；ClaimSpec 說「如何觀察與拒絕錯誤實作」。兩者以 immutable ClaimRef 相接，語言版本分開演進。

【推論】`規格/語言/約束.schema.json` 的 top-level 固定如下；所有 object `additionalProperties=false`：

| 欄位 | 型別 | 必填 | 語意 |
|---|---|---:|---|
| `$schema` | absolute URI | 是 | 【推論】固定 `urn:nova:schema:constraint:1`。 |
| `constraint_version` | literal `1.0.0` | 是 | 【推論】選擇 compiler 語意。 |
| `constraint_id` | ASCII SemanticId | 是 | 【推論】跨 revision 不變；章節號與中文標題不得當 id。 |
| `revision` | integer ≥ 1 | 是 | 【推論】任何 executable byte 改變就升版。 |
| `supersedes` | ConstraintRef 或 null | 是 | 【推論】revision 1 為 null；不靠「最新檔」猜取代關係。 |
| `strength` | `ADVISORY` \| `ENFORCED` | 是 | 【推論】兩型的 conditional fields 互斥。 |
| `owner` | 七個既有 owner id 之一 | 是 | 【推論】值域是 EXECUTION／PURSUIT／WORK／CRITERION／RESOURCE／EFFECT／KNOWLEDGE；ADVISORY 只能是 KNOWLEDGE，ENFORCED 必須等於 gate owner。 |
| `lifecycle_machine_ref` | MachineRef＋digest | 是 | 【推論】ADVISORY 必須綁 KnowledgeAssertion machine；ENFORCED 綁目標 owner 的強制約束 machine，authority 不同即拒絕。 |
| `scope` | ExplicitScope | 是 | 【推論】每個維度都明填 ALL 或 ANY_OF；空欄不代表全部。 |
| `statement_ref` | UTF-8 TextRef＋digest | 是 | 【推論】人讀內容；ADVISORY 也以這份 exact bytes 注入。 |
| `reason_ref` | TextRef＋digest | 是 | 【推論】解釋為何存在，不參與 predicate。 |
| `proposal_event_ref` | EventRef | 是 | 【推論】來源可回到 user command、incident 或 maintenance proposal。 |
| `evidence_refs` | EvidenceRef[]，min 1 | 是 | 【推論】沒有證據的歷史疤痕不得入 catalog。 |
| `claim_binding` | ClaimRef＋negative-control-id | 是 | 【推論】引用同一 ClaimSpec 的 actual、positive、指定 negative；只附 test 名稱不算。 |
| `valid_from` | UTC instant | 是 | 【推論】不能早於 admission event。 |
| `review_at` | UTC instant | 是 | 【推論】必須 `valid_from < review_at ≤ valid_from+90d`。 |
| `expires_at` | UTC instant | 是 | 【推論】必須 `review_at < expires_at ≤ valid_from+180d`；schema 不提供永不過期。 |
| `advisory` | AdvisoryPolicy 或 null | 是 | 【推論】ADVISORY 時必填，ENFORCED 時必為 null。 |
| `enforcement` | EnforcementPolicy 或 null | 是 | 【推論】ENFORCED 時必填，ADVISORY 時必為 null。 |

【推論】`ExplicitScope` 的四個維度全部必填；每個值是 `{"kind":"ALL"}` 或 `{"kind":"ANY_OF","values":[…]}`，後者 `minItems=1`：

```text
work_types
backend_ids
criterion_refs
operation_ids
```

【推論】這個 v1 scope DSL 刻意不接受自由 regex、Python predicate、時間查詢或「其餘全部」。新增 scope 維度要升 `ConstraintSpec` minor 版並補 overlap negative control；不能把任意 expression 藏進 selector。

【推論】`AdvisoryPolicy` 固定為：

```text
text_ref:              與 statement_ref 相同 digest
delivery_requirement: REQUIRED_FOR_DISPATCH | BEST_EFFORT
persistence:           INVOCATION_START | REASSERT_EACH_TURN
priority:              integer 0..100
```

【推論】priority 是 proposal 的一部分，但沒有自行生效；知識准入者接受某版，就同時為該值背書。caller、scheduler、backend 與 executor 都不能在派工時改 priority。

【推論】`EnforcementPolicy` 固定為：

```text
gate_ref:              owner + gate-id + revision + digest
gate_catalog:          closed predicate/action catalog ref + digest
operation_ids:         non-empty SemanticId[]
predicate:             typed, total Predicate AST
on_violation:          DENY_COMMAND | TERMINATE_EXECUTION | QUARANTINE_SUBJECT
reason_code:           typed reason id
required_capabilities: non-empty CapabilityId[]
enforcement_claim_ref: ClaimRef
defense_in_depth:      BackendDefenseRef[]
```

【推論】`claim_binding` 證明整條宣告的 admission sensitivity；`enforcement_claim_ref` 另證明 runtime gate 與旁路覆蓋。兩者可指同一 ClaimSpec revision，但欄位不能省略，compiler 會驗 subject contract 與 constraint digest 都相符。

【推論】狀態不寫回 ConstraintSpec；檔案不能自稱 ACTIVE。ADVISORY 沿既有 KnowledgeAssertion machine；每個 ENFORCED owner 各有 authority-bound `強制約束.machine.json`，邊固定為：

```text
PROPOSED       → ACTIVE | REJECTED
ACTIVE         → REVIEW_REQUIRED | REVOKED | SUPERSEDED | EXPIRED
REVIEW_REQUIRED→ REVOKED | SUPERSEDED | EXPIRED
REVOKED        → SUPERSEDED | RETIRED
EXPIRED        → SUPERSEDED | RETIRED
REJECTED／SUPERSEDED／RETIRED 為封閉終態
```

【推論】同一 revision 沒有 REVIEW_REQUIRED→ACTIVE；完成複審必須產生帶新 `review_at`／`expires_at` 的 successor revision，舊版進 SUPERSEDED。到 `review_at` 仍執行到 `expires_at`；不自動續期。所有 status event 帶 machine digest，沿用第三輪的 declared-transition engine／DB FK，不在 constraint compiler 裡硬編另一套狀態機。

【推論】90 天 review／180 天 expiry 讓每條規則半年至少重新證成一次，並留一個最長 90 天的處理窗；窗用完仍沒 successor 就按下段 fail closed。這是 v1 governance policy，不是 schema 永久常數；任何改值都要新 ConstraintSpec language/policy revision，不能改 clock job 讓舊 revision 暗中延命。

【推論】到期語意固定：ADVISORY 不再注入並使 matching Work 的 context snapshot 失效；ENFORCED 舊 predicate 不再執行，但該 semantic slot 留下 `EXPIRED` tombstone，目標 gate 以 `POLICY_REVISION_EXPIRED` fail closed，直到有已證成 successor 或帶 ClaimSpec 的顯式 RETIRED event。這避免「忘記複審」自動打開安全邊界。

### 2.2 Source、runtime 與 code 的唯一位置

| 東西 | 精確位置 | 權力 |
|---|---|---|
| ConstraintSpec meta-schema | 【推論】`規格/語言/約束.schema.json` | 【推論】只定結構與 conditional lint，不擁有任何 ACTIVE 狀態。 |
| 跨工作 ADVISORY bootstrap instances | 【推論】`規格/知識/約束/告知/<semantic-id>.constraint.json` | 【推論】由知識權威 admit；沒有新的 `規格/約束/` 大桶。 |
| ENFORCED bootstrap instances | 【推論】`規格/<owner>/約束/強制/<semantic-id>.constraint.json`，owner 只能是執行／追求／工作／判準／資源／效果／知識之一。 | 【推論】與被限制的 invariant 同址；path 與 `owner` 不同即 lint fail。 |
| runtime proposal／revision | 【推論】spec bytes 進 CAS，metadata／status event 進權威 SQLite；不把 mutable 使用者資料寫回 `規格/`。 | 【推論】Git 目錄只承接 bootstrap source，不冒充 runtime database。 |
| 共用 parser／scope／compiler | 【推論】`nova/約束/` | 【推論】domain-neutral language kernel，只輸出 immutable plan，不可 activate constraint。 |
| ADVISORY admission／selection | 【推論】`nova/權威/知識/告知約束.py`、`上下文計畫.py` | 【推論】知識權威產生 ordered ContextPlan，不直接呼叫 backend。 |
| exact context assembly | 【推論】`nova/領域/執行/上下文組裝.py` | 【推論】Execution envelope 在 backend adapter 之前計量、選取、注入並產生 ContextManifest。 |
| ENFORCED runtime | 【推論】各 owner 的 `約束閘.py`；資源面沿用並擴充既有 `資格閘.py`。 | 【推論】只有目標權威能 DENY／TERMINATE／QUARANTINE。 |
| 驗收 | 【推論】ClaimSpec instance 跟 guarantee owner 放在 `規格/<owner>/保證/`；跨 owner matrix 在 `驗收/約束/`。 | 【推論】ConstraintSpec 不內嵌任意測試程式。 |

【推論】`規格/` 不新開頂層 `約束/`。那個看似整齊的目錄會暗示一支中央筆能改所有權威的政策，正好把剛切好的寫權抹掉；共用的只有 `規格/語言/約束.schema.json`。

### 2.3 告知型的完整注入時序

【推論】每次建立 Execution 前固定走六步，任何 backend 都不得跳步：

1. 【推論】Work 持有 `KnowledgeSnapshot` 與 `ContextSelectionPolicyVersion` digest；Knowledge Authority 以 immutable Work／Pursuit／Execution facts 套 scope，輸出 ordered `ContextPlan`。
2. 【推論】Execution context assembler 取得 exact backend/model fingerprint 與 `CONSERVATIVE_CONTEXT_MEASURE` capability；沒有可靠上界函式時回 `UNSUPPORTED_CONTEXT_ACCOUNTING`。
3. 【推論】assembler 先放所有 `REQUIRED_FOR_DISPATCH`，再按固定順序裝 `BEST_EFFORT`；整條文字只能全放或全不放，不截斷、不讓 LLM 摘要。
4. 【推論】assembler 產生 immutable `ContextManifest`：每個 applicable ref、included／omitted、理由、計量值、policy digest、backend fingerprint 與 preamble digest 都在內。
5. 【推論】adapter 只收到已組好的 `InvocationEnvelope`；它沒有 ConstraintSpec registry、不能重新選取。告知文字放在 machine-owned policy preamble，不混進可被對話摘要改寫的歷史訊息。
6. 【推論】若 declaration 要 `REASSERT_EACH_TURN`，adapter 必須在每次外部可見 turn 重新掛同一 digest；opaque CLI 無 compaction hook 時回 `UNSUPPORTED_CONTEXT_CHANNEL`，不能把首次注入冒充壓縮存活。

【推論】新 constraint 啟用、到期、撤銷或 supersede 時，所有 matching 非終態 Work 收到 `CONTEXT_SNAPSHOT_INVALIDATED`。正在跑的 Execution 不被偷偷改 prompt；下一個 Execution 前必須先寫顯式 `work.context-rebased` event 並釘新 snapshot。若一條禁令必須中斷正在跑的行為，它不該是 ADVISORY，應建 ENFORCED constraint。

---

## 3. Q3：有限上下文的硬 admission、選取與不靜默語意

### 3.1 必須有上限；v1 數字現在定死

【推論】同一個具體 Execution scope 最多匹配 **16 條 ACTIVE ADVISORY constraints**。`statement_ref` 的 canonical UTF-8 內容每條最多 **1,024 bytes**，semantic id 最多 64 ASCII bytes。Knowledge admission 會在有限的 work-type×backend×criterion×operation registry 上枚舉 overlap；第 17 條不得 ACTIVE，回 `ADVISORY_SCOPE_SATURATED`。新增一個 scope dimension 或 registry value 時先重跑 overlap lint。

【推論】16 不是上下文容量的猜測，而是 governance cap：它把 omission header、review 工作量與「事故就加一條」的腐爛速度變成硬上限。超過時只能讓新 revision 明確 supersede／合併舊規則，或用有證據的 RETIRED event 移除；不准自動摘要成一條語義不明的新文字。

【推論】對 exact backend/model fingerprint，令：

```text
C = manifest 證成的總 context capacity
O = 本次保留的最大 output tokens
U = base system + tools + task + retained history 的保守 token 上界
H = max(512, ceil(0.05 * C))                    # provider／tokenizer 誤差與 protocol headroom
M = 完整 ContextManifest control header 的實測保守上界
A = max(0, min(4096, floor(0.10 * C), C-O-U-H-M))
```

【推論】`A` 是 advisory text hard budget。所有量都由 adapter 提供且通過 ClaimSpec 的 conservative meter 計算；provider 用 token、byte 或 preflight 皆可，但必須證明回傳值是上界。拿不到上界不是「大概夠」，而是 `UNSUPPORTED_CONTEXT_ACCOUNTING`。

【推論】10% 讓告知文字永遠只是 task context 的少數，4,096 是跨大模型仍不膨脹的絕對成本帽；5%／至少 512 的 headroom 吸收 provider framing 與 conservative meter 邊界。這三個數字是 `ContextSelectionPolicyVersion` 的 v1 executable parameters，不是假裝量測出的自然常數；改值要新 policy digest 與同一 overload／omission suite。

### 3.2 誰淘汰哪一條

【推論】選取權固定屬於 Knowledge Authority 的 immutable `ContextSelectionPolicyVersion`，Work 建立時釘住版本；caller、Execution scheduler、backend 及 executor 都無權臨場重排。

【推論】排序與 packing 固定為：

1. 【推論】`REQUIRED_FOR_DISPATCH` 全部先放；任一條放不下，**不建立 Execution**，回 `CONTEXT_REQUIREMENTS_UNSATISFIED`。這只保證文字 delivery，不保證遵守。
2. 【推論】`BEST_EFFORT` 依 `(priority DESC, scope-specificity DESC, reviewed_at DESC, constraint_id ASC)` 排序。
3. 【推論】依序整條 first-fit：放不下該條就記 omitted，繼續看下一條較短者；不截斷、不重寫、不交換同分順序。
4. 【推論】priority 由知識准入者在 admit exact revision 時核准；scope-specificity 由 compiler 依 ANY_OF 維度數與集合寬度計算，作者不能自報。

【推論】因此「超過額度淘汰誰」不是 executor 的自由裁量，也不是呼叫端每次塞 prompt 的順序副作用。相同 snapshot、policy、backend fingerprint 與 task bytes 必須得到相同 ContextManifest digest。

### 3.3 不允許靜默降級，能保證到哪裡

【推論】每一條**已 ACTIVE、scope 命中但未被送入**的 constraint 同時出現在三處：權威 `ContextManifest` evidence、事件流／UI，以及送給 executor 的 compact control header；reason 只能是 `CONTEXT_BUDGET` 或 `UNSUPPORTED_CHANNEL`。scope 不命中的規則不屬本次候選集；EXPIRED／REVOKED 會先使 snapshot invalid，沒有 rebase 就不建立 Execution。這防止把整個歷史 catalog 塞進 header。如果連最多 16 條的完整 omission header 都放不下，Execution 不啟動，回 `CONSTRAINT_MANIFEST_OVERFLOW`。

【推論】executor-visible header 至少含：

```text
policy_digest
included: [constraint-ref...]
omitted:  [{constraint-ref, reason}...]
statement: "included 表示文字已送達；不表示行為已保證"
```

【推論】這已消除**系統層的**靜默降級：沒有任何一條會無事件地消失。但「LLM 知道」若指內部理解，沒有可信 observer 可證；可驗收的最強命題只是「送達 bytes 明確告知它哪條未送達」。把 comprehension 偷寫成 hard claim 仍是在說謊。

【推論】UI 必須把 `ADVISORY_CONTEXT_DEGRADED` 與 included／omitted counts 畫進 visual log；它仍只 fold event，不查 Knowledge Authority。告知型行為不得出現在 Work 的 guarantee／accepted verdict 清單，即使該次 executor 剛好遵守。

### 3.4 壓縮與成本

【推論】`INVOCATION_START` 只保證第一次 InvocationEnvelope 有 exact bytes；經 opaque backend 自行壓縮後不作存活宣稱。`REASSERT_EACH_TURN` 只在 adapter offer 包含 `TURN_BOUNDARY_CONTROL` 與 `CONTEXT_SEGMENT_REASSERTION` 時可執行，且 real-compaction fixture 後的 trusted outbound observer 必須看到同一 digest。

【推論】代價已固定，不藏起來：每個 external turn 最多重付 4,096 tokens 告知文字＋manifest／5% headroom；最多 16 條會增加 admission overlap lint；小 context backend 會更常得到 `CONTEXT_REQUIREMENTS_UNSATISFIED`；opaque CLI 可能完全不能承接壓縮存活型約束。這些是誠實能力邊界，不是待補的例外。

---

## 4. Q4：若沒有任何可靠的供應商剩餘額度

### 4.1 原需求的字面版本不可滿足

【查證】[需求-前端控制](./需求-前端控制.md#一要看到什麼讀主要用途)要求看「各執行者後端的剩餘額度」，並把它視為派工前的閘；同檔又正確區分「我們的花費帳」與「供應商剩餘額度」，後者是不權威、可能缺席的外部觀測。（來源：該需求第一節與第三節。）

【推論】在「所有後端都沒有可靠 observation」的前提下，任何剩餘數字都只能由本地用量、方案額度或最後成功呼叫推估；別的 client 消耗、供應商重置與政策變更都不在本系統權威內。因此字面需求不可驗收，沒有 adapter、資料庫或 UI 技巧能補出不存在的觀測。

【推論】需求正式改寫為：**對每個 backend 顯示供應商額度的可觀測能力；有可靠觀測才顯示剩餘值，沒有就明寫不可觀測，同時顯示本地權威預算、最後成功／拒絕、斷路狀態與下次 probe。** UI 禁止以 `∞`、`0`、空白或估算數字代替 UNOBSERVABLE。

### 4.2 capability 與 view union

【推論】backend manifest 的 `provider_quota_mode` 固定四型：

| mode | 可宣稱的事 |
|---|---|
| `RELIABLE_REMAINING` | 【推論】adapter 能產生帶 unit、observed_at、valid_until、remaining、source 的 fresh typed observation；`valid_until-observed_at ≤ 5m`。 |
| `REJECTION_ONLY` | 【推論】事前沒有 remaining，但能把 quota／rate rejection 與其他 fault 型別化，並可能提供 reset／retry-after。 |
| `UNOBSERVABLE` | 【推論】沒有可靠 remaining，連拒絕原因也可能只能分類為 ambiguous；絕不產生數字。 |
| `NOT_APPLICABLE` | 【推論】本地模型／重播器沒有供應商 quota；不是免費付費 backend 的逃生口。 |

【推論】`RELIABLE_REMAINING` 的 runtime observation 才有 `KNOWN | STALE | TEMPORARILY_UNAVAILABLE`；`REJECTION_ONLY`／`UNOBSERVABLE` 使用 `BLIND_READY | BLIND_IN_FLIGHT | CIRCUIT_OPEN | PROBE_IN_FLIGHT | QUARANTINED`。把結構性 UNOBSERVABLE 混回暫時 UNKNOWN，正是第三輪 policy 會把全部 backend 永久停掉的原因。

【推論】view event 至少帶：`backend_id`、`mode`、`state`、`remaining?`、`unit?`、`observed_at?`、`valid_until?`、`local_budget_remaining`、`last_success_at?`、`last_rejection_class?`、`circuit_open_until?`、`next_probe_at?`。只有 `KNOWN` 可帶 remaining；schema 對其他 variant 出現 remaining 直接拒絕。

### 4.3 派工閘的最終政策

| mode／狀態 | 派工決定 |
|---|---|
| `RELIABLE_REMAINING/KNOWN` | 【推論】只有**觀測到的** `remaining ≥ 本次 worst_case_provider_units` 且本地 worst-case cost reserve 成功才可派；unit 無法換算就不 eligible。 |
| `RELIABLE_REMAINING/STALE` 或 `TEMPORARILY_UNAVAILABLE` | 【推論】零新付費 Execution，回 `WAITING_QUOTA_OBSERVATION`。這保留第三輪對「本來聲稱可觀測、現在失鮮」的 fail-closed。 |
| `REJECTION_ONLY` 或 `UNOBSERVABLE`、circuit closed | 【推論】進 `BLIND_BOUNDED`：每 backend 最多 1 個付費 Execution 在途；每次仍先保留本地 worst-case cost。 |
| `CIRCUIT_OPEN` | 【推論】零普通派工；只在 `next_probe_at` 到時准 1 個 probe reservation。 |
| `NOT_APPLICABLE` | 【推論】不走 provider quota gate，但仍走本地 wall／turn／resource limits。 |
| `QUARANTINED` | 【推論】零派工，只有明確 operator command＋通過 adapter contract 才可恢復。 |

【推論】`BLIND_BOUNDED` 的代價是每個不可觀測 backend 串行；換來額度耗盡瞬間最多只有一個在途呼叫暴露於白卷。這不是「耗盡 backend 絕不被派工」的保證——在不可觀測前提下那條保證不可能成立；可成立的是自有花費不超支與盲派損失有界。

【推論】即使 `RELIABLE_REMAINING/KNOWN` 也只是 fresh observation，不是供應商的 atomic reservation；其他 client 可能在 observation 與 dispatch 之間耗掉額度。v1 的 claim 只保證 gate 不會在**最新觀測已不足或失鮮**時派工，不宣稱外部真實額度永不競態。只有供應商未來提供可驗的 atomic admission permit，才值得新增另一個 capability／ClaimSpec revision；v1 不預留一條假綠保證。

### 4.4 斷路與 probe 數字

【推論】adapter 將 outcome 分成 `SUCCESS`、`QUOTA_EXHAUSTED`、`RATE_LIMITED`、`AUTHENTICATION_FAILED`、`TRANSIENT_BACKEND_ERROR`、`EMPTY_OR_INVALID_RESPONSE`、`UNCLASSIFIED_REJECTION`；自由 stderr 不直接驅動狀態。

【推論】轉移政策固定如下：

- 【推論】`QUOTA_EXHAUSTED`：有可信 `reset_at` 就開到該時刻；沒有就開 **24 小時**。
- 【推論】`RATE_LIMITED`：有可信 `retry_after` 就開到該時刻；沒有就開 **15 分鐘**。
- 【推論】`EMPTY_OR_INVALID_RESPONSE` 或 `UNCLASSIFIED_REJECTION`：視為可能白卷，開 **24 小時**，不拿「也許只是暫時」連續燒呼叫。
- 【推論】`AUTHENTICATION_FAILED`：直接 QUARANTINED，沒有 time-based auto close。
- 【推論】已由 adapter contract 證成的 `TRANSIENT_BACKEND_ERROR`：health circuit 開 **15 分鐘**；未證成分類一律降到 `UNCLASSIFIED_REJECTION`，不是升成可重試。
- 【推論】open 到期只准一個 `PROBE_IN_FLIGHT`；成功回 BLIND_READY，失敗按上列重新開。沒有 provider reset／retry signal 時，每 backend 每 24 小時最多一個失敗 probe。

【推論】24 小時的目的不是猜供應商 reset，而是把 ambiguous 白卷硬壓到每 backend 每日最多一次；15 分鐘只用於已型別化的 rate／transient fault，避免把短暫服務抖動當整日額度耗盡。改這兩個值必須升 blind-circuit policy revision 並重跑 fake-time crash／probe matrix。

【推論】所有 blind dispatch／open／probe／result 都是 resource authority event，UI 純 fold 即可顯示。probe 也先 reserve、也計入 Work／backend budget，不存在「健康檢查不算錢」。

### 4.5 這改變與不改變什麼

【推論】第三輪 `UNKNOWN→零派工` 被拆成兩條：**宣告可觀測但失鮮仍零派工；宣告不可觀測則走 BLIND_BOUNDED。**這不是 runtime 從 strict 悄悄降級；mode 是 backend manifest 的 immutable capability，改 mode 要新 fingerprint、contract evidence 與 adapter re-admission。

【推論】以下裁決不變：本地預算先 reserve、RateCard 每 reservation 釘版、AllocationPolicy 對 Work 釘版、比例是 soft target、資格是 live hard gate、UI 純事件 fold、SQLite state owner 與獨立尾隨庫。新增的 quota circuit 只是資源面狀態，沒有新增層或 store。

---

## 5. Q5：最終定案核對

### 5.1 未決條目數

【推論】未決條目數：**0**。

【推論】尚待 adapter 實測的只有 capability facts：是否能讀 reliable remaining、是否能分類 rejection、是否有 reset／retry-after、是否能保守計量 context、是否能在壓縮後重掛 segment。每一個 true／false 都已有唯一 branch 與 typed result；沒有「測完再決定語意」。

### 5.2 新增、取代或保留的 ClaimSpec semantic ids

【推論】ConstraintSpec 是新語言，但 ClaimSpec meta-schema 不需升版；既有 `claimspec_version=0.2.0` 的 `subject.contract` 已能綁 `constraint-catalog.v1`、owner gate、context assembler 與 quota gate。把 constraint-specific policy 欄硬塞進 ClaimSpec 才會混淆宣告與驗收。

| semantic id | 動作 | 原子保證 |
|---|---|---|
| `constraint.scope.explicit-selector` | 【推論】新增 | 【推論】四個 scope 維度皆明示 ALL／ANY_OF；空白不變全域。 |
| `constraint.admission.negative-control-required` | 【推論】新增 | 【推論】無可解析 direct-red control evidence 的 proposal 不得 ACTIVE。 |
| `constraint.advisory.not-behavioral-guarantee` | 【推論】新增 | 【推論】ADVISORY ref 出現在 invariant／guarantee list 時 admission 轉紅。 |
| `constraint.enforced.system-gate-unavoidable` | 【推論】新增 | 【推論】ENFORCED 必須綁 owner gate 並拒絕固定旁路反例。 |
| `constraint.enforced.backend-native-insufficient` | 【推論】新增 | 【推論】只剩 backend-native hook 時 all-backend matrix 轉紅。 |
| `constraint.enforced.capability-fail-closed` | 【推論】新增 | 【推論】isolation／mediation offer 不足只回 UNSUPPORTED，不降 advisory、不 skip。 |
| `constraint.lifecycle.no-auto-renew` | 【推論】新增 | 【推論】到期不延長；ENFORCED semantic slot fail closed 到 successor／RETIRED。 |
| `constraint.governance.proposal-cannot-activate` | 【推論】新增 | 【推論】self-maintenance／executor identity 無 activate command path。 |
| `constraint.governance.approval-envelope-bound` | 【推論】新增 | 【推論】activate 綁 proposal／constraint／evidence digest、10 分鐘 one-use nonce，Work 沒有 mint port。 |
| `constraint.governance.recurrence-proposal-bounded` | 【推論】新增 | 【推論】3 次／7 天、至少 2 Work、同 signature 30 天只建一件普通 proposal Work。 |
| `constraint.advisory.context-budget-bounded` | 【推論】新增 | 【推論】16 條、1,024 bytes／條與 A 公式都由外部 assembler 執法。 |
| `constraint.advisory.required-fit-or-no-dispatch` | 【推論】新增 | 【推論】任一 REQUIRED text 放不下就沒有 backend invocation。 |
| `constraint.advisory.omission-disclosed` | 【推論】新增 | 【推論】每個 omitted ref 同時出現在 evidence、event/UI 與 executor header。 |
| `constraint.advisory.reasserted-after-compaction` | 【推論】新增 | 【推論】只有具 reassert capability 的 adapter 能在真壓縮後送達同 digest。 |
| `constraint.snapshot.explicit-rebase` | 【推論】新增 | 【推論】啟用／到期／撤銷後，下一 Execution 前有明確 snapshot rebase event。 |
| `resource.provider-quota.observable.fresh-required` | 【推論】新增並取代第三輪過寬的 `額度缺席保守.claim.json` | 【推論】只對宣告 RELIABLE_REMAINING 的 backend，失鮮／暫缺零新派工。 |
| `resource.provider-quota.observable.worst-case-sufficient` | 【推論】新增 | 【推論】最新 fresh observation 的 remaining 足以涵蓋本次 worst-case provider units 才可派；不冒充 provider atomic reservation。 |
| `resource.provider-quota.unobservable.no-fabricated-value` | 【推論】新增 | 【推論】REJECTION_ONLY／UNOBSERVABLE 的 event 與 UI 不得出現 remaining。 |
| `resource.provider-quota.blind-dispatch.single-flight` | 【推論】新增 | 【推論】不可觀測 paid backend 同時最多一個 Execution。 |
| `resource.provider-quota.blind-circuit.probe-bounded` | 【推論】新增 | 【推論】open 時零普通派工，無 reset signal 時每 24h 最多一個失敗 probe。 |
| `view.provider-quota.observability-truthful` | 【推論】新增 | 【推論】view 明分 capability、provider observation、本地預算與 circuit，不猜剩餘值。 |

【推論】既有 `execution.spend-limit.external`／先保留後花費、`resource.rate-card.reservation-pinned`、`view.fold.events-only` 與 `backend.allocation.work-pinned` 語意不改版；quota 不可觀測不能成為繞過自有帳的理由。

### 5.3 第三輪目錄樹的唯一 diff

【推論】以下 `+`／`M`／`-` 是第三輪定案樹的完整變動；未列路徑不動。`<semantic-id>` 是一檔一責任的固定命名槽，不是允許一個目錄塞多條規則。

```text
規格/
M  目錄.json                                  — 納入 ConstraintSpec、context policy、quota machine 與新 claims digest。
├── 語言/
+   ├── 約束.schema.json                       — ConstraintSpec 1.0、conditional fields、explicit scope 與 TTL 上限。
M   └── 後端能力.schema.json                   — 加 quota mode、context upper-bound meter、turn/reassert capabilities。
├── 執行/
+   ├── 約束/強制約束.machine.json             — Execution-owned constraint revision 的 declared lifecycle。
+   ├── 約束/強制/<semantic-id>.constraint.json — Execution-owned 強制規則；一條一檔。
+   └── 保證/告知上下文不靜默.claim.json        — required-fit、omission manifest 與 reassert 保證。
├── 追求/
M   ├── 追求.machine.json                     — 加 context requirement failure／retry-other-backend／deadline triggers。
+   ├── 約束/強制約束.machine.json             — Pursuit-owned constraint revision lifecycle。
+   └── 約束/強制/<semantic-id>.constraint.json — Pursuit transition／feedback 的強制規則。
├── 工作/
M   ├── 工作.machine.json                     — 加 context invalidated／rebased 的 declared self-transitions 與 gate fact。
+   ├── 重複失敗提案.policy.json               — 3 次／7 天／2 Work／30 天 cooldown 與 typed signature。
+   ├── 約束/強制約束.machine.json             — Work-owned constraint revision lifecycle。
+   ├── 約束/強制/<semantic-id>.constraint.json — fan-out／selection／terminal 的強制規則。
+   └── 保證/重複失敗只提案.claim.json         — detector 只建 ordinary Work，不能寫 ACTIVE constraint。
├── 判準/
+   ├── 約束/強制約束.machine.json             — Criterion-owned constraint revision lifecycle。
+   ├── 約束/強制/<semantic-id>.constraint.json — definition／evaluation／feedback 自身的強制規則。
+   └── 保證/約束准入敏感度.claim.json          — scope、負控、owner/gate 與 advisory-not-guarantee meta claim。
├── 資源/
+   ├── 供應商額度.machine.json                — observable／blind／open／probe／quarantine 宣告式狀態機。
+   ├── 約束/強制約束.machine.json             — Resource-owned constraint revision lifecycle。
+   ├── 約束/強制/<semantic-id>.constraint.json — reserve、eligibility、quota/rate 的強制規則。
-   ├── 保證/額度缺席保守.claim.json            — 過寬語意移除，不把 structural unobservable 當 transient missing。
    ├── 保證/
+       ├── 可觀測額度失鮮封鎖.claim.json       — RELIABLE_REMAINING 的 fresh fail-closed。
+       ├── 不可觀測額度誠實.claim.json         — 不產生偽 remaining。
+       └── 盲派與探針有界.claim.json           — single-flight、circuit 與 probe cap。
├── 效果/
+   ├── 約束/強制約束.machine.json             — Effect-owned constraint revision lifecycle。
+   └── 約束/強制/<semantic-id>.constraint.json — intent／delivery gate 的強制規則。
├── 知識/
M   ├── 知識主張.machine.json                  — 加 ADVISORY_CONSTRAINT profile 與 context invalidation output，不加新狀態。
+   ├── 告知上下文.policy.json                  — 16 條、A 公式、排序、packing 與 rebase 規則。
+   ├── 約束/
+   │   ├── 告知/<semantic-id>.constraint.json  — 跨工作 reusable advisory instances 的唯一位置。
+   │   ├── 強制約束.machine.json              — Knowledge-owned ENFORCED constraint revision lifecycle。
+   │   └── 強制/<semantic-id>.constraint.json  — knowledge admission/use 自身的強制規則。
    └── 保證/
+       ├── 告知不得冒充保證.claim.json         — advisory 只能證明 delivery。
+       ├── 約束生命週期.claim.json             — review、expiry、revocation、no-auto-renew。
+       └── 只能提案不得啟用.claim.json         — self-maintenance 權限負控。
├── 組合/
M   ├── 軟體工程工作.flow.json                 — Knowledge ContextPlan→Execution assembly 與 typed context failure 回 Pursuit。
M   ├── 自我維護.flow.json                     — repeated typed failure→constraint-authoring Work；沒有 install edge。
+   └── 約束治理.flow.json                     — Work candidate→evaluation→PROPOSED→explicit approver command；無 verdict→ACTIVE 自動 binding。
└── 介面/
M   ├── 事件流.schema.json                     — 加 constraint context 與 provider quota/circuit tagged events。
M   └── 應用服務.openapi.yaml                  — 加 propose/admit/retire constraint typed commands；無 auto-activate route。

nova/
+├── 約束/                                    — 無權威狀態的共用宣告語言 kernel。
+│   ├── 公開契約.py                            — ConstraintRef、ExplicitScope、ContextPlan、EnforcementPlan value types。
+│   ├── 載入.py                                — schema、canonical digest、ClaimRef 與 catalog resolution。
+│   ├── 範圍.py                                — finite match、specificity 與 overlap enumeration。
+│   ├── 編譯.py                                — ConstraintSpec 到 owner plan；不提供 activate API。
+│   └── test_語言.py                           — unknown field、implicit ALL、錯 owner、缺負控固定反例。
├── 領域/
│   ├── 執行/
M   │   ├── 公開契約.py                        — 加 InvocationEnvelope、ContextManifest 與 typed context errors。
M   │   ├── 端口.py                            — 加 context plan／conservative meter consumer ports。
+   │   ├── 上下文組裝.py                      — 計 A、pack、產生 manifest、組 machine-owned preamble。
+   │   ├── 約束閘.py                          — invocation／brokered operation 的 Execution-owned PEP。
+   │   └── test_上下文與約束.py                — required-fit、omission、reassert 與旁路反例。
│   ├── 追求/
+   │   └── 約束閘.py                          — Pursuit decision 前的 owner-specific PEP。
│   └── 工作/
M       ├── 維護提案.py                        — 依 typed signature／7-day window／cooldown 建 constraint-authoring Work request。
+       ├── 約束閘.py                          — Work decision 前的 owner-specific PEP。
+       └── test_維護約束提案.py                — 單一 runaway Work、自由文字差異與 cooldown 固定反例。
├── 權威/
│   ├── 判準/
+   │   └── 約束閘.py                          — criterion definition／evaluation／feedback PEP。
│   ├── 資源/
M   │   ├── 額度觀測.py                        — 改成四種 quota capability 與 typed observation／rejection。
+   │   ├── 盲派斷路.py                        — single-flight、open、half-open probe 與 quarantine decisions。
M   │   ├── 資格閘.py                          — 依 quota mode 分 observable fail-closed／blind-bounded。
M   │   └── test_資源.py                       — 加 circuit、probe、no-fabricated-value 與 all-unobservable matrix。
│   ├── 效果/
+   │   └── 約束閘.py                          — effect intent／delivery PEP。
│   └── 知識/
+       ├── 告知約束.py                        — ADVISORY_CONSTRAINT admission、TTL、revocation profile。
+       ├── 上下文計畫.py                      — scope、priority、snapshot 到 ordered ContextPlan。
+       ├── 約束閘.py                          — knowledge admission/use PEP。
M       └── test_治理.py                       — 加 saturation、expiry、rebase 與 proposal-only cases。
├── 應用/
M   ├── 命令.py                                — 加 propose/admit/retire/rebase typed commands。
+   ├── 核准.py                                — 驗 one-use ApprovalEnvelope、digest binding 與 10 分鐘期限；不提供 Work mint port。
M   ├── 排程.py                                — Execution 前取得 ContextPlan 並經 assembler；不自行挑 constraint。
│   └── 處理/
M       ├── 建立工作.py                        — 釘 KnowledgeSnapshot 與 ContextSelectionPolicyVersion digest。
+       ├── 提案約束.py                        — 人／maintenance source 都先建 constraint-authoring Work；accepted result 才寫 PROPOSED。
+       ├── 准入約束.py                        — 驗 Claim evidence 後送 target authority command；需 explicit approver。
+       └── 退役約束.py                        — successor 或有證據 RETIRED，禁止自動續期／刪 tombstone。
├── 基礎設施/
│   └── 狀態庫/sqlite/遷移/
+       └── 0005_約束與額度斷路.sql            — constraint status／scope index／one-use approval／context manifest refs／quota circuit ledger。
├── 介接/執行者後端/
│   ├── 共用/
M   │   ├── manifest.py                        — quota/context capability union。
+   │   └── 上下文.py                          — conservative measure、policy segment、turn reassert adapter contract。
│   └── <每個-backend>/
M       ├── manifest.py                        — 明示 quota mode 與 context offers；不得留 UNKNOWN capability。
M       ├── 額度.py                            — 只產生該 mode 允許的 observation／typed rejection。
+       ├── 上下文.py                          — backend-specific meter／segment binding；opaque compaction 明示 unsupported。
M       └── test_契約.py                       — quota mode、single-flight outcome mapping、context meter／reassert contract。
└── 啟動/
M   ├── 狀態擁有者.py                         — 組 constraint ledger、owner gates 與 quota circuit。
M   └── 應用服務.py                           — 組 Knowledge ContextPlan port、Execution assembler 與 event tail。

前端/src/
M  ├── 事件流/歸約.ts                         — fold constraint manifest、quota capability、circuit／probe events。
├── 畫面/
M  │   ├── 後端額度.ts                        — conditional remaining；UNOBSERVABLE 不畫數字。
+  │   └── 約束治理.ts                        — visual-log 狀態＋本機 explicit review／approve command；不持有 admission decision。
M  └── 文字/zh-TW.json                        — 新 semantic ids 的繁中顯示，不改 wire ids。

架構/
M  ├── 依賴規則.toml                          — 新增「約束→核心」；owner 可 import 約束公開契約，backend 不可讀 registry。
M  ├── 檢查規格引用.py                        — 加 ConstraintRef、owner/path/gate、Claim negative-control closure。
+  ├── 檢查約束歸屬.py                        — advisory 唯一知識路徑、enforced owner-local 與無頂層約束大桶。
M  └── test_依賴規則.py                       — backend 選 constraint、proposal 直接 activate、跨 owner gate 的非法 fixture。

驗收/
+├── 約束/
+│   ├── test_告知不是保證.py                  — advisory 進 guarantee list 的負控。
+│   ├── test_執法點與後端矩陣.py              — system gate、旁路、all active backends、capability fail-closed。
+│   ├── test_上下文額度與省略.py              — 16 條、A 公式、required failure、三處 omission disclosure。
+│   ├── test_壓縮重注入.py                    — 真 compaction 後 outbound exact digest；opaque adapter unsupported。
+│   └── test_過期與提案權.py                  — no-auto-renew、expired fail-closed、proposal 無 activate 權。
+├── 資源/
+│   ├── test_額度不可觀測.py                  — 全 backend 無 remaining 時仍誠實且 bounded dispatch。
+│   └── test_盲派斷路.py                      — single-flight、24h／15m、one-probe 與 crash replay。
M └── 前端契約/test_額度與政策.py              — 新 quota union、no fabricated number、constraint context pure fold。

工具/
M  └── 驗規格.py                              — 納入 ConstraintSpec、scope overlap、owner/gate 與 Claim closure admission。
```

【推論】runtime data tree不新增鬆散的 `約束/` 檔案夾。ConstraintSpec bytes 進既有 CAS，權威狀態與 circuit 進 `權威狀態.sqlite3`，可視事件進既有尾隨庫；另開 mutable JSON 目錄會製造繞過 admission 的第二支筆。

【推論】依賴方向只新增一條 neutral edge：`約束 → 核心`，三層與四權威可 import `約束.公開契約`，但彼此仍不得互 import。Knowledge Authority 輸出 ContextPlan；Execution 只消費 plan；backend 只消費 InvocationEnvelope。這三段不得縮成 backend 自己查知識庫。

【推論】新增 constraint 的共同變更集固定為：instance＋目標 owner gate catalog／plan＋ClaimSpec direct negative evidence＋`目錄.json` digest；ADVISORY 再加 context selection sensitivity，ENFORCED 再加 all-active-backend bypass matrix。缺一項整個 revision 不得 ACTIVE。

### 5.4 哪些第三輪裁決失效

| 第三輪裁決 | 本輪結果 |
|---|---|
| `UNKNOWN`／missing／stale 一律零新付費 Execution | 【推論】**部分失效。**只保留給 manifest 宣告 `RELIABLE_REMAINING` 後的暫時 missing／stale；結構性 `REJECTION_ONLY`／`UNOBSERVABLE` 改走 BLIND_BOUNDED。 |
| UI 顯示 `KNOWN／STALE／UNKNOWN／NOT_APPLICABLE` | 【推論】**被較精確 union 取代。**結構 capability 與 runtime observation／circuit 分開，只有 KNOWN 有 remaining。 |
| Work pin KnowledgeSnapshot | 【推論】**不失效，補上強制 rebase。**constraint activation／expiry／revocation 使 snapshot invalid，下一 Execution 前留下 explicit rebase event。 |
| 四個權威面、三層、父子非 DAG | 【推論】不失效；ConstraintSpec 語言不取得終態寫權。 |
| COOPERATIVE_PROCESS＋per-claim capability negotiation | 【推論】不失效；反而用來拒絕不可避免性不足的 ENFORCED constraint。 |
| ClaimSpec 0.2.0、雙測試池、揭露即燒掉 | 【推論】不失效；ConstraintSpec 只引用它，不改 feedback／isolation 語意。 |
| SQLite single-owner rollback＋獨立 WAL event tail | 【推論】不失效；新增寫入在既有 envelope 內，沒有第二 writer 或 UI domain query。 |
| 本地預算硬上限、RateCard reservation pin、ratio soft／eligibility hard | 【推論】不失效；provider quota 不可觀測只改 eligibility 分支，不能繞 reserve。 |

【推論】本輪也否決需求檔內兩個尚未成為第三輪裁決的說法：強制規則不一定住 Execution gate；「壓縮後正確覆述」不是 delivery guarantee。這不是推翻四面架構，而是阻止新需求把同一種假保證重新塞回來。

### 5.5 最終閉合檢查

【推論】所有新欄位都有 owner、固定值域、typed failure 與負控：scope 沒有 implicit ALL；ADVISORY 沒有 compliance claim；ENFORCED 沒有可繞過 gate 或能力降級；TTL 沒有自動續；proposal 沒有 activation edge。

【推論】上下文容量沒有「以後再調」的空洞：同 scope 16 條、每條 1,024 bytes、A 公式、required 不 fit 即不派、best-effort 固定排序、每條 omission 三處可見，全部已定。

【推論】額度不可觀測沒有被留在風險表：literal UI 數字要求被明確判為不可滿足，替代 view contract、manifest modes、single-flight、24h／15m circuit、one-probe cap 與 ClaimSpec 都已定。

【推論】最終未決數仍為 **0**。下一步可以直接依下列可獨立測試子系統拆 spec／plan：ConstraintSpec 語言與 admission、owner enforcement gates、知識／context assembly、provider quota／circuit、事件／UI 契約；不需要再回來問任何 schema 欄位或 fallback 語意。
