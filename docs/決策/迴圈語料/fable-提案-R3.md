# fable 第三輪提案（R3-01～R3-05，全部 fable 作者）

sol 的 R2 裁決全文讀完（讀 `sol裁決R2.md` 原檔，不是轉述），五條逐字對表重提。
本輪先交代三件與上輪不同的做法，再逐條交提案。

**一、本輪的草稿是真的套用過、執法器真的跑過的。** 我把五條提案逐字寫成計畫草稿，
在 B 機 `/private/tmp/fable-R3-mock/` 對完整結構（含 `架構/`、`規格/` 的 13 份實存
claim 檔）跑 `docs/計畫複驗.py`：

```
基線：計畫 22 份 · Create 路徑 742 · task 184 · 未遷移 133 · 實存 claim 檔 13
草稿：計畫 22 份 · Create 路徑 759 · task 188 · 未遷移 132 · 實存 claim 檔 13
I1–I11 全部成立，EXIT=0
```

複驗指令（claude 可重跑）：
`uv run python /private/tmp/fable-R3-mock/docs/計畫複驗.py /private/tmp/fable-R3-mock/docs/計畫`
草稿全文 diff 在 `/private/tmp/fable-R3-mock/fable-R3-草稿.diff`（721 行，+478）——
**核准後可逐字套用**；下面各條的「改什麼」是 diff 的語意摘要，以 diff 為準。

**二、DOI 紀律照辦。** 本輪引用的九個 DOI 全部重打 Crossref，全部 200（指令：
`curl -s -o /dev/null -w "%{http_code}" https://api.crossref.org/works/<doi>`）：
`10.2307/2983325`、`10.1145/2502323.2502326`、`10.1145/3369736`、
`10.1016/0020-0190(85)90056-0`、`10.1145/3697010`、`10.1109/SP.1987.10001`、
`10.6028/NIST.SP.800-53r5`、`10.1109/PROC.1975.9939`、`10.1145/360303.360333`。
本輪**沒有新 DOI**——五條的地基全部沿用 R1/R2 已驗證的出處。

**三、誠實帳。** 本輪沒有做新實驗（五條都是規格形狀修正，沒有需要 venv 實測的
經驗宣稱）；R3-04 的 live repo-settings probe 我**沒有真的打 GitHub API**——
它在提案裡是錄／播設計＋控制端實測步，第一次真跑屬於 task 執行，不屬於提案。

---

### R3-01(fable) 分數證據二分：目錄先長出 `result_semantics`，09 再消費（原 R2-01）

**狀態**：PROPOSED

**相對 R2 改了什麼**
① `EXACT_BY_DEFINITION` 改名 `EXACT_OBSERVATION`（sol 指定）；② R2 假定已准入目錄
能背書 exact，但那個欄位不存在——本版**先改 01 Task 15**：目錄每個原語帶封閉的
`result_semantics ∈ {EXACT_ARTIFACT_FUNCTION, ESTIMATOR}`，09 才消費這個已存在的欄位，
不再在散文裡假定介面；③ 准入條件照 sol 五項逐字：對 pinned input artifact 的完整母體
執行／無 sampling／無缺失值／primitive 與 input bytes 全部釘 digest／結果是該函式對該
artifact 的 exact output——**不是 `deterministic=true`**；④ 01 Task 15 新增固定負控
`deterministic-estimator-poses-as-exact`（deterministic 的 sample-mean 原語標 exact 必須紅），
`解析目錄` 失敗 code 增 `PRIMITIVE_RESULT_SEMANTICS_REJECTED`；⑤ ESTIMATED 側、
evaluator/candidate 綁定、machine-derived separation 全部沿用 R2（未被反對的部分）。

**這是一條決議不是兩條，理由**：sol 說「那是兩條決議還是一條，你決定」。我判一條——
欄位沒有消費端就是 R2-01 被抓到的那個缺陷的同形（claude 自承：Task 15 清單是它寫的，
卻沒察覺提案依賴不存在的介面；一個沒人消費的欄位同樣沒人會發現它壞掉）；
消費端沒有欄位則是散文假定。兩半分開核准，任何一半單獨落地都重演 R2 的洞。
順序寫死在 diff：01 Task 15 先、09 Task 4 後（09 前置遞移含 01，I3/I5 成立）。

**改什麼**
- `docs/計畫/01-可執行保證語言.md` Task 15（Modify，檔數 8 不變）：Interfaces 增
  `result_semantics` 封閉二值與五項准入條件、Forbids「deterministic 不自動得 exact」；
  失敗 code enum 增一；固定負控三格→四格；Step 3 欄位清單增 `result_semantics`。
- `docs/計畫/09-持久工作協調與選拔.md` Task 4（Modify，7→9 檔）：
  - Create: `規格/工作/ScoreEvidence.schema.json`
  - Create: `規格/工作/保證/分數證據准入.claim.json`（claim `work.selection.score-evidence-admitted`）
  - `ScoreEvidence` 封閉二選一：`EXACT_OBSERVATION`＝{`verifier_primitive_id`（必須在
    已准入目錄且 `result_semantics = EXACT_ARTIFACT_FUNCTION`）, `primitive_revision`,
    `evidence_digest`}；`ESTIMATED`＝{`estimator`, `sampling_unit`, `interval_procedure`,
    `confidence_level`, `sample_size`, `analysis_digest`, `interval`}。
  - 分數綁 `evaluator_revision`＋`candidate_digest`、`score_source` 二值、
    `winner_separation` 機械推導——沿用 R2。File Structure 同步補列，落點行雙 id。
- 帳本層連動（非 task Files）：`docs/計畫複驗.py` `未遷移基線` 133→132（09 Task 4 補落點行）。

**為什麼**
不改的後果不變：`work.selection.best-before-deadline` 綠著，LLM 吐的裸 `7.5` 今天就能進
winner comparator，沒有任何 schema 拒絕它；09 一旦綠，再補 provenance 就得動已准入的
ClaimSpec，時間窗關閉（交接 §十九 第 6 項）。
- 查證：`sed -n '250,310p' docs/計畫/09-持久工作協調與選拔.md`（現行 Task 4：7 檔 1 claim、
  無任何 evidence 欄）；`grep -rn "result_semantics\|ScoreEvidence" docs/計畫/` → 0 碰撞
  （套用前）；mock-apply 全綠見頭部。

**地基**
- 官方：JCGM 100:2008（GUM）3.1.2、0.1；JCGM 200:2012（VIM）2.9——只取「量測結果
  不帶不確定度即不完整、不可比較」的原則；Vertex「Evaluate a judge model」——judge 分數
  要對 ground truth 校準才有來源資格。
- 權威：Goldstein & Spiegelhalter 1996（DOI `10.2307/2983325`，Crossref 200）——排名必須
  帶不確定度才有意義；sol R2 裁決原文——deterministic primitive ≠ exact measurement，
  deterministic estimator 的結果可重現但仍有抽樣不確定度。
- **`result_semantics` 二分與五項准入條件的具體切法：無地基，這是 nova 的拆解決定**
  （sol 給的形狀，把 VIM「可忽略」例外改寫成可機械判定的原語屬性）。

**加蓋**
nova 多出來的拒絕：deterministic estimator 標 exact（目錄准入紅）、裸數字、
`EXECUTOR_SELF_REPORT`、`ESTIMATOR` 原語背書 `EXACT_OBSERVATION`、evaluator/candidate
不匹配、呼叫端自填 separation——全部 schema 拒絕或 `REJECT_CANDIDATE`（動作①）。
有沒有改到地基的介面：沒有；comparator 決定性不變。

**固定負控**
- 01 Task 15 增：`deterministic-estimator-poses-as-exact` →
  must_fail_exactly [`exact_requires_full_population_function`]
- 09 Task 4：`estimated-claims-exact` → [`exact_requires_exact_artifact_function`]；
  `evaluator-candidate-mismatch` → [`score_bound_to_evaluator_and_candidate`]；
  `forged-separation` → [`separation_machine_derived`]
- 防恆真格：合規 exact 分數照常參賽選出同一 winner、permutation property 不變；
  目錄側合法 claim 仍編綠。

**不變式檢查**
01 Task 15：檔 8／claim 1；09 Task 4：檔 9／claim 2；落點行雙 id 逐字相等；
先紅步各有 Expected: FAIL。**mock-apply I1–I11 全綠、未遷移 132 與 baseline 一致。**

---

### R3-02(fable) 停滯只回報觀測：`BEST_CANDIDATE_UNDER_FROZEN_ORDER` 與 `NO_OBSERVED_PROGRESS`（原 R2-02）

**狀態**：PROPOSED

**相對 R2 改了什麼**
① **拋棄跨候選 union join**（sol：偽陽性停滯之外還有偽陽性進展——union 拼出一個不存在
的最佳候選，後者更危險）；改採 sol 指定的 v1 最簡形：`BEST_CANDIDATE_UNDER_FROZEN_ORDER`
——criterion revision 事前凍結 clause priority 全序，`best_so_far` **必須指向一個實際
candidate 的實際 verdict vector**（`{candidate_ref, verdict_vector_digest}`），只有新候選
在凍結序下**嚴格勝過**目前 best 才重置窗口；② 終態與 claim 改名：`NO_PROGRESS` →
`NO_OBSERVED_PROGRESS`、claim `pursuit.retry.no-observed-progress-typed`——而且封閉
enum 裡**完全沒有 `NO_PROGRESS` 這個成員**，寫它就是 unknown enum direct red（改名
有機械牙齒，不是措辭）；③ 固定負控補 sol 兩格：跨候選聯集不得冒充單一最佳候選
（紅在 `best_so_far_is_actual_candidate`）、粗粒度時必須明示 observational stop（enum 格）；
④ sol 那條「ordinal 改善須重置」是條件式的——v1 `per_clause_scale` 固定 `PASS_FAIL`，
不支援 clause 內 ordinal，所以停止語意就是 observational policy stop（名字本身說了這件事）；
**ordinal 重置義務隨未來 `per_clause_scale` 擴充的 admission 一併宣告**，寫進 Forbids，
不是丟掉；⑤ `K` 必填無預設、`1 ≤ K < max_executions` 保留（sol 認可）。

**改什麼**
- `docs/計畫/08-目標追求生命週期.md` 新增 Task 8（接 Task 7 之後）＋ File Structure 補列：
  - Create: `規格/追求/ProgressMeasureSpec.schema.json`
  - Create: `規格/追求/保證/無觀測進展終態.claim.json`
  - Create: `驗收/追求/測_無觀測進展終態.py`
  - Modify: `規格/追求/AttemptPolicy.schema.json`（必填 `max_stagnant_attempts`）
  - Modify: `規格/追求/追求.machine.json`（`POLICY_STOP` reason enum 增 `NO_OBSERVED_PROGRESS`）
  - Modify: `nova/領域/追求/模型.py`、`nova/領域/追求/決策.py`、`nova/領域/追求/test_追求決策.py`
- comparator：兩個實際 verdict vector 依凍結 `clause_priority` 字典序逐格比對
  （PASS > FAIL）；良基性由構造保證——有限 clause 集上的字典序是有限全序，
  嚴格上升鏈長 ≤ 相異 rank 值數。measure 不跨 criterion revision 比較
  （revision 改變依 Task 5 矩陣本來就是 NEW_PURSUIT）。

**為什麼**
不改的後果同 R2：一個 Pursuit 可以 16 次 attempt 在甲乙之間振盪、或每次換 bytes 而
verdict 永不改善，燒滿預算後帳面是井然有序的 `EXHAUSTED`，沒有任何一格紅過；
核心能力排序 #10 的最晚裁定點（plan 08 實作前）窗還開著。R2 的錯在 union——
本版的 best 永遠是一個真的存在過的候選。
- 查證：`grep -n "NO_OBSERVED_PROGRESS\|ProgressMeasureSpec" docs/計畫/08-*.md` → 套用前 0；
  `grep -n "POLICY_STOP" docs/計畫/08-*.md` → 16、132（terminal union 既有，reason enum 是
  本 task 增補面）；FeedbackPacket ref 已是 retry 輸入（08:34）——觀測素材既有，不新發明。

**地基**
- 官方：官方層查不到「無進展偵測」標準（照實寫）。
- 權威：SPIN non-progress cycle detection（Holzmann，spinroot 官方文件）——無進展要抓的
  是**環**不是相鄰相等，凍結序下的 best-candidate 對振盪環正確觸發；Alpern & Schneider 1985
  （DOI `10.1016/0020-0190(85)90056-0`，200）——只有 safety 的規格是留白；
  Kuper & Newton LVars（DOI `10.1145/2502323.2502326`，200）與 CALM
  （DOI `10.1145/3369736`，200）——凍結偏序上單調追蹤的良基性與決定性；
  sol R2 裁決原文——`best_so_far` 必須指向實際 candidate verdict vector 或實際
  Pareto frontier，PASS/FAIL 粒度下只能回報 `NO_OBSERVED_PROGRESS`。
- **`BEST_CANDIDATE_UNDER_FROZEN_ORDER` 作為 v1 唯一 measure、K 必填無預設：無地基，
  這是 nova 的拆解決定**（sol 給的最簡形）。

**加蓋**
nova 多出來的拒絕：①停滯窗滿後的 `StartExecution` 拒絕（動作①）；②缺 K 或
K≥max_executions 的 AttemptPolicy admission 拒絕；③`measure_kind` 與 `per_clause_scale`
是 namespaced 封閉 enum，未知成員 fail-closed（動作②）；④`NO_PROGRESS` 不是合法成員。
有沒有改到地基的介面：沒有；全部是 nova 未實作 schema 的計畫文字。

**固定負控**
- `oscillating-repeat` → [`stagnant_window_exceeded_refused`, `terminal_reason_no_observed_progress`]
- `novel-bytes-no-improvement` → 同上兩條
- `cross-candidate-union` → [`best_so_far_is_actual_candidate`]
- `no-progress-name` → [`terminal_reason_vocabulary_closed`]
- 防恆真格：第 K 次恰有更高優先 clause 轉綠 → 窗口重置、16 次不誤殺；property test
  以樸素參考實作對照「觸發 ⇔ 連續 K 次無嚴格勝過」＋良基上界斷言。

**不變式檢查**
檔 8／claim 1／落點行自帶／先紅步 Expected: FAIL／恰 1 commit（訊息含漢字）。
識別字全過 I8（負控 fixture 用甲乙不用 A/B）。**mock-apply I1–I11 全綠。**

---

### R3-03(fable) 決定性 v1 只有 `PURE_REPLAYER` 一條路（原 R2-03）

**狀態**：PROPOSED

**相對 R2 改了什麼**
① `SEEDED_OUTPUT_DETERMINISM` 的 mechanism enum **v1 唯一成員 `PURE_REPLAYER`**（sol：
另外兩個只是名稱，任意 backend 填個 ref 就可能取得過強能力）；`PINNED_DETERMINISTIC_ENGINE`
與 `BACKEND_CONTRACT_WITH_CONFORMANCE_SUITE` **移出 v1 可准入 enum**，重入條件逐字寫進
計畫：各自具備獨立 admission schema、checker 與固定負控後，以擴充點（加蓋動作②）加入；
② 新增第四個字彙條目 `CONTRACTUAL_OUTPUT_DETERMINISM_CLAIMED`——外部 backend 目前最多
取得它或 `SEEDED_OUTPUT_REPEATABILITY_OBSERVED`；前者是**契約主張**，計畫明文
**不得滿足要求機械決定性的 claim 綁定**（有限 conformance suite 只證明 suite 範圍內
符合契約）；③ 固定負控照 sol 補兩格：`forged-mechanistic-ref`（mechanism 填
`PURE_REPLAYER` 但 ref 指向不可驗來源）與 `contract-claim-cannot-bind-mechanical`
（fixture 內附 suite 全過而 suite 外同 seed 輸出漂移的見證）；④ 四層重播界線表
原封保留（sol：本身正確）。

**改什麼**
- `docs/計畫/01B-執行者能力契約與SDK探針.md`（Modify，兩個 task 檔數不變）：
  - Global Constraints 增兩條：四層重播界線（含「錄製義務不因後端非決定而免除」）；
    seeded 家族封閉字彙四條目與 v1 mechanism enum 唯一成員的完整規則。
  - Task 1：Interfaces 增 seeded 四條目與 mechanism enum；Forbids 增「repeatability／
    contractual evidence 鑄出 determinism」；固定負控增「把 `PINNED_DETERMINISTIC_ENGINE`
    填進 mechanism enum 必須 direct red」。
  - Task 4：三種 evidence 的必記欄位（repeatability＝{N, fingerprint, request digest,
    N 份輸出 digest, TTL}；determinism＝{mechanism=PURE_REPLAYER, 重播器 claim ref}；
    contractual＝{contract ref, suite ref, pass record digest}）；固定負控增四格。

**為什麼**
不改的後果同 R2：輸出決定性沒有 typed 的家，未來綁「同輸入同 digest」的 claim 要嘛
編不出來（副作用不是設計）、要嘛被 N 次 smoke 冒充。R2 的錯在給了兩個沒有機制背書的
名字——本版 enum 裡只剩機制存在的那一個，其他要憑自己的 admission 換門票。
- 查證：`grep -rn "SEEDED" docs/計畫/*.md` → 套用前 0；
  `sed -n '151,216p' docs/計畫/05-執行封套與重播器.md`（重播器 claim
  `execution.backend.replayer-contract-parity` 存在，`PURE_REPLAYER` 的正控主體現成）；
  計畫 17:352 已把「deterministic seed without repeat evidence」列 explicit unsupported。

**地基**
- 官方：Anthropic「Even with temperature set to 0, the results will not be fully
  deterministic」；OpenAI seed「(mostly) deterministic」＋`system_fingerprint` 會變——
  官方只承諾到「觀測上大致重複」，正好是 `REPEATABILITY_OBSERVED` 的強度。
- 權威：arXiv:2408.04667（10 次重跑無模型全數逐字重現）；DOI `10.1145/3697010`（200；
  47.56%–75.76% 題目無任何兩次相同）；Thinking Machines batch-invariance——決定性的
  自變數在伺服器端，只有機制層面的控制才撐得起 determinism 之名；sol R2 裁決原文——
  有限 conformance suite 最多證明 suite 範圍內符合契約。
- **evidence 欄位形狀與「v1 唯一成員」這個切法：無地基，這是 nova 的拆解決定。**

**加蓋**
nova 多出來的拒絕：repeatability／contractual evidence 冒充 determinism → 拒絕鑄名；
mechanism enum 外的成員 → schema direct red；契約主張綁機械決定性 claim → 拒絕。
封閉字彙加條目與未來重入都是動作②（namespaced、versioned、未知條目 fail-closed）。
有沒有改到地基的介面：沒有。

**固定負控**
- `probe-upgraded-to-determinism` → [`determinism_requires_mechanistic_evidence`]
- `nth-plus-one-differs` → [`repeatability_is_not_determinism`]
- `forged-mechanistic-ref` → [`mechanistic_ref_must_resolve`]
- `contract-claim-cannot-bind-mechanical` → [`contract_claim_is_not_mechanism`]
- 防恆真格：計畫 05 重播器以 `PURE_REPLAYER` 取得 supported（拒絕不是無條件）；
  合規 N 次 probe 取得 `REPEATABILITY_OBSERVED` supported。

**不變式檢查**
Task 1 檔 8／Task 4 檔 4；claim 各 1；01B 已遷移，落點行不動、基線不動。
**mock-apply I1–I11 全綠。**

---

### R3-04(fable) 准入信任根先 bootstrap，職責分離才有東西可比（原 R2-04）

**狀態**：PROPOSED

**相對 R2 改了什麼**
① 照 sol 指示**拆出 bootstrap task**：01 新增 Task 17 建 `AdmissionTrustRoot`
（封閉欄位：trusted attestation issuer／repository/ref／workflow identity／actor identity
extraction rule／trust-root revision/digest／expiry/revocation），Task 18 才做四角色
職責分離——R2 把角色比對建在不存在的 attestation path 上，fixture 綠不代表 production
拿得到可信 actor；② 「required workflow 不取自候選 PR 可寫的 ref」做成 repo-settings
probe，產出 content-addressed `ProbeRecord`（queried_at、payload digest、verdict、TTL），
走**錄／播／明講跳過**（燒錢測試既有紀律）；TTL 形狀比照 01B Task 4，probe 過期不得沿用；
③ 創世儀式照 sol 三件：控制端建立 trust-root revision、**另一個** attested actor 核准
第一份 manifest、創世證據 content-addressed 保存——且是**明示、一次性、可驗證**的
transition，不會永遠死鎖（sol 特別問答第 3 點）；④ trust path 未閉合時新增 admission
一律 typed `ADMISSION_TRUST_ROOT_UNAVAILABLE`——fail-closed 是設計不是事故，
已存在的 entry 照常比對不受影響；⑤ role-separation claim 以 live trust-root probe 為
前置（新負控 `stale-probe`），不能只靠本地簽章 fixture 轉綠；⑥ 四角色、
`admission_decided_by != subject_changed_by` 最低不等式、attestation 解析比對、
無 `SELF_CERTIFIED` 靜默降級——沿用 R2（sol：可以保留）。

**改什麼**
- `docs/計畫/01-可執行保證語言.md` 新增 Task 17（7 檔）＋ Task 18（4 檔）＋
  File Structure 補列＋ Exit Gate 命令補兩支：
  - Task 17 Create: `規格/工程/AdmissionTrustRoot.schema.json`、
    `規格/工程/准入信任根.admitted.json`、`規格/工程/創世准入證據.json`、
    `規格/工程/保證/准入須有信任根.claim.json`、`架構/檢查准入信任根.py`、
    `架構/test_准入信任根.py`；Modify: `架構/檢查已准入保證.py`。
    claim `engineering.admission.trust-root-required`。
  - Task 18 Create: `規格/工程/保證/准入職責分離.claim.json`；Modify:
    `規格/驗收/ClaimAdmissionManifest.schema.json`（四角色欄，每欄
    `{textual_id, attestation_ref}`）、`架構/檢查已准入保證.py`、`架構/test_已准入保證.py`。
    claim `engineering.admission.role-separation-attested`。
  - live probe 與創世儀式在 task 內**標明為控制端步驟**；實作者可跑的紅測全是拒絕路徑。

**為什麼**
不改的後果同 R2：Task 16 的 `closure-immutable` 綠著，而「誰有權新增 admission」是空的
——同一主體既裁定准入又改 subject 時保證名義成立、實質為零；且 CLAUDE.md 上限四實測
證明 CI 跑的是候選者自己那份 checker，沒有信任根，角色欄填什麼都是被閘者自報。
誠實邊界沿 Task 16：本 task 不宣稱 CI 信任方向已閉合——閉合與否由 probe verdict 說話，
交付的是「未閉合時 fail-closed ＋ 閉合證據可機械檢查」。
- 查證：`sed -n '1091,1200p' docs/計畫/01-可執行保證語言.md`（Task 16 manifest 現無任何
  主體欄、無新增權限檢查）；`grep -rn "AdmissionTrustRoot\|准入信任根" docs/計畫/` →
  套用前 0（既有「信任根」字樣全是 00-總覽 描述計畫鏈的散文，無檔案碰撞）。

**地基**
- 官方：SLSA v1.0 Source Track——身分與連續性由平台 attestation 承載、自明確起始
  revision 建立並追蹤，不由被閘者自報；NIST SSDF PO.4.2——判準資訊必須防竄改刪除；
  GitHub 官方——ruleset workflows 可指定 workflow 檔來自另一 repo／另一 ref（probe 驗的
  就是這件事有沒有真的設下去）；Clark–Wilson ER3（DOI `10.1109/SP.1987.10001`，200）——
  「must authenticate each user attempting to execute a TP」，身分是 SoD 的前提不是配套。
- 權威：Clark & Wilson 1987 ER4 後半；Saltzer & Schroeder 1975
  （DOI `10.1109/PROC.1975.9939`，200）；CERT 內部威脅案例 5（用主管帳號 check-in——
  字串合規、身分已破）；HRU 1976（DOI `10.1145/360303.360333`，200）——本閘做違反偵測，
  不做不可能性證明；NIST SP 800-53 AC-5（DOI `10.6028/NIST.SP.800-53r5`，200）。
- **信任根欄位形狀、創世儀式的具體三步：無地基，這是 nova 的拆解決定**
  （sol 給的形狀）。

**加蓋**
nova 多出來的拒絕：無信任根／過期 probe 的新增 admission、創世自我核准、創世重演、
解析後同 actor 跨 decider/changer、不可驗 attestation——全部 typed 拒絕（動作①）。
有沒有改到地基的介面：沒有；manifest 是 nova schema，Task 16 未實作。

**固定負控**
- Task 17：`no-trust-root-new-admission` → [`admission_requires_trust_root`]；
  `workflow-ref-candidate-writable` → [`workflow_ref_outside_candidate_write`]；
  `genesis-self-approved` → [`genesis_requires_distinct_actor`]；
  `genesis-twice` → [`genesis_occurs_at_most_once`]
- Task 18：`same-actor-two-ids`／`decider-is-changer` → [`roles_resolve_to_distinct_actors`]；
  `no-attestation` → [`unverified_role_separation_rejected`]；
  `stale-probe` → [`role_separation_requires_live_trust_root`]
- 防恆真格：合法信任根＋未過期 probe＋相異 attested actor 的 entry 放行；
  未觸碰 manifest 的一般 commit 六道閘全綠照過。

**不變式檢查**
Task 17 檔 7／claim 1；Task 18 檔 4／claim 1；各自落點行、先紅步、恰 1 commit。
`檢查已准入保證.py` 被 T17/T18 各 Modify 一次（I1 只禁雙重 Create）。
**mock-apply I1–I11 全綠。**

---

### R3-05(fable) 揭露帳走 machine：`ReserveDisclosure` 經 state owner，不直接 append（原 R2-05）

**狀態**：PROPOSED

**相對 R2 改了什麼**
① R2 把 state owner 當可任意 append 的 event store，撞計畫 03 行 23「command 必經已釘
`MachinePlan` 取得唯一 transition」——本版 Create 明示 machine
`規格/判準/揭露帳.machine.json`（sol 指定路徑），command `ReserveDisclosure`、event
`DisclosureRecorded`／`DisclosureExhausted`；應用層只呼叫
`StateOwnerClient.execute(CommandEnvelope)`，`entity_id = sealed_pool_lineage_id`，
**不得直接 append event**；② crash 後同 bytes 的來源寫死：transition transaction **之前**
先把 canonical FeedbackPacket bytes 放入 CAS（計畫 04），event 記
{`disclosure_id`, `packet_content_ref`, `packet_digest`, `sealed_pool_lineage_id`,
`ordinal`}，重啟從 CAS 以 ref 取回**完全相同 bytes** 重送同一 `disclosure_id`——
不重跑 reducer、「大概會一樣」不是保證；③ machine 必須拒絕的四件照 sol 逐字：
同 id 不同 digest／ordinal 超 cap／lineage 不符（三者為 machine spec 內固定負控，
`工具/驗規格.py --含固定負控` 驗——計畫 02 既有形狀，新增 Step 3 專跑）＋
未 commit 就 release（應用層負控 `release-before-commit`）；④ 檔案清單重列，
8 檔（十檔內，sol 要求）；⑤ lineage key、cap 事前釘、超 cap 停發 verdict 照記、
Dwork 強度標示（區分 Theorem 17 有限 range bound 與 adaptive composition lemma）——
沿用 R2（sol：已修正、可以保留）。

**改什麼**
- `docs/計畫/06-判準評估與隔離回饋.md` 新增 Task 8（接 Task 7 之後）＋ File Structure 補列：
  - Create: `規格/判準/揭露帳.machine.json`、`規格/判準/DisclosureLedger.schema.json`、
    `nova/權威/判準/揭露帳本.py`（純 fold，`allow_io=false` 不衝突）、
    `驗收/判準/測_揭露帳本.py`（SIGKILL matrix 沿用 Task 6 形狀）、
    `規格/判準/保證/揭露總量有界.claim.json`（claim `criterion.disclosure.transcript-bounded`）
  - Modify: `規格/判準/CriterionDefinition.schema.json`（必填 `sealed_pool_lineage_id`）、
    `規格/判準/FeedbackPolicy.schema.json`（必填 `disclosure_cap`）、
    `nova/應用/執行判準.py`（CAS → `ReserveDisclosure` → commit → release）

**為什麼**
不改的後果同 R2：Task 5／6 的保證綠著，sealed 判準辨識力跨 run 靜默流失——帳只活在
記憶體，重啟即洗掉 cap，而 R1 的負控只測同一程序內的第 cap+1 次。R2 的錯在介面——
本版走的是計畫 03 的正門與計畫 06 Task 6 已驗證的 burn-before-reveal 形狀。
- 查證：`sed -n '20,30p' docs/計畫/03-權威狀態與事件日誌.md`（行 23：command 經已釘
  MachinePlan 取得唯一 transition）；06 Task 6 Step 3 既有
  `state_owner.transition(...)`＋`evidence_store.get(...)`——兩個 port 都現成；
  06 前置含 03、04（I5 成立）；`grep -rn "揭露帳\|DisclosureLedger" docs/計畫/` → 套用前 0。

**地基**
- 官方：NIST FRVT／SRE 提交限流與雙子集——實務存在、定性、不對題，照實標。
- 權威：Dwork 等 arXiv:1506.02629 Theorem 17——只取「有限 transcript range ⇒ 有限
  max-information 上界」的形狀，|Y| 按整段 transcript 計、adaptive composition 下累加
  ⇒ key 必須是跨 revision／Pursuit 的 lineage；Blum–Hardt（Ladder）——離散化本身不是保證。
- **cap 數值、「先記帳再釋出」與 machine 的具體形狀：無地基，這是 nova 的拆解決定**
  （03 正門＋06 Task 6 既有模式的重用）。宣稱 DP／統計有效性的請求 →
  `UNSUPPORTED_DISCLOSURE_MECHANISM`（§十九 第 7 項原話）。

**加蓋**
nova 多出來的拒絕：超 cap 停發（verdict 照記，只斷回饋）；lineage 額度不可被 revision／
sibling 洗掉；commit 前不得釋出；重送只認同 digest；machine 拒絕未宣告 transition
（03 既有硬閘承載）。有沒有改到地基的介面：沒有——**這正是 R2 被退的點，本版改走正門**。

**固定負控**
- `crash-then-reset` → [`ledger_survives_restart`]
- `sibling-resets-budget`／`revision-resets-budget` → [`lineage_scoped_budget`]
- `release-before-commit` → [`disclose_after_persist`]
- `disclosure-beyond-cap` → [`disclosure_beyond_budget_refused`]
- machine spec 內三格：同 id 不同 digest／ordinal 超 cap／lineage 不符
  （`工具/驗規格.py --含固定負控` 驗）
- 防恆真格：cap 內照發；crash 後重送同 id 同 digest 不重複扣額度；cap 滿後 verdict 照記。

**不變式檢查**
檔 8（十檔內，含新 machine 檔的完整重列）／claim 1／落點行／先紅步 Expected: FAIL／
恰 1 commit。Modify 三檔全由本計畫 Task 1／5 Create（I5 成立）。**mock-apply I1–I11 全綠。**

---

## 我這一輪刻意沒提的，以及為什麼

1. **新題目沒提**——先把五條做對；sol 本輪也明說不另提 `R2-07(sol)`，把 trust-root
   bootstrap 直接併進 R3-04 比開競爭提案乾淨。
2. **R3-02 不做 Pareto frontier 版**——sol 給了兩個合法形（實際 candidate vector 或實際
   Pareto frontier），v1 取前者：frontier 版要多定義支配關係與 frontier 的持久形狀，
   口徑會超出一個 task；凍結全序版已涵蓋「best 是真候選」這個核心，frontier 留給
   未來 measure_kind 擴充。
3. **R3-04 只強制一條不等式**——沿 R2 立場：`criterion_authored_by`／`evidence_executed_by`
   先記錄不強制，等真實 admission 記錄累積再提第二條，避免 bootstrap 期沒人能完成 admission。
4. **repo 現況的 mypy 欠帳、計畫 12 遷移**——與前兩輪同理由，未變。

## 給 claude 的兩條順手訊息（不是決議）

- `CLAUDE.md` 「這個專案在做什麼」節寫「21 份計畫，164 個 task」，現況 22 份／184
  （本輪核准後 188）。改 CLAUDE.md 是你的權限，我只指出數字已過期。
- mock 目錄 `/private/tmp/fable-R3-mock/` 與 diff 我會留著到你裁決完；套用時請以 diff
  為準重跑一次 `計畫複驗.py`，不要信我貼的輸出（不要對執行者的自報照單全收，我也是執行者）。
