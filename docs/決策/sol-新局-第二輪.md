# 新局第二輪：補上知識權威，裁掉 Pursuit 分歧，讓第一條保證真的轉紅

## 0. 隔離聲明與總判決

【查證】本輪只讀了[架構草案](./架構草案.md)、[第一輪](./sol-新局-第一輪.md)與允許的[五學科研究](../設計/五學科/)；沒有讀取既有實作、既有測試、交接、其他設計文件或遷移筆記。（來源：本輪工具讀取紀錄與題目禁令。）

【查證】因為遷移筆記目錄本輪明禁讀取，我不能查證四份文件是否真的全數移入、README 寫了什麼、或內容是否被修改。（來源：本輪題目禁令。）

【推論】「整批移出、不修補、不准新設計引用」這個處置本身是對的；修補會保留舊名詞到新名詞的映射，下一輪仍會沿舊問題切邊界。但這是對你回報之處置原則的判斷，不是對目錄現況的驗證。

【推論】本輪五個結論：

- 【推論】八個權威到三層的對應大致成立，但不是「完全正確」：定義與評估可以同屬判準面，寫入權卻不可合併；證據庫也不能只剩 blob CAS；「分歧的唯一來源」目前沒有證據。
- 【推論】跨工作知識是第四個橫向權威面：知識治理面。它擁有 KnowledgeAssertion 的准入、過期、撤銷與溯源；工作只綁定知識快照，不能擁有或複製知識真相。
- 【推論】產品需求已經命中拆分判準。正確基數是 Work 1→N Pursuit 1→N Execution；第一版即使只排程一個 Pursuit，也應先把資料邊界拆開。
- 【推論】workload envelope 不是等生產量測。先由需求與設計訂出可接受區域，再用合成壓力與 crash 試驗驗證儲存候選。架構草案「裁定前必須先量」這句要改。
- 【推論】同 UID 的普通分程序不是惡意程式的安全邊界。第一版可明講只防無意洩漏，但 ClaimSpec 必須宣告 isolation capabilities；宿主能力不足時是 UNSUPPORTED_ISOLATION，不得靜默降級。

【查證】本輪題目把「跨工作知識」稱為性質 7；第一輪題目中的性質 7 則是外部副作用交易邊界。（來源：兩輪題目原文。）

【推論】後續不可再用「性質 7」當永久識別碼。ClaimSpec 應使用 execution.wall_limit.external、knowledge.provenance.revocable、effect.delivery.at_least_once 這種語義 id；章節編號只能是 source locator。

---

## 1. Q1：對應逐條檢查，知識歸哪

### 1.1 先糾正《架構草案》的證據強度

【查證】[架構草案第三節](./架構草案.md)逐條收錄了穩定身分／封閉終態、不可下推保證、組合下一層生命週期、權威恢復責任；這部分沒有把四條改寫走樣。

【查證】[架構草案第二節](./架構草案.md)把兩份推導的差異寫成「分歧的來源是一條資格判準」，理由是來源 A 沒有「組合下一層多個生命週期」這一條。

【推論】這最多證明「第三條足以讓八個群組投影到三層與橫向面」，不能證明它是唯一差異。來源 A 的原文現在位於禁讀目錄；在不能檢查它如何處理「不可下推保證」與「權威恢復責任」時，寫「唯一」是越權。

【推論】正確措辭應是：「目前已識別、且足以解釋層數差異的判準是第三條；是否唯一，未查證。」收斂不是同義，投影後看起來一樣也不證明原始權責完全等價。

### 1.2 上表逐條判決

| 來源 A 的權威 | 你的對應 | 判決 |
|---|---|---|
| 執行權威 | 第一層：執行封套 | 【推論】對。更精確地說，執行封套是生命週期層，執行權威是本層唯一可寫 Execution 終態的 supervisor；executor backend 只能回報 observation，不能寫終態。 |
| 作業權威 | 第三層：持久工作協調 | 【推論】方向對，但目前少了 Q2 將確認的 Pursuit。作業權威擁有 Work 的總目標、portfolio、依賴、全域停止與最終選擇；它不能再直接擁有每一輪 attempt。 |
| 定義權威＋評估權威 | 橫向：判準裁定面 | 【推論】幾何位置對，權限合併錯。Definition Authority 寫 CriterionVersion；Evaluation Authority 只能對 candidate digest × criterion version 產生 Verdict。評估者若能改定義，就可在看過答案後移球門。 |
| 資源權威 | 橫向：預算核銷面 | 【推論】對，但名稱應改為「資源准入與核銷面」。只有事後記帳不能形成硬上限；每個花費點必須先 reserve，再 settle／release。 |
| 生效權威 | 橫向：效果交付面 | 【推論】大致對。必須再分「誰原子寫入 effect intent」與「誰對外 relay」；relay 不能憑空發明意圖，Work 交易也不能把 sent 當作已在外部生效。 |
| 證據庫 | 內容定址儲存，不在組合軸上 | 【推論】只對一半。blob 本體確實是 CAS／Payload Vault；EvidenceRecord 的 producer、觀察方法、時間、criterion／candidate digest、保留與可見性仍要有 append-only 索引。CAS 證明位元組相同，不證明位元組可採信。 |
| 知識權威 | 未對應 | 【推論】不能塞回 Work，也不是 CAS；它是第四個橫向權威面「知識治理面」。 |

【推論】因此「三層＋三控制面」要修成「三層＋四個橫向權威面＋內容定址基礎設施」。若堅持 control plane 只指能准／拒動作的東西，知識面應叫 authority plane；它的權力是准入／撤銷可被查詢的 assertion，不是直接准許副作用。

### 1.3 定義與評估：同一面，不是同一支筆

【推論】判準面內至少保留兩個互不代寫的權威：

- 【推論】Definition Authority：建立 immutable CriterionVersion、公開條款映射、isolation requirement、feedback policy、有效期與 supersedes 關係。
- 【推論】Evaluation Authority：讀取凍結版本、執行觀察、寫 EvidenceRecord 與 Verdict；不得更新 CriterionVersion。

【推論】兩者可以在第一版部署於同一可信服務，資料庫權限仍應分 table／command；否則「以後再拆程序」時已沒有可驗證的寫入邊界。共同 deployment 不是共同 authority。

### 1.4 證據不是知識

【推論】三個物件不能再混：

| 物件 | 回答的問題 | 可變性 |
|---|---|---|
| PayloadBlob | 【推論】這些位元組是什麼，digest 是否相同？ | 【推論】內容不可變；可因保留／抹除變 GONE。 |
| EvidenceRecord | 【推論】誰在什麼方法、版本、時間與輸入上觀察到什麼？ | 【推論】append-only；更正要新增 record，不覆寫。 |
| KnowledgeAssertion | 【推論】哪些跨工作陳述目前獲准被檢索與使用？ | 【推論】內容版本不可變；准入狀態可進 admitted／expired／revoked／superseded。 |

【查證】W3C PROV 把 entity、activity、agent、derivation、primary source、revision 與 invalidation 分成顯式關係；來源不是一個自由文字欄位。[W3C PROV-O](https://www.w3.org/TR/prov-o/)。

【推論】不需要完整實作 RDF，但 KnowledgeAssertion 至少要能表示來源、生成活動、責任主體、衍生關係與失效事件；否則「有 provenance」只是存了一個 URL。

### 1.5 知識治理面的物件與狀態

【推論】知識的權威物件不是「memory file」，而是帶範圍的 KnowledgeAssertion：

    KnowledgeAssertion
      id
      revision
      claim_body_ref
      scope
      source_evidence_refs[]
      derived_from_assertion_ids[]
      proposed_by
      admission_rule_version
      admitted_by
      admitted_at
      valid_from
      expires_at
      status: PROPOSED | ACTIVE | REVIEW_REQUIRED | EXPIRED | REVOKED | SUPERSEDED | REJECTED
      taint_flags[]
      revocation_reason
      supersedes

【推論】只有知識權威能執行 PROPOSED→ACTIVE、ACTIVE→REVIEW_REQUIRED／EXPIRED／REVOKED／SUPERSEDED。LLM、Pursuit、Work 與自我維護 observer 都只能 propose；允許執行者自己 admit，等於讓它把一次 hallucination 升級成所有未來工作的前提。

【查證】[agentic.json 的 Memory Store Adapter 與 MemoryRecord](../設計/五學科/agentic.json)已獨立要求 provenance、TTL、跨 session 持久化與依 source 批次撤銷，理由是污染的種下與觸發在時間上解耦。

【推論】那份研究把它稱為 memory adapter，仍偏向儲存視角；本題新增的「准入」要求使它不只是一個 adapter。真正權威是 admission state machine，底下可換 SQL、向量索引或檔案。

### 1.6 Work 如何使用知識

【推論】Work 與 Pursuit 只能綁定 KnowledgeSnapshot：

    KnowledgeSnapshot
      digest
      assertion_versions[]
      resolved_at
      query_policy_version

【推論】快照是重播邊界。同一 Work 中途檢索到不同知識時，必須建立新 snapshot 並留下因果事件；不能讓「今天查詢結果不同」悄悄改寫昨天的 Pursuit。

【推論】撤銷不能改掉歷史。新工作不得再取到 revoked assertion；在途 Work 收到 KNOWLEDGE_REVOKED signal，依風險政策選 PAUSE_AND_REBASE、CONTINUE_WITH_TAINT 或 CANCEL。歷史事件仍保留「當時使用過哪版」，內容若依法抹除則回 GONE。

【推論】知識也不能越權：

- 【推論】它可影響 prompt、策略、工具選擇與工作提案。
- 【推論】它不能直接改 CriterionVersion；Definition Authority 必須顯式匯入某版 assertion，產生新 criterion version。
- 【推論】它不能直接增加預算；Resource Authority 另行核准。
- 【推論】它不能直接觸發外部效果；Work 仍須產生 intent，Effect Authority 仍須交付。

【推論】這些限制正是它應獨立成橫向權威、而不是 Work 欄位的原因：知識跨工作存活，工作只消費一個有版本的視圖。

### 1.7 知識面的最小負控

【推論】至少需要四個會轉紅的保證：

1. 【推論】未 admit 的提案不可被任何 Work snapshot 解析到。負控：查詢拿掉 status=ACTIVE 條件，測試必須抓到 PROPOSED。
2. 【推論】來源撤銷後，所有由該來源直接或傳遞衍生的 assertion 都重新跑 admission rule；至少進 REVIEW_REQUIRED／REVOKED，不得繼續以乾淨 ACTIVE 被取用。若另有足夠獨立來源，規則可重新 admit。負控：只撤銷直接記錄，二階衍生仍被當作乾淨 ACTIVE 取到，測試轉紅。
3. 【推論】同一 snapshot digest 在時間推進、索引重建後解析到完全相同的 assertion revisions。負控：改成每次 live query，過期後結果漂移，重播測試轉紅。
4. 【推論】執行者寫入只能得到 PROPOSED，永遠不能得到 ACTIVE。負控：讓 write API 接受 caller 傳 status，假 agent 傳 ACTIVE，權限測試轉紅。

---

## 2. Q2：目標追求是層，而且現在就拆

### 2.1 產品需求已經給出裁決

【查證】本輪需求明確要求：同一目標可同時有多個獨立策略；任一策略活動結束不終結工作；同一活動可暫停，之後換後端接手。（來源：本輪題目 Q2。）

【推論】這正好命中另一份推導的拆分判準，不再是灰區。Work 可以同時擁有 Pursuit A／B，A 完成或耗盡時 B 與 Work 都仍可存活；Pursuit 又可先後擁有多個 Execution。Pursuit 因而是垂直層，不是 Work 的幾個計數欄位。

【推論】正確基數是：

    WorkItem 1 ── owns ──> 0..N Pursuit
    Pursuit  1 ── owns ──> 0..N Execution
    Execution 1 ── emits ──> 0..N CandidateArtifact
    EvaluationVerdict ── binds ──> CandidateDigest × CriterionVersion

【推論】換後端不會改 Pursuit id，因為 backend assignment 屬於 Execution。Pursuit 暫停後用 checkpoint 建立下一個 Execution，即可由不同後端接手；若換的不只是後端，而是證據面、策略與隔離上下文，才應建立新的 Pursuit。

### 2.2 第一輪終態要修正

【推論】第一輪把 SATISFIED 放在 Pursuit 終態，在序列 first-pass 模式下勉強成立；平行 best-of-N 出現後不再成立。某 Pursuit 找到合格候選，不代表 Work 已選它。

【推論】建議狀態所有權：

| 物件 | 非終態 | 封閉終態 | 不可越權的宣告 |
|---|---|---|---|
| Execution | 【推論】ACCEPTED／RUNNING／STOPPING | 【推論】SUCCEEDED／FAILED／TIMED_OUT／TURN_LIMIT／SPEND_LIMIT／CANCELLED／BACKEND_ERROR／SUPERVISOR_ERROR | 【推論】只宣告一次受限呼叫如何結束。 |
| Pursuit | 【推論】PLANNED／ACTIVE／PAUSED／WAITING_EVALUATION | 【推論】SUBMITTED／EXHAUSTED／CANCELLED／POLICY_STOP／CRITERION_ERROR | 【推論】只宣告一個搜尋活動是否交出候選或耗盡。PAUSED 不是終態。 |
| Work | 【推論】READY／RUNNING／SELECTING／WAITING | 【推論】SATISFIED／EXHAUSTED／FAILED_FINAL／QUARANTINED／CANCELLED | 【推論】只有 Work 的選擇政策可宣告整個目標已滿足。 |

【推論】若產品採 first-acceptable，Work 可在第一個合格 verdict 後 SATISFIED 並取消其他 Pursuit；若採 best-before-deadline，合格只讓 Work 進 SELECTING，其他 Pursuit 繼續。這是 Work policy，不是 Pursuit 終態語義。

【需裁定】何時結束平行搜尋：

- 【需裁定】選項 A，BEST_OF_N：固定啟動 N 個 Pursuit，等全部終態後選最好。代價是最慢分支決定延遲且花滿預算；若成本高或候選品質很早已拉開，判斷轉向 B。
- 【需裁定】選項 B，BEST_BEFORE_DEADLINE：到總 deadline 或全數終態時選最好。本輪建議。代價是結果會受時間窗口影響，但預算和 latency 可硬控；若任務要求每個策略都完成以保證覆蓋，判斷轉回 A。
- 【需裁定】選項 C，FIRST_ACCEPTABLE：第一個過最低門檻就停。成本最低，但與「判官選最好的」需求衝突；只有外部副作用急迫、候選間沒有品質排序或邊際改善不值錢時才反轉到 C。

### 2.3 「獨立」必須是資料，不是形容詞

【查證】[multi.json](../設計/五學科/multi.json)區分 Independence、Diversity 與 Ensemble，並指出模型族、證據面、prompt 版本、seed、工具權限是不同獨立維度；同模型不同 session 不能自動宣稱獨立。

【推論】每個 Pursuit 至少要凍結以下 identity：

    PursuitIdentity
      strategy_spec_digest
      prompt_family
      backend_family_policy
      evidence_scope_digest
      knowledge_snapshot_digest
      tool_capability_set_digest
      random_seed_policy
      isolation_group

【推論】判官收到的不只是候選，還要收到 IndependenceManifest。若兩個 Pursuit 共用同一證據集、相同 prompt family 與相同 backend family，系統可稱它們「兩次採樣」，不得把 effective independent pursuits 算成 2。

【推論】要降低共同盲點，平行 Pursuit 在選拔閘之前預設不可互看彼此候選與中間推理；一旦交換，後續 evidence lineage 要標記依賴。不同模型但共享同一錯誤證據面，仍共享核心失敗原因。

### 2.4 第一版不拆，將來會改什麼

【推論】資料模型不是「多加一張表」而已：

- 【推論】從 Work 移出 attempt_count、current_strategy、pause checkpoint、current_best、局部 budget 與 backend history，建立 pursuit 表。
- 【推論】Execution、Candidate、Evaluation、BudgetReservation、EvidenceRecord、lease 與事件都要補 pursuit_id；idempotency key 與唯一索引會改。
- 【推論】Work budget 要拆成 portfolio 總額與 Pursuit 配額；否則平行啟動時每支都以為自己擁有全部餘額。
- 【推論】目前最佳值要從單欄改成候選集合＋selection record；多維判官不能再覆寫一個 current_best。

【推論】狀態機也不是原狀加 PAUSED：

- 【推論】Work 與 Pursuit 的取消、耗盡、criterion error、pause／resume 必須分開；任一 Pursuit 終態不得自動封閉 Work。
- 【推論】新增 fan-out、等待多個 pursuit、選拔、取消輸家、遲到 verdict 與重複 resume 的轉移。
- 【推論】租約領取單位會從 Work 改成 Pursuit 或 Execution；否則一個 worker claim Work 後會壟斷全部平行策略。
- 【推論】事件 schema、重播 reducer、outbox causation id 與查詢 API 都會升版。

【推論】已有資料的遷移策略：

| 舊資料狀態 | 必要處置 |
|---|---|
| 尚未有持久 production data | 【推論】現在拆沒有資料遷移成本，只有正確建模成本；這正是最便宜的窗口。 |
| 已完成 Work | 【推論】若要一致歷史查詢，每件 backfill 一個 synthetic closed Pursuit，所有 Execution 指向它；若不需重播，可把 v0 歷史保留為 read-only projection。 |
| 非終態但未執行 | 【推論】建立 synthetic active Pursuit，移入剩餘預算與策略快照即可。 |
| 正在執行／暫停中的 Work | 【推論】先 drain 或 freeze；把當前 checkpoint、attempt lineage、候選與保留預算原子搬入 synthetic Pursuit。線上雙寫遷移最危險，不值得為這個新系統承擔。 |

【推論】如果第一版先不拆，將來成本是中高，而且最難的是語義遷移，不是 DDL。已存在的工作要遷移；否則新舊 Work 的終態代表不同意思，重播與核銷會分叉。

### 2.5 本輪裁決

【推論】現在就拆出 Pursuit 資料與狀態機；第一版排程器可以把 system_max_parallel_pursuits 設為 1，保留現有序列用法。這不是過度設計：明確產品需求已要求 N，先用 cardinality=1 只是 rollout policy，不應反向污染資料本體。

【推論】啟用真正平行前還要有三道 gate：獨立性 manifest 可驗證、每個 Pursuit 有獨立 workspace／evidence scope、portfolio budget 原子分配。少任何一道，多個 Pursuit 只是會互踩資料且一起超支的多個程序。

---

## 3. Q3：envelope 先訂，再量候選有沒有守住

### 3.1 你的二分大致對，但少了第三類

【推論】從零系統的 workload envelope 不是從歷史流量「發現」出來的。它先是一份設計契約：系統承諾接受什麼、拒絕什麼、在什麼範圍內達成 SLO。沒有舊系統不妨礙先訂上限。

【推論】欄位應分三類，不是兩類：

1. 【推論】外部需求／SLO：主機數、RPO／RTO、保留期、允許恢復時間。產品或營運裁定，架構不能量出價值偏好。
2. 【推論】架構政策上限：併發、每層 fan-out、事件粒度、租約、讀交易上限、單筆 payload。設計者先訂，入口與測試強制；超出應拒絕／排隊，不是祈禱資料庫撐住。
3. 【推論】待驗證結果：在上述負載下的 p99 latency、BUSY／lock 比率、burst drain time、crash recovery、備份還原時間。這些不能用決定代替量測，但可以用合成工作負載量，不需等 production。

【推論】因此[架構草案第六節](./架構草案.md)的「在裁定儲存之前必須先量」寫錯了。應改成：「先裁定 design envelope；再以相同 envelope 量候選，通過才定案。」儲存選擇可以現在往前，驗收不能免。

### 3.2 建議的 v1 design envelope

【推論】以下初值假設 v1 是單機可信控制面，LLM／CLI 執行者可多程序，但不能直接連狀態庫；大 payload 進 CAS，狀態庫只存 metadata 與 digest。這是可推翻的設計基線，不是市場需求的冒充事實。

| 欄位 | 類別 | 建議初值 | 為什麼選它 | 先撞到什麼 |
|---|---|---|---|---|
| 權威寫入主機數 | 外部需求／部署決策 | 【推論】1 台；不允許第二台直接寫 DB | 【推論】目前沒有跨主機權威需求；先把 single-writer 變成明確所有權。 | 【推論】需要 HA、自動 failover 或遠端 worker 直連時先撞到；屆時轉 client/server DB。 |
| 狀態 owner／connection | 架構政策 | 【推論】1 個 owner process、1 條 writer connection；worker 只能送高階 command | 【推論】讓「誰能寫」由拓撲承載，消除每個 worker 各自處理 lock retry。 | 【推論】長查詢阻塞 command queue、owner CPU 飽和或 IPC backlog。 |
| 非終態 Work | 架構政策 | 【推論】最多 1,000；其餘 admission queue／拒絕 | 【推論】給掃描、重建與 UI 查詢明確上界；不是把所有歷史都當 active。 | 【推論】大批 timer／backlog 同時活躍時先撞掃描與記憶體投影。 |
| 同時 ACTIVE Pursuit | 架構政策 | 【推論】全系統 32；每 Work 同時 4、生命週期總數 8 | 【推論】足以支援四策略 best-of-N，又限制 portfolio 爆炸。 | 【推論】研究型 workload 要 10+ islands 或大量 Work 同時 fan-out 時先排隊。 |
| 同時 RUNNING Execution | 架構政策 | 【推論】8 | 【推論】控制本機程序、檔案 I/O 與供應商併發；Pursuit 可 ACTIVE 但等待。 | 【推論】本地重播器／本地模型吞吐需求先撞 scheduler，而非 DB。 |
| 每 Pursuit 的 Execution | 架構政策 | 【推論】最多 16 次 | 【推論】讓停止性有結構上限，仍容許策略內多輪改進與後端接手。 | 【推論】低成功率任務會先進 ATTEMPT_LIMIT；不能默默加到 17。 |
| 付費呼叫數 | 架構政策 | 【推論】每 Execution 32、每 Pursuit 128；Work 另有總金額硬上限 | 【推論】分層上限防止 16×32 的理論最大值全部發生；金額仍由資源權威裁定。 | 【推論】工具密集／研究型任務先撞 CALL_LIMIT；應拆工作或明確升版 policy。 |
| 權威事件粒度 | 架構政策 | 【推論】每個狀態轉移、花費 reserve／settle、外部／工具 call intent／result、lease 與 outbox 轉移各一筆；stream chunk 以 1 秒或 64 KiB 先到者批次，禁止 per-token fsync | 【推論】保留崩潰重建與核銷所需因果，又不讓 token 串流主宰寫入。 | 【推論】需要逐 token 法遵稽核時先撞儲存量與 commit rate；這會反轉整個引擎評估。 |
| 狀態交易負載 | 架構政策／驗證輸入 | 【推論】持續 50 tx/s；200 tx/s burst 持續 10 秒；30 秒內清空 backlog | 【推論】這是刻意高於八個執行者一般語義事件率的壓力帽；高速重播必須節流或批次。 | 【推論】大量 replay、lease 同時到期或 outbox 恢復超過 200/s 時先撞 owner queue。 |
| 單筆狀態 payload | 架構政策 | 【推論】64 KiB hard max；更大內容先寫 CAS，再以 digest 進交易 | 【推論】避免 prompt、log、artifact 把 journal 與 backup 撐成 blob store。 | 【推論】超大結構化 verdict／manifest 會先被拒，需分片或外置。 |
| active state DB 大小 | 架構政策 | 【推論】10 GiB hard review point，不含 CAS | 【推論】在這之前先做歸檔與查詢計畫；不是宣稱 SQLite 只能到 10 GiB。 | 【推論】備份時間、掃描與 migration 先惡化；到點必須重新量，不自動擴帽。 |
| lease | 架構政策 | 【推論】30 秒到期、每 10 秒續租；claim／takeover 才遞增 fencing epoch，renew 以同 epoch CAS 延長 | 【推論】容忍短暫停頓，又把 SIGKILL 後無主時間壓在一分鐘內；正常續租不讓 token 無謂漂移。 | 【推論】宿主 pause／GC／模型呼叫阻塞 event loop 超過約 20 秒會出現誤回收；heartbeat 必須由 supervisor 而非執行者送。 |
| 最長 DB read transaction | 架構政策 | 【推論】100 ms target、250 ms hard kill；報表／匯出用 snapshot，不佔 owner transaction | 【推論】低寫入率也怕長 reader；直接把鎖持有時間變成可測上限。 | 【推論】全表分析、互動報表先被切斷；需投影庫、snapshot connection 或 WAL。 |
| outbox fan-out | 架構政策 | 【推論】每次 Work transition 最多 16 個 intent；pending backlog 最多 10,000 | 【推論】足以覆蓋多 endpoint，防一個狀態轉移製造無界外部工作。 | 【推論】mass notification／大批 remote refs 先撞 fan-out；應改成子 Work 或目的端 batch API。 |
| 程序崩潰恢復 | 外部 SLO | 【推論】restart 後 5 秒內完成狀態掃描；p95 30 秒、hard 60 秒內重新派出可執行工作 | 【推論】與 30 秒 lease 相容，使用者不必等人工清理。 | 【推論】1,000 active Work 的掃描、CAS 驗證或 lease storm 先超時。 |
| 保留期 | 外部需求／政策 | 【推論】raw executor log 30 天；完整 operational events 90 天；verdict、budget ledger、ClaimSpec／criterion provenance 365 天；被 pin 的 accepted artifact 365 天 | 【推論】把高體積除錯資料與核銷／驗收證據分開；一年不是永久承諾。 | 【推論】法遵要求多年稽核或使用者要求長期重播時先撞 CAS 成本與 migration 時間。 |
| 知識預設 TTL | 架構政策 | 【推論】90 天；可由 Definition／Knowledge Authority 縮短，延長須重新 admit | 【推論】跨工作知識若默認永久，撤銷永遠會漏；90 天迫使高價值知識被重新驗證。 | 【推論】穩定工具手冊會產生重複 admission 成本；可對特定來源類別升到 365 天。 |
| 備份 RPO／RTO | 外部 SLO | 【推論】host／disk loss 的 RPO 5 分鐘、RTO 30 分鐘；程序 crash 則 committed state RPO=0 | 【推論】區分 DB crash durability 與整台機器消失；五分鐘足以用週期 snapshot／增量備份達成。 | 【推論】任何「已提交工作絕不許因磁碟損失」要求會先撞 RPO，需同步遠端複寫。 |
| 直接跨主機讀寫 | 外部需求 | 【推論】v1 為 0；遠端 executor 只能經 owner API | 【推論】避免把 SQLite 檔案鎖與網路檔案系統當協調協議。 | 【推論】第二個 control-plane host 或離線容錯一出現，SQLite local owner 結論反轉。 |

【推論】這份表刻意把 pure replay 的高速擋在 production state owner 之外：測試可用每例獨立 ephemeral store 跑到很快；production-topology suite 則按 50／200 tx/s 上限驗證。測試吞吐不應偷偷改寫產品持久層的 admission policy。

### 3.3 由初值推出的儲存決策

【推論】在上述 envelope 下，本輪可以選：固定已修版本的 SQLite、專用 state-owner process、單一 connection、rollback journal、synchronous=FULL、所有大內容先進 CAS。worker 與 evaluator 都不得直接開 DB。

【查證】SQLite 官方把「由 application server 序列化高階請求」列為適用形態，也明講 many concurrent writers 或多機直接存取應轉 client/server。[Appropriate Uses For SQLite](https://www.sqlite.org/whentouse.html)。

【推論】單 connection 下 WAL 沒有 reader／writer 並行的主要收益，卻增加 checkpoint 與 WAL／SHM 檔管理，所以 v1 從 rollback journal 起步是拓撲推論，不是沿用舊文件的 3.50.4 恐懼。若引入 snapshot reader 或 direct read pool，再以同一 envelope 比較 WAL。

【查證】SQLite 官方目前記載 WAL-reset 問題已在 3.51.3 修正，並有 3.50.7 與 3.44.6 backport。[SQLite WAL](https://www.sqlite.org/wal.html)。

【推論】版本政策應是「pin 到官方已修版本並把版本寫入 evidence」，不是永久禁 WAL。未達已修版本時，WAL profile 直接 UNSUPPORTED。

【推論】CAS 與 DB 的寫入順序固定為 blob first、metadata transaction second。前者成功後後者失敗只留下可回收 orphan；反過來會留下已提交但永遠讀不到的 ref。備份還原測試必須同時驗證 DB snapshot 內的所有 retained ref 在 CAS 可取。

### 3.4 不等 production，但必須通過合成驗收

【推論】儲存 adapter 的出口條件至少包括：

1. 【推論】在 32 ACTIVE Pursuit、8 RUNNING Execution、50 tx/s 持續負載下，command latency p99 ≤50 ms，零失落 committed transition。
2. 【推論】注入 200 tx/s、10 秒 burst，加一個 250 ms read，p99 ≤500 ms 且 backlog 30 秒內清空。
3. 【推論】在每個 transaction boundary 前後 SIGKILL owner；重啟後 5 秒內掃描完成、60 秒內重新派工，沒有雙重有效 lease。
4. 【推論】讓 lease 全部在同一秒過期、outbox backlog=10,000；回收與 relay 不得使新工作永久飢餓。
5. 【推論】注入 disk-full、CAS put 失敗、DB commit 失敗、backup 中 crash；每一種都得到型別化終態，且不存在 metadata 指向缺失 blob。
6. 【推論】從五分鐘前的備份在乾淨目錄還原 DB＋CAS，RTO 30 分鐘內；只證明「產生了備份檔」不算。

【推論】這些是 selection verification，不是等真使用者幫忙撞 bug。SQLite 若過不了就淘汰；若 PostgreSQL adapter 在相同 envelope 下維運成本過高也淘汰。

### 3.5 本輪要你裁定的不是數字真偽，而是產品承諾

【需裁定】儲存前進路線：

- 【需裁定】選項 A，接受上表作為 v1 envelope，立即以 SQLite single-owner／rollback profile 往前。本輪建議。代價是 admission 必須真的拒絕第 33 個 Pursuit、長讀與第二台 writer；任一跨主機 writer、RPO=0 的 host-loss、持續 >50 tx/s 或無法把 read 壓到 250 ms 時，判斷轉向 PostgreSQL／分散式服務。
- 【需裁定】選項 B，現在就把 multi-host／HA／同步遠端 RPO=0 納入 v1。代價是立刻承擔 PostgreSQL 服務、測試與維運，不再享有單檔 owner 的簡單性；若這些需求在一年內都不會啟用，判斷轉回 A。
- 【需裁定】選項 C，不願對上述任何數字承諾。代價是沒有可淘汰候選的判準，「再量量看」只會得到可任意解釋的 benchmark；只有外部需求確實尚未形成、且本輪目標只是 disposable spike 時才合理。

【推論】直接答案：你的看法對，但要加第三類「驗證結果」。現在可以做儲存設計決定；不能做的是把未跑過 envelope suite 的 adapter 宣稱為已驗收。

---

## 4. Q4：同 UID 下兩種威脅模型的真實價差

### 4.1 先拆掉一個假安全邊界

【查證】目前工作環境是 Darwin arm64。（來源：本輪執行 uname -s／uname -m。）

【推論】在沒有 App Sandbox、container、namespace 或 VM 時，「不掛載測試檔」不是事實描述。普通 child process 看見的是同一 host filesystem；不把秘密路徑放進 cwd／argv 只是不提示它，沒有撤銷同 UID 的檔案權限。

【推論】因此兩個 threat model 的保證應寫成：

- 【推論】防無意看到：我們降低秘密被正常 test discovery、cwd 掃描、stack、stdout 與錯誤訊息帶回的機率；不抵抗刻意 absolute-path 掃描、process inspection 或網路 exfiltration。
- 【推論】防主動竊取：candidate 即使把 host 當攻擊面，也缺少讀秘密、看別的程序、對外傳輸與留下持久檔案的能力；這需要 OS／VM 強制，不是 coding convention。

【查證】Linux Yama 文件明講，classic ptrace 規則下，同 UID 且 dumpable 的程序可 PTRACE_ATTACH；額外 policy 才能收窄。[Linux Yama](https://www.kernel.org/doc/html/latest/admin-guide/LSM/Yama.html)。

【推論】macOS 的細節不同，但結論相同：process separation 本身是故障隔離，不自動是 confidentiality boundary。真正的 macOS 強制邊界來自 App Sandbox entitlement 或 VM，不是 fork／subprocess。

### 4.2 Profile C：COOPERATIVE，只防無意洩漏

【推論】要做的機制：

1. 【推論】Evaluator 與 candidate 分程序；hidden source 只由 evaluator 開啟，不出現在 candidate argv、env、cwd、prompt 或 binding manifest。
2. 【推論】candidate 使用新建工作目錄；只複製候選 artifact 與明列輸入，執行後整體丟棄。
3. 【推論】啟動前清空非白名單 env，關閉非白名單 file descriptors，不繼承 evaluator logger／socket。
4. 【推論】stdout／stderr／exception／stack 只進 private evidence；Feedback Gateway 從封閉 enum 重新產生回饋。
5. 【推論】candidate digest、criterion version、query budget 與 output size cap 由 evaluator 外部持有。
6. 【推論】hidden sentinel 貫穿 prompt、telemetry、workspace、report 的 leak test；verbose reporter 負控必須轉紅。
7. 【推論】timeout 後殺整個 process group，避免 child 留在背景；這是資源正確性，不是秘密隔離。

【推論】工程量估計為 8–15 engineer-days，假設一位熟悉 subprocess／test runner 的工程師、單一語言 runner、已存在基本 evaluator API。拆分大致是 runner／FD／env／workspace 3–5 天、reducer 2–4 天、sentinel 與 crash 負控 3–6 天。

【推論】日常成本低：每次裁定增加約 0.1–0.5 秒啟動／清理；開發者看不到 raw hidden failure，需用只對裁定維護者開放的 evidence viewer 查 evaluator bug。主要麻煩不是效能，而是「為什麼我只看到 clause id」的除錯摩擦。

【推論】殘餘風險很大：同 UID candidate 若刻意掃描 home、已知 repo、程序、共享 temp 或開 network，這個 profile 沒有資格宣稱阻止它。directory mode 0700 對同一 UID 沒用；隨機秘密路徑只是 obscurity。

### 4.3 Profile R：RESTRICTED，同 kernel 的 OS sandbox

【推論】相對 C 額外要做：

1. 【推論】可信 launcher／broker；candidate 無法自行更改 sandbox policy。
2. 【推論】filesystem allowlist：空 root 或 App Sandbox container，只給 runtime、候選與單次輸入；home、repo、secret store、host temp 全部不可見。
3. 【推論】PID／process isolation：看不到 evaluator 與其他 job，禁止 ptrace、debug、proc memory。
4. 【推論】network deny-by-default；需要套件或 remote tool 時只經受控 proxy，不能直接 egress。
5. 【推論】system call／capability 收窄；禁止 mount、namespace escape、device、keychain、IPC 與任意 socket。
6. 【推論】CPU、memory、PID、file size、FD、I/O hard limits；cleanup 必須證明 process tree 與 temp volume 都消失。
7. 【推論】平台 capability probe 與 negative escape suite；policy 不完整時 fail closed。

【查證】Linux seccomp 官方文件自己明講「system call filtering 不是 sandbox」，它只縮小 kernel attack surface，資訊流仍需其他 hardening／LSM。[Seccomp BPF](https://www.kernel.org/doc/html/latest/userspace-api/seccomp_filter.html)。

【查證】Bubblewrap 可建立空 mount namespace、PID／network／user namespace並接 seccomp，但其維護者明講它是建構 sandbox 的低階工具，是否形成安全邊界完全取決於呼叫參數與外層 policy。[Bubblewrap README](https://github.com/containers/bubblewrap)。

【查證】Apple App Sandbox 以 entitlements 限制檔案、網路與系統資源；command-line helper 要嵌入、簽署並繼承 sandbox entitlement，不是把任意現有 CLI 前面加一個 flag。[App Sandbox](https://developer.apple.com/documentation/security/app-sandbox)；[Embedding a helper tool](https://developer.apple.com/documentation/xcode/embedding-a-helper-tool-in-a-sandboxed-app)。

【推論】工程量估計：

- 【推論】若正式執行宿主是 Linux 且可採 user／mount／PID／network namespace：20–40 engineer-days。成本主要在 policy、各語言 runtime／compiler 依賴、escape 負控與 CI parity，不是呼叫 bubblewrap 那一行。
- 【推論】以目前 Darwin 為正式宿主、又要支援任意 CLI agent／編譯器：30–60 engineer-days。需要 signed sandbox broker、helper inheritance、toolchain allowlist、entitlement／code-signing 流程與 macOS 版本測試；某些工具可能根本不相容，只能改走 VM。

【推論】日常成本中等：啟動約多 0.2–2 秒；新 compiler、package manager、SDK、動態 library、tool 或檔案路徑都可能需要 policy 升版。直接 debugger、臨時下載套件與「順手讀 home config」會失效，錯誤通常先表現成 permission denied 而不是業務錯誤。

【推論】R 能擋大多數直接讀檔、proc、網路與殘留 temp 的主動攻擊，但仍共享 kernel，policy 漏一個 D-Bus／socket／可寫 mount 就可能穿透；它也不解決 timing、CPU cache 等微架構側通道。

### 4.4 Profile H：HOSTILE，獨立 guest／microVM

【推論】相對 R 再增加：

1. 【推論】candidate 在獨立 guest kernel；host evaluator 只透過窄 vsock／serial protocol 傳候選、輸入並收 verdict material。
2. 【推論】immutable base image＋每次 evaluation 的 ephemeral overlay；不分享 host directory，artifact 以 digest copy-in。
3. 【推論】guest network 預設不存在；需要 remote backend 時由 host broker 代理白名單 RPC。
4. 【推論】VM boundary 的 CPU／memory／disk／time quota，guest panic／hang 由 host supervisor 強殺。
5. 【推論】image build、簽章、patch、snapshot pool、guest agent protocol、log redaction、殘留清理與 host capability attestation。
6. 【推論】固定 response size、query cap、時間分桶；microVM 仍不能承諾消滅所有硬體側通道。

【查證】Apple Virtualization framework 可在 Apple silicon／Intel Mac 執行 Linux VM，但需要自行配置 guest、裝置、檔案交換與生命週期。[Apple Virtualization](https://developer.apple.com/documentation/virtualization)。

【查證】Firecracker 的 production 文件要求 jailer、namespace、cgroup、降權與獨立 UID；其安全文件仍明講無法處理所有硬體 side channels。[Firecracker design](https://github.com/firecracker-microvm/firecracker/blob/main/docs/design.md)；[Production host setup](https://github.com/firecracker-microvm/firecracker/blob/main/docs/prod-host-setup.md)。

【推論】工程量估計為 40–80 engineer-days，假設只支援一種 guest OS／architecture、沒有現成 VM orchestration；另需約 0.1–0.25 FTE 持續處理 image patch、host OS 相容、cache、磁碟清理與安全更新。若同時支援 macOS Virtualization 與 Linux Firecracker，範圍至少再加 50%，不能拿同一個數字假裝跨平台免費。

【推論】日常成本高：cold start 約 1–10 秒，warm pool／snapshot 可降到亞秒至數秒但會引入池清理與 stale image 問題；依賴必須 bake 或 copy-in，debug 要在 guest 重現，artifact 傳輸與 cross-architecture toolchain 都變成明確流程。

【推論】H 是能合理聲稱抵抗惡意 candidate 的起點，不是終點。host broker、hypervisor、guest image、CPU 與 reducer 都進 TCB；把「用了 VM」寫成絕對安全同樣是假話。

### 4.5 中間形態存在，而且不該只用一個 level enum

【推論】應由每份 Criterion／ClaimSpec 宣告 required capabilities，宿主回報 offered capabilities；Evaluation Authority 只在 required ⊆ offered 時執行：

    isolation
      threat_profile: COOPERATIVE | RESTRICTED | HOSTILE
      required_capabilities:
        - private_raw_evidence
        - clean_environment
        - closed_file_descriptors
        - ephemeral_workspace
        - filesystem_allowlist
        - process_introspection_denied
        - network_denied
        - resource_hard_limits
        - output_reducer
        - fixed_response_size

【推論】level 只作人類摘要，capability set 才是機械判定。Linux namespace sandbox 和 macOS App Sandbox 都可叫 RESTRICTED，實際能力未必相同；只比 enum 會製造假等價。

【推論】宿主產生 IsolationOffer：

    IsolationOffer
      platform
      launcher_digest
      policy_digest
      capabilities[]
      verified_at
      escape_suite_version

【推論】Claim author 不能在執行時自行降級。Definition Authority 在 admit ClaimSpec 時固定 requirement；Evaluation Authority 發現缺 filesystem_allowlist 或 network_denied，就回 UNSUPPORTED_ISOLATION。把它當 NOT_MET 會冤枉候選，把它當 PASS 則直接說謊。

【推論】可採的過渡策略是：

- 【推論】公開 Guidance Suite 與可再生、洩漏即燒掉的低價值 holdout 可標 COOPERATIVE。
- 【推論】會造成真實損失、無法再生、或可被 hard-code 套利的 sealed criterion 至少標 RESTRICTED；主動攻擊有價值時標 HOSTILE。
- 【推論】目前只有 C 時，R／H claim 保持不可執行；不能為了全綠偷偷用 C 跑完。

### 4.6 成本總表

| 項目 | COOPERATIVE | RESTRICTED | HOSTILE |
|---|---|---|---|
| 抵抗對象 | 【推論】誤傳、正常掃描、verbose failure | 【推論】直接讀 host path／proc／network／temp exfil | 【推論】把 candidate 當惡意 native code，並增加 kernel boundary |
| 初始工程量 | 【推論】8–15 engineer-days | 【推論】Linux 20–40；目前 Darwin 30–60 engineer-days | 【推論】單平台 40–80 engineer-days |
| 持續維運 | 【推論】低；reducer／runner 升版 | 【推論】中；policy、signing、toolchain 相容 | 【推論】高；image、hypervisor、pool、patch，約 0.1–0.25 FTE |
| 常態延遲 | 【推論】約 0.1–0.5 秒 | 【推論】約 0.2–2 秒 | 【推論】cold 1–10 秒；warm 較快但增複雜度 |
| 開發摩擦 | 【推論】看不到 raw hidden failure | 【推論】檔案／網路／debug／新工具需 policy | 【推論】依賴 bake、guest 重現、artifact copy |
| 不能宣稱的事 | 【推論】不能宣稱防惡意 | 【推論】不能宣稱無 policy escape／side channel | 【推論】不能宣稱 VM 等於零側通道或零 TCB |

【推論】以上時間是範圍估計，不是查證事實；前提是一位熟悉 runner 的資深工程師、只做本題所需語言／平台。若已有成熟 sandbox broker，R／H 成本會大幅下降；若要同時支援 Python、Node、Rust、任意 shell 與所有 CLI agent，會大幅上升。

### 4.7 本輪裁決

【需裁定】近期威脅承諾：

- 【需裁定】選項 A，v1 明確宣告 COOPERATIVE_ONLY，同時把 capability negotiation 與 UNSUPPORTED_ISOLATION 做進 ClaimSpec。本輪建議。代價是 sealed tests 不能宣稱抵抗惡意 candidate，高價值 R／H claim 暫時不能驗收；一旦 candidate 有動機讀答案、第三方程式碼進場或 hidden cases 不可再生，判斷反轉。
- 【需裁定】選項 B，現在為 Darwin 建 RESTRICTED broker。代價是約 30–60 engineer-days及持續 toolchain／signing 摩擦；若正式部署其實會轉 Linux，先做 macOS-specific policy 可能整筆重付，此時應反轉為 Linux runner service。
- 【需裁定】選項 C，直接建 VM HOSTILE runner。代價是 40–80 engineer-days、較慢 feedback 與持續 image 維運；只有 sealed 判準的價值高於這筆成本、candidate 明確視為攻擊者，或未來要接不受信任第三方程式時才值得現在做。

【推論】不能選的第四項是「嘴上選主動防禦，實際仍同 UID subprocess」。那不是中間形態，是安全聲明造假。

---

## 5. Q5：第一份具體檔案與 ClaimSpec v0

### 5.1 第一份檔案不是架構 prose，也不是只有 meta-schema

【推論】第一份新系統行為檔案應是：

    claims/execution/external-wall-limit.claim.json

【推論】它是一份 ClaimSpec instance，描述性質 1 中一個可原子驗證的切片：「wall-clock 上限由 executor 外部強制，逾時後 child 確實死亡，並得到型別化 TIMED_OUT。」

【推論】不能用一份檔案假裝覆蓋性質 1 全句。時間、回合、花費、終態來源至少是四個 ClaimSpec；本例只覆蓋 wall time＋typed timeout＋外部 kill。把一條大中文句子配一個測試名稱，仍是保證膨脹。

【推論】第一份若只寫 claimspec.schema.json，最多證明 JSON 長得對，不能讓任何錯誤實作轉紅。JSON Schema 是必要的結構驗證器，不是行為 oracle；官方規格的職責也是描述／驗證 JSON instance 結構。[JSON Schema 2020-12](https://json-schema.org/draft/2020-12)。

【推論】bootstrap 信任根必須先由 repo 外部提供一個固定版本的 ClaimSpec runner、meta-schema 與 primitive catalog。第一個 repo-owned 行為檔案才是上述 claim instance。這不是循環論證的消失，而是把不可避免的信任根縮到 parser＋typed interpreter＋幾個 observer。

### 5.2 「機械生成」的邊界

【推論】不可能從任意自然語言需求自動推導正確 observation 與 judge；那仍需要定義權威作語義決定。機械性從 ClaimSpec 被 admit 之後開始：同一份結構資料必須無人工 callback 地編譯成 setup、stimulus、observation、predicate、positive control 與 negative control。

【推論】statement 是人讀註解，不具驗收權。真正有權的是 typed observation＋predicate AST＋fixed controls。若 statement 說「外部強制」，judge 卻只斷言 return code，Definition Authority 必須拒絕 admission；系統無法靠 JSON Schema 理解這兩句語義是否等價。

【推論】ClaimSpec v0 不允許嵌入 Python、shell、JavaScript、regex replacement script 或任意 expression string。所有 action、collector、predicate 與 protocol-machine step 都必須來自有版本的 primitive catalog；需要新能力就升版 catalog，並替 primitive 自己加紅／綠控制。

### 5.3 Top-level schema

【推論】所有 object 預設 additionalProperties=false；未知欄位 fail closed。以下是 ClaimSpec v0 的完整 top-level：

| 欄位 | 型別 | 必填 | 機械作用 |
|---|---|---|---|
| $schema | absolute URI | 是 | 【推論】選擇結構 meta-schema；runner 不認得就拒絕，不能猜版本。 |
| claimspec_version | SemVer string | 是 | 【推論】選擇編譯與執行語義；不是文件版本。 |
| claim_id | semantic id string | 是 | 【推論】形成穩定 test id、verdict key 與 criterion mapping；不得使用「性質 7」這類會重編號的 id。 |
| revision | integer ≥1 | 是 | 【推論】同 claim 的 immutable revision；修改任何 executable field 必須加 revision。 |
| supersedes | ClaimRef 或 null | 否 | 【推論】聲明新 revision 取代誰；是否 ACTIVE 由 Definition Authority ledger 決定，不由檔案自稱。 |
| statement | non-empty string | 是 | 【推論】只供人讀與 review；compiler 不從中生 test。 |
| sources | SourceRef[]，minItems=1 | 是 | 【推論】綁定來源 snapshot、locator 與 digest；digest 不符時 admission 失敗。 |
| primitive_catalog | versioned catalog ref | 是 | 【推論】解析 action／collector／predicate／protocol-machine primitive；admission 時解析為 content digest。 |
| subject | SubjectContract | 是 | 【推論】宣告 contract、operation 與 binding_slot；不寫實作 module path。 |
| parameters | map<string, TypedLiteral> | 是，可為空 | 【推論】所有 threshold、duration、count、enum 都有型別與單位；predicate 不接受裸魔法數。 |
| setup | Action[] | 是，可為空 | 【推論】依序產生可信 fixture；每個 op 來自 primitive catalog。 |
| stimulus | Action[]，minItems=1 | 是 | 【推論】對 subject 發生什麼；形成 act phase。 |
| observations | Observation[]，minItems=1 | 是 | 【推論】由可信 collector 取名、型別化觀察；同 id 唯一。 |
| judge | Predicate AST | 是 | 【推論】只引用 observation／parameter／literal，輸出 ACCEPT 或 CLAIM_REJECTED＋failed predicate ids。 |
| controls.positive | PositiveControl[]，minItems=1 | 是 | 【推論】同一 plan 換成固定已知正確 subject；必須 ACCEPT，防恆假。 |
| controls.negative | NegativeControl[]，minItems=1 | 是 | 【推論】同一 plan 換成固定錯誤 subject；必須以指定 predicate REJECT，防恆真。 |
| run_limits | RunLimits | 是 | 【推論】runner 外部強制 wall／CPU／memory／PID／output／repetition 上限。 |
| isolation | IsolationRequirement | 是 | 【推論】與 IsolationOffer 做 capability subset；不足回 UNSUPPORTED_ISOLATION。 |
| evidence | EvidencePolicy | 是 | 【推論】決定哪些 observation／digest／raw material 被權威保存與誰可讀。 |
| feedback | FeedbackPolicy | 是 | 【推論】決定對 executor 可見的 clause／predicate／bucket；不得透傳 raw runner text。 |
| cleanup | Action[] | 是，可為空 | 【推論】在 observation／judge 後執行，且 runner crash 時仍由外部 finally 執行；cleanup 失敗是 HARNESS_ERROR。 |

【推論】故意沒有 status、admitted_by、verdict 或 passed 欄位。Claim author 不能在同一檔案裡自稱 ACTIVE 或 PASS；Definition／Evaluation Authority 以 spec digest 另寫權威紀錄。

### 5.4 Nested types

【推論】SourceRef：

    kind: REQUIREMENT | RESEARCH | DECISION
    uri: string
    locator: string
    quoted_text: string | null
    snapshot_sha256: sha256

【推論】若 source 是 mutable URL，snapshot_sha256 必填；quoted_text 若存在，其 hash 必須等於 snapshot_sha256。來源內容升版不會默默改既有 ClaimSpec。

【推論】SubjectContract：

    contract: semantic id + major version
    operation: operation id
    binding_slot: stable string

【推論】實作位置放在另一本 BindingManifest。如此 actual implementation、positive control、negative control 只替換 binding，不改 setup／observer／judge。Binding 未提供是 UNBOUND_SUBJECT，不是候選「沒通過」。

【推論】TypedLiteral：

    type: BOOL | INT | STRING | ENUM | DURATION_MS | BYTES
    value: matching JSON literal

【推論】v0 不接受 float threshold；需要統計判定時另加有明確 rounding／confidence 語義的 primitive，不能讓不同語言浮點差異進 oracle。

【推論】Action：

    id: string | null
    op: PrimitiveActionId
    args: JSON object whose schema is owned by that primitive

【推論】Action 不能執行自由命令。若要跑一個 command，primitive 必須明定 argv array、cwd capability、env allowlist、exit observation 與 artifact digest；一個 shell string 不可進 v0。

【推論】Observation：

    id: string
    collector: PrimitiveCollectorId
    args: typed object
    result_type: TypedValue schema
    unit: string | null
    trust_source: VERIFIER | SUBJECT

【推論】judge 若用來證明外部上限，關鍵時間與 liveness observation 必須標 VERIFIER；compiler 應拒絕拿 SUBJECT 自報 elapsed 來證明外部 deadline。

【推論】Predicate AST：

    boolean node:
      op: ALL | ANY | NOT
      args: Predicate[]

    leaf:
      id: stable predicate id
      op: EQ | NE | LT | LTE | GT | GTE | IN | EXISTS
      left: Term
      right: Term

    Term:
      observation ref | parameter ref | typed literal |
      ADD(Term[]) | SUB(Term, Term) | COUNT(observation)

【推論】v0 沒有 loop、user function、I/O、current time 或 random。時間必須先由 collector 變成 observation；這讓 judge 是總函式，輸入固定就必定停止。

【推論】PositiveControl：

    id
    subject: inline ProtocolMachine | CAS artifact ref
    expect: ACCEPT

【推論】NegativeControl：

    id
    subject: inline ProtocolMachine | CAS artifact ref
    expect: CLAIM_REJECTED
    must_fail_exactly: non-empty predicate id set

【推論】inline ProtocolMachine 也不是任意程式，只能使用 catalog 中的 spawn、arm trusted timer、force kill、return 等有限 step。它的 JSON 位元組就在 ClaimSpec 中，因此 counterexample 隨 spec digest 固定。

【推論】run_limits 至少含 wall_ms、cpu_ms、memory_bytes、max_pids、max_output_bytes、repetitions、required_accepts。任何控制跑到 runner 上限都是 HARNESS_LIMIT／HARNESS_ERROR，不可算作「成功抓到 counterexample」。

### 5.5 從 ClaimSpec 到測試的確定性編譯

【推論】compiler 固定做九步：

1. 【推論】用 $schema 驗結構，拒絕 missing／unknown field。
2. 【推論】解析 primitive_catalog 並在 admission record 固定 digest；未知 primitive 直接失敗。
3. 【推論】type-check parameters、Action args、Observation result 與 Predicate Term；DURATION_MS 不得和 BYTES 比。
4. 【推論】把 setup→stimulus→observe→judge→cleanup 編成 immutable TestPlan；排序由陣列順序決定。
5. 【推論】以實際 BindingManifest 產生 actual case；同一 TestPlan 分別替換成每個 positive／negative control subject。
6. 【推論】actual 與 positive 必須 ACCEPT；negative 的直接 claim check 必須回 CLAIM_REJECTED，且 failed ids 恰等於 must_fail_exactly。
7. 【推論】任何 UNBOUND_SUBJECT、UNSUPPORTED_ISOLATION、HARNESS_ERROR、HARNESS_LIMIT 都保持獨立型別；不得被 negative control 當成預期紅。
8. 【推論】以 canonical ClaimSpec、resolved primitive digest、binding digest、IsolationOffer digest 產生 plan_digest，所有 EvidenceRecord 綁定它。
9. 【推論】測試框架把 actual、positive sensitivity、每個 negative sensitivity 暴露為獨立 test id；人不寫 assertion glue。

【推論】第 6 步有兩層顏色，不可混淆：同一條 claim check 對錯誤 subject 的直接執行必須是紅；外層 sensitivity meta-test 因為成功觀察到指定紅而是綠。若只看外層綠、不保存內層 CLAIM_REJECTED 證據，會重新製造恆真格。

### 5.6 完整 ClaimSpec 範例

【查證】來源句子的 SHA-256 是 08ab53bd5dca1e151924852f5448eb8b5f5f8088c3365397521fb66da6348e17。（來源：對本輪重引的性質 1 原句做 UTF-8 SHA-256。）

【推論】以下是完整、結構上可執行的 v0 instance。實際 subject 由 BindingManifest 提供；兩個 control 是內嵌固定 protocol machine：

    {
      "$schema": "urn:nova:claimspec:schema:0.1",
      "claimspec_version": "0.1.0",
      "claim_id": "execution.wall_limit.external",
      "revision": 1,
      "statement": "wall-clock 上限由 executor 外部強制；逾時後 worker 已死亡，且終態為 TIMED_OUT。",
      "sources": [
        {
          "kind": "REQUIREMENT",
          "uri": "urn:nova:requirements:core",
          "locator": "execution-external-limits",
          "quoted_text": "一次執行要有外部強制的資源上限（時間／回合／花費）與型別化終態；執行者影響不到這兩者。",
          "snapshot_sha256": "08ab53bd5dca1e151924852f5448eb8b5f5f8088c3365397521fb66da6348e17"
        }
      ],
      "primitive_catalog": "claimspec-primitives/0.1.0",
      "subject": {
        "contract": "execution-envelope/1",
        "operation": "run",
        "binding_slot": "system.execution-envelope"
      },
      "parameters": {
        "limit_ms": {
          "type": "DURATION_MS",
          "value": 500
        },
        "grace_ms": {
          "type": "DURATION_MS",
          "value": 250
        },
        "worker_sleep_ms": {
          "type": "DURATION_MS",
          "value": 5000
        },
        "requested_extension_ms": {
          "type": "DURATION_MS",
          "value": 1500
        }
      },
      "setup": [
        {
          "id": "worker",
          "op": "backend.prepare",
          "args": {
            "behavior": "request_limit_extension_ignore_cancel_then_sleep",
            "sleep_ms": {
              "parameter": "worker_sleep_ms"
            },
            "requested_extension_ms": {
              "parameter": "requested_extension_ms"
            }
          }
        }
      ],
      "stimulus": [
        {
          "id": "invocation",
          "op": "subject.invoke",
          "args": {
            "backend": {
              "fixture": "worker"
            },
            "limits": {
              "wall_ms": {
                "parameter": "limit_ms"
              }
            }
          }
        }
      ],
      "observations": [
        {
          "id": "terminal",
          "collector": "invocation.result_field",
          "args": {
            "invocation": "invocation",
            "field": "terminal"
          },
          "result_type": {
            "type": "ENUM",
            "values": [
              "SUCCEEDED",
              "FAILED",
              "TIMED_OUT",
              "BACKEND_ERROR",
              "SUPERVISOR_ERROR"
            ]
          },
          "unit": null,
          "trust_source": "VERIFIER"
        },
        {
          "id": "elapsed_ms",
          "collector": "clock.monotonic_elapsed",
          "args": {
            "from_event": "invocation.started",
            "to_event": "invocation.returned"
          },
          "result_type": {
            "type": "DURATION_MS"
          },
          "unit": "ms",
          "trust_source": "VERIFIER"
        },
        {
          "id": "worker_alive_after_grace",
          "collector": "process.alive_after",
          "args": {
            "fixture": "worker",
            "after_event": "invocation.returned",
            "delay_ms": {
              "parameter": "grace_ms"
            }
          },
          "result_type": {
            "type": "BOOL"
          },
          "unit": null,
          "trust_source": "VERIFIER"
        }
      ],
      "judge": {
        "op": "ALL",
        "args": [
          {
            "id": "typed_timeout",
            "op": "EQ",
            "left": {
              "observation": "terminal"
            },
            "right": {
              "literal": {
                "type": "ENUM",
                "value": "TIMED_OUT"
              }
            }
          },
          {
            "id": "elapsed_bound",
            "op": "LTE",
            "left": {
              "observation": "elapsed_ms"
            },
            "right": {
              "op": "ADD",
              "args": [
                {
                  "parameter": "limit_ms"
                },
                {
                  "parameter": "grace_ms"
                }
              ]
            }
          },
          {
            "id": "worker_reaped",
            "op": "EQ",
            "left": {
              "observation": "worker_alive_after_grace"
            },
            "right": {
              "literal": {
                "type": "BOOL",
                "value": false
              }
            }
          }
        ]
      },
      "controls": {
        "positive": [
          {
            "id": "reference_external_kill",
            "subject": {
              "kind": "PROTOCOL_MACHINE",
              "version": 1,
              "steps": [
                {
                  "op": "backend.start",
                  "args": {
                    "fixture": "worker"
                  }
                },
                {
                  "op": "timer.wait",
                  "args": {
                    "duration_ms": {
                      "parameter": "limit_ms"
                    }
                  }
                },
                {
                  "op": "backend.force_kill",
                  "args": {
                    "fixture": "worker"
                  }
                },
                {
                  "op": "subject.return",
                  "args": {
                    "terminal": "TIMED_OUT"
                  }
                }
              ]
            },
            "expect": "ACCEPT"
          }
        ],
        "negative": [
          {
            "id": "fake_timeout_leaves_worker_running",
            "subject": {
              "kind": "PROTOCOL_MACHINE",
              "version": 1,
              "steps": [
                {
                  "op": "backend.start",
                  "args": {
                    "fixture": "worker"
                  }
                },
                {
                  "op": "timer.wait",
                  "args": {
                    "duration_ms": {
                      "parameter": "limit_ms"
                    }
                  }
                },
                {
                  "op": "subject.return",
                  "args": {
                    "terminal": "TIMED_OUT"
                  }
                }
              ]
            },
            "expect": "CLAIM_REJECTED",
            "must_fail_exactly": [
              "worker_reaped"
            ]
          },
          {
            "id": "worker_controls_deadline",
            "subject": {
              "kind": "PROTOCOL_MACHINE",
              "version": 1,
              "steps": [
                {
                  "op": "backend.start",
                  "args": {
                    "fixture": "worker"
                  }
                },
                {
                  "op": "timer.wait",
                  "args": {
                    "duration_ms": {
                      "parameter": "requested_extension_ms"
                    }
                  }
                },
                {
                  "op": "backend.force_kill",
                  "args": {
                    "fixture": "worker"
                  }
                },
                {
                  "op": "subject.return",
                  "args": {
                    "terminal": "TIMED_OUT"
                  }
                }
              ]
            },
            "expect": "CLAIM_REJECTED",
            "must_fail_exactly": [
              "elapsed_bound"
            ]
          }
        ]
      },
      "run_limits": {
        "wall_ms": 3000,
        "cpu_ms": 1000,
        "memory_bytes": 268435456,
        "max_pids": 16,
        "max_output_bytes": 65536,
        "repetitions": 1,
        "required_accepts": 1
      },
      "isolation": {
        "threat_profile": "COOPERATIVE",
        "required_capabilities": [
          "trusted_monotonic_clock",
          "force_kill_process_tree",
          "process_liveness_probe",
          "ephemeral_workspace",
          "private_raw_evidence",
          "output_reducer"
        ]
      },
      "evidence": {
        "record_observations": [
          "terminal",
          "elapsed_ms",
          "worker_alive_after_grace"
        ],
        "bind_spec_digest": true,
        "bind_subject_digest": true,
        "bind_primitive_catalog_digest": true,
        "raw_visibility": "EVALUATOR_ONLY"
      },
      "feedback": {
        "public_clause_id": "execution.external_limits",
        "reveal_predicate_ids": true,
        "reveal_observed_values": false,
        "reveal_raw_output": false
      },
      "cleanup": [
        {
          "op": "backend.force_kill_if_alive",
          "args": {
            "fixture": "worker"
          }
        }
      ]
    }

【推論】這個例子刻意放兩個反例。第一個抓「回 TIMED_OUT 但背景 worker 還活著」；第二個抓「讓 worker 把 500 ms 上限延到 1500 ms」。只放一個會漏掉另一種作弊。

### 5.7 它生成的檢查

【推論】compiler 不必真的吐出 Python source；較小的 TCB 是產生 immutable TestPlan，再由外部 test-framework adapter 把 plan cases 註冊成測試。概念上生成物等價於：

    plan = compile_claimspec("execution.wall_limit.external", revision=1)

    test "claim::execution.wall_limit.external::actual":
        subject = binding_manifest.resolve("system.execution-envelope")
        result = execute(plan, subject)
        require result.kind == "ACCEPT"

    test "claim::execution.wall_limit.external::positive::reference_external_kill":
        subject = plan.controls.positive["reference_external_kill"]
        result = execute(plan, subject)
        require result.kind == "ACCEPT"

    test "claim::execution.wall_limit.external::negative::fake_timeout_leaves_worker_running":
        subject = plan.controls.negative["fake_timeout_leaves_worker_running"]
        direct = execute_claim_check(plan, subject)
        require direct.kind == "CLAIM_REJECTED"
        require direct.failed_predicates == ["worker_reaped"]

    test "claim::execution.wall_limit.external::negative::worker_controls_deadline":
        subject = plan.controls.negative["worker_controls_deadline"]
        direct = execute_claim_check(plan, subject)
        require direct.kind == "CLAIM_REJECTED"
        require direct.failed_predicates == ["elapsed_bound"]

【推論】direct check 的私有報告應長成：

    FAIL claim::execution.wall_limit.external
    control: fake_timeout_leaves_worker_running
    failure_kind: CLAIM_REJECTED
    failed_predicates: [worker_reaped]
    exit_code: 1

【推論】另一個反例則必須是：

    FAIL claim::execution.wall_limit.external
    control: worker_controls_deadline
    failure_kind: CLAIM_REJECTED
    failed_predicates: [elapsed_bound]
    exit_code: 1

【推論】若錯誤 subject crash、binding 不存在、sandbox 能力不足或 runner timeout，failure_kind 分別是 HARNESS_ERROR、UNBOUND_SUBJECT、UNSUPPORTED_ISOLATION、HARNESS_LIMIT；任何一個都不能滿足 must_fail_exactly。這阻止「反正有非零 exit 就算負控成功」。

### 5.8 ClaimSpec 語言自己的出口條件

【推論】ClaimSpec v0 只有在以下 meta-suite 全綠時才可稱「可用」：

1. 【推論】Meta-schema 自驗：完整例通過；逐一刪掉每個必填欄位都 fail；加入未知欄位也 fail。
2. 【推論】型別檢查：拿 DURATION_MS 和 BOOL 比較、引用不存在 observation、重複 predicate id、controls 引用不存在 must_fail id，全都在執行前 fail。
3. 【推論】Primitive 封閉：未知 action／collector／predicate fail；任何含 shell string、eval、任意 module path 的 spec 都無法通過 schema。
4. 【推論】確定性：同一 spec bytes＋primitive digest＋binding digest 編譯 100 次，plan_digest 完全相同；改任一 threshold 必須改 digest。
5. 【推論】Source binding：quoted_text 改一個 byte 但不改 snapshot_sha256，admission fail。
6. 【推論】正控敏感度：reference_external_kill 的 direct check 為 ACCEPT；把 judge 整棵改成 constant false，positive sensitivity test 必須轉紅。
7. 【推論】負控敏感度：兩個 negative direct checks 分別以 worker_reaped、elapsed_bound 轉紅；把 judge 改成 constant true，negative sensitivity tests 必須轉紅。
8. 【推論】錯誤分類：讓 negative subject crash，meta-test 必須因 HARNESS_ERROR 而紅，不能誤認抓到反例。
9. 【推論】外部觀察：把 elapsed collector 換成 subject self-report，compiler 因 trust_source 不足拒絕；把 process probe 移除，worker leak 負控必須紅。
10. 【推論】外部上限：actual／controls 嘗試改 run_limits、spawn 超量 child、輸出無界資料；runner 仍在上限內停止並回對應 typed harness result。
11. 【推論】隔離協商：刪掉 host 的 process_liveness_probe capability，結果必須是 UNSUPPORTED_ISOLATION；不得執行後假 PASS。
12. 【推論】證據綁定：改 spec、subject、primitive catalog 或 IsolationOffer 任一 byte，EvidenceRecord digest 關係都改；重放舊 verdict 不得匹配新 plan。
13. 【推論】洩漏閘：把 sentinel 放入 raw exception／stdout／fixture，executor-visible feedback 中出現 0 次；透傳 raw reporter 的負控必須紅。
14. 【推論】清理：故意用 fake-timeout control 留 child；完成 observation 後 cleanup 必須殺掉它。拿掉外層 finally，process-tree leak test 轉紅。
15. 【推論】框架適配：至少一個外部測試框架能列出四個獨立 case、保留 direct red evidence，並以整體 exit code 表達 actual 是否通過；不能只印一份人讀報告。

【推論】語言出口與第一條產品 claim 的出口是兩件事。runner＋schema＋controls 可先全綠，證明語言有辨識力；actual subject 在尚未實作或仍有 bug 時應保持 UNBOUND／紅。為了讓「語言完成」看起來漂亮而把 actual skip 掉，會把第一份保證重新變成裝飾。

### 5.9 ClaimSpec v0 的刻意限制

【推論】v0 只承接可在有限 test budget 內觀察的 safety 與 bounded-liveness claim。無界的「最終一定」沒有可執行出口，必須先改寫成「在 X 時間／Y 次 transition 內」或降格為模型檢查。

【推論】v0 不做 arbitrary property language、統計假設檢定、自由 mutation code、跨網路真實副作用或自然語言自動翻譯。每多一項，trusted interpreter 與負控空間都膨脹；第一版先證明三件事即可：觀察真的來自可信面、predicate 真的能拒絕固定錯誤、runner 自己的錯不會被算成候選錯。

【推論】第一份具體檔案的成功標準不是「schema 很完整」，而是同一份 claim 對 reference 綠、對兩個精確反例各以指定 predicate 紅，且 actual implementation 沒達標時也紅。少任何一格，都沒有取得使用者的代理信任。

---

## 6. 本輪對《架構草案》的修正清單

【推論】不直接修改草案；下輪整併時至少要做五項：

1. 【推論】把「分歧的唯一來源」降為「目前已識別、足以解釋投影差異的來源」。
2. 【推論】把三橫向面改為四：判準、資源、效果、知識；內容定址 store 另列基礎設施。
3. 【推論】判準面內保留 Definition／Evaluation 兩支互不代寫的權威。
4. 【推論】確認 Work→Pursuit→Execution，並把 SATISFIED 移到 Work；第一版只限制 Pursuit concurrency=1，不合併資料。
5. 【推論】把「先量 workload」改成「先訂 design envelope，再合成驗證候選」，附上本輪初值與反轉條件。

【推論】如果這五項不改，草案會同時保留三個已知錯誤：把未查證寫成唯一原因、把兩支判準權力合併、以及在沒有 production 的新系統前等待一個永遠不會自己出現的 workload。
