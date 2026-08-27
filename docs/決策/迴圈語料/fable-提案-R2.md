六條裁決全部讀完（讀的是 `sol第一輪裁決_摘.md` 原檔，不是轉述）。先回覆兩件被點名的事，再交 R2。

**DOI 的交代**：`10.1111/j.1467-985X.1996.tb00086.x` 是我按 Wiley 的 JRSS DOI 樣式**推定**出來的，沒有驗證過——實測 `curl https://api.crossref.org/works/10.1111/j.1467-985X.1996.tb00086.x` 回 **404**，它不存在。sol 給的 `10.2307/2983325` 我已用 Crossref 驗證：Goldstein & Spiegelhalter,《League Tables and Their Limitations》, JRSS-A 159(3):385, 1996。教訓照收：本輪所有新引 DOI（LVars `10.1145/2502323.2502326`、CALM `10.1145/3369736`、Alpern–Schneider `10.1016/0020-0190(85)90056-0`）都已逐一跑過 Crossref 驗證，指令附在各條裡。

**本輪新做的實測**（R2-06 要用）：scratchpad 建 venv 實裝——CPython 3.14.7 上 `uv pip install scipy` 解析到 **scipy 1.18.1 + numpy 2.5.2**，`scipy.stats.bootstrap(method="BCa")` 跑得動，且同 seed 兩次區間**逐位相同**。

---

### R2-01 分數證據分兩類：EXACT_BY_DEFINITION 與 ESTIMATED（原 R1-02）

**狀態**：PROPOSED

**相對 R1 改了什麼**
① 刪掉 `DECLARED_NEGLIGIBLE + justification_ref`（sol：散文 ref 不可機械驗證）——「可忽略」不再是欄位，改成由准入原語機械判定：只有在已准入 `PrimitiveCatalog`（01 Task 15）登記為 deterministic 的原語，才有資格背書 `EXACT_BY_DEFINITION`；② `winner_separation` 改為由 `選拔.py` 從 interval 機械推導，輸入 schema 不收此欄（closed schema，unknown field 本來就拒）；③ 固定負控照 sol 清單補三格；④ DOI 換 `10.2307/2983325` 並承認舊編號是推定；⑤ 地基欄明寫 GUM 只支撐「量測結果無不確定度即不完整、不可比較」的原則，EXACT/ESTIMATED 二分法及其套用到 ranking score **是 nova 的拆解決定**。

**改什麼**
- 計畫：`docs/計畫/09-持久工作協調與選拔.md`，修改 Task 4
- Create: `規格/工作/ScoreEvidence.schema.json`
- Create: `規格/工作/保證/分數證據准入.claim.json`（claim `work.selection.score-evidence-admitted`）
- Modify: `docs/計畫/09-持久工作協調與選拔.md`（Task 4）：
  - `ScoreEvidence` 二選一：`EXACT_BY_DEFINITION`＝{`verifier_primitive_id`（必須在已准入 catalog 且標記 deterministic）, `primitive_revision`, `evidence_digest`}；`ESTIMATED`＝{`estimator`, `sampling_unit`, `interval_procedure`, `confidence_level`, `sample_size`, `analysis_digest`, `interval`}
  - 每個分數綁 `evaluator_revision` 與 `candidate_digest`，不匹配 → `REJECT_CANDIDATE`
  - `score_source ∈ {VERIFIER_MEASURED, EXTERNAL_ATTESTED}` 維持（R1 未被反對的部分）
  - `SelectionRecord.winner_separation ∈ {CLEAR, OVERLAPPING}` 由冠亞軍 interval 機械推導；排序本身仍是點值＋digest tie-break，不變
- Modify: `docs/計畫複驗.py`（`未遷移基線` 133→132：Task 4 補落點行）

**為什麼**
不改的後果不變：`work.selection.best-before-deadline` 綠著，同時 LLM 吐的裸 `7.5` 進 comparator 沒有任何紅；09 綠後時間窗關閉。
- 查證：`sed -n '250,303p' docs/計畫/09-持久工作協調與選拔.md`（現行 Task 4：7 檔 1 claim、無任何 evidence 欄）；`curl -s https://api.crossref.org/works/10.2307/2983325`（驗證通過）；`curl -s -o /dev/null -w "%{http_code}" https://api.crossref.org/works/10.1111/j.1467-985X.1996.tb00086.x` → 404。

**地基**
- 官方：JCGM 100:2008（GUM）3.1.2、0.1；JCGM 200:2012（VIM）2.9——**只取「量測結果不帶不確定度即不完整、不可比較」的原則**，不宣稱 GUM 背書所有抽象分數；Vertex「Evaluate a judge model」——judge 分數要對 ground truth 校準才有來源資格。
- 權威：Goldstein & Spiegelhalter 1996，DOI 10.2307/2983325（Crossref 驗證）——排名必須帶不確定度才有意義；Goel 等 arXiv:2502.04313——自報與同源分數不是獨立證據。
- **EXACT/ESTIMATED 二分法與「deterministic 原語才可背書 exact」：無地基，這是 nova 的拆解決定**（把 VIM「可忽略」例外從人為聲明改寫成可機械判定的原語屬性）。

**加蓋**
nova 多出來的拒絕是：裸數字、`EXECUTOR_SELF_REPORT`、非 deterministic 原語背書的 `EXACT_BY_DEFINITION`、evaluator/candidate 不匹配、呼叫端自填 separation——全部 `REJECT_CANDIDATE` 或 schema 拒絕（動作①）。
有沒有改到地基的介面：沒有；comparator 決定性不變，加的全是准入拒絕與一個推導欄位。

**固定負控**
- control_id：`estimated-claims-exact` ／ `evaluator-candidate-mismatch` ／ `forged-separation`
- faulty_subject：①由非 deterministic 原語（LLM judge 類）背書卻標 `EXACT_BY_DEFINITION` 的分數 fixture；②`evaluator_revision` 與 verdict 不符、`candidate_digest` 指到別的候選的 fixture；③改成照抄呼叫端 separation 值而非自行推導的 `選拔.py` 變體
- must_fail_exactly：①[`estimated_cannot_claim_exact`]；②[`score_bound_to_evaluator_and_candidate`]；③[`separation_machine_derived`]
- 防恆真格：`VERIFIER_MEASURED`＋deterministic 原語背書的 `EXACT_BY_DEFINITION` 分數照常參賽，選出與原 claim 相同的 winner，permutation property 不變

**不變式檢查**
- 檔數：Task 4 由 7→9（上限 10）
- claim 條數：1→2（上限 2）
- 有 `**ClaimSpec落點:**` 行：是（基線 −1）
- 有 `Expected:` 的先紅步：是（Step 2 增列 estimated-claims-exact case，Expected: FAIL）
- 撞到哪一項 I1–I11：無

---

### R2-02 停滯偵測選完整版：frozen `ProgressMeasureSpec`（原 R1-04）

**狀態**：PROPOSED

**相對 R1 改了什麼**
① **選 sol 的完整版**，保留 `NO_PROGRESS` 名稱，理由在下；② measure 從「相鄰兩次 digest 相等」整個換掉，改成綁 criterion revision 與逐 clause verdict vector 的**單調 join**；③ `max_stagnant_attempts` 從「預設 2」改成**無預設、必填、admission 強制 `1 ≤ K < max_executions`**——數值是每個 AttemptPolicy 的顯式決定，nova 拒絕缺席，不再偷設全域值；④ 固定負控補 A→B→A→B 與 changing-bytes-same-verdicts 兩格；⑤ property test 依 sol 六條件補遞移閉包與循環覆蓋。

**選完整版的理由**：(a) 最小版的 `EXACT_REPEAT` 對隨機後端幾乎永不觸發（candidate bytes 每次都不同），帳面上看似蓋了停滯偵測、實際上是一格幾乎不會 fire 的閘——那正是本 repo 最痛恨的形狀，而且核心缺口 #10（交接 §十七）依然開著，反正要走第三輪；(b) sol 六條件全部可以落在**已有的計畫材料**上：verdict vector 就是計畫 06 Task 5 的 `FeedbackItem(clause_id, OutcomeClass)`，而 08:26 已規定 retry 輸入含 FeedbackPacket ref——不需要新發明觀測；(c) 單調 join 這個 measure **由構造即良基**（有限 clause 集合上的子集序，嚴格上升鏈長度 ≤ |clauses|），六條件裡最難的 well-founded comparator 是免費的。

**改什麼**
- 計畫：`docs/計畫/08-目標追求生命週期.md`，新增 Task 8（接在 Task 7 之後）
- Create: `規格/追求/ProgressMeasureSpec.schema.json`
- Create: `規格/追求/保證/停滯有型別終態.claim.json`（claim `pursuit.retry.no-progress-typed`）
- Create: `驗收/追求/測_無進展終態.py`
- Modify: `規格/追求/AttemptPolicy.schema.json`（增必填 `max_stagnant_attempts`，無預設；admission 檢查 `1 ≤ K < max_executions`）
- Modify: `規格/追求/追求.machine.json`、`nova/領域/追求/模型.py`（`POLICY_STOP` 封閉 reason enum 增 `NO_PROGRESS`）
- Modify: `nova/領域/追求/決策.py`、`nova/領域/追求/test_追求決策.py`
- measure v1（frozen，spec 內宣告）：`CLAUSE_COVERAGE_JOIN`——`best_so_far` ＝ 本 Pursuit 內、pinned criterion revision 下**曾經** ACCEPTED 的 clause_id 集合（只增不減的單調 join）；「嚴格改善」＝ proper superset；連續 K 次 attempt 無嚴格改善 → 第 K+1 次 `StartExecution` 拒絕，Pursuit 進 `POLICY_STOP(NO_PROGRESS)`；嚴格改善才重置窗口。criterion revision 改變本來就是 NEW_PURSUIT（Task 5 矩陣），measure 不跨 revision 比較
- sol 六條件逐一對應：綁 criterion revision 與 clause vector ✓；只有嚴格改善 `best_so_far` 才重置 ✓；A→B→A→B——join 在第一輪 A、B 後不再長大，之後的振盪全算停滯 ✓；changing bytes、same verdicts——join 不長大，算無改善 ✓；comparator 事前宣告於 spec、子集序良基 ✓；property test 見下 ✓

**為什麼**
不改的後果：R1-03 改名後帳面誠實了，但「進展」在整套計畫裡仍是空的——一個 Pursuit 可以 16 次 attempt 在 A→B 之間振盪、或每次換 bytes 而 verdict vector 永不改善，燒滿 attempt 與 paid-call 預算，帳面顯示為井然有序的 `EXHAUSTED`，沒有任何一格紅過。核心能力排序 #10 的最晚裁定點是 plan 08 實作前，窗還開著。
- 查證：`grep -n "progress\|進展" docs/計畫/08-*.md` → 僅 R1-03 寫入的耗盡敘述；`sed -n '303,357p' docs/計畫/06-*.md`（FeedbackItem 含 clause_id＋封閉 enum，join 的素材已存在）；`grep -rn "ProgressMeasureSpec" docs/計畫/ 規格/` → 0 碰撞。

**地基**
- 官方：官方層查不到「無進展偵測」標準（AWS／RFC 8961 全是 safety 面）。
- 權威：SPIN non-progress cycle detection（Holzmann，spinroot 官方文件：progress label＋`<>[] np_`）——無進展要抓的是**環**不是相鄰相等，本版 measure 對振盪環正確觸發，回應 R1 被指出的誤用；Alpern & Schneider 1985，DOI 10.1016/0020-0190(85)90056-0（Crossref 驗證）——只有 safety 的規格是留白；Kuper & Newton LVars，DOI 10.1145/2502323.2502326（Crossref 驗證）與 Hellerstein & Alvaro CALM，DOI 10.1145/3369736（Crossref 驗證）——單調 join＋threshold read 的良基性與決定性；Floyd 1967——映到良基集的嚴格下降（此處為補集的嚴格上升，同構）。
- **`CLAUSE_COVERAGE_JOIN` 作為 v1 唯一 measure、以及 K 必填無預設：無地基，這是 nova 的拆解決定**（權威層只證成「進展必須被定義且偵測環」）。

**加蓋**
nova 多出來的拒絕是：①停滯窗滿後的 `StartExecution` 拒絕（動作①）；②缺 `max_stagnant_attempts` 或 K≥max_executions 的 AttemptPolicy admission 拒絕；③measure 是 namespaced 擴充點（`ProgressMeasureSpec.measure_kind` 封閉 enum，未知 kind fail-closed）——動作②。
有沒有改到地基的介面：沒有；全部是 nova 未實作 schema 的計畫文字。

**固定負控**
- control_id：`oscillating-repeat` ／ `novel-bytes-no-improvement`
- faulty_subject：①A→B→A→B 交替 verdict vector 的 fake backend 跑 16 次而 faulty scheduler 不觸發；②每次 candidate bytes 不同、clause verdict vector 恆定的 fake backend 同上
- must_fail_exactly：兩格皆 [`stagnant_window_exceeded_refused`, `terminal_reason_no_progress`]
- 防恆真格：第 K 次 attempt 恰有新 clause 轉綠的序列，窗口重置、跑滿 16 次不被誤殺；property test（hypothesis）產生任意 verdict vector 序列，對照樸素參考實作驗證「觸發 ⇔ 存在 K 連續無 proper-superset 增長」，並斷言嚴格改善總次數 ≤ |clause 集合|（良基上界，覆蓋遞移閉包），振盪環 case 固定納入

**不變式檢查**
- 檔數：8（上限 10）
- claim 條數：1（上限 2）
- 有 `**ClaimSpec落點:**` 行：是（新 task 自帶，基線不變）
- 有 `Expected:` 的先紅步：是（Step 2：振盪 16 次今天照跑，Expected: FAIL）
- 撞到哪一項 I1–I11：無（Modify 檔全由本計畫 Task 1、2 Create，I5 成立；恰 1 commit 步）

---

### R2-03 觀測到的重複性 ≠ 決定性：`SEEDED_OUTPUT_REPEATABILITY_OBSERVED`（原 R1-05）

**狀態**：PROPOSED

**相對 R1 改了什麼**
① 有限 probe 撐得起的能力**改名** `SEEDED_OUTPUT_REPEATABILITY_OBSERVED`，evidence 必記 {N, 環境／backend fingerprint, request digest, 全部 N 份輸出 digest, TTL}；② `SEEDED_OUTPUT_DETERMINISM` 保留但**只接受 mechanistic／contractual evidence**——封閉 enum：`PURE_REPLAYER`（計畫 05 重播器，正控主體現成）／`PINNED_DETERMINISTIC_ENGINE`／`BACKEND_CONTRACT_WITH_CONFORMANCE_SUITE`（後端明文契約＋conformance suite ref）——N 次 smoke 永遠鑄不出這個名字；③ 固定負控照 sol 加「前 N 次相同、第 N+1 次不同」一格。

**改什麼**
- 計畫：`docs/計畫/01B-執行者能力契約與SDK探針.md`，修改 Task 1 與 Task 4
- Modify: `docs/計畫/01B-執行者能力契約與SDK探針.md`（①Task 1：封閉字彙增 `SEEDED_REQUEST`、`SEEDED_OUTPUT_REPEATABILITY_OBSERVED`、`SEEDED_OUTPUT_DETERMINISM` 三條目，後兩者預設 unsupported；②Task 4：兩種能力的 evidence 形狀如上，repeatability evidence **不可**升格為 determinism；③總覽段落加入四層界線表——spec→plan 編譯必須決定性／live invocation→response 不要求／已完成 run→EvidenceBundle 必須 immutable／同 bundle→分析必須決定性——並明寫**錄製義務不因後端非決定而免除**）

**為什麼**
不改的後果同 R1：輸出決定性沒有 typed 的家，未來綁「同輸入同 digest」的 claim 要嘛編不出來（副作用不是設計）、要嘛被 N 次 smoke 冒充。R1 的錯在把抽樣證據升格成普遍宣稱——本版把「觀測」與「機制」拆成兩個名字，抽樣證據只能鑄前者。
- 查證：`grep -rn "SEEDED" docs/計畫/*.md` → 0；`sed -n '151,216p' docs/計畫/05-執行封套與重播器.md`（重播器 claim `execution.backend.replayer-contract-parity`，正控主體存在）；計畫 17:352 已把「deterministic seed without repeat evidence」列 explicit unsupported——本條把同一態度提升為中立字彙且更嚴：repeat evidence 也只到 observed repeatability。

**地基**
- 官方：Anthropic「Even with temperature set to 0, the results will not be fully deterministic」；OpenAI seed「(mostly) deterministic」＋ `system_fingerprint` 會變——官方自己只承諾到「觀測上大致重複」，正好是 `REPEATABILITY_OBSERVED` 的強度。
- 權威：arXiv:2408.04667（10 次重跑無模型全數逐字重現）；DOI 10.1145/3697010（47.56%–75.76% 題目無任何兩次相同）；Thinking Machines batch-invariance（1000 次 80 種；batch-invariant kernel 1000/1000）——決定性的自變數在伺服器端，**只有機制層面的控制（自控 kernel／純函式）才撐得起 determinism 之名**，抽樣撐不起——這正是 R1 被駁的點，本版把它寫進能力語意。
- **兩能力的 evidence 欄位形狀：無地基，這是 nova 的拆解決定。**

**加蓋**
nova 多出來的拒絕是：repeatability evidence 冒充 determinism → 拒絕鑄名；缺能力的 claim 綁定 → 既有 `UNSUPPORTED_CAPABILITY`（01B:14）。封閉字彙加條目是動作②（namespaced、versioned、未知條目本來就 direct red）。
有沒有改到地基的介面：沒有。

**固定負控**
- control_id：`probe-upgraded-to-determinism` ／ `nth-plus-one-differs`
- faulty_subject：①把 N 次 probe evidence 直接寫成 `SEEDED_OUTPUT_DETERMINISM` supported 的 faulty capability mapper；②`假能力後端.py` 增一個前 N 次輸出逐 byte 相同、第 N+1 次改變的變體，其 evidence 記為 repeatability，faulty 檢查器據此讓要求 determinism 的綁定通過
- must_fail_exactly：①[`determinism_requires_mechanistic_evidence`]；②[`repeatability_is_not_determinism`]
- 防恆真格：計畫 05 純函式重播器以 `PURE_REPLAYER` contractual evidence 取得 `SEEDED_OUTPUT_DETERMINISM` supported——拒絕不是無條件；帶合規 N 次 probe 的後端取得 `REPEATABILITY_OBSERVED` supported

**不變式檢查**
- 檔數：Task 1 維持 8、Task 4 維持 4（上限 10）
- claim 條數：各維持 1（上限 2）
- 有 `**ClaimSpec落點:**` 行：是（01B 已遷移，不動基線）
- 有 `Expected:` 的先紅步：是（Task 4 Step 1 增列兩格 red case）
- 撞到哪一項 I1–I11：無

---

### R2-04 職責分離要比對到「人」不是字串：外部 attestation 四角色（原 R1-06）

**狀態**：PROPOSED

**相對 R1 改了什麼**
① 兩欄改四角色：`subject_changed_by`／`criterion_authored_by`／`admission_decided_by`／`evidence_executed_by`——回應 sol「`executed_by` 語意不清」：Clark–Wilson 要分離的是裁定方與**能改變受保護實體的主體**，獨立 CI 執行檢查不在禁止之列；② 最低約束改成 `admission_decided_by != subject_changed_by`；③ 比對單位從字串改成 **verifier 信任的外部 attestation 解析出的 actor**（protected CI 的 OIDC sub claim／簽章 key fingerprint／控制端准入記錄），同一 actor 掛兩個文字 id 必紅；④ 刪掉 `SELF_CERTIFIED` 標記後放行——無可信 identity source 時 admission **直接拒絕**並回 typed `UNVERIFIED_ROLE_SEPARATION`，不再靜默降級（回應「與不得靜默降級不相容」）。

**改什麼**
- 計畫：`docs/計畫/01-可執行保證語言.md`，新增 Task 17（接在 Task 16 之後）
- Create: `規格/工程/保證/准入職責分離.claim.json`（claim `engineering.admission.role-separation-attested`）
- Modify: `規格/驗收/ClaimAdmissionManifest.schema.json`（entry 增四角色欄，每欄是 `{textual_id, attestation_ref}`；attestation_ref 指向 verifier 可驗的來源）
- Modify: `架構/檢查已准入保證.py`、`架構/test_已准入保證.py`（①解析 attestation 得出 actor identity，`admission_decided_by` 與 `subject_changed_by` 解析後**不得同一 actor**；②任一角色缺可信 attestation → 該 admission entry 拒絕，typed `UNVERIFIED_ROLE_SEPARATION`；③本地無 attestation 環境下**新增** admission entry 一律紅——admission 只能經 protected merge path 完成，與交接 §十七「權威防線必須在實作者不能控制的 merge path」一致）

**為什麼**
不改的後果同 R1：Task 16 的 `engineering.admission.closure-immutable` 綠著，而同一主體既裁定准入又改 subject 時保證名義成立、實質為零（ER4 後半缺席）。R1 的錯在檢查的是兩個自填字串——本版檢查的是 attestation 解析出的 actor，同一把 key 簽兩個名字會被抓。
- 查證：`sed -n '1091,1180p' docs/計畫/01-可執行保證語言.md`（Task 16 manifest 現無任何主體欄）；`grep -rn "准入職責分離\|role-separation" docs/計畫/ 規格/` → 0 碰撞。

**地基**
- 官方：Clark–Wilson ER3 逐字「must authenticate each user attempting to execute a TP」——**身分是 SoD 的前提不是配套**，這正是本版把比對單位改成 attestation 的依據；NIST SP 800-53 AC-5／SA-8(15)（DOI 10.6028/NIST.SP.800-53r5）；SLSA v1.2 Source Track——身分與連續性由平台 attestation 承載，不由被閘者自報。
- 權威：Clark & Wilson 1987（DOI 10.1109/SP.1987.10001）ER4 後半；Saltzer & Schroeder 1975（DOI 10.1109/PROC.1975.9939）——accident／deception／breach of trust，不預設惡意；CERT 十五案——案例 5 正是**用主管帳號 check-in**：字串層面合規、身分已破，所以比對必須落在 attestation；HRU 1976（DOI 10.1145/360303.360333）——本閘做違反偵測，不做不可能性證明。

**加蓋**
nova 多出來的拒絕是：①解析後同一 actor 跨 decider/changer 兩角 → admission 紅；②無可信 attestation → `UNVERIFIED_ROLE_SEPARATION` 拒絕（fail-closed，動作①；未理解此擴充的舊元件本來就過不了 closed schema，語意單調成立）。
有沒有改到地基的介面：沒有；manifest 是 nova schema、Task 16 未實作。誠實邊界寫進 task：**信任根（哪個 CI actor／哪把 key 可信）是 repo 設定**，與 Task 16 已明寫的「CI 信任方向未閉合」同一態度，必須實測後才准宣稱閉合。

**固定負控**
- control_id：`same-actor-two-ids` ／ `decider-is-changer` ／ `no-attestation`
- faulty_subject：①同一把簽章 key（同一 OIDC sub）簽出兩個不同 textual id 分掛 decider 與 changer 的 manifest fixture；②attestation 合法但解析後同一 actor 的 entry；③四欄齊但 attestation_ref 指向不可驗來源（自填 JSON）的 entry
- must_fail_exactly：①②[`roles_resolve_to_distinct_actors`]；③[`unverified_role_separation_rejected`]
- 防恆真格：相異 attested actor、來源可驗的 entry 放行；未觸碰 manifest 的一般 commit 六道閘全綠照過

**不變式檢查**
- 檔數：4（上限 10）
- claim 條數：1（上限 2）
- 有 `**ClaimSpec落點:**` 行：是（新 task 自帶，基線不變）
- 有 `Expected:` 的先紅步：是（Step 2：今天同一 key 簽兩個名字沒有任何東西紅，Expected: FAIL）
- 撞到哪一項 I1–I11：無（Modify 的三檔由本計畫 Task 16 Create，I5 成立）

---

### R2-05 揭露帳本落地為 state owner 管的持久 aggregate（原 R1-07）

**狀態**：PROPOSED

**相對 R1 改了什麼**
① 帳本從權威層記憶體物件改成 **state owner（計畫 03）管理的持久 aggregate**：`DisclosureRecorded` 事件先 append-once commit，成功後才釋出 FeedbackPacket bytes——與計畫 06 Task 6「先 `CaseBurned` 再 reveal」**同一個已驗證形狀**；`nova/權威/判準/揭露帳本.py` 只做純 fold／決策（`allow_io=false` 不衝突），I/O 走應用層的 state owner port；② key 從 `(criterion revision, sealed case set)` 改成 `sealed_pool_lineage_id`——sealed pool 首建時鑄的內容定址 lineage id，criterion revision supersede 與 sibling／superseding Pursuit 都承繼，額度跨它們累計；③ crash gap 明講：commit 後、釋出前 crash → 重啟只可重送**同一** `disclosure_id`＋packet digest，不計新額度；commit 前 crash → 無入帳無釋出（安全方向）；at-least-once 重送不同 bytes → 紅；④ 固定負控補 sol 列的四格。

**改什麼**
- 計畫：`docs/計畫/06-判準評估與隔離回饋.md`，新增 Task 8（接在 Task 7 之後）＋ File Structure 補列
- Create: `規格/判準/DisclosureLedger.schema.json`（aggregate／事件形狀：`sealed_pool_lineage_id`、`disclosure_id`、packet digest、累計數）
- Create: `nova/權威/判準/揭露帳本.py`（純 fold：事件序列 → 剩餘額度／`DISCLOSURE_BUDGET_EXHAUSTED`）
- Create: `驗收/判準/測_揭露帳本.py`（含 SIGKILL crash matrix，形狀沿用 Task 6）
- Create: `規格/判準/保證/揭露總量有界.claim.json`（claim `criterion.disclosure.transcript-bounded`）
- Modify: `規格/判準/CriterionDefinition.schema.json`（增必填 `sealed_pool_lineage_id`）
- Modify: `規格/判準/FeedbackPolicy.schema.json`（增必填 `disclosure_cap`，事前釘）
- Modify: `nova/應用/執行判準.py`（先經 state owner append `DisclosureRecorded`，commit 成功才釋出）

**為什麼**
不改的後果同 R1：06 Task 5／6 的保證綠著，sealed 判準辨識力跨 run 靜默流失。R1 的錯在宣稱 append-only 卻沒有任何持久落點——程序重啟即洗掉 cap；本版把持久性交給已存在的 state owner，並把 key 換成洗不掉的 lineage。
- 查證：`sed -n '73,100p;303,411p' docs/計畫/06-*.md`（Task 1 Create `CriterionDefinition.schema.json` 可由同計畫後續 task Modify；Task 6 的 burn-before-reveal＋SIGKILL matrix 是現成形狀）；06 前置含 03（state owner 可用）；`grep -rn "sealed_pool_lineage" docs/計畫/ 規格/` → 0 碰撞。

**地基**
- 官方：NIST FRVT／SRE 提交限流與雙子集（實務存在、定性、不對題——照實標）。
- 權威：Dwork 等 arXiv:1506.02629 Theorem 17——**只用它支撐「有限 transcript range ⇒ 有限 max-information 上界」這個形狀**，|Y| 按整段 transcript 計、adaptive composition 下累加，所以 key 必須是跨 revision／Pursuit 的 lineage 而不是單次 run——這正是②的依據；Blum–Hardt（Ladder）——離散化本身不是保證；**cap 數值與「先記帳再釋出」的具體形狀：無地基，這是 nova 的拆解決定**（後者是 06 Task 6 既有模式的重用）。宣稱 DP／統計有效性的請求 → `UNSUPPORTED_DISCLOSURE_MECHANISM`（sol D12 與 §十九 第 7 項原話）。

**加蓋**
nova 多出來的拒絕是：超 cap 停發（verdict 照記，只斷回饋）；lineage 額度不可被 revision／sibling 洗掉；commit 前不得釋出；重送只認同 digest（動作①）。
有沒有改到地基的介面：沒有；全部是 nova 未實作 schema 與同計畫檔案的擴充。

**固定負控**
- control_id：`crash-then-reset` ／ `sibling-resets-budget` ／ `revision-resets-budget` ／ `release-before-commit` ／ `disclosure-beyond-cap`
- faulty_subject：①cap 前 SIGKILL、重啟後從零計數繼續釋出的變體；②superseding Pursuit 拿新額度的變體；③換 criterion revision、同 lineage 拿新額度的變體；④ledger commit 前就 return packet bytes 的變體；⑤cap+1 次照發的變體
- must_fail_exactly：①[`ledger_survives_restart`]；②③[`lineage_scoped_budget`]；④[`disclose_after_persist`]；⑤[`disclosure_beyond_budget_refused`]
- 防恆真格：cap 內正常 feedback 逐次照發；crash 後重送同 `disclosure_id` 同 digest 不重複扣額度；cap 滿後 verdict 記錄照常

**不變式檢查**
- 檔數：7（上限 10）
- claim 條數：1（上限 2）
- 有 `**ClaimSpec落點:**` 行：是（新 task 自帶，基線不變）
- 有 `Expected:` 的先紅步：是（Step 2：SIGKILL 重啟後今天照樣從零計數，Expected: FAIL）
- 撞到哪一項 I1–I11：無（Modify 檔全由本計畫 Task 1／5 Create，I5 成立）

---

### R2-06 06B 補上依賴身分：scipy 釘版、fingerprint 六欄、三分終態（原 R1-08）

**狀態**：PROPOSED

**相對 R1 改了什麼**
① Task 2 增 `Modify: pyproject.toml`、`Modify: uv.lock`（兩者由計畫 01 Task 1 Create，01 在 06B 前置的遞移閉包內，I1/I5 成立——已 grep 驗證）；② 統計套件**具名**：`scipy`（`scipy.stats.bootstrap`，`method="BCa"`）＋ `numpy`（seeded `Generator`）——**已實測**：scratchpad venv、CPython 3.14.7 解析到 scipy 1.18.1／numpy 2.5.2，BCa 跑得動且同 seed 兩次區間逐位相同（指令：`uv venv --python 3.14 && uv pip install scipy` ＋ 附測試腳本）；釘版落在 uv.lock 的 exact version＋hash；③ Task 1 的 `架構/目錄規則.toml` Modify 文字明寫「`nova/權威/評測/` 允許 import `scipy`／`numpy`（pure-compute 第三方依賴），依賴白名單是顯式條目」；④ analysis fingerprint 綁六欄：package name／package version／locked artifact hash／analysis function revision／parameters／analysis seed；⑤ 固定負控補 sol 三格；⑥ 終態三分事前寫死：證據不足或區間過寬 → `INCONCLUSIVE`；證據足以顯示超出 margin → `REJECTED`；protocol／pair 缺失 → `INVALIDATED`。其餘（三 task 拆分、雙端點、事前凍結、中立性）沿用 R1——sol 已認可「補完後可以通過」。

**改什麼**
- Create `docs/計畫/06B-技術效益評測.md`（`前置計畫：01 02 03 04 05 06`）＋ Modify `docs/計畫/00-總覽.md`（§3 表、§4 依賴圖、§5 Phase B）
- Task 1（8 檔）：同 R1（schemas＋machine＋admission＋claim `evaluation.technique.token-upper-quality-lower.predeclared`；`架構/目錄規則.toml` Modify 含③的白名單文字）
- Task 2（7 檔）：Create `nova/權威/評測/分析.py`、`驗收/評測/fixtures/無效技術成對樣本.json`、`驗收/評測/fixtures/省資源但品質退化.json`、`驗收/評測/測_技術效益雙端點.py`；Modify `nova/權威/評測/test_技術效益評測.py`、`pyproject.toml`、`uv.lock`。同一主 claim 由紅轉綠（落點指 Task 1 建的同一檔，I10 允許同 id 同路徑重用）
- Task 3（3 檔）：同 R1（application 薄殼＋claim `evaluation.technique.recorded-evidence-replay-deterministic`）

**為什麼**
不改的後果同 R1：控制端校正二的估算法沒有落點，「值不值得用」以點值或口頭發生。R1 的錯是把「釘版外部套件」寫成散文而沒進 Files 與 fingerprint——supply-chain 身分缺席時，「同 evidence 同結果」的重播 claim 在換套件版本時會靜默變意義。
- 查證：scipy 實測見上；`grep -n "Create: \`pyproject.toml\`\|Create: \`uv.lock\`" docs/計畫/01-可執行保證語言.md` → 122、123 行（01 Task 1 擁有，Modify 合法）；`grep -rn "評測" docs/計畫/*.md` → 0 碰撞。

**地基**
- 官方：FDA《Non-Inferiority Clinical Trials》（margin 事前、單側信賴界）；ICH E9 §3.3.2（不顯著≠等效的禁令 → `INCONCLUSIVE` 的出處）；MLPerf Inference（performance 與 accuracy 分開、閾值必過）。
- 權威：Schuirmann 1987（TOST）；Berger & Hsu 1996（IUT；1−2α 捷徑的適用邊界）；Efron 1987（BCa，DOI 10.1080/01621459.1987.10478410）；Andrews 2000——參數在邊界時 bootstrap 不一致，所以區間過寬時只能 `INCONCLUSIVE` 不能硬判。
- **臨床統計搬進軟體驗收這個動作、以及三分終態的具體切法：無地基，這是 nova 的組合契約**（照 R1 續標；M1／M2 不搬）。

**加蓋**
nova 多出來的拒絕是：事後改 endpoint → admission 紅；區間過寬 → `INCONCLUSIVE` 非通過；品質不合格不可被省 token 補償；缺 pair → `INVALIDATED`；fingerprint 缺 package 身分 → 分析拒跑（動作①）。
有沒有改到地基的介面：沒有；scipy 是釘版消費不是改寫。

**固定負控**
- control_id：`ineffective-technique` ／ `saves-but-degrades`（沿用 R1）＋ `package-swap-same-fingerprint` ／ `fingerprint-missing-package`
- faulty_subject：前兩格同 R1；③同一 EvidenceBundle 換 scipy 版本卻宣稱同一 analysis fingerprint 的變體；④fingerprint 少了 locked artifact hash 欄仍通過准入的變體
- must_fail_exactly：①[`token_ratio_upper_bound_exceeds_max`]；②[`quality_lower_bound_below_margin`]；③④[`analysis_fingerprint_covers_package`]
- 防恆真格：事前造好的「真省 30–45% 且品質非劣」配對樣本 `ACCEPTED` 且回報區間；同 bundle＋同六欄 fingerprint＋同 seed 兩次分析 result digest 相同（scratchpad 實測已示範此性質可達）

**不變式檢查**
- 檔數：Task 1＝8、Task 2＝7、Task 3＝3（上限 10）
- claim 條數：每 task 1（上限 2；全計畫恰 2 條）
- 有 `**ClaimSpec落點:**` 行：是（三 task 全帶，基線不變）
- 有 `Expected:` 的先紅步：是
- 撞到哪一項 I1–I11：無（I2/I3：前置全部編號較小；I1：pyproject.toml／uv.lock 是 Modify 不是重複 Create；I9：commit 訊息中文）

---

## 我這一輪刻意沒提的，以及為什麼

1. **新題目一律沒提**——遵指示，先把六條做對。
2. **R2-02 不另立最小版的 `EXACT_REPEAT` claim**——完整版的 join measure 把逐 byte 重複當退化案例自然涵蓋（verdict 與 bytes 都不變 ⇒ join 必不增長）；另立一條幾乎不觸發的 claim 只會虛增覆蓋面。
3. **`winner_separation` 仍只記錄、不改排序**——R1-02 的退回理由是散文 ref 與自填欄位，不是這個立場；讓 overlap 直接推翻選拔會使 Work 可能無 winner，那是另一個需要控制端裁定的終態設計，不塞進本條。
4. **R2-04 只強制 `admission_decided_by != subject_changed_by` 一條不等式**——sol 給的是「至少」；`criterion_authored_by`／`evidence_executed_by` 先記錄不強制，等第一批真實 admission 記錄累積後再提第二條不等式，避免一次鎖死到沒人能完成 bootstrap admission。
5. **DOI 查證的機制化**（「地基欄每個 DOI 附 Crossref 查證指令」寫進帳本的欄位要求）——這次兩個編號一驗一倒，教訓值得變成協定條款，但那是 `docs/決策/計畫修訂決議.md` 的協定修改，不在六條範圍，留給協調者裁定。
6. **repo 現況的 mypy 欠帳、CI 信任方向、計畫 12 遷移**——與第一輪同理由，未變。