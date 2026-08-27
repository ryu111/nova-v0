codex
我會先逐行看 R11-03 的 25 行並對壞／好兩個目錄重跑；其餘五條再檢查是否只是「把名字移走」或真的把執法責任收斂到已有機制。這輪不改檔。
exec
/bin/zsh -lc "sed -n '1,220p' /private/tmp/fable-R11-mock/複驗器.diff; UV_CACHE_DIR=/private/tmp/nova-uv-cache uv run python /private/tmp/fable-R11-mock/docs/計畫複驗.py /private/tmp/fable-R11-mock/負控/計畫; bad="'$?; UV_CACHE_DIR=/private/tmp/nova-uv-cache uv run python /private/tmp/fable-R11-mock/docs/計畫複驗.py /private/tmp/fable-R11-mock/docs/計畫; good=$?; echo "negative_exit=$bad positive_exit=$good"' in /Users/sbu/nova
 succeeded in 16ms:
計畫 22 份 · Create 路徑 775 個 · task 192 個 · ClaimSpec 落點未遷移 131 個 · 實存 claim 檔 13 份
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
negative_exit=1 positive_exit=0

exec
/bin/zsh -lc "find /private/tmp/fable-R11-mock -maxdepth 2 -type f -name '*.diff' -print; git diff --no-index -- docs/計畫複驗.py /private/tmp/fable-R11-mock/docs/計畫複驗.py || true" in /Users/sbu/nova
 succeeded in 0ms:
/private/tmp/fable-R11-mock/fable-R11-計畫01.diff
/private/tmp/fable-R11-mock/fable-R11-計畫10.diff
/private/tmp/fable-R11-mock/fable-R11-計畫06.diff
/private/tmp/fable-R11-mock/fable-R11-複驗器.diff
/private/tmp/fable-R11-mock/fable-R11-計畫08.diff
/private/tmp/fable-R11-mock/fable-R11-計畫09.diff
diff --git a/docs/計畫複驗.py b/private/tmp/fable-R11-mock/docs/計畫複驗.py
index ec2d07d..aebfb91 100644
--- a/docs/計畫複驗.py
+++ b/private/tmp/fable-R11-mock/docs/計畫複驗.py
@@ -52,7 +52,8 @@
          把某個 id 的落點路徑與另一個 id 的對調（**這條 I10 抓不到，I11 才抓得到**）。
   I10 → ①刪掉某已遷移 task 的落點行而不動 baseline；②把某 id 的路徑改一個字指到沒人 Create 的檔；
         ③把兩個 id 指到同一條路徑；④落點行少寫一個 id；⑤把某 id 指到更晚的 task 才 Create 的檔。
-  I6 → 把兩個 task 併成一個（commit 步會變成兩個）。
+  I6 → 把兩個 task 併成一個（commit 步會變成兩個）；把任一 task 標題序號改成
+       與位置不符（撞號或跳號）。
        註：ClaimSpec 上限 2 抓不到 1+1 合併（併完剛好是 2，仍在上限內），
        所以偵測合併靠的是 commit 步那條——每個 task 都恰好一次 commit。
 
@@ -192,6 +193,12 @@ def i6_任務口徑(檔, 上限條=2, 上限檔=10):
         s = open(f, encoding='utf-8').read()
         for i, b in enumerate(re.split(r'^### Task ', s, flags=re.M)[1:], 1):
             名 = f'{編號(f)}-Task{i}'
+            # 標題序號必須等於出現位置：R11 實測 08 出現兩個「Task 9」（R8 套用改號後，
+            # R9 的 diff 仍寫舊號、逐字套用），本檢查之前完全不看標題數字，撞號不紅。
+            標題號 = re.match(r'(\d+)\s*:', b)
+            if not 標題號 or int(標題號.group(1)) != i:
+                失敗.append(f'I6 task 標題序號與位置不符：{名} 的標題寫 Task '
+                            f'{標題號.group(1) if 標題號 else "?"}（撞號或跳號）')
             區 = re.findall(r'\*\*ClaimSpec:\*\*(.+?)(?:\n\n|\*\*固定負控)', b, re.S)
             條 = set()
             for x in 區:

exec
/bin/zsh -lc "sed -n '1,240p' /private/tmp/fable-R11-mock/fable-R11-計畫06.diff; sed -n '1,180p' /private/tmp/fable-R11-mock/fable-R11-計畫01.diff; sed -n '1,180p' /private/tmp/fable-R11-mock/fable-R11-計畫09.diff; sed -n '1,180p' /private/tmp/fable-R11-mock/fable-R11-計畫10.diff" in /Users/sbu/nova
 succeeded in 0ms:
--- B/計畫/06-判準評估與隔離回饋.md	2026-08-28 00:39:56
+++ 草稿/計畫/06-判準評估與隔離回饋.md	2026-08-28 02:21:23
@@ -36,11 +36,13 @@
 ├── DisclosureLedger.schema.json              — lineage、disclosure_id、digest、ordinal。
 ├── FeedbackPolicy.schema.json                 — clause-level reducer policy。
 ├── IsolationCapability.schema.json            — requirement/offer capability vocabulary。
+├── RevealApproval.schema.json                 — 揭露核准封閉形狀；核准者由 attestation 承載。
 └── 保證/
     ├── sealed內容不進候選.claim.json          — projection/env/argv 都不含 sealed refs。
     ├── 隔離不得靜默降級.claim.json            — unsupported capability typed terminal。
     ├── 回饋經reducer.claim.json               — assertion repr 不逐字外洩。
     ├── 揭露即燒掉.claim.json                  — revealed case cannot be reused。
+    ├── 揭露須經核准.claim.json                — 六格核准負控；無 binding 即 fail-closed。
     └── 揭露總量有界.claim.json                — cap 跨 run、跨 revision、跨 sibling 累計。
 nova/權威/判準/
 ├── 定義.py                                   — immutable definition admission/read API。
@@ -48,6 +50,7 @@
 ├── 隔離協商.py                               — required subset offered 純判定。
 ├── 回饋閘.py                                 — raw result -> FeedbackPacket reducer。
 ├── 案例治理.py                               — ACTIVE/BURNED/REVOKED lifecycle。
+├── 揭露核准.py                               — RevealApprovalVerifier port＋fail-closed 預設。
 ├── 揭露帳本.py                               — 純 fold：事件序列 → 剩餘額度。
 └── test_判準權威.py                          — domain and admission tests。
 nova/基礎設施/裁定執行/
@@ -363,18 +366,40 @@
 
 **Files:**
 - Create: `nova/權威/判準/案例治理.py`
+- Create: `nova/權威/判準/揭露核准.py`
+- Create: `規格/判準/RevealApproval.schema.json`
+- Create: `規格/判準/保證/揭露須經核准.claim.json`
 - Modify: `nova/權威/判準/定義.py`
 - Modify: `nova/應用/執行判準.py`
 - Create: `驗收/判準/測_揭露燒毀.py`
 - Create: `規格/判準/保證/揭露即燒掉.claim.json`
 
 **Interfaces:**
-- Produces: `authorize_reveal(case_ref, approval_envelope) -> RevealReceipt`。
+- Produces: `RevealApproval`（封閉形狀）——`criterion_revision`／`criterion_digest`、
+  exact `case_ref`、`requested_action = REVEAL_RAW_CASE`、`approver_attestation_ref`、
+  `authority_revision`／`authority_digest`、`issued_at`、`expiry` 或明確 one-shot、`nonce`。
+- Produces: `RevealApprovalVerifier` port——
+  `verify(approval, criterion_revision, case_ref, requested_action)
+  -> VerifiedRevealApproval | ApprovalFailure`。`authorize_reveal` **只收**
+  `VerifiedRevealApproval`；**無 production binding 時一律
+  `APPROVAL_AUTHORITY_UNAVAILABLE`**——raw reveal 是安全邊界，fail-closed 不降名。
+  production binding 的落點＝計畫 12 權威閘（明文，本 task 只交付 port、schema、
+  fake verifier 與 fail-closed 預設）。
+  （R10→R11 修正：只加 schema 不夠——沒有任何已存在的 authority 能判斷
+  `approver_attestation_ref` 是否有效，「有 schema 不等於能驗」。）
+- Produces: `authorize_reveal(case_ref, verified_approval) -> RevealReceipt`。
 - Produces: atomic `CaseBurned` event before raw reveal bytes are returned。
 
-**ClaimSpec:** 【推論】`criterion.sealed-case.reveal-burns-before-release` 從紅轉綠。
+**ClaimSpec:** 【推論】`criterion.sealed-case.reveal-burns-before-release` 與 `criterion.sealed-case.reveal-requires-verified-approval` 從紅轉綠。
 
 **固定負控:** 【推論】在 `CaseBurned` commit 前／後 SIGKILL；commit 前不得收到 raw detail，commit 後重啟不得再次選中該 case。
+核准六格：`unresolvable-attestation`（attestation ref 指向不可驗來源）、
+`binds-other-case`（approval 綁另一個 case_ref）、`binds-other-criterion-revision`、
+`approves-other-action`（`requested_action` 不是 `REVEAL_RAW_CASE`）、
+`approval-replayed`（同 nonce／one-shot 重播第二次）——五者必須紅在
+`reveal_requires_verified_approval`；`verifier-unavailable`（無 production binding
+時送任何 reveal）必須紅在 `approval_authority_unavailable_fails_closed`。
+防恆真格：合法 approval 經 fake verifier 放行，burn-before-release 流程照舊。
 
 - [ ] **Step 1: 寫 ordering 與兩 crash points red**
 
@@ -407,7 +432,7 @@
 - [ ] **Step 5: Commit**
 
 ```bash
-git add nova/權威/判準 nova/應用/執行判準.py 驗收/判準/測_揭露燒毀.py 規格/判準/保證/揭露即燒掉.claim.json
+git add nova/權威/判準 規格/判準/RevealApproval.schema.json 規格/判準/保證/揭露須經核准.claim.json nova/應用/執行判準.py 驗收/判準/測_揭露燒毀.py 規格/判準/保證/揭露即燒掉.claim.json
 git commit -m "feat: 封存 case 揭露前先燒掉"
 ```
 
--- B/計畫/01-可執行保證語言.md	2026-08-28 00:50:38
+++ 草稿/計畫/01-可執行保證語言.md	2026-08-28 02:21:23
@@ -97,6 +97,8 @@
 架構/test_准入信任根.py                        — 八格負控：無收據、內嵌、metadata 回寫、雙花等。
 規格/工程/保證/准入職責分離.claim.json        — decider 與 changer 解析後不得同一 actor。
 驗收/工具鏈/突變批次/命名閘.toml               — 命名閘那批指定突變的宣告。
+驗收/工具鏈/測_跑驗收字首.py                   — 字首零命中與包裝層吞紅負控。
+規格/工程/保證/字首零命中必紅.claim.json       — 0 命中不得靜默通過。
 規格/工程/保證/指定突變可重跑.claim.json       — 同一批突變任何人跑都得到同一份結果。
 架構/檢查工程規範.py                          — AST/JSON/SQL/shell/path/size機械檢查。
 架構/test_工程規範.py                         — 固定錯置、超長、混script與shell中文負控。
@@ -1494,7 +1496,70 @@
 ```
 
 ---
+
+### Task 19: 跑驗收的字首選取有宣告、有測試、有零命中殺手
+
+**Files:**
+- Create: `規格/工程/保證/字首零命中必紅.claim.json`
+- Create: `驗收/工具鏈/測_跑驗收字首.py`
+- Modify: `工具/跑驗收.py`
+
+**Interfaces:**
+- Produces: `工具/跑驗收.py --prefix <字首>`——跑所有 `claim_id` 以該字首開頭的
+  claim，回報命中數；**0 命中必須 exit 非零並明講**。
+- **為什麼是新 task**：`--prefix` 有 11 份計畫的 Exit Gate 在消費
+  （07／08／10／11／12／14–19），但 Task 9 交付的 runner 沒有這個旗標——
+  它是**尚未實作的被消費介面**。Task 9 已交付且其 claim 已准入，
+  不得回填新介面；新介面＝新 task。
+- **可預見的失敗模式（措辭精確：這是設計要防的，不是已實測的 bug）**：
+  實作時若把「0 命中」對映到成功、或包裝層把 pytest 的 exit 5（no tests collected）
+  吞成「無事可做」，字首打錯或 namespace 改名就會讓某份計畫的 Exit Gate
+  靜默跑零條 claim 而綠。已實測的現況（claude，2026-08-28）：裸 pytest `-k`
+  零命中回 **exit 5 不是 0**——所以本 task 防的是**包裝層**丟失這個非零，
+  不是修一個已存在的 silent-green。
 
+**ClaimSpec:** 【推論】`claimspec.runner.prefix-zero-match-fails` 從紅轉綠。
+
+**ClaimSpec落點:** `claimspec.runner.prefix-zero-match-fails` → `規格/工程/保證/字首零命中必紅.claim.json`（本 task Create）
+
+**固定負控:** 【推論】兩格。`prefix-zero-match`：`--prefix 不存在的字首.` 必須
+exit 非零並回報「0 命中」。`wrapper-swallows-empty`：把 0 命中改判成功
+（或把 exit 5 對映成 0）的 runner 變體，必須紅在 `zero_match_is_failure`。
+防恆真格：存在的字首照常跑該組 claim 並回報命中數；單一 `--claim` 路徑不受影響。
+
+- [ ] **Step 1: 寫兩格負控與防恆真格的 red tests**
+
+```python
+def test_不存在字首必須非零並明講() -> None:
+    結果 = 跑(["--prefix", "不存在的字首."])
+    assert 結果.exit_code != 0
+    assert "0 命中" in 結果.stderr
+```
+
+- [ ] **Step 2: 跑紅測確認 --prefix 尚未實作**
+
+Run: `uv run pytest -q 驗收/工具鏈/測_跑驗收字首.py`
+
+Expected: 【推論】FAIL；`--prefix` 目前是 unrecognized argument。
+不得是收集錯誤冒充紅測。
+
+- [ ] **Step 3: 實作字首選取與零命中判定**
+
+- [ ] **Step 4: 跑負控、防恆真格與 ClaimSpec**
+
+Run: `uv run pytest -q 驗收/工具鏈/測_跑驗收字首.py && uv run python 工具/跑驗收.py --claim claimspec.runner.prefix-zero-match-fails`
+
+Expected: 【推論】PASS；兩格負控各紅在自己宣告的 predicate。
+
+- [ ] **Step 5: Commit**
+
+```bash
+git add 規格/工程/保證/字首零命中必紅.claim.json 驗收/工具鏈/測_跑驗收字首.py 工具/跑驗收.py
+git commit -m "feat: 跑驗收的字首選取零命中必紅"
+```
+
+---
+
 ## Plan Exit Gate
 
 【推論】本 plan 完成的唯一判定命令是：
--- B/計畫/09-持久工作協調與選拔.md	2026-08-28 00:39:56
+++ 草稿/計畫/09-持久工作協調與選拔.md	2026-08-28 02:24:22
@@ -273,7 +273,12 @@
   `analysis_digest`, `interval`}。deterministic 但 `result_semantics = ESTIMATOR` 的原語
   仍必須走 `ESTIMATED`——可重現不等於無抽樣不確定度。
 - Produces: 每個分數綁 `evaluator_revision` 與 `candidate_digest`，不匹配 → `REJECT_CANDIDATE`；
-  `score_source ∈ {VERIFIER_MEASURED, EXTERNAL_ATTESTED}`，裸數字與 `EXECUTOR_SELF_REPORT` 拒絕。
+  `score_source` 封閉 enum **v1 唯一成員 `VERIFIER_MEASURED`**，裸數字與
+  `EXECUTOR_SELF_REPORT` 拒絕。`EXTERNAL_ATTESTED` **移出 v1 enum**——它目前沒有
+  attestation verifier、沒有負控，塞在 enum 裡是一個沒有機制的名字（同
+  `OUTPUT_DETERMINISM` mechanism enum 的處理：名字要有機制才進 enum）；
+  重入條件＝外部分數的 attestation verifier port＋「不可驗 attestation 必拒」負控
+  隨同一變更入場（R11 覆蓋審修正）。
 - Produces: `SelectionRecord.winner_separation ∈ {CLEAR, OVERLAPPING}` 由冠亞軍 interval
   機械推導；輸入 schema 不收此欄（closed schema，unknown field 拒絕）。排序本身仍是
   點值＋digest tie-break，不變。
@@ -289,6 +294,8 @@
 指到別的候選的 fixture，必須紅在 `score_bound_to_evaluator_and_candidate`；
 `forged-separation`——改成照抄呼叫端 separation 值而非自行推導的 `選拔.py` 變體，
 必須紅在 `separation_machine_derived`。
+`unknown-score-source`——`score_source` 塞 enum 外值（含 `EXTERNAL_ATTESTED`），
+closed schema 必須拒，紅在 `score_source_vocabulary_closed`。
 防恆真格：`VERIFIER_MEASURED`＋`EXACT_ARTIFACT_FUNCTION` 原語背書的分數照常參賽，
 選出與原 claim 相同的 winner，permutation property 不變。
 
--- B/計畫/10-知識治理與快照.md	2026-08-27 11:59:34
+++ 草稿/計畫/10-知識治理與快照.md	2026-08-28 02:24:22
@@ -427,6 +427,7 @@
 - Create: `驗收/知識/測_跨權威越界.py`
 - Create: `規格/知識/保證/知識不得越權.claim.json`
 - Modify: `nova/權威/知識/端口.py`
+- Modify: `架構/依賴規則.toml`
 
 **Interfaces:**
 - Allows: context/policy proposal and immutable snapshot refs only。
@@ -449,16 +450,20 @@
 
 Expected: 【推論】FAIL。
 
-- [ ] **Step 3: 收窄 ports 並加入 import-linter rule**
+- [ ] **Step 3: 收窄 ports 並把禁止邊登錄進既有依賴規則**
 
 ```toml
-[[tool.importlinter.contracts]]
-name = "knowledge cannot write other authorities"
-type = "forbidden"
-source_modules = ["nova.權威.知識"]
-forbidden_modules = ["nova.權威.判準", "nova.權威.資源", "nova.權威.效果"]
+[[deny]]
+from = ["nova.權威.知識.*"]
+to = ["nova.權威.判準.*", "nova.權威.資源.*", "nova.權威.效果.*"]
 ```
 
+【推論】禁止邊登錄在 **`架構/依賴規則.toml`**、由 **`架構/檢查後端依賴.py`**
+（計畫 03 Task 8 建立）執法——不引入 import-linter。理由：同一類保證兩套執法器
+會分家，且 import-linter 不解析 literal `importlib.import_module` alias，
+而 03 Task 8 的檢查器有這個能力與對應負控——用較弱的第二套工具執法同一條規則，
+等於給動態 import 開一條繞過道（R11 覆蓋審修正）。
+
 - [ ] **Step 4: 跑 ClaimSpec 與全知識 suite**
 
 Run: `uv run pytest -q nova/權威/知識 nova/基礎設施/知識索引 nova/應用/test_知識服務.py 驗收/知識 -n 2 && uv run python 工具/跑驗收.py --prefix knowledge.`
@@ -468,7 +473,7 @@
 - [ ] **Step 5: Commit**
 
 ```bash
-git add nova/權威/知識/端口.py 驗收/知識/測_跨權威越界.py 規格/知識/保證/知識不得越權.claim.json pyproject.toml
+git add nova/權威/知識/端口.py 驗收/知識/測_跨權威越界.py 規格/知識/保證/知識不得越權.claim.json 架構/依賴規則.toml
 git commit -m "test: 強制知識的權威邊界"
 ```
 

codex
我逐行檢查了 R11-03 的 diff，並重跑兩個方向：

- 未修撞號目錄：exit 1，精確指出 `08-Task10` 標題寫成 Task 9。
- 已修草稿：exit 0，I1–I11 全綠。
- 合套結果：22 份計畫、775 個 Create、192 tasks、未遷移 131。

## 逐條裁決

| 決議 | 裁決 | 理由 |
|---|---|---|
| R11-00 | APPROVE | RevealApproval 現在不只具有 schema，還有 verifier port、無 binding fail-closed 與六個針對有效性的負控。 |
| R11-01 | APPROVE | `--prefix` 被安排成新的可執行 task 與獨立 claim，沒有回填已交付 Task 9。 |
| R11-02 | APPROVE | 純粹修正 Task 標題序號與內文引用，不改任何行為保證。 |
| R11-03 | APPROVE | 新檢查直接抓到真實撞號，對修正版本不誤殺，且錯誤訊息能定位檔案內的位置與標題值。 |
| R11-04 | APPROVE | 移除沒有 verifier 的 `EXTERNAL_ATTESTED` 是收縮未實現能力，不是削弱已存在的分數保證。 |
| R11-05 | APPROVE | 收斂到既有、較強且已有動態 import 負控的依賴檢查器，避免同一保證由兩套規則分叉。 |

## 寫入條件

### R11-00

`VerifiedRevealApproval` 不能只是任何呼叫端都能自行建構的普通資料型別，否則只是把 `approval_envelope` 改名。

Task 文字需釘死：

- production `VerifiedRevealApproval` 只能由 `RevealApprovalVerifier` 的成功結果取得。
- `authorize_reveal` 必須驗證 verification evidence 與以下內容綁定：

  - approval digest
  - criterion revision/digest
  - exact case ref
  - requested action
  - authority revision/digest

- 增加固定負控：

  - `forged-verified-wrapper`  
    → `verified_approval_requires_verifier_evidence`

  直接手造 `VerifiedRevealApproval` 不得取得 reveal。

- `expiry 或 one-shot` 必須是 discriminated union，不能是數個可同時缺席的 optional 欄位：

  ```text
  validity =
    EXPIRES_AT(timestamp)
    | ONE_SHOT(nonce)
  ```

- `approval-replayed` 的 one-shot 消費必須與 `CaseBurned` 在同一 state-owner transaction 中落盤；不能只靠程序記憶體 set。
- plan 12 production binding 未完成時，所有 raw reveal 都維持 `APPROVAL_AUTHORITY_UNAVAILABLE`。fake verifier 只能證明 contract，不得讓 release gate 宣稱 production approval 已可用。

### R11-01

`--prefix` 的匹配必須定義為純字首匹配，但輸出需固定排序，避免檔案列舉順序造成 evidence digest 漂移。

另外要測：

- 至少一條匹配 claim 紅時整體 exit 非零；
- 相同 claim 集以不同檔案列舉順序載入，執行清單與 evidence digest 相同；
- `--claim` 與 `--prefix` 同時出現時明確拒絕，不能暗定優先序。

### R11-03

這 25 行的核心邏輯正確：

```python
標題號 = re.match(r'(\d+)\s*:', b)
if not 標題號 or int(標題號.group(1)) != i:
    ...
```

它同時能抓：

- 重複號；
- 跳號；
- 從 0 開始；
- 標題缺數字或冒號；
- 實際位置與標題號不一致。

保留真實撞號 fixture 作為執法器的回歸負控，不能在套用後因「現況已修好」而刪掉。最好把最小壞檔固定在複驗器自己的 fixture 中，否則 `/private/tmp/.../負控` 被清掉後，這項檢查又只剩程式碼、沒有長期牙齒。

### R11-04

重入條件必須維持原子性：

> `EXTERNAL_ATTESTED`、verifier port、production/fake contract、不可驗 attestation 負控與正控，必須在同一變更加入。

不得先把 enum 名稱放回去、稍後再補 verifier。

### R11-05

既有檢查器必須對知識權威新增三種固定負控：

- 靜態 import；
- `importlib.import_module("literal.path")` 與 alias；
- `__import__()` 或非 literal 動態路徑。

非 literal 動態 module name 若無法解析，必須 fail-closed 或在權威層全面禁止；不能因為無法判定就略過。

另外，Task 7 的 Run 必須實際執行 `架構/檢查後端依賴.py`，不能只修改 TOML 後期待其他總閘順帶執行。

## R11-03 的定位

把它放在 I6 合理。I6 管 task 口徑與結構，標題序號就是 task identity 的結構成分，不需要新增 I12。

但「執法器自己的變更沒有執法器管」仍成立。因此這次兩票只能批准加入；長期保護必須靠上面的永久負控 fixture。沒有 fixture，未來刪掉這六行時 I1–I11 仍可能全綠。
tokens used
18,294
我逐行檢查了 R11-03 的 diff，並重跑兩個方向：

- 未修撞號目錄：exit 1，精確指出 `08-Task10` 標題寫成 Task 9。
- 已修草稿：exit 0，I1–I11 全綠。
- 合套結果：22 份計畫、775 個 Create、192 tasks、未遷移 131。

## 逐條裁決

| 決議 | 裁決 | 理由 |
|---|---|---|
| R11-00 | APPROVE | RevealApproval 現在不只具有 schema，還有 verifier port、無 binding fail-closed 與六個針對有效性的負控。 |
| R11-01 | APPROVE | `--prefix` 被安排成新的可執行 task 與獨立 claim，沒有回填已交付 Task 9。 |
| R11-02 | APPROVE | 純粹修正 Task 標題序號與內文引用，不改任何行為保證。 |
| R11-03 | APPROVE | 新檢查直接抓到真實撞號，對修正版本不誤殺，且錯誤訊息能定位檔案內的位置與標題值。 |
| R11-04 | APPROVE | 移除沒有 verifier 的 `EXTERNAL_ATTESTED` 是收縮未實現能力，不是削弱已存在的分數保證。 |
| R11-05 | APPROVE | 收斂到既有、較強且已有動態 import 負控的依賴檢查器，避免同一保證由兩套規則分叉。 |

## 寫入條件

### R11-00

`VerifiedRevealApproval` 不能只是任何呼叫端都能自行建構的普通資料型別，否則只是把 `approval_envelope` 改名。

Task 文字需釘死：

- production `VerifiedRevealApproval` 只能由 `RevealApprovalVerifier` 的成功結果取得。
- `authorize_reveal` 必須驗證 verification evidence 與以下內容綁定：

  - approval digest
  - criterion revision/digest
  - exact case ref
  - requested action
  - authority revision/digest

- 增加固定負控：

  - `forged-verified-wrapper`  
    → `verified_approval_requires_verifier_evidence`

  直接手造 `VerifiedRevealApproval` 不得取得 reveal。

- `expiry 或 one-shot` 必須是 discriminated union，不能是數個可同時缺席的 optional 欄位：

  ```text
  validity =
    EXPIRES_AT(timestamp)
    | ONE_SHOT(nonce)
  ```

- `approval-replayed` 的 one-shot 消費必須與 `CaseBurned` 在同一 state-owner transaction 中落盤；不能只靠程序記憶體 set。
- plan 12 production binding 未完成時，所有 raw reveal 都維持 `APPROVAL_AUTHORITY_UNAVAILABLE`。fake verifier 只能證明 contract，不得讓 release gate 宣稱 production approval 已可用。

### R11-01

`--prefix` 的匹配必須定義為純字首匹配，但輸出需固定排序，避免檔案列舉順序造成 evidence digest 漂移。

另外要測：

- 至少一條匹配 claim 紅時整體 exit 非零；
- 相同 claim 集以不同檔案列舉順序載入，執行清單與 evidence digest 相同；
- `--claim` 與 `--prefix` 同時出現時明確拒絕，不能暗定優先序。

### R11-03

這 25 行的核心邏輯正確：

```python
標題號 = re.match(r'(\d+)\s*:', b)
if not 標題號 or int(標題號.group(1)) != i:
    ...
```

它同時能抓：

- 重複號；
- 跳號；
- 從 0 開始；
- 標題缺數字或冒號；
- 實際位置與標題號不一致。

保留真實撞號 fixture 作為執法器的回歸負控，不能在套用後因「現況已修好」而刪掉。最好把最小壞檔固定在複驗器自己的 fixture 中，否則 `/private/tmp/.../負控` 被清掉後，這項檢查又只剩程式碼、沒有長期牙齒。

### R11-04

重入條件必須維持原子性：

> `EXTERNAL_ATTESTED`、verifier port、production/fake contract、不可驗 attestation 負控與正控，必須在同一變更加入。

不得先把 enum 名稱放回去、稍後再補 verifier。

### R11-05

既有檢查器必須對知識權威新增三種固定負控：

- 靜態 import；
- `importlib.import_module("literal.path")` 與 alias；
- `__import__()` 或非 literal 動態路徑。

非 literal 動態 module name 若無法解析，必須 fail-closed 或在權威層全面禁止；不能因為無法判定就略過。

另外，Task 7 的 Run 必須實際執行 `架構/檢查後端依賴.py`，不能只修改 TOML 後期待其他總閘順帶執行。

## R11-03 的定位

把它放在 I6 合理。I6 管 task 口徑與結構，標題序號就是 task identity 的結構成分，不需要新增 I12。

但「執法器自己的變更沒有執法器管」仍成立。因此這次兩票只能批准加入；長期保護必須靠上面的永久負控 fixture。沒有 fixture，未來刪掉這六行時 I1–I11 仍可能全綠。
