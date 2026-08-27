# fable 第十二輪：計畫 12／13／14／15 覆蓋審（R12-00～R12-03）

範圍照指示：十一條清單逐 task 審 12、13、14、15，並對 14／15 做**交叉比對**
（一邊有殺手另一邊沒有的不對稱）。外加 sol 上輪留給我裁量的執法器長期牙齒——
本輪提為 R12-00。

**總計**：36 個 task 審完，**33 過、3 不過**。兩份滿分：**13 全過十格、
交叉比對前的 15 單看也幾乎全過**——不對稱缺口正是單看看不到、比對才現形的那種。

**Mock-apply（基線 main `3c4c1c2`）**：

```
基線：計畫 22 份 · Create 775 · task 192 · 未遷移 131
草稿：計畫 22 份 · Create 779（+4）· task 193（+1，15 Task 8）· 未遷移 130（−1，12 T9 遷移）· I1–I11 全綠 · EXIT=0
```

**自測模式真跑**：`uv run python /private/tmp/fable-R12-mock/docs/計畫複驗.py --自測`
→ `自測 ✓ 撞號：非零且含「I6 task 標題序號與位置不符」`、EXIT=0。
草稿複驗：`uv run python /private/tmp/fable-R12-mock/docs/計畫複驗.py /private/tmp/fable-R12-mock/docs/計畫`
**請重跑兩條，不要信我貼的輸出——我也是執行者。**

**四份 diff**（你 scratchpad＋mock 目錄各一份，互相獨立）：
`fable-R12-計畫12.diff`（34 行，R12-01）／`計畫14.diff`（12 行，R12-03）／
`計畫15.diff`（114 行，R12-02）／`複驗器.diff`（83 行，R12-00＋R12-01 的基線 hunk
＋兩個自測 fixture 新檔）。**基線帳**：R12-01 過 → 130；退 → 131（複驗器 diff 的
基線 hunk 單獨砍掉即可）。
**DOI**：零新引。**誠實帳**：無新實驗（自測是真跑）；15 的 Codex 能力判斷
（無 pre-tool callback、`--ask-for-approval never` 是關核准不是給 callback）沿用
計畫 15 自己引的官方 command reference，我沒有另行 probe 真 binary。

---

### R12-00(fable) 執法器自測：撞號 fixture 有長期的家

sol 上輪原話：「真實撞號 fixture 不能只活在暫存目錄——否則『套用後現況已修好』
會讓這項檢查只剩程式碼、沒有長期牙齒。」本條落地：
- Create `docs/計畫複驗自測/撞號/{01-範例.md, 預期.txt}`——最小撞號計畫
  （兩個 Task 1）＋預期訊息字串。
- `計畫複驗.py` 增 `--自測` 模式：對每個情境目錄以 subprocess 跑自己，
  斷言 **exit 非零且輸出含預期字串**。誠實邊界寫進 docstring：fixture 只保證
  目標訊息出現，其他不變式在最小 fixture 上本來就會紅（如 I10 基線），不計。
- 情境目錄是開放結構——未來每個「值得長期牙齒」的執法器負控都能加一個目錄，
  不用再改程式。
- **接入自動執行點屬控制端裁定**（本 repo 的閘清單所在處我無權指定）；
  本條先給牙齒與指令。
- 治理提醒同上輪：執法器與自測的變更沒有執法器管，你們兩票是唯一的閘。

## 計畫 12 逐 task 判定表

| Task | 宣稱 | ① | ② | 判定 |
|---|---|---|---|---|
| T1 schema＋kernel | explicit-selector | 是：五 invalid instances | 是 | **過** |
| T2 admission 證據閉合 | 兩 claim | 是：四格含 HARNESS_ERROR 不算數 | 是 | **過** |
| T3 owner lifecycles | no-auto-renew | 是：90/180 邊界＋tombstone | 是 | **過** |
| T4 owner gates | 兩 claim | 是：bypass matrix＋native-hook-only | 是 | **過** |
| T5 capability fail-closed | 一 claim | 是 | 是 | **過** |
| T6 advisory 16 條 cap | catalog-bounded | 是：17th＋size 邊界 | 是 | **過** |
| T7 計量與 packing | 兩 claim | 是：低估一 token／截斷／猜值 unsupported | 是 | **過** |
| T8 三處揭露＋compaction | 兩 claim | 是：three-sink equality＋trusted observer | 是 | **過** |
| T9 顯式 rebase | explicit-rebase | 是（一格） | **否：本 task 零 Create**——claim 無檔可住、Step 1 紅測無 Files 條目可寫（「測試無家」同形）；Step 2 跑的 test_工作決策.py 也不在 Files | **不過** → R12-01 |
| T10 approval envelope | 兩 claim | 是：五格 nonce matrix | 是 | **過** |
| T11 重複偵測 | recurrence-bounded | 是：truth table | 是 | **過** |
| T12 歸屬檢查器 | owner-local | 是：四 fixtures | 是 | **過** |

另（不立案，全域遷移債帳內）：12 有數個 task 兩 id 配一 claim 檔或零檔
（T4／T7／T8 各兩 id）——落點行遷移時解。

### R12-01(fable) 12 T9 補家
Create `規格/工作/保證/脈絡快照顯式rebase.claim.json`＋落點行；
Files 補 Modify `test_工作決策.py`／`test_追求決策.py`（紅測的家；
兩檔由 09 T1／08 T1 Create，12 前置閉包內，I5 成立）。基線 131→130。

## 計畫 13 逐 task 判定表（**十格全過零決議**）

| Task | 判定 | 一句理由 |
|---|---|---|
| T1 封閉 wire unions | 過 | 五 invalid fixtures 含 long-running 缺 operation_ref |
| T2 ports-only boundary | 過 | concrete-import／UnitOfWork 洩漏負控 |
| T3 唯一 handler | 過 | 0/2 handlers＋direct-terminal spy |
| T4 冪等＋ACL | 過 | same-key-diff-bytes conflict＋禁欄注入 |
| T5 tail-only／fold-only | 過 | FailingIfCalled spy port 零呼叫斷言 |
| T6 Python facade | 過 | public surface snapshot |
| T7 CLI exit map | 過 | REJECTED=2 映射＋UTF-8/NFD |
| T8 OpenAPI＋SSE | 過 | route closure snapshot＋backpressure |
| T9 三介面 parity | 過 | 同 command 三 adapter 同 result＋inward imports |
| T10 MCP 第四介面 | 過 | legacy disposition 封閉表＋不釘 experimental MCP Tasks |

## 計畫 14／15 交叉比對表（adapter 家族的不對稱）

| 面向 | 14 Claude SDK | 15 Codex CLI | 判定 |
|---|---|---|---|
| manifest fingerprint | ✓ T1 | ✓ T1（含 executable digest） | 對稱 |
| 協定封閉：unknown | ✓ T2 | ✓ T2 | 對稱 |
| 協定封閉：**malformed／dup／line-cap** | **✗ 只殺 unknown** | ✓ T2（malformed.jsonl／dup id／line cap） | **不對稱** → R12-03 |
| cancel／外部限額 | ✓ T3 | ✓ T3 | 對稱 |
| 額度逐 bucket | ✓ T4 | ✓ T4 | 對稱 |
| context 誠實 | ✓ T5 | ✓ T5 | 對稱 |
| ambient config 隔離 | ✓ T7（catalog 入 fingerprint） | ✓ T5（poisoned home） | 對稱（形不同牙都在） |
| **no-criterion 投影** | ✓ T6（claim＋測_投影＋canary） | **✗ 只在 T7 Interfaces 一句話——無檔案、無 claim、無 fixture** | **不對稱** → R12-02 |
| **01B 能力映射** | ✓ T7（工具／輸出／委派成本兩 claim） | **✗ 零對應 task；前置也漏 01B** | **不對稱** → R12-02 |
| update 誠實 | ✓ T5 負控（latest 冒充 pinned） | ✓ T6 專門 claim | 對稱（15 較強，14 已覆蓋面） |
| named faulty matrix | T6 跑完整 matrix | ✓ T7 六個 named subjects | 對稱（形不同） |

### R12-02(fable) 15 對稱補齊
①前置補 **01B**（能力字彙的來源——缺它 manifest 的能力宣告沒有 typed 主詞）；
②新 **Task 8**（5 檔／2 claims）：manifest 對 01B 四類能力**逐項宣告帶機制證據**
——`PRE_TOOL_DECISION`＝unsupported（Codex 無 pre-tool callback；
`--ask-for-approval never` 是關核准不是給 callback）、`NATIVE_STRUCTURED_OUTPUT`
依 probe、`DELEGATION`＝unsupported、usage scope＝`ROOT_ONLY` 不升格；
＋no-criterion 投影（canary 不進 argv/env/stdin/workspace、registry import 禁）。
四格負控＋防恆真（誠實 manifest 通過 05 的 required-capability 協商）。
T7 matrix 的「no-criterion projection」名詞從此有主體。

### R12-03(fable) 14 補 malformed 負控
T2 負控補 `malformed-sdk-payload`（缺必填欄位／非法 enum 的 SDK message 必須
`PROTOCOL_FAULT`，不得當 assistant text）——15 的 `malformed.jsonl` 對稱格。

---

## 刻意沒做的

1. **13 零決議**——十格逐條在表。
2. 14 名 faulty matrix 形不同不立案（T6 已跑完整 matrix）；15 update claim 較強
   不回頭改 14（T5 負控已覆蓋 claim 面）。
3. 12 的 2-id-1-file 群——全域遷移債，不重複立案。
4. R12-00 的自測**接入閘清單**——控制端裁定範圍，本條只給牙齒。

## 給 claude 的順手訊息

- 套用規則：四份 diff 各自獨立；複驗器 diff 含 R12-00（自測）＋R12-01 基線 hunk
  （R12-01 被退就砍基線 hunk）＋兩個 fixture 新檔。
- mock 目錄：R12 留著（含自測 fixture）；R11 的可刪。
- 進度帳：已審 02–15 共十四份；剩 01、01B、06B、16–20 共八份，兩輪內收完。
- 交叉比對在 adapter 家族的實效：兩個不對稱都是「單看一份全過、並排才現形」
  ——16（通用 CLI）與 17（本地模型）下輪照樣並排審。
