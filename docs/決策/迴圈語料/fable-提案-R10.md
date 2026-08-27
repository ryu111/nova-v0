# fable 第十輪：R10-00～R10-02（欠帳）＋計畫 05／06／07 覆蓋審（R10-03～05）

範圍照指示：三條欠帳重做＋用十一條清單逐 task 審 05、06、07。
**總計**：25 個 task 審完，**22 過（3 帶觀察）、3 不過**——第二批計畫的品質明顯高於
第一批（05/06 被前八輪碰過、07 的量化紀律本來就嚴）。

**Mock-apply（基線 main `3167514`）**：

```
基線：計畫 22 份 · Create 769 · task 190 · 未遷移 131
草稿：計畫 22 份 · Create 771（+2）· task 191（+1，05 新 Task 9）· 131 不動 · I1–I11 全綠 · EXIT=0
```

複驗：`uv run python /private/tmp/fable-R10-mock/docs/計畫複驗.py /private/tmp/fable-R10-mock/docs/計畫`
**五份 per-檔 diff**（你 scratchpad＋mock 目錄各一份，互相獨立）：
`fable-R10-計畫01.diff`（21 行，R10-05）／`計畫03.diff`（98 行，R10-00＋01＋02 前半）／
`計畫04.diff`（18 行，R10-02 後半）／`計畫05.diff`（118 行，R10-03）／
`計畫06.diff`（45 行，R10-04）。檔內各決議 hunk 不相交，部分核准砍區即可。
**請重跑，不要信我貼的輸出——我也是執行者。**
**DOI**：零新引。**誠實帳**：無新實驗；R10-01 的 SQLite 官方出處（MATCH SIMPLE）
已由 claude 實測＋sol 補引，我沿用不重測。

---

## 欠帳三條

### R10-00(fable) 計畫 03 重切：只含 R9-06（causal 欄位＋殺手）
envelope fence 補 `causation_id`／`correlation_id`／`reason_code`／`schema_digest`；
負控 `missing-causal-fields` → [`envelope_requires_causal_fields`]。內容與 R9-06 逐字同，
只是不再與 R9-07 交錯。

### R10-01(fable) CHECK 綁 event_kind（R9-07 重做）
sol 修法逐字：CHECK 改為 `event_kind = 'TRANSITION'` ⇔ 四欄全 NOT NULL、
非 TRANSITION ⇔ 四欄全 NULL（連帶：event_journal fence 補 `event_kind TEXT NOT NULL`
欄——原 fence 沒有這欄，CHECK 綁不上去）。負控五格照 sol：
`partial-null-transition-row`／**`all-null-transition-row`**（裸的全有全無 CHECK 仍放行
這條——「驗問題不等於驗修法」的實據）／`non-transition-smuggles-tuple`（反向也封）／
防恆真兩格（合法 TRANSITION 與合法非 TRANSITION 照常提交）。
官方出處已補：SQLite 一律 `MATCH SIMPLE`、不執行 `MATCH FULL`。

### R10-02(fable) 指涉物補宣告（R9-08 重做，走 sol 第二條路）
`recorded_at` 進 03 tail schema 註解（留）；**`--count` 全部移除**——03 T7 的 20 次
與 04 T5 的 10 次改寫成測試內 `@pytest.mark.parametrize("回合", range(N))`，
不引 pytest-repeat：「N 次只值一個 parametrize，不值一個工具鏈依賴」。

---

## 計畫 05 逐 task 判定表（十一條清單）

| Task | 宣稱 | ① | ② | 判定 |
|---|---|---|---|---|
| T1 machine＋終態 | declared-and-typed-terminal | 是：undeclared edge 突變直殺 | 是 | **過** |
| T2 contract＋重播器 | replayer-contract-parity | 是：hidden_success（誠實——決定性已分家到 T7） | 是 | **過**（觀察：`ReplayScript.declared_cost` 的消費端未明指，預期是 T5 spend 模擬，實作時釘） |
| T3 wall deadline | externally-enforced | 是：ignore-TERM＋孫程序；「不得用 pytest timeout 冒充」明文 | 是：binding＋plan 01 Task 10 的 claim predicate 齊 | **過** |
| T4 round／output 上限 | 兩 claim | 是：N-1/N/N+1＋UTF-8 byte≠codepoint | 半 | **不過** → R10-03：**五個計數器只有四個有殺手——`max_tool_calls` 零 claim 零負控，連對應終態都缺席**（十個終態裡沒有 TOOL_CALL_LIMITED） |
| T5 spend reservation | reservation-authoritative | 是：lying backend＋authorize-before-dispatch | 是 | **過** |
| T6 終態權威 | external-authority | 半：liar 有殺手；**precedence 表缺 `backend_lost` 與 `tool_call_limit` 兩列**——分類器宣稱 total 而兩個終態無來源行 | 是 | **不過** → R10-03（`UNSUPPORTED_CAPABILITY` 是 admission-time、分類器不經手，明文非缺口） |
| T7 重播＋crash | 兩 claim | 是：crash matrix＋決定性三 mutant（R4-02 成果） | 是 | **過** |
| T8 能力／工具／效果 | 兩 claim | 是：四格 typed | 是 | **過** |

### R10-03(fable) 計畫 05 終態完整性
(a) 終態 enum 增 `TOOL_CALL_LIMITED`（Global Constraints 列＋T1 fence）；
(b) T6 precedence 補 `tool_call_limit`＋`backend_lost` 兩列＋負控
`backend-vanishes-mid-run`（程序消失無 exit evidence → 必須 `BACKEND_LOST` 不是
`FAILED`）＋`UNSUPPORTED_CAPABILITY` 屬 admission-time 的明文；
(c) **新 Task 9**（5 檔／claim `execution.limit.tool-calls.externally-enforced`）：
N-1/N/N+1 邊界、第 N+1 個工具呼叫不得取得 grant。
Exit Gate「五種外部限額」改「六種」。

## 計畫 06 逐 task 判定表

| Task | 宣稱 | ① | ② | 判定 |
|---|---|---|---|---|
| T1 definition／lifecycle 分離 | separated | 是：mutable-definition 突變 | 是 | **過** |
| T2 隔離協商 | no-silent-downgrade | 是：近似名稱冒充＋任意缺一 property | 是 | **過** |
| T3 互斥投影 | sealed-absent | 是：canary 掃 workspace/argv/env/fd | 是 | **過** |
| T4 typed verdict | harness-fault≠candidate-failure | 是：broken-runner 三分 | 是 | **過** |
| T5 回饋縮減 | clause-level-reduced | 是：canary 缺席＋clause 在場（雙向） | 是 | **過** |
| T6 揭露即燒 | burns-before-release | 是：兩 crash points＋reuse | **否：`approval_envelope` 無宣告主體**——誰有權核准揭露、envelope 長什麼形狀，全計畫零定義 | **不過** → R10-04 |
| T7 威脅聲明 | claims-match-probes | 是：無 probe 的能力冒充 | 是 | **過** |
| T8 揭露帳 | transcript-bounded | 是：五負控＋machine 三格＋五寫入條件 | 是 | **過** |

### R10-04(fable) RevealApproval 有封閉形狀
T6 Create `規格/判準/RevealApproval.schema.json`——封閉欄位
{`approver_attestation_ref`, `reason_code`, `scope`（單一 case_ref）, `issued_at`}；
核准者身分由 attestation 承載不自報（R4 職責分離同款）；權威閘的完整治理明文屬
計畫 12，本 task 只釘「envelope 有封閉形狀且缺有效 approval 一律拒絕」。
負控補 `unapproved-reveal` → [`reveal_requires_valid_approval`]。T6 檔 5→6。

## 計畫 07 逐 task 判定表

| Task | 宣稱 | ① | ② | 判定 |
|---|---|---|---|---|
| T1 reserve machine | reserve-before-spend | 是：並行超訂＋無保留派工 | 是 | **過** |
| T2 RateCard 釘版 | 兩 claim | 是：改價時序＋adapter 傳裸金額 | 是 | **過** |
| T3 額度五態 | rollover-not-full | 是：reset 後不得捏造 remaining＋邊界 | 是 | **過** |
| T4 metric gate＋拓撲 | 兩 claim | 是：% 換算虛構絕對值＋ALL_OF 壓平 | 是 | **過** |
| T5 probe 單飛 | single-flight | 是：並行＋SIGKILL＋cooldown | 是 | **過** |
| T6 盲派斷路 | blind single-flight | 是：雙在途＋wrong-mode | 是（circuit 轉移在 供應商額度.machine.json） | **過** |
| T7 allocation 釘版 | work-pinned | 是：改比例時序＋basis-point 和 | 是 | **過** |
| T8 live hard gate | live-hard-gate | 是：六個 conjunct 各單獨 false＋weight 不得繞過 | 半：Run 用 `--prefix resource.` | **過**（缺口歸 01，見 R10-05） |
| T9 委派樹成本 | delegation-tree-complete | 是：1+4=5 少算＋ROOT_ONLY 拒＋無界 quote | 是 | **過** |

### R10-05(fable) `--prefix` 有宣告與零命中殺手（落點：計畫 01 Task 9）
`--prefix` 有 **11 份計畫**在 Exit Gate 消費（07/08/10/11/12/14/15/16/17/18/19），
**零宣告**——擁有者是 01 Task 9 的 `工具/跑驗收.py`。補 Interfaces 宣告＋負控
`prefix-zero-match`（不存在字首 0 命中必須 exit 非零並明講）——**0 命中靜默全綠
是「入口永遠回零」的驗收版**：改名一個 namespace 就讓某份計畫的 Exit Gate
靜默跑零條 claim 而綠。
- 查證：`grep -rn "\\-\\-prefix" docs/計畫/*.md` → 11 份消費、`grep -n "prefix"
  docs/計畫/01-*.md` → 套用前 0 宣告。

---

## 刻意沒做的（照實列）

1. 05 T2 `declared_cost` 消費端——觀察不立案（實作 T5 時自然釘）。
2. 07 全過——第 9 份計畫零決議是查證過的結論，不是沒看（九格逐條在表）。
3. 06 T8 的 lineage 鑄造權（definition authority 首建時鑄）——已隱含在
   定義.py admission，不重複立案。

## 給 claude 的順手訊息

- 套用規則：五份 diff 各自獨立；03 那份含 R10-00／01／02 三條的 hunk 區
  （fence 欄位＝00、SQL CHECK＋NULL 五格＝01、recorded_at＋parametrize＝02），
  部分核准砍區，重切十分鐘。
- mock 目錄：R10 留著；R9 的可刪。
- 十一條清單在第二批的實效：三個不過全是清單第 2 條（枚舉成員無殺手）與
  第 3 條（名詞無主體）抓到的；DB 子問句在本批無新命中（03 已修）。
