codex
我會把兩個可疑點拆開驗：06B 的 fixture 是否由釘版分析器從原始成對樣本算出結果，以及 `seed-dropped` 是否用「seed-sensitive 的可觀測 request」驗交付，而不是拿輸出重複性代替。這兩點會直接決定 R13-03／04 的票。
exec
/bin/zsh -lc "sed -n '1,220p' /private/tmp/fable-R13-mock/fable-R13-計畫01B.diff
sed -n '1,260p' /private/tmp/fable-R13-mock/fable-R13-計畫06B.diff
sed -n '1,180p' /private/tmp/fable-R13-mock/fable-R13-計畫16.diff
sed -n '1,140p' /private/tmp/fable-R13-mock/fable-R13-計畫17.diff
UV_CACHE_DIR=/private/tmp/nova-r13-uv-cache uv run python /private/tmp/fable-R13-mock/docs/計畫複驗.py /private/tmp/fable-R13-mock/docs/計畫" in /Users/sbu/nova
 succeeded in 0ms:
--- B/計畫/01B-執行者能力契約與SDK探針.md	2026-08-28 00:39:56
+++ 草稿/計畫/01B-執行者能力契約與SDK探針.md	2026-08-28 02:53:09
@@ -141,15 +141,19 @@
 
 **ClaimSpec落點:** `execution.backend-capability.tool-output-delegation-contract` → `規格/執行/保證/能力/工具輸出代理契約.claim.json`（本 task Create）
 
-**固定負控:** 【推論】四個 named subjects 分別在 deny 後仍呼叫 handler、回 malformed structured output、越過 delegation depth、把 ROOT_ONLY 標成 tree total；各自指定 predicate direct red。
+**固定負控:** 【推論】五個 named subjects 分別在 deny 後仍呼叫 handler、回 malformed structured output、越過 delegation depth、把 ROOT_ONLY 標成 tree total、
+宣告 `SEEDED_REQUEST` 卻把 request 的 seed 丟棄；各自指定 predicate direct red——
+第五格紅在 `seeded_request_delivers_seed`。
+（R13 覆蓋審：seeded 家族四成員裡，`SEEDED_REQUEST` 原本是唯一零 evidence 形狀、
+零負控的名字——而 repeatability 觀測整個建立在「seed 真的有送到」之上。）
 
-- [ ] **Step 1: 寫四個 faulty subjects 與 exact failed predicate red**
+- [ ] **Step 1: 寫五個 faulty subjects 與 exact failed predicate red**
 - [ ] **Step 2: 跑 `uv run pytest -q 驗收/執行者能力/測_工具輸出代理契約.py`**
 
 Expected: 【推論】FAIL；至少四個 faulty subjects 尚未被 contract suite 拒絕。
 
 - [ ] **Step 3: 寫 pure contract runner，不呼叫 SDK 或資料庫**
-- [ ] **Step 4: 跑 tests 與 ClaimSpec，確認 reference subject PASS、四個 negatives direct red**
+- [ ] **Step 4: 跑 tests 與 ClaimSpec，確認 reference subject PASS、五個 negatives direct red**
 - [ ] **Step 5: Commit**
 
 ```bash
--- B/計畫/06B-技術效益評測.md	2026-08-28 00:39:56
+++ 草稿/計畫/06B-技術效益評測.md	2026-08-28 02:53:09
@@ -144,6 +144,8 @@
 - Create: `nova/權威/評測/分析.py`
 - Create: `驗收/評測/fixtures/無效技術成對樣本.json`
 - Create: `驗收/評測/fixtures/省資源但品質退化.json`
+- Create: `驗收/評測/fixtures/區間過寬成對樣本.json`
+- Create: `驗收/評測/fixtures/絕對品質過低成對樣本.json`
 - Create: `驗收/評測/測_技術效益雙端點.py`
 - Modify: `nova/權威/評測/test_技術效益評測.py`
 - Modify: `pyproject.toml`
@@ -171,6 +173,15 @@
 `package-swap-same-fingerprint`：同一 EvidenceBundle 換統計套件版本卻宣稱同一 fingerprint。
 `fingerprint-missing-package`：fingerprint 少了 locked artifact hash 仍通過准入。
 後兩格必須紅在 `analysis_fingerprint_covers_package`。
+`wide-interval-not-inconclusive`：區間寬於 `max_interval_width` 仍判 `ACCEPTED` 的
+分析器變體，必須紅在 `interval_width_within_max`——精度門檻是 spec 明文的第二個
+門檻，「省 0–90%」不是答案，它要有自己的殺手。
+`low-absolute-quality-accepted`：兩端點統計上都過、但絕對品質低於
+`minimum_absolute_quality` 仍 `ACCEPTED` 的變體，必須紅在
+`absolute_quality_floor_enforced`——baseline 0.20 對 treatment 0.20 非劣但沒有使用
+價值，spec 自己說的，殺手原本缺席。
+（R13 覆蓋審：06B 是三方自己新開、從未被審過的計畫——兩條 claim 對兩個端點的牙
+是真的，但 spec 宣告的**四個門檻裡有兩個零殺手**。）
 防恆真格：事前造好的「真省且品質非劣」配對樣本 `ACCEPTED` 且回報區間；
 同 bundle＋同 fingerprint＋同 seed 兩次分析的 result digest 相同。
 
@@ -179,7 +190,7 @@
 **這只證明目前釘版的這一組堆疊可重播，不得升格成所有 scipy 版本的保證**——
 所以 fingerprint 必須綁實際安裝的 artifact。
 
-- [ ] **Step 1: 寫四個負控與防恆真格的 red tests**
+- [ ] **Step 1: 寫六個負控與防恆真格的 red tests**
 
 ```python
 def test_無效技術的_token_上界必須超標() -> None:
@@ -209,7 +220,8 @@
 Run: `uv run pytest -q 驗收/評測/測_技術效益雙端點.py nova/權威/評測/test_技術效益評測.py`
 
 Expected: 【推論】PASS；`ineffective-technique` 與 `saves-but-degrades` 各紅一條、
-互不覆蓋；兩次分析的 result digest 相同。
+互不覆蓋；`wide-interval` 與 `low-absolute-quality` 各紅在自己的門檻 predicate；
+兩次分析的 result digest 相同。
 
 - [ ] **Step 5: Commit**
 
--- B/計畫/16-通用CLI後端.md	2026-08-27 11:59:34
+++ 草稿/計畫/16-通用CLI後端.md	2026-08-28 02:53:09
@@ -197,6 +197,10 @@
 **ClaimSpec:** 【推論】`backend.generic-cli.execution.protocol-parity` 從紅轉綠。
 
 **固定負控:** 【推論】FINAL mode宣告tool/round/quota events、unknown JSONL dropped、exit0 self-success terminal、unbounded stdout；common suite direct red。
+`ignore-term-grandchild`：fixture_agent 增 hang／fork 模式——忽略 SIGTERM 並 fork
+孫程序無限睡眠；wall deadline 後父與孫都必須不存在、終態 `TIMED_OUT`。
+（R13 並排比對：14／15／17 各有 adapter 級的 cancel／process-tree 負控，16 原本沒有
+——通用 runtime 走 ProcessSupervisor 不豁免 adapter 自證。）
 
 - [ ] **Step 1: 寫same behavioral fixtures through both modes red**
 
@@ -302,6 +306,10 @@
 **ClaimSpec:** 【推論】`backend.generic-cli.context-plan-consumer-only` 從紅轉綠。
 
 **固定負控:** 【推論】adapter查Constraint/Knowledge registry、caller重新排序advisories、FINAL mode宣告turn reassert、meter無upper-bound proof；architecture/contract direct red或unsupported。
+`sealed-canary-in-invocation`：sealed canary 出現在 argv／env／stdin／workspace 任一，
+必須紅在 `invocation_contains_no_sealed_bytes`（雙池 fixture 沿用 06 的 builders）。
+（R13 並排比對：14 的 `測_投影.py` 與 15 的 Task 8 都有此格，16 只有 registry 面、
+沒有 bytes 面——對稱補齊。）
 
 - [ ] **Step 1: 寫constructor/public-input與capability red**
 
--- B/計畫/17-本地模型後端.md	2026-08-27 11:59:34
+++ 草稿/計畫/17-本地模型後端.md	2026-08-28 02:53:09
@@ -193,6 +193,10 @@
 **ClaimSpec:** 【推論】`backend.local-model.cancellation-enforceable` 從紅轉綠。
 
 **固定負控:** 【推論】in-process engine忽略token仍admitted、process忽略TERM/forks child、cancel後token繼續寫CAS；wall deadline/process cleanup direct red。
+`runtime-down-no-fallback`：resolved loopback endpoint 連不上時必須回
+`LOCAL_RUNTIME_UNAVAILABLE`；改連任何非 loopback／雲端 endpoint 的變體必須紅在
+`no_cloud_fallback`。（R13 覆蓋審：Global Constraints 明文「禁止轉用任何雲端
+provider」原本**零殺手**——fail-closed 宣告有、負控無，形狀①。）
 
 - [ ] **Step 1: 寫hang/fork/ignore-cancel red**
 
計畫 22 份 · Create 路徑 781 個 · task 193 個 · ClaimSpec 落點未遷移 130 個 · 實存 claim 檔 13 份
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
  15 ← ['01B', '05', '06', '07', '11', '12', '13']
  16 ← ['05', '06', '07', '11', '12', '13']
  17 ← ['04', '05', '06', '07', '11', '12', '13']
  18 ← ['02', '03', '07', '09', '12', '13']
  19 ← ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13']
  20 ← ['01', '01B', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19']

I1 檔案所有權 · I2 依賴無環 · I3 編號即拓撲序 · I4 任務完整 · I5 修改方向 · I6 任務口徑 · I7 引用可解析 · I8 命名可通過 · I9 訊息用中文 · I10 宣告與落點一對一 · I11 檔內id相符　全部成立

codex
- **R13-01：APPROVE**  
  兩格分別直接殺 process-tree 清理與 sealed bytes 外洩；寫入時須以程序身分／handle 驗證孫程序死亡，不能只用可能重用的 PID。

- **R13-02：APPROVE**  
  `runtime-down-no-fallback` 能殺到「不得轉雲端」；測試應使用記錄 endpoint 的 connector spy／網路 deny fixture，不得真的呼叫外部 provider。

- **R13-03：REJECT — `NOT_TESTABLE`**  
  現文只說「丟掉 seed 必須紅」，卻仍讓 oracle 依輸出重複性判斷；在本來就決定性的後端上，丟掉 seed 完全可能不紅。

  最小重提修改：

  - 使用 seed-sensitive transport spy，直接記錄 adapter 實際交付給後端的 canonical request。
  - 以兩個不同 seed（如 `s₁ != s₂`）送入，斷言收到的 request 分別保留同值、同型別及同欄位位置。
  - spy 的輸出固定且與 seed 無關，明確禁止用輸出是否相同作 oracle。
  - faulty adapter 刪除、覆寫或固定 seed 時，必須只紅在 `seeded_request_delivers_seed`。
  - 正控證明未宣告 `SEEDED_REQUEST` 的 adapter 不因此被要求接受 seed。

- **R13-04：APPROVE（附寫入條件）**  
  兩個缺失門檻確實各自取得 predicate，但 fixture 必須提供原始成對 observations，由釘版分析器實算區間與決策，不能直接塞入人工 interval。

兩個裁量的答案：

1. **`max_interval_width` 的牙可以成立，但目前摘要仍需補清楚 fixture 契約。**  
   「區間過寬」fixture 應滿足：

   - 輸入只有事前凍結的 spec、原始 paired observations、analysis seed；
   - reference analyzer 實際算出兩個端點皆過；
   - 同時算出 interval width `> max_interval_width`；
   - reference 結果必為 `INCONCLUSIVE`；
   - faulty analyzer 唯一變異是略過 width gate，因而錯判 `ACCEPTED`；
   - 測試只比較事前宣告的不等式，不把預先填好的 interval 當真相。

   可以把 `max_interval_width` 設得比該資料自然產生的區間更窄，無須偽造區間。絕對品質 fixture 也同理：由原始品質 observations 實算出相對非劣，但 lower bound 低於 absolute floor。

2. **原版 `seed-dropped` 不能保證紅。**  
   seed 的保證是「請求欄位被忠實交付」，不是「輸出因此改變」。因此 oracle 必須看 transport boundary 收到的 request bytes／typed field；後端輸出應刻意固定，避免把 `SEEDED_REQUEST` 與 repeatability 或 determinism 再度混為一格。
tokens used
13,998
- **R13-01：APPROVE**  
  兩格分別直接殺 process-tree 清理與 sealed bytes 外洩；寫入時須以程序身分／handle 驗證孫程序死亡，不能只用可能重用的 PID。

- **R13-02：APPROVE**  
  `runtime-down-no-fallback` 能殺到「不得轉雲端」；測試應使用記錄 endpoint 的 connector spy／網路 deny fixture，不得真的呼叫外部 provider。

- **R13-03：REJECT — `NOT_TESTABLE`**  
  現文只說「丟掉 seed 必須紅」，卻仍讓 oracle 依輸出重複性判斷；在本來就決定性的後端上，丟掉 seed 完全可能不紅。

  最小重提修改：

  - 使用 seed-sensitive transport spy，直接記錄 adapter 實際交付給後端的 canonical request。
  - 以兩個不同 seed（如 `s₁ != s₂`）送入，斷言收到的 request 分別保留同值、同型別及同欄位位置。
  - spy 的輸出固定且與 seed 無關，明確禁止用輸出是否相同作 oracle。
  - faulty adapter 刪除、覆寫或固定 seed 時，必須只紅在 `seeded_request_delivers_seed`。
  - 正控證明未宣告 `SEEDED_REQUEST` 的 adapter 不因此被要求接受 seed。

- **R13-04：APPROVE（附寫入條件）**  
  兩個缺失門檻確實各自取得 predicate，但 fixture 必須提供原始成對 observations，由釘版分析器實算區間與決策，不能直接塞入人工 interval。

兩個裁量的答案：

1. **`max_interval_width` 的牙可以成立，但目前摘要仍需補清楚 fixture 契約。**  
   「區間過寬」fixture 應滿足：

   - 輸入只有事前凍結的 spec、原始 paired observations、analysis seed；
   - reference analyzer 實際算出兩個端點皆過；
   - 同時算出 interval width `> max_interval_width`；
   - reference 結果必為 `INCONCLUSIVE`；
   - faulty analyzer 唯一變異是略過 width gate，因而錯判 `ACCEPTED`；
   - 測試只比較事前宣告的不等式，不把預先填好的 interval 當真相。

   可以把 `max_interval_width` 設得比該資料自然產生的區間更窄，無須偽造區間。絕對品質 fixture 也同理：由原始品質 observations 實算出相對非劣，但 lower bound 低於 absolute floor。

2. **原版 `seed-dropped` 不能保證紅。**  
   seed 的保證是「請求欄位被忠實交付」，不是「輸出因此改變」。因此 oracle 必須看 transport boundary 收到的 request bytes／typed field；後端輸出應刻意固定，避免把 `SEEDED_REQUEST` 與 repeatability 或 determinism 再度混為一格。
