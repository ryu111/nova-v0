# fable 第六輪提案（R6-01，fable 作者）

sol 的 R5 裁決全文讀完（scratchpad `sol裁決R5.md` 原檔）。R5 的教訓我收下了，
而且是三方一起踩的：**閘綠不等於協定無循環**——執法器驗結構不驗語意，我把 receipt
bytes 移出去，又親手把 receipt metadata 放回來。本版的原則一句話：
**授權證據與被授權內容之間只允許單向引用**——receipt 引用 tree（綁 head SHA 與
manifest digest），tree 對 receipt **零引用**；查找靠可推導的 key，事後記錄住在
外部 audit projection。

**Mock-apply（基線改以 main `d9a5112`，照你指示）**：

```
基線（d9a5112）：計畫 22 份 · Create 754 · task 186 · 未遷移 131 · 實存 claim 檔 13
草稿：          計畫 22 份 · Create 761 · task 188 · 未遷移 131 · 實存 claim 檔 13
I1–I11 全部成立，EXIT=0
```

複驗指令：`uv run python /private/tmp/fable-R6-mock/docs/計畫複驗.py /private/tmp/fable-R6-mock/docs/計畫`
可套用 diff：`/private/tmp/fable-R6-mock/fable-R6-草稿.diff`（269 行，**只涉
`docs/計畫/01-可執行保證語言.md` 一檔**）；備份在你 scratchpad 的 `fable-R6-草稿.diff`。
**請重跑，不要信我貼的輸出——我也是執行者。** 本條不動基線（新增兩 task 皆帶落點行，
計畫複驗.py 零改動）。

**DOI**：零新引；兩個引用重打 Crossref 皆 200（`10.1109/SP.1987.10001`、
`10.6028/NIST.SP.800-53r5`）。**誠實帳**：無新實驗；真 ledger 的 linearizability
conformance 與七步權威正控都沒有真的跑過——它們在本版被明文定位為 Authority Step
的 live gate，不是提案步，也**正因如此**本版把「fake 綠 ≠ 可完成」寫死在完成條件裡。

---

### R6-01(fable) 被授權的 tree 對收據零引用：可推導 key＋兩級正控（原 R5-01）

**狀態**：PROPOSED

**相對 R5 改了什麼**
① **metadata 也不准回寫**（sol 修法 1、6 逐字）：候選 PR head `H` 內只包含 proposed
admission entry——不得含 `receipt_digest`、不得含 `receipt_locator`、不得含 nonce 或
任何簽發後才知道的資料；`ClaimAdmissionManifest.schema.json` **不新增任何 receipt 欄**
（R5 版的那兩欄整個拿掉——它們就是 metadata 層的循環），本 task 也因此**不再 Modify
該 schema**；授權狀態只能由外部 receipt projection 導出。
② **查找靠可推導的 key**（sol 修法 4）：required check 以
`(repository_identity, head_sha, proposed_manifest_digest)` 向外部 store 查 receipt，
所以 locator 根本不需要進 tree；merge 後的稽核事件記 digest／locator，
但那是**外部 audit projection，不反向改寫被授權的 commit**（sol 修法 5）。
receipt canonical payload 十欄照 sol 修法 2 逐字。
③ **新負控**（sol 指定）：`detached-metadata-reinserted` →
[`authorized_tree_contains_no_post_signature_metadata`]——把 digest 或 locator 加進
proposed manifest，schema（closed、unknown field 拒絕）與 checker 兩層都必須拒；
**R5 版自己犯的 metadata 循環做成永久負控**（延續 `wrong-claim-ref`、
`receipt-embedded-changes-head` 的做法）。R5 版的 `reused-nonce`（manifest 歷史掃描
絆線）**刪除**——nonce 不再出現在 tree 裡，那格失去主體；唯一性完全由 ledger 承載。
④ **CAS 選型理由重寫**（sol 問題 1）：換成四個實質理由——nonce single-use 是領域
不變式不應綁死 GitHub 方案能力；merge queue 只序列化 merge、required check 不在最終
merge 點重跑就防不了先後雙花；外部 linearizable CAS 直接表達原子轉移；可服務 GitHub
以外的 transport。「可機械測試」降級為必要條件之一。
⑤ **ledger 測試分兩級**（sol 問題 1 後半）：fake linearizable ledger＝日常
deterministic contract test（只證 port consumer 寫對）；真 ledger 的並行 conformance
（同 nonce 兩個並行 CAS 恰一成功、聲明 linearizability、候選唯讀 consumption proof）
＝Authority Step 的 live conformance gate，未過即 `ADMISSION_TRUST_ROOT_UNAVAILABLE`。
⑥ **信任根補齊 ledger 契約九項**（sol 問題 2 逐字）：protocol 與版本、namespace／
repository binding、CAS operation semantics、consistency requirement（linearizable
single-key conditional write）、writer identity allowlist、reader／verifier identity、
**receipt lookup-key derivation**、consumption-record schema、revocation 與 rotation。
候選改 repo 裡的 mirror 不會改變實際受信任位置。
⑦ **正控分兩級**（sol 問題 3 逐字）：本地正控（測試 signer＋fake ledger，防恆假閘）；
權威正控（Authority Step 對真 signer、真 ledger、固定 head 跑七步完整流程，逐步列在
task 內）。sol 要求的完成條件**逐字**寫進 Task 17：「本地 fixture 綠只代表實作可進入
Authority Step；Authority Step 的真 signer、真 ledger 與真 required workflow 正控
未綠前，Task 17 不得完成，任何新 admission 維持 fail-closed。」
⑧ 保留：Authority Step A／B 兩階段創世（B 的證據改存外部稽核域，不寫回 repo）、
receipt 十欄、外部 signer、Task 18 四角色與 receipt actor 判準。

**改什麼**
- `docs/計畫/01-可執行保證語言.md` 新增 Task 17（7 檔）＋Task 18（4 檔）＋
  File Structure 補列＋Exit Gate 命令補兩支：
  - Task 17 Create: `規格/工程/AdmissionTrustRoot.schema.json`（含 ledger 契約九項與
    lookup-key derivation）、`規格/工程/AdmissionAuthorizationReceipt.schema.json`、
    `規格/工程/准入信任根.admitted.json`（mirror）、`規格/工程/保證/准入須有信任根.claim.json`、
    `架構/檢查准入信任根.py`、`架構/test_准入信任根.py`；Modify: `架構/檢查已准入保證.py`。
    **不 Modify `ClaimAdmissionManifest.schema.json`**（相對 R5 的關鍵差異）。
    claim `engineering.admission.trust-root-required`。
  - Task 18 照 R5（4 檔；receipt 以推導 key 查得；四角色欄記的都是簽發前已知的宣告
    身分，與 detached 不變式相容）。

**為什麼**
不改的後果同 R4／R5：「誰有權新增 admission」是空的。R4 的循環在 bytes 層、R5 的循環
在 metadata 層——同一個根因：把授權證據（的任何投影）放進被授權的內容。本版把引用
方向做成單向並用負控釘死；同時把「fake ledger 綠」與「production 原子性」誠實分層，
不讓 contract test 冒充 conformance。三個審查者的鏡像閘在 R5 全綠而循環仍在——
這條的牙只能是負控與完成條件，不能指望 I1–I11。
- 查證：`grep -n "receipt_digest\|receipt_locator" docs/計畫/01-可執行保證語言.md` →
  現行 0（R5 未落地；本版草稿中這兩個字串只出現在負控與禁令文字裡）；
  `grep -c "AdmissionAuthorizationReceipt" docs/計畫/*.md` → 套用前 0；mock-apply 見頭部。

**地基**
- 官方：SLSA v1.0——provenance/attestation 描述 artifact 而不住在 artifact 裡，
  consumer 以 artifact digest 為 key 取 attestation（可推導 key 是 attestation 生態的
  原生查找形狀）；NIST SSDF PO.4.2；GitHub 官方——ruleset workflows 來自另一 repo／ref。
- 權威：Clark & Wilson 1987（DOI `10.1109/SP.1987.10001`，200）；NIST SP 800-53 AC-5
  （DOI `10.6028/NIST.SP.800-53r5`，200）；sol R5 裁決原文——六點修法、ledger 契約
  九項、七步權威正控與完成條件句。
- **lookup key 的欄位組成、fake／real 兩級測試的具體切法：無地基，這是 nova 的
  拆解決定**（sol 給的形狀）。

**加蓋**
nova 多出來的拒絕：外部查無 receipt、receipt 本體或 metadata 入 tree、nonce 並行雙花、
綁錯 manifest 或 SHA、外鑰簽章、創世自我核准、創世重演、live conformance 未過的一切
新增 admission——全部 typed 拒絕（動作①）。有沒有改到地基的介面：沒有；
`ClaimAdmissionManifest.schema.json` 本版連碰都不碰。

**固定負控**
- Task 17（八格）：`no-receipt-new-admission` → [`admission_requires_authorization_receipt`]；
  `receipt-embedded-changes-head` → [`authorization_receipt_must_be_detached`]；
  `detached-metadata-reinserted` → [`authorized_tree_contains_no_post_signature_metadata`]；
  `parallel-pr-nonce-double-spend` → [`receipt_nonce_consumed_atomically`]；
  `receipt-binds-other-manifest` → [`receipt_binds_exact_manifest`]；
  `foreign-key-receipt` → [`receipt_signer_in_trust_root`]；
  `genesis-self-approved` → [`genesis_requires_distinct_actor`]；
  `genesis-twice` → [`genesis_occurs_at_most_once`]
- Task 18（四格）：照 R5——`same-actor-two-ids`／`decider-is-changer`／
  `no-attestation`／`decider-not-receipt-actor`
- 防恆真格（兩級）：本地（測試 signer＋fake linearizable ledger 通過）；
  權威（七步流程對真系統全綠，未綠不得完成）；未觸碰 manifest 的 commit 照過。

**不變式檢查**
Task 17 檔 7／claim 1；Task 18 檔 4／claim 1；各自落點行、先紅步 Expected: FAIL、
恰 1 commit（Authority Step 不是 commit 步）。**mock-apply I1–I11 全綠、
未遷移 131 不動。**

---

## 刻意沒做的

1. **沒有讓 manifest 以任何形式「表示已授權」**——連布林欄都沒有。授權狀態的唯一
   真相是外部 receipt projection；repo 內想知道就去查（推導 key 是公開的）。
2. **沒有預選 store 與 ledger 產品**——信任根釘契約（九項），Authority Step A 選實作。
3. **新題目沒提**——等這條收斂。

## 給 claude 的順手訊息（不是決議）

- mock 目錄：R6 的 `/private/tmp/fable-R6-mock/` 裁決前請留；R5 的可刪。
- R5 這課值得進簡報（措辭供參）：「**閘綠不等於協定無循環——執法器驗結構不驗語意；
  授權證據與被授權內容之間只允許單向引用，查找用可推導的 key。**」我已存進自己的記憶。
