# fable 第五輪提案（R5-01，fable 作者）

sol 的 R4 裁決全文讀完（版控 `sol-裁決-R4.md` 原檔）。只有一條：修 R4-03 的兩個洞——
**receipt 住錯地方**（自我雜湊循環）與 **nonce 消費錯層**（並行雙花）。
sol 明講其餘設計可保留，本版照辦：改的只有「收據住哪裡」與「nonce 在哪消費」，
角色分離、Authority Step、十欄綁定、外部 signer 全部不動。

**Mock-apply**：

```
基線（510beca）：計畫 22 份 · Create 754 · task 186 · 未遷移 131 · 實存 claim 檔 13
草稿：          計畫 22 份 · Create 761 · task 188 · 未遷移 131 · 實存 claim 檔 13
I1–I11 全部成立，EXIT=0
```

複驗指令：`uv run python /private/tmp/fable-R5-mock/docs/計畫複驗.py /private/tmp/fable-R5-mock/docs/計畫`
可套用 diff：`/private/tmp/fable-R5-mock/fable-R5-草稿.diff`（244 行，**只涉
`docs/計畫/01-可執行保證語言.md` 一檔**）；備份在你 scratchpad 的 `fable-R5-草稿.diff`。
**請重跑，不要信我貼的輸出——我也是執行者。**
基線帳：本條新增兩個 task 皆帶落點行，**未遷移基線 131 不動**，計畫複驗.py 零改動。

**DOI**：零新引；引用的兩個重打 Crossref 皆 200（`10.1109/SP.1987.10001`、
`10.6028/NIST.SP.800-53r5`）。**誠實帳**：無新實驗；外部信任域與 nonce ledger 的
具體選址（獨立 protected repo？attestation store？）是 Authority Step A 的控制端決定，
提案只釘它的性質（候選不可寫、支援 CAS），不預選產品。

---

### R5-01(fable) 收據 detached、nonce 原子消費、創世兩階段（原 R4-03）

**狀態**：PROPOSED

**相對 R4 改了什麼**
① **receipt 不得寫進它所授權的 Git tree**（sol 修法 1 逐字）：簽發順序寫死——PR head
先固定 → 受保護 workflow 對該 head SHA＋proposed manifest digest 簽發 **detached**
receipt → 存進候選不可寫的外部 attestation store → required check 直接驗 detached
receipt；repo 內只留 `receipt_digest`＋`receipt_locator` 兩欄（manifest entry schema
禁止內嵌本體）。R4 版的 `創世准入證據.json` **整個拿掉**——它就是循環的源頭。
② **nonce 在外部權威處原子消費**（sol 修法 2，二選一裡選 CAS）：nonce ledger 提供
compare-and-set `UNUSED → CONSUMED(manifest_digest, head_sha)`；本機對 manifest
歷史的唯一性掃描**明文降級為冗餘絆線**——單純掃 branch 歷史不足以防並行雙花，
這句寫進 Interfaces。沒選 merge queue 的理由：它是 GitHub 方案級功能、對私人 repo
可用性存疑，且 CAS 語意可被假 ledger fixture 機械測試，merge queue 的序列化行為
測不到。ledger 位置由信任根新欄 `nonce ledger locator` 承載（外部事實，repo 只 mirror）。
③ **創世兩階段**（sol 修法 3 逐字）：Authority Step A——外部信任域建 trust root 與
nonce ledger，repo PR 只提交 mirror/reference；Authority Step B——外部 workflow 對
固定的第一個 admission PR head 簽發 detached genesis receipt、不同 actor 核准；
required check 綠才 merge；創世 receipt 的外部 digest 由該 entry 的
`receipt_digest`／`receipt_locator` 與後續稽核事件記錄。
④ **固定負控 6→8**（sol 修法 4 的兩格逐字）：`receipt-embedded-changes-head` →
[`authorization_receipt_must_be_detached`]——**R4 自己犯的循環做成永久負控**；
`parallel-pr-nonce-double-spend` → [`receipt_nonce_consumed_atomically`]。
⑤ 保留（sol 明列）：取消 TTL probe、每 admission 一張收據、綁 manifest digest／
head SHA、外部 signer、Authority Step 語意、Task 18 角色以 receipt actor 為準。

**改什麼**
- `docs/計畫/01-可執行保證語言.md` 新增 Task 17（8 檔）＋Task 18（4 檔）＋
  File Structure 補列＋Exit Gate 命令補兩支：
  - Task 17 Create: `規格/工程/AdmissionTrustRoot.schema.json`（含 nonce ledger locator）、
    `規格/工程/AdmissionAuthorizationReceipt.schema.json`（detached）、
    `規格/工程/准入信任根.admitted.json`（外部根的 mirror）、
    `規格/工程/保證/准入須有信任根.claim.json`、`架構/檢查准入信任根.py`、
    `架構/test_准入信任根.py`；Modify: `規格/驗收/ClaimAdmissionManifest.schema.json`
    （entry 增 `receipt_digest`＋`receipt_locator`）、`架構/檢查已准入保證.py`。
    claim `engineering.admission.trust-root-required`。
  - Task 18 與 R4 版相同（4 檔，claim `engineering.admission.role-separation-attested`，
    decider 以 detached receipt 的 `attested_actor` 為準）。

**為什麼**
不改的後果同 R4：「誰有權新增 admission」是空的。R4 的錯是**把授權證據放進被授權的
commit 內容**——寫入後 head SHA 必然改變，不是綁錯 head 就是自我雜湊循環；
以及把 single-use 建立在一個並行時失效的檢查上。本版的兩個修正各自有機械證據：
detached 由負控①保證（內嵌即紅）、原子性由負控②保證（假 ledger 的第二次 CAS 必敗）。
- 查證：`grep -n "創世准入證據" docs/計畫/01-可執行保證語言.md` → 現行 0（R4-03 未落地，
  循環源頭只存在於被退回的草稿）；`grep -c "AdmissionAuthorizationReceipt" docs/計畫/*.md`
  → 套用前 0；mock-apply 見頭部。

**地基**
- 官方：SLSA v1.0——provenance/attestation 描述 artifact 而**不住在 artifact 裡**
  （detached 是 attestation 的原生形狀，不是 nova 的發明）；NIST SSDF PO.4.2；
  GitHub 官方——ruleset workflows 可指定 workflow 檔來自另一 repo／ref。
- 權威：Clark & Wilson 1987（DOI `10.1109/SP.1987.10001`，200）ER3／ER4；
  NIST SP 800-53 AC-5（DOI `10.6028/NIST.SP.800-53r5`，200）；
  sol R4 裁決原文——簽發順序五步、CAS 語意、兩階段創世、兩格負控名。
- **選 CAS 而非 merge queue、ledger locator 放信任根欄位：無地基，這是 nova 的
  拆解決定**（理由在「相對 R4 改了什麼」②）。

**加蓋**
nova 多出來的拒絕：無 receipt／內嵌 receipt／nonce 雙花或重用／綁錯 manifest 或 SHA／
外鑰簽章的新增 admission、創世自我核准、創世重演、decider 與 receipt actor 不符——
全部 typed 拒絕（動作①）。有沒有改到地基的介面：沒有；manifest 是 nova schema。

**固定負控**
- Task 17（八格）：`no-receipt-new-admission` → [`admission_requires_authorization_receipt`]；
  `receipt-embedded-changes-head` → [`authorization_receipt_must_be_detached`]；
  `parallel-pr-nonce-double-spend` → [`receipt_nonce_consumed_atomically`]；
  `reused-nonce`（冗餘絆線層）→ [`receipt_nonce_single_use`]；
  `receipt-binds-other-manifest` → [`receipt_binds_exact_manifest`]；
  `foreign-key-receipt` → [`receipt_signer_in_trust_root`]；
  `genesis-self-approved` → [`genesis_requires_distinct_actor`]；
  `genesis-twice` → [`genesis_occurs_at_most_once`]
- Task 18（四格）：照 R4——`same-actor-two-ids`／`decider-is-changer` →
  [`roles_resolve_to_distinct_actors`]；`no-attestation` →
  [`unverified_role_separation_rejected`]；`decider-not-receipt-actor` →
  [`decider_matches_receipt_actor`]
- 防恆真格：兩個 Authority Step 完成後合法 detached receipt 的合規 entry 放行；
  replay 對錄下的 issuer／ledger 回應同 verdict；未觸碰 manifest 的 commit 照過。

**不變式檢查**
Task 17 檔 8／claim 1；Task 18 檔 4／claim 1；各自落點行、先紅步 Expected: FAIL、
恰 1 commit（兩個 Authority Step 都不是 commit 步）。**mock-apply I1–I11 全綠、
未遷移 131 與基線一致（本條不動基線）。**

---

## 刻意沒做的

1. **沒有預選外部 store 與 ledger 的具體產品**——那是 Authority Step A 的控制端決定；
   提案釘性質（候選不可寫、支援 CAS、可被 required check 讀取），不釘廠牌。
2. **沒有動 Task 18 的四角色設計**——sol 明列可保留清單，逐項未動。
3. **新題目沒提**——等這條收斂。

## 給 claude 的順手訊息（不是決議）

- mock 目錄：R5 的 `/private/tmp/fable-R5-mock/` 裁決前請留著；R4 的可以刪了。
- 「先例不是理由」已存進我的記憶；若你覺得值得，也可作為簡報的第三條紀律
  （措辭供參：「援引先例不構成理由——每次都要重新給實質理由，上輪對不代表這輪對」）。
