# fable 第十三輪：計畫 16／17／18／01B／06B 覆蓋審（R13-01～R13-04）

範圍照指示：16／17 並排審、01B 問「名字沒有機制」、06B 首次有人審、18 單審。
**總計**：28 個 task 審完，**23 過、5 不過** → 四條決議（全是負控補格，零新 task）。
**18 七格全過零決議**（第五份滿分）。

**Mock-apply（基線 main `641c4a3`）**：

```
基線：計畫 22 份 · Create 779 · task 193 · 未遷移 130
草稿：計畫 22 份 · Create 781（+2，06B 兩個 fixture）· task 193 不變 · 130 不變 · I1–I11 全綠 · EXIT=0
```

複驗：`uv run python /private/tmp/fable-R13-mock/docs/計畫複驗.py /private/tmp/fable-R13-mock/docs/計畫`
**四份 diff**（你 scratchpad＋mock 目錄各一份，互相獨立、全為既有 hunk 無新檔
——上輪的路徑前綴教訓這輪沒有觸發面）：`fable-R13-計畫16.diff`（24 行）／
`計畫17.diff`（13 行）／`計畫01B.diff`（25 行）／`計畫06B.diff`（46 行）。
**請重跑，不要信我貼的輸出——我也是執行者。**
**DOI**：零新引。**誠實帳**：無新實驗。

---

## 16／17 並排比對表（沿用 14／15 方法）

| 面向 | 16 通用 CLI | 17 本地模型 | 判定 |
|---|---|---|---|
| spec／manifest fingerprint | ✓ T1/T2（executable digest＋argv literal） | ✓ T1（六個 semantic artifacts 逐一） | 對稱 |
| 協定封閉 | ✓ T3（JSONL／FINAL 雙模式同套件） | ✓ T2 | 對稱 |
| **cancel／process-tree** | **✗ 零 adapter 級負控** | ✓ T3（noncooperative 拒入＋ignore-TERM/fork） | **不對稱** → R13-01 |
| 額度誠實 | ✓ T4 四模式真值表 | ✓ T4 NOT_APPLICABLE＋零帳入帳 | 對稱 |
| context | ✓ T5 consumer-only | ✓ T5 exact meter | 對稱 |
| **sealed 投影** | **✗ 只有 registry 面、無 bytes 面（canary）** | （17 無 sealed 面需求——engine 只收 envelope，manifest 無 registry 觸角，T6 收窄 constructor 覆蓋） | **不對稱** → R13-01 |
| update | ✓ T6 exact-target | ✓ 明文不在 v1＋overclaim 負控 | 對稱（形不同） |
| **runtime 不可用時的行為** | （16 無固定 endpoint 需求） | **✗「禁止轉用任何雲端 provider」明文零殺手** | **17 獨有缺口** → R13-02 |
| named faulty matrix | ✓ T7 五個 | T6 named overclaims（形不同，牙在） | 對稱 |

## 計畫 16 判定（7 格：5 過、2 不過）

T1／T2／T4／T6／T7 過（各理由在並排表）；**T3 不過**（cancel 零 adapter 級負控
——通用 runtime 走 ProcessSupervisor 不豁免 adapter 自證，14/15/17 都有）；
**T5 不過**（sealed canary bytes 面缺——14 的 測_投影／15 的 Task 8 都有）。

### R13-01(fable) 16 對稱補齊
T3 負控補 `ignore-term-grandchild`（fixture_agent 增 hang／fork 模式；deadline 後
父孫皆亡、終態 TIMED_OUT）；T5 負控補 `sealed-canary-in-invocation` →
[`invocation_contains_no_sealed_bytes`]（雙池 fixture 沿用 06 builders）。
零新檔，掛既有 claims。

## 計畫 17 判定（6 格：5 過、1 不過）

T1／T2／T4／T5／T6 過（fingerprint 六 artifact 逐一、零帳入帳、exact meter、
overclaim 四格都強）；**T3 不過**：Global Constraints【實測】段明文
「連線失敗只回 `LOCAL_RUNTIME_UNAVAILABLE`，**禁止轉用任何雲端 provider**」——
**fail-closed 宣告有、殺手無**（形狀①）。

### R13-02(fable) 17 禁轉雲端的殺手
T3 負控補 `runtime-down-no-fallback`：loopback endpoint 連不上必回
`LOCAL_RUNTIME_UNAVAILABLE`；改連任何非 loopback／雲端 endpoint 的變體紅在
[`no_cloud_fallback`]。零新檔。

## 計畫 18 判定（**7 格全過零決議**）

| Task | 一句理由 |
|---|---|
| T1 工具鏈鎖定 | 四負控含 NFC/NFD 與 lock integrity |
| T2 pure reducer | fetch/Date.now/random／gap 查詢／duplicate 雙計／out-of-order 全有殺手 |
| T3 GraphBundle 高亮 | tamper／unknown node／同節點雙 token |
| T4 健康＋額度誠實 | rolled≠full／fraction≠token／∞禁止／heartbeat 不清 STALE |
| T5 constraint 可見 | 四誤導變體各紅；「送達≠保證」明文 |
| T6 低頻控制 | 直連 route／樂觀改 state／自鑄 nonce 全紅 |
| T7 組裝 | startup 順序／未譯 id 原樣顯示／非色彩狀態 |

## 計畫 01B 判定（5 格：4 過、1 不過）——opus 問的「名字沒有機制」

逐成員查：`PRE_TOOL_DECISION`／`NATIVE_STRUCTURED_OUTPUT`／`DELEGATION` → T2 四
faulty subjects 各有殺手✓；usage 三 scope → relabel 負控＋07 T9 拒 settle 鏈✓；
seeded 家族 → `OUTPUT_DETERMINISM` 五格（R4-02）✓、`REPEATABILITY_OBSERVED`
evidence 形狀✓、`CONTRACTUAL_…CLAIMED` 不得綁機械✓——
**唯一漏網：`SEEDED_REQUEST`**。它零 evidence 形狀、零負控，而 repeatability
觀測整個建立在「seed 真的有送到」之上——宣告了它、把 seed 丟掉，N 次 probe
照樣跑、照樣「觀測到重複」（模型恰好穩定時），能力帳面全綠。

### R13-03(fable) SEEDED_REQUEST 的機制
01B T2 faulty subjects 四→五：`seed-dropped`（宣告 SEEDED_REQUEST 但把 request
的 seed 丟棄）→ [`seeded_request_delivers_seed`]。零新檔。

## 計畫 06B 判定（3 格：2 過、1 不過）——首次有人審

T1 過（凍結＋post-hoc margin＋missing-pair 殺手真）；T3 過（rerun≠replay 兩負控真）；
**T2 不過**：兩條 claim 對**兩個端點**的牙是真的（ineffective／saves-but-degrades
各紅一條互不覆蓋——設計正確），但 spec 明文宣告**四個門檻，兩個零殺手**：
- `max_interval_width`（精度門檻）——分析器忽略它、從過寬區間發 ACCEPTED，不紅。
  spec 自己說「省 0–90% 不是答案」，但沒有東西驗這句。
- `minimum_absolute_quality`（絕對下限）——spec 自己舉例「baseline 0.20 對 0.20
  非劣但沒有使用價值」，同樣沒有殺手。

### R13-04(fable) 06B 兩個門檻的殺手
T2 負控四→六：`wide-interval-not-inconclusive` → [`interval_width_within_max`]、
`low-absolute-quality-accepted` → [`absolute_quality_floor_enforced`]；
Files 補兩個 fixture（`區間過寬成對樣本.json`／`絕對品質過低成對樣本.json`，
7→9 檔）。**自我揭露**：06B 的骨架是我在 R1-08／R2-06 提的——這兩個門檻是我
自己當初寫進 spec 卻沒配殺手的，覆蓋審抓到提案者自己。

---

## 刻意沒做的

1. **18 零決議**——七格逐條在表。
2. 16 的 usage scope 不立案——05 T8（relabel 負控）＋07 T9（`USAGE_SCOPE_INCOMPLETE`
   拒 settle）既有鏈條覆蓋，16 的 spec 語言已含 capability claims 欄。
3. 17 無 named-matrix task 不立案——T6 named overclaims 形不同牙在。
4. 06B 的 `USAGE_SCOPE_INCOMPLETE` 依賴（05 tree-inclusive evidence）——依賴宣告
   誠實明文已在，不立案。

## 給 claude 的順手訊息

- 套用規則：四份 diff 各自獨立、全為既有檔 hunk（無新檔，上輪路徑前綴教訓
  這輪無觸發面）。
- mock 目錄：R13 留著；R12 的可刪。
- 進度帳：**已審 02–18＋01B＋06B 共十九份；只剩 01、19、20 三份**——下輪收官。
- 並排法第二次收成：16／17 的兩個不對稱同樣是「單看全過、並排才現形」；
  01B 的 SEEDED_REQUEST 則是「逐成員問機制」抓到的——兩種問法互補，
  01（最大、被改最多次）下輪建議兩種都上。
