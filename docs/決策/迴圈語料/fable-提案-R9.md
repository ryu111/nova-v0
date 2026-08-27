# fable 第九輪：R9-00＋計畫 02／03／04 覆蓋審（R9-01～R9-10）

覆蓋驅動第一輪，範圍照新指示：R9-00（R8-01 選項 B）＋逐 task 審 02、03、04。
方法：逐 task 讀全文，對每格問兩條定案判準（①固定負控殺得到宣稱的性質嗎；
②有沒有不存在的指涉物），輔以跨計畫 grep（指令附各條）。通過格照列——
「沒提到」不等於「看過了」。

**總計**：24 個 task 審完，**13 過（4 帶觀察）、11 不過** → 十條決議（R9-01～10）
＋一條欠帳（R9-00）。

**Mock-apply（基線 main `85c1d9f`；02/03/04/08 與計畫複驗.py 在 #15 未變，已比對）**：

```
基線：計畫 22 份 · Create 763 · task 189 · 未遷移 131
草稿：計畫 22 份 · Create 769（+6，全屬 R9-00）· task 190（+1）· 131 不動 · I1–I11 全綠 · EXIT=0
```

複驗：`uv run python /private/tmp/fable-R9-mock/docs/計畫複驗.py /private/tmp/fable-R9-mock/docs/計畫`
**四份 per-檔 diff**（你 scratchpad 與 mock 目錄各一份，互相獨立可套用）：
`fable-R9-00.diff`（08，191 行）／`fable-R9-計畫02.diff`（89 行，R9-01～05）／
`fable-R9-計畫03.diff`（68 行，R9-06～08 的 03 部分）／`fable-R9-計畫04.diff`
（31 行，R9-08 的 04 部分＋R9-09～10）。檔內各決議 hunk 不相交，部分核准砍區即可。
**請重跑，不要信我貼的輸出——我也是執行者。**
**又被 I8 咬一次**（`test_…同digest` 黏漢字，改「同摘要」後綠）——第二次，閘在工作。
**DOI**：零新引。**誠實帳**：無新實驗；SQLite composite FK 的 NULL 行為（R9-07）
是我的知識宣稱，sol 複核時請對 SQLite 官方文件驗證。

---

## 計畫 02 逐 task 判定表

| Task | 宣稱 | ①負控殺得到？ | ②指涉物在？ | 判定 |
|---|---|---|---|---|
| T1 載入封閉 model | closed＋canonical digest | 半：unknown-field 殺 closed；**canonical digest 零負控** | 否：「FlowSpec 發明 state」在 load 層無 catalog 可對（T6 既有同格） | 不過 → R9-03 |
| T2 Guard proof cells | closed AST＋partition | 半：partition 側強；**closed AST 只殺 CALL**，字彙擴張與五個上限零負控 | 否：Step 5 的 Hypothesis partition 測試**無任何 Files 條目建它** | 不過 → R9-04 |
| T3 structural lints | closed-reachable-terminal | 半：五 fixture 各殺一條；**`cardinality`／`claim-ref` 零負控** | 否：`claim-ref` 全計畫無定義無消費端 | 不過 → R9-05 |
| T4 declared-edge-only | 只走宣告轉移 | 是：三負控＋指定突變直殺 | 是（歧義 fixture 手造合法） | **過** |
| T5 DecisionTable＋budget | escape budget | 是：三負控＋`//5→//4` 突變直殺 | 是 | **過**（觀察：table 封閉性靠 rows 重用 guard AST，T2 claim 覆蓋，不立案） |
| T6 FlowSpec 綁定 | 只綁既有 output→trigger | 是：四格 typed | **否：`machines.require_output` 的 output 在 MachineSpec 欄位清單根本沒宣告** | 不過 → R9-01 |
| T7 圖同源＋migration | 同源＋顯式升版 | 是：三格直殺兩 claim | **否：`LocaleCatalog` 無 schema 無 Create 無來源** | 不過 → R9-02 |

另（不立案）：02 宣告 9 個 claim id 只 Create 4 份檔——屬全域 65-id 遷移債（131 帳內）。
T3 Create 的是 T4 的 claim 檔——順序合法（T3<T4），非缺陷。

## 計畫 03 逐 task 判定表

| Task | 宣稱 | ① | ② | 判定 |
|---|---|---|---|---|
| T1 event envelope | causal-and-canonical | 半：canonical 有指定突變（拿 sort_keys）✓；**causal 半邊零負控** | 否：Global Constraints 要求 causation／correlation／reason／schema digest 四欄，**envelope fence 全漏** | 不過 → R9-06 |
| T2 composite FK | FK declared-only | 半：直插＋移除 FK 突變✓；**partial-NULL 直插零負控**——SQLite composite FK 任一欄 NULL 即整條不檢查，是繞過孔 | 是 | 不過 → R9-07 |
| T3 single owner | 單一 writer | 是：雙 owner＋DB path 拒 | 是 | **過**（觀察：stale lockfile 由 T7 重啟矩陣隱含覆蓋） |
| T4 atomic＋idempotent | 原子與冪等 | 是：fault injection＋重送＋33-event＋commit-before-head 突變 | 是 | **過** |
| T5 lease fencing | 單一有效 lease | 是：三負控＋SIGSTOP 實測 | 是 | **過** |
| T6 tail publisher | byte-identical | 是：dup／gap／drift | **否：負控引用的 `recorded_at` 全計畫只出現在負控裡**，tail schema 未宣告 | 不過 → R9-08 |
| T7 SIGKILL matrix | crash recovery | 是：三 subjects＋六 fault points 矩陣 | 半：`--count=20` 需 pytest-repeat，Tech Stack 未列 | 不過（小） → R9-08 |
| T8 DB bypass 檢查 | no-bypass | 是：static／alias／reflective 三組【實測】標記 | 是 | **過** |

## 計畫 04 逐 task 判定表

| Task | 宣稱 | ① | ② | 判定 |
|---|---|---|---|---|
| T1 CAS | addressed-and-verified | 是：flip-byte／size錯／aliasing／corrupt≠missing＋指定突變 | 是 | **過** |
| T2 EvidenceRecord | append-only | 半：UPDATE／不指 old id／懸空 ref✓；**DELETE 零負控** | 是 | 不過 → R9-09 |
| T3 segment→manifest | verified-before-membership | 是：五負控＋省略 read-back 突變 | 是 | **過** |
| T4 checkpoint 等價 | checkpoint＋suffix＝genesis | 是：property＋四負控＋忽略 seq 突變 | 是 | **過** |
| T5 prune 前提 | publish-before-prune | 是：四前提各拿掉一次＋重啟重做 | 半：`--count=10` 同 R9-08 | **過**（R9-08 連帶修） |
| T6 retention＋capacity | 分層＋硬停 | 半：「不早刪」有殺手；**「停收」半邊零負控** | 是 | 不過 → R9-10 |
| T7 cursor 連續 | segment-tail contiguous | 是：漏／重排／改一 event | 是 | **過** |
| T8 backup／restore | rpo5-rto30-inventory | 是：缺 ref／非空 root／cursor 不一致 | 是 | **過**（觀察：5m 排程擁有者＝計畫 20 的 backup-worker——`grep -n 備份 20-*.md` 67 行；claim 用 fixture 驗機制、真備份還原由 20 `--release` 承接，帳面誠實） |
| T9 envelope 量測 | quick-sensitivity | 是：三 subjects；`ENGINE_SELECTION_ACCEPTED=false` 明示、final claim 歸 20 | 是 | **過** |

---

## 決議（狀態全 PROPOSED；02 的五條與 R9-00 內容同前一版提案，此處收斂為摘要）

### R9-00 提示家族＋組裝政策：誠實降級版（R8-01 選項 B）
sol 修法逐條：保留 policy ref 入 identity；刪兩格無第二主體的負控改三格可達
（`assembly_policy_must_resolve`／`digest_content_bound`／`vocabulary_closed`）；
「第二個 kind 准入前不宣稱『不同合法政策必切 Pursuit』已驗過」逐字入 task；
enum 擴充硬前置（同一變更必附首組可達正負控）；canonical bytes 只涵蓋有效語意欄位
（policy 不含 semantic_id／revision，防 sol 抓的反向破壞 R1-01），防恆真格釘住
「僅 id 不同必須同摘要」。7 檔／claim 1／七負控四防恆真。diff：`fable-R9-00.diff`。

### R9-01 MachineSpec 宣告 output（02）
§子系統規格＋T1 Interfaces 補 output（`output_id`＋`payload_digest`，transition 以
`emits` 引用）；T1 負控補 `emits` 引用未宣告 output → red。T6 的 `require_output`
從此有東西可查——`prompt_family_ref` 的同形：比較器有了，被比較的東西沒宣告。

### R9-02 拿掉 LocaleCatalog（02 T7）
`render_dot(GraphIR)`；SVG 屬性刪 `locale-digest`。本地化屬 view 層（計畫 18），
在 02 為指涉物發明主體方向反了。查證：`grep -rn LocaleCatalog docs/計畫/` → 僅 02 T7。

### R9-03 T1 負控修正（02）
移除錯層的「FlowSpec 發明 state」（介面在 T6 的 `compile_flow(flow, machines)`，
T6 既有同格——歸位不是刪保證）；補 `digest-over-raw-bytes` →
[`canonical_digest_key_order_insensitive`]——claim 叫 closed-**and-digested** 而
digested 半邊零負控。

### R9-04 T2 補字彙與上限負控＋測試給個家（02）
Files 補 `Modify: nova/狀態機/test_檢查.py`（Step 5 的 Hypothesis oracle 原本無家
——收集到零個測試＝檢查靜默消失）；負控補 `arith-operator` →
[`guard_vocabulary_closed`]（只殺 CALL 殺不掉字彙擴張）與 `limit-boundary` →
[`GUARD_LIMIT_EXCEEDED`]（五個上限各一個越界 witness）；fence 同步補兩列。

### R9-05 T3 failure id 收斂（02）
`cardinality` 移走（屬 T6 綁定層負控覆蓋）；`claim-ref` 刪除（無定義無負控無消費端
——「宣告了驗收意圖不等於安排了可執行驗收」）。清單封閉為五個各有 fixture 的 id。

### R9-06 envelope 補 causal 欄位與殺手（03 T1）
fence 補 `causation_id`／`correlation_id`／`reason_code`／`schema_digest`
（Global Constraints 已要求、fence 全漏）；負控補 `missing-causal-fields` →
[`envelope_requires_causal_fields`]——claim 名 causal-and-canonical，causal 要有殺手。

### R9-07 全有全無 CHECK（03 T2）
migration 補 CHECK（transition 四欄全 NULL 或全 NOT NULL）；負控補
`partial-null-transition-row`（machine_digest 設值、transition_id NULL 直插必須
IntegrityError）——**SQLite composite FK 任一欄 NULL 即整條不檢查**，沒有 CHECK
這是繞過 FK 的靜默孔。此為我的知識宣稱，請 sol 對 SQLite 官方文件複核。

### R9-08 指涉物補宣告（03＋04）
03 tail schema 註解補 `recorded_at`（原本只活在負控裡）；03／04 Tech Stack 補
pytest-repeat（`--count=20`／`--count=10` 的指涉——插件缺席時 Run 直接
unrecognized argument）。

### R9-09 append-only 補 DELETE 殺手（04 T2）
負控補 `delete-old-row` → [`evidence_rows_undeletable`]（DB 層 trigger 擋）——
append-only 只殺 UPDATE 殺不掉 DELETE。

### R9-10 硬停「停收」半邊補殺手（04 T6）
負控補 `admission-past-hard-point` → [`hard_point_stops_admission`]——
「不早刪」與「停收」是兩個半邊，原本只有前者有殺手。

---

## 刻意沒做的（照實列）

1. 02 T5／03 T3／04 T5／04 T8／04 T9 的觀察不立案——理由各在表內。
2. 9-claim-id／4-claim-檔（02）與同型缺檔（03 有 7 id／3 檔、04 有 9 id／7 檔）
   ——全域遷移債，131 帳內，不重複立案。
3. 04 T8 的 RPO 排程原擬立案，查證後撤回——擁有者在計畫 20（backup-worker，
   five-minute），不硬找。

## 給 claude 的順手訊息

- 套用規則：四份 diff 各自獨立；檔內部分核准砍該決議的 hunk 區（各條「改什麼」
  即區界），要重切十分鐘內交。
- mock 目錄：R9 留著；R8 三個可刪。
- 覆蓋審檢查清單（下一批 05／06／07 沿用）：負控殺的是宣稱的性質還是隔壁的性質；
  介面枚舉的每個成員有沒有殺手；負控引用的每個名詞有沒有宣告主體；Run 指令的
  旗標與檔案是否可達；fence 欄位與 Global Constraints 是否一致。
