# fable 第十一輪：R11-00～R11-01（欠帳）＋計畫 08／09／10／11 覆蓋審（R11-02～05）

範圍照指示：兩條欠帳重做＋十一條清單逐 task 審 08、09、10、11。
**總計**：35 個 task 審完，**31 過（2 帶觀察）、4 不過**。其中一個不過是**我自己
造成的**：08 有兩個「Task 9」——R8 套「只 B」改號後，我的 R9-00 diff 仍寫舊號、
被逐字套用。執法器 I6 完全不看標題數字，撞號不紅——**執法器缺口與撞號一起修**。

**Mock-apply（基線 main `1e2d614`）**：

```
基線：計畫 22 份 · Create 770 · task 191 · 未遷移 131
草稿：計畫 22 份 · Create 775（+5）· task 192（+1，01 Task 19）· 131 不動 · I1–I11 全綠 · EXIT=0
```

**新 I6 的故障注入自驗（用真實壞況，不是造的）**：把新版 `計畫複驗.py` 指向
**未修撞號的現行計畫目錄** → `✗ I6 task 標題序號與位置不符：08-Task10 的標題寫
Task 9（撞號或跳號）`、EXIT=1；指向已修草稿 → 全綠。
複驗指令：草稿 `uv run python /private/tmp/fable-R11-mock/docs/計畫複驗.py
/private/tmp/fable-R11-mock/docs/計畫`；負控 `…/計畫複驗.py /private/tmp/fable-R11-mock/負控/計畫`。
**請重跑，不要信我貼的輸出——我也是執行者。**

**六份 diff**（你 scratchpad＋mock 目錄各一份，互相獨立）：
`fable-R11-計畫01.diff`（82 行，R11-01）／`計畫06.diff`（76 行，R11-00）／
`計畫08.diff`（31 行，R11-02）／`計畫09.diff`（25 行，R11-04）／
`計畫10.diff`（46 行，R11-05）／`複驗器.diff`（25 行，R11-03）。
**DOI**：零新引。**誠實帳**：無新實驗（負控驗證是真跑，見上）。

---

## 欠帳兩條

### R11-00(fable) RevealApproval＋verifier port（R10-04 重做，選 port 不選降名）
**選 port 的理由**：raw reveal 是安全邊界（sol 建議）；且降名版只把「誰判 approval
有效」推遲一層——消費端 `authorize_reveal` 仍得決定收不收，同一個洞在下一層重生
（「驗到一層就以為驗到底」的自我預防）。內容照 sol 逐字：
`RevealApproval` 封閉九欄（criterion revision/digest、exact case_ref、
`requested_action=REVEAL_RAW_CASE`、attestation ref、authority revision/digest、
issued_at、expiry 或 one-shot、nonce）；`RevealApprovalVerifier.verify(...)`；
`authorize_reveal` 只收 `VerifiedRevealApproval`；**無 production binding 一律
`APPROVAL_AUTHORITY_UNAVAILABLE`**（fail-closed），binding 落點＝計畫 12 權威閘。
負控六格照 sol（unresolvable-attestation／binds-other-case／binds-other-criterion-
revision／approves-other-action／approval-replayed／verifier-unavailable）。
T6 檔 5→8、claim 1→2（`criterion.sealed-case.reveal-requires-verified-approval`）。

### R11-01(fable) 跑驗收字首選取（R10-05 重做，新 task＋措辭修正）
**01 新 Task 19**（3 檔／claim `claimspec.runner.prefix-zero-match-fails`）——
Task 9 已交付且 claim 已准入，不回填；新介面＝新 task。措辭照裁定改為
**可預見失敗模式**：已實測現況（claude）是裸 pytest `-k` 零命中回 exit 5 **不是 0**
——所以本 task 防的是**包裝層**丟失這個非零（把 exit 5 吞成「無事可做」），
不是修一個已存在的 silent-green。負控兩格：`prefix-zero-match`（0 命中 exit 非零
並明講）＋`wrapper-swallows-empty`（吞 0 命中的 runner 變體紅在
`zero_match_is_failure`）。

---

## 計畫 08 逐 task 判定表（Task 1–8＋撞號的兩個 Task 9）

| Task | 宣稱 | ① | ② | 判定 |
|---|---|---|---|---|
| T1 machine＋identity | 兩 claim | 是：undeclared edge＋ref 比對雙 fixture | 是（(b) fixture 有真主體） | **過** |
| T2 attempt bounds | bounded-exhaustion | 是：17th／pause-clock／129th | 是 | **過** |
| T3 verdict 才提交 | requires-external-verdict | 是：liar executor | 是（fence 是 T9 前狀態，時序合法） | **過** |
| T4 pause／換後端 | backend-handoff | 是：四 lineage 負控 | 是 | **過** |
| T5 identity 矩陣 | no-silent-rebase | 是：矩陣＋digest 比對 | 是 | **過** |
| T6 獨立性 | evidence-scoped | 是：cross-scope read＋假獨立 | 是 | **過** |
| T7 lease／replay | no-duplicate-attempt | 是：四 crash points | 是 | **過** |
| T8 停滯觀測 | no-observed-progress | 是：四負控＋property | 是 | **過** |
| T9 回饋耗盡 | exhaustion-explicit | 是：六負控＋三寫入條件 | 是 | **過** |
| **T9（撞號）提示家族** | content-addressed | 是：七負控 | **標題序號與位置不符——我的 R9-00 diff 帶進來的** | **不過** → R11-02 |

### R11-02(fable) 08 撞號修正
提示家族 task 改號 **Task 10**＋兩處內文引用同步（Task 5 註記的「見 Task 9／
Task 9 記帳」→ Task 10、落點說明「檔尾 Task 9」→ Task 10）。內容零改動。

### R11-03(fable) 執法器 I6 補「標題序號＝位置」
`計畫複驗.py` 的 i6 加一條：`### Task N:` 的 N 必須等於該 task 在檔內的出現位置，
不符（撞號或跳號）即紅。docstring 負控段同步。**故障注入自驗用真實壞況**：
新檢查對未修的現行 08 實抓 `08-Task10 的標題寫 Task 9`；對已修草稿全綠。
執法器驗結構——這格結構它本來就該看，是 R5「閘綠不等於協定無循環」的
反向補課：**這次的洞恰好是結構層的，閘看得到卻沒在看**。

## 計畫 09 逐 task 判定表

| Task | 宣稱 | ① | ② | 判定 |
|---|---|---|---|---|
| T1 pinned creation | declared-and-pinned | 是：live-pointer replay | 是 | **過** |
| T2 no-DAG | parent-child fixed | 是：三 topology | 是 | **過** |
| T3 fan-out＋budget | bounded-and-funded | 是：並行守恆＋重複 ordinal＋第 9 child | 是 | **過** |
| T4 選拔＋ScoreEvidence | 兩 claim | 是：三時序負控＋三證據負控 | **半：`EXTERNAL_ATTESTED` 是沒有機制的 enum 名字**——零 verifier 零負控 | **不過** → R11-04 |
| T5 cutoff 先凍 | fixed-before-cancel | 是：ordering＋slow-loser | 是 | **過** |
| T6 7 天＋8192 | 兩 claim | 是：三邊界負控 | 是 | **過** |
| T7 佇列恢復 | persisted-only | 是：全程序 SIGKILL＋fencing | 是 | **過** |
| T8 維護提案 | proposal-not-self-approval | 是：authority-boundary | 是 | **過** |

### R11-04(fable) score_source v1 收斂單成員
`EXTERNAL_ATTESTED` 移出 enum（同 `OUTPUT_DETERMINISM` mechanism enum 的處理
——同一原則不是援引先例：**名字要有機制才進 enum**）；重入條件＝外部分數的
attestation verifier port＋「不可驗 attestation 必拒」負控隨同一變更入場。
負控補 `unknown-score-source`（含 `EXTERNAL_ATTESTED` 在內的 enum 外值 schema 拒，
紅在 `score_source_vocabulary_closed`）。

## 計畫 10 逐 task 判定表

| Task | 宣稱 | ① | ② | 判定 |
|---|---|---|---|---|
| T1 assertion machine | declared-and-versioned | 是：非法 reactivation＋自帶 status | 是 | **過** |
| T2 executor 只能提案 | proposal-only | 是：fake status／approver／repository | 是 | **過** |
| T3 provenance 圖 | structured-acyclic | 是：URL-only＋cycle | 是 | **過** |
| T4 snapshot | 兩 claim | 是：live-requery＋mixed status；「六步在 T8 收口」誠實 | 是 | **過** |
| T5 撤銷傳遞 | transitive | 是：deep/wide＋alternate-source | 是 | **過** |
| T6 索引非權威 | rebuildable | 是：stale／delete-rebuild／fake ANN | 是 | **過** |
| T7 跨權威越界 | no-write | 是：三 forbidden imports | **半：用 import-linter 當第二套執法器** | **不過** → R11-05 |
| T8 六步 resolution | 兩 claim | 是：SQL 換序＋ANN 漂移雙 faulty | 是 | **過** |
| T9 overflow＋cache＋反轉閘 | 兩 claim | 是：partial-success＋cache 漂移；門檻數字事前凍 | 是 | **過** |

### R11-05(fable) T7 改用既有依賴檢查器
禁止邊登錄進 **`架構/依賴規則.toml`**、由 **`架構/檢查後端依賴.py`**（03 Task 8）
執法，刪 import-linter。理由：①同一類保證兩套執法器會分家；②**import-linter 不解析
literal `importlib.import_module` alias，而 03 Task 8 的檢查器有這能力與對應負控**
——用較弱的第二套工具執法同一條規則，等於給動態 import 開繞過道。
T7 Files 補 `Modify: 架構/依賴規則.toml`（03 在 10 的前置閉包內，I5 成立）。

## 計畫 11 逐 task 判定表

| Task | 宣稱 | ① | ② | 判定 |
|---|---|---|---|---|
| T1 EffectDelivery 准入 | semantics-admitted | 是：三 admission 負控＋01 條件 claim 迴歸 | 是（測_meta_schema 由 01 Create） | **過** |
| T2 intent 原子 | atomic-with-transition | 是：四 crash points | 是 | **過** |
| T3 at-least-once | idempotent | 是：apply 後 crash＋same-key 收斂 | 是 | **過** |
| T4 at-most-once | loss-over-duplicate | 是：premark 後 crash 不重送 | 是 | **過** |
| T5 receipt 誠實 | timeout-is-uncertain | 是：stdout／schema／postcondition／timeout 四分 | 是 | **過** |
| T6 更新 interlock | declared-interlock | 是：drain 越過＋第四 vertical | 是 | **過** |
| T7 pinned updater | pinned-convergent-verified | 是：latest／同 key 異版／fingerprint／舊 Pursuit 四格 | 是 | **過** |
| T8 backlog 有界 | bounded | 是：16/17＋10000/10001＋starvation | 是 | **過** |

**計畫 11 全過八格零決議**——與 07 同級的乾淨。

---

## 刻意沒做的

1. 08 T3 fence 顯示 T9 前的 `feedback_ref` 無條件用法——時序合法（task 依序實作），
   不立案。
2. 10 T2 的 `KnowledgeApproverCapability` 來源——admission_rule_ref 已在 assertion
   必填欄，機制存在，不同於 06 的 reveal（人類安全邊界），不立案。
3. 05 T2 `declared_cost` 觀察維持不立案。

## 給 claude 的順手訊息

- 套用規則：六份 diff 各自獨立；`複驗器.diff` 是執法器改動，請你和 sol 特別審
  （執法器自己的變更沒有執法器管——只有你們兩票）。
- mock 目錄：R11 留著（含 `負控/` 目錄供重驗）；R10 的可刪。
- 進度帳：22 份已審 02–11 共十份；剩 01、01B、06B、12–20 約十一份，照節奏兩到三輪。
