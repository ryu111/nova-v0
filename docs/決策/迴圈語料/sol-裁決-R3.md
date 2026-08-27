codex
我會重跑鏡像閘，並抽查五條真正容易假綠的地方：R3-01 的 exact 語意是否由 catalog 執法、R3-02 的全序是否處理缺失／等長向量、R3-03 的 replayer ref 是否真的解析、R3-04 的錄播是否被錯當即時事實、R3-05 的 CAS→reserve→release 是否具備冪等 crash 語意。
exec
/bin/zsh -lc 'test -d /private/tmp/fable-R3-mock && uv run python /private/tmp/fable-R3-mock/docs/計畫複驗.py /private/tmp/fable-R3-mock/docs/計畫
rg -n "result_semantics|EXACT_ARTIFACT_FUNCTION|NO_OBSERVED_PROGRESS|BEST_CANDIDATE_UNDER_FROZEN_ORDER|PURE_REPLAYER|AdmissionTrustRoot|ProbeRecord|ReserveDisclosure|packet_content_ref" /private/tmp/fable-R3-mock/docs/計畫/*.md | head -n 350' in /Users/sbu/nova
 succeeded in 0ms:
error: Failed to initialize cache at `/Users/sbu/.cache/uv`
  Caused by: failed to open file `/Users/sbu/.cache/uv/sdists-v9/.git`: Operation not permitted (os error 1)
/private/tmp/fable-R3-mock/docs/計畫/08-目標追求生命週期.md:53:    ├── 無觀測進展終態.claim.json             — 連續 K 次無嚴格改善只能 NO_OBSERVED_PROGRESS。
/private/tmp/fable-R3-mock/docs/計畫/08-目標追求生命週期.md:521:  `measure_kind` 封閉 enum，v1 唯一成員 `BEST_CANDIDATE_UNDER_FROZEN_ORDER`；
/private/tmp/fable-R3-mock/docs/計畫/08-目標追求生命週期.md:528:  Pursuit 進 `POLICY_STOP(NO_OBSERVED_PROGRESS)`。
/private/tmp/fable-R3-mock/docs/計畫/08-目標追求生命週期.md:531:- Produces: `POLICY_STOP` 的封閉 reason enum 增 `NO_OBSERVED_PROGRESS`；enum 裡**沒有**
/private/tmp/fable-R3-mock/docs/計畫/08-目標追求生命週期.md:563:    assert 軌跡.終態理由 == "NO_OBSERVED_PROGRESS"
/private/tmp/fable-R3-mock/docs/計畫/08-目標追求生命週期.md:582:把「窗滿」轉成拒絕 `StartExecution` 並發 `POLICY_STOP(NO_OBSERVED_PROGRESS)`。
/private/tmp/fable-R3-mock/docs/計畫/06-判準評估與隔離回饋.md:34:├── 揭露帳.machine.json                       — ReserveDisclosure／Recorded／Exhausted。
/private/tmp/fable-R3-mock/docs/計畫/06-判準評估與隔離回饋.md:479:- Produces: `揭露帳.machine.json`——明示 machine，command `ReserveDisclosure`、
/private/tmp/fable-R3-mock/docs/計畫/06-判準評估與隔離回饋.md:484:  放入 CAS（計畫 04）；event 必記 `disclosure_id`、`packet_content_ref`、`packet_digest`、
/private/tmp/fable-R3-mock/docs/計畫/06-判準評估與隔離回饋.md:487:- Produces: crash 後從 CAS 以 `packet_content_ref` 取回**完全相同的 bytes** 重送同一
/private/tmp/fable-R3-mock/docs/計畫/06-判準評估與隔離回饋.md:551:- [ ] **Step 4: 寫純 fold 帳本與應用層順序（CAS → ReserveDisclosure → commit → release）**
/private/tmp/fable-R3-mock/docs/計畫/01B-執行者能力契約與SDK探針.md:25:  `PURE_REPLAYER`**（計畫 05 重播器）；`PINNED_DETERMINISTIC_ENGINE` 與
/private/tmp/fable-R3-mock/docs/計畫/01B-執行者能力契約與SDK探針.md:86:  的 mechanism enum v1 唯一成員 `PURE_REPLAYER`。
/private/tmp/fable-R3-mock/docs/計畫/01B-執行者能力契約與SDK探針.md:191:  全部 N 份輸出 digest, TTL}；determinism evidence 必記 {`mechanism = PURE_REPLAYER`,
/private/tmp/fable-R3-mock/docs/計畫/01B-執行者能力契約與SDK探針.md:207:`forged-mechanistic-ref`——mechanism 填 `PURE_REPLAYER` 但 ref 指向不可驗來源（自填 JSON、
/private/tmp/fable-R3-mock/docs/計畫/01B-執行者能力契約與SDK探針.md:213:防恆真格：計畫 05 純函式重播器以 `PURE_REPLAYER` mechanism evidence 取得
/private/tmp/fable-R3-mock/docs/計畫/09-持久工作協調與選拔.md:270:  （01 Task 15）且 `result_semantics = EXACT_ARTIFACT_FUNCTION`；`ESTIMATED`＝
/private/tmp/fable-R3-mock/docs/計畫/09-持久工作協調與選拔.md:272:  `analysis_digest`, `interval`}。deterministic 但 `result_semantics = ESTIMATOR` 的原語
/private/tmp/fable-R3-mock/docs/計畫/09-持久工作協調與選拔.md:285:分數證據三格：`estimated-claims-exact`——由 `result_semantics = ESTIMATOR` 的原語背書
/private/tmp/fable-R3-mock/docs/計畫/09-持久工作協調與選拔.md:291:防恆真格：`VERIFIER_MEASURED`＋`EXACT_ARTIFACT_FUNCTION` 原語背書的分數照常參賽，
/private/tmp/fable-R3-mock/docs/計畫/01-可執行保證語言.md:92:規格/工程/AdmissionTrustRoot.schema.json      — 准入信任根的封閉 schema。
/private/tmp/fable-R3-mock/docs/計畫/01-可執行保證語言.md:1030:- Produces: 目錄的每個原語帶封閉的 `result_semantics ∈ {EXACT_ARTIFACT_FUNCTION, ESTIMATOR}`。
/private/tmp/fable-R3-mock/docs/計畫/01-可執行保證語言.md:1031:  `EXACT_ARTIFACT_FUNCTION` 的准入條件五項缺一不可：對 pinned input artifact 的**完整母體**執行、
/private/tmp/fable-R3-mock/docs/計畫/01-可執行保證語言.md:1034:- Forbids: deterministic 原語自動取得 `EXACT_ARTIFACT_FUNCTION`——決定性只保證可重現，
/private/tmp/fable-R3-mock/docs/計畫/01-可執行保證語言.md:1058:標 `EXACT_ARTIFACT_FUNCTION` 送准入，必須紅在 `exact_requires_full_population_function`
/private/tmp/fable-R3-mock/docs/計畫/01-可執行保證語言.md:1071:    估 = 准入請求(樣本平均原語(), result_semantics="EXACT_ARTIFACT_FUNCTION")
/private/tmp/fable-R3-mock/docs/計畫/01-可執行保證語言.md:1090:`fixed_controls`、`result_semantics`。權威層只解析不讀檔；`工具/跑驗收.py` 負責把 bytes 交進去。
/private/tmp/fable-R3-mock/docs/計畫/01-可執行保證語言.md:1213:- Create: `規格/工程/AdmissionTrustRoot.schema.json`
/private/tmp/fable-R3-mock/docs/計畫/01-可執行保證語言.md:1222:- Produces: `AdmissionTrustRoot`——封閉欄位：trusted attestation issuer、repository/ref、
/private/tmp/fable-R3-mock/docs/計畫/01-可執行保證語言.md:1226:  可寫的 ref**，產出 content-addressed `ProbeRecord`（queried_at、api payload digest、
/private/tmp/fable-R3-mock/docs/計畫/01-可執行保證語言.md:1294:git add 規格/工程/AdmissionTrustRoot.schema.json 規格/工程/准入信任根.admitted.json 規格/工程/創世准入證據.json 規格/工程/保證/准入須有信任根.claim.json 架構/檢查准入信任根.py 架構/test_准入信任根.py 架構/檢查已准入保證.py

exec
/bin/zsh -lc "UV_CACHE_DIR=/private/tmp/nova-uv-cache uv run python /private/tmp/fable-R3-mock/docs/計畫複驗.py /private/tmp/fable-R3-mock/docs/計畫
sed -n '1015,1105p' /private/tmp/fable-R3-mock/docs/計畫/01-可執行保證語言.md
sed -n '505,610p' /private/tmp/fable-R3-mock/docs/計畫/08-目標追求生命週期.md
sed -n '1188,1395p' /private/tmp/fable-R3-mock/docs/計畫/01-可執行保證語言.md
sed -n '455,580p' /private/tmp/fable-R3-mock/docs/計畫/06-判準評估與隔離回饋.md" in /Users/sbu/nova
 succeeded in 0ms:
計畫 22 份 · Create 路徑 759 個 · task 188 個 · ClaimSpec 落點未遷移 132 個 · 實存 claim 檔 13 份
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
- Create: `規格/語言/原語目錄.admitted.json`
- Create: `規格/語言/保證/原語目錄須經准入.claim.json`
- Create: `nova/權威/判準/原語目錄准入.py`
- Create: `nova/權威/判準/test_原語目錄准入.py`
- Create: `驗收/保證規格語言/測_目錄准入.py`
- Modify: `nova/權威/判準/保證規格編譯.py`
- Modify: `工具/跑驗收.py`

**Interfaces:**
- Consumes: 已准入清單 bytes（由呼叫端讀進來——權威層不碰檔案系統）與一個 `catalog_ref`。
- Produces: `解析目錄(清單, catalog_ref) -> 原語目錄 | CatalogFailure`。
  失敗 code 封閉為 `UNADMITTED_PRIMITIVE_CATALOG`、`CATALOG_DIGEST_MISMATCH`、
  `PRIMITIVE_MISSING_CONTROLS`、`PRIMITIVE_RESULT_SEMANTICS_REJECTED`。
- Forbids: production 路徑接受呼叫端自備的 `原語目錄` 物件。編譯入口只收 `catalog_ref`。
- Forbids: 同一個 `catalog_id` 對到兩份不同 digest 的內容。
- Produces: 目錄的每個原語帶封閉的 `result_semantics ∈ {EXACT_ARTIFACT_FUNCTION, ESTIMATOR}`。
  `EXACT_ARTIFACT_FUNCTION` 的准入條件五項缺一不可：對 pinned input artifact 的**完整母體**執行、
  無 sampling、無缺失值、primitive 與 input bytes 全部釘 digest、
  結果是該函式對該 artifact 的 exact output。不滿足者只能標 `ESTIMATOR`。
- Forbids: deterministic 原語自動取得 `EXACT_ARTIFACT_FUNCTION`——決定性只保證可重現，
  不保證無抽樣不確定度；一個 deterministic 原語也可以算 sample mean。

**為什麼**：`compile_claim(spec, catalog, binding, offer)` 的 catalog 目前由呼叫端自備。
`nova/權威/判準/test_保證規格語言.py::test_plan_digest_涵蓋四個輸入` 逐字證明換一份自備目錄
**仍然編得出 `TestPlan`**，只是 digest 不同。digest 不同只能證明「這次用了另一份目錄」，
不能證明「這份目錄有權存在」。所以 `UNKNOWN_PRIMITIVE` 擋的是「claim 用了目錄裡沒有的原語」，
**不擋「自備一份含新原語的目錄」**——而後者正是 pixel primitive 與 LLM-judge primitive
未來會走的路。今天的 fail-closed 是副作用不是設計。
地基：OWASP 對 agent tools 要求 backend enforcement 與 verified allowlist registry，
不讓呼叫端自報能用什麼；SLSA 要求 consumer 只接受指定的 signer-builder pair。
加蓋（nova 多出來的拒絕）：未准入目錄、同 id 不同 digest、新原語沒有自己的固定負控、
deterministic estimator 冒充 exact。

**ClaimSpec:** 【推論】`claimspec.catalog.admitted-only` 從紅轉綠。

**ClaimSpec落點:** `claimspec.catalog.admitted-only` → `規格/語言/保證/原語目錄須經准入.claim.json`（本 task Create）

**固定負控:** 【推論】四格。`self-supplied-catalog`：呼叫端自備一份只多加了 `always.pass`
的目錄，必須紅在 `catalog_is_admitted`，不得靜默編出合法 `TestPlan`。
`same-id-different-digest`：同一個 `catalog_id` 換掉內容，必須紅在 `catalog_digest_is_content_bound`。
`primitive-without-controls`：准入清單裡的原語沒有列出自己的固定負控，必須紅在
`primitive_admission_requires_named_controls`。
`deterministic-estimator-poses-as-exact`：一個 deterministic、但對樣本算 sample mean 的原語
標 `EXACT_ARTIFACT_FUNCTION` 送准入，必須紅在 `exact_requires_full_population_function`
——它可重現，但結果仍有抽樣不確定度，只能標 `ESTIMATOR`。
防恆真格兩條：已准入目錄下的合法 claim 仍必須編綠；引用目錄外原語仍必須紅在
`UNKNOWN_PRIMITIVE` 而不是被新的 code 蓋掉。

- [ ] **Step 1: 寫四個負控與兩個防恆真格的 red tests**

```python
def test_自備目錄不得編出計畫() -> None:
    自備 = 原語目錄("ref.v1", (原語("always.pass", 內部, "STRING"),))
    assert 解析目錄(清單, 自備.digest.hex).code == "UNADMITTED_PRIMITIVE_CATALOG"

def test_決定性估計原語不得標成精確() -> None:
    估 = 准入請求(樣本平均原語(), result_semantics="EXACT_ARTIFACT_FUNCTION")
    assert 解析目錄(含(估), 目錄ref()).code == "PRIMITIVE_RESULT_SEMANTICS_REJECTED"

def test_合法目錄下的正常_claim_仍要編綠() -> None:
    assert isinstance(編(底(), catalog=已准入目錄()), TestPlan)
```

- [ ] **Step 2: 跑紅測確認自備目錄今天仍然編得出計畫**

Run: `uv run pytest -q 驗收/保證規格語言/測_目錄准入.py`

Expected: 【推論】FAIL；`self-supplied-catalog` 那格拿到的是一個合法 `TestPlan`
而不是 typed 失敗——這正是缺口本身。不得是 `ModuleNotFoundError`：
import error 冒充紅測會讓這一格從此沒驗過任何東西。

- [ ] **Step 3: 寫 schema、bootstrap 清單與解析器**

【推論】`原語目錄.admitted.json` 是資料：每個原語列 `primitive_id`、`revision`、
`implementation_digest`、`observation_type`、`effect_kind`、`required_isolation`、
`fixed_controls`、`result_semantics`。權威層只解析不讀檔；`工具/跑驗收.py` 負責把 bytes 交進去。

- [ ] **Step 4: 把編譯入口改成只收 catalog_ref**

【推論】`compile_claim` 保留 catalog 參數以維持 `plan_digest` 綁四個輸入，
但 production 呼叫路徑一律先過 `解析目錄`；自備物件走不進去。

- [ ] **Step 5: 跑四個負控與兩個防恆真格**

Run: `uv run pytest -q 驗收/保證規格語言/測_目錄准入.py nova/權威/判準/test_原語目錄准入.py`

Expected: 【推論】PASS；四個負控各紅在自己宣告的 code，兩個防恆真格綠。

- [ ] **Step 6: Commit**

```bash
```

### Task 8: 停滯只回報觀測——凍結順序下的最佳候選

**Files:**
- Create: `規格/追求/ProgressMeasureSpec.schema.json`
- Create: `規格/追求/保證/無觀測進展終態.claim.json`
- Create: `驗收/追求/測_無觀測進展終態.py`
- Modify: `規格/追求/AttemptPolicy.schema.json`
- Modify: `規格/追求/追求.machine.json`
- Modify: `nova/領域/追求/模型.py`
- Modify: `nova/領域/追求/決策.py`
- Modify: `nova/領域/追求/test_追求決策.py`

**Interfaces:**
- Produces: `ProgressMeasureSpec(measure_kind, clause_priority, per_clause_scale)`。
  `measure_kind` 封閉 enum，v1 唯一成員 `BEST_CANDIDATE_UNDER_FROZEN_ORDER`；
  `clause_priority` 是 pinned criterion revision 的 clause_id 全集的一個全序
  （admission 驗兩個集合相等）；`per_clause_scale` v1 固定 `PASS_FAIL`。
- Produces: `best_so_far = {candidate_ref, verdict_vector_digest}`——必須指向**一個實際
  candidate 的實際 verdict vector**。「嚴格改善」＝新候選的 verdict vector 在凍結的
  `clause_priority` 字典序下（每格 PASS > FAIL）嚴格勝過目前 `best_so_far`；
  只有嚴格改善才重置停滯窗；連續 K 次無嚴格改善 → 第 K+1 次 `StartExecution` 拒絕，
  Pursuit 進 `POLICY_STOP(NO_OBSERVED_PROGRESS)`。
- Produces: `AttemptPolicy.max_stagnant_attempts`（K）必填無預設，admission 強制
  `1 ≤ K < max_executions`——數值是每個 AttemptPolicy 的顯式決定，nova 拒絕缺席。
- Produces: `POLICY_STOP` 的封閉 reason enum 增 `NO_OBSERVED_PROGRESS`；enum 裡**沒有**
  `NO_PROGRESS` 這個成員——criterion 只提供 PASS/FAIL 時，系統只能誠實回報
  「沒觀測到進展」，不能聲稱知道真實無進展。
- Forbids: 跨候選 union clause coverage 充當 progress state——不同候選各自通過的 clause
  拼起來是一個不存在的虛構候選。
- Forbids: measure 跨 criterion revision 比較（revision 改變依 Task 5 矩陣本來就是
  NEW_PURSUIT）。`per_clause_scale` 未來以動作②擴充 ordinal 時，該擴充的 admission
  必須同時宣告「ordinal 改善重置窗口」的義務；v1 不支援 ordinal，停止語意即 observational
  policy stop。

**ClaimSpec:** 【推論】`pursuit.retry.no-observed-progress-typed` 從紅轉綠。

**ClaimSpec落點:** `pursuit.retry.no-observed-progress-typed` → `規格/追求/保證/無觀測進展終態.claim.json`（本 task Create）

**固定負控:** 【推論】四格。`oscillating-repeat`：甲、乙兩種 verdict vector 交替的 fake
backend 跑 16 次——凍結序下 best 自第二輪起不再被嚴格勝過，不觸發停滯窗的 faulty
scheduler 必須紅在 `stagnant_window_exceeded_refused` 與 `terminal_reason_no_observed_progress`。
`novel-bytes-no-improvement`：每次 candidate bytes 不同、verdict vector 恆定，同前兩條。
`cross-candidate-union`：把候選甲（只過條款一）與候選乙（只過條款二）的通過集合
union 起來當 best 的變體——union 使窗口誤重置，必須紅在 `best_so_far_is_actual_candidate`。
`no-progress-name`：把終態 reason 寫成 `NO_PROGRESS` 的變體——closed schema 必須拒絕
unknown enum 成員，紅在 `terminal_reason_vocabulary_closed`。
防恆真格：第 K 次 attempt 恰有更高優先 clause 轉綠的序列，窗口重置、跑滿 16 次不被誤殺；
property test（hypothesis）以樸素參考實作對照「觸發 ⇔ 連續 K 次無嚴格勝過目前 best」，
並斷言嚴格改善鏈長 ≤ 相異 rank 值數（有限字典序的良基上界）。

- [ ] **Step 1: 寫四個負控與防恆真格的 red tests**

```python
def test_甲乙交替十六次必須在停滯窗滿時拒絕() -> None:
    軌跡 = 跑追求(交替後端(向量甲(), 向量乙()), 政策(max_stagnant_attempts=3))
    assert 軌跡.終態 == PursuitTerminal.POLICY_STOP
    assert 軌跡.終態理由 == "NO_OBSERVED_PROGRESS"

def test_跨候選聯集不得冒充最佳() -> None:
    追蹤 = 進展追蹤(凍結序(), 聯集變體=True)
    with pytest.raises(SchemaViolation):
        追蹤.納入(候選乙_只過條款二())
```

- [ ] **Step 2: 跑紅測確認今天振盪 16 次照樣燒滿預算**

Run: `uv run pytest -q 驗收/追求/測_無觀測進展終態.py`

Expected: 【推論】FAIL；16 次 attempt 在甲乙之間振盪、每次換 bytes 而 verdict 不變，
全部跑到 `EXHAUSTED` 才停——帳面井然有序，沒有任何一格紅過。不得是 `ModuleNotFoundError`。

- [ ] **Step 3: 寫 frozen-order comparator、停滯窗與 machine reason**

【推論】comparator 是純函式：兩個實際 verdict vector 依 `clause_priority` 逐格比對，
PASS > FAIL；`best_so_far` 只在嚴格勝過時更新並重置窗口。決策層在 `next_action`
把「窗滿」轉成拒絕 `StartExecution` 並發 `POLICY_STOP(NO_OBSERVED_PROGRESS)`。

- [ ] **Step 4: 跑 property tests 與 ClaimSpec**

Run: `uv run pytest -q nova/領域/追求/test_追求決策.py 驗收/追求/測_無觀測進展終態.py && uv run python 工具/跑驗收.py --claim pursuit.retry.no-observed-progress-typed`

Expected: 【推論】PASS；四個負控各紅在自己宣告的 predicate，防恆真格與 property test 綠。

- [ ] **Step 5: Commit**

```bash
git add 規格/追求/ProgressMeasureSpec.schema.json 規格/追求/保證/無觀測進展終態.claim.json 規格/追求/AttemptPolicy.schema.json 規格/追求/追求.machine.json nova/領域/追求 驗收/追求/測_無觀測進展終態.py
git commit -m "feat: 停滯只回報觀測到的無進展"
```

---

## Plan Exit Gate

- 【推論】Pursuit 有自己的 machine/terminal；一個 Pursuit 終結不會寫 Work terminal。
- 【推論】attempt/call/deadline/budget 任一耗盡都停止，pause 不延長 deadline，第 17 次 Execution 永遠不建立。
- 【推論】只有 external ACCEPT verdict 可 `SUBMITTED`；raw/self-reported success 無權提交。
- 【推論】同 Pursuit 可 checkpoint 後換允許後端；identity-breaking change 只能走 superseding Pursuit。
- 【推論】workspace/evidence scopes 與 IndependenceManifest 能抓出假獨立。
- 【推論】`uv run pytest -q nova/領域/追求 nova/應用/test_追求服務.py 驗收/追求 -n 2` 與全部 `pursuit.*` ClaimSpecs 綠。

## Execution Handoff

【推論】Task 5 的 change matrix 是後續所有 adapter 與 updater 的契約，不接受 adapter 自行解釋「同一後端」。完成後才可做 Work portfolio 與 selection；否則 Work 無法知道 child 終態和 independence evidence 的語義。
把驗收退化成「看到 TIMED_OUT 字串就算」的改動，這道閘必須先於 wall-limit runner 擋下來。

- [ ] **Step 4: 寫 checker 並接進閘清單**

【推論】集合比對用 `iterdir()` 過濾 `is_file()` 直接列舉，不從別的型別推導——
與 `檢查工程規範.py` 列目錄的做法同一條規則。

- [ ] **Step 5: 跑三個負控與防恆真格**

Run: `uv run pytest -q 架構/test_已准入保證.py && uv run python 工具/驗全部.py`

Expected: 【推論】PASS；三個負控各紅在自己宣告的 predicate，防恆真格讓正常 commit 通過。

- [ ] **Step 6: Commit**

```bash
git add 規格/驗收/ClaimAdmissionManifest.schema.json 規格/驗收/已准入保證.manifest.json 規格/工程/保證/已准入保證不可原地改弱.claim.json 架構/檢查已准入保證.py 架構/test_已准入保證.py 架構/目錄規則.toml .github/workflows/gates.yml
git commit -m "feat: 已准入保證的閉包不可被實作者原地改弱"
```

---

### Task 17: 建立准入信任根與創世儀式

**Files:**
- Create: `規格/工程/AdmissionTrustRoot.schema.json`
- Create: `規格/工程/准入信任根.admitted.json`
- Create: `規格/工程/創世准入證據.json`
- Create: `規格/工程/保證/准入須有信任根.claim.json`
- Create: `架構/檢查准入信任根.py`
- Create: `架構/test_准入信任根.py`
- Modify: `架構/檢查已准入保證.py`

**Interfaces:**
- Produces: `AdmissionTrustRoot`——封閉欄位：trusted attestation issuer、repository/ref、
  workflow identity、actor identity extraction rule、trust-root revision/digest、
  expiry/revocation。
- Produces: repo-settings probe——查 ruleset 設定，驗證 **required workflow 不取自候選 PR
  可寫的 ref**，產出 content-addressed `ProbeRecord`（queried_at、api payload digest、
  verdict、TTL）。probe 走錄／播／明講跳過（既有燒錢測試紀律）：pytest 回放已錄 payload，
  live 查詢是本 task 的實測步。TTL 形狀比照 01B Task 4（fingerprint＋TTL，過期不得沿用）。
- Produces: 信任根缺席、過期或 probe 過期時，`檢查已准入保證.py` 對**新增** manifest entry
  一律 typed 拒絕 `ADMISSION_TRUST_ROOT_UNAVAILABLE`——fail-closed 是設計不是事故；
  已存在的 entry 照常比對集合與 digest，不受影響。
- Produces: 創世儀式是**明示、一次性、可驗證**的 transition：控制端建立 trust-root
  revision；由**另一個** attested actor 核准第一份 manifest；創世證據 content-addressed
  存進 `創世准入證據.json`。儀式之後一切新增 admission 走一般信任根路徑。
- Forbids: 宣稱 CI 信任方向已閉合。閉合與否由 probe 的 verdict 說話（Task 16 既有態度：
  必須實測後才准宣稱成立）；本 task 交付的是「未閉合時 fail-closed ＋ 閉合證據可機械檢查」。

**為什麼**：Task 16 的 manifest 擋得住「改弱已准入檔案」，但「誰有權新增 admission」
還是空的——受信任 attestation path 尚未存在時，任何角色分離檢查的 fixture 可以綠、
production admission 卻拿不到可信 actor。地基：SLSA v1.0 Source Track——身分與連續性
由平台 attestation 承載、從一個明確的起始 revision 建立並追蹤，不由被閘者自報；
NIST SSDF PO.4.2——判準資訊必須防竄改；CLAUDE.md 上限四的實測（CI 跑的是候選者
自己那份 checker）就是本 task 要求 probe 的原因。
加蓋（nova 多出來的拒絕）：無信任根的新增 admission、創世自我核准、創世重演。

**ClaimSpec:** 【推論】`engineering.admission.trust-root-required` 從紅轉綠。

**ClaimSpec落點:** `engineering.admission.trust-root-required` → `規格/工程/保證/准入須有信任根.claim.json`（本 task Create）

**固定負控:** 【推論】四格。`no-trust-root-new-admission`：信任根檔缺席（或 revoked）時
新增一條 manifest entry，必須紅在 `admission_requires_trust_root`（typed
`ADMISSION_TRUST_ROOT_UNAVAILABLE`，不得靜默通過）。`workflow-ref-candidate-writable`：
probe fixture 記錄 required workflow 取自候選 PR 可寫 ref，必須紅在
`workflow_ref_outside_candidate_write`。`genesis-self-approved`：創世證據裡建立者與
核准者解析為同一 actor，必須紅在 `genesis_requires_distinct_actor`。`genesis-twice`：
儀式已有證據後再送一次創世 transition，必須紅在 `genesis_occurs_at_most_once`。
防恆真格：合法信任根＋未過期 probe 下，新增一條合規 entry 通過；未觸碰 manifest 的
一般 commit 六道閘全綠照過。

- [ ] **Step 1: 寫四個負控與防恆真格的 red tests**

```python
def test_無信任根時新增准入必須被拒() -> None:
    結果 = 跑准入閘(工作樹(新增一條entry(), 信任根=None))
    assert 結果.code == "ADMISSION_TRUST_ROOT_UNAVAILABLE"

def test_創世不得自我核准() -> None:
    assert 驗創世(創世證據(建立者=甲(), 核准者=甲())).code == "GENESIS_SELF_APPROVAL"
```

- [ ] **Step 2: 跑紅測確認今天新增 admission 沒有任何身分要求**

Run: `uv run pytest -q 架構/test_准入信任根.py`

Expected: 【推論】FAIL；今天任何人在任何環境都能新增 manifest entry，
沒有 typed 拒絕。不得是 `ModuleNotFoundError` 之外什麼都沒紅。

- [ ] **Step 3: 寫 schema、checker 與 probe（錄／播）**

【推論】`檢查准入信任根.py` 的機械面：schema 驗證、digest、expiry、創世證據欄位與
distinct-actor；probe 面讀已錄 payload 判 verdict。**live probe 與創世儀式是控制端步驟**：
控制端執行 live 查詢與 trust-root revision 建立，另一 attested actor 核准第一份 manifest。

- [ ] **Step 4: 跑四個負控與防恆真格**

Run: `uv run pytest -q 架構/test_准入信任根.py && uv run python 工具/驗全部.py`

Expected: 【推論】PASS；四個負控各紅在自己宣告的 predicate；儀式完成前，
唯一合法的新增路徑是創世 transition 本身。

- [ ] **Step 5: Commit**

```bash
git add 規格/工程/AdmissionTrustRoot.schema.json 規格/工程/准入信任根.admitted.json 規格/工程/創世准入證據.json 規格/工程/保證/准入須有信任根.claim.json 架構/檢查准入信任根.py 架構/test_准入信任根.py 架構/檢查已准入保證.py
git commit -m "feat: 准入要有信任根，創世儀式一次性可驗證"
```

---

### Task 18: 准入職責分離要比對到 attested actor

**Files:**
- Create: `規格/工程/保證/准入職責分離.claim.json`
- Modify: `規格/驗收/ClaimAdmissionManifest.schema.json`
- Modify: `架構/檢查已准入保證.py`
- Modify: `架構/test_已准入保證.py`

**Interfaces:**
- Produces: manifest entry 增四角色欄——`subject_changed_by`／`criterion_authored_by`／
  `admission_decided_by`／`evidence_executed_by`，每欄是 `{textual_id, attestation_ref}`。
- Produces: 比對單位是**依信任根（Task 17）的 actor identity extraction rule 解析出的
  actor**，不是自填字串；最低約束 `admission_decided_by != subject_changed_by`
  （解析後不得同一 actor）。`criterion_authored_by`／`evidence_executed_by` v1 只記錄
  不強制——Clark–Wilson 要分離的是裁定方與能改動受保護實體的主體，
  獨立 CI 執行檢查不在禁止之列。
- Forbids: 任一強制角色缺可信 attestation、或信任根 probe 過期時放行——一律 typed
  `UNVERIFIED_ROLE_SEPARATION` 拒絕，不做 `SELF_CERTIFIED` 之類的標記後放行（不得靜默降級）。

**為什麼**：Task 16 的 `engineering.admission.closure-immutable` 綠著，而同一主體
既裁定准入又改 subject 時，保證名義成立、實質為零（Clark–Wilson ER4 後半缺席）。
比對字串抓不到同一把 key 簽兩個名字（CERT 內部威脅案例 5 正是用主管帳號 check-in——
字串合規、身分已破）。地基：Clark & Wilson 1987（DOI 10.1109/SP.1987.10001）ER3——
「must authenticate each user attempting to execute a TP」，身分是 SoD 的前提不是配套；
NIST SP 800-53 AC-5（DOI 10.6028/NIST.SP.800-53r5）；SLSA Source Track。
加蓋：解析後同 actor 跨兩角、無可信 attestation、probe 過期，三者 admission 紅。

**ClaimSpec:** 【推論】`engineering.admission.role-separation-attested` 從紅轉綠。

**ClaimSpec落點:** `engineering.admission.role-separation-attested` → `規格/工程/保證/准入職責分離.claim.json`（本 task Create）

**固定負控:** 【推論】四格。`same-actor-two-ids`：同一把簽章 key（同一 OIDC sub）簽出
兩個不同 textual id 分掛 decider 與 changer，必須紅在 `roles_resolve_to_distinct_actors`。
`decider-is-changer`：attestation 合法但解析後同一 actor，必須紅在同一條。
`no-attestation`：四欄齊但 `attestation_ref` 指向不可驗來源（自填 JSON），必須紅在
`unverified_role_separation_rejected`。`stale-probe`：信任根 probe 過期時送新 entry，
必須紅在 `role_separation_requires_live_trust_root`——本格是 Task 17 的 live probe
前置的機械化，不能只靠本地簽章 fixture 轉綠。
防恆真格：相異 attested actor、來源可驗、probe 未過期的 entry 放行；
未觸碰 manifest 的一般 commit 六道閘全綠照過。

- [ ] **Step 1: 寫四個負控與防恆真格的 red tests**

```python
def test_同把鑰匙簽兩個名字必須被抓() -> None:
    entry = 造entry(decider=簽名(鑰匙甲(), "審查者"), changer=簽名(鑰匙甲(), "實作者"))
    assert 驗職責分離(entry, 信任根()).code == "ROLE_SEPARATION_VIOLATED"
```

- [ ] **Step 2: 跑紅測確認今天同一 key 簽兩個名字沒有任何東西紅**

Run: `uv run pytest -q 架構/test_已准入保證.py -k 職責`

Expected: 【推論】FAIL；manifest 目前沒有任何主體欄，角色分離無從檢查。

- [ ] **Step 3: 寫四角色欄、actor 解析與不等式檢查**

- [ ] **Step 4: 跑四個負控與防恆真格**

Run: `uv run pytest -q 架構/test_已准入保證.py && uv run python 工具/驗全部.py`

Expected: 【推論】PASS；四個負控各紅在自己宣告的 predicate，防恆真格綠。

- [ ] **Step 5: Commit**

```bash
git add 規格/工程/保證/准入職責分離.claim.json 規格/驗收/ClaimAdmissionManifest.schema.json 架構/檢查已准入保證.py 架構/test_已准入保證.py
git commit -m "feat: 准入職責分離比對到 attested actor"
```

---

## Plan Exit Gate

【推論】本 plan 完成的唯一判定命令是：

```bash
uv run ruff format --check . && uv run ruff check . && uv run mypy nova 架構 工具 && uv run python 架構/檢查工程規範.py && uv run python 架構/檢查已准入保證.py && uv run python 架構/檢查准入信任根.py && uv run pytest -q -n 2 架構/test_工程規範.py 架構/test_已准入保證.py 架構/test_准入信任根.py 驗收/工具鏈 驗收/保證規格語言 nova/核心 nova/權威/判準 nova/基礎設施/裁定執行
```

【推論】必須同時保存工程規範四類fixed negative、第一份 wall-limit actual ACCEPT、positive ACCEPT、negative direct CLAIM_REJECTED evidence；只有 pytest exit 0 而缺 direct red evidence不算完成。

## Execution Handoff

【推論】完成後進 [02-宣告式狀態機.md](./02-宣告式狀態機.md)。若使用 subagent-driven execution，每個 Task 一個 fresh worker，先審 ClaimSpec／負控，再審 production code；不得讓同一 worker 自己宣稱它寫的 judge 有牙。
Expected: 【推論】PASS；同 UID offer 不含四個 hostile capabilities。

- [ ] **Step 5: Commit**

```bash
git add 規格/判準/IsolationCapability.schema.json nova/基礎設施/裁定執行/隔離執行.py 驗收/判準/測_威脅聲明.py
git commit -m "test: 把隔離 claim 綁到宿主探針"
```

---

### Task 8: 揭露帳是 state owner 管的持久 aggregate

**Files:**
- Create: `規格/判準/揭露帳.machine.json`
- Create: `規格/判準/DisclosureLedger.schema.json`
- Create: `nova/權威/判準/揭露帳本.py`
- Create: `驗收/判準/測_揭露帳本.py`
- Create: `規格/判準/保證/揭露總量有界.claim.json`
- Modify: `規格/判準/CriterionDefinition.schema.json`
- Modify: `規格/判準/FeedbackPolicy.schema.json`
- Modify: `nova/應用/執行判準.py`

**Interfaces:**
- Produces: `揭露帳.machine.json`——明示 machine，command `ReserveDisclosure`、
  event `DisclosureRecorded`／`DisclosureExhausted`。應用層只能呼叫
  `StateOwnerClient.execute(CommandEnvelope)`（計畫 03），
  `CommandEnvelope.entity_id = sealed_pool_lineage_id`，**不得直接 append event**。
- Produces: 順序契約——transition transaction 之前，先把 canonical FeedbackPacket bytes
  放入 CAS（計畫 04）；event 必記 `disclosure_id`、`packet_content_ref`、`packet_digest`、
  `sealed_pool_lineage_id`、`ordinal`；`DisclosureRecorded` commit 成功後才釋出 packet bytes
  ——與本計畫 Task 6「先 `CaseBurned` 再 reveal」同一個已驗證形狀。
- Produces: crash 後從 CAS 以 `packet_content_ref` 取回**完全相同的 bytes** 重送同一
  `disclosure_id`，不重跑 reducer、不計新額度——「重新執行大概會一樣」不是保證。
- Produces: machine 必須拒絕——同 `disclosure_id` 不同 `packet_digest`；`ordinal` 超
  `disclosure_cap`；`sealed_pool_lineage_id` 不符；三者為 machine spec 內的固定負控，
  由 `工具/驗規格.py` 驗（計畫 02 的既有形狀）。
- Produces: `sealed_pool_lineage_id`——sealed pool 首建時鑄的內容定址 lineage id；
  criterion revision supersede 與 sibling／superseding Pursuit 都承繼，額度跨它們累計。
  `CriterionDefinition` 增必填 `sealed_pool_lineage_id`；`FeedbackPolicy` 增必填
  `disclosure_cap`（事前釘）。
- Forbids: `nova/權威/判準/揭露帳本.py` 做 I/O——它只做純 fold／決策
  （事件序列 → 剩餘額度／`DISCLOSURE_BUDGET_EXHAUSTED`），`allow_io=false` 不衝突；
  持久化與 I/O 全走應用層的 state owner port。

**為什麼**：Task 5／6 的保證綠著，sealed 判準的辨識力卻跨 run 靜默流失——
揭露帳若只活在權威層記憶體，程序重啟即洗掉 cap，而負控只測同一程序內的第 cap+1 次。
持久性交給已存在的 state owner（06 前置含 03），key 換成洗不掉的 lineage。
地基：Dwork 等 arXiv:1506.02629 Theorem 17——只取「有限 transcript range ⇒ 有限
max-information 上界」這個形狀，|Y| 按整段 transcript 計、adaptive composition 下累加，
所以 key 必須是跨 revision／Pursuit 的 lineage 而不是單次 run（正式引用時區分
Theorem 17 的有限 range bound 與 adaptive composition lemma）；NIST FRVT／SRE 的
提交限流是實務存在、定性、不對題——照實標。cap 數值與「先記帳再釋出」的具體形狀：
無地基，這是 nova 的拆解決定（Task 6 既有模式的重用）。宣稱 DP／統計有效性的請求
→ `UNSUPPORTED_DISCLOSURE_MECHANISM`。
加蓋：超 cap 停發（verdict 照記，只斷回饋）；lineage 額度不可被 revision／sibling 洗掉；
commit 前不得釋出；重送只認同 digest。

**ClaimSpec:** 【推論】`criterion.disclosure.transcript-bounded` 從紅轉綠。

**ClaimSpec落點:** `criterion.disclosure.transcript-bounded` → `規格/判準/保證/揭露總量有界.claim.json`（本 task Create）

**固定負控:** 【推論】五格。`crash-then-reset`：cap 前 SIGKILL、重啟後從零計數繼續釋出
的變體，必須紅在 `ledger_survives_restart`。`sibling-resets-budget`：superseding Pursuit
拿新額度的變體，與 `revision-resets-budget`（換 criterion revision、同 lineage 拿新額度）
皆必須紅在 `lineage_scoped_budget`。`release-before-commit`：ledger commit 前就 return
packet bytes 的變體，必須紅在 `disclose_after_persist`。`disclosure-beyond-cap`：
cap+1 次照發的變體，必須紅在 `disclosure_beyond_budget_refused`。
machine 層三格固定負控住在 `揭露帳.machine.json` 內（同 id 不同 digest／ordinal 超 cap／
lineage 不符），由 `工具/驗規格.py --含固定負控` 驗。
防恆真格：cap 內正常 feedback 逐次照發；crash 後重送同 `disclosure_id` 同 digest
不重複扣額度；cap 滿後 verdict 記錄照常。

- [ ] **Step 1: 寫五個負控與防恆真格的 red tests（SIGKILL matrix 沿用 Task 6 形狀）**

```python
def test_崩潰重啟後額度不得歸零() -> None:
    軌跡 = 揭露到(3, 政策(disclosure_cap=5), 崩潰於="第三次commit後")
    重啟 = 重建帳本(軌跡.資料根)
    assert 重啟.已揭露 == 3
```

- [ ] **Step 2: 跑紅測確認今天重啟就洗掉 cap**

Run: `uv run pytest -q 驗收/判準/測_揭露帳本.py`

Expected: 【推論】FAIL；揭露計數只活在程序記憶體，重啟後從零開始。
不得是 `ModuleNotFoundError` 冒充紅測。

- [ ] **Step 3: 寫 machine spec 並驗固定負控**

Run: `uv run python 工具/驗規格.py 規格/判準/揭露帳.machine.json --含固定負控`

Expected: 【推論】PASS；同 id 不同 digest、ordinal 超 cap、lineage 不符三格
machine 負控各自 direct red。

- [ ] **Step 4: 寫純 fold 帳本與應用層順序（CAS → ReserveDisclosure → commit → release）**

- [ ] **Step 5: 跑五個負控、防恆真格與 ClaimSpec**

Run: `uv run pytest -q 驗收/判準/測_揭露帳本.py && uv run python 工具/跑驗收.py --claim criterion.disclosure.transcript-bounded`

Expected: 【推論】PASS；五個負控各紅在自己宣告的 predicate。

- [ ] **Step 6: Commit**

```bash
git add 規格/判準/揭露帳.machine.json 規格/判準/DisclosureLedger.schema.json 規格/判準/保證/揭露總量有界.claim.json 規格/判準/CriterionDefinition.schema.json 規格/判準/FeedbackPolicy.schema.json nova/權威/判準/揭露帳本.py nova/應用/執行判準.py 驗收/判準/測_揭露帳本.py
git commit -m "feat: 揭露帳持久化，額度跨 run 不歸零"
```

---

## Plan Exit Gate

- 【推論】候選 projection 的可見 bytes、argv、env、fds 都不含 sealed canary；evaluator projection 仍能執行 sealed cases。
- 【推論】required capability 缺一項即 `UNSUPPORTED_ISOLATION`，沒有 fallback branch。
- 【推論】raw assertion repr 不進 FeedbackPacket；clause id 與 retry class 保留最小梯度。
- 【推論】揭露先 burn 後 release，全部 crash points 後 case 都不會被重用。
- 【推論】`uv run pytest -q nova/權威/判準 nova/基礎設施/裁定執行 nova/應用/test_執行判準.py 驗收/判準 -n 2` 與本 plan ClaimSpecs 全綠。

## Execution Handoff

【推論】Task 3 與 Task 7 的審查者要逐項比對「宣稱能力」與真實機制，不接受以文件宣稱取代 probe。完成本 plan 與 plan 07 後，才有資格實作 Pursuit feedback loop。

exec
/bin/zsh -lc "sed -n '250,315p' /private/tmp/fable-R3-mock/docs/計畫/09-持久工作協調與選拔.md
sed -n '165,230p' /private/tmp/fable-R3-mock/docs/計畫/01B-執行者能力契約與SDK探針.md
rg -n \"ProbeRecord|TTL|live probe|錄／播|創世|控制端\" /private/tmp/fable-R3-mock/docs/計畫/01-可執行保證語言.md | tail -n 80
rg -n \"FeedbackPacket|packet_content_ref|CAS|ReserveDisclosure|DisclosureRecorded\" /private/tmp/fable-R3-mock/docs/計畫/06-判準評估與隔離回饋.md | tail -n 100" in /Users/sbu/nova
 succeeded in 0ms:
---

### Task 4: 建立 deterministic BEST_BEFORE_DEADLINE 選拔

**Files:**
- Create: `規格/工作/最佳截止前.policy.json`
- Create: `規格/工作/RankingSchema.schema.json`
- Create: `規格/工作/ScoreEvidence.schema.json`
- Create: `nova/領域/工作/選拔.py`
- Create: `nova/領域/工作/test_選拔.py`
- Modify: `nova/領域/工作/決策.py`
- Create: `驗收/三層流程/測_選拔截止.py`
- Create: `規格/工作/保證/最佳截止前選拔.claim.json`
- Create: `規格/工作/保證/分數證據准入.claim.json`

**Interfaces:**
- Produces: `rank_candidates(schema, verdicts, cutoff_seq) -> SelectionRecord`。
- Produces: cutoff reasons `DEADLINE|ALL_CHILDREN_TERMINAL|PERMANENT_RESOURCE_EXHAUSTION`。
- Produces: 每維分數必附 `ScoreEvidence`，封閉二選一——`EXACT_OBSERVATION`＝
  {`verifier_primitive_id`, `primitive_revision`, `evidence_digest`}，其中原語必須在已准入目錄
  （01 Task 15）且 `result_semantics = EXACT_ARTIFACT_FUNCTION`；`ESTIMATED`＝
  {`estimator`, `sampling_unit`, `interval_procedure`, `confidence_level`, `sample_size`,
  `analysis_digest`, `interval`}。deterministic 但 `result_semantics = ESTIMATOR` 的原語
  仍必須走 `ESTIMATED`——可重現不等於無抽樣不確定度。
- Produces: 每個分數綁 `evaluator_revision` 與 `candidate_digest`，不匹配 → `REJECT_CANDIDATE`；
  `score_source ∈ {VERIFIER_MEASURED, EXTERNAL_ATTESTED}`，裸數字與 `EXECUTOR_SELF_REPORT` 拒絕。
- Produces: `SelectionRecord.winner_separation ∈ {CLEAR, OVERLAPPING}` 由冠亞軍 interval
  機械推導；輸入 schema 不收此欄（closed schema，unknown field 拒絕）。排序本身仍是
  點值＋digest tie-break，不變。

**ClaimSpec:** 【推論】`work.selection.best-before-deadline` 與 `work.selection.score-evidence-admitted` 從紅轉綠。

**ClaimSpec落點:** `work.selection.best-before-deadline` → `規格/工作/保證/最佳截止前選拔.claim.json`（本 task Create）；`work.selection.score-evidence-admitted` → `規格/工作/保證/分數證據准入.claim.json`（本 task Create）

**固定負控:** 【推論】第一個 ACCEPT 不是最高分、相同分數 input iteration order 不同、verdict 在 cutoff seq 後才落盤；winner 必須仍是 cutoff 前依 schema 最佳者，晚到者 excluded。
分數證據三格：`estimated-claims-exact`——由 `result_semantics = ESTIMATOR` 的原語背書
卻標 `EXACT_OBSERVATION` 的分數 fixture，必須紅在 `exact_requires_exact_artifact_function`；
`evaluator-candidate-mismatch`——`evaluator_revision` 與 verdict 不符、`candidate_digest`
指到別的候選的 fixture，必須紅在 `score_bound_to_evaluator_and_candidate`；
`forged-separation`——改成照抄呼叫端 separation 值而非自行推導的 `選拔.py` 變體，
必須紅在 `separation_machine_derived`。
防恆真格：`VERIFIER_MEASURED`＋`EXACT_ARTIFACT_FUNCTION` 原語背書的分數照常參賽，
選出與原 claim 相同的 winner，permutation property 不變。

- [ ] **Step 1: 寫 first-acceptable、tie、late-verdict 與 score-evidence red**

```python
def test_selection_uses_rank_not_arrival_order() -> None:
    result = rank_candidates(schema_desc("quality"), [accepted("early", 10, seq=5), accepted("late", 20, seq=7)], cutoff_seq=7)
    assert result.winner_ref == candidate_ref("late")

def test_估計原語背書的分數不得標成精確() -> None:
    分 = 分數(7.5, 證據=精確觀測(估計原語ref()))
    assert admit_score(分, 已准入目錄()).code == "REJECT_CANDIDATE"
```

- [ ] **Step 2: 跑 tests 確認 arrival order 決定 winner、裸分數照樣進 comparator**

Run: `uv run pytest -q nova/領域/工作/test_選拔.py 驗收/三層流程/測_選拔截止.py`

Expected: 【推論】FAIL；LLM 吐的裸 `7.5` 今天直接進 winner comparator，沒有任何 schema 拒絕它。

- [ ] **Step 3: 寫 typed normalization、ordered comparator、digest tie-break**

```python
rank_key = tuple(normalize(score[dim.score_id], dim) for dim in schema.dimensions) + (candidate.digest.value,)
- [ ] **Step 2: 跑 `uv run pytest -q 驗收/執行者能力/測_SDK靜態介面.py`**

Expected: 【推論】FAIL；probe 尚不存在，或缺 surface 的 fixture 被放行。

- [ ] **Step 3: pin SDK 並以 public inspect/type metadata 寫 exhaustive probe**
- [ ] **Step 4: 跑 tests、真 pinned package probe 與 ClaimSpec，確認 PASS**
- [ ] **Step 5: Commit**

```bash
git add pyproject.toml uv.lock 工具/探ClaudeSDK介面.py 驗收/執行者能力/測_SDK靜態介面.py 規格/執行/保證/能力/SDK靜態介面存在.claim.json
git commit -m "test: 釘住 Claude SDK 的能力面"
```

---

### Task 4: 讓 CapabilityEvidence 綁 exact fingerprint、controls 與 TTL

**Files:**
- Create: `規格/執行/CapabilityEvidence.schema.json`
- Modify: `nova/領域/執行/能力.py`
- Create: `驗收/執行者能力/測_能力證據.py`
- Create: `規格/執行/保證/能力/能力證據不可沿用.claim.json`

**Interfaces:**
- Produces: `validate_capability_evidence(evidence, exact_fingerprint, now) -> VALID|EXPIRED|FINGERPRINT_MISMATCH|CONTROL_INCOMPLETE`。
- Produces: repeatability evidence 必記 {`N`, 環境／backend fingerprint, request digest,
  全部 N 份輸出 digest, TTL}；determinism evidence 必記 {`mechanism = PURE_REPLAYER`,
  重播器 claim ref（`execution.backend.replayer-contract-parity`）}；contractual evidence
  必記 {contract ref, conformance suite ref, pass record digest}。
- Forbids: repeatability 或 contractual evidence 升格為 determinism——N 次逐 byte 相同
  只證成「觀測到重複性」，第 N+1 次仍可能變。

**ClaimSpec:** 【推論】`execution.backend-capability.evidence-fingerprint-ttl-bound` 從紅轉綠。

**ClaimSpec落點:** `execution.backend-capability.evidence-fingerprint-ttl-bound` → `規格/執行/保證/能力/能力證據不可沿用.claim.json`（本 task Create）

**固定負控:** 【推論】SDK/CLI/model/settings catalog 任一 digest 改變仍沿用舊 evidence，或 `now == expires_at` 仍 VALID；direct red。
seeded 家族四格：`probe-upgraded-to-determinism`——把 N 次 probe evidence 直接寫成
`SEEDED_OUTPUT_DETERMINISM` supported 的 faulty capability mapper，必須紅在
`determinism_requires_mechanistic_evidence`。`nth-plus-one-differs`——`假能力後端.py`
增一個前 N 次輸出逐 byte 相同、第 N+1 次改變的變體，其 evidence 記為 repeatability，
faulty 檢查器據此讓要求 determinism 的綁定通過，必須紅在 `repeatability_is_not_determinism`。
`forged-mechanistic-ref`——mechanism 填 `PURE_REPLAYER` 但 ref 指向不可驗來源（自填 JSON、
非重播器 claim）的 evidence，必須紅在 `mechanistic_ref_must_resolve`。
`contract-claim-cannot-bind-mechanical`——持 `CONTRACTUAL_OUTPUT_DETERMINISM_CLAIMED`
（含合法 contract ref 與 suite pass record）的後端綁定要求 `SEEDED_OUTPUT_DETERMINISM`
的 claim，必須紅在 `contract_claim_is_not_mechanism`；fixture 內附 suite 外輸出改變的
見證（suite 全過而 suite 外同 seed 輸出漂移），釘死「suite 過」不等於「機械決定」。
防恆真格：計畫 05 純函式重播器以 `PURE_REPLAYER` mechanism evidence 取得
`SEEDED_OUTPUT_DETERMINISM` supported——拒絕不是無條件；帶合規 N 次 probe 的後端
取得 `SEEDED_OUTPUT_REPEATABILITY_OBSERVED` supported。

- [ ] **Step 1: 寫 fingerprint one-field mutation 與 TTL boundary red**
- [ ] **Step 2: 跑 `uv run pytest -q 驗收/執行者能力/測_能力證據.py`**

Expected: 【推論】FAIL；舊 evidence 尚會跨 fingerprint／expiry 被接受。

- [ ] **Step 3: 寫 canonical evidence validation 與 closed invalid reasons**
- [ ] **Step 4: 跑 tests 與 ClaimSpec，確認 PASS**
- [ ] **Step 5: Commit**

```bash
git add 規格/執行/CapabilityEvidence.schema.json nova/領域/執行/能力.py 驗收/執行者能力/測_能力證據.py 規格/執行/保證/能力/能力證據不可沿用.claim.json
git commit -m "feat: 把能力證據綁到執行期指紋"
```

11:**Spec:** 【查證】本檔「子系統規格」，以及[第二輪 ClaimSpec](../決策/sol-新局-第二輪.md#5-q5第一份具體檔案與-claimspec-v0)、[第五輪工具鏈實測](../決策/sol-新局-第五輪.md#4-cpython-314不是看起來支援是真的跑過)、[控制端複驗](../決策/控制端審查.md#工具鏈我的一手複驗不是採信它的宣稱)、[Ruff設定與check模式](https://docs.astral.sh/ruff/configuration/)、[mypy strict構成](https://mypy.readthedocs.io/en/stable/existing_code.html)、[Python identifier normalization](https://docs.python.org/3/reference/lexical_analysis.html#identifiers)與[Bash name定義](https://www.gnu.org/software/bash/manual/html_node/Definitions.html)。
94:規格/工程/創世准入證據.json                    — 一次性創世儀式的 content-addressed 證據。
96:架構/檢查准入信任根.py                         — schema/digest/expiry/創世＋probe 錄播。
97:架構/test_准入信任根.py                        — 無信任根、可寫 ref、自我核准、創世重演。
1210:### Task 17: 建立准入信任根與創世儀式
1215:- Create: `規格/工程/創世准入證據.json`
1226:  可寫的 ref**，產出 content-addressed `ProbeRecord`（queried_at、api payload digest、
1227:  verdict、TTL）。probe 走錄／播／明講跳過（既有燒錢測試紀律）：pytest 回放已錄 payload，
1228:  live 查詢是本 task 的實測步。TTL 形狀比照 01B Task 4（fingerprint＋TTL，過期不得沿用）。
1232:- Produces: 創世儀式是**明示、一次性、可驗證**的 transition：控制端建立 trust-root
1233:  revision；由**另一個** attested actor 核准第一份 manifest；創世證據 content-addressed
1234:  存進 `創世准入證據.json`。儀式之後一切新增 admission 走一般信任根路徑。
1244:加蓋（nova 多出來的拒絕）：無信任根的新增 admission、創世自我核准、創世重演。
1254:`workflow_ref_outside_candidate_write`。`genesis-self-approved`：創世證據裡建立者與
1256:儀式已有證據後再送一次創世 transition，必須紅在 `genesis_occurs_at_most_once`。
1267:def test_創世不得自我核准() -> None:
1268:    assert 驗創世(創世證據(建立者=甲(), 核准者=甲())).code == "GENESIS_SELF_APPROVAL"
1278:- [ ] **Step 3: 寫 schema、checker 與 probe（錄／播）**
1280:【推論】`檢查准入信任根.py` 的機械面：schema 驗證、digest、expiry、創世證據欄位與
1281:distinct-actor；probe 面讀已錄 payload 判 verdict。**live probe 與創世儀式是控制端步驟**：
1282:控制端執行 live 查詢與 trust-root revision 建立，另一 attested actor 核准第一份 manifest。
1289:唯一合法的新增路徑是創世 transition 本身。
1294:git add 規格/工程/AdmissionTrustRoot.schema.json 規格/工程/准入信任根.admitted.json 規格/工程/創世准入證據.json 規格/工程/保證/准入須有信任根.claim.json 架構/檢查准入信任根.py 架構/test_准入信任根.py 架構/檢查已准入保證.py
1295:git commit -m "feat: 准入要有信任根，創世儀式一次性可驗證"
1336:必須紅在 `role_separation_requires_live_trust_root`——本格是 Task 17 的 live probe
7:**Architecture:** 【推論】判準面拆成 immutable definition authority、evaluation authority 與 feedback reducer。候選只取得 guidance pool 的公開條款；sealed pool 的檔案與 expected values 不進候選 workspace。評估器在 execution 結束後取得候選 CAS snapshot，以 `IsolationCapability` 協商可執行等級；reducer 只輸出 clause-level code、位置類別與 remediation class，不逐字轉送 assertion repr。
9:**Tech Stack:** 【推論】CPython 3.14.7、ClaimSpec/TestPlan、MachineSpec、temporary filesystem projection、subprocess evaluator、CAS evidence、SQLite state owner。
25:【推論】`Verdict` 是 evaluation authority 的產物，包含每條 claim 的 typed result與 evidence refs；它不包含 ClaimSpec source bytes。`FeedbackPacket` 是衍生物，不是 verdict 本體。
34:├── 揭露帳.machine.json                       — ReserveDisclosure／Recorded／Exhausted。
49:├── 回饋閘.py                                 — raw result -> FeedbackPacket reducer。
74:【推論】必須先完成 plan 01–05。沒有 ClaimSpec control semantics，sealed negative 可能是假紅；沒有 MachineSpec/state owner，case burn 與 verdict 會在 crash 後分叉；沒有 CAS，原始 evidence 會被塞入 feedback；沒有 execution envelope，evaluator 自身沒有外部上限。缺任何一項都不能宣稱判準權在執行者之外。
262:- Persists: raw evidence CAS ref、TestPlan digest、candidate snapshot digest、per-claim CaseResult。
318:- Produces: `reduce_feedback(verdict, policy) -> FeedbackPacket`。
323:**固定負控:** 【推論】raw assertion 為 `expected SECRET-ANSWER-441, got 0`；FeedbackPacket canonical bytes 不得含 `SECRET`、`ANSWER`、`441` 或 raw repr，但要含失敗 `clause_id`。
344:return FeedbackPacket(items=tuple(FeedbackItem(clause_id=r.clause_id, outcome_class=map_outcome(r), location_bucket=map_location(r), retryability=map_retry(r)) for r in verdict.results))
394:- [ ] **Step 3: 先 append-once `CaseBurned`，再從 CAS 釋出 raw bytes**
479:- Produces: `揭露帳.machine.json`——明示 machine，command `ReserveDisclosure`、
480:  event `DisclosureRecorded`／`DisclosureExhausted`。應用層只能呼叫
483:- Produces: 順序契約——transition transaction 之前，先把 canonical FeedbackPacket bytes
484:  放入 CAS（計畫 04）；event 必記 `disclosure_id`、`packet_content_ref`、`packet_digest`、
485:  `sealed_pool_lineage_id`、`ordinal`；`DisclosureRecorded` commit 成功後才釋出 packet bytes
487:- Produces: crash 後從 CAS 以 `packet_content_ref` 取回**完全相同的 bytes** 重送同一
551:- [ ] **Step 4: 寫純 fold 帳本與應用層順序（CAS → ReserveDisclosure → commit → release）**
572:- 【推論】raw assertion repr 不進 FeedbackPacket；clause id 與 retry class 保留最小梯度。

context compacted
codex
機械閘已由你與 fable 各跑一次；我現在只補查「語意是否真的有牙」，不把 I1–I11 全綠誤當成設計正確。最關鍵的是 R3-03 所引用的重播器 claim，及 R3-04 外部信任是否被 TTL 錄播偷換成當下保證。
exec
/bin/zsh -lc "rg -n -C 8 'execution\\.backend\\.replayer-contract-parity|replayer-contract-parity|重播器' docs/計畫/05-執行封套與重播器.md | head -n 180" in /Users/sbu/nova
 succeeded in 0ms:
1:# 執行封套與重播器 Implementation Plan
2-
3-> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:subagent-driven-development` (recommended) or `superpowers:executing-plans` to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.
4-
5:**Goal:** 【推論】建立一次執行的外部權威邊界：後端只能產生事件與候選產物，不能延長 wall time／回合／輸出／核准花費，也不能指定自己的權威終態；純函式重播器以零付費跑完整契約。
6-
7-**Architecture:** 【推論】`ExecutionEnvelope` 是第一個垂直生命週期。領域決策只讀 `ExecutionFacts`，程序監督、時鐘與資源保留由 port 提供；每個後端實作相同的 typed event protocol。封套把後端事件歸約成權威狀態，超限時由父程序終止整個 process group，最終只發布一個 typed terminal event。
8-
9-**Tech Stack:** 【推論】CPython 3.14.7、asyncio、`subprocess` process groups、Linux/macOS platform adapter、JSON Schema、SQLite owner port（由 plan 03 提供）、ClaimSpec runner（plan 01）。
10-
11-**Spec:** 【查證】本檔「子系統規格」，以及[第一輪性質 1](../sol-新局-第一輪.md)、[第二輪三層裁決](../sol-新局-第二輪.md)、[第三輪狀態機定案](../sol-新局-第三輪.md)、[第五輪 Guard 與工具鏈定案](../sol-新局-第五輪.md)。
12-
13-## Global Constraints
14-
15-- 【推論】後端事件中的 `done`、`success`、文字「完成」都只是觀測，不是權威終態。
16-- 【推論】wall time、回合、輸出 bytes、工具呼叫與核准花費的計數器由封套持有；後端拿不到可寫 reference。
17-- 【推論】每次執行恰有一個終態：`SUCCEEDED`、`FAILED`、`TIMED_OUT`、`ROUND_LIMITED`、`OUTPUT_LIMITED`、`SPEND_LIMITED`、`CANCELLED`、`BACKEND_LOST`、`UNSUPPORTED_CAPABILITY`、`INTERNAL_FAULT`。
18-- 【推論】程序型後端必須以 argv 啟動，禁止 shell string；終止需覆蓋孫程序且有 kill escalation。
19:- 【推論】重播器與付費後端接受相同 `ExecutionRequest`、產生相同 `BackendEvent` union，不另開測試捷徑。
20-- 【推論】`ExecutionRequest` 引用 plan 01B 的 `ToolAuthorizationPolicyRef`、`StructuredOutputContractRef`、`DelegationPolicyRef`；manifest 以 `PRE_TOOL_DECISION|NATIVE_STRUCTURED_OUTPUT|DELEGATION` 宣告能力，缺 required capability 只回 typed `UNSUPPORTED_CAPABILITY`。
21-- 【推論】工具操作分成 `READ_ONLY|EFFECT_INTENT_REQUIRED|LOCAL_WORKSPACE_MUTATION|DELEGATION`；`EFFECT_INTENT_REQUIRED` handler 只能呼叫 EffectIntent port，不得直接碰外部 endpoint。
22-- 【推論】usage observation 必帶 `ROOT_ONLY|DELEGATION_TREE_TOTAL|UNKNOWN` scope；封套不得把 root usage 升格成 tree total。
23-
24-## 子系統規格
25-
26-【推論】`ExecutionRequest` 固定包含 `execution_id`、`pursuit_id`、`backend_ref`、`workspace_snapshot_ref`、`input_payload_ref`、`limits`、`isolation_offer_ref`、`budget_reservation_ref`、`idempotency_key`；不包含判準內容。
27-
--
38-├── BackendEvent.schema.json                  — 封閉後端事件 union。
39-├── 綁定/
40-│   └── production執行封套.binding.json       — production supervisor exact capability binding。
41-└── 保證/
42-    ├── 外部時間上限.claim.json               — wall deadline 由父程序強制。
43-    ├── 外部回合上限.claim.json               — 第 N+1 回合不會送入後端。
44-    ├── 外部輸出上限.claim.json               — 超量 bytes 截斷並 typed terminal。
45-    ├── 執行者不得裁定終態.claim.json         — 自報成功不越權。
46:    └── 重播器同契約.claim.json               — replay 與付費 adapter 契約一致。
47-nova/領域/執行/
48-├── 公開契約.py                               — request、limits、events、terminal public types。
49-├── 模型.py                                   — ExecutionAggregate 與 counter state。
50-├── 決策.py                                   — 純函式 command/fact -> events。
51-├── 端口.py                                   — Backend、Supervisor、Clock、BudgetPort protocols。
52-└── test_執行決策.py                          — state/limit decision-table tests。
53-nova/介接/執行者後端/
54-├── 共用/
55-│   ├── manifest.py                           — capability manifest model。
56-│   ├── 契約套件.py                           — adapter contract suite。
57-│   └── 程序事件.py                           — stdout/stderr/exit normalization。
58:└── 重播器/
59-    ├── manifest.py                           — deterministic zero-cost capabilities。
60-    ├── 執行.py                               — script -> async BackendEvent stream。
61-    └── test_契約.py                          — 共用 contract suite instance。
62-nova/基礎設施/系統/
63-├── 程序監督.py                               — process-group spawn/TERM/KILL。
64-├── 單調時鐘.py                               — monotonic deadline implementation。
65-└── test_程序監督.py                          — child/grandchild kill integration tests。
66-nova/應用/執行封套.py                         — load、reserve、run、persist terminal orchestration。
--
143-
144-```bash
145-git add 規格/執行/執行.machine.json nova/領域/執行
146-git commit -m "feat: 宣告執行生命週期與終態"
147-```
148-
149----
150-
151:### Task 2: 定義跨後端 request/event contract 與重播器
152-
153-**Files:**
154-- Create: `規格/執行/ExecutionRequest.schema.json`
155-- Create: `規格/執行/BackendEvent.schema.json`
156-- Create: `nova/領域/執行/端口.py`
157-- Create: `nova/介接/執行者後端/共用/manifest.py`
158-- Create: `nova/介接/執行者後端/共用/契約套件.py`
159:- Create: `nova/介接/執行者後端/重播器/manifest.py`
160:- Create: `nova/介接/執行者後端/重播器/執行.py`
161:- Create: `nova/介接/執行者後端/重播器/test_契約.py`
162:- Create: `規格/執行/保證/重播器同契約.claim.json`
163-
164-**Interfaces:**
165-- Produces: `ExecutorBackend.events(request) -> AsyncIterator[BackendEvent]`。
166-- Produces: `ReplayScript(events, virtual_elapsed_ms, declared_cost)`。
167-
168:**ClaimSpec:** 【推論】`execution.backend.replayer-contract-parity` 從紅轉綠。
169-
170-**固定負控:** 【推論】重播 script 發出未知 event kind `hidden_success`；schema 與 adapter contract 必須在進 state owner 前拒絕。
171-
172-- [ ] **Step 1: 寫共用 contract suite 的 schema／順序 red tests**
173-
174-```python
175-async def assert_backend_contract(backend: ExecutorBackend) -> None:
176-    events = [event async for event in backend.events(fixed_request())]
177-    assert events[0].kind == BackendEventKind.STARTED
178-    assert all(validate_backend_event(event) is None for event in events)
179-```
180-
181:- [ ] **Step 2: 跑重播器 instance 確認 module 缺失**
182-
183:Run: `uv run pytest -q nova/介接/執行者後端/重播器/test_契約.py`
184-
185-Expected: 【推論】FAIL with import/schema error。
186-
187-- [ ] **Step 3: 寫 immutable request、closed event union 與純函式 replay stream**
188-
189-```python
190-class ExecutorBackend(Protocol):
191-    manifest: BackendManifest
--
194-
195-async def replay(script: ReplayScript) -> AsyncIterator[BackendEvent]:
196-    for event in script.events:
197-        yield event
198-```
199-
200-- [ ] **Step 4: 跑共用 contract suite**
201-
202:Run: `uv run pytest -q nova/介接/執行者後端/重播器/test_契約.py -n 2`
203-
204-Expected: 【推論】PASS，重複相同 script 產生相同 canonical event bytes。
205-
206-- [ ] **Step 5: 跑未知 event named negative**
207-
208:Run: `uv run python 工具/跑驗收.py --claim execution.backend.replayer-contract-parity`
209-
210-Expected: 【推論】negative direct red，failed predicate 恰為 `backend_event.closed_union`。
211-
212-- [ ] **Step 6: Commit**
213-
214-```bash
215:git add 規格/執行/ExecutionRequest.schema.json 規格/執行/BackendEvent.schema.json 規格/執行/保證/重播器同契約.claim.json nova/領域/執行/端口.py nova/介接/執行者後端
216:git commit -m "feat: 加入執行者後端契約與重播器"
217-```
218-
219----
220-
221-### Task 3: 由父程序強制 wall deadline 與 process-tree kill
222-
223-**Files:**
224-- Create: `nova/基礎設施/系統/單調時鐘.py`
--
441-```
442-
443----
444-
445-### Task 7: 證明重播、重送與 crash recovery 確定性
446-
447-**Files:**
448-- Modify: `nova/應用/執行封套.py`
449:- Modify: `nova/介接/執行者後端/重播器/執行.py`
450-- Create: `驗收/執行封套/測_重播契約.py`
451-- Create: `驗收/執行封套/測_crash_recovery.py`
452-
453-**Interfaces:**
454-- Produces: `resume_execution(execution_id) -> AlreadyTerminal | ResumedExecution`。
455-- Persists: input/event/script digest and terminal event idempotency key。
456-
457-**ClaimSpec:** 【推論】`execution.recovery.single-terminal-after-crash` 從紅轉綠。
--
485-
486-Run: `uv run pytest -q 驗收/執行封套/測_重播契約.py 驗收/執行封套/測_crash_recovery.py -n 2 && uv run python 工具/跑驗收.py --claim execution.recovery.single-terminal-after-crash`
487-
488-Expected: 【推論】PASS；每個 execution 恰一 terminal，兩次 replay canonical evidence digest 相同。
489-
490-- [ ] **Step 5: Commit**
491-
492-```bash
493:git add nova/應用/執行封套.py nova/介接/執行者後端/重播器/執行.py 驗收/執行封套
494-git commit -m "feat: 冪等地恢復執行"
495-```
496-
497----
498-
499-### Task 8: 消費能力契約並攔截工具、輸出、代理與效果路徑
500-
501-**Files:**
502-- Modify: `規格/執行/ExecutionRequest.schema.json`
503-- Modify: `規格/執行/BackendEvent.schema.json`
504-- Modify: `nova/領域/執行/端口.py`
505-- Modify: `nova/領域/執行/模型.py`
506-- Modify: `nova/介接/執行者後端/共用/manifest.py`

codex
## 裁決

### R3-01(fable) — REJECT `NOT_TESTABLE`

一句話：`result_semantics` 目前仍是原語自行宣告的 enum；五項 exact 條件只有散文，執法器只能識別特製的 sample-mean fixture，不能阻止另一個 estimator 自稱 `EXACT_ARTIFACT_FUNCTION`。

一條決議內含兩個有序 task 符合我的原意。問題不在是否拆成兩條決議，而在 provider 與 consumer 之間的契約仍然沒有牙。

可重提的最小修改：

- Task 15 的 exact 准入不能只收 `result_semantics`。
- 增加 `result_semantics_evidence`，至少綁：

  - pinned input-domain manifest digest
  - primitive implementation digest
  - coverage/completeness evidence ref
  - missing-input observation
  - exactness 固定負控清單

- 每個宣稱 exact 的原語，至少要有指定 mutation：

  - 漏掉一個輸入成員
  - 只跑子樣本
  - 遇到 missing value 後靜默略過

  三者必須讓該原語自己的 admission claim 轉紅。
- 若不打算機械證明五項條件，就把名稱降成 `EXACTNESS_EXTERNALLY_ATTESTED`，並誠實承認它是受信任 attestation，不是由 catalog 自動證明的 exact。

不能用「已准入 catalog」掩蓋這個洞：准入只能證明檔案經過某流程，不能憑空證明未被測到的 completeness。

---

### R3-02(fable) — APPROVE

一句話：改成「凍結全序下的實際最佳候選」消除了不存在的 union candidate，`NO_OBSERVED_PROGRESS` 也把 PASS/FAIL 粗粒度造成的觀測限制寫進了終態語意。

寫入時必須補清楚三個細節：

- 每個 candidate 的 verdict vector 必須完整覆蓋 `clause_priority`；缺 clause 必須 typed reject，不能當作 `FAIL` 或忽略。
- `clause_priority` 必須與該 criterion revision 的 clause id 集合完全相等，不能重複、缺漏或混入額外 id。
- `best_so_far` 的 candidate ref、vector digest 與比較結果必須進持久事件，重建不得重新執行 evaluator。

`CLAUSE_COVERAGE_JOIN` 的確有兩種錯：它既可能把實際改善漏掉，也可能拼出不存在的「最佳候選」。本版已修掉後者，並用 `OBSERVED` 誠實限縮前者，因此可接受。

我接受 fable 對 `EXACT_REPEAT` 的反駁：它可以是診斷訊號，但不能冒充完整的停滯判準；對隨機後端，它幾乎不會觸發。

---

### R3-03(fable) — REJECT `NOT_TESTABLE`

一句話：`execution.backend.replayer-contract-parity` 的既有固定負控只殺未知 event kind；它沒有指定一個「相同 script 第二次產生不同 canonical bytes」的 mutant，因此單靠該 claim ref 鑄造機械決定性仍可能假綠。

計畫 05 Task 2 雖在正控步驟寫了「重複相同 script 產生相同 canonical event bytes」，但它的固定負控紅在 `backend_event.closed_union`，不是 determinism。這不足以支撐新的強能力名稱。

可重提的最小修改：

- 在 plan 05 建立獨立 claim，例如  
  `execution.backend.replayer-output-deterministic`。
- 固定負控必須是：同一 `ReplayScript` 第二次重播時改變順序、bytes、時間正規化結果或 terminal bytes。
- `must_fail_exactly` 指向例如：

  - `same_script_same_canonical_event_bytes`
  - `replay_order_stable`
  - `replay_ignores_ambient_time`

- `PURE_REPLAYER` evidence 必須引用該 claim 的 exact revision、digest 與已准入 predicate，不得只引用 `claim_id` 字串。
- `SEEDED_OUTPUT_DETERMINISM` 建議改成中立的 `OUTPUT_DETERMINISM`。重播器沒有靠 seed 產生結果；把純重播器塞進 seeded 語意會混淆「生成決定性」與「既錄 bytes 的重播決定性」。

其餘切分——observed repeatability、contractual claim、mechanical determinism 三者分開——是對的。

---

### R3-04(fable) — REJECT `WEAKENS_GUARANTEE`

一句話：帶 TTL 的 repo-settings 錄播只能證明「某時曾觀測到設定正確」，不能證明這一次 admission 仍由候選不可寫的 workflow 執行；把前者當後者會讓信任根保證在 TTL 內靜默失效。

錄播可以驗證 parser、schema 與決策程式，但不能充當外部狀態的當下證明。repo settings 在 probe 後一秒就可能改變，TTL 不會阻止它。

可重提的最小修改：

- 每次新增 admission 都必須取得一次 live、single-use `AdmissionAuthorizationReceipt`。
- receipt 至少綁：

  - repository identity
  - exact PR/head SHA
  - proposed manifest digest
  - trust-root revision/digest
  - ruleset identity及其版本或不可變摘要
  - required workflow repo/ref/digest
  - workflow run id
  - attested actor
  - issued_at
  - one-time nonce

- receipt 只能消費一次；不得用泛用 TTL probe 授權多筆 admission。
- replay record 只可證明「相同外部回應會導出相同 verdict」，能力名稱必須是 observation/replay，不得成為 live authorization。
- 無法 live 查證時，新 admission 維持 `ADMISSION_TRUST_ROOT_UNAVAILABLE`。
- trust root 的初始 public key／外部 workflow identity 必須位於候選 PR 不可改的信任域；repo 內的 `准入信任根.admitted.json` 只能是該外部事實的鏡像，不能自行成為自己的信任根。

需要控制端執行的創世儀式可以進計畫，但必須明標為 `Authority Step`：

- 它不是實作者的 commit 步。
- 實作者可以完成拒絕路徑與 replay 測試。
- 在控制端產生並驗證真實創世證據前，Task 17 不得宣告完成，後續 admission 必須 fail-closed。

---

### R3-05(fable) — APPROVE

一句話：CAS → `ReserveDisclosure` → state-owner commit → release 已經把揭露帳接回宣告式 machine 與唯一狀態擁有者，修掉了直接 append 和 crash 洗額度兩個根本錯誤。

寫入時必須固定以下細節：

- `ordinal` 必須由 aggregate 根據已提交的唯一 disclosure 數量產生，呼叫端不得提交或指定 ordinal。
- `ReserveDisclosure` 的冪等鍵必須是 lineage 內唯一的 `disclosure_id`：

  - 同 id、同 packet digest：回傳既有 reservation，不重扣。
  - 同 id、不同 digest：typed reject。
  - 新 id、額度已滿：拒絕且不得 release。

- `sealed_pool_lineage_id` 必須是首建時鑄造、後代繼承的穩定 lineage identity，不得是會隨 revision 內容變化的當前集合 digest。
- reserve 失敗或 commit 前 crash 留下的 CAS blob 是不可達 orphan；必須明講可由 GC 回收，且候選不能僅憑猜測 content ref 取得 sealed bytes。
- `DisclosureExhausted` 不得在每次超額重試時無限追加；同一 command/id 必須冪等，或 exhaustion 成為 aggregate 的既有狀態投影。

## 本輪票面

| 決議 | 裁決 |
|---|---|
| R3-01 | REJECT `NOT_TESTABLE` |
| R3-02 | APPROVE |
| R3-03 | REJECT `NOT_TESTABLE` |
| R3-04 | REJECT `WEAKENS_GUARANTEE` |
| R3-05 | APPROVE |

本輪我不另提 R3-06。先把 R3-01 的 exact 證據、R3-03 的 determinism 負控，以及 R3-04 的單次 live admission receipt 補實，再開新題，避免讓未收斂項目互相遮蔽。
tokens used
119,730
## 裁決

### R3-01(fable) — REJECT `NOT_TESTABLE`

一句話：`result_semantics` 目前仍是原語自行宣告的 enum；五項 exact 條件只有散文，執法器只能識別特製的 sample-mean fixture，不能阻止另一個 estimator 自稱 `EXACT_ARTIFACT_FUNCTION`。

一條決議內含兩個有序 task 符合我的原意。問題不在是否拆成兩條決議，而在 provider 與 consumer 之間的契約仍然沒有牙。

可重提的最小修改：

- Task 15 的 exact 准入不能只收 `result_semantics`。
- 增加 `result_semantics_evidence`，至少綁：

  - pinned input-domain manifest digest
  - primitive implementation digest
  - coverage/completeness evidence ref
  - missing-input observation
  - exactness 固定負控清單

- 每個宣稱 exact 的原語，至少要有指定 mutation：

  - 漏掉一個輸入成員
  - 只跑子樣本
  - 遇到 missing value 後靜默略過

  三者必須讓該原語自己的 admission claim 轉紅。
- 若不打算機械證明五項條件，就把名稱降成 `EXACTNESS_EXTERNALLY_ATTESTED`，並誠實承認它是受信任 attestation，不是由 catalog 自動證明的 exact。

不能用「已准入 catalog」掩蓋這個洞：准入只能證明檔案經過某流程，不能憑空證明未被測到的 completeness。

---

### R3-02(fable) — APPROVE

一句話：改成「凍結全序下的實際最佳候選」消除了不存在的 union candidate，`NO_OBSERVED_PROGRESS` 也把 PASS/FAIL 粗粒度造成的觀測限制寫進了終態語意。

寫入時必須補清楚三個細節：

- 每個 candidate 的 verdict vector 必須完整覆蓋 `clause_priority`；缺 clause 必須 typed reject，不能當作 `FAIL` 或忽略。
- `clause_priority` 必須與該 criterion revision 的 clause id 集合完全相等，不能重複、缺漏或混入額外 id。
- `best_so_far` 的 candidate ref、vector digest 與比較結果必須進持久事件，重建不得重新執行 evaluator。

`CLAUSE_COVERAGE_JOIN` 的確有兩種錯：它既可能把實際改善漏掉，也可能拼出不存在的「最佳候選」。本版已修掉後者，並用 `OBSERVED` 誠實限縮前者，因此可接受。

我接受 fable 對 `EXACT_REPEAT` 的反駁：它可以是診斷訊號，但不能冒充完整的停滯判準；對隨機後端，它幾乎不會觸發。

---

### R3-03(fable) — REJECT `NOT_TESTABLE`

一句話：`execution.backend.replayer-contract-parity` 的既有固定負控只殺未知 event kind；它沒有指定一個「相同 script 第二次產生不同 canonical bytes」的 mutant，因此單靠該 claim ref 鑄造機械決定性仍可能假綠。

計畫 05 Task 2 雖在正控步驟寫了「重複相同 script 產生相同 canonical event bytes」，但它的固定負控紅在 `backend_event.closed_union`，不是 determinism。這不足以支撐新的強能力名稱。

可重提的最小修改：

- 在 plan 05 建立獨立 claim，例如  
  `execution.backend.replayer-output-deterministic`。
- 固定負控必須是：同一 `ReplayScript` 第二次重播時改變順序、bytes、時間正規化結果或 terminal bytes。
- `must_fail_exactly` 指向例如：

  - `same_script_same_canonical_event_bytes`
  - `replay_order_stable`
  - `replay_ignores_ambient_time`

- `PURE_REPLAYER` evidence 必須引用該 claim 的 exact revision、digest 與已准入 predicate，不得只引用 `claim_id` 字串。
- `SEEDED_OUTPUT_DETERMINISM` 建議改成中立的 `OUTPUT_DETERMINISM`。重播器沒有靠 seed 產生結果；把純重播器塞進 seeded 語意會混淆「生成決定性」與「既錄 bytes 的重播決定性」。

其餘切分——observed repeatability、contractual claim、mechanical determinism 三者分開——是對的。

---

### R3-04(fable) — REJECT `WEAKENS_GUARANTEE`

一句話：帶 TTL 的 repo-settings 錄播只能證明「某時曾觀測到設定正確」，不能證明這一次 admission 仍由候選不可寫的 workflow 執行；把前者當後者會讓信任根保證在 TTL 內靜默失效。

錄播可以驗證 parser、schema 與決策程式，但不能充當外部狀態的當下證明。repo settings 在 probe 後一秒就可能改變，TTL 不會阻止它。

可重提的最小修改：

- 每次新增 admission 都必須取得一次 live、single-use `AdmissionAuthorizationReceipt`。
- receipt 至少綁：

  - repository identity
  - exact PR/head SHA
  - proposed manifest digest
  - trust-root revision/digest
  - ruleset identity及其版本或不可變摘要
  - required workflow repo/ref/digest
  - workflow run id
  - attested actor
  - issued_at
  - one-time nonce

- receipt 只能消費一次；不得用泛用 TTL probe 授權多筆 admission。
- replay record 只可證明「相同外部回應會導出相同 verdict」，能力名稱必須是 observation/replay，不得成為 live authorization。
- 無法 live 查證時，新 admission 維持 `ADMISSION_TRUST_ROOT_UNAVAILABLE`。
- trust root 的初始 public key／外部 workflow identity 必須位於候選 PR 不可改的信任域；repo 內的 `准入信任根.admitted.json` 只能是該外部事實的鏡像，不能自行成為自己的信任根。

需要控制端執行的創世儀式可以進計畫，但必須明標為 `Authority Step`：

- 它不是實作者的 commit 步。
- 實作者可以完成拒絕路徑與 replay 測試。
- 在控制端產生並驗證真實創世證據前，Task 17 不得宣告完成，後續 admission 必須 fail-closed。

---

### R3-05(fable) — APPROVE

一句話：CAS → `ReserveDisclosure` → state-owner commit → release 已經把揭露帳接回宣告式 machine 與唯一狀態擁有者，修掉了直接 append 和 crash 洗額度兩個根本錯誤。

寫入時必須固定以下細節：

- `ordinal` 必須由 aggregate 根據已提交的唯一 disclosure 數量產生，呼叫端不得提交或指定 ordinal。
- `ReserveDisclosure` 的冪等鍵必須是 lineage 內唯一的 `disclosure_id`：

  - 同 id、同 packet digest：回傳既有 reservation，不重扣。
  - 同 id、不同 digest：typed reject。
  - 新 id、額度已滿：拒絕且不得 release。

- `sealed_pool_lineage_id` 必須是首建時鑄造、後代繼承的穩定 lineage identity，不得是會隨 revision 內容變化的當前集合 digest。
- reserve 失敗或 commit 前 crash 留下的 CAS blob 是不可達 orphan；必須明講可由 GC 回收，且候選不能僅憑猜測 content ref 取得 sealed bytes。
- `DisclosureExhausted` 不得在每次超額重試時無限追加；同一 command/id 必須冪等，或 exhaustion 成為 aggregate 的既有狀態投影。

## 本輪票面

| 決議 | 裁決 |
|---|---|
| R3-01 | REJECT `NOT_TESTABLE` |
| R3-02 | APPROVE |
| R3-03 | REJECT `NOT_TESTABLE` |
| R3-04 | REJECT `WEAKENS_GUARANTEE` |
| R3-05 | APPROVE |

本輪我不另提 R3-06。先把 R3-01 的 exact 證據、R3-03 的 determinism 負控，以及 R3-04 的單次 live admission receipt 補實，再開新題，避免讓未收斂項目互相遮蔽。
