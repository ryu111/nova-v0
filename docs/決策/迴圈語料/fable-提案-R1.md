研究語料與 repo 都查證完了。先交代三個影響提案形狀的查證結果，再給決議。

**三個前提查證**（審查者可重跑）：

- `uv run python docs/計畫複驗.py` → 21 份計畫、181 task、I1–I11 全綠、未遷移 136（已遷移：01、01B、19、20）。**注意**：用系統 `python3` 跑會在 `架構/檢查工程規範.py:251` 報 SyntaxError——那行是 PEP 758（3.14 起合法的無括號 except），必須用 `uv run`。
- 實存 claim 檔 13 份，全部屬計畫 01；01B、05–09 的 claim 檔**都還不存在**，所以下列對這些計畫的文字修改不觸碰任何已准入 ClaimSpec。
- `grep -rn "必須是 DAG\|不承載狀態\|只承載依賴" docs/計畫/*.md` → **0 命中**；`grep -rn "評測" docs/計畫/*.md` → 0；`grep -c "prompt_family" docs/計畫/08-*.md` → 3（行 24、340、354）；`grep -rn "PromptFamily" docs/計畫/*.md` → 0。

---

### R1-01 讓 `prompt_family_ref` 有內容可比：identity ref 一律內容定址

**狀態**：PROPOSED

**改什麼**
- 計畫：`docs/計畫/08-目標追求生命週期.md`，修改 Task 1（`PursuitIdentity` 的 ref 形狀）與 Task 5（identity 變更矩陣的比較依據）
- Create: `規格/追求/保證/追求機獨立宣告.claim.json`（Task 1 既有 claim `pursuit.lifecycle.independent-declared-machine` 目前**沒有任何 claim 檔落點**，一併補）
- Create: `規格/追求/保證/內容定址身分.claim.json`（新 claim `pursuit.identity.content-addressed-refs`）
- Modify: `docs/計畫/08-目標追求生命週期.md`（Task 1：`規格/追求/PursuitIdentity.schema.json` 的 ref 欄位改為 `{semantic_id, revision, digest}` 三元組；Task 5：Step 3 的 `IDENTITY_BREAKING_FIELDS` 比較改為比 digest，不比 ref 字串）
- Modify: `docs/計畫複驗.py`（`未遷移基線` 136→134：Task 1、Task 5 補 `**ClaimSpec落點:**` 行）

**為什麼**
不改的後果：08 Task 5 已編列的固定負控「prompt family 改變 → `NEW_PURSUIT_REQUIRED`」是**恆真格**——`classify_identity_change("prompt_family")` 比的是兩個字串，兩個不同 ref 指同一份 bytes 判「開新 Pursuit」、同一 ref 底下內容漂移判「同一 Pursuit」，兩種錯都不會紅（交接 §十八 待辦一）。而 21 份計畫裡 `PromptFamily` 命中 0：這個 ref 指向不存在的東西。ref 帶 digest 之後，字串相等 ⇔ 內容相等，恆真消失。
- 查證：`grep -n "prompt_family" docs/計畫/08-目標追求生命週期.md`（3 處）；`grep -rn "PromptFamily" docs/計畫/*.md`（0）；`sed -n '70,134p;321,371p' docs/計畫/08-目標追求生命週期.md`（Task 1 無 claim 檔 Create、Task 5 矩陣原文）。

**地基**
- 官方：AWS Bedrock Prompt Management——version 逐字是「a snapshot ... at a point in time」（https://docs.aws.amazon.com/bedrock/latest/userguide/prompt-management.html）；OpenAI 已公告棄用託管 prompt registry、改推 prompt 進 code 走 git history——能抄的是「版本化不可變 snapshot」語意，不是託管 registry 實作（兩層盤點 prompt 格）。
- 權威：Chen、Zaharia、Zou（arXiv:2307.09009）同名模型三個月行為漂移 84%→51%；Sclar 等（ICLR 2024，arXiv:2310.11324）格式擾動最高 76 分差——prompt 身分不綁 bytes 就不是身分。

**加蓋**
nova 多出來的拒絕是：①identity 比較收到**缺 digest 的 ref** → typed `UNRESOLVED_IDENTITY_REF` 拒絕；②digest 與 CAS bytes 不符 → typed 拒絕。
有沒有改到地基的介面：沒有。`PursuitIdentity` 是 nova 自己的 schema、尚未實作；內容定址是採用 plan 04 CAS 的既有語意。PromptFamily 的 registry／governance **不在本條**（那是順序 4–5，落點 plan 10／12，主體尚不存在）。

**固定負控**
- control_id：`identity-ref-string-compare`
- faulty_subject：把 `classify_resume_change` 改成比 ref 字串的變體，配兩份 fixture——(a) 兩個不同 semantic_id、同 digest 的 ref；(b) 同 ref、CAS bytes 已換
- must_fail_exactly：[`same_bytes_is_same_pursuit`, `digest_mismatch_rejected`]
- 防恆真格：digest 相異的合法換 prompt family → `NEW_PURSUIT_REQUIRED` 照舊成立（原矩陣不變）

**不變式檢查**
- 檔數：Task 1 由 6→8、Task 5 由 4→4（上限 10）
- claim 條數：Task 1 由 1→2、Task 5 維持 1（上限 2）
- 有 `**ClaimSpec落點:**` 行：是（兩個 task 都補，基線 −2）
- 有 `Expected:` 的先紅步：是（沿用各 task 既有先紅步，Task 5 Step 2 增列 same-bytes case FAIL）
- 撞到哪一項 I1–I11：無（新 Create 路徑 0 碰撞，已 grep；I10 基線同步調整，多了少了都會紅）

---

### R1-02 選拔分數必須帶來源與不確定度：`ScoreEvidence`

**狀態**：PROPOSED

**改什麼**
- 計畫：`docs/計畫/09-持久工作協調與選拔.md`，修改 Task 4
- Create: `規格/工作/ScoreEvidence.schema.json`
- Create: `規格/工作/保證/分數證據准入.claim.json`（新 claim `work.selection.score-evidence-admitted`）
- Modify: `docs/計畫/09-持久工作協調與選拔.md`（Task 4：`RankingSchema` 每維增 `score_source` allowlist；分數值改經 `ScoreEvidence`——`source ∈ {VERIFIER_MEASURED, EXTERNAL_ATTESTED}`（`EXECUTOR_SELF_REPORT` 不在集合內，出現即 `REJECT_CANDIDATE`）＋ `uncertainty`（`DECLARED_NEGLIGIBLE`＋justification ref，或 `HALF_WIDTH`＋level）；`SelectionRecord` 增 `winner_separation ∈ {CLEAR, OVERLAPPING}`，冠亞軍區間重疊必須記 `OVERLAPPING`——記錄，不改變 deterministic 排序本身）
- Modify: `docs/計畫複驗.py`（基線 136→135：Task 4 補落點行）

**為什麼**
不改的後果：已編列保證 `work.selection.best-before-deadline` 會綠著，同時「最佳」二字沒有語意——今天一個 LLM 吐的 `7.5` 就能進 winner comparator，沒有任何 schema 拒絕它（交接 §十八 待辦二）；且 GUM 0.1 逐字：無不確定度時量測結果「cannot be compared」。**時間窗會關**：09 一旦綠，再補就得動已准入 ClaimSpec，實作者無權。
- 查證：`sed -n '250,303p' docs/計畫/09-持久工作協調與選拔.md`（Task 4 現只有 `score_id/value_type/direction/missing`，7 檔 1 claim）；13 份實存 claim 無任何 09 的檔。

**地基**
- 官方：JCGM 100:2008（GUM）3.1.2「complete only when accompanied by a statement of the uncertainty」、0.1「cannot be compared」；JCGM 200:2012（VIM）2.9 NOTE 2——不確定度可忽略是**要記錄的判斷**不是預設（NIST TN 1297 例外條款同）；Vertex「Evaluate a judge model」——judge 分數要對 human ground truth 校準才有來源資格。
- 權威：Goldstein & Spiegelhalter（JRSS-A 1996，DOI 10.1111/j.1467-985X.1996.tb00086.x）——名次的 95% 區間可橫跨 20 名，帶不確定度排序才有意義；Goel 等（arXiv:2502.04313）judge 與被評模型相似度 r=0.84——自報與同源分數不是獨立證據。

**加蓋**
nova 多出來的拒絕是：無 `ScoreEvidence` 的裸數字、`EXECUTOR_SELF_REPORT` 來源、缺 uncertainty 聲明，一律 `REJECT_CANDIDATE`。這與計畫 01 Task 10 已落地的 `UNTRUSTED_OBSERVATION`（自報觀察連編都編不出 plan）同一形狀。
有沒有改到地基的介面：沒有。comparator 仍是 deterministic（點值排序＋digest tie-break 不變）；加的是准入拒絕與一個記錄欄位。JCGM 適用範圍是物理量，搬到分數上是超譯風險——本條**只搬「無不確定度不得比較」的拒絕**，不宣稱 GUM 背書整套選拔，此界線寫進 task 文字。

**固定負控**
- control_id：`naked-llm-score`
- faulty_subject：fixture 候選帶 `source=EXECUTOR_SELF_REPORT` 的 `7.5`，以及一組冠亞軍區間重疊但 `winner_separation=CLEAR` 的假 SelectionRecord
- must_fail_exactly：[`self_reported_score_rejected`, `overlap_must_be_recorded`]
- 防恆真格：`VERIFIER_MEASURED`＋`DECLARED_NEGLIGIBLE`（有 justification ref）的分數照常參賽並選出同一 winner——原 claim 的 permutation property 不變

**不變式檢查**
- 檔數：Task 4 由 7→9（上限 10）
- claim 條數：1→2（上限 2）
- 有 `**ClaimSpec落點:**` 行：是（兩個 id 各對一檔，基線 −1）
- 有 `Expected:` 的先紅步：是（Step 2 增列 naked-score case，Expected: FAIL）
- 撞到哪一項 I1–I11：無

---

### R1-03 上限是耗盡不是活性：`bounded-liveness` 改名 `bounded-exhaustion`

**狀態**：PROPOSED

**改什麼**
- 計畫：`docs/計畫/08-目標追求生命週期.md`，修改行 28 的 Architecture 敘述與 Task 2
- Modify: `docs/計畫/08-目標追求生命週期.md`（①行 28「liveness measure」改稱「耗盡量測」，並加一句：**命中上限是偵測（typed `EXHAUSTED`），不是進展證明**；②行 149、182 的 claim id `pursuit.retry.bounded-liveness` → `pursuit.retry.bounded-exhaustion`；claim 檔名 `有界反覆.claim.json` 不動）
- Modify: `docs/計畫複驗.py`（基線 136→135：Task 2 補落點行）

**為什麼**
不改的後果：帳上會有一條名叫 liveness 的綠 claim，而它的 oracle 只驗 safety（第 17 次被擋、deadline 不可延、第 129 次 call 被擋）——兩層盤點 termination 格的裁決逐字：把固定迭代上限當終止見證「不是缺一塊，是**多了一個假保證**」。judge 不動、負控不動、什麼算綠不動；動的只是宣稱名，讓宣稱降到 oracle 實際證明的強度。
- 查證：`grep -n "bounded-liveness" docs/計畫/08-*.md` → 僅 149、182 兩處；`docs/決策/sol-新局-*.md` 另有歷史引用，是討論記錄不改。Task 2 三格負控全是邊界檢查，無任何進展判準。

**地基**
- 官方：官方層查不到「無進展偵測」——AWS Builders' Library／RFC 8961 給的全是 safety（timeout、bounded retry、backoff cap）。
- 權威：Lamport 1977（DOI 10.1109/TSE.1977.229904）與 Alpern–Schneider 1985（Info. Proc. Letters，safety ∩ liveness）——只寫得出 safety 的規格是**留白**不是完備；Holzmann Power of Ten Rule 2 與 JPL D-60411：上限要靜態可證，**超限路徑是 assertion failure（偵測）**，不是證明；Biere 等 1999（BMC）：有界展開是找 bug 的正解，不是證明沒 bug 的正解。

**加蓋**
nova 多出來的拒絕是：無（本條不加能力也不加拒絕，是把一條宣稱的名字縮到證據撐得住的範圍）。
有沒有改到地基的介面：沒有；claim 尚未有檔、尚未准入，判準與負控一字不動。

**固定負控**
- control_id：沿用 Task 2 既有三格（`17th-execution`／`deadline-extended-after-pause`／`129th-paid-call`），不新增
- faulty_subject：同原文
- must_fail_exactly：同原文（三者必須在建立 Execution 前 terminal/reject）
- 防恆真格：16 次以內的正常 retry 不被拒（原 property test 不變）

**不變式檢查**
- 檔數：Task 2 維持 6（上限 10）
- claim 條數：維持 1（上限 2）
- 有 `**ClaimSpec落點:**` 行：是（補上，基線 −1）
- 有 `Expected:` 的先紅步：是（原 Step 2 不變）
- 撞到哪一項 I1–I11：無（id 改名後宣告行與落點行同步，I10 要求兩行逐字相等，抄錯自己會紅）

---

### R1-04 停滯要有型別：連續無進展的 retry 必須 typed 終止，不是燒完 16 次

**狀態**：PROPOSED

**改什麼**
- 計畫：`docs/計畫/08-目標追求生命週期.md`，新增 Task 8（接在 Task 7 之後）
- Create: `驗收/追求/測_無進展終態.py`
- Create: `規格/追求/保證/停滯有型別終態.claim.json`（claim `pursuit.retry.no-progress-typed`）
- Modify: `規格/追求/AttemptPolicy.schema.json`（增 `max_stagnant_attempts`，事前釘、必須 < `max_executions`，預設 2）
- Modify: `規格/追求/追求.machine.json`、`nova/領域/追求/模型.py`（`POLICY_STOP` 的封閉 reason enum 增 `NO_PROGRESS`；不動 terminal union 本身）
- Modify: `nova/領域/追求/決策.py`、`nova/領域/追求/test_追求決策.py`
- 判準：連續 N 次 attempt 的 `(candidate_bundle_digest, feedback_packet_digest)` 完全相同 → 第 N+1 次 `StartExecution` 被拒，Pursuit 進 `POLICY_STOP(NO_PROGRESS)`

**為什麼**
不改的後果：R1-03 改名後，「進展」在整套計畫裡仍然是空的——一個 Pursuit 可以連續 16 次產出逐 byte 相同的候選與相同的 feedback，帳面顯示為井然有序的 `EXHAUSTED`，燒掉 16 份 attempt 預算，而沒有任何一格紅過。這正是交接 §十七 能力排序第 10 項（核心、路徑 A、最晚裁定點「plan 08 retry 狀態機實作前」——08 未實作，窗還開著）。判準用 digest 而非「分數沒變好」：隨機後端合法重取樣時 candidate digest 會變，不會被誤殺。
- 查證：`grep -n "progress\|進展\|停滯" docs/計畫/08-*.md` → 0 命中；08:26 已定義 retry 輸入三元組（checkpoint＋FeedbackPacket ref＋selection），本 task 消費它，不新發明。

**地基**
- 官方：官方層查不到（同 R1-03——AWS／RFC 只有 safety 面）。
- 權威：SPIN 的 non-progress cycle detection（Holzmann《The SPIN Model Checker》，progress label＋`<>[] np_`）——「無進展」的標準工具化形狀就是**偵測具名的無進展環**；Podelski–Rybalchenko 2004（LICS，DOI 10.1109/LICS.2004.1319598）——單一全域遞減量不是一般解。**「連續 N 次 digest 不變」這個具體判準兩層都引不出來：無地基，這是 nova 的拆解決定**（權威層只證成「進展必須被定義且被偵測」）。

**加蓋**
nova 多出來的拒絕是：第 N+1 次停滯 attempt 的 `StartExecution` 被拒。這是合法動作①（對既有 retry 能力增加拒絕）。
有沒有改到地基的介面：沒有；`AttemptPolicy` 是 nova schema、未實作，加欄位是計畫文字修改；reason enum 是封閉 enum 的計畫期擴充。

**固定負控**
- control_id：`third-stagnant-attempt`
- faulty_subject：假 scheduler 在兩次相同 `(candidate_digest, feedback_digest)` 後仍建第三次 Execution
- must_fail_exactly：[`stagnant_attempt_refused`, `terminal_reason_no_progress`]
- 防恆真格：candidate digest 每次不同的隨機後端跑滿 16 次不被 `NO_PROGRESS` 誤殺（fake backend 每 attempt 換 bytes）

**不變式檢查**
- 檔數：7（上限 10）
- claim 條數：1（上限 2）
- 有 `**ClaimSpec落點:**` 行：是（新 task 自帶，基線不變）
- 有 `Expected:` 的先紅步：是（Step 2：第三次停滯 attempt 今天照樣開跑，Expected: FAIL）
- 撞到哪一項 I1–I11：無（新 task Modify 的檔全由本計畫 Task 1、2 Create，I5 成立；恰 1 commit 步）

---

### R1-05 輸出決定性降級成 typed 能力：`SEEDED_REQUEST` 與 `SEEDED_OUTPUT_DETERMINISM`

**狀態**：PROPOSED

**改什麼**
- 計畫：`docs/計畫/01B-執行者能力契約與SDK探針.md`，修改 Task 1 與 Task 4
- Modify: `docs/計畫/01B-執行者能力契約與SDK探針.md`（①Task 1：capability 封閉字彙增兩個獨立條目 `SEEDED_REQUEST`（可送 seed）與 `SEEDED_OUTPUT_DETERMINISM`（同 request 逐 byte 同輸出），後者**預設 unsupported**；②Task 4：`SEEDED_OUTPUT_DETERMINISM` 的 `CapabilityEvidence` 必須含同 request N 次重複實測逐 byte 相同的 probe evidence，缺者維持 unsupported；③總覽段落加入四層界線表：spec→plan 編譯必須決定性／live invocation→response **不要求**／已完成 run→EvidenceBundle 必須 immutable／同 bundle→分析結果必須決定性——並明寫**「不可重播」不得靜默變成「可以不重播」：錄製義務不因後端非決定而免除**）

**為什麼**
不改的後果：01B 的 `execution.backend-capability.closed-vocabulary` 會綠著，同時「輸出決定性」這個能力**沒有 typed 的家**——未來任何一條想綁「兩次同輸入同 digest」的 claim，要嘛編不出來（好的 fail-closed，但是副作用不是設計），要嘛有人拿 seed 冒充決定性而沒有任何格會紅。兩層盤點 determinism 格的裁決：公開託管 API 上逐 byte 同輸入**不保證**逐 token 同輸出，這是廠商自己聲明的既成事實，宣稱必須降級成 typed 能力查詢。計畫 17:352 已把「deterministic seed without repeat evidence」列 explicit unsupported——本條把同一規則從單一後端提升到 01B 的中立字彙，讓五個後端計畫共用。
- 查證：`grep -rn "SEEDED\|OUTPUT_DETERMINISM" docs/計畫/*.md` → 0；`sed -n '58,95p;164,196p' docs/計畫/01B-*.md`（Task 1 字彙現只有三項；Task 4 evidence 綁 fingerprint/TTL）；`grep -n "seed" docs/計畫/17-*.md`（352、356 行既有規則）。

**地基**
- 官方：Anthropic 官方逐字「Even with temperature set to 0, the results will not be fully deterministic」（https://docs.anthropic.com/en/api/messages）；OpenAI seed 只給「(mostly) deterministic」且 `system_fingerprint` 會因服務端改動而變。
- 權威：arXiv:2408.04667（10 次重跑無任何模型全數逐字重現）；DOI 10.1145/3697010（47.56%–75.76% 的題目沒有任何兩次輸出相同）；Thinking Machines batch-invariance 實測（同 prompt 1000 次 80 種輸出；batch-invariant kernel 可做到 1000/1000，代價 +60% 延遲）——不決定性的自變數是伺服器端 batch 與規約順序，呼叫端無權控制，所以這**必須**是後端逐一舉證的能力，不是公理。

**加蓋**
nova 多出來的拒絕是：自報 `SEEDED_OUTPUT_DETERMINISM` 而無重複實測 evidence → 該能力維持 unsupported；任何 claim 綁定要求此能力而 offer 缺它 → 既有規則（01B:14）自動 `UNSUPPORTED_CAPABILITY`。這是合法動作②：經已宣告、封閉、具版本的 capability 字彙擴充新能力，舊元件對未知 capability 本來就 direct red（Task 1 既有負控）。
有沒有改到地基的介面：沒有；字彙是 nova 的封閉 enum，計畫未實作。

**固定負控**
- control_id：`self-reported-determinism`
- faulty_subject：`驗收/執行者能力/fixtures/假能力後端.py` 增一個宣告 `SEEDED_OUTPUT_DETERMINISM` 但 evidence 只有單次 probe 的變體
- must_fail_exactly：[`determinism_requires_repeat_evidence`]
- 防恆真格：帶 N 次逐 byte 相同 probe evidence（如本地 batch-invariant 引擎）的後端，該能力判 supported——拒絕不是無條件的

**不變式檢查**
- 檔數：Task 1 維持 8、Task 4 維持 4（上限 10）
- claim 條數：兩 task 各維持 1（上限 2）
- 有 `**ClaimSpec落點:**` 行：是（01B 已遷移，既有行不動，基線不變）
- 有 `Expected:` 的先紅步：是（沿用各 task 既有先紅步，Task 4 Step 1 增列 repeat-evidence case）
- 撞到哪一項 I1–I11：無

---

### R1-06 ER4 的後半：認證者與執行者不得同一

**狀態**：PROPOSED

**改什麼**
- 計畫：`docs/計畫/01-可執行保證語言.md`，新增 Task 17（接在 Task 16 之後）
- Create: `規格/工程/保證/認證與執行分離.claim.json`（claim `engineering.admission.certifier-not-executor`）
- Modify: `規格/驗收/ClaimAdmissionManifest.schema.json`（每個 entry 增 `certified_by`、`executed_by`、`identity_source` 三欄，closed schema）
- Modify: `架構/檢查已准入保證.py`、`架構/test_已准入保證.py`（admission 檢查 `certified_by != executed_by`；`identity_source` 為單一可偽造來源時該 entry 標 `SELF_CERTIFIED` 降級並在報告顯示，不靜默）

**為什麼**
不改的後果：Task 16 的 `engineering.admission.closure-immutable` 會綠著——manifest 與 digest 都對——但當同一主體既認證判準又寫實作時，這條保證名義成立、實質為零：Clark–Wilson ER4 是雙向的，nova 現行條文只有前半（「實作者不能改已准入 ClaimSpec」限制的是**改動**），後半（認證方不得持有該對象的**執行權**）沒有任何機制對應（兩層盤點 SoD 格：缺的那塊「剛好是 nova 現行條文的鏡像盲點」）。CERT 十五案全部倒在「工具不強制第二人」或「日誌沒人看」——所以本條做成會紅的閘，不是文件。
- 查證：`sed -n '1091,1180p' docs/計畫/01-可執行保證語言.md`（Task 16 現行 manifest 無任何主體欄位）；`grep -rn "certifier\|認證與執行" docs/計畫/*.md` → 0。

**地基**
- 官方：NIST SP 800-53 Rev.5 AC-5（Separation of Duties）與 SA-8(15)（DOI 10.6028/NIST.SP.800-53r5）——官方自註出處指回 Saltzer 1975；NIST SP 800-218 SSDF PS.1。注意官方全是 organization-defined／opt-in：**照抄官方預設值不會得到職責分離**，這句要寫進 task。
- 權威：Clark & Wilson 1987（DOI 10.1109/SP.1987.10001）ER4 逐字「No certifier of a TP ... may ever have execute permission with respect to that entity」；Saltzer & Schroeder 1975（DOI 10.1109/PROC.1975.9939）——accident／deception／breach of trust 三重理由，**不必預設執行者有惡意**；HRU 1976（DOI 10.1145/360303.360333）與 Li et al. 2007（DOI 10.1145/1237500.1237501）——閘的正確形狀是**違反偵測＋降級**，不是不可能性證明。

**加蓋**
nova 多出來的拒絕是：manifest entry `certified_by == executed_by` → admission 紅；`identity_source` 可偽造 → 降級標示（合法動作①）。誠實邊界寫進 task：ER3 先於 ER4——身分由同 UID 自填時本閘只能**偵測與降級**，不能證明分離；這與 Task 16 已明寫的「CI 信任方向未閉合」同一態度。
有沒有改到地基的介面：沒有；manifest 是 nova 自己的 schema、Task 16 未實作。

**固定負控**
- control_id：`certifier-is-executor`
- faulty_subject：manifest fixture 中一個 entry 的 `certified_by` 與 `executed_by` 填同一 id
- must_fail_exactly：[`certifier_executor_distinct`]
- 防恆真格：相異主體、欄位齊全的 manifest，六道閘全綠時本閘放行（沿用 Task 16 防恆真格的形狀）

**不變式檢查**
- 檔數：4（上限 10）
- claim 條數：1（上限 2）
- 有 `**ClaimSpec落點:**` 行：是（基線不變）
- 有 `Expected:` 的先紅步：是（Step 2：今天同一 id 填兩欄沒有任何東西紅，Expected: FAIL）
- 撞到哪一項 I1–I11：無（Modify 的三個檔皆由本計畫 Task 16 Create，I5 成立）

---

### R1-07 封存回饋的累積揭露要有帳：有限 transcript 上限，不冒稱 DP

**狀態**：PROPOSED

**改什麼**
- 計畫：`docs/計畫/06-判準評估與隔離回饋.md`，新增 Task 8（接在 Task 7 之後）＋ File Structure 補列
- Create: `規格/判準/DisclosureLedger.schema.json`
- Create: `nova/權威/判準/揭露帳本.py`
- Create: `驗收/判準/測_揭露帳本.py`
- Create: `規格/判準/保證/揭露總量有界.claim.json`（claim `criterion.disclosure.transcript-bounded`）
- Modify: `nova/應用/執行判準.py`、`規格/判準/FeedbackPolicy.schema.json`（policy 增 `disclosure_cap`，事前釘）
- 機制：每個 `(criterion revision, sealed case set)` 維持 append-only transcript，Task 5 的 FeedbackPacket 是有限 enum（`OutcomeClass`×`LocationBucket`×`Retryability`），每次釋出記一筆；超過 cap → feedback 停發、回 typed `DISCLOSURE_BUDGET_EXHAUSTED`（verdict 照記，只斷回饋）；任何宣稱 DP／reusable-holdout 統計保證的請求 → `UNSUPPORTED_DISCLOSURE_MECHANISM`

**為什麼**
不改的後果：06 Task 5／6 的兩條保證（`criterion.feedback.clause-level-reduced`、`criterion.sealed-case.reveal-burns-before-release`）會綠著，同時 sealed 判準的辨識力**跨 run 靜默流失**——單次 feedback 縮減得再好，適應性重複評估的累積資訊量沒有任何東西在數。兩層盤點 holdout 格：官方層（FRVT 限流、GMLP 獨立性）全是定性、不觸及時間維度；可計算的上界全在權威層。Ladder 的教訓要寫進 task：對提交數只有 log 依賴靠的是「回饋很少改變」，不是「回饋離散」——離散化本身不是保證。
- 查證：`sed -n '303,411p' docs/計畫/06-*.md`（Task 5 enum 三元組、Task 6 揭露即燒掉；兩者都沒有跨 run 計量）；`grep -rn "disclosure\|揭露帳" docs/計畫/*.md` → 僅 Task 6 的單次燒毀。

**地基**
- 官方：NIST FRVT／SRE 的提交限流與 progress/test 雙子集（實務存在，定性；兩層盤點註明「存在但不對題」）。
- 權威：Dwork 等 arXiv:1506.02629 Theorem 17——I∞^β ≤ log(|Y|/β)，|Y| 按**整段 transcript** 計，對任意資料分布成立、不要求機制隨機化——這正是「有限 enum 回饋＋有限次數」上界的形狀；Blum–Hardt（Ladder）與 Russo–Zou 補失效條件。**具體 cap 數值兩層都給不出：無地基，這是 nova 的拆解決定**（權威層只背書「上界隨 transcript 取值總數的 log 成長」這個形狀）。

**加蓋**
nova 多出來的拒絕是：①超過 cap 停發 feedback（動作①）；②冒稱統計保證 → `UNSUPPORTED_DISCLOSURE_MECHANISM`（sol 第三輪 D12 原話：cap 可以是安全政策，「不能宣稱它保持某個顯著水準」；§十九 第 7 項作者原話同）。
有沒有改到地基的介面：沒有；FeedbackPolicy 是 nova schema、06 未實作。

**固定負控**
- control_id：`disclosure-beyond-cap`
- faulty_subject：faulty policy `disclosure_cap` 缺失（或 ∞），配一段跑到第 cap+1 次仍發出 FeedbackPacket 的執行
- must_fail_exactly：[`cap_predeclared_required`, `disclosure_beyond_budget_refused`]
- 防恆真格：cap 內的正常 feedback 逐次照發，且 verdict 記錄在 cap 後仍照常（斷的是回饋不是裁定）

**不變式檢查**
- 檔數：6（上限 10）
- claim 條數：1（上限 2）
- 有 `**ClaimSpec落點:**` 行：是（基線不變）
- 有 `Expected:` 的先紅步：是（Step 2：第 cap+1 次 feedback 今天照發，Expected: FAIL）
- 撞到哪一項 I1–I11：無（Modify 的兩檔由本計畫 Task 5／既有 task Create，I5 成立；File Structure 新列檔案皆有 Create，I7 成立）

---

### R1-08 新開計畫 06B-技術效益評測：雙端點、事前凍結、區間夠窄才算答案

**狀態**：PROPOSED

**改什麼**
- 計畫：Create `docs/計畫/06B-技術效益評測.md`（新計畫，3 個 task；`前置計畫：01 02 03 04 05 06`）＋ Modify `docs/計畫/00-總覽.md`（§3 子系統表、§4 依賴圖、§5 Phase B 各補一行）
- Task 1（宣告與准入，8 檔）：Create `規格/評測/TechniqueExperimentSpec.schema.json`、`規格/評測/TechniqueExperimentResult.schema.json`、`規格/評測/技術效益評測.machine.json`、`規格/評測/保證/技術效益雙端點事前凍結.claim.json`、`nova/權威/評測/模型.py`、`nova/權威/評測/准入.py`、`nova/權威/評測/test_技術效益評測.py`；Modify `架構/目錄規則.toml`。claim `evaluation.technique.token-upper-quality-lower.predeclared`。spec 事前釘：配對（同 case 同 replicate block、block randomization）、`max_token_ratio`（上界端點）、`noninferiority_margin`＋`minimum_absolute_quality`（相對 margin＋絕對下限）、`max_interval_width`（「省 0–90%」不是答案）、樣本數由事前效果量算出、`missing_pair=REJECT_RUN`。admission 拒絕看到資料後改任何端點。
- Task 2（決定性分析器與統計負控，5 檔）：Create `nova/權威/評測/分析.py`、`驗收/評測/fixtures/無效技術成對樣本.json`、`驗收/評測/fixtures/省資源但品質退化.json`、`驗收/評測/測_技術效益雙端點.py`；Modify `nova/權威/評測/test_技術效益評測.py`。同一 claim id 由紅轉綠（落點指 Task 1 建的同一檔，I10 允許同 id 同路徑重用——交接 §十四 第 2 點）。統計實作**釘版外部套件**，package/version/digest 進 analysis fingerprint，nova 不重寫 bootstrap／CI 演算法（sol F3）。p 值不顯著 → typed `INCONCLUSIVE`，不是通過。
- Task 3（application 薄殼與重播，3 檔）：Create `nova/應用/執行技術效益評測.py`、`nova/應用/test_執行技術效益評測.py`、`規格/評測/保證/隨機實驗證據重播一致.claim.json`。claim `evaluation.technique.recorded-evidence-replay-deterministic`：同一 sealed EvidenceBundle＋同 analysis digest＋同 analysis seed → 同 interval、同 decision、同 result digest；`rerun_model` 是新 `MeasurementRun` 不是 replay，不覆寫舊 run。

**為什麼**
不改的後果：控制端校正二的新需求（「某技術真的省 token 且品質不低於門檻」的估算法）沒有落點，於是「值不值得用」的判斷會以點值、以 plan 07 的金額帳、或以任何人的一句話發生——而那三者都沒有驗收權。它不進 07（07 管「能不能花」）、不進 06（06 管「單一候選合不合判準」）、不進 09（09 管「合法分數怎麼選 winner」）：它有自己的生命週期 `DRAFT→DESIGN_FROZEN→RUNNING→EVIDENCE_SEALED→ANALYZED→ACCEPTED|REJECTED|INCONCLUSIVE|INVALIDATED`。
- 查證：`grep -rn "評測" docs/計畫/*.md` → 0（namespace 無碰撞）；`grep -n "值得\|價值" docs/計畫/07-*.md` → 0（07 本來就沒管這件事，sol「07 退回」是 ALREADY_TRUE，故本條**不動 07**）；06B 依賴 05 的 `UsageEvidence`（01B Create、經 05 正規化），06→05→01B 在遞移閉包內，I5 成立。

**地基**
- 官方：FDA《Non-Inferiority Clinical Trials》（https://www.fda.gov/media/78504/download）——margin 事前選定、單側信賴界判定；ICH E9 §3.3.2 逐字禁令「以不顯著推等效 inappropriate」；MLPerf Inference（https://docs.mlcommons.org/inference/）——performance 與 accuracy 分開測、accuracy threshold 必過，速度不能補償品質。
- 權威：Schuirmann 1987（TOST，DOI 10.1007/BF01068419）；Berger & Hsu 1996（IUT，1−2α 捷徑只對 TOST 成立）；Lakens 等 2018（DOI 10.1177/2515245918770963）；Madaan 等同設定重跑波動（<1pp 的「改善」與雜訊不可區分）。**誠實標記：整套統計出自臨床法規，搬進軟體驗收這個動作本身兩層都引不出——是 nova 的組合契約**（兩層盤點 non-inferiority 格裁決），FDA 的 M1/M2 推導**不搬**（nova 沒有安慰劑與歷史試驗的對應物）。

**加蓋**
nova 多出來的拒絕是：事後改 margin／endpoint → admission 紅；區間過寬 → `INCONCLUSIVE` 不是通過；品質退化不能被省 token 補償（intersection-union，兩端點 AND）；缺 pair → `INVALIDATED` 不是剔除難看樣本；宣稱 live 模型輸出可重播 → 不在本計畫射程（重播只及 sealed evidence，與 R1-05 四層界線一致）。
有沒有改到地基的介面：沒有；全部是新 namespace。中立性：spec 內零產品名詞，benchmark set 是 content-addressed ref。

**固定負控**
- control_id：`ineffective-technique`＋`saves-but-degrades`（兩格，sol 第三輪 A 段原形）
- faulty_subject：fixture「無效技術」（treatment 與 baseline token 同分布、品質可相同）；fixture「省 token 但品質差超過 margin」
- must_fail_exactly：前者 [`token_ratio_upper_bound_exceeds_max`]；後者 [`quality_lower_bound_below_margin`]——兩格各殺一條 predicate，證明兩端點都有牙且不能互相補償
- 防恆真格：一組事前造好的「真省 30–45% 且品質非劣」配對樣本必須 `ACCEPTED`，且回報的是區間不是點值

**不變式檢查**
- 檔數：Task 1＝8、Task 2＝5、Task 3＝3（上限 10）
- claim 條數：每 task 1（上限 2；全計畫恰 2 條，符合 sol 建議）
- 有 `**ClaimSpec落點:**` 行：是（三個 task 全帶，新計畫不動基線）
- 有 `Expected:` 的先紅步：是（每 task 都有）
- 撞到哪一項 I1–I11：無（I2/I3：06B 前置全部編號較小、`序位("06B")` 介於 06 與 07；I1：Create 路徑 0 碰撞已 grep；I9：commit 訊息中文）

---

## 我這一輪刻意沒提的，以及為什麼

1. **「graph 壓成 DAG」「edge 不承載狀態」的計畫修正**——sol 判錯誤抽象，但 `grep -rn "必須是 DAG\|不承載狀態\|只承載依賴" docs/計畫/*.md` 是 **0 命中**：錯誤抽象只存在於交接與作者四輪的歷史敘述，§十九已記入降級清單；09:7 的「禁止 arbitrary DAG edge」限定的是 Work 父子排程拓撲這一種圖，屬合法加蓋。提了就是 `ALREADY_TRUE`。
2. **plan 07 從「技術價值判定」退回**——07 文字本來就沒有這件事（grep 0），sol 的裁決已經是現況。06B 開出來後分工自然成立。
3. **ClaimSpec `observations` 帶不確定度（0.3.0 升版）**——`規格/語言/ClaimSpec.schema.json` 已實作、13 份 claim 實存，`claimspec_version` enum 是 `["0.2.0"]`；動它是對已採用介面的變更，必須走版本化擴充點與 RequirementChange，不是本迴圈的計畫文字修改。今天 observations 承載的是 exact typed 值（exit code、event count、terminal state），VIM 2.9 NOTE 2 的「可忽略」例外成立；本輪先把不確定度義務放在兩個尚未實作的比較權威（R1-02、R1-08）。
4. **PromptFamily governance 與 PromptPlan 完整前綴**（§十九 順序 4、5）——落點主體（plan 10 snapshot resolve、plan 12 Task 7）尚未實作，時間窗未關；本輪只補會讓**已編列負控恆真**的最小內容身分（R1-01）。
5. **Visual evaluator protocol**（順序 9）——sol 中立化表格已給形狀，落點在 06 isolation 後；等計畫 06 遷移批次一併，不單獨動。
6. **mypy 欠帳一**——落點待控制端指派，且作者明講 49 個基線 error 不能直接接 required gate；先動會逼第一個實作者清無關的債。
7. **CI 信任方向閉合（ruleset workflows 指定另一 repo/ref）**——這是 repo 設定與實測動作，不是計畫文字；Task 16 已誠實寫「未閉合、實測後才准宣稱成立」。由控制端執行設定並實測後，才改那一段字。
8. **計畫 12 的遷移與 T4 拆分**（§十四 欠帳 4）——屬遷移批次工作，作者已給修復規則，與本輪的保證缺口無關。

另兩件帳務注意：八條中有四條會把未遷移 task 補上落點行（R1-01 兩個、R1-02 一個、R1-03 一個），`docs/計畫複驗.py` 的 `未遷移基線` 須在 APPLIED 時按實際合併結果一次調整（136→132 若全過）——I10 兩個方向都會紅，抄錯基線閘自己會抓；R1-03 與 R1-04 有文字相依（改名後的敘述被 R1-04 引用），若 R1-03 被退回，R1-04 的行 28 引文需回退為原名，機制本身不受影響。