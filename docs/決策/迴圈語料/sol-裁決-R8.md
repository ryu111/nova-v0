codex
我會重跑三個變體中的 AB，並只檢查一個語意問題：R8-01 的兩個 policy identity 負控是否存在兩個「都能通過 admission」的正控主體。若第二個只能靠非法 enum 捏出來，那不是在測 identity。
exec
/bin/zsh -lc "UV_CACHE_DIR=/private/tmp/nova-uv-cache uv run python /private/tmp/fable-R8-mock/AB/docs/計畫複驗.py /private/tmp/fable-R8-mock/AB/docs/計畫 && rg -n -C 4 'VERBATIM_SEGMENTS_V1|same-family-different-assembly-policy|assembly_policy_is_identity|effective_digest_covers_assembly_policy|FeedbackUnavailable|blind_retry_carries_no_verdict_detail' /private/tmp/fable-R8-mock/AB/docs/計畫/08-目標追求生命週期.md" in /Users/sbu/nova
 succeeded in 0ms:
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
57-    ├── identity不可偷換.claim.json            — identity-changing resume direct red。
58-    └── 獨立證據面.claim.json                 — parallel scopes do not cross-read。
59-規格/提示/
60-├── PromptFamily.schema.json                  — 有序段集合與 canonical bytes 的封閉 schema。
61:├── PromptAssemblyPolicy.schema.json          — 組裝政策身分；v1 唯一 VERBATIM_SEGMENTS_V1。
62-└── 保證/
63-    └── 提示家族內容定址.claim.json           — 順序入身分、漂移拒絕、政策入身分、禁冒充。
64-nova/領域/提示/
65-├── 家族.py                                   — canonical serialization 與 source_artifact_digest。
--
637-  canonical bytes＝依宣告順序串接 `(segment_kind, content_digest)` 的 canonical JSON；
638-  **它的 digest 名為 `source_artifact_digest`**——宣告內容與順序的身分，
639-  `prompt_family_ref` 的 digest 從此有 preimage。**順序是身分的一部分。**
640-- Produces: `PromptAssemblyPolicy`——封閉欄位：`semantic_id`、`revision`、
641:  `resolution_rule_kind`（封閉 enum，**v1 唯一成員 `VERBATIM_SEGMENTS_V1`**＝逐字使用
642-  family 段、不插值、不重排；未知 kind fail-closed，未來成員以動作②擴充並各自帶
643-  admission）。政策 canonical bytes＝欄位的 canonical JSON，digest 有 preimage——
644-  **不重演本 task 自己要修的「ref 無指涉物」洞**。
645-- Produces: 層級公式寫死——`source_artifact_digest`＝PromptFamily 宣告內容與順序的
--
685-`prose-family`：無 canonical bytes 與 digest 的散文 family，必須紅在
686-`family_requires_canonical_bytes`。
687-`unknown-segment-kind`：`segment_kind` 塞 enum 外新值，closed schema 必須拒，
688-紅在 `segment_kind_vocabulary_closed`。
689:`same-family-different-assembly-policy`：同一 family、兩個不同政策 digest，
690:判 `SAME_PURSUIT` 的比較器變體必須紅在 `assembly_policy_is_identity`。
691-`family-digest-used-as-effective-digest`：把 `source_artifact_digest` 直接代入
692-effective 比較（政策變了仍判同一）的變體，必須紅在
693:`effective_digest_covers_assembly_policy`。
694-防恆真格三條：兩個不同 `semantic_id`、同 canonical bytes、同政策 → `SAME_PURSUIT`
695-（Task 1 防恆真格接上真主體）；合法換段內容 → `NEW_PURSUIT_REQUIRED`；
696-同 family 同政策完整 resolve → `SAME_PURSUIT`。
697-
--
745-
746-**Interfaces:**
747-- Produces: **事件分家**（typed event union 的擁有者是 `公開契約.py`，本 task Modify 它）：
748-  `FeedbackAccepted(feedback_ref)`——**`feedback_ref` 永遠不可 nullable**，schema 層釘死；
749:  `FeedbackUnavailable(reason)`——closed reason enum，v1 成員
750:  `DISCLOSURE_BUDGET_EXHAUSTED`。耗盡時**先記 `FeedbackUnavailable`**，
751-  再依政策產生 `RetryRequested(feedback_state=FEEDBACK_EXHAUSTED)` 或
752-  `POLICY_STOP(FEEDBACK_EXHAUSTED)`。**「沒有回饋」是一等事件，不是 payload 裡的
753-  字串，更不是「回饋是空的」。**
754-- Produces: `AttemptPolicy.on_feedback_exhausted ∈ {CONTINUE_BLIND, POLICY_STOP}`，
--
768-`FeedbackAccepted(feedback_ref=verdict.feedback_ref)`——`feedback_ref` 缺席的行為
769-未定義。未定義的下場只有偽造空 packet（把「沒有」冒充「有但是空」，污染事件流）
770-或靜默盲燒兩種，都是靜默降級。事件分家讓缺席在事件流裡**看得見**，
771-重播與稽核不需要從 payload 字串反推。
772:- 查證：`grep -rn "on_feedback_exhausted\|FeedbackUnavailable" docs/計畫/` → 套用前 0；
773-  `grep -n "DISCLOSURE_BUDGET_EXHAUSTED" docs/計畫/06-判準評估與隔離回饋.md` → 497。
774-地基：官方層查不到「feedback 耗盡消費協定」（照實寫）。權威：arXiv:1506.02629——
775-揭露上限的存在理由（R3-05 既有地基），本條是它的消費端。
776-**事件分家形狀與成員集：無地基，這是 nova 的拆解決定**（「不得靜默降級」的落實）。
--
789-admission 的變體，必須紅在 `exhaustion_policy_required`。
790-`stop-policy-still-starts`：宣告 `POLICY_STOP` 而耗盡後仍 `StartExecution` 的變體，
791-必須紅在 `stop_policy_refuses_start`。
792-`vector-releaked-to-executor`：盲跑 retry 輸入夾帶 verdict vector 或 clause 細節的
793:變體，必須紅在 `blind_retry_carries_no_verdict_detail`。
794-`shadow-reason-name`：終態理由寫 enum 外名（如 `FEEDBACK_DEPLETED`），closed enum
795-必須拒，紅在 `terminal_reason_vocabulary_closed`。
796:防恆真格兩條：`CONTINUE_BLIND` 下耗盡後 `FeedbackUnavailable` 先入流、標記入 retry、
797-照常續跑且停滯窗照常計數到觸發（與 Task 8 的交點正控）；cap 未滿時 feedback 照常，
798-本政策不介入。
799-
800-- [ ] **Step 1: 寫六個負控與兩個防恆真格的 red tests**
801-
802-```python
803-def test_耗盡後不得偽造空回饋() -> None:
804-    軌跡 = 跑追求(判準回拒絕(無回饋=True), 政策(on_feedback_exhausted="CONTINUE_BLIND"))
805:    assert 軌跡.事件流.含("FeedbackUnavailable")
806-    assert not 軌跡.事件流.含偽造packet()
807-
808-def test_停止政策下耗盡不得再啟動() -> None:
809-    軌跡 = 跑追求(判準回拒絕(無回饋=True), 政策(on_feedback_exhausted="POLICY_STOP"))
--
813-- [ ] **Step 2: 跑紅測確認今天 feedback_ref 缺席行為未定義**
814-
815-Run: `uv run pytest -q 驗收/追求/測_回饋耗盡.py`
816-
817:Expected: 【推論】FAIL；event union 無 `FeedbackUnavailable`、`AttemptPolicy` 無政策欄、
818-choreography 無耗盡臂。不得是收集錯誤冒充紅測。
819-
820-- [ ] **Step 3: 寫事件分家、政策欄、分支與 reason enum**
821-

codex
## R8-01(fable) — REJECT `NOT_TESTABLE`

一句話：`PromptAssemblyPolicy` v1 只有一個合法語意，卻宣稱能用「兩個不同的合法政策 digest」證明 policy change 會切斷 Pursuit；目前不存在第二個能通過 admission 的測試主體，該負控只能拿非法 enum 或無效 ref 製造紅燈，測到的不是 identity。

我重跑 AB 鏡像：22 份計畫、769 個 Create、190 tasks、未遷移 131，I1–I11 全部成立。你的疑問成立：這格目前是不可達、近似恆真的保證。

另外，若 policy canonical bytes 包含 `semantic_id`／`revision`，還會反向破壞既有規則：兩份語意相同、只有 id/revision 不同的政策會得到不同 digest，錯判 `NEW_PURSUIT_REQUIRED`。

### 可重提的最小修改

二選一。

#### 選項 A：現在定義第二個真正合法的政策

至少兩個 production-admitted policy 必須產生不同 effective semantic prefix；例如兩種具有完整規格與正控的 framing policy。兩者都必須：

- 通過 schema與admission；
- 有可執行的解析語意；
- 對同一 PromptFamily 產生不同 effective digest；
- 各有固定負控；
- 不依賴非法 enum fixture。

如此才能保留：

- `same-family-different-assembly-policy`
- `effective_digest_covers_assembly_policy`

#### 選項 B：v1 保持單成員，但誠實降級 claim

這是我建議的最小方案：

- 保留 `prompt_assembly_policy_ref` 進 PursuitIdentity。
- 保留單成員 `VERBATIM_SEGMENTS_V1` 與未知政策 fail-closed。
- 刪除目前無合法第二主體的兩格 policy-change 負控。
- 改驗：

  - `assembly-policy-ref-required`  
    → `assembly_policy_must_resolve`
  - `assembly-policy-digest-mismatch`  
    → `assembly_policy_digest_content_bound`
  - `assembly-policy-unknown-kind`  
    → `assembly_policy_vocabulary_closed`

- 明寫：在第二個 policy kind 被准入前，不宣稱「不同合法政策必切 Pursuit」已經接受過正負控驗證。
- 把以下規則設成未來 enum admission 的硬前置：

  > 新增第二個 `resolution_rule_kind` 的同一變更，必須同時新增 `assembly_policy_is_identity` 與 `effective_digest_covers_assembly_policy` 的第一組可達正負控；缺少就不得擴 enum。

- `source_artifact_digest` 只涵蓋有效語意欄位，不涵蓋 `semantic_id`／`revision`；完整三元組另留作稽核。

這樣不會假裝 v1 已驗到不存在的比較，同時也不留下 floating policy。

---

## R8-02(fable) — APPROVE

一句話：本版已把「沒有回饋」提升為獨立事件、禁止 nullable `FeedbackAccepted`、禁止 verdict vector 回流 executor，完整落實上一輪的寫入條件。

寫入時保留以下事件順序不變：

```text
FeedbackUnavailable(DISCLOSURE_BUDGET_EXHAUSTED)
→ RetryRequested(FEEDBACK_EXHAUSTED)
```

或：

```text
FeedbackUnavailable(DISCLOSURE_BUDGET_EXHAUSTED)
→ POLICY_STOP(FEEDBACK_EXHAUSTED)
```

兩個事件必須在同一次 state-owner transition 中取得確定順序；不能先啟動下一個 Execution，再補記 `FeedbackUnavailable`。

`vector-releaked-to-executor` 是有效新增負控。它應檢查完整 outbound manifest，而不只檢查 `RetryRequested` 的直接欄位，避免 clause detail 經其他 context segment 繞回執行者。

## 單成員 enum 裁定

是，目前的 `same-family-different-assembly-policy` 沒有合法第二主體。

以下都不能證明它：

- 使用未知 enum：只證明 closed vocabulary。
- 任意偽造另一個 digest：只證明 digest mismatch。
- 改 `semantic_id`／`revision`：既有規則要求相同有效內容仍是同一 Pursuit，不能拿 metadata 差異冒充政策差異。
- 修改同一 enum 背後的程式碼：那是 implementation drift，應由 compiler/conformance digest 捕捉，不是第二種政策。

因此，在第二個合法政策出現前，要採上面的選項 B，不得保留一條不可達的 policy-change 負控。

## 本輪票面

| 決議 | 裁決 |
|---|---|
| R8-01 | REJECT `NOT_TESTABLE` |
| R8-02 | APPROVE |
tokens used
14,521
## R8-01(fable) — REJECT `NOT_TESTABLE`

一句話：`PromptAssemblyPolicy` v1 只有一個合法語意，卻宣稱能用「兩個不同的合法政策 digest」證明 policy change 會切斷 Pursuit；目前不存在第二個能通過 admission 的測試主體，該負控只能拿非法 enum 或無效 ref 製造紅燈，測到的不是 identity。

我重跑 AB 鏡像：22 份計畫、769 個 Create、190 tasks、未遷移 131，I1–I11 全部成立。你的疑問成立：這格目前是不可達、近似恆真的保證。

另外，若 policy canonical bytes 包含 `semantic_id`／`revision`，還會反向破壞既有規則：兩份語意相同、只有 id/revision 不同的政策會得到不同 digest，錯判 `NEW_PURSUIT_REQUIRED`。

### 可重提的最小修改

二選一。

#### 選項 A：現在定義第二個真正合法的政策

至少兩個 production-admitted policy 必須產生不同 effective semantic prefix；例如兩種具有完整規格與正控的 framing policy。兩者都必須：

- 通過 schema與admission；
- 有可執行的解析語意；
- 對同一 PromptFamily 產生不同 effective digest；
- 各有固定負控；
- 不依賴非法 enum fixture。

如此才能保留：

- `same-family-different-assembly-policy`
- `effective_digest_covers_assembly_policy`

#### 選項 B：v1 保持單成員，但誠實降級 claim

這是我建議的最小方案：

- 保留 `prompt_assembly_policy_ref` 進 PursuitIdentity。
- 保留單成員 `VERBATIM_SEGMENTS_V1` 與未知政策 fail-closed。
- 刪除目前無合法第二主體的兩格 policy-change 負控。
- 改驗：

  - `assembly-policy-ref-required`  
    → `assembly_policy_must_resolve`
  - `assembly-policy-digest-mismatch`  
    → `assembly_policy_digest_content_bound`
  - `assembly-policy-unknown-kind`  
    → `assembly_policy_vocabulary_closed`

- 明寫：在第二個 policy kind 被准入前，不宣稱「不同合法政策必切 Pursuit」已經接受過正負控驗證。
- 把以下規則設成未來 enum admission 的硬前置：

  > 新增第二個 `resolution_rule_kind` 的同一變更，必須同時新增 `assembly_policy_is_identity` 與 `effective_digest_covers_assembly_policy` 的第一組可達正負控；缺少就不得擴 enum。

- `source_artifact_digest` 只涵蓋有效語意欄位，不涵蓋 `semantic_id`／`revision`；完整三元組另留作稽核。

這樣不會假裝 v1 已驗到不存在的比較，同時也不留下 floating policy。

---

## R8-02(fable) — APPROVE

一句話：本版已把「沒有回饋」提升為獨立事件、禁止 nullable `FeedbackAccepted`、禁止 verdict vector 回流 executor，完整落實上一輪的寫入條件。

寫入時保留以下事件順序不變：

```text
FeedbackUnavailable(DISCLOSURE_BUDGET_EXHAUSTED)
→ RetryRequested(FEEDBACK_EXHAUSTED)
```

或：

```text
FeedbackUnavailable(DISCLOSURE_BUDGET_EXHAUSTED)
→ POLICY_STOP(FEEDBACK_EXHAUSTED)
```

兩個事件必須在同一次 state-owner transition 中取得確定順序；不能先啟動下一個 Execution，再補記 `FeedbackUnavailable`。

`vector-releaked-to-executor` 是有效新增負控。它應檢查完整 outbound manifest，而不只檢查 `RetryRequested` 的直接欄位，避免 clause detail 經其他 context segment 繞回執行者。

## 單成員 enum 裁定

是，目前的 `same-family-different-assembly-policy` 沒有合法第二主體。

以下都不能證明它：

- 使用未知 enum：只證明 closed vocabulary。
- 任意偽造另一個 digest：只證明 digest mismatch。
- 改 `semantic_id`／`revision`：既有規則要求相同有效內容仍是同一 Pursuit，不能拿 metadata 差異冒充政策差異。
- 修改同一 enum 背後的程式碼：那是 implementation drift，應由 compiler/conformance digest 捕捉，不是第二種政策。

因此，在第二個合法政策出現前，要採上面的選項 B，不得保留一條不可達的 policy-change 負控。

## 本輪票面

| 決議 | 裁決 |
|---|---|
| R8-01 | REJECT `NOT_TESTABLE` |
| R8-02 | APPROVE |
