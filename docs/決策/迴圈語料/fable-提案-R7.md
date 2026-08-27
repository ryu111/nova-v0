# fable 第七輪提案（R7-01～R7-02，全部 fable 作者）

第一輪沒有退回件、由我自選題。選題判準沿用控制端那條：
**「不補會不會讓一條已編列的保證在帳面上維持綠色」**。兩條都命中：
R7-01 是交接 §十八 待辦一（已編列的固定負控懸空無主體），R7-02 是 R3-05 落地後
新生的縫（choreography 對 `feedback_ref` 缺席的行為未定義）。兩條都在 plan 08、
都在實作前的窗內。

**Mock-apply（基線 main `2c2bec1`）**：

```
基線：計畫 22 份 · Create 761 · task 188 · 未遷移 131 · 實存 claim 檔 13
草稿：計畫 22 份 · Create 768 · task 190 · 未遷移 131 · 實存 claim 檔 13
I1–I11 全部成立，EXIT=0
```

複驗指令：`uv run python /private/tmp/fable-R7-mock/docs/計畫複驗.py /private/tmp/fable-R7-mock/docs/計畫`
可套用 diff：`/private/tmp/fable-R7-mock/fable-R7-草稿.diff`（237 行，只涉
`docs/計畫/08-目標追求生命週期.md` 一檔）；備份在你 scratchpad 的 `fable-R7-草稿.diff`。
**請重跑，不要信我貼的輸出——我也是執行者。**

**值得記的一筆**：mock 第一跑**紅了**——I8 抓到我自己寫的黏寫識別字
`test_同ref下段內容漂移必須被拒`（`ref` 黏漢字），改成 `同參照` 後全綠。
閘不分作者，它在做真的工作。

**diff 相依性**：兩條都接在 plan 08 檔尾（Task 9、Task 10）且都補 File Structure，
hunk 物理上相鄰——**R7-02 的 diff 以 R7-01 已套用為前提**；只核准其一時我十分鐘內
重切（Task 序號與 File Structure 行會變）。

**基線帳**：兩條的新 task 皆帶落點行，**未遷移基線 131 不動**，計畫複驗.py 零改動。

**DOI**：本輪零 DOI 引用（地基是 Anthropic／AWS／OpenAI 官方文件與 arXiv:1506.02629，
無 Crossref 可驗項）。**誠實帳**：無新實驗；R7-02 的成員集設計是我的裁量，
開放問題明標供裁定（見該條）。

---

### R7-01(fable) 提示家族有內容定址的主體（交接 §十九 第 3 項）

**狀態**：PROPOSED

**要修的洞**
`prompt_family_ref` 是 `PursuitIdentity` 的 immutable 欄位、在 `IDENTITY_BREAKING_FIELDS`
（08:382）、是 Task 5 change matrix 的一維（08:368）——但 22 份計畫裡它的指涉物命中
**0**（查證：`grep -rn "PromptFamily" docs/計畫/*.md` → 只有 08 的三處 ref 用法）。
R1-01 把比較修成比 `effective_content_digest`，修好了**比較器**；被比較的東西仍不存在
——Task 1 的 (b) fixture 與 Task 5 的 prompt_family 維只能拿任意發明的 bytes 當主體。
連帶（§十八 原文）：工具清單→system prompt→固定文件那串前綴的內容與**順序**沒有
任何計畫定義過，**前綴漂了不會有人紅**。

**改什麼**
`docs/計畫/08-目標追求生命週期.md` 新增 Task 9（6 檔）＋File Structure 補列＋
Exit Gate 補 `nova/領域/提示` 與 `prompt.family.*`：
- Create: `規格/提示/PromptFamily.schema.json`——封閉欄位 {`semantic_id`, `revision`,
  `segments`（**有序**，每段 {`segment_kind`, `content_ref`, `content_digest`}）}；
  `segment_kind` 封閉 enum {`SYSTEM_PROMPT`, `TOOL_CATALOG`, `FIXED_DOCUMENT`,
  `OUTPUT_CONTRACT`}，未知 kind fail-closed；段內容住 CAS（計畫 04）。
- Create: `規格/提示/保證/提示家族內容定址.claim.json`（claim `prompt.family.content-addressed`）
- Create: `nova/領域/提示/家族.py`（canonical bytes＝依宣告順序串接
  `(segment_kind, content_digest)` 的 canonical JSON；family digest 對它取；
  **順序是身分的一部分**）＋ `test_提示家族.py`
- Create: `驗收/追求/測_提示家族身分.py`；Modify: `nova/領域/追求/模型.py`
  （`resolve_identity_ref` 對 prompt_family 解析到本 artifact，逐段驗 digest、
  重算 family digest；不符回既有 `UNRESOLVED_IDENTITY_REF`）。
- **`prompt_family_ref` 的 digest 從此有 preimage——就是那份 canonical bytes。**

**邊界（正面宣告）**：本條只定義 artifact 與 canonical bytes。governance（誰有權鑄
revision、admission authority）屬計畫 10 落點（§十九 第 4 項）不碰；invocation 時的
完整前綴組裝與計量屬計畫 12 Task 7 前（第 5 項）不碰。
**落點說明**：sol 給的落點「plan 08 Task 1 後」——本 task 落檔尾 Task 9，序位在
Task 1 之後即滿足；插入重編會讓既有 task 落點行全部錯位，代價無收益。
**命名裁量**：claim namespace `prompt.family.*` 是新開的（I11 只驗綁定不管 namespace
語意），供審。

**地基**
- 官方：Anthropic prompt caching——cache hit 要求前綴**逐字相同**、hash 累積、
  階層固定 tools → system → messages（順序入身分的直接依據，§十九 可用地基表）；
  AWS Bedrock Prompt Management 與 OpenAI Agents SDK `Prompt`——prompt 是版本化
  artifact（id＋version）。
- **segment_kind 成員集與 canonical serialization 具體形狀：無地基，nova 拆解決定。**

**加蓋**：未知 segment_kind、散文 family、同 ref 內容漂移、順序不敏感 digest——全拒。
不改地基介面。

**固定負控**（四格＋防恆真兩條）
- `segment-reorder-same-set` → [`segment_order_is_identity`]
- `content-drift-under-same-ref` → [`digest_mismatch_rejected`]——Task 1 的 (b) fixture
  從此有真主體，predicate 同名沿用
- `prose-family` → [`family_requires_canonical_bytes`]
- `unknown-segment-kind` → [`segment_kind_vocabulary_closed`]
- 防恆真：兩個不同 semantic_id、同 canonical bytes → 同 family digest →
  `SAME_PURSUIT`（Task 1 防恆真格接上真主體）；合法換段內容 → `NEW_PURSUIT_REQUIRED`

**不變式檢查**：Task 9 檔 6／claim 1／落點行／先紅步 Expected: FAIL／恰 1 commit。
**mock-apply I1–I11 全綠**（含一次真實的 I8 紅→修正）。

---

### R7-02(fable) 回饋耗盡是顯式決定不是靜默降級

**狀態**：PROPOSED

**要修的洞**
R3-05 落地後，揭露額度耗盡是**會發生的正常狀態**（cap 事前釘、verdict 照記、只斷回饋
——06:497 `DISCLOSURE_BUDGET_EXHAUSTED`）。而 08 Task 3 Step 3 的 choreography 寫死
`FeedbackAccepted(feedback_ref=verdict.feedback_ref)`（08:253-258）——`feedback_ref`
**缺席時的行為未定義**。未定義的下場只有兩種：實作者偽造空 packet（把「沒有回饋」
冒充「回饋是空的」，污染事件流），或靜默續跑（executor 盲燒 16 次 attempt 而帳面
看不出它已無回饋可學）。兩者都是靜默降級。
- 查證：`grep -rn "on_feedback_exhausted\|FEEDBACK_EXHAUSTED" docs/計畫/` → 套用前 0。

**改什麼**
`docs/計畫/08-目標追求生命週期.md` 新增 Task 10（6 檔）＋File Structure 補列：
- Create: `規格/追求/保證/回饋耗盡要顯式.claim.json`（claim `pursuit.feedback.exhaustion-explicit`）
  ＋ `驗收/追求/測_回饋耗盡.py`
- Modify: `規格/追求/AttemptPolicy.schema.json`——增**必填無預設**
  `on_feedback_exhausted ∈ {CONTINUE_BLIND, POLICY_STOP}`，admission 拒缺席。
  這是「顯式決定不可缺席」原則的第二次適用（第一次是 `max_stagnant_attempts`）——
  不是援引先例，是同一原則：nova 拒絕替呼叫端偷做預設決定。
  **開放問題供裁定**：成員集是否該有第三支（例如降頻續跑）；v1 取最小集。
- Modify: `規格/追求/追求.machine.json`（`POLICY_STOP` reason enum 增
  `FEEDBACK_EXHAUSTED`，closed、無影子名）、`nova/領域/追求/決策.py`、
  `nova/應用/推進追求.py`——耗盡分支：`CONTINUE_BLIND` → retry 輸入帶 typed
  `FEEDBACK_EXHAUSTED` 標記，不偽造不重用；`POLICY_STOP` → 終態。
- **盲跑仍有界**：停滯量測（Task 8）用 verdict vector 不用 FeedbackPacket——verdict
  照記，所以 `CONTINUE_BLIND` 下停滯窗照常計數、16 次上限照常；盲跑不是無界燒錢。

**地基**
- 官方層查不到「feedback 耗盡消費協定」（照實寫）。權威：arXiv:1506.02629——揭露
  上限的存在理由（R3-05 既有地基），本條是它的消費端。
- **分支形狀與成員集：無地基，nova 拆解決定**（「不得靜默降級」既有原則的落實）。

**加蓋**：缺政策 admission 拒、偽造／重用 packet 拒、`POLICY_STOP` 下續跑拒（動作①）；
reason enum 加成員（動作②）。不改地基介面。

**固定負控**（四格＋防恆真兩條）
- `fabricated-empty-packet` → [`no_fabricated_feedback`]
- `silent-continue-without-policy` → [`exhaustion_policy_required`]
- `stop-policy-still-starts` → [`stop_policy_refuses_start`]
- `shadow-reason-name` → [`terminal_reason_vocabulary_closed`]（Task 8 同族紀律）
- 防恆真：`CONTINUE_BLIND` 下照常續跑、標記入 retry 輸入、停滯窗照常計數到觸發
  （與 Task 8 的交點正控）；cap 未滿時本政策不介入。

**不變式檢查**：Task 10 檔 6／claim 1／落點行／先紅步 Expected: FAIL／恰 1 commit。
Modify 四檔皆本計畫 Task 1／2／3 Create（I5 成立）。**mock-apply I1–I11 全綠。**

---

## 刻意沒做的

1. **PromptFamily governance 與 PromptPlan 前綴沒有一起提**——三件事三個落點
   （08／10／12），一次提完口徑就超過「一次做得完」；content identity 是另外兩件的
   前置，先立主體。
2. **R7-02 沒有做第三支政策成員**——最小集先行，成員集開放供裁定。
3. **Visual evaluator protocol（§十九 第 9 項）本輪未選**——它的窗（第一個 visual
   criterion）還遠，且需要先查 Playwright 地基的權威層；下輪候選。

## 給 claude 的順手訊息（不是決議）

- mock 目錄：R7 的 `/private/tmp/fable-R7-mock/` 裁決前請留；R6 的可刪。
- 這輪 I8 抓到我自己的黏寫識別字——「閘不分作者」又一實例，值得留在帳本裡。
