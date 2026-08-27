codex
我會重跑鏡像閘，但這輪真正的判定點不是 I1–I11：我要檢查 detached receipt 是否仍透過 `receipt_digest/locator` 間接進入它所簽的 manifest digest，以及假 ledger 的 CAS 測試是否被誤升格成 production 原子性證據。
exec
/bin/zsh -lc "UV_CACHE_DIR=/private/tmp/nova-uv-cache uv run python /private/tmp/fable-R5-mock/docs/計畫複驗.py /private/tmp/fable-R5-mock/docs/計畫 && rg -n -C 4 'proposed manifest digest|receipt_digest|receipt_locator|compare-and-set|Authority Step|防恆真格' /private/tmp/fable-R5-mock/docs/計畫/01-可執行保證語言.md | tail -n 220" in /Users/sbu/nova
 succeeded in 0ms:
計畫 22 份 · Create 路徑 761 個 · task 188 個 · ClaimSpec 落點未遷移 131 個 · 實存 claim 檔 13 份
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
82-規格/語言/原語目錄.admitted.json              — 唯一有權存在的原語清單；呼叫端不得自備。
83-規格/語言/保證/原語目錄須經准入.claim.json     — 自備目錄一律 typed 拒絕。
84-nova/權威/判準/原語目錄准入.py                 — catalog_ref → 原語目錄，或 typed 失敗。
85-nova/權威/判準/test_原語目錄准入.py            — 自備目錄、同 id 不同 digest、缺負控。
86:驗收/保證規格語言/測_目錄准入.py               — 目錄准入的黑箱負控與防恆真格。
87-規格/驗收/ClaimAdmissionManifest.schema.json  — 已准入保證閉包的封閉 schema。
88-規格/驗收/已准入保證.manifest.json             — 受保護 artifact 的檔案集合與 digest。
89-規格/工程/保證/已准入保證不可原地改弱.claim.json — 改弱已准入答案必須被擋。
90-架構/檢查已准入保證.py                         — 集合與 digest 雙向比對；不叫 baseline。
--
908-**ClaimSpec落點:** `engineering.gates.automatically-enforced` → `規格/工程/保證/閘必須自動執行.claim.json`（本 task Create）
909-
910-**固定負控:** 【推論】統一入口漏掉宣告清單裡任一道閘、CI workflow 少跑其中一支、
911-安裝好的 hook 不把非零 exit 傳出去——三者都必須 direct red。
912:防恆真格：閘全綠時 hook 不得擋住正常 commit。
913-
914-- [ ] **Step 1: 寫三個負控的 red tests**
915-
916-```python
--
933-
934-【推論】hook 只作快速回饋、可被 `--no-verify` 繞過；權威執法點是 CI 的 required check。
935-這個上限要寫進 CLAUDE.md，不得宣稱「不可能繞過」。
936-
937:- [ ] **Step 4: 跑三個負控與防恆真格**
938-
939-Run: `uv run pytest -q 架構/test_工程規範.py && uv run python 工具/驗全部.py`
940-
941-Expected: 【推論】PASS；入口 exit 0，三個負控各自 direct red，閘全綠時正常 commit 不被擋。
--
968-**ClaimSpec落點:** `engineering.named-mutation.repeatable` → `規格/工程/保證/指定突變可重跑.claim.json`（本 task Create）
969-
970-**固定負控:** 【推論】宣告 `expect="殺掉"` 但實際存活的突變必須回非零；宣告 `expect="存活"`
971-卻被殺掉的等價突變也必須回非零；目標字串不存在時必須明講而不是當成通過。
972:防恆真格：一批全部相符時回零，且跑完後工作樹必須與跑之前逐位元組相同。
973-
974-- [ ] **Step 1: 寫三個負控的 red tests**
975-
976-```python
--
994-
995-【推論】突變就地套用再還原（`try/finally`），開跑前先確認工作樹乾淨——
996-複製整個 repo 會重建 venv，慢到沒人願意跑；沒人跑的工具等於不存在。
997-
998:- [ ] **Step 4: 跑三個負控與防恆真格**
999-
1000-Run: `uv run pytest -q 架構/test_工程規範.py -k 突變 && uv run python 工具/跑指定突變.py 驗收/工具鏈/突變批次/命名閘.toml`
1001-
1002-Expected: 【推論】PASS；命名閘那批逐條相符、回零，工作樹跑完與跑前相同。
--
1083-`exact-without-evidence`：標 exact 但缺 `result_semantics_evidence` 任一欄，必須紅在
1084-`exact_requires_semantics_evidence`。
1085-`exact-missing-designated-mutations`：evidence 齊全但 `fixed_controls` 缺三條指定 mutation
1086-任一，必須紅在 `exact_requires_designated_mutations`。
1087:防恆真格三條：已准入目錄下的合法 claim 仍必須編綠；引用目錄外原語仍必須紅在
1088-`UNKNOWN_PRIMITIVE` 而不是被新的 code 蓋掉；一個帶齊 evidence 與三條指定 mutation 的
1089-合規 exact 原語通過准入，且對它施加三條 mutation 各自使其 admission 轉紅（故障注入自驗）。
1090-
1091:- [ ] **Step 1: 寫六個負控與三個防恆真格的 red tests**
1092-
1093-```python
1094-def test_自備目錄不得編出計畫() -> None:
1095-    自備 = 原語目錄("ref.v1", (原語("always.pass", 內部, "STRING"),))
--
1126-
1127-【推論】`compile_claim` 保留 catalog 參數以維持 `plan_digest` 綁四個輸入，
1128-但 production 呼叫路徑一律先過 `解析目錄`；自備物件走不進去。
1129-
1130:- [ ] **Step 5: 跑六個負控與三個防恆真格**
1131-
1132-Run: `uv run pytest -q 驗收/保證規格語言/測_目錄准入.py nova/權威/判準/test_原語目錄准入.py`
1133-
1134:Expected: 【推論】PASS；六個負控各紅在自己宣告的 code，三個防恆真格綠。
1135-
1136-- [ ] **Step 6: Commit**
1137-
1138-```bash
--
1190-`delete-an-admitted-claim`：整份刪掉一個已准入的 claim 檔，必須紅在
1191-`manifest_covers_exact_file_set`；這一格專門抓「只比對內容不比對集合」的寫法。
1192-`rewrite-the-manifest`：同一個 commit 裡同步改掉 manifest 的 digest，必須紅在
1193-`candidate_cannot_rewrite_admission_baseline`。
1194:防恆真格：六道閘全綠且沒有動到任何已准入檔案時，這道閘必須放行。
1195-
1196:- [ ] **Step 1: 寫三個負控與防恆真格的 red tests**
1197-
1198-```python
1199-def test_縮短_must_fail_exactly_要被擋(tmp_path: Path) -> None:
1200-    改弱(claim="規格/執行/保證/外部時間上限.claim.json", 欄="must_fail_exactly",
--
1224-
1225-【推論】集合比對用 `iterdir()` 過濾 `is_file()` 直接列舉，不從別的型別推導——
1226-與 `檢查工程規範.py` 列目錄的做法同一條規則。
1227-
1228:- [ ] **Step 5: 跑三個負控與防恆真格**
1229-
1230-Run: `uv run pytest -q 架構/test_已准入保證.py && uv run python 工具/驗全部.py`
1231-
1232:Expected: 【推論】PASS；三個負控各紅在自己宣告的 predicate，防恆真格讓正常 commit 通過。
1233-
1234-- [ ] **Step 6: Commit**
1235-
1236-```bash
--
1258-  trust-root revision/digest、expiry/revocation。**信任根與 nonce ledger 都位於候選 PR
1259-  不可寫的外部信任域**；repo 內的 `准入信任根.admitted.json` 只是該外部事實的
1260-  mirror/reference，不能自行成為自己的信任根。
1261-- Produces: `AdmissionAuthorizationReceipt`——**live、single-use、detached**。
1262:  封閉欄位：repository identity、exact PR/head SHA、proposed manifest digest、
1263-  trust-root revision/digest、ruleset identity 及其版本或不可變摘要、required workflow
1264-  repo/ref/digest、workflow run id、attested actor、issued_at、one-time nonce。
1265-  **簽發順序寫死**：PR head 先固定 → 受保護 workflow 對該 head SHA 與 proposed
1266-  manifest digest 簽發 detached receipt → receipt 存進候選不可寫的外部 attestation
1267-  store → required check 直接驗 detached receipt。**receipt 不得寫進它所授權的
1268-  Git tree**——被簽的 head 不得包含自己的 receipt；repo 內只能在 manifest entry 留
1269:  `receipt_digest` 與 `receipt_locator` 兩欄（Modify `ClaimAdmissionManifest.schema.json`），
1270-  schema 禁止內嵌 receipt 本體。
1271:- Produces: **nonce 在外部權威處原子消費**——nonce ledger 提供 compare-and-set
1272-  `UNUSED → CONSUMED(manifest_digest, head_sha)`，同一 nonce 的第二次消費必須失敗。
1273-  本機 checker 對 manifest 歷史的 nonce 唯一性掃描只是**冗餘絆線**：
1274-  單純掃目前 branch 看歷史不足以防並行雙花，保證來自 ledger CAS，
1275-  required check 驗的是消費記錄與 receipt 的綁定。
1276-- Produces: `檢查已准入保證.py` 對**新增** manifest entry 要求
1277:  `receipt_digest`＋`receipt_locator` 且 receipt 驗證通過（簽章 key 在信任根、
1278-  綁本次 manifest digest＋head SHA、nonce 已在 ledger 原子消費）；缺任一一律 typed
1279-  拒絕 `ADMISSION_TRUST_ROOT_UNAVAILABLE`——fail-closed 是設計不是事故；
1280-  已存在的 entry 照常比對集合與 digest，不受影響。
1281-- Produces: replay 測試只證明「**相同外部回應導出相同 verdict**」——錄下的 issuer／
1282-  ledger 回應餵進驗證器必得同一判定。這個能力的名字是 observation/replay，
1283-  **不得成為 live authorization**。
1284:- **Authority Step A（控制端，非實作者 commit 步）**：在候選不可寫的外部信任域建立
1285-  trust root 與 nonce ledger；repo PR 只提交該外部根的 mirror/reference。
1286:- **Authority Step B（控制端，非實作者 commit 步）**：外部 workflow 對固定的
1287-  第一個 admission PR head 簽發 detached genesis receipt，由**不同** attested actor
1288-  核准；required check 綠後才能 merge；創世 receipt 的外部 digest 由該 admission 的
1289:  manifest entry（`receipt_digest`／`receipt_locator`）與後續稽核事件記錄。
1290:  實作者可以完成全部拒絕路徑與 replay 測試；**在兩個 Authority Step 完成並驗證前，
1291-  本 task 不得宣告完成，期間一切新增 admission 必須 fail-closed。**
1292-
1293-**為什麼**：Task 16 的 manifest 擋得住「改弱已准入檔案」，但「誰有權新增 admission」
1294-是空的。R4 版的 receipt 綁 exact head SHA 卻又把 receipt 與創世證據寫進同一個 PR——
--
1320-`foreign-key-receipt`：簽章 key 不在信任根的 receipt，必須紅在 `receipt_signer_in_trust_root`。
1321-`genesis-self-approved`：genesis receipt 的簽發者與核准者解析為同一 actor，必須紅在
1322-`genesis_requires_distinct_actor`。
1323-`genesis-twice`：創世已完成後再送一次創世 transition，必須紅在 `genesis_occurs_at_most_once`。
1324:防恆真格：兩個 Authority Step 完成後，帶合法 detached receipt 的合規 entry 放行；
1325-replay 測試對錄下的 issuer／ledger 回應得到同一 verdict；
1326-未觸碰 manifest 的一般 commit 六道閘全綠照過。
1327-
1328:- [ ] **Step 1: 寫八個負控與防恆真格的 red tests**
1329-
1330-```python
1331-def test_無收據時新增准入必須被拒() -> None:
1332-    結果 = 跑准入閘(工作樹(新增一條entry(), 收據=None))
--
1356-manifest 不內嵌本體）／nonce 消費記錄綁定＋歷史唯一絆線；replay 面：錄下的
1357-issuer／ledger 回應 → verdict 決定性。checker 不打網路——live 簽發與 CAS 消費
1358-發生在受保護 workflow 與外部 ledger，checker 只驗收據與消費記錄本身。
1359-
1360:- [ ] **Step 4: 跑八個負控與防恆真格**
1361-
1362-Run: `uv run pytest -q 架構/test_准入信任根.py && uv run python 工具/驗全部.py`
1363-
1364:Expected: 【推論】PASS；八個負控各紅在自己宣告的 predicate；Authority Step 完成前，
1365-一切新增 admission 維持 typed 拒絕。
1366-
1367:- [ ] **Step 5: Authority Step A＋B（控制端）——外部信任域與 detached 創世**
1368-
1369-【推論】A：控制端在候選不可寫的外部信任域建立 trust root 與 nonce ledger，
1370-repo 只 mirror；B：外部 workflow 對固定的第一個 admission PR head 簽發 detached
1371-genesis receipt，另一 attested actor 核准。兩步完成並驗證前本 task 不得宣告完成。
--
1419-`unverified_role_separation_rejected`。
1420-`decider-not-receipt-actor`：`admission_decided_by` 與該筆 detached receipt 的
1421-`attested_actor` 解析為不同 actor，必須紅在 `decider_matches_receipt_actor`——
1422-裁定者身分由收據承載，不由 manifest 自報。
1423:防恆真格：相異 attested actor、來源可驗、receipt 有效且 actor 相符的 entry 放行；
1424-未觸碰 manifest 的一般 commit 六道閘全綠照過。
1425-
1426:- [ ] **Step 1: 寫四個負控與防恆真格的 red tests**
1427-
1428-```python
1429-def test_同把鑰匙簽兩個名字必須被抓() -> None:
1430-    entry = 造entry(decider=簽名(鑰匙甲(), "審查者"), changer=簽名(鑰匙甲(), "實作者"))
--
1438-Expected: 【推論】FAIL；manifest 目前沒有任何主體欄，角色分離無從檢查。
1439-
1440-- [ ] **Step 3: 寫四角色欄、actor 解析與不等式檢查**
1441-
1442:- [ ] **Step 4: 跑四個負控與防恆真格**
1443-
1444-Run: `uv run pytest -q 架構/test_已准入保證.py && uv run python 工具/驗全部.py`
1445-
1446:Expected: 【推論】PASS；四個負控各紅在自己宣告的 predicate，防恆真格綠。
1447-
1448-- [ ] **Step 5: Commit**
1449-
1450-```bash

codex
## R5-01(fable) — REJECT `INVARIANT_BREAK`

一句話：receipt 本體雖已 detached，但 manifest entry 又新增 `receipt_digest`／`receipt_locator`，同時 receipt 綁定 proposed manifest digest 與 exact head SHA；把這兩欄寫入 manifest 仍會改變 manifest digest 與 head，原本的自我參照循環只是從 receipt bytes 換成 receipt metadata。

我重跑了鏡像閘：22 份計畫、761 個 Create、188 tasks、未遷移 131，I1–I11 全綠。機械結構成立，但沒有抓到這個協定循環。

### 可重提的最小修改

v1 採真正 detached 的單階段形狀：

1. 候選 PR head `H` 內只包含 proposed admission entry。

   - entry 不得包含 `receipt_digest`
   - entry 不得包含 `receipt_locator`
   - entry 不得包含 nonce 或任何簽發後才能知道的資料

2. 受保護 workflow 對以下 canonical payload 簽發 receipt：

   ```text
   repository_identity
   exact_head_sha = H
   proposed_manifest_digest
   trust_root_revision/digest
   ruleset_identity/version
   required_workflow_identity/digest
   workflow_run_id
   attested_actor
   nonce
   issued_at
   ```

3. receipt、locator、digest 與 nonce consumption record 全部留在候選不可寫的外部信任域。

4. required check 以可推導的 lookup key 查找 receipt，例如：

   ```text
   (repository_identity, head_sha, proposed_manifest_digest)
   ```

   因此不需要把 locator 寫回 Git tree。

5. merge 後的稽核事件記錄 receipt digest／locator，但那是外部 audit projection，不反向改寫被授權的 commit。

6. `ClaimAdmissionManifest.schema.json` 不新增 `receipt_digest`／`receipt_locator`。它若需要表示授權狀態，只能由外部 receipt projection 導出，不能把授權證據塞回被授權內容。

新增固定負控：

- `detached-metadata-reinserted`  
  → `authorized_tree_contains_no_post_signature_metadata`

它要把 `receipt_digest` 或 `receipt_locator` 加入 proposed manifest，證明 schema／checker 會拒絕。

## 三個問題

### 1. CAS 或 merge queue

選外部 CAS，我同意；但「可機械測試」只是必要條件之一，不足以單獨證成選型。

CAS 在這裡比 merge queue合適的實質理由是：

- nonce 的 single-use 是領域不變式，不應綁死 GitHub 方案能力。
- merge queue 只序列化 merge；若 required check 沒有在最終 merge 點重新執行，它不必然防止兩個 PR 先後使用同一 nonce。
- 外部 linearizable CAS 可以直接表達所需原子轉移。
- 它也能服務 GitHub 以外的 transport。

但「假 ledger 第二次 CAS 失敗」只證明 port consumer 寫對，不能證明 production ledger 真有原子性。計畫必須另外要求 production conformance：

- 同一 nonce 的兩個並行 CAS，只能恰一個成功。
- 測試必須對 Authority Step A 選定的真 ledger 執行。
- ledger 必須聲明 linearizability 或等價的單鍵條件寫入保證。
- 權限必須確保候選只能讀 consumption proof，不能直接寫 ledger。
- live conformance 未通過時，`ADMISSION_TRUST_ROOT_UNAVAILABLE`。

因此應同時有：

- fake ledger：日常 deterministic contract test；
- real ledger：Authority Step 的 live conformance gate。

### 2. Ledger locator 放進 `AdmissionTrustRoot`

可以，但只放 locator 不夠。信任根還必須釘：

- ledger protocol 與版本
- namespace／repository binding
- CAS operation semantics
- consistency requirement：linearizable single-key conditional write
- writer identity allowlist
- reader／verifier identity
- receipt lookup-key derivation
- consumption-record schema
- revocation與rotation規則

repo 裡的 locator 仍只是外部信任根的 mirror；候選修改 locator 不會改變實際受信任位置。

### 3. 正控從哪裡來

假 fixture 只能當單元正控，不能完成 production 防恆真格。正控必須分兩級：

- 本地正控：用測試 signer 與 fake linearizable ledger，證明合法資料會通過 checker。它防止 checker 成為「永遠拒絕」的恆假閘。
- 權威正控：Authority Step A／B 對真外部 signer、真 ledger、固定 PR head 跑一次完整流程：

  1. 固定 head `H`
  2. 對 proposed manifest digest 簽發 detached receipt
  3. 真 ledger CAS 恰一次成功
  4. required check 驗簽、綁定與 consumption record
  5. 第二次消費同 nonce 失敗
  6. 合規 admission check 綠
  7. receipt 與 consumption evidence content-addressed 保存於外部稽核域

Task 17 必須明標：

> 本地 fixture 綠只代表實作可進入 Authority Step；Authority Step 的真 signer、真 ledger 與真 required workflow 正控未綠前，Task 17 不得完成，任何新 admission 維持 fail-closed。

所以你的判斷正確：真正的「做對必須綠」是 Authority Step 的一部分，不能由假 fixture 冒充。
tokens used
14,500
## R5-01(fable) — REJECT `INVARIANT_BREAK`

一句話：receipt 本體雖已 detached，但 manifest entry 又新增 `receipt_digest`／`receipt_locator`，同時 receipt 綁定 proposed manifest digest 與 exact head SHA；把這兩欄寫入 manifest 仍會改變 manifest digest 與 head，原本的自我參照循環只是從 receipt bytes 換成 receipt metadata。

我重跑了鏡像閘：22 份計畫、761 個 Create、188 tasks、未遷移 131，I1–I11 全綠。機械結構成立，但沒有抓到這個協定循環。

### 可重提的最小修改

v1 採真正 detached 的單階段形狀：

1. 候選 PR head `H` 內只包含 proposed admission entry。

   - entry 不得包含 `receipt_digest`
   - entry 不得包含 `receipt_locator`
   - entry 不得包含 nonce 或任何簽發後才能知道的資料

2. 受保護 workflow 對以下 canonical payload 簽發 receipt：

   ```text
   repository_identity
   exact_head_sha = H
   proposed_manifest_digest
   trust_root_revision/digest
   ruleset_identity/version
   required_workflow_identity/digest
   workflow_run_id
   attested_actor
   nonce
   issued_at
   ```

3. receipt、locator、digest 與 nonce consumption record 全部留在候選不可寫的外部信任域。

4. required check 以可推導的 lookup key 查找 receipt，例如：

   ```text
   (repository_identity, head_sha, proposed_manifest_digest)
   ```

   因此不需要把 locator 寫回 Git tree。

5. merge 後的稽核事件記錄 receipt digest／locator，但那是外部 audit projection，不反向改寫被授權的 commit。

6. `ClaimAdmissionManifest.schema.json` 不新增 `receipt_digest`／`receipt_locator`。它若需要表示授權狀態，只能由外部 receipt projection 導出，不能把授權證據塞回被授權內容。

新增固定負控：

- `detached-metadata-reinserted`  
  → `authorized_tree_contains_no_post_signature_metadata`

它要把 `receipt_digest` 或 `receipt_locator` 加入 proposed manifest，證明 schema／checker 會拒絕。

## 三個問題

### 1. CAS 或 merge queue

選外部 CAS，我同意；但「可機械測試」只是必要條件之一，不足以單獨證成選型。

CAS 在這裡比 merge queue合適的實質理由是：

- nonce 的 single-use 是領域不變式，不應綁死 GitHub 方案能力。
- merge queue 只序列化 merge；若 required check 沒有在最終 merge 點重新執行，它不必然防止兩個 PR 先後使用同一 nonce。
- 外部 linearizable CAS 可以直接表達所需原子轉移。
- 它也能服務 GitHub 以外的 transport。

但「假 ledger 第二次 CAS 失敗」只證明 port consumer 寫對，不能證明 production ledger 真有原子性。計畫必須另外要求 production conformance：

- 同一 nonce 的兩個並行 CAS，只能恰一個成功。
- 測試必須對 Authority Step A 選定的真 ledger 執行。
- ledger 必須聲明 linearizability 或等價的單鍵條件寫入保證。
- 權限必須確保候選只能讀 consumption proof，不能直接寫 ledger。
- live conformance 未通過時，`ADMISSION_TRUST_ROOT_UNAVAILABLE`。

因此應同時有：

- fake ledger：日常 deterministic contract test；
- real ledger：Authority Step 的 live conformance gate。

### 2. Ledger locator 放進 `AdmissionTrustRoot`

可以，但只放 locator 不夠。信任根還必須釘：

- ledger protocol 與版本
- namespace／repository binding
- CAS operation semantics
- consistency requirement：linearizable single-key conditional write
- writer identity allowlist
- reader／verifier identity
- receipt lookup-key derivation
- consumption-record schema
- revocation與rotation規則

repo 裡的 locator 仍只是外部信任根的 mirror；候選修改 locator 不會改變實際受信任位置。

### 3. 正控從哪裡來

假 fixture 只能當單元正控，不能完成 production 防恆真格。正控必須分兩級：

- 本地正控：用測試 signer 與 fake linearizable ledger，證明合法資料會通過 checker。它防止 checker 成為「永遠拒絕」的恆假閘。
- 權威正控：Authority Step A／B 對真外部 signer、真 ledger、固定 PR head 跑一次完整流程：

  1. 固定 head `H`
  2. 對 proposed manifest digest 簽發 detached receipt
  3. 真 ledger CAS 恰一次成功
  4. required check 驗簽、綁定與 consumption record
  5. 第二次消費同 nonce 失敗
  6. 合規 admission check 綠
  7. receipt 與 consumption evidence content-addressed 保存於外部稽核域

Task 17 必須明標：

> 本地 fixture 綠只代表實作可進入 Authority Step；Authority Step 的真 signer、真 ledger 與真 required workflow 正控未綠前，Task 17 不得完成，任何新 admission 維持 fail-closed。

所以你的判斷正確：真正的「做對必須綠」是 Authority Step 的一部分，不能由假 fixture 冒充。
