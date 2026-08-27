codex
我會先重跑 R7 鏡像閘，再把兩條拆成「它實際證明什麼」與「它文字宣稱證明什麼」比較。R7-01 的關鍵不是 CAS 遞迴是否成立，而是 `family_digest` 有沒有被冒充成 R1-01 要求的 effective outbound digest。
exec
/bin/zsh -lc "UV_CACHE_DIR=/private/tmp/nova-uv-cache uv run python /private/tmp/fable-R7-mock/docs/計畫複驗.py /private/tmp/fable-R7-mock/docs/計畫 && rg -n -C 5 'effective_content_digest|prompt_family_ref|PromptFamily|family digest|on_feedback_exhausted|CONTINUE_BLIND|FEEDBACK_EXHAUSTED' /private/tmp/fable-R7-mock/docs/計畫/08-目標追求生命週期.md" in /Users/sbu/nova
 succeeded in 0ms:
計畫 22 份 · Create 路徑 768 個 · task 190 個 · ClaimSpec 落點未遷移 131 個 · 實存 claim 檔 13 份
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
19-- 【推論】Pursuit 不可讀其他平行 Pursuit 的 candidate/intermediate reasoning；交換後 lineage 必須標依賴，不能繼續宣稱獨立。
20-- 【推論】任何 Execution 只能 nominate 一個 CandidateBundle；同一 candidate digest × criterion revision 最多一個有效 final verdict。
21-
22-## 子系統規格
23-
24:【推論】`PursuitIdentity` 固定包含 `strategy_family`、`prompt_family_ref`、`model_family_policy`、`backend_policy_ref`、`evidence_scope_ref`、`workspace_scope_ref`、`tool_policy_ref`、`seed_policy`、`knowledge_snapshot_ref`；建立後 immutable。
25-
26-【推論】**每個 `*_ref` 一律是 `{semantic_id, revision, digest}` 三元組，不是裸字串。**
27-理由：identity 比較若比字串，兩個不同 ref 指向同一份 bytes 會判「要開新 Pursuit」、
28-同一個 ref 底下內容漂移會判「同一個 Pursuit」——**兩種錯都不會有測試轉紅**，
29-Task 5 的 change matrix 就成了恆真格。帶 digest 之後字串相等 ⇔ 內容相等，恆真消失。
30:比較的依據是 `effective_content_digest`（該 ref 實際交付內容的 digest），
31-**不是只含間接引用的 manifest source digest**；完整三元組仍留在記錄中供稽核。
32-缺 digest 的 ref 進到比較一律 typed `UNRESOLVED_IDENTITY_REF`，digest 與 CAS bytes 不符亦然。
33-
34-【推論】每次 retry 的輸入由 `checkpoint_ref + FeedbackPacket ref + next Execution selection` 組成；raw verdict 或 sealed evidence 不可進 execution input。
35-
--
55-    ├── 判準裁定才提交.claim.json             — executor self-success cannot submit。
56-    ├── 暫停換後端不終結.claim.json           — same Pursuit, new Execution/backend。
57-    ├── identity不可偷換.claim.json            — identity-changing resume direct red。
58-    └── 獨立證據面.claim.json                 — parallel scopes do not cross-read。
59-規格/提示/
60:├── PromptFamily.schema.json                  — 有序段集合與 canonical bytes 的封閉 schema。
61-└── 保證/
62-    └── 提示家族內容定址.claim.json           — 順序入身分、漂移拒絕、散文家族拒絕。
63-nova/領域/提示/
64:├── 家族.py                                   — canonical serialization 與 family digest。
65-└── test_提示家族.py                          — 順序、漂移、未知段 kind 負控。
66-nova/領域/追求/
67-├── 公開契約.py                               — commands/events/checkpoint/candidate/terminal types。
68-├── 模型.py                                   — PursuitAggregate and immutable identity。
69-├── 決策.py                                   — attempt/evaluation/pause/stop pure decisions。
--
385-Expected: 【推論】FAIL at fingerprint case。
386-
387-- [ ] **Step 3: 寫 exact dimension comparison；禁止 arbitrary equality hook**
388-
389-```python
390:IDENTITY_BREAKING_FIELDS = ("model_family_policy", "prompt_family_ref", "evidence_scope_ref", "workspace_scope_ref", "tool_policy_ref", "knowledge_snapshot_ref")
391-```
392-
393:【推論】**每一維比的是 `effective_content_digest`，不是 ref 字串。** 兩個不同 `semantic_id`
394-指向同一份 bytes 判 `SAME_PURSUIT`（並留下 ref-changed 稽核事件）；同一個 `semantic_id`
395-底下 digest 不同一律拒絕 floating ref。缺 digest 進到比較回 `UNRESOLVED_IDENTITY_REF`。
396-
397-- [ ] **Step 4: 跑 matrix/property tests 與 ClaimSpec**
398-
--
613----
614-
615-### Task 9: 提示家族有內容定址的主體
616-
617-**Files:**
618:- Create: `規格/提示/PromptFamily.schema.json`
619-- Create: `規格/提示/保證/提示家族內容定址.claim.json`
620-- Create: `nova/領域/提示/家族.py`
621-- Create: `nova/領域/提示/test_提示家族.py`
622-- Create: `驗收/追求/測_提示家族身分.py`
623-- Modify: `nova/領域/追求/模型.py`
624-
625-**Interfaces:**
626:- Produces: `PromptFamily`——封閉欄位：`semantic_id`、`revision`、`segments`（**有序** tuple，
627-  每段 `{segment_kind, content_ref, content_digest}`）。`segment_kind` 封閉 enum：
628-  `SYSTEM_PROMPT`、`TOOL_CATALOG`、`FIXED_DOCUMENT`、`OUTPUT_CONTRACT`；
629-  未知 kind fail-closed（未來成員以加蓋動作②擴充）。段內容住 CAS（計畫 04），
630-  family 只持 ref 與 digest。
631-- Produces: `canonical_family_bytes(family) -> bytes`——依宣告順序串接
632-  `(segment_kind, content_digest)` 的 canonical JSON；`family_digest` 對它取 digest。
633-  **順序是身分的一部分**：同段集合、不同順序＝不同 family。
634:  `prompt_family_ref = {semantic_id, revision, digest}` 的 digest **從此有 preimage**
635-  ——就是這份 canonical bytes。
636:- Produces: `resolve_identity_ref` 對 `prompt_family_ref` 解析到本 artifact：
637:  逐段驗 `content_digest` 對 CAS bytes、重算 family digest 比對 ref；
638-  任一不符回 `UNRESOLVED_IDENTITY_REF`（Task 1 既有 code，不新增）。
639-- **邊界（正面宣告，不是省略）**：本 task 只定義 artifact 與它的 canonical bytes。
640-  **governance**（誰有權鑄新 revision、admission authority、與 KnowledgeSnapshot 的
641-  resolve 關係）屬計畫 10 的落點（交接 §十九 第 4 項），本 task 不碰；
642-  **invocation 時的完整前綴組裝與計量**（把 family 變成真後端收到的 context）屬
643-  計畫 12 Task 7 前的落點（第 5 項），本 task 不碰。
644-
645:**為什麼**：`prompt_family_ref` 是 `PursuitIdentity` 的 immutable 欄位、在
646-`IDENTITY_BREAKING_FIELDS`、是 Task 5 change matrix 的一維——但 22 份計畫裡
647-它的指涉物命中 **0**：沒有 schema、沒有 Create、沒有 canonical bytes 的定義。
648:R1-01 把比較修成比 `effective_content_digest`，修好了**比較器**；被比較的東西
649-仍不存在——Task 1 的 (b) fixture 與 Task 5 的 prompt_family 維只能拿任意發明的
650-bytes 當主體，比較器被證明了，「prompt family 變了」的生產語意仍未定義。
651-連帶（交接 §十八 原文）：工具清單→system prompt→固定文件那串前綴的內容與**順序**
652-沒有任何一份計畫定義過，**前綴漂了不會有人紅**。
653-落點說明：sol 給的落點是「plan 08 Task 1 後」（§十九 第 3 項）；本 task 落檔尾
--
671-`digest_mismatch_rejected`——Task 1 的 (b) fixture 從此有真主體，predicate 同名沿用。
672-`prose-family`：只有散文描述、無 canonical bytes 與 digest 的 family，必須紅在
673-`family_requires_canonical_bytes`。
674-`unknown-segment-kind`：`segment_kind` 塞 enum 外新值，closed schema 必須拒，
675-紅在 `segment_kind_vocabulary_closed`。
676:防恆真格兩條：兩個不同 `semantic_id`、同 canonical bytes → family digest 相同，
677-經 Task 5 comparator 判 `SAME_PURSUIT`（Task 1 防恆真格接上真主體）；
678-合法換 `SYSTEM_PROMPT` 段內容 → digest 改變 → `NEW_PURSUIT_REQUIRED`。
679-
680-- [ ] **Step 1: 寫四個負控與兩個防恆真格的 red tests**
681-
--
693-
694-- [ ] **Step 2: 跑紅測確認今天 prompt_family 的 digest 沒有 preimage**
695-
696-Run: `uv run pytest -q nova/領域/提示/test_提示家族.py 驗收/追求/測_提示家族身分.py`
697-
698:Expected: 【推論】FAIL；`PromptFamily` schema 與 canonical bytes 尚不存在，
699:`prompt_family_ref` 的 digest 是一個沒有定義過內容的數字。不得是收集錯誤冒充紅測。
700-
701-- [ ] **Step 3: 寫 schema、canonical serialization 與 resolve 接線**
702-
703-- [ ] **Step 4: 跑四個負控、兩個防恆真格與 ClaimSpec**
704-
--
707-Expected: 【推論】PASS；四個負控各紅在自己宣告的 predicate。
708-
709-- [ ] **Step 5: Commit**
710-
711-```bash
712:git add 規格/提示/PromptFamily.schema.json 規格/提示/保證/提示家族內容定址.claim.json nova/領域/提示 驗收/追求/測_提示家族身分.py nova/領域/追求/模型.py
713-git commit -m "feat: 提示家族有內容定址的主體"
714-```
715-
716----
717-
--
724-- Modify: `規格/追求/追求.machine.json`
725-- Modify: `nova/領域/追求/決策.py`
726-- Modify: `nova/應用/推進追求.py`
727-
728-**Interfaces:**
729:- Produces: `AttemptPolicy.on_feedback_exhausted ∈ {CONTINUE_BLIND, POLICY_STOP}`，
730-  **必填無預設**，admission 拒缺席——顯式決定不可缺席這條設計原則的第二次適用
731-  （第一次是 Task 8 的 `max_stagnant_attempts`；不是援引先例，是同一原則：
732-  nova 拒絕替呼叫端偷做預設決定）。**成員集是否該有第三支（例如降頻續跑）供裁定，
733-  v1 取最小集。**
734-- Produces: 揭露額度耗盡（計畫 06 Task 8 的 `DISCLOSURE_BUDGET_EXHAUSTED`——
735-  verdict 照記、只斷回饋）時，`CLAIM_REJECTED` 分支的 retry 輸入**不再有
736:  `feedback_ref`**：依宣告政策——`CONTINUE_BLIND` → `RetryRequested` 帶 typed
737:  `FEEDBACK_EXHAUSTED` 標記，**不偽造空 packet、不重用舊 packet 冒充新鮮**；
738:  `POLICY_STOP` → Pursuit 進 `POLICY_STOP(FEEDBACK_EXHAUSTED)`。
739:- Produces: `POLICY_STOP` reason enum 增 `FEEDBACK_EXHAUSTED`（closed，
740-  無影子名——Task 8 的 `terminal_reason_vocabulary_closed` 同族紀律）。
741-- Produces: 盲跑仍有界：停滯量測（Task 8）用的是 verdict vector 不是 FeedbackPacket
742:  ——verdict 照記，所以 `CONTINUE_BLIND` 下停滯窗照常計數，16 次 attempt 上限照常；
743-  盲跑不是無界燒錢。
744-
745-**為什麼**：計畫 06 Task 8 落地後，揭露帳耗盡是一個**會發生的正常狀態**（cap 事前釘、
746-verdict 照記、只斷回饋），而 Task 3 的 choreography 寫死
747-`FeedbackAccepted(feedback_ref=verdict.feedback_ref)`——`feedback_ref` 缺席時的行為
748-**未定義**。未定義的下場只有兩種：實作者偽造空 packet（把「沒有回饋」冒充成
749-「回饋是空的」，污染 FeedbackAccepted 事件流），或靜默續跑（executor 盲燒 16 次
750-attempt 而帳面看不出它已經沒有回饋可學）。兩者都是靜默降級。
751-- 查證：`sed -n '253,258p' docs/計畫/08-目標追求生命週期.md`（Step 3 的 match 分支
752-  無 feedback 缺席臂）；`grep -n "DISCLOSURE_BUDGET_EXHAUSTED" docs/計畫/06-*.md`
753:  → 497（耗盡語意既有）；`grep -rn "on_feedback_exhausted\|FEEDBACK_EXHAUSTED"
754-  docs/計畫/` → 套用前 0。
755-地基：官方層查不到「feedback 耗盡消費協定」（照實寫）。權威：Dwork 等
756-arXiv:1506.02629——揭露上限的存在理由（R3-05 既有地基），本 task 是它的消費端；
757-**分支形狀與成員集：無地基，這是 nova 的拆解決定**（「不得靜默降級」既有原則的落實）。
758-加蓋：缺政策的 AttemptPolicy admission 拒、偽造／重用 packet 拒、`POLICY_STOP`
--
762-
763-**ClaimSpec落點:** `pursuit.feedback.exhaustion-explicit` → `規格/追求/保證/回饋耗盡要顯式.claim.json`（本 task Create）
764-
765-**固定負控:** 【推論】四格。`fabricated-empty-packet`：耗盡後造空 packet（或重用上一輪
766-packet）冒充新鮮回饋餵 `FeedbackAccepted` 的變體，必須紅在 `no_fabricated_feedback`。
767:`silent-continue-without-policy`：`AttemptPolicy` 缺 `on_feedback_exhausted` 仍通過
768-admission 的變體，必須紅在 `exhaustion_policy_required`。
769-`stop-policy-still-starts`：宣告 `POLICY_STOP` 而耗盡後仍 `StartExecution` 的變體，
770-必須紅在 `stop_policy_refuses_start`。
771-`shadow-reason-name`：終態理由寫成 enum 外名（如 `FEEDBACK_DEPLETED`），closed enum
772-必須拒，紅在 `terminal_reason_vocabulary_closed`。
773:防恆真格兩條：`CONTINUE_BLIND` 宣告下耗盡後照常續跑、`FEEDBACK_EXHAUSTED` 標記
774-入 retry 輸入、且停滯窗照常計數到觸發（與 Task 8 的交點正控）；
775-cap 未滿時 feedback 照常流動，本政策不介入。
776-
777-- [ ] **Step 1: 寫四個負控與兩個防恆真格的 red tests**
778-
779-```python
780-def test_耗盡後不得偽造空回饋() -> None:
781:    軌跡 = 跑追求(判準回拒絕(feedback_ref=None), 政策(on_feedback_exhausted="CONTINUE_BLIND"))
782-    assert not 軌跡.事件含偽造packet()
783:    assert 軌跡.retry輸入.標記 == "FEEDBACK_EXHAUSTED"
784-
785-def test_停止政策下耗盡不得再啟動() -> None:
786:    軌跡 = 跑追求(判準回拒絕(feedback_ref=None), 政策(on_feedback_exhausted="POLICY_STOP"))
787:    assert 軌跡.終態理由 == "FEEDBACK_EXHAUSTED"
788-```
789-
790-- [ ] **Step 2: 跑紅測確認今天 feedback_ref 缺席行為未定義**
791-
792-Run: `uv run pytest -q 驗收/追求/測_回饋耗盡.py`

codex
## R7-01(fable) — REJECT `WEAKENS_GUARANTEE`

一句話：Task 9 建立了可信的 PromptFamily source artifact，但隨即把 `family_digest` 當成 Task 5 的 `effective_content_digest`；組裝政策尚未入 PursuitIdentity，因此同一 Pursuit 可以在 family 不變時收到不同的有效前綴，既有 identity 保證仍可能假綠。

`family_digest` 的遞迴內容綁定成立。問題不是 CAS，而是它證明的層級：

```text
family_digest
  = PromptFamily 宣告內容與順序的身分

effective_prompt_digest
  = PromptFamily
  + 組裝政策
  + 實際解析出的有效段落
```

目前只完成第一層，卻接到要求第二層的比較器。

### 可重提的最小修改

Task 9 可以保留，但必須補以下界線：

- `family_digest` 明確改稱或定義為 `source_artifact_digest`，不得冒稱完整 `effective_content_digest`。
- `PursuitIdentity` 現在就增加內容定址的 `prompt_assembly_policy_ref`，並列入 `IDENTITY_BREAKING_FIELDS`。
- 定義：

  ```text
  effective_prompt_digest =
      digest(
          resolved ordered semantic segments
          + prompt_assembly_policy revision/digest
      )
  ```

- Task 9 可以先建立 family resolver；plan 12 才實作 compiler 與真實組裝，但在 plan 12 完成前：

  - 不得宣稱 PromptFamily 相同等於有效前綴相同；
  - 不得讓缺 `prompt_assembly_policy_ref` 的 Pursuit 通過 admission；
  - Task 5 的 production 比較不得把 `family_digest` 直接代入 `effective_content_digest`。

- 固定負控新增：

  - `same-family-different-assembly-policy`  
    → `assembly_policy_is_identity`
  - `family-digest-used-as-effective-digest`  
    → `effective_digest_covers_assembly_policy`

- plan 12 後續還必須證明：相同 family＋相同 assembly policy 解析成相同 canonical semantic prefix。後端通道序列化則由 adapter conformance 另驗，不塞進 family claim。

因此你的疑問成立：這不是 cache 條款單獨負責的事。cache hit/miss 的 outbound bytes parity 是另一條保證；但「組裝政策改變是否仍屬同一 Pursuit」必須現在進 identity，不能等 cache 測試補救。

### Namespace 裁量

`prompt.family.*` 可以接受。它描述的是中立的 prompt artifact，不是特定後端，也不是 Pursuit lifecycle 本身。建議固定 namespace 分工：

- `prompt.family.*`：家族 artifact、解析、內容身分
- `prompt.plan.*`：有效組裝與 semantic prefix
- `execution.prompt.*`：adapter 實際 outbound mapping

I11 目前不檢查 namespace 語意不影響本次判斷；後續可另加 namespace ownership lint，但不綁進本條。

---

## R7-02(fable) — APPROVE

一句話：揭露額度耗盡後只有「明示盲跑」或「明示停止」兩種 v1 語意，能封住偽造空 feedback 與靜默續跑，且兩條路都仍受既有停滯與 attempt 上限約束。

### 寫入條件

耗盡不能只變成 retry payload 裡的一個字串。事件模型必須明確區分：

```text
FeedbackAccepted(feedback_ref)
FeedbackUnavailable(reason=DISCLOSURE_BUDGET_EXHAUSTED)
```

因此 Files 至少要補 Modify 真正擁有該 typed event union 的檔案，例如 `nova/領域/追求/公開契約.py` 或其實際 owner；仍在十檔上限內。

並釘死：

- `FeedbackAccepted` 永遠要求有效 `feedback_ref`，不可 nullable。
- 耗盡時先記 `FeedbackUnavailable`，再依政策產生：

  - `CONTINUE_BLIND` → `RetryRequested(feedback_state=FEEDBACK_EXHAUSTED)`
  - `POLICY_STOP` → `POLICY_STOP(FEEDBACK_EXHAUSTED)`

- `CONTINUE_BLIND` 不得重用舊 feedback ref。
- progress measure 可以讀系統內部保存的 verdict vector，但該 vector 不得因此重新洩漏給 executor。
- 固定負控新增或擴充一格：

  - `feedback-accepted-without-ref`  
    → `feedback_accepted_requires_ref`

### 是否需要第三支

v1 不加第三支。

「降頻續跑」不是第三種終局語意，而是帶參數的新排程政策，至少還需要定義：

- 降頻單位
- 觸發時點
- 剩餘 attempt 如何重算
- 是否建立 superseding Pursuit
- 對 deadline 與 budget reservation 的影響

現在塞入 enum 只會得到一個沒有完整狀態機語意的名字。未來若有量測證明二元政策造成不必要停止或浪費，再以 namespaced policy 擴充；目前 `{CONTINUE_BLIND, POLICY_STOP}` 已封閉所有必要 v1 行為。

## 本輪票面

| 決議 | 裁決 |
|---|---|
| R7-01 | REJECT `WEAKENS_GUARANTEE` |
| R7-02 | APPROVE |
tokens used
16,288
## R7-01(fable) — REJECT `WEAKENS_GUARANTEE`

一句話：Task 9 建立了可信的 PromptFamily source artifact，但隨即把 `family_digest` 當成 Task 5 的 `effective_content_digest`；組裝政策尚未入 PursuitIdentity，因此同一 Pursuit 可以在 family 不變時收到不同的有效前綴，既有 identity 保證仍可能假綠。

`family_digest` 的遞迴內容綁定成立。問題不是 CAS，而是它證明的層級：

```text
family_digest
  = PromptFamily 宣告內容與順序的身分

effective_prompt_digest
  = PromptFamily
  + 組裝政策
  + 實際解析出的有效段落
```

目前只完成第一層，卻接到要求第二層的比較器。

### 可重提的最小修改

Task 9 可以保留，但必須補以下界線：

- `family_digest` 明確改稱或定義為 `source_artifact_digest`，不得冒稱完整 `effective_content_digest`。
- `PursuitIdentity` 現在就增加內容定址的 `prompt_assembly_policy_ref`，並列入 `IDENTITY_BREAKING_FIELDS`。
- 定義：

  ```text
  effective_prompt_digest =
      digest(
          resolved ordered semantic segments
          + prompt_assembly_policy revision/digest
      )
  ```

- Task 9 可以先建立 family resolver；plan 12 才實作 compiler 與真實組裝，但在 plan 12 完成前：

  - 不得宣稱 PromptFamily 相同等於有效前綴相同；
  - 不得讓缺 `prompt_assembly_policy_ref` 的 Pursuit 通過 admission；
  - Task 5 的 production 比較不得把 `family_digest` 直接代入 `effective_content_digest`。

- 固定負控新增：

  - `same-family-different-assembly-policy`  
    → `assembly_policy_is_identity`
  - `family-digest-used-as-effective-digest`  
    → `effective_digest_covers_assembly_policy`

- plan 12 後續還必須證明：相同 family＋相同 assembly policy 解析成相同 canonical semantic prefix。後端通道序列化則由 adapter conformance 另驗，不塞進 family claim。

因此你的疑問成立：這不是 cache 條款單獨負責的事。cache hit/miss 的 outbound bytes parity 是另一條保證；但「組裝政策改變是否仍屬同一 Pursuit」必須現在進 identity，不能等 cache 測試補救。

### Namespace 裁量

`prompt.family.*` 可以接受。它描述的是中立的 prompt artifact，不是特定後端，也不是 Pursuit lifecycle 本身。建議固定 namespace 分工：

- `prompt.family.*`：家族 artifact、解析、內容身分
- `prompt.plan.*`：有效組裝與 semantic prefix
- `execution.prompt.*`：adapter 實際 outbound mapping

I11 目前不檢查 namespace 語意不影響本次判斷；後續可另加 namespace ownership lint，但不綁進本條。

---

## R7-02(fable) — APPROVE

一句話：揭露額度耗盡後只有「明示盲跑」或「明示停止」兩種 v1 語意，能封住偽造空 feedback 與靜默續跑，且兩條路都仍受既有停滯與 attempt 上限約束。

### 寫入條件

耗盡不能只變成 retry payload 裡的一個字串。事件模型必須明確區分：

```text
FeedbackAccepted(feedback_ref)
FeedbackUnavailable(reason=DISCLOSURE_BUDGET_EXHAUSTED)
```

因此 Files 至少要補 Modify 真正擁有該 typed event union 的檔案，例如 `nova/領域/追求/公開契約.py` 或其實際 owner；仍在十檔上限內。

並釘死：

- `FeedbackAccepted` 永遠要求有效 `feedback_ref`，不可 nullable。
- 耗盡時先記 `FeedbackUnavailable`，再依政策產生：

  - `CONTINUE_BLIND` → `RetryRequested(feedback_state=FEEDBACK_EXHAUSTED)`
  - `POLICY_STOP` → `POLICY_STOP(FEEDBACK_EXHAUSTED)`

- `CONTINUE_BLIND` 不得重用舊 feedback ref。
- progress measure 可以讀系統內部保存的 verdict vector，但該 vector 不得因此重新洩漏給 executor。
- 固定負控新增或擴充一格：

  - `feedback-accepted-without-ref`  
    → `feedback_accepted_requires_ref`

### 是否需要第三支

v1 不加第三支。

「降頻續跑」不是第三種終局語意，而是帶參數的新排程政策，至少還需要定義：

- 降頻單位
- 觸發時點
- 剩餘 attempt 如何重算
- 是否建立 superseding Pursuit
- 對 deadline 與 budget reservation 的影響

現在塞入 enum 只會得到一個沒有完整狀態機語意的名字。未來若有量測證明二元政策造成不必要停止或浪費，再以 namespaced policy 擴充；目前 `{CONTINUE_BLIND, POLICY_STOP}` 已封閉所有必要 v1 行為。

## 本輪票面

| 決議 | 裁決 |
|---|---|
| R7-01 | REJECT `WEAKENS_GUARANTEE` |
| R7-02 | APPROVE |
