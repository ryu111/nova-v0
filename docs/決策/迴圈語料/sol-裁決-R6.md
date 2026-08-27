codex
## R6-01(fable) — APPROVE

一句話：被授權 tree 現在對 receipt 完全零引用，receipt 只以固定 head SHA 與 manifest digest 單向引用 tree；nonce 的唯一性也移到外部 linearizable CAS，原本兩層自我參照與並行雙花都已消除。

我重跑鏡像閘：22 份計畫、761 個 Create、188 tasks、未遷移 131，I1–I11 全部成立。

## Task 18 的方向

你的推論成立：四個角色欄是簽發前已知的 proposed admission 內容，因此不構成循環。它們可以進 manifest，receipt 隨後確認其中的裁定者身分。

但方向必須在 Task 18 釘死：

1. required check 只能用公開公式：

   ```text
   (repository_identity, exact_head_sha, proposed_manifest_digest)
   ```

   查找唯一 receipt。

2. 查找過程不得讀取以下 manifest 欄位：

   - `admission_decided_by`
   - 其他角色 id
   - 任意 receipt locator
   - nonce
   - signer identity

3. receipt 查回並完成驗簽後，checker 才從 receipt 取得可信的 `attested_actor`。

4. 比較方向固定為：

   ```text
   declared admission_decided_by
       == verified receipt.attested_actor
   ```

   manifest 角色欄只是待驗宣告，沒有定位或選擇 receipt 的權力。

5. 填錯角色後被 receipt 打臉而 fail-closed，是正確行為；不得反過來用 manifest 宣告挑選「能與它相符」的 receipt。

建議把這條加入固定負控：

- `manifest-actor-selects-receipt`
- faulty subject：store 同時存在兩張 receipt；錯誤 checker 依 `admission_decided_by` 選出 actor 相符的那張，而不是依公開 lookup key 取得唯一 receipt。
- `must_fail_exactly`：

  ```text
  receipt_selected_only_by_derived_lookup_key
  ```

這是寫入條件，不構成 REJECT。

另須釘清 `attested_actor` 的來源：它不能只是外部 workflow 自填的字串。receipt signer 是 workflow issuer；`attested_actor` 是經 trust root 的 actor-extraction rule 從平台核准證據解析出的裁定者。兩者是不同角色，schema 與測試不得混為一欄。

## 正控確認

兩級正控的切法成立：

- fake signer／fake ledger 只證明 checker 不是恆拒絕，且 port consumer 遵守契約。
- 真 signer／真 ledger／真 required workflow 的七步 Authority Step 才證明部署能力存在。

Task 17 在 live 正控完成前不得完成、新 admission 必須 fail-closed，這個完成條件保留即可。

本輪不另提新決議。
tokens used
7,187
## R6-01(fable) — APPROVE

一句話：被授權 tree 現在對 receipt 完全零引用，receipt 只以固定 head SHA 與 manifest digest 單向引用 tree；nonce 的唯一性也移到外部 linearizable CAS，原本兩層自我參照與並行雙花都已消除。

我重跑鏡像閘：22 份計畫、761 個 Create、188 tasks、未遷移 131，I1–I11 全部成立。

## Task 18 的方向

你的推論成立：四個角色欄是簽發前已知的 proposed admission 內容，因此不構成循環。它們可以進 manifest，receipt 隨後確認其中的裁定者身分。

但方向必須在 Task 18 釘死：

1. required check 只能用公開公式：

   ```text
   (repository_identity, exact_head_sha, proposed_manifest_digest)
   ```

   查找唯一 receipt。

2. 查找過程不得讀取以下 manifest 欄位：

   - `admission_decided_by`
   - 其他角色 id
   - 任意 receipt locator
   - nonce
   - signer identity

3. receipt 查回並完成驗簽後，checker 才從 receipt 取得可信的 `attested_actor`。

4. 比較方向固定為：

   ```text
   declared admission_decided_by
       == verified receipt.attested_actor
   ```

   manifest 角色欄只是待驗宣告，沒有定位或選擇 receipt 的權力。

5. 填錯角色後被 receipt 打臉而 fail-closed，是正確行為；不得反過來用 manifest 宣告挑選「能與它相符」的 receipt。

建議把這條加入固定負控：

- `manifest-actor-selects-receipt`
- faulty subject：store 同時存在兩張 receipt；錯誤 checker 依 `admission_decided_by` 選出 actor 相符的那張，而不是依公開 lookup key 取得唯一 receipt。
- `must_fail_exactly`：

  ```text
  receipt_selected_only_by_derived_lookup_key
  ```

這是寫入條件，不構成 REJECT。

另須釘清 `attested_actor` 的來源：它不能只是外部 workflow 自填的字串。receipt signer 是 workflow issuer；`attested_actor` 是經 trust root 的 actor-extraction rule 從平台核准證據解析出的裁定者。兩者是不同角色，schema 與測試不得混為一欄。

## 正控確認

兩級正控的切法成立：

- fake signer／fake ledger 只證明 checker 不是恆拒絕，且 port consumer 遵守契約。
- 真 signer／真 ledger／真 required workflow 的七步 Authority Step 才證明部署能力存在。

Task 17 在 live 正控完成前不得完成、新 admission 必須 fail-closed，這個完成條件保留即可。

本輪不另提新決議。
