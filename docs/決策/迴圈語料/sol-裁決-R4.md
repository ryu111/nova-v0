codex
我會用 `superpowers:receiving-code-review` 的核證方式處理：先驗三個「看似補齊、其實仍可能假綠」的語意點，再投票；不改檔。重點是 exact 的證明強度、claim-ref 的可信綁定，以及 receipt 的簽發／消費是否真的閉環。
exec
/bin/zsh -lc "sed -n '1,240p' /Users/sbu/.codex/plugins/cache/openai-curated-remote/superpowers/6.3.0/skills/receiving-code-review/SKILL.md && rg -n -C 5 'result_semantics_evidence|exactness_fixed_controls|wrong-claim-ref|AdmissionAuthorizationReceipt|receipt_nonce|Authority Step' /private/tmp/fable-R4-mock/docs/計畫/{01-可執行保證語言.md,01B-執行者能力契約與SDK探針.md,05-執行封套與重播器.md,09-持久工作協調與選拔.md}" in /Users/sbu/nova
 succeeded in 0ms:
---
name: receiving-code-review
description: Use when receiving code review feedback, before implementing suggestions, especially if feedback seems unclear or technically questionable - requires technical rigor and verification, not performative agreement or blind implementation
---

# Code Review Reception

## Overview

Code review requires technical evaluation, not emotional performance.

**Core principle:** Verify before implementing. Ask before assuming. Technical correctness over social comfort.

## The Response Pattern

```
WHEN receiving code review feedback:

1. READ: Complete feedback without reacting
2. UNDERSTAND: Restate requirement in own words (or ask)
3. VERIFY: Check against codebase reality
4. EVALUATE: Technically sound for THIS codebase?
5. RESPOND: Technical acknowledgment or reasoned pushback
6. IMPLEMENT: One item at a time, test each
```

## Forbidden Responses

**NEVER:**
- "You're absolutely right!" (explicit instruction-file violation)
- "Great point!" / "Excellent feedback!" (performative)
- "Let me implement that now" (before verification)

**INSTEAD:**
- Restate the technical requirement
- Ask clarifying questions
- Push back with technical reasoning if wrong
- Just start working (actions > words)

## Handling Unclear Feedback

```
IF any item is unclear:
  STOP - do not implement anything yet
  ASK for clarification on unclear items

WHY: Items may be related. Partial understanding = wrong implementation.
```

**Example:**
```
your human partner: "Fix 1-6"
You understand 1,2,3,6. Unclear on 4,5.

❌ WRONG: Implement 1,2,3,6 now, ask about 4,5 later
✅ RIGHT: "I understand items 1,2,3,6. Need clarification on 4 and 5 before proceeding."
```

## Source-Specific Handling

### From your human partner
- **Trusted** - implement after understanding
- **Still ask** if scope unclear
- **No performative agreement**
- **Skip to action** or technical acknowledgment

### From External Reviewers
```
BEFORE implementing:
  1. Check: Technically correct for THIS codebase?
  2. Check: Breaks existing functionality?
  3. Check: Reason for current implementation?
  4. Check: Works on all platforms/versions?
  5. Check: Does reviewer understand full context?

IF suggestion seems wrong:
  Push back with technical reasoning

IF can't easily verify:
  Say so: "I can't verify this without [X]. Should I [investigate/ask/proceed]?"

IF conflicts with your human partner's prior decisions:
  Stop and discuss with your human partner first
```

**your human partner's rule:** "External feedback - be skeptical, but check carefully"

## YAGNI Check for "Professional" Features

```
IF reviewer suggests "implementing properly":
  grep codebase for actual usage

  IF unused: "This endpoint isn't called. Remove it (YAGNI)?"
  IF used: Then implement properly
```

**your human partner's rule:** "You and reviewer both report to me. If we don't need this feature, don't add it."

## Implementation Order

```
FOR multi-item feedback:
  1. Clarify anything unclear FIRST
  2. Then implement in this order:
     - Blocking issues (breaks, security)
     - Simple fixes (typos, imports)
     - Complex fixes (refactoring, logic)
  3. Test each fix individually
  4. Verify no regressions
```

## When To Push Back

Push back when:
- Suggestion breaks existing functionality
- Reviewer lacks full context
- Violates YAGNI (unused feature)
- Technically incorrect for this stack
- Legacy/compatibility reasons exist
- Conflicts with your human partner's architectural decisions

**How to push back:**
- Use technical reasoning, not defensiveness
- Ask specific questions
- Reference working tests/code
- Involve your human partner if architectural

**If you're uncomfortable pushing back out loud:** Name that tension, then tell your partner about the issue you've seen. They'll appreciate your honesty.

## Acknowledging Correct Feedback

When feedback IS correct:
```
✅ "Fixed. [Brief description of what changed]"
✅ "Good catch - [specific issue]. Fixed in [location]."
✅ [Just fix it and show in the code]

❌ "You're absolutely right!"
❌ "Great point!"
❌ "Thanks for catching that!"
❌ "Thanks for [anything]"
❌ ANY gratitude expression
```

**Why no thanks:** Actions speak. Just fix it. The code itself shows you heard the feedback.

**If you catch yourself about to write "Thanks":** DELETE IT. State the fix instead.

## Gracefully Correcting Your Pushback

If you pushed back and were wrong:
```
✅ "You were right - I checked [X] and it does [Y]. Implementing now."
✅ "Verified this and you're correct. My initial understanding was wrong because [reason]. Fixing."

❌ Long apology
❌ Defending why you pushed back
❌ Over-explaining
```

State the correction factually and move on.

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Performative agreement | State requirement or just act |
| Blind implementation | Verify against codebase first |
| Batch without testing | One at a time, test each |
| Assuming reviewer is right | Check if breaks things |
| Avoiding pushback | Technical correctness > comfort |
| Partial implementation | Clarify all items first |
| Can't verify, proceed anyway | State limitation, ask for direction |

## Real Examples

**Performative Agreement (Bad):**
```
Reviewer: "Remove legacy code"
❌ "You're absolutely right! Let me remove that..."
```

**Technical Verification (Good):**
```
Reviewer: "Remove legacy code"
✅ "Checking... build target is 10.15+, this API needs 13+. Need legacy for backward compat. Current impl has wrong bundle ID - fix it or drop pre-13 support?"
```

**YAGNI (Good):**
```
Reviewer: "Implement proper metrics tracking with database, date filters, CSV export"
✅ "Grepped codebase - nothing calls this endpoint. Remove it (YAGNI)? Or is there usage I'm missing?"
```

**Unclear Item (Good):**
```
your human partner: "Fix items 1-6"
You understand 1,2,3,6. Unclear on 4,5.
✅ "Understand 1,2,3,6. Need clarification on 4 and 5 before implementing."
```

## GitHub Thread Replies

When replying to inline review comments on GitHub, reply in the comment thread (`gh api repos/{owner}/{repo}/pulls/{pr}/comments/{id}/replies`), not as a top-level PR comment.
/private/tmp/fable-R4-mock/docs/計畫/09-持久工作協調與選拔.md-266-- Produces: `rank_candidates(schema, verdicts, cutoff_seq) -> SelectionRecord`。
/private/tmp/fable-R4-mock/docs/計畫/09-持久工作協調與選拔.md-267-- Produces: cutoff reasons `DEADLINE|ALL_CHILDREN_TERMINAL|PERMANENT_RESOURCE_EXHAUSTION`。
/private/tmp/fable-R4-mock/docs/計畫/09-持久工作協調與選拔.md-268-- Produces: 每維分數必附 `ScoreEvidence`，封閉二選一——`EXACT_OBSERVATION`＝
/private/tmp/fable-R4-mock/docs/計畫/09-持久工作協調與選拔.md-269-  {`verifier_primitive_id`, `primitive_revision`, `evidence_digest`}，其中原語必須在已准入目錄
/private/tmp/fable-R4-mock/docs/計畫/09-持久工作協調與選拔.md-270-  （01 Task 15）、`result_semantics = EXACT_ARTIFACT_FUNCTION` 且該語意由
/private/tmp/fable-R4-mock/docs/計畫/09-持久工作協調與選拔.md:271:  `result_semantics_evidence` 與三條指定 mutation 背書——不是原語自我宣告；`ESTIMATED`＝
/private/tmp/fable-R4-mock/docs/計畫/09-持久工作協調與選拔.md-272-  {`estimator`, `sampling_unit`, `interval_procedure`, `confidence_level`, `sample_size`,
/private/tmp/fable-R4-mock/docs/計畫/09-持久工作協調與選拔.md-273-  `analysis_digest`, `interval`}。deterministic 但 `result_semantics = ESTIMATOR` 的原語
/private/tmp/fable-R4-mock/docs/計畫/09-持久工作協調與選拔.md-274-  仍必須走 `ESTIMATED`——可重現不等於無抽樣不確定度。
/private/tmp/fable-R4-mock/docs/計畫/09-持久工作協調與選拔.md-275-- Produces: 每個分數綁 `evaluator_revision` 與 `candidate_digest`，不匹配 → `REJECT_CANDIDATE`；
/private/tmp/fable-R4-mock/docs/計畫/09-持久工作協調與選拔.md-276-  `score_source ∈ {VERIFIER_MEASURED, EXTERNAL_ATTESTED}`，裸數字與 `EXECUTOR_SELF_REPORT` 拒絕。
--
/private/tmp/fable-R4-mock/docs/計畫/01B-執行者能力契約與SDK探針.md-209-`determinism_requires_mechanistic_evidence`。`nth-plus-one-differs`——`假能力後端.py`
/private/tmp/fable-R4-mock/docs/計畫/01B-執行者能力契約與SDK探針.md-210-增一個前 N 次輸出逐 byte 相同、第 N+1 次改變的變體，其 evidence 記為 repeatability，
/private/tmp/fable-R4-mock/docs/計畫/01B-執行者能力契約與SDK探針.md-211-faulty 檢查器據此讓要求 determinism 的綁定通過，必須紅在 `repeatability_is_not_determinism`。
/private/tmp/fable-R4-mock/docs/計畫/01B-執行者能力契約與SDK探針.md-212-`forged-mechanistic-ref`——mechanism 填 `PURE_REPLAYER` 但 claim_ref 缺 revision／digest
/private/tmp/fable-R4-mock/docs/計畫/01B-執行者能力契約與SDK探針.md-213-或指向不可驗來源的 evidence，必須紅在 `mechanistic_ref_must_resolve`。
/private/tmp/fable-R4-mock/docs/計畫/01B-執行者能力契約與SDK探針.md:214:`wrong-claim-ref`——claim_ref 指到 `execution.backend.replayer-contract-parity`
/private/tmp/fable-R4-mock/docs/計畫/01B-執行者能力契約與SDK探針.md-215-（一條負控只殺未知 event kind、沒有決定性負控的 claim）的 evidence，必須紅在
/private/tmp/fable-R4-mock/docs/計畫/01B-執行者能力契約與SDK探針.md-216-`mechanistic_ref_targets_determinism_claim`——引用 claim 時要往下看它的負控殺的是什麼。
/private/tmp/fable-R4-mock/docs/計畫/01B-執行者能力契約與SDK探針.md-217-`contract-claim-cannot-bind-mechanical`——持 `CONTRACTUAL_OUTPUT_DETERMINISM_CLAIMED`
/private/tmp/fable-R4-mock/docs/計畫/01B-執行者能力契約與SDK探針.md-218-（含合法 contract ref 與 suite pass record）的後端綁定要求 `OUTPUT_DETERMINISM`
/private/tmp/fable-R4-mock/docs/計畫/01B-執行者能力契約與SDK探針.md-219-的 claim，必須紅在 `contract_claim_is_not_mechanism`；fixture 內附 suite 外輸出改變的
--
/private/tmp/fable-R4-mock/docs/計畫/01-可執行保證語言.md-88-規格/驗收/已准入保證.manifest.json             — 受保護 artifact 的檔案集合與 digest。
/private/tmp/fable-R4-mock/docs/計畫/01-可執行保證語言.md-89-規格/工程/保證/已准入保證不可原地改弱.claim.json — 改弱已准入答案必須被擋。
/private/tmp/fable-R4-mock/docs/計畫/01-可執行保證語言.md-90-架構/檢查已准入保證.py                         — 集合與 digest 雙向比對；不叫 baseline。
/private/tmp/fable-R4-mock/docs/計畫/01-可執行保證語言.md-91-架構/test_已准入保證.py                        — 改弱、刪整份、改 manifest 三格負控。
/private/tmp/fable-R4-mock/docs/計畫/01-可執行保證語言.md-92-規格/工程/AdmissionTrustRoot.schema.json      — 准入信任根的封閉 schema（外部事實的鏡像）。
/private/tmp/fable-R4-mock/docs/計畫/01-可執行保證語言.md:93:規格/工程/AdmissionAuthorizationReceipt.schema.json — live、單次、帶 nonce 的授權收據。
/private/tmp/fable-R4-mock/docs/計畫/01-可執行保證語言.md-94-規格/工程/准入信任根.admitted.json            — issuer/repo/workflow/extraction rule 鏡像。
/private/tmp/fable-R4-mock/docs/計畫/01-可執行保證語言.md-95-規格/工程/創世准入證據.json                    — 一次性創世儀式的 content-addressed 證據。
/private/tmp/fable-R4-mock/docs/計畫/01-可執行保證語言.md-96-規格/工程/保證/准入須有信任根.claim.json      — 無收據的新增 admission 一律 typed 拒絕。
/private/tmp/fable-R4-mock/docs/計畫/01-可執行保證語言.md-97-架構/檢查准入信任根.py                         — 收據簽章/綁定/nonce 唯一＋replay 驗證器。
/private/tmp/fable-R4-mock/docs/計畫/01-可執行保證語言.md-98-架構/test_准入信任根.py                        — 無收據、nonce 重用、綁錯、外鑰、創世兩格。
--
/private/tmp/fable-R4-mock/docs/計畫/01-可執行保證語言.md-1027-  失敗 code 封閉為 `UNADMITTED_PRIMITIVE_CATALOG`、`CATALOG_DIGEST_MISMATCH`、
/private/tmp/fable-R4-mock/docs/計畫/01-可執行保證語言.md-1028-  `PRIMITIVE_MISSING_CONTROLS`、`PRIMITIVE_RESULT_SEMANTICS_REJECTED`。
/private/tmp/fable-R4-mock/docs/計畫/01-可執行保證語言.md-1029-- Forbids: production 路徑接受呼叫端自備的 `原語目錄` 物件。編譯入口只收 `catalog_ref`。
/private/tmp/fable-R4-mock/docs/計畫/01-可執行保證語言.md-1030-- Forbids: 同一個 `catalog_id` 對到兩份不同 digest 的內容。
/private/tmp/fable-R4-mock/docs/計畫/01-可執行保證語言.md-1031-- Produces: 目錄的每個原語帶封閉的 `result_semantics ∈ {EXACT_ARTIFACT_FUNCTION, ESTIMATOR}`。
/private/tmp/fable-R4-mock/docs/計畫/01-可執行保證語言.md:1032:  `EXACT_ARTIFACT_FUNCTION` 不是自我宣告——必須同時附 `result_semantics_evidence`，封閉欄位：
/private/tmp/fable-R4-mock/docs/計畫/01-可執行保證語言.md-1033-  `input_domain_manifest_digest`（pinned 輸入域 manifest）、`primitive_implementation_digest`、
/private/tmp/fable-R4-mock/docs/計畫/01-可執行保證語言.md-1034-  `coverage_evidence_ref`（對 manifest 全體成員的完整執行觀測）、`missing_input_observation`
/private/tmp/fable-R4-mock/docs/計畫/01-可執行保證語言.md:1035:  （遇缺失值的 typed 觀測，不得靜默略過）、`exactness_fixed_controls`（見下）。
/private/tmp/fable-R4-mock/docs/計畫/01-可執行保證語言.md-1036-  缺任一欄即 `PRIMITIVE_RESULT_SEMANTICS_REJECTED`，只能標 `ESTIMATOR`。
/private/tmp/fable-R4-mock/docs/計畫/01-可執行保證語言.md-1037-- Produces: 每個宣稱 exact 的原語，其 `fixed_controls` **必含三條指定 mutation**——
/private/tmp/fable-R4-mock/docs/計畫/01-可執行保證語言.md-1038-  ①漏掉一個輸入成員；②只跑子樣本；③遇到 missing value 後靜默略過——三者各自
/private/tmp/fable-R4-mock/docs/計畫/01-可執行保證語言.md-1039-  `must_fail_exactly` 於該原語自身的 admission predicate，跑法走 Task 14 的
/private/tmp/fable-R4-mock/docs/計畫/01-可執行保證語言.md-1040-  `工具/跑指定突變.py` 既有軌道。checker 驗「三條存在且宣告完整」，驗收跑「三條真的殺紅」。
--
/private/tmp/fable-R4-mock/docs/計畫/01-可執行保證語言.md-1064-`same-id-different-digest`：同一個 `catalog_id` 換掉內容，必須紅在 `catalog_digest_is_content_bound`。
/private/tmp/fable-R4-mock/docs/計畫/01-可執行保證語言.md-1065-`primitive-without-controls`：准入清單裡的原語沒有列出自己的固定負控，必須紅在
/private/tmp/fable-R4-mock/docs/計畫/01-可執行保證語言.md-1066-`primitive_admission_requires_named_controls`。
/private/tmp/fable-R4-mock/docs/計畫/01-可執行保證語言.md-1067-`deterministic-estimator-poses-as-exact`：一個 deterministic、但對樣本算 sample mean 的原語
/private/tmp/fable-R4-mock/docs/計畫/01-可執行保證語言.md-1068-標 `EXACT_ARTIFACT_FUNCTION` 送准入，必須紅在 `exact_requires_full_population_function`。
/private/tmp/fable-R4-mock/docs/計畫/01-可執行保證語言.md:1069:`exact-without-evidence`：標 exact 但缺 `result_semantics_evidence` 任一欄，必須紅在
/private/tmp/fable-R4-mock/docs/計畫/01-可執行保證語言.md-1070-`exact_requires_semantics_evidence`。
/private/tmp/fable-R4-mock/docs/計畫/01-可執行保證語言.md-1071-`exact-missing-designated-mutations`：evidence 齊全但 `fixed_controls` 缺三條指定 mutation
/private/tmp/fable-R4-mock/docs/計畫/01-可執行保證語言.md-1072-任一，必須紅在 `exact_requires_designated_mutations`。
/private/tmp/fable-R4-mock/docs/計畫/01-可執行保證語言.md-1073-防恆真格三條：已准入目錄下的合法 claim 仍必須編綠；引用目錄外原語仍必須紅在
/private/tmp/fable-R4-mock/docs/計畫/01-可執行保證語言.md-1074-`UNKNOWN_PRIMITIVE` 而不是被新的 code 蓋掉；一個帶齊 evidence 與三條指定 mutation 的
--
/private/tmp/fable-R4-mock/docs/計畫/01-可執行保證語言.md-1103-
/private/tmp/fable-R4-mock/docs/計畫/01-可執行保證語言.md-1104-- [ ] **Step 3: 寫 schema、bootstrap 清單與解析器**
/private/tmp/fable-R4-mock/docs/計畫/01-可執行保證語言.md-1105-
/private/tmp/fable-R4-mock/docs/計畫/01-可執行保證語言.md-1106-【推論】`原語目錄.admitted.json` 是資料：每個原語列 `primitive_id`、`revision`、
/private/tmp/fable-R4-mock/docs/計畫/01-可執行保證語言.md-1107-`implementation_digest`、`observation_type`、`effect_kind`、`required_isolation`、
/private/tmp/fable-R4-mock/docs/計畫/01-可執行保證語言.md:1108:`fixed_controls`、`result_semantics`、（exact 時必附）`result_semantics_evidence`。
/private/tmp/fable-R4-mock/docs/計畫/01-可執行保證語言.md-1109-權威層只解析不讀檔；`工具/跑驗收.py` 負責把 bytes 交進去。
/private/tmp/fable-R4-mock/docs/計畫/01-可執行保證語言.md-1110-
/private/tmp/fable-R4-mock/docs/計畫/01-可執行保證語言.md-1111-- [ ] **Step 4: 把編譯入口改成只收 catalog_ref**
/private/tmp/fable-R4-mock/docs/計畫/01-可執行保證語言.md-1112-
/private/tmp/fable-R4-mock/docs/計畫/01-可執行保證語言.md-1113-【推論】`compile_claim` 保留 catalog 參數以維持 `plan_digest` 綁四個輸入，
--
/private/tmp/fable-R4-mock/docs/計畫/01-可執行保證語言.md-1228-
/private/tmp/fable-R4-mock/docs/計畫/01-可執行保證語言.md-1229-### Task 17: 新增准入要憑一次性的授權收據
/private/tmp/fable-R4-mock/docs/計畫/01-可執行保證語言.md-1230-
/private/tmp/fable-R4-mock/docs/計畫/01-可執行保證語言.md-1231-**Files:**
/private/tmp/fable-R4-mock/docs/計畫/01-可執行保證語言.md-1232-- Create: `規格/工程/AdmissionTrustRoot.schema.json`
/private/tmp/fable-R4-mock/docs/計畫/01-可執行保證語言.md:1233:- Create: `規格/工程/AdmissionAuthorizationReceipt.schema.json`
/private/tmp/fable-R4-mock/docs/計畫/01-可執行保證語言.md-1234-- Create: `規格/工程/准入信任根.admitted.json`
/private/tmp/fable-R4-mock/docs/計畫/01-可執行保證語言.md-1235-- Create: `規格/工程/創世准入證據.json`
/private/tmp/fable-R4-mock/docs/計畫/01-可執行保證語言.md-1236-- Create: `規格/工程/保證/准入須有信任根.claim.json`
/private/tmp/fable-R4-mock/docs/計畫/01-可執行保證語言.md-1237-- Create: `架構/檢查准入信任根.py`
/private/tmp/fable-R4-mock/docs/計畫/01-可執行保證語言.md-1238-- Create: `架構/test_准入信任根.py`
--
/private/tmp/fable-R4-mock/docs/計畫/01-可執行保證語言.md-1242-- Produces: `AdmissionTrustRoot`——封閉欄位：trusted attestation issuer、repository/ref、
/private/tmp/fable-R4-mock/docs/計畫/01-可執行保證語言.md-1243-  workflow identity、actor identity extraction rule、trust-root revision/digest、
/private/tmp/fable-R4-mock/docs/計畫/01-可執行保證語言.md-1244-  expiry/revocation。**信任根的初始 public key 與外部 workflow identity 必須位於候選 PR
/private/tmp/fable-R4-mock/docs/計畫/01-可執行保證語言.md-1245-  不可改的信任域**；repo 內的 `准入信任根.admitted.json` 只是該外部事實的鏡像，
/private/tmp/fable-R4-mock/docs/計畫/01-可執行保證語言.md-1246-  不能自行成為自己的信任根。
/private/tmp/fable-R4-mock/docs/計畫/01-可執行保證語言.md:1247:- Produces: `AdmissionAuthorizationReceipt`——**live、single-use**。每次新增 admission
/private/tmp/fable-R4-mock/docs/計畫/01-可執行保證語言.md-1248-  必須恰取得一張、恰消費一次。封閉欄位：repository identity、exact PR/head SHA、
/private/tmp/fable-R4-mock/docs/計畫/01-可執行保證語言.md-1249-  proposed manifest digest、trust-root revision/digest、ruleset identity 及其版本或
/private/tmp/fable-R4-mock/docs/計畫/01-可執行保證語言.md-1250-  不可變摘要、required workflow repo/ref/digest、workflow run id、attested actor、
/private/tmp/fable-R4-mock/docs/計畫/01-可執行保證語言.md-1251-  issued_at、one-time nonce。nonce 在整份 manifest 歷史裡唯一；
/private/tmp/fable-R4-mock/docs/計畫/01-可執行保證語言.md-1252-  **不得用泛用 TTL probe 授權多筆 admission**。
--
/private/tmp/fable-R4-mock/docs/計畫/01-可執行保證語言.md-1256-  predicate 紅。無法 live 查證時新增 admission 維持拒絕——fail-closed 是設計不是事故；
/private/tmp/fable-R4-mock/docs/計畫/01-可執行保證語言.md-1257-  已存在的 entry 照常比對集合與 digest，不受影響。
/private/tmp/fable-R4-mock/docs/計畫/01-可執行保證語言.md-1258-- Produces: replay 測試只證明「**相同外部回應導出相同 verdict**」——錄下的 issuer 回應
/private/tmp/fable-R4-mock/docs/計畫/01-可執行保證語言.md-1259-  餵進驗證器必得同一判定。這個能力的名字是 observation/replay，
/private/tmp/fable-R4-mock/docs/計畫/01-可執行保證語言.md-1260-  **不得成為 live authorization**：repo settings 在觀測後一秒就可能改變。
/private/tmp/fable-R4-mock/docs/計畫/01-可執行保證語言.md:1261:- **Authority Step（控制端步驟，非實作者 commit 步）**：創世儀式——控制端建立
/private/tmp/fable-R4-mock/docs/計畫/01-可執行保證語言.md-1262-  trust-root revision；由**另一個** attested actor 核准第一份 manifest 並簽發第一張
/private/tmp/fable-R4-mock/docs/計畫/01-可執行保證語言.md-1263-  receipt；創世證據 content-addressed 存進 `創世准入證據.json`。實作者可以完成
/private/tmp/fable-R4-mock/docs/計畫/01-可執行保證語言.md-1264-  全部拒絕路徑與 replay 測試；**在控制端產生並驗證真實創世證據之前，本 task 不得
/private/tmp/fable-R4-mock/docs/計畫/01-可執行保證語言.md-1265-  宣告完成，期間一切新增 admission 必須 fail-closed。**
/private/tmp/fable-R4-mock/docs/計畫/01-可執行保證語言.md-1266-
--
/private/tmp/fable-R4-mock/docs/計畫/01-可執行保證語言.md-1278-
/private/tmp/fable-R4-mock/docs/計畫/01-可執行保證語言.md-1279-**ClaimSpec落點:** `engineering.admission.trust-root-required` → `規格/工程/保證/准入須有信任根.claim.json`（本 task Create）
/private/tmp/fable-R4-mock/docs/計畫/01-可執行保證語言.md-1280-
/private/tmp/fable-R4-mock/docs/計畫/01-可執行保證語言.md-1281-**固定負控:** 【推論】六格。`no-receipt-new-admission`：無 receipt 新增一條 manifest entry，
/private/tmp/fable-R4-mock/docs/計畫/01-可執行保證語言.md-1282-必須紅在 `admission_requires_authorization_receipt`（typed `ADMISSION_TRUST_ROOT_UNAVAILABLE`）。
/private/tmp/fable-R4-mock/docs/計畫/01-可執行保證語言.md:1283:`reused-nonce`：同一 nonce 的 receipt 授權第二筆 admission，必須紅在 `receipt_nonce_single_use`。
/private/tmp/fable-R4-mock/docs/計畫/01-可執行保證語言.md-1284-`receipt-binds-other-manifest`：receipt 的 manifest digest 或 head SHA 與本次不符，
/private/tmp/fable-R4-mock/docs/計畫/01-可執行保證語言.md-1285-必須紅在 `receipt_binds_exact_manifest`。
/private/tmp/fable-R4-mock/docs/計畫/01-可執行保證語言.md-1286-`foreign-key-receipt`：簽章 key 不在信任根的 receipt，必須紅在 `receipt_signer_in_trust_root`。
/private/tmp/fable-R4-mock/docs/計畫/01-可執行保證語言.md-1287-`genesis-self-approved`：創世證據裡建立者與核准者解析為同一 actor，必須紅在
/private/tmp/fable-R4-mock/docs/計畫/01-可執行保證語言.md-1288-`genesis_requires_distinct_actor`。
--
/private/tmp/fable-R4-mock/docs/計畫/01-可執行保證語言.md-1321-Run: `uv run pytest -q 架構/test_准入信任根.py && uv run python 工具/驗全部.py`
/private/tmp/fable-R4-mock/docs/計畫/01-可執行保證語言.md-1322-
/private/tmp/fable-R4-mock/docs/計畫/01-可執行保證語言.md-1323-Expected: 【推論】PASS；六個負控各紅在自己宣告的 predicate；創世儀式完成前，
/private/tmp/fable-R4-mock/docs/計畫/01-可執行保證語言.md-1324-唯一合法的新增路徑是創世 transition 本身。
/private/tmp/fable-R4-mock/docs/計畫/01-可執行保證語言.md-1325-
/private/tmp/fable-R4-mock/docs/計畫/01-可執行保證語言.md:1326:- [ ] **Step 5: Authority Step（控制端）——創世儀式與首張 receipt**
/private/tmp/fable-R4-mock/docs/計畫/01-可執行保證語言.md-1327-
/private/tmp/fable-R4-mock/docs/計畫/01-可執行保證語言.md-1328-【推論】控制端建立 trust-root revision 並公告外部信任域位置；另一 attested actor
/private/tmp/fable-R4-mock/docs/計畫/01-可執行保證語言.md-1329-核准第一份 manifest、簽發首張 receipt；創世證據 content-addressed 落
/private/tmp/fable-R4-mock/docs/計畫/01-可執行保證語言.md-1330-`規格/工程/創世准入證據.json`。此步完成前本 task 不得宣告完成。
/private/tmp/fable-R4-mock/docs/計畫/01-可執行保證語言.md-1331-
/private/tmp/fable-R4-mock/docs/計畫/01-可執行保證語言.md-1332-- [ ] **Step 6: Commit**
/private/tmp/fable-R4-mock/docs/計畫/01-可執行保證語言.md-1333-
/private/tmp/fable-R4-mock/docs/計畫/01-可執行保證語言.md-1334-```bash
/private/tmp/fable-R4-mock/docs/計畫/01-可執行保證語言.md:1335:git add 規格/工程/AdmissionTrustRoot.schema.json 規格/工程/AdmissionAuthorizationReceipt.schema.json 規格/工程/准入信任根.admitted.json 規格/工程/創世准入證據.json 規格/工程/保證/准入須有信任根.claim.json 架構/檢查准入信任根.py 架構/test_准入信任根.py 架構/檢查已准入保證.py
/private/tmp/fable-R4-mock/docs/計畫/01-可執行保證語言.md-1336-git commit -m "feat: 新增准入要憑一次性的授權收據"
/private/tmp/fable-R4-mock/docs/計畫/01-可執行保證語言.md-1337-```
/private/tmp/fable-R4-mock/docs/計畫/01-可執行保證語言.md-1338-
/private/tmp/fable-R4-mock/docs/計畫/01-可執行保證語言.md-1339----
/private/tmp/fable-R4-mock/docs/計畫/01-可執行保證語言.md-1340-

exec
/bin/zsh -lc "sed -n '1010,1095p' /private/tmp/fable-R4-mock/docs/計畫/01-可執行保證語言.md; sed -n '430,535p' /private/tmp/fable-R4-mock/docs/計畫/05-執行封套與重播器.md; sed -n '1238,1338p' /private/tmp/fable-R4-mock/docs/計畫/01-可執行保證語言.md" in /Users/sbu/nova
 succeeded in 0ms:
```

### Task 15: 只准用已准入的原語目錄

**Files:**
- Create: `規格/語言/PrimitiveCatalog.schema.json`
- Create: `規格/語言/原語目錄.admitted.json`
- Create: `規格/語言/保證/原語目錄須經准入.claim.json`
- Create: `nova/權威/判準/原語目錄准入.py`
- Create: `nova/權威/判準/test_原語目錄准入.py`
- Create: `驗收/保證規格語言/測_目錄准入.py`
- Modify: `nova/權威/判準/保證規格編譯.py`
- Modify: `工具/跑驗收.py`

**Interfaces:**
- Consumes: 已准入清單 bytes（由呼叫端讀進來——權威層不碰檔案系統）與一個 `catalog_ref`。
- Produces: `解析目錄(清單, catalog_ref) -> 原語目錄 | CatalogFailure`。
  失敗 code 封閉為 `UNADMITTED_PRIMITIVE_CATALOG`、`CATALOG_DIGEST_MISMATCH`、
  `PRIMITIVE_MISSING_CONTROLS`、`PRIMITIVE_RESULT_SEMANTICS_REJECTED`。
- Forbids: production 路徑接受呼叫端自備的 `原語目錄` 物件。編譯入口只收 `catalog_ref`。
- Forbids: 同一個 `catalog_id` 對到兩份不同 digest 的內容。
- Produces: 目錄的每個原語帶封閉的 `result_semantics ∈ {EXACT_ARTIFACT_FUNCTION, ESTIMATOR}`。
  `EXACT_ARTIFACT_FUNCTION` 不是自我宣告——必須同時附 `result_semantics_evidence`，封閉欄位：
  `input_domain_manifest_digest`（pinned 輸入域 manifest）、`primitive_implementation_digest`、
  `coverage_evidence_ref`（對 manifest 全體成員的完整執行觀測）、`missing_input_observation`
  （遇缺失值的 typed 觀測，不得靜默略過）、`exactness_fixed_controls`（見下）。
  缺任一欄即 `PRIMITIVE_RESULT_SEMANTICS_REJECTED`，只能標 `ESTIMATOR`。
- Produces: 每個宣稱 exact 的原語，其 `fixed_controls` **必含三條指定 mutation**——
  ①漏掉一個輸入成員；②只跑子樣本；③遇到 missing value 後靜默略過——三者各自
  `must_fail_exactly` 於該原語自身的 admission predicate，跑法走 Task 14 的
  `工具/跑指定突變.py` 既有軌道。checker 驗「三條存在且宣告完整」，驗收跑「三條真的殺紅」。
- Forbids: deterministic 原語自動取得 `EXACT_ARTIFACT_FUNCTION`——決定性只保證可重現，
  不保證無抽樣不確定度；一個 deterministic 原語也可以算 sample mean。
- **機械證明的邊界（誠實寫死）**：本 task 證明的是「evidence 齊全、對 pinned manifest 的
  coverage 觀測一致、三條指定 mutation 真的殺得紅」；manifest 之外的 completeness
  不由 catalog 憑空證明——exact 的語意錨定在 pinned input-domain manifest 上。

**為什麼**：`compile_claim(spec, catalog, binding, offer)` 的 catalog 目前由呼叫端自備。
`nova/權威/判準/test_保證規格語言.py::test_plan_digest_涵蓋四個輸入` 逐字證明換一份自備目錄
**仍然編得出 `TestPlan`**，只是 digest 不同。digest 不同只能證明「這次用了另一份目錄」，
不能證明「這份目錄有權存在」。所以 `UNKNOWN_PRIMITIVE` 擋的是「claim 用了目錄裡沒有的原語」，
**不擋「自備一份含新原語的目錄」**——而後者正是 pixel primitive 與 LLM-judge primitive
未來會走的路。今天的 fail-closed 是副作用不是設計。
地基：OWASP 對 agent tools 要求 backend enforcement 與 verified allowlist registry，
不讓呼叫端自報能用什麼；SLSA 要求 consumer 只接受指定的 signer-builder pair。
加蓋（nova 多出來的拒絕）：未准入目錄、同 id 不同 digest、新原語沒有自己的固定負控、
無證據或無指定 mutation 的 exact 宣告、deterministic estimator 冒充 exact。

**ClaimSpec:** 【推論】`claimspec.catalog.admitted-only` 從紅轉綠。

**ClaimSpec落點:** `claimspec.catalog.admitted-only` → `規格/語言/保證/原語目錄須經准入.claim.json`（本 task Create）

**固定負控:** 【推論】六格。`self-supplied-catalog`：呼叫端自備一份只多加了 `always.pass`
的目錄，必須紅在 `catalog_is_admitted`，不得靜默編出合法 `TestPlan`。
`same-id-different-digest`：同一個 `catalog_id` 換掉內容，必須紅在 `catalog_digest_is_content_bound`。
`primitive-without-controls`：准入清單裡的原語沒有列出自己的固定負控，必須紅在
`primitive_admission_requires_named_controls`。
`deterministic-estimator-poses-as-exact`：一個 deterministic、但對樣本算 sample mean 的原語
標 `EXACT_ARTIFACT_FUNCTION` 送准入，必須紅在 `exact_requires_full_population_function`。
`exact-without-evidence`：標 exact 但缺 `result_semantics_evidence` 任一欄，必須紅在
`exact_requires_semantics_evidence`。
`exact-missing-designated-mutations`：evidence 齊全但 `fixed_controls` 缺三條指定 mutation
任一，必須紅在 `exact_requires_designated_mutations`。
防恆真格三條：已准入目錄下的合法 claim 仍必須編綠；引用目錄外原語仍必須紅在
`UNKNOWN_PRIMITIVE` 而不是被新的 code 蓋掉；一個帶齊 evidence 與三條指定 mutation 的
合規 exact 原語通過准入，且對它施加三條 mutation 各自使其 admission 轉紅（故障注入自驗）。

- [ ] **Step 1: 寫六個負控與三個防恆真格的 red tests**

```python
def test_自備目錄不得編出計畫() -> None:
    自備 = 原語目錄("ref.v1", (原語("always.pass", 內部, "STRING"),))
    assert 解析目錄(清單, 自備.digest.hex).code == "UNADMITTED_PRIMITIVE_CATALOG"

def test_決定性估計原語不得標成精確() -> None:
    估 = 准入請求(樣本平均原語(), result_semantics="EXACT_ARTIFACT_FUNCTION")
    assert 解析目錄(含(估), 目錄ref()).code == "PRIMITIVE_RESULT_SEMANTICS_REJECTED"

def test_精確原語缺指定突變必須被拒() -> None:
    缺 = 精確原語(證據=齊(), fixed_controls=只有("漏掉一個輸入成員"))
    assert 解析目錄(含(缺), 目錄ref()).code == "PRIMITIVE_RESULT_SEMANTICS_REJECTED"

def test_合法目錄下的正常_claim_仍要編綠() -> None:
    assert isinstance(編(底(), catalog=已准入目錄()), TestPlan)
```

```

- [ ] **Step 4: 跑所有 terminal pairwise tests 與 ClaimSpec**

Run: `uv run pytest -q 驗收/執行封套/測_終態權威.py && uv run python 工具/跑驗收.py --claim execution.terminal.external-authority`

Expected: 【推論】PASS；named liar negative direct red。

- [ ] **Step 5: Commit**

```bash
git add nova/領域/執行/決策.py nova/應用/執行封套.py 驗收/執行封套/測_終態權威.py 規格/執行/保證/執行者不得裁定終態.claim.json
git commit -m "feat: 執行終態的裁定權留在後端之外"
```

---

### Task 7: 證明重播、重送與 crash recovery 確定性

**Files:**
- Modify: `nova/應用/執行封套.py`
- Modify: `nova/介接/執行者後端/重播器/執行.py`
- Create: `驗收/執行封套/測_重播契約.py`
- Create: `驗收/執行封套/測_crash_recovery.py`
- Create: `規格/執行/保證/重播器輸出決定性.claim.json`
- Create: `規格/執行/保證/崩潰後恰一終態.claim.json`

**Interfaces:**
- Produces: `resume_execution(execution_id) -> AlreadyTerminal | ResumedExecution`。
- Persists: input/event/script digest and terminal event idempotency key。
- Produces: 重播器輸出決定性——同一 `ReplayScript` 任意次重播產生逐位相同的
  canonical event bytes、相同事件順序、相同 terminal bytes；時間正規化只讀 script 內
  宣告的 `virtual_elapsed_ms`，不讀環境時鐘。這是 `PURE_REPLAYER` 能力（01B）唯一
  合法的機制依據；`replayer-contract-parity` 只保證契約形狀，**不保證決定性**，
  不得被引用來鑄造決定性能力。

**ClaimSpec:** 【推論】`execution.recovery.single-terminal-after-crash` 與 `execution.backend.replayer-output-deterministic` 從紅轉綠。

**ClaimSpec落點:** `execution.recovery.single-terminal-after-crash` → `規格/執行/保證/崩潰後恰一終態.claim.json`（本 task Create）；`execution.backend.replayer-output-deterministic` → `規格/執行/保證/重播器輸出決定性.claim.json`（本 task Create）

**固定負控:** 【推論】在 backend exit 與 terminal commit 之間 SIGKILL state owner，重啟後重播相同 events；不得發布第二個不同 terminal，也不得重新計費。
重播決定性三格：`replay-reorders-events`——第二次重播交換兩個事件順序的變體，
必須紅在 `replay_order_stable`；`replay-rewrites-bytes`——第二次重播改寫任一事件
canonical bytes 的變體，必須紅在 `same_script_same_canonical_event_bytes`；
`replay-injects-ambient-time`——把環境時鐘讀值混進時間正規化的變體，
必須紅在 `replay_ignores_ambient_time`。
防恆真格：合規重播器同一 script 兩次重播 canonical evidence digest 逐位相同。

- [ ] **Step 1: 寫 crash point matrix 的 failing case**

```python
@pytest.mark.parametrize("crash_point", ["after_started", "after_backend_exit", "before_terminal_commit", "after_terminal_commit"])
def test_restart_has_one_terminal(crash_point: str) -> None:
    report = run_restart_case(crash_point)
    assert len(report.terminal_events) == 1
    assert report.settlement_count == 1
```

- [ ] **Step 2: 跑 matrix 確認至少 before-terminal 重複**

Run: `uv run pytest -q 驗收/執行封套/測_crash_recovery.py`

Expected: 【推論】FAIL with duplicate/missing terminal before idempotent resume。

- [ ] **Step 3: 以 state owner idempotency key 寫 resume 決策**

```python
terminal_key = IdempotencyKey(f"execution:{execution_id}:terminal")
state_owner.append_once(terminal_key, terminal_event)
```

- [ ] **Step 4: 跑 matrix、replayer determinism 與 claim**

Run: `uv run pytest -q 驗收/執行封套/測_重播契約.py 驗收/執行封套/測_crash_recovery.py -n 2 && uv run python 工具/跑驗收.py --claim execution.recovery.single-terminal-after-crash && uv run python 工具/跑驗收.py --claim execution.backend.replayer-output-deterministic`

Expected: 【推論】PASS；每個 execution 恰一 terminal；決定性三格 mutant 各紅在自己宣告的 predicate，兩次 replay canonical evidence digest 逐位相同。

- [ ] **Step 5: Commit**

```bash
git add nova/應用/執行封套.py nova/介接/執行者後端/重播器/執行.py 驗收/執行封套 規格/執行/保證/重播器輸出決定性.claim.json 規格/執行/保證/崩潰後恰一終態.claim.json
git commit -m "feat: 冪等地恢復執行，重播決定性有自己的負控"
```

---

### Task 8: 消費能力契約並攔截工具、輸出、代理與效果路徑

**Files:**
- Modify: `規格/執行/ExecutionRequest.schema.json`
- Modify: `規格/執行/BackendEvent.schema.json`
- Modify: `nova/領域/執行/端口.py`
- Modify: `nova/領域/執行/模型.py`
- Modify: `nova/介接/執行者後端/共用/manifest.py`
- Modify: `nova/介接/執行者後端/共用/契約套件.py`
- Modify: `nova/介接/執行者後端/重播器/執行.py`
- Create: `驗收/執行封套/測_能力與工具閘.py`
- Create: `規格/執行/保證/能力契約不可降級.claim.json`
- Create: `規格/執行/保證/效果工具只產生意圖.claim.json`

**Interfaces:**
- Consumes: plan 01B 的三種 policy refs、closed capabilities與scoped `UsageEvidence`。
- Emits: `TOOL_DENIED|OUTPUT_SCHEMA_VIOLATION|UNSUPPORTED_CAPABILITY`。
- Routes: `EFFECT_INTENT_REQUIRED` through an injected `EffectIntentPort`; concrete owner/relay由後續 plan 11 注入，本 Task 不依賴它。

**ClaimSpec:** 【推論】`execution.capability.required-no-silent-fallback` 與 `execution.tool.effect-intent-only` 從紅轉綠。
- Create: `架構/test_准入信任根.py`
- Modify: `架構/檢查已准入保證.py`

**Interfaces:**
- Produces: `AdmissionTrustRoot`——封閉欄位：trusted attestation issuer、repository/ref、
  workflow identity、actor identity extraction rule、trust-root revision/digest、
  expiry/revocation。**信任根的初始 public key 與外部 workflow identity 必須位於候選 PR
  不可改的信任域**；repo 內的 `准入信任根.admitted.json` 只是該外部事實的鏡像，
  不能自行成為自己的信任根。
- Produces: `AdmissionAuthorizationReceipt`——**live、single-use**。每次新增 admission
  必須恰取得一張、恰消費一次。封閉欄位：repository identity、exact PR/head SHA、
  proposed manifest digest、trust-root revision/digest、ruleset identity 及其版本或
  不可變摘要、required workflow repo/ref/digest、workflow run id、attested actor、
  issued_at、one-time nonce。nonce 在整份 manifest 歷史裡唯一；
  **不得用泛用 TTL probe 授權多筆 admission**。
- Produces: `檢查已准入保證.py` 對**新增** manifest entry 要求一張綁定本次
  （manifest digest＋head SHA）的有效 receipt；缺席、簽章 key 不在信任根、nonce 重複、
  綁到別的 manifest——一律 typed 拒絕 `ADMISSION_TRUST_ROOT_UNAVAILABLE` 或對應
  predicate 紅。無法 live 查證時新增 admission 維持拒絕——fail-closed 是設計不是事故；
  已存在的 entry 照常比對集合與 digest，不受影響。
- Produces: replay 測試只證明「**相同外部回應導出相同 verdict**」——錄下的 issuer 回應
  餵進驗證器必得同一判定。這個能力的名字是 observation/replay，
  **不得成為 live authorization**：repo settings 在觀測後一秒就可能改變。
- **Authority Step（控制端步驟，非實作者 commit 步）**：創世儀式——控制端建立
  trust-root revision；由**另一個** attested actor 核准第一份 manifest 並簽發第一張
  receipt；創世證據 content-addressed 存進 `創世准入證據.json`。實作者可以完成
  全部拒絕路徑與 replay 測試；**在控制端產生並驗證真實創世證據之前，本 task 不得
  宣告完成，期間一切新增 admission 必須 fail-closed。**

**為什麼**：Task 16 的 manifest 擋得住「改弱已准入檔案」，但「誰有權新增 admission」
是空的。R3 版用帶 TTL 的 probe 錄播充當證明，被指出只能證明「某時曾觀測到設定正確」，
不能證明「這一次 admission 仍由候選不可寫的 workflow 執行」——把前者當後者，
信任根保證在 TTL 內靜默失效。本版改為每次 admission 取一張 live、單次、帶 nonce 的
receipt，由受保護 workflow 於該 head SHA 的 run 中簽發；錄播降級回它真正能證明的事。
地基：SLSA v1.0 Source Track——身分與連續性由平台 attestation 承載；NIST SSDF PO.4.2；
Clark–Wilson ER3（DOI 10.1109/SP.1987.10001）——身分是 SoD 的前提。
加蓋：無 receipt／nonce 重用／綁錯 manifest／外鑰簽章的新增 admission、創世自我核准、
創世重演——全部 typed 拒絕。

**ClaimSpec:** 【推論】`engineering.admission.trust-root-required` 從紅轉綠。

**ClaimSpec落點:** `engineering.admission.trust-root-required` → `規格/工程/保證/准入須有信任根.claim.json`（本 task Create）

**固定負控:** 【推論】六格。`no-receipt-new-admission`：無 receipt 新增一條 manifest entry，
必須紅在 `admission_requires_authorization_receipt`（typed `ADMISSION_TRUST_ROOT_UNAVAILABLE`）。
`reused-nonce`：同一 nonce 的 receipt 授權第二筆 admission，必須紅在 `receipt_nonce_single_use`。
`receipt-binds-other-manifest`：receipt 的 manifest digest 或 head SHA 與本次不符，
必須紅在 `receipt_binds_exact_manifest`。
`foreign-key-receipt`：簽章 key 不在信任根的 receipt，必須紅在 `receipt_signer_in_trust_root`。
`genesis-self-approved`：創世證據裡建立者與核准者解析為同一 actor，必須紅在
`genesis_requires_distinct_actor`。
`genesis-twice`：儀式已有證據後再送一次創世 transition，必須紅在 `genesis_occurs_at_most_once`。
防恆真格：創世完成後，帶合法 receipt 的合規 entry 放行；replay 測試對錄下的 issuer
回應得到同一 verdict；未觸碰 manifest 的一般 commit 六道閘全綠照過。

- [ ] **Step 1: 寫六個負控與防恆真格的 red tests**

```python
def test_無收據時新增准入必須被拒() -> None:
    結果 = 跑准入閘(工作樹(新增一條entry(), 收據=None))
    assert 結果.code == "ADMISSION_TRUST_ROOT_UNAVAILABLE"

def test_同一收據不得授權兩筆准入() -> None:
    收據 = 合法收據(nonce="甲")
    assert 跑准入閘(工作樹(兩條entry(), 收據=收據)).code == "RECEIPT_NONCE_REUSED"
```

- [ ] **Step 2: 跑紅測確認今天新增 admission 沒有任何授權要求**

Run: `uv run pytest -q 架構/test_准入信任根.py`

Expected: 【推論】FAIL；今天任何人在任何環境都能新增 manifest entry，
沒有 typed 拒絕。不得是 `ModuleNotFoundError` 之外什麼都沒紅。

- [ ] **Step 3: 寫 schema、checker 與 replay 驗證器**

【推論】`檢查准入信任根.py` 的機械面：receipt schema／簽章對信任根鏡像的驗證／
manifest digest 與 head SHA 綁定／nonce 全歷史唯一；replay 面：錄下的 issuer 回應 →
verdict 決定性。checker 不打網路——live 簽發發生在受保護 workflow 的 run 裡，
checker 只驗收據本身。

- [ ] **Step 4: 跑六個負控與防恆真格**

Run: `uv run pytest -q 架構/test_准入信任根.py && uv run python 工具/驗全部.py`

Expected: 【推論】PASS；六個負控各紅在自己宣告的 predicate；創世儀式完成前，
唯一合法的新增路徑是創世 transition 本身。

- [ ] **Step 5: Authority Step（控制端）——創世儀式與首張 receipt**

【推論】控制端建立 trust-root revision 並公告外部信任域位置；另一 attested actor
核准第一份 manifest、簽發首張 receipt；創世證據 content-addressed 落
`規格/工程/創世准入證據.json`。此步完成前本 task 不得宣告完成。

- [ ] **Step 6: Commit**

```bash
git add 規格/工程/AdmissionTrustRoot.schema.json 規格/工程/AdmissionAuthorizationReceipt.schema.json 規格/工程/准入信任根.admitted.json 規格/工程/創世准入證據.json 規格/工程/保證/准入須有信任根.claim.json 架構/檢查准入信任根.py 架構/test_准入信任根.py 架構/檢查已准入保證.py
git commit -m "feat: 新增准入要憑一次性的授權收據"
```


codex
## 裁決

### R4-01(fable) — APPROVE

一句話：`EXACT_ARTIFACT_FUNCTION` 現在誠實地表示「對 pinned manifest 與 pinned implementation 的完整、非抽樣函式結果」，不是「對現實世界的絕對真值」；在這個限縮語意下，coverage evidence 加三條指定 mutation 足以支撐名稱。

三條 mutation本身確實不能證明「實作沒有漏」。真正的正面證據是 `coverage_evidence_ref`；mutation 的作用是證明 coverage gate 不是擺設。兩者缺一不可。

寫入時必須明定：

- `coverage_evidence_ref` 指向的資料必須列出實際處理過的每個 manifest member identity/digest。
- checker 必須機械比較：

  ```text
  observed_member_set == pinned_manifest_member_set
  ```

  不能只驗 evidence 存在、數量相等或摘要格式正確。
- 重複成員、額外成員、缺少成員、member digest 不符，都必須紅。
- `missing_input_observation` 必須是由執行事件 fold 出來的 typed observation，不得由原語自填布林值。
- 三條 mutation 分別破壞上述集合相等、完整母體執行及 missing handling predicate；不能只靠 mutation 名稱白名單。
- Task 文字必須保留這條邊界：

  > `EXACT_ARTIFACT_FUNCTION` 不保證 manifest 完整代表現實，也不保證該函式是正確的品質定義；它只保證對已釘 artifact domain 沒有抽樣不確定度。

因此我不要求降名。若 `coverage_evidence_ref` 最後只被驗「存在」，那實作仍不合本次核准內容，必須退回。

---

### R4-02(fable) — APPROVE

一句話：新的 determinism claim 有三個直接針對決定性的固定負控，能力證據又綁 exact revision、digest 與 predicate ids，已補上先前「引用一條其實沒驗這件事的 claim」的洞。

把 `execution.recovery.single-terminal-after-crash` 的遷移債一起補進 Task 7 可以接受，理由不是援引先例，而是：

- 該 id 原本就由同一 Task 7 宣告；
- 新增落點行後，Task 7 必須完整列出它宣告的所有 claim；
- 補的是同一 task 既有保證的缺失 artifact，不是夾帶另一個子系統；
- task 仍符合檔數、claim 數與單 commit 上限。

`wrong-claim-ref` 有牙，但寫入時不能實作成單純的 claim-id 白名單。必須如下執法：

- `PURE_REPLAYER` 的 capability policy 明確宣告所需 predicate set：

  ```text
  replay_order_stable
  same_script_same_canonical_event_bytes
  replay_ignores_ambient_time
  ```

- resolver 從 ProtectedClaimClosure 解析 exact claim revision/digest。
- resolved claim 的已准入 predicate set 必須涵蓋上述集合。
- `claim_id` 只是語義定位，不能單獨取得資格。
- capability policy 本身必須是封閉、版本化、內容定址的資料，或由受保護程式碼與自己的 ClaimSpec 承載。

如此 `wrong-claim-ref` 不是在問「名字是不是白名單裡那個」，而是在問「這份已准入證據是否真的驗了能力要求的三個 predicate」。

---

### R4-03(fable) — REJECT `INVARIANT_BREAK`

一句話：receipt 綁 exact PR/head SHA，但 Authority Step 又把 receipt／創世證據寫進該 PR 後才 commit；寫入後 head SHA 必然改變，因此 receipt 不是綁錯 head，就是形成不可解的自我雜湊循環。

另有第二個競態：若 nonce 只靠 repo manifest history 檢查，兩個並行 PR 可以在彼此尚未合併時使用同一 nonce，各自通過；這不構成真正的 single-use。

可重提的最小修改：

1. Receipt 不得寫進它所授權的 Git tree。

   - PR head 先固定。
   - 受保護 workflow 對該 head SHA 與 proposed manifest digest 簽發 detached receipt。
   - receipt 存在候選不可寫的外部 attestation／artifact store。
   - required check 直接驗 detached receipt。
   - repo 內只能在後續留下 receipt digest 或外部 locator，不能讓被簽 head 包含自己的 receipt。

2. nonce 必須在外部權威處原子消費。

   合法選項二選一：

   - protected admission ledger 提供 compare-and-set：`UNUSED → CONSUMED(manifest_digest, head_sha)`；或
   - 強制 merge queue 序列化，並在真正 merge 前對最新 base 重驗 nonce 未使用。

   單純掃目前 branch 看歷史不足以防並行雙花。

3. 創世改成兩階段：

   - Authority Step A：在候選不可寫的外部信任域建立 trust root。
   - repo PR：只提交該外部根的 mirror/reference。
   - Authority Step B：外部 workflow 對固定 PR head 簽發 detached genesis receipt，由不同 actor 核准。
   - required check 綠後才能 merge；創世 receipt 的外部 digest再由後續稽核事件記錄。

4. ClaimSpec 固定負控再加兩格：

   - `receipt-embedded-changes-head`  
     → `authorization_receipt_must_be_detached`
   - `parallel-pr-nonce-double-spend`  
     → `receipt_nonce_consumed_atomically`

其餘設計——取消 TTL probe、每次 admission 一張收據、綁 manifest digest/head SHA、外部 signer、Authority Step、角色以 receipt actor 為準——可以保留。

## 本輪票面

| 決議 | 裁決 |
|---|---|
| R4-01 | APPROVE |
| R4-02 | APPROVE |
| R4-03 | REJECT `INVARIANT_BREAK` |

我本輪不另提新決議。R4-03 只差把 receipt 從「被授權的 commit 內容」移到外部 attestation，並補上 nonce 的原子消費；不需要重做其餘角色分離設計。
tokens used
29,648
## 裁決

### R4-01(fable) — APPROVE

一句話：`EXACT_ARTIFACT_FUNCTION` 現在誠實地表示「對 pinned manifest 與 pinned implementation 的完整、非抽樣函式結果」，不是「對現實世界的絕對真值」；在這個限縮語意下，coverage evidence 加三條指定 mutation 足以支撐名稱。

三條 mutation本身確實不能證明「實作沒有漏」。真正的正面證據是 `coverage_evidence_ref`；mutation 的作用是證明 coverage gate 不是擺設。兩者缺一不可。

寫入時必須明定：

- `coverage_evidence_ref` 指向的資料必須列出實際處理過的每個 manifest member identity/digest。
- checker 必須機械比較：

  ```text
  observed_member_set == pinned_manifest_member_set
  ```

  不能只驗 evidence 存在、數量相等或摘要格式正確。
- 重複成員、額外成員、缺少成員、member digest 不符，都必須紅。
- `missing_input_observation` 必須是由執行事件 fold 出來的 typed observation，不得由原語自填布林值。
- 三條 mutation 分別破壞上述集合相等、完整母體執行及 missing handling predicate；不能只靠 mutation 名稱白名單。
- Task 文字必須保留這條邊界：

  > `EXACT_ARTIFACT_FUNCTION` 不保證 manifest 完整代表現實，也不保證該函式是正確的品質定義；它只保證對已釘 artifact domain 沒有抽樣不確定度。

因此我不要求降名。若 `coverage_evidence_ref` 最後只被驗「存在」，那實作仍不合本次核准內容，必須退回。

---

### R4-02(fable) — APPROVE

一句話：新的 determinism claim 有三個直接針對決定性的固定負控，能力證據又綁 exact revision、digest 與 predicate ids，已補上先前「引用一條其實沒驗這件事的 claim」的洞。

把 `execution.recovery.single-terminal-after-crash` 的遷移債一起補進 Task 7 可以接受，理由不是援引先例，而是：

- 該 id 原本就由同一 Task 7 宣告；
- 新增落點行後，Task 7 必須完整列出它宣告的所有 claim；
- 補的是同一 task 既有保證的缺失 artifact，不是夾帶另一個子系統；
- task 仍符合檔數、claim 數與單 commit 上限。

`wrong-claim-ref` 有牙，但寫入時不能實作成單純的 claim-id 白名單。必須如下執法：

- `PURE_REPLAYER` 的 capability policy 明確宣告所需 predicate set：

  ```text
  replay_order_stable
  same_script_same_canonical_event_bytes
  replay_ignores_ambient_time
  ```

- resolver 從 ProtectedClaimClosure 解析 exact claim revision/digest。
- resolved claim 的已准入 predicate set 必須涵蓋上述集合。
- `claim_id` 只是語義定位，不能單獨取得資格。
- capability policy 本身必須是封閉、版本化、內容定址的資料，或由受保護程式碼與自己的 ClaimSpec 承載。

如此 `wrong-claim-ref` 不是在問「名字是不是白名單裡那個」，而是在問「這份已准入證據是否真的驗了能力要求的三個 predicate」。

---

### R4-03(fable) — REJECT `INVARIANT_BREAK`

一句話：receipt 綁 exact PR/head SHA，但 Authority Step 又把 receipt／創世證據寫進該 PR 後才 commit；寫入後 head SHA 必然改變，因此 receipt 不是綁錯 head，就是形成不可解的自我雜湊循環。

另有第二個競態：若 nonce 只靠 repo manifest history 檢查，兩個並行 PR 可以在彼此尚未合併時使用同一 nonce，各自通過；這不構成真正的 single-use。

可重提的最小修改：

1. Receipt 不得寫進它所授權的 Git tree。

   - PR head 先固定。
   - 受保護 workflow 對該 head SHA 與 proposed manifest digest 簽發 detached receipt。
   - receipt 存在候選不可寫的外部 attestation／artifact store。
   - required check 直接驗 detached receipt。
   - repo 內只能在後續留下 receipt digest 或外部 locator，不能讓被簽 head 包含自己的 receipt。

2. nonce 必須在外部權威處原子消費。

   合法選項二選一：

   - protected admission ledger 提供 compare-and-set：`UNUSED → CONSUMED(manifest_digest, head_sha)`；或
   - 強制 merge queue 序列化，並在真正 merge 前對最新 base 重驗 nonce 未使用。

   單純掃目前 branch 看歷史不足以防並行雙花。

3. 創世改成兩階段：

   - Authority Step A：在候選不可寫的外部信任域建立 trust root。
   - repo PR：只提交該外部根的 mirror/reference。
   - Authority Step B：外部 workflow 對固定 PR head 簽發 detached genesis receipt，由不同 actor 核准。
   - required check 綠後才能 merge；創世 receipt 的外部 digest再由後續稽核事件記錄。

4. ClaimSpec 固定負控再加兩格：

   - `receipt-embedded-changes-head`  
     → `authorization_receipt_must_be_detached`
   - `parallel-pr-nonce-double-spend`  
     → `receipt_nonce_consumed_atomically`

其餘設計——取消 TTL probe、每次 admission 一張收據、綁 manifest digest/head SHA、外部 signer、Authority Step、角色以 receipt actor 為準——可以保留。

## 本輪票面

| 決議 | 裁決 |
|---|---|
| R4-01 | APPROVE |
| R4-02 | APPROVE |
| R4-03 | REJECT `INVARIANT_BREAK` |

我本輪不另提新決議。R4-03 只差把 receipt 從「被授權的 commit 內容」移到外部 attestation，並補上 nonce 的原子消費；不需要重做其餘角色分離設計。
