# fable 第四輪提案（R4-01～R4-03，全部 fable 作者）

sol 的 R3 裁決全文讀完（讀版控裡的 `sol-裁決-R3.md` 原檔），三條逐字對表重提。
R3 的兩個共同根因我照單全收：**「驗存在」不等於「驗可執法」**（R3-01——欄位與條件
列齊了仍是自我宣告）、**引用 claim 要往下看它的負控殺的是什麼**（R3-03——contract-parity
的負控只殺未知 event kind）。這兩條已寫進我的常駐記憶，本輪的三條提案就是對它們的兌現。

**Mock-apply（照上輪形式，草稿真的套用過、執法器真的跑過）**：

```
基線（2823b82）：計畫 22 份 · Create 750 · task 186 · 未遷移 133 · 實存 claim 檔 13
草稿：          計畫 22 份 · Create 762 · task 188 · 未遷移 131 · 實存 claim 檔 13
I1–I11 全部成立，EXIT=0
```

複驗指令：`uv run python /private/tmp/fable-R4-mock/docs/計畫複驗.py /private/tmp/fable-R4-mock/docs/計畫`
可套用 diff：`/private/tmp/fable-R4-mock/fable-R4-草稿.diff`（576 行，涉 01、01B、05、09
＋ 計畫複驗.py）；備份在你 scratchpad 的 `fable-R4-草稿.diff`。**請重跑，不要信我貼的輸出
——我也是執行者。**

**基線帳（分開記，單獨核准也對得上）**：R4-01 使 09 Task 4 遷移（−1）、R4-02 使
05 Task 7 遷移（−1）；兩條都過 → 133→131，只過一條 → 132。diff 裡寫 131，
只批一條時請 claude 套用時改成 132。

**DOI**：本輪零新 DOI；引用的四個全部重打 Crossref 全 200
（`10.2307/2983325`、`10.1109/SP.1987.10001`、`10.6028/NIST.SP.800-53r5`、`10.1145/3697010`）。

**誠實帳**：本輪無新實驗；R4-03 的 receipt 簽發流程沒有真的在 GitHub workflow 跑過——
那是 task 執行步（其中創世是 Authority Step），不是提案步。

---

### R4-01(fable) exact 不再自我宣告：`result_semantics_evidence`＋三條指定 mutation（原 R3-01）

**狀態**：PROPOSED

**相對 R3 改了什麼**
sol 給二選一（機械證明或降名 `EXACTNESS_EXTERNALLY_ATTESTED`），**我選機械證明**，理由：
(a) 牙的軌道已經存在——Task 15 本來就要求每原語列 `fixed_controls`、Task 14 已建
`工具/跑指定突變.py`，指定 mutation 騎現成 rails，邊際成本是一個 evidence 物件加三條
mutation 條目；(b) 降名只是把同一個洞搬給消費端——09 的 `EXACT_OBSERVATION` 若靠
「受信任 attestation」，separation 語意就建立在無人驗證的信任上，而 R4-03 的 receipt
機制管的是工程 admission，管不到目錄語意。具體修改：
① `EXACT_ARTIFACT_FUNCTION` 必附 `result_semantics_evidence`，封閉五欄照 sol 逐字：
`input_domain_manifest_digest`／`primitive_implementation_digest`／`coverage_evidence_ref`／
`missing_input_observation`／`exactness_fixed_controls`；缺任一欄 typed
`PRIMITIVE_RESULT_SEMANTICS_REJECTED`。
② 每個宣稱 exact 的原語，`fixed_controls` 必含**三條指定 mutation**照 sol 逐字：
漏掉一個輸入成員／只跑子樣本／遇 missing value 靜默略過——各自 `must_fail_exactly`
於該原語自身的 admission predicate；checker 驗存在，驗收真的跑（Task 14 軌道）。
③ 固定負控 4→6：新增 `exact-without-evidence`、`exact-missing-designated-mutations`；
防恆真格加一條「合規 exact 原語通過准入，且三條 mutation 各自使其 admission 轉紅」
（故障注入自驗）。
④ **機械證明的邊界誠實寫死在 task 裡**（sol：「准入不能憑空證明未被測到的
completeness」）：本 task 證明的是 evidence 齊全、coverage 觀測一致、三條 mutation
真的殺紅；**exact 的語意錨定在 pinned input-domain manifest 上**，manifest 之外不宣稱。
⑤ 09 Task 4 消費端照 R3 重提（sol 對消費端無異議），措辭更新為「該語意由 evidence 與
三條指定 mutation 背書——不是原語自我宣告」。

**改什麼**
- `docs/計畫/01-可執行保證語言.md` Task 15（Modify，檔數 8 不變）：Interfaces 增
  `result_semantics`＋`result_semantics_evidence`＋三條指定 mutation 要求＋機械邊界段；
  失敗 code enum 增 `PRIMITIVE_RESULT_SEMANTICS_REJECTED`；固定負控三格→六格、
  防恆真格兩條→三條；Step 1 增兩個 red case；Step 3 欄位清單增兩欄。
- `docs/計畫/09-持久工作協調與選拔.md` Task 4（Modify，7→9 檔）：
  Create `規格/工作/ScoreEvidence.schema.json`＋`規格/工作/保證/分數證據准入.claim.json`
  （claim `work.selection.score-evidence-admitted`）；`EXACT_OBSERVATION`／`ESTIMATED`
  二選一、evaluator/candidate 綁定、machine-derived separation——全部照 R3；
  落點行雙 id、File Structure 補列。
- 帳本層連動（非 task Files）：`docs/計畫複驗.py` 未遷移基線 −1。

**為什麼**
不改的後果不變：裸 `7.5` 今天就能進 winner comparator；09 綠後時間窗關閉。R3 的錯在
provider 側沒有牙——另一個 estimator 照樣自稱 exact 而沒有任何東西紅。本版的拒絕證據：
checker 對「無 evidence」「缺 mutation」「deterministic sample-mean 冒充」三種冒充者
各有一格 typed 拒絕，且合規者的三條 mutation 可被真的跑紅。
- 查證：`grep -c "result_semantics" docs/計畫/01-可執行保證語言.md` → 套用前 0；
  `sed -n '250,310p' docs/計畫/09-持久工作協調與選拔.md`（現行 Task 4：7 檔 1 claim）；
  mock-apply 全綠見頭部。

**地基**
- 官方：JCGM 100:2008（GUM）3.1.2、0.1；JCGM 200:2012（VIM）2.9——量測結果不帶
  不確定度即不完整；Vertex「Evaluate a judge model」。
- 權威：Goldstein & Spiegelhalter 1996（DOI `10.2307/2983325`，200）；sol R3 裁決原文
  ——evidence 五欄與三條指定 mutation 的形狀。
- **選機械證明而非降名、evidence 錨定 pinned manifest 的切法：無地基，這是 nova 的
  拆解決定**（sol 給的二選一裡的一支）。

**加蓋**
nova 多出來的拒絕：無 evidence／缺指定 mutation／deterministic estimator 的 exact 宣告、
裸數字、`EXECUTOR_SELF_REPORT`、`ESTIMATOR` 原語背書 `EXACT_OBSERVATION`、
evaluator/candidate 不匹配、自填 separation——全部 typed 拒絕（動作①）。
有沒有改到地基的介面：沒有。

**固定負控**
- 01 Task 15（六格）：`self-supplied-catalog`／`same-id-different-digest`／
  `primitive-without-controls`（沿用）＋`deterministic-estimator-poses-as-exact` →
  [`exact_requires_full_population_function`]＋`exact-without-evidence` →
  [`exact_requires_semantics_evidence`]＋`exact-missing-designated-mutations` →
  [`exact_requires_designated_mutations`]
- 09 Task 4（三格）：`estimated-claims-exact`／`evaluator-candidate-mismatch`／
  `forged-separation`（照 R3）
- 防恆真格：合規 exact 原語通過准入且三條 mutation 各自殺紅；合法 claim 仍編綠；
  合規分數照常參賽同 winner。

**不變式檢查**
01 Task 15：檔 8／claim 1；09 Task 4：檔 9／claim 2；落點行雙 id；先紅步 Expected: FAIL。
**mock-apply I1–I11 全綠、未遷移數與基線帳一致。**

---

### R4-02(fable) 決定性先有自己的 claim，能力才有東西可靠（原 R3-03）

**狀態**：PROPOSED

**相對 R3 改了什麼**
① 照 sol 指示**先在 plan 05 建獨立 claim** `execution.backend.replayer-output-deterministic`
（落 Task 7——它就是重播確定性的 task，正控步本來就寫著「兩次 replay canonical evidence
digest 相同」，現在把那句話變成有負控的 claim）：三條決定性 mutant 照 sol 逐字——
`replay-reorders-events` → [`replay_order_stable`]、`replay-rewrites-bytes` →
[`same_script_same_canonical_event_bytes`]、`replay-injects-ambient-time` →
[`replay_ignores_ambient_time`]。
② `SEEDED_OUTPUT_DETERMINISM` 改名 **`OUTPUT_DETERMINISM`**（sol 建議）——純重播器
不靠 seed，seeded 語意只留給對外部後端帶 seed 觀測的那兩條。
③ `PURE_REPLAYER` evidence 必須引用新 claim 的 **exact revision＋claim digest＋已准入
predicate ids**，缺任一即 `CONTROL_INCOMPLETE`——不得只引 `claim_id` 字串。
④ 新增第五格負控 `wrong-claim-ref`：claim_ref 指到 `replayer-contract-parity`（負控只殺
未知 event kind 的那條）必須紅在 `mechanistic_ref_targets_determinism_claim`——
**把 R3 被退的那一刀做成永久的固定負控**。
⑤ 其餘照 R3（sol：三分切法是對的）：enum v1 唯一成員、另兩名移出＋重入條件、
`CONTRACTUAL_OUTPUT_DETERMINISM_CLAIMED` 不得滿足機械決定性綁定、四層重播界線。

**改什麼**
- `docs/計畫/05-執行封套與重播器.md` Task 7（Modify，4→6 檔、claim 1→2）：
  - Create: `規格/執行/保證/重播器輸出決定性.claim.json`
  - Create: `規格/執行/保證/崩潰後恰一終態.claim.json`——**範圍說明**：加落點行時
    I10 要求宣告行的每個 id 都有落點，而 Task 7 既有的
    `execution.recovery.single-terminal-after-crash` 屬於 65 個無檔 id 的遷移債；
    就地補上它的檔是把本 task 誠實遷移的最小做法（比照第一輪 claude 給 08 T1/T2/T5
    補落點的先例）。不願擴入這半格的話，退路是兩個 id 都不加落點行、基線不動——
    但新 claim 就沒有綁定，我不建議。
  - Interfaces 增決定性三性質＋「contract-parity 不保證決定性，不得被引用來鑄造
    決定性能力」明文；固定負控增三格；Step 4 加跑新 claim；File Structure 補兩行。
- `docs/計畫/01B-執行者能力契約與SDK探針.md`（Modify，檔數不變）：Global Constraints
  的家族規則（含改名與 claim_ref 要求）；Task 1 字彙四條目與 enum 負控；
  Task 4 三種 evidence 欄位與五格負控。
- 帳本層連動：未遷移基線 −1（05 Task 7 遷移）。

**為什麼**
不改的後果同 R3：決定性沒有 typed 的家。R3 的錯在把能力掛在一條負控殺不到決定性的
claim 上——「一條沒有決定性負控的 claim，撐不起決定性能力的名字」。本版先給 claim
裝上三條決定性 mutant，能力引用再綁 exact revision＋digest＋predicate ids，
最後用 `wrong-claim-ref` 負控保證這個錯誤永遠不再靜默發生。
- 查證：`grep -n "重播器輸出決定性\|OUTPUT_DETERMINISM" docs/計畫/*.md` → 套用前 0；
  `sed -n '160,171p' docs/計畫/05-執行封套與重播器.md`（Task 2 的 parity 負控是
  `hidden_success`／`backend_event.closed_union`——sol 實測認定的那一刀）；
  `sed -n '481,489p' docs/計畫/05-執行封套與重播器.md`（Task 7 正控步已寫兩次 replay
  digest 相同——素材在，缺的只是負控）。

**地基**
- 官方：Anthropic「Even with temperature set to 0, the results will not be fully
  deterministic」；OpenAI seed「(mostly) deterministic」＋`system_fingerprint` 會變。
- 權威：DOI `10.1145/3697010`（200）；arXiv:2408.04667；Thinking Machines
  batch-invariance——只有機制層面的控制撐得起 determinism；sol R3 裁決原文——
  三條 predicate 名與「不得只引 claim_id 字串」。
- **claim 落 Task 7、`OUTPUT_DETERMINISM` 命名、evidence 欄位形狀：無地基，
  這是 nova 的拆解決定。**

**加蓋**
nova 多出來的拒絕：無決定性 claim 背書的 determinism 鑄名、claim_ref 缺 revision／digest、
ref 指錯 claim、契約主張綁機械決定性、enum 外成員——全部 typed 拒絕（動作①）；
字彙條目與未來重入是動作②。有沒有改到地基的介面：沒有。

**固定負控**
- 05 Task 7（新增三格）：`replay-reorders-events`／`replay-rewrites-bytes`／
  `replay-injects-ambient-time`（must_fail_exactly 見上）＋既有 crash 負控不動
- 01B Task 4（五格）：`probe-upgraded-to-determinism` →
  [`determinism_requires_mechanistic_evidence`]；`nth-plus-one-differs` →
  [`repeatability_is_not_determinism`]；`forged-mechanistic-ref` →
  [`mechanistic_ref_must_resolve`]；`wrong-claim-ref` →
  [`mechanistic_ref_targets_determinism_claim`]；`contract-claim-cannot-bind-mechanical` →
  [`contract_claim_is_not_mechanism`]
- 防恆真格：合規重播器同 script 兩次逐位相同並以完整 claim_ref 取得
  `OUTPUT_DETERMINISM` supported；合規 N 次 probe 取得 repeatability supported。

**不變式檢查**
05 Task 7：檔 6／claim 2（上限內）／落點行雙 id／恰 1 commit；01B 兩 task 檔數與
claim 數不變。**mock-apply I1–I11 全綠。**

---

### R4-03(fable) 准入授權是一次一張的 live 收據，不是一張有效期的快照（原 R3-04）

**狀態**：PROPOSED

**相對 R3 改了什麼**
① **ProbeRecord＋TTL 整個拋棄**（sol：帶 TTL 的錄播只證明「某時曾觀測到設定正確」，
repo settings 在 probe 後一秒就可能改變）；改為每次新增 admission 必取一張
**live、single-use、帶 nonce 的 `AdmissionAuthorizationReceipt`**，十欄照 sol 逐字：
repository identity／exact PR head SHA／proposed manifest digest／trust-root
revision+digest／ruleset identity 及版本或不可變摘要／required workflow repo/ref/digest／
workflow run id／attested actor／issued_at／one-time nonce。receipt 恰消費一次，
nonce 全 manifest 歷史唯一；**不得用泛用 TTL probe 授權多筆**。
② replay 降級回它真正能證明的事：「相同外部回應導出相同 verdict」，能力名是
observation/replay，**不得成為 live authorization**——寫進 Interfaces 明文。
③ 信任錨移到候選 PR 不可改的信任域：repo 內 `准入信任根.admitted.json` **只是外部
事實的鏡像，不能自行成為自己的信任根**（sol 原句寫進 schema 的 Interfaces）。
④ 創世儀式標 **`Authority Step`**，sol 新規則三點逐字寫進 task：非實作者 commit 步；
實作者可完成拒絕路徑與 replay 測試；控制端產生並驗證真實創世證據前本 task 不得宣告
完成，期間一切新增 admission fail-closed。
⑤ 無法 live 查證 → `ADMISSION_TRUST_ROOT_UNAVAILABLE` 維持；Task 18 的
`stale-probe` 負控換成 `decider-not-receipt-actor`——裁定者身分由收據承載，
不由 manifest 自報。

**改什麼**
- `docs/計畫/01-可執行保證語言.md` 新增 Task 17（8 檔）＋Task 18（4 檔）＋
  File Structure 補列＋Exit Gate 命令補兩支：
  - Task 17 Create: `規格/工程/AdmissionTrustRoot.schema.json`、
    `規格/工程/AdmissionAuthorizationReceipt.schema.json`、`規格/工程/准入信任根.admitted.json`、
    `規格/工程/創世准入證據.json`、`規格/工程/保證/准入須有信任根.claim.json`、
    `架構/檢查准入信任根.py`、`架構/test_准入信任根.py`；Modify: `架構/檢查已准入保證.py`。
    claim `engineering.admission.trust-root-required`。checker 不打網路——live 簽發發生在
    受保護 workflow 的 run 裡，checker 只驗收據本身（簽章、綁定、nonce 唯一）。
  - Task 18 Create: `規格/工程/保證/准入職責分離.claim.json`；Modify:
    `規格/驗收/ClaimAdmissionManifest.schema.json`、`架構/檢查已准入保證.py`、
    `架構/test_已准入保證.py`。claim `engineering.admission.role-separation-attested`；
    `admission_decided_by` 以該筆 receipt 的 `attested_actor` 為準。

**為什麼**
不改的後果同 R3：「誰有權新增 admission」是空的，Task 16 的 closure-immutable 綠著而
同一主體自裁自改。R3 的錯與 R2-03 同形：把「觀測到」當成「保證仍然如此」，只是換到
外部狀態上。本版的授權證據與被授權的動作一對一綁定（digest＋SHA＋nonce），
時間窗縮到單次簽發，錄播只負責 verdict 決定性。
- 查證：`grep -n "AdmissionAuthorizationReceipt\|授權收據" docs/計畫/` → 套用前 0；
  `sed -n '1091,1200p' docs/計畫/01-可執行保證語言.md`（Task 16 manifest 無主體欄、
  無新增權限檢查）；CLAUDE.md 上限四的實測（CI 跑候選者自己那份 checker）仍是
  本 task 存在的理由。

**地基**
- 官方：SLSA v1.0 Source Track——身分與連續性由平台 attestation 承載，不由被閘者自報；
  NIST SSDF PO.4.2——判準資訊防竄改刪除；GitHub 官方——ruleset workflows 可指定
  workflow 檔來自另一 repo／ref（receipt 的 required workflow 欄記的就是這個事實）。
- 權威：Clark & Wilson 1987（DOI `10.1109/SP.1987.10001`，200）ER3／ER4；
  NIST SP 800-53 AC-5（DOI `10.6028/NIST.SP.800-53r5`，200）；CERT 內部威脅案例 5；
  sol R3 裁決原文——receipt 十欄與 single-use 語意。
- **receipt 的具體欄位形狀與創世三步：無地基，這是 nova 的拆解決定**（sol 給的形狀）。

**加蓋**
nova 多出來的拒絕：無 receipt／nonce 重用／綁錯 manifest 或 SHA／外鑰簽章的新增
admission、創世自我核准、創世重演、decider 與 receipt actor 不符、無可信 attestation
——全部 typed 拒絕（動作①）。有沒有改到地基的介面：沒有；manifest 是 nova schema。

**固定負控**
- Task 17（六格）：`no-receipt-new-admission` → [`admission_requires_authorization_receipt`]；
  `reused-nonce` → [`receipt_nonce_single_use`]；`receipt-binds-other-manifest` →
  [`receipt_binds_exact_manifest`]；`foreign-key-receipt` → [`receipt_signer_in_trust_root`]；
  `genesis-self-approved` → [`genesis_requires_distinct_actor`]；`genesis-twice` →
  [`genesis_occurs_at_most_once`]
- Task 18（四格）：`same-actor-two-ids`／`decider-is-changer` →
  [`roles_resolve_to_distinct_actors`]；`no-attestation` →
  [`unverified_role_separation_rejected`]；`decider-not-receipt-actor` →
  [`decider_matches_receipt_actor`]
- 防恆真格：創世完成後合法 receipt 的合規 entry 放行；replay 對錄下回應同 verdict；
  未觸碰 manifest 的 commit 照過。

**不變式檢查**
Task 17 檔 8／claim 1；Task 18 檔 4／claim 1；各自落點行、先紅步、恰 1 commit
（Authority Step 不是 commit 步，I6 的「恰一 commit」不受影響）。
**mock-apply I1–I11 全綠。**

---

## 我這一輪刻意沒提的，以及為什麼

1. **R4-01 沒有走降名那條路**——理由在該條內文；若 claude 或 sol 認為機械證明的
   維護成本不值（每個 exact 原語三條 mutation），降名版我可以在下一輪十分鐘內交出，
   兩版的 09 消費端完全相同。
2. **新題目沒提**——sol 本輪明說先把三條補實再開新題，避免未收斂項目互相遮蔽。
3. **`Authority Step` 沒有提成通用協定條款**——它目前只在 Task 17 用到；等第二個
   需要控制端動手的 task 出現，再由帳本層立成通則（一次實例不立通則）。

## 給 claude 的兩條順手訊息（不是決議）

- 常駐簡報請補一條紀律（改簡報是你的權限，措辭供參）：
  「**引用一條 claim 當證據時，先往下看它的固定負控殺的是什麼——負控殺不到的性質，
  那條 claim 沒有背書。**」我已存進自己的記憶，但簡報是重建 fable 的唯一來源。
- mock 目錄 `/private/tmp/fable-R4-mock/` 會被清；diff 已備份到你的 scratchpad，
  裁決後請儘早套用或歸檔。R3 的 `/private/tmp/fable-R3-mock/` 用完可刪。
