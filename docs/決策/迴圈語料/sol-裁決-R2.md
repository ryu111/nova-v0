codex
我會先查三個提案暗中依賴的既有契約：PrimitiveCatalog 是否真的已有 deterministic 語意、state owner 是否允許 plan 06 自行追加新 aggregate/event，以及 Task 16 的 admission bootstrap 路徑。這三處若只是「前置存在」但介面不存在，不能算可直接套用。
exec
/bin/zsh -lc "sed -n '995,1090p' docs/計畫/01-可執行保證語言.md && sed -n '1085,1205p' docs/計畫/01-可執行保證語言.md && sed -n '20,140p' docs/計畫/03-狀態擁有者與事件流.md && sed -n '220,430p' docs/計畫/03-狀態擁有者與事件流.md && sed -n '300,420p' docs/計畫/06-判準評估與隔離回饋.md" in /Users/sbu/nova
 exited 1 in 0ms:
Expected: 【推論】PASS；命名閘那批逐條相符、回零，工作樹跑完與跑前相同。

- [ ] **Step 5: Commit**

```bash
git add 工具/跑指定突變.py 驗收/工具鏈/突變批次 規格/工程/保證/指定突變可重跑.claim.json 架構/test_工程規範.py
git commit -m "build: 把跑指定突變包成有測試的工具"
```

### Task 15: 只准用已准入的原語目錄

**Files:**
- Create: `規格/語言/PrimitiveCatalog.schema.json`
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
  `PRIMITIVE_MISSING_CONTROLS`。
- Forbids: production 路徑接受呼叫端自備的 `原語目錄` 物件。編譯入口只收 `catalog_ref`。
- Forbids: 同一個 `catalog_id` 對到兩份不同 digest 的內容。

**為什麼**：`compile_claim(spec, catalog, binding, offer)` 的 catalog 目前由呼叫端自備。
`nova/權威/判準/test_保證規格語言.py::test_plan_digest_涵蓋四個輸入` 逐字證明換一份自備目錄
**仍然編得出 `TestPlan`**，只是 digest 不同。digest 不同只能證明「這次用了另一份目錄」，
不能證明「這份目錄有權存在」。所以 `UNKNOWN_PRIMITIVE` 擋的是「claim 用了目錄裡沒有的原語」，
**不擋「自備一份含新原語的目錄」**——而後者正是 pixel primitive 與 LLM-judge primitive
未來會走的路。今天的 fail-closed 是副作用不是設計。
地基：OWASP 對 agent tools 要求 backend enforcement 與 verified allowlist registry，
不讓呼叫端自報能用什麼；SLSA 要求 consumer 只接受指定的 signer-builder pair。
加蓋（nova 多出來的拒絕）：未准入目錄、同 id 不同 digest、新原語沒有自己的固定負控。

**ClaimSpec:** 【推論】`claimspec.catalog.admitted-only` 從紅轉綠。

**ClaimSpec落點:** `claimspec.catalog.admitted-only` → `規格/語言/保證/原語目錄須經准入.claim.json`（本 task Create）

**固定負控:** 【推論】三格。`self-supplied-catalog`：呼叫端自備一份只多加了 `always.pass`
的目錄，必須紅在 `catalog_is_admitted`，不得靜默編出合法 `TestPlan`。
`same-id-different-digest`：同一個 `catalog_id` 換掉內容，必須紅在 `catalog_digest_is_content_bound`。
`primitive-without-controls`：准入清單裡的原語沒有列出自己的固定負控，必須紅在
`primitive_admission_requires_named_controls`。
防恆真格兩條：已准入目錄下的合法 claim 仍必須編綠；引用目錄外原語仍必須紅在
`UNKNOWN_PRIMITIVE` 而不是被新的 code 蓋掉。

- [ ] **Step 1: 寫三個負控與兩個防恆真格的 red tests**

```python
def test_自備目錄不得編出計畫() -> None:
    自備 = 原語目錄("ref.v1", (原語("always.pass", 內部, "STRING"),))
    assert 解析目錄(清單, 自備.digest.hex).code == "UNADMITTED_PRIMITIVE_CATALOG"

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
`fixed_controls`。權威層只解析不讀檔；`工具/跑驗收.py` 負責把 bytes 交進去。

- [ ] **Step 4: 把編譯入口改成只收 catalog_ref**

【推論】`compile_claim` 保留 catalog 參數以維持 `plan_digest` 綁四個輸入，
但 production 呼叫路徑一律先過 `解析目錄`；自備物件走不進去。

- [ ] **Step 5: 跑三個負控與兩個防恆真格**

Run: `uv run pytest -q 驗收/保證規格語言/測_目錄准入.py nova/權威/判準/test_原語目錄准入.py`

Expected: 【推論】PASS；三個負控各紅在自己宣告的 code，兩個防恆真格綠。

- [ ] **Step 6: Commit**

```bash
git add 規格/語言/PrimitiveCatalog.schema.json 規格/語言/原語目錄.admitted.json 規格/語言/保證/原語目錄須經准入.claim.json nova/權威/判準/原語目錄准入.py nova/權威/判準/test_原語目錄准入.py 驗收/保證規格語言/測_目錄准入.py nova/權威/判準/保證規格編譯.py 工具/跑驗收.py
git commit -m "feat: 只准用已准入的原語目錄，自備目錄一律拒絕"
```

---

git add 規格/語言/PrimitiveCatalog.schema.json 規格/語言/原語目錄.admitted.json 規格/語言/保證/原語目錄須經准入.claim.json nova/權威/判準/原語目錄准入.py nova/權威/判準/test_原語目錄准入.py 驗收/保證規格語言/測_目錄准入.py nova/權威/判準/保證規格編譯.py 工具/跑驗收.py
git commit -m "feat: 只准用已准入的原語目錄，自備目錄一律拒絕"
```

---

### Task 16: 已准入保證的閉包不可被實作者原地改弱

**Files:**
- Create: `規格/驗收/ClaimAdmissionManifest.schema.json`
- Create: `規格/驗收/已准入保證.manifest.json`
- Create: `規格/工程/保證/已准入保證不可原地改弱.claim.json`
- Create: `架構/檢查已准入保證.py`
- Create: `架構/test_已准入保證.py`
- Modify: `架構/目錄規則.toml`
- Modify: `.github/workflows/gates.yml`

**Interfaces:**
- Produces: `uv run python 架構/檢查已准入保證.py`——比對 manifest 宣告的檔案集合與
  各檔 digest；任一不符即非零。新增 `[[gate]] name = "admission"`。
- Produces: 封閉的 `protected_artifacts.role`：`CLAIM_SOURCE`、`ORACLE`、`FIXED_NEGATIVE`、
  `MUTATION_RECIPE`、`PREDICATE_DEFINITION`、`FIXTURE`、`PRIMITIVE_CATALOG`、
  `BINDING_CONTRACT`、`HARNESS_COMPONENT`。
- Forbids: 把這份清單叫 baseline。業界的 baseline 語意是「已接受的現狀快照」，
  **設計上就允許重新產生**——那正好是本 task 要防的動作。
- Forbids: 只比對已知檔案的內容。必須**同時比對集合**：`iterdir()` 取實際檔案集合與
  manifest 的 name 集合互相 diff，缺一個要紅、多一個也要紅。

**為什麼**：`must_fail_exactly` 目前只在四支實作檔裡被讀取，**沒有任何東西擋得住它被改**。
實作者可以先把 `must_fail_exactly` 縮短、或改 fixture、或改 predicate，再讓測試按新答案紅。
這不是單一 claim 失守，是整個 ClaimSpec 語言的 meta-guarantee 變成恆真。
地基：OPA signed bundle 的驗證第二步逐字要求「the JWT payload and target directory
specify the same set of files」——只 hash 已知檔案的話，刪掉一整份 claim 會靜默通過；
NIST SSDF PO.4.2 要求判準資訊必須防止被竄改或刪除；SLSA Source Track 要求連續性
從一個明確的起始 revision 建立並追蹤。
加蓋：DRAFT 可改；某個 exact revision 一旦 admit，規格側閉包不可修改。
production subject 本來就要被改，凍的是規格側。

**已知未閉合的出口（不得寫成已解決）**：CI 目前跑的是候選者自己那一份 checker。
實測 PR #8 的 CI log：`git checkout --force refs/remotes/pull/8/merge`。
官方解法是 ruleset workflows 指定 workflow 檔來自另一個 repo／另一個 ref，
讓閘的程式離開被閘管的人的寫入範圍。本 task 只做 manifest 與 checker；
信任方向的閉合是 repo 設定，**必須實測後才准宣稱成立**。

**ClaimSpec:** 【推論】`engineering.admission.closure-immutable` 從紅轉綠。

**ClaimSpec落點:** `engineering.admission.closure-immutable` → `規格/工程/保證/已准入保證不可原地改弱.claim.json`（本 task Create）

**固定負控:** 【推論】三格。`weaken-must-fail-exactly`：把第一份 wall-limit claim 的
`must_fail_exactly` 從 `["elapsed_bound", "worker_dead"]` 縮成 `["terminal_is_timed_out"]`，
必須紅在 `admitted_claim_source_is_byte_identical`——即使縮短後測試自己會綠。
`delete-an-admitted-claim`：整份刪掉一個已准入的 claim 檔，必須紅在
`manifest_covers_exact_file_set`；這一格專門抓「只比對內容不比對集合」的寫法。
`rewrite-the-manifest`：同一個 commit 裡同步改掉 manifest 的 digest，必須紅在
`candidate_cannot_rewrite_admission_baseline`。
防恆真格：六道閘全綠且沒有動到任何已准入檔案時，這道閘必須放行。

- [ ] **Step 1: 寫三個負控與防恆真格的 red tests**

```python
def test_縮短_must_fail_exactly_要被擋(tmp_path: Path) -> None:
    改弱(claim="規格/執行/保證/外部時間上限.claim.json", 欄="must_fail_exactly",
        值=["terminal_is_timed_out"])
    assert 跑閘() != 0

def test_刪掉一整份已准入_claim_要被擋() -> None:
    刪("規格/執行/保證/外部時間上限.claim.json")
    assert 跑閘() != 0
```

- [ ] **Step 2: 跑紅測確認今天改弱不會有任何東西紅**

Run: `uv run pytest -q 架構/test_已准入保證.py`

Expected: 【推論】FAIL；`ModuleNotFoundError: 架構.檢查已准入保證` 之外，
`weaken-must-fail-exactly` 那格今天**六道閘全綠**——改弱之後測試按新答案紅，
而新答案是實作者自己寫的。

- [ ] **Step 3: 寫 manifest schema 與第一份 manifest**

【推論】第一個 entry 是 `execution.limit.wall.externally-enforced`，因為它已經有最清楚的
差異證據：`terminal_is_timed_out` 在負控中保持綠，正是它有辨識力的證據。
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

## Plan Exit Gate

【推論】本 plan 完成的唯一判定命令是：

```bash
uv run ruff format --check . && uv run ruff check . && uv run mypy nova 架構 工具 && uv run python 架構/檢查工程規範.py && uv run python 架構/檢查已准入保證.py && uv run pytest -q -n 2 架構/test_工程規範.py 架構/test_已准入保證.py 驗收/工具鏈 驗收/保證規格語言 nova/核心 nova/權威/判準 nova/基礎設施/裁定執行
```

【推論】必須同時保存工程規範四類fixed negative、第一份 wall-limit actual ACCEPT、positive ACCEPT、negative direct CLAIM_REJECTED evidence；只有 pytest exit 0 而缺 direct red evidence不算完成。

## Execution Handoff

【推論】完成後進 [02-宣告式狀態機.md](./02-宣告式狀態機.md)。若使用 subagent-driven execution，每個 Task 一個 fresh worker，先審 ClaimSpec／負控，再審 production code；不得讓同一 worker 自己宣稱它寫的 judge 有牙。
sed: docs/計畫/03-狀態擁有者與事件流.md: No such file or directory

exec
/bin/zsh -lc 'ls docs/計畫/03* && rg -n "state owner|StateOwner|append|事件|repository|Aggregate" docs/計畫/03*.md | head -n 240' in /Users/sbu/nova
 succeeded in 0ms:
docs/計畫/03-權威狀態與事件日誌.md
1:# 權威狀態與事件日誌 Implementation Plan
5:**Goal:** 【推論】建立唯一 state owner、declared-transition journal與可獨立尾隨 replica；任一 transaction boundary SIGKILL 後只靠持久 bytes 恢復，不遺失 committed event、不接受非法 edge、不產生兩個有效 lease。
7:**Architecture:** 【推論】`權威狀態.sqlite3` 用 one process／one connection／rollback／FULL，所有 worker 只送 typed command；同一 transaction append event、更新 head、寫 owner ledgers。commit 後 single publisher 按 global_seq 冪等複製到 `尾隨事件.sqlite3` WAL；tail 可砍，權威 journal 不可由 reader 寫。
11:**Spec:** 【查證】本檔「子系統規格」、[第三輪 runtime 三道硬閘與事件](../sol-新局-第三輪.md#27-執行時禁止未宣告轉移三道硬閘)、[第二輪 workload envelope](../sol-新局-第二輪.md#32-建議的-v1-design-envelope)。第五輪 archive／prune 由 Plan 04 承接。
23:【推論】state owner API 接 `CommandEnvelope(command_id, entity_id, expected_seq, trigger_id, payload)`，載入 entity 已釘 MachinePlan，取得唯一 transition，再在一筆 transaction 寫 event＋head。command idempotency key 重送回同 result，不重跑 decision。
30:規格/語言/事件.schema.json                    — event tagged-union envelope。
32:規格/介面/保證/事件流獨立.claim.json           — reader 不碰 owner transaction。
33:nova/核心/事件.py                              — EventEnvelope value／canonical bytes。
39:├── 工作單元.py                                — BEGIN／append／head／commit。
45:    ├── 0001_事件與機器目錄.sql                — journal、catalog、head、idempotency。
47:nova/基礎設施/事件流/sqlite/
51:└── 遷移/0001_尾隨事件.sql                     — event bytes、digest、cursor。
61:└── 測_事件流獨立.py                           — long tail 不持 owner transaction。
72:### Task 1: 固定事件 envelope 與 canonical bytes
75:- Create: `規格/語言/事件.schema.json`
76:- Create: `nova/核心/事件.py`
135:git add 規格/語言/事件.schema.json nova/核心/事件.py nova/應用/工作單元.py nova/應用/test_工作單元.py
136:git commit -m "feat: 定義 canonical 的領域事件封套"
144:- Create: `nova/基礎設施/狀態庫/sqlite/遷移/0001_事件與機器目錄.sql`
211:git add nova/基礎設施/狀態庫/sqlite/遷移/0001_事件與機器目錄.sql nova/基礎設施/狀態庫/sqlite/機器目錄.py nova/基礎設施/狀態庫/sqlite/test_工作單元.py 驗收/儲存/測_非法轉移資料庫負控.py
225:- Produces: `StateOwnerClient.execute(CommandEnvelope) -> CommandResult`
280:### Task 4: 原子 append event、head 與 command idempotency
284:- Modify: `nova/基礎設施/狀態庫/sqlite/遷移/0001_事件與機器目錄.sql`
322:        self.append_events(events)
342:git add nova/基礎設施/狀態庫/sqlite/工作單元.py nova/基礎設施/狀態庫/sqlite/遷移/0001_事件與機器目錄.sql nova/基礎設施/狀態庫/sqlite/test_工作單元.py
343:git commit -m "feat: 事件與 head 原子提交"
418:- Create: `nova/基礎設施/事件流/sqlite/遷移/0001_尾隨事件.sql`
419:- Create: `nova/基礎設施/事件流/sqlite/尾隨庫.py`
420:- Create: `nova/基礎設施/事件流/sqlite/發布器.py`
421:- Create: `nova/基礎設施/事件流/sqlite/test_發布器.py`
422:- Create: `驗收/儲存/測_事件流獨立.py`
444:Run: `uv run pytest -q nova/基礎設施/事件流/sqlite/test_發布器.py`
453:    return tail.append_idempotent(batch.events, expected_after=after)
458:Run: `uv run pytest -q nova/基礎設施/事件流/sqlite/test_發布器.py`
464:Run: `uv run pytest -q 驗收/儲存/測_事件流獨立.py`
471:git add nova/基礎設施/狀態庫/sqlite/讀取埠.py nova/基礎設施/事件流/sqlite
472:git commit -m "feat: 發佈逐位元組相同的事件尾流"
483:- Modify: `nova/基礎設施/事件流/sqlite/發布器.py`
537:git add 規格/儲存/保證/權威交易崩潰重建.claim.json 驗收/儲存/測_強制終止矩陣.py nova/基礎設施/狀態庫/sqlite/擁有者.py nova/基礎設施/事件流/sqlite/發布器.py
549:- Create: `規格/介面/保證/事件流獨立.claim.json`
612:git add 架構 規格/介面/保證/事件流獨立.claim.json
619:uv run pytest -q -n 2 nova/應用 nova/基礎設施/狀態庫 nova/基礎設施/事件流 驗收/儲存 架構 && uv run python 架構/檢查後端依賴.py nova

exec
/bin/zsh -lc "sed -n '20,70p' docs/計畫/03-權威狀態與事件日誌.md && sed -n '215,350p' docs/計畫/03-權威狀態與事件日誌.md && rg -n \"ClaimAdmissionManifest|已准入保證|admission|准入\" docs/計畫/01-可執行保證語言.md docs/計畫/20-整體組裝與跨系統驗收.md | tail -n 100" in /Users/sbu/nova
 succeeded in 0ms:

## 子系統規格

【推論】state owner API 接 `CommandEnvelope(command_id, entity_id, expected_seq, trigger_id, payload)`，載入 entity 已釘 MachinePlan，取得唯一 transition，再在一筆 transaction 寫 event＋head。command idempotency key 重送回同 result，不重跑 decision。

【推論】tail publisher 的 truth 是 state-owner read port，不是直接另開權威 SQLite reader；它按 cursor 取 committed canonical event bytes，寫 WAL cache並更新 durable publisher cursor。UI subscriber只拿 range／live event port。

## File Structure

```text
規格/語言/事件.schema.json                    — event tagged-union envelope。
規格/儲存/保證/權威交易崩潰重建.claim.json     — state-owner persisted-only restart。
規格/介面/保證/事件流獨立.claim.json           — reader 不碰 owner transaction。
nova/核心/事件.py                              — EventEnvelope value／canonical bytes。
nova/應用/
├── 工作單元.py                                — state-owner port，不暴露 SQL。
└── test_工作單元.py                           — fake/real contract。
nova/基礎設施/狀態庫/sqlite/
├── 擁有者.py                                  — one connection command loop／IPC。
├── 工作單元.py                                — BEGIN／append／head／commit。
├── 機器目錄.py                                — admitted transition catalog。
├── 租約.py                                    — lease／renew／takeover fencing。
├── 讀取埠.py                                  — publisher/recovery bounded range port。
├── test_工作單元.py                           — adapter contract。
└── 遷移/
    ├── 0001_事件與機器目錄.sql                — journal、catalog、head、idempotency。
    └── 0002_租約.sql                          — lease owner／expiry／epoch。
nova/基礎設施/事件流/sqlite/
├── 發布器.py                                  — global_seq idempotent copy。
├── 尾隨庫.py                                  — WAL range/read-only subscription。
├── test_發布器.py                             — duplicate／gap／restart。
└── 遷移/0001_尾隨事件.sql                     — event bytes、digest、cursor。
nova/啟動/狀態擁有者.py                        — 唯一 state DB composition root。
架構/
├── 依賴規則.toml                              — sqlite import allowlist。
├── 檢查後端依賴.py                            — AST import graph checker。
└── test_依賴規則.py                           — direct DB bypass fixture。
驗收/儲存/
├── 測_非法轉移資料庫負控.py                   — composite FK 第二道紅。
├── 測_強制終止矩陣.py                         — boundary SIGKILL。
├── 測_租約回收.py                             — fencing epoch。
└── 測_事件流獨立.py                           — long tail 不持 owner transaction。
```

## Dependency Gate

前置計畫：01 02

【推論】Plan 01 提供 executable claims；Plan 02 提供 MachinePlan、transition catalog rows與 illegal-edge decision。缺 02 時 SQLite 只能存自由 state string，DB 負控沒有 oracle。

---
---

### Task 3: 建 single-owner command loop 與唯一 writer connection

**Files:**
- Create: `nova/基礎設施/狀態庫/sqlite/擁有者.py`
- Create: `nova/啟動/狀態擁有者.py`
- Modify: `nova/基礎設施/狀態庫/sqlite/test_工作單元.py`

**Interfaces:**
- Produces: `StateOwnerClient.execute(CommandEnvelope) -> CommandResult`
- Produces: owner startup attestation `pid/db_path/journal_mode/synchronous`。

**ClaimSpec:** 【推論】`storage.state-owner.single-writer-topology` 從紅轉綠。

**固定負控:** 【推論】第二個 owner 對相同 data root 啟動必須 `STATE_OWNER_ALREADY_ACTIVE`；worker 直接拿 DB path 的 fixture 被依賴／startup gate 拒絕。

- [ ] **Step 1: 寫 two-owner test**

```python
def test_同資料根只能一個_owner(tmp_path: Path) -> None:
    first = start_owner(tmp_path)
    second = start_owner(tmp_path)
    assert first.ready
    assert second.failure.code == "STATE_OWNER_ALREADY_ACTIVE"
```

- [ ] **Step 2: 跑紅測**

Run: `uv run pytest -q nova/基礎設施/狀態庫/sqlite/test_工作單元.py -k owner`

Expected: 【推論】FAIL with missing owner process。

- [ ] **Step 3: 寫 lockfile attestation、one connection與 command queue**

```python
def open_authoritative_connection(path: Path) -> sqlite3.Connection:
    connection = sqlite3.connect(path, isolation_level=None)
    connection.execute("PRAGMA journal_mode=DELETE")
    connection.execute("PRAGMA synchronous=FULL")
    connection.execute("PRAGMA foreign_keys=ON")
    return connection
```

- [ ] **Step 4: 跑 single-owner tests**

Run: `uv run pytest -q nova/基礎設施/狀態庫/sqlite/test_工作單元.py -k owner`

Expected: 【推論】PASS；worker client 沒有 connection property。

- [ ] **Step 5: 驗 startup attestation**

Run: `uv run python -m nova.啟動.狀態擁有者 --data-root /private/tmp/nova-owner-probe --一次性自檢`

Expected: 【推論】exit 0 and `journal_mode=delete,synchronous=2,connections=1`；自檢清掉 probe root。

- [ ] **Step 6: Commit**

```bash
git add nova/基礎設施/狀態庫/sqlite/擁有者.py nova/啟動/狀態擁有者.py nova/基礎設施/狀態庫/sqlite/test_工作單元.py
git commit -m "feat: 讓命令經由單一狀態 owner 串行化"
```

---

### Task 4: 原子 append event、head 與 command idempotency

**Files:**
- Create: `nova/基礎設施/狀態庫/sqlite/工作單元.py`
- Modify: `nova/基礎設施/狀態庫/sqlite/遷移/0001_事件與機器目錄.sql`
- Modify: `nova/基礎設施/狀態庫/sqlite/test_工作單元.py`

**Interfaces:**
- Consumes: `MachinePlan.transition(current_state, trigger, facts)` from Plan 02。
- Produces: exactly one stored `CommandResult` per command id；event batch 1–32。

**ClaimSpec:** 【推論】`storage.command.event-head-atomic`、`storage.command.idempotent-replay` 從紅轉綠。

**固定負控:** 【推論】event insert 後、head update 前 raise；相同 command 重送；33-event command，各自不得留下 partial rows。

- [ ] **Step 1: 寫 failure injection tests**

```python
def test_event_後_head_前失敗整筆_rollback(uow: SqliteUnitOfWork) -> None:
    result = uow.execute(command(), fault=FaultPoint.AFTER_EVENT_BEFORE_HEAD)
    assert result.failure.code == "INJECTED_STORAGE_FAULT"
    assert uow.count_events() == 0
    assert uow.load_head(entity_id()) is None
```

- [ ] **Step 2: 跑紅測**

Run: `uv run pytest -q nova/基礎設施/狀態庫/sqlite/test_工作單元.py -k 'atomic or idempotent or fanout'`

Expected: 【推論】FAIL due partial state or missing UoW。

- [ ] **Step 3: 寫 transaction pipeline**

```python
def execute(self, command: CommandEnvelope) -> CommandResult:
    with self.immediate_transaction():
        if cached := self.command_result(command.command_id):
            return cached
        head = self.require_expected_head(command.entity_id, command.expected_seq)
        transition = self.machine_engine.decide(head, command.trigger)
        events = self.event_factory.build(transition, command)
        require_range("events_per_transaction", len(events), 1, 32)
        self.append_events(events)
        self.update_head(head.fold(events))
        return self.store_command_result(command.command_id, events)
```

- [ ] **Step 4: 跑 atomic／idempotency tests**

Run: `uv run pytest -q nova/基礎設施/狀態庫/sqlite/test_工作單元.py -k 'atomic or idempotent or fanout'`

Expected: 【推論】PASS；重送回相同 event ids，不增加 rows。

- [ ] **Step 5: 跑 named mutation：commit 移到 head 前**

Run: `uv run python 工具/跑驗收.py --claim storage.command.event-head-atomic`

Expected: 【推論】direct red `partial_commit_visible`。

- [ ] **Step 6: Commit**

```bash
git add nova/基礎設施/狀態庫/sqlite/工作單元.py nova/基礎設施/狀態庫/sqlite/遷移/0001_事件與機器目錄.sql nova/基礎設施/狀態庫/sqlite/test_工作單元.py
git commit -m "feat: 事件與 head 原子提交"
```

---

### Task 5: 建 lease renew／takeover fencing

**Files:**
docs/計畫/20-整體組裝與跨系統驗收.md:81:├── 測_workload封套.py                       — admission caps、60m soak、burst、publisher latency。
docs/計畫/20-整體組裝與跨系統驗收.md:520:【推論】支援exact target的fixture走drain→install→fingerprint verify；Codex manifest在command admission即回`UNSUPPORTED_UPDATE:NO_EXACT_TARGET_INSTALLER`且UI event不產生可更新能力。
docs/計畫/20-整體組裝與跨系統驗收.md:544:- Exercises: CriterionSnapshot、KnowledgeSnapshot、ContextManifest、ConstraintSet、IsolationOffer、BudgetReservation、QuotaTopology in one Execution admission。
docs/計畫/20-整體組裝與跨系統驗收.md:553:- [ ] **Step 1: 寫同一Execution admission的五個fault cases**
docs/計畫/20-整體組裝與跨系統驗收.md:591:### Task 9: 實測 admission caps、soak、burst與事件發布 SLO
docs/計畫/20-整體組裝與跨系統驗收.md:807:【推論】每筆control包含admitted-before-subject digest、owner ClaimRef、faulty subject／semantic mutation anchor、exact test id、`must_fail_exactly`與admission event ref；execution後不能修改同revision。
docs/計畫/01-可執行保證語言.md:33:【推論】designated mutation 是 `NegativeControl` 或 `MutationControlRef` 在 admission 前固定的 faulty subject／semantic anchor；mutmut 全掃只產生 diagnostic EvidenceRecord，不產生 acceptance percentage。
docs/計畫/01-可執行保證語言.md:81:規格/語言/PrimitiveCatalog.schema.json        — 已准入原語目錄的封閉 schema。
docs/計畫/01-可執行保證語言.md:83:規格/語言/保證/原語目錄須經准入.claim.json     — 自備目錄一律 typed 拒絕。
docs/計畫/01-可執行保證語言.md:84:nova/權威/判準/原語目錄准入.py                 — catalog_ref → 原語目錄，或 typed 失敗。
docs/計畫/01-可執行保證語言.md:85:nova/權威/判準/test_原語目錄准入.py            — 自備目錄、同 id 不同 digest、缺負控。
docs/計畫/01-可執行保證語言.md:86:驗收/保證規格語言/測_目錄准入.py               — 目錄准入的黑箱負控與防恆真格。
docs/計畫/01-可執行保證語言.md:87:規格/驗收/ClaimAdmissionManifest.schema.json  — 已准入保證閉包的封閉 schema。
docs/計畫/01-可執行保證語言.md:88:規格/驗收/已准入保證.manifest.json             — 受保護 artifact 的檔案集合與 digest。
docs/計畫/01-可執行保證語言.md:89:規格/工程/保證/已准入保證不可原地改弱.claim.json — 改弱已准入答案必須被擋。
docs/計畫/01-可執行保證語言.md:90:架構/檢查已准入保證.py                         — 集合與 digest 雙向比對；不叫 baseline。
docs/計畫/01-可執行保證語言.md:91:架構/test_已准入保證.py                        — 改弱、刪整份、改 manifest 三格負控。
docs/計畫/01-可執行保證語言.md:435:**固定負控:** 【推論】加入 `"passed": true`、移除 negative controls、把 `wall_ms` 寫成 string、外部效果原語搭配 `effect_delivery=null`、非效果 claim 搭配 non-null contract、宣告 `EXACTLY_ONCE` 六個 instance 都必須 admission red。
docs/計畫/01-可執行保證語言.md:1004:### Task 15: 只准用已准入的原語目錄
docs/計畫/01-可執行保證語言.md:1009:- Create: `規格/語言/保證/原語目錄須經准入.claim.json`
docs/計畫/01-可執行保證語言.md:1010:- Create: `nova/權威/判準/原語目錄准入.py`
docs/計畫/01-可執行保證語言.md:1011:- Create: `nova/權威/判準/test_原語目錄准入.py`
docs/計畫/01-可執行保證語言.md:1012:- Create: `驗收/保證規格語言/測_目錄准入.py`
docs/計畫/01-可執行保證語言.md:1017:- Consumes: 已准入清單 bytes（由呼叫端讀進來——權威層不碰檔案系統）與一個 `catalog_ref`。
docs/計畫/01-可執行保證語言.md:1032:加蓋（nova 多出來的拒絕）：未准入目錄、同 id 不同 digest、新原語沒有自己的固定負控。
docs/計畫/01-可執行保證語言.md:1036:**ClaimSpec落點:** `claimspec.catalog.admitted-only` → `規格/語言/保證/原語目錄須經准入.claim.json`（本 task Create）
docs/計畫/01-可執行保證語言.md:1041:`primitive-without-controls`：准入清單裡的原語沒有列出自己的固定負控，必須紅在
docs/計畫/01-可執行保證語言.md:1042:`primitive_admission_requires_named_controls`。
docs/計畫/01-可執行保證語言.md:1043:防恆真格兩條：已准入目錄下的合法 claim 仍必須編綠；引用目錄外原語仍必須紅在
docs/計畫/01-可執行保證語言.md:1054:    assert isinstance(編(底(), catalog=已准入目錄()), TestPlan)
docs/計畫/01-可執行保證語言.md:1059:Run: `uv run pytest -q 驗收/保證規格語言/測_目錄准入.py`
docs/計畫/01-可執行保證語言.md:1078:Run: `uv run pytest -q 驗收/保證規格語言/測_目錄准入.py nova/權威/判準/test_原語目錄准入.py`
docs/計畫/01-可執行保證語言.md:1085:git add 規格/語言/PrimitiveCatalog.schema.json 規格/語言/原語目錄.admitted.json 規格/語言/保證/原語目錄須經准入.claim.json nova/權威/判準/原語目錄准入.py nova/權威/判準/test_原語目錄准入.py 驗收/保證規格語言/測_目錄准入.py nova/權威/判準/保證規格編譯.py 工具/跑驗收.py
docs/計畫/01-可執行保證語言.md:1086:git commit -m "feat: 只准用已准入的原語目錄，自備目錄一律拒絕"
docs/計畫/01-可執行保證語言.md:1091:### Task 16: 已准入保證的閉包不可被實作者原地改弱
docs/計畫/01-可執行保證語言.md:1094:- Create: `規格/驗收/ClaimAdmissionManifest.schema.json`
docs/計畫/01-可執行保證語言.md:1095:- Create: `規格/驗收/已准入保證.manifest.json`
docs/計畫/01-可執行保證語言.md:1096:- Create: `規格/工程/保證/已准入保證不可原地改弱.claim.json`
docs/計畫/01-可執行保證語言.md:1097:- Create: `架構/檢查已准入保證.py`
docs/計畫/01-可執行保證語言.md:1098:- Create: `架構/test_已准入保證.py`
docs/計畫/01-可執行保證語言.md:1103:- Produces: `uv run python 架構/檢查已准入保證.py`——比對 manifest 宣告的檔案集合與
docs/計畫/01-可執行保證語言.md:1104:  各檔 digest；任一不符即非零。新增 `[[gate]] name = "admission"`。
docs/計畫/01-可執行保證語言.md:1129:**ClaimSpec:** 【推論】`engineering.admission.closure-immutable` 從紅轉綠。
docs/計畫/01-可執行保證語言.md:1131:**ClaimSpec落點:** `engineering.admission.closure-immutable` → `規格/工程/保證/已准入保證不可原地改弱.claim.json`（本 task Create）
docs/計畫/01-可執行保證語言.md:1136:`delete-an-admitted-claim`：整份刪掉一個已准入的 claim 檔，必須紅在
docs/計畫/01-可執行保證語言.md:1139:`candidate_cannot_rewrite_admission_baseline`。
docs/計畫/01-可執行保證語言.md:1140:防恆真格：六道閘全綠且沒有動到任何已准入檔案時，這道閘必須放行。
docs/計畫/01-可執行保證語言.md:1150:def test_刪掉一整份已准入_claim_要被擋() -> None:
docs/計畫/01-可執行保證語言.md:1157:Run: `uv run pytest -q 架構/test_已准入保證.py`
docs/計畫/01-可執行保證語言.md:1159:Expected: 【推論】FAIL；`ModuleNotFoundError: 架構.檢查已准入保證` 之外，
docs/計畫/01-可執行保證語言.md:1176:Run: `uv run pytest -q 架構/test_已准入保證.py && uv run python 工具/驗全部.py`
docs/計畫/01-可執行保證語言.md:1183:git add 規格/驗收/ClaimAdmissionManifest.schema.json 規格/驗收/已准入保證.manifest.json 規格/工程/保證/已准入保證不可原地改弱.claim.json 架構/檢查已准入保證.py 架構/test_已准入保證.py 架構/目錄規則.toml .github/workflows/gates.yml
docs/計畫/01-可執行保證語言.md:1184:git commit -m "feat: 已准入保證的閉包不可被實作者原地改弱"
docs/計畫/01-可執行保證語言.md:1194:uv run ruff format --check . && uv run ruff check . && uv run mypy nova 架構 工具 && uv run python 架構/檢查工程規範.py && uv run python 架構/檢查已准入保證.py && uv run pytest -q -n 2 架構/test_工程規範.py 架構/test_已准入保證.py 驗收/工具鏈 驗收/保證規格語言 nova/核心 nova/權威/判準 nova/基礎設施/裁定執行

exec
/bin/zsh -lc "sed -n '300,410p' docs/計畫/06-判準評估與隔離回饋.md && sed -n '20,85p' docs/計畫/04-內容定址與分層儲存.md" in /Users/sbu/nova
 exited 1 in 0ms:

---

### Task 5: 只輸出 clause-level gated feedback

**Files:**
- Create: `規格/判準/FeedbackPolicy.schema.json`
- Create: `nova/權威/判準/回饋閘.py`
- Modify: `nova/應用/執行判準.py`
- Create: `驗收/判準/測_回饋縮減.py`
- Create: `規格/判準/保證/回饋經reducer.claim.json`

**Interfaces:**
- Produces: `reduce_feedback(verdict, policy) -> FeedbackPacket`。
- Produces: fixed enums `OutcomeClass`、`LocationBucket`、`Retryability`。

**ClaimSpec:** 【推論】`criterion.feedback.clause-level-reduced` 從紅轉綠。

**固定負控:** 【推論】raw assertion 為 `expected SECRET-ANSWER-441, got 0`；FeedbackPacket canonical bytes 不得含 `SECRET`、`ANSWER`、`441` 或 raw repr，但要含失敗 `clause_id`。

- [ ] **Step 1: 寫 secret canary absence 與 gradient presence red**

```python
def test_feedback_has_clause_without_expected_repr() -> None:
    packet = reduce_feedback(verdict_with_raw("expected SECRET-ANSWER-441, got 0"), fixed_policy())
    encoded = canonical_json_bytes(packet)
    assert b"clause.limit.enforced" in encoded
    assert b"SECRET-ANSWER-441" not in encoded
```

- [ ] **Step 2: 跑測試確認 raw stderr 被轉送**

Run: `uv run pytest -q 驗收/判準/測_回饋縮減.py`

Expected: 【推論】FAIL at canary absence。

- [ ] **Step 3: 寫 allowlist reducer；未知 raw class 歸 `UNCLASSIFIED`**

```python
return FeedbackPacket(items=tuple(FeedbackItem(clause_id=r.clause_id, outcome_class=map_outcome(r), location_bucket=map_location(r), retryability=map_retry(r)) for r in verdict.results))
```

- [ ] **Step 4: 跑 reducer property tests 與 ClaimSpec**

Run: `uv run pytest -q 驗收/判準/測_回饋縮減.py && uv run python 工具/跑驗收.py --claim criterion.feedback.clause-level-reduced`

Expected: 【推論】PASS；任意 raw UTF-8 string 不會直接出現在 packet。

- [ ] **Step 5: Commit**

```bash
git add 規格/判準/FeedbackPolicy.schema.json 規格/判準/保證/回饋經reducer.claim.json nova/權威/判準/回饋閘.py nova/應用/執行判準.py 驗收/判準/測_回饋縮減.py
git commit -m "feat: 判準回饋逐條把關"
```

---

### Task 6: 實作「揭露即燒掉」且 crash-safe

**Files:**
- Create: `nova/權威/判準/案例治理.py`
- Modify: `nova/權威/判準/定義.py`
- Modify: `nova/應用/執行判準.py`
- Create: `驗收/判準/測_揭露燒毀.py`
- Create: `規格/判準/保證/揭露即燒掉.claim.json`

**Interfaces:**
- Produces: `authorize_reveal(case_ref, approval_envelope) -> RevealReceipt`。
- Produces: atomic `CaseBurned` event before raw reveal bytes are returned。

**ClaimSpec:** 【推論】`criterion.sealed-case.reveal-burns-before-release` 從紅轉綠。

**固定負控:** 【推論】在 `CaseBurned` commit 前／後 SIGKILL；commit 前不得收到 raw detail，commit 後重啟不得再次選中該 case。

- [ ] **Step 1: 寫 ordering 與兩 crash points red**

```python
def test_reveal_is_after_burn_commit() -> None:
    trace = reveal_with_crash("after_burn_before_return")
    assert trace.committed("CaseBurned")
    assert not select_for_evaluation(trace.case_ref).is_selectable
```

- [ ] **Step 2: 跑測試確認 reveal/burn 非原子順序**

Run: `uv run pytest -q 驗收/判準/測_揭露燒毀.py`

Expected: 【推論】FAIL at one crash point。

- [ ] **Step 3: 先 append-once `CaseBurned`，再從 CAS 釋出 raw bytes**

```python
receipt = state_owner.transition(case_ref, command=BurnForReveal(approval_ref), idempotency_key=reveal_key)
return RevealPayload(receipt=receipt, bytes=evidence_store.get(case_ref.content_ref))
```

- [ ] **Step 4: 跑 crash matrix 與 ClaimSpec**

Run: `uv run pytest -q 驗收/判準/測_揭露燒毀.py && uv run python 工具/跑驗收.py --claim criterion.sealed-case.reveal-burns-before-release`

Expected: 【推論】PASS；named reuse negative direct red。

- [ ] **Step 5: Commit**

```bash
git add nova/權威/判準 nova/應用/執行判準.py 驗收/判準/測_揭露燒毀.py 規格/判準/保證/揭露即燒掉.claim.json
git commit -m "feat: 封存 case 揭露前先燒掉"
```

---

sed: docs/計畫/04-內容定址與分層儲存.md: No such file or directory

codex
## 三個特別問題

1. 是，`CLAUSE_COVERAGE_JOIN` 有偽陽性停滯，也有偽陽性進展：

   - clause 內部改善但尚未轉綠，會被算成停滯。
   - 候選 A 只通過 clause 1、候選 B 只通過 clause 2，跨候選 union 變成 `{1,2}`，卻沒有任何單一候選同時通過兩條。

   因此它不能承載泛稱的 `NO_PROGRESS`。

2. 我接受 fable 對 `EXACT_REPEAT` 的反駁。我的最小版只適合成為窄義、低成本的 `EXACT_REPEAT` 訊號，不能關閉一般無進展偵測缺口。把它當完整答案確實會形成幾乎不觸發的假保證。

3. 是，R2-04 目前會造成 bootstrap 死鎖。受信任 merge path 尚未閉合時，「所有新增 admission 都必須已有外部 attestation」只有兩種結果：第一份 admission 永遠建不了，或測試 fixture 綠、production 路徑其實不可用。

## 裁決總表

| 決議 | 我的票 | 理由碼 |
|---|---|---|
| R2-01 | REJECT | `FOUNDATION_MISREAD`, `INVARIANT_BREAK` |
| R2-02 | REJECT | `WEAKENS_GUARANTEE` |
| R2-03 | REJECT | `NOT_TESTABLE`, `WEAKENS_GUARANTEE` |
| R2-04 | REJECT | `NOT_TESTABLE`, `WEAKENS_GUARANTEE` |
| R2-05 | REJECT | `CHANGES_INTERFACE`, `WEAKENS_GUARANTEE` |
| R2-06 | APPROVE | — |

---

### R2-01 — REJECT

理由碼：`FOUNDATION_MISREAD`, `INVARIANT_BREAK`

一句話：deterministic primitive 不等於 exact measurement；一個 deterministic primitive 也可以計算 sample mean，其結果可重現但仍有抽樣不確定度。

此外，現有 Task 15 的 PrimitiveCatalog 沒有 `deterministic` 或 measurement-semantics 欄位。它目前只有：

```text
primitive_id
revision
implementation_digest
observation_type
effect_kind
required_isolation
fixed_controls
```

R2-01 卻假定 catalog 已能背書 exact，這個介面不存在。

最小修改：

- 把 `EXACT_BY_DEFINITION` 改成 `EXACT_OBSERVATION`。
- 准入條件不是單純 `deterministic=true`，而是：

  ```text
  對 pinned input artifact 的完整母體執行
  無 sampling
  無缺失值
  primitive 與 input bytes 全部釘 digest
  結果是該函式對該 artifact 的 exact output
  ```

- ESTIMATED primitive 即使 deterministic，也仍必須走 interval。
- 先修改 plan 01 Task 15，讓 catalog 具有封閉的：

  ```text
  result_semantics = EXACT_ARTIFACT_FUNCTION | ESTIMATOR
  ```

  並為「deterministic estimator 冒充 exact」加入固定負控。
- R2-01 再消費這個已存在的欄位；不能在 plan 09 散文裡假定它存在。

正確 DOI 已修復，該部分沒有問題。

---

### R2-02 — REJECT

理由碼：`WEAKENS_GUARANTEE`

一句話：跨候選的 accepted-clause union 既會誤殺真實改善，也會把不同候選各自通過的 clause 拼成一個不存在的「最佳候選」，不能取得 `NO_PROGRESS` 名稱。

最小修改：

- 不准跨候選 union clause coverage。
- `best_so_far` 必須指向一個實際 candidate verdict vector，或一個實際 Pareto frontier；不能是從多個候選拼出的虛構向量。
- v1 最簡單可採：

  ```text
  BEST_CANDIDATE_UNDER_FROZEN_ORDER
  ```

  Criterion revision 事前固定 clause priority／ordinal progress order；只有新候選在該 frozen order 下嚴格勝過目前 best candidate 才重置窗口。

- 如果 criterion 只提供 PASS/FAIL，無法表達「位置 A 到位置 B 更接近」，系統只能誠實回報 `NO_OBSERVED_PROGRESS`，不能聲稱知道真實無進展。
- terminal reason 與 claim 改成：

  ```text
  NO_OBSERVED_PROGRESS
  pursuit.retry.no-observed-progress-typed
  ```

- 固定負控補：

  - A 通過 clause 1、B 通過 clause 2，union 不得冒充單一最佳候選；
  - clause 內 ordinal 改善時，若 frozen measure 支援該 ordinal，窗口必須重置；
  - measure 不支援細粒度時，結果必須明示是 observational policy stop。

`K` 必填無預設可以保留。

---

### R2-03 — REJECT

理由碼：`NOT_TESTABLE`, `WEAKENS_GUARANTEE`

一句話：`PURE_REPLAYER` 有可測機制，但 `PINNED_DETERMINISTIC_ENGINE` 與 `BACKEND_CONTRACT_WITH_CONFORMANCE_SUITE` 目前只是名稱；任意 backend 填一個 ref 就可能取得過強能力。

有限 conformance suite 仍不能證明未來所有輸出決定性。它最多證明 suite 範圍內符合契約。

最小修改：

- v1 只准 `PURE_REPLAYER` 取得：

  ```text
  SEEDED_OUTPUT_DETERMINISM
  ```

- `PINNED_DETERMINISTIC_ENGINE` 與 `BACKEND_CONTRACT_WITH_CONFORMANCE_SUITE` 暫不放進可准入 enum；等各自有獨立 admission schema、checker 與固定負控後再以擴充加入。
- 外部 backend 目前最多取得：

  ```text
  SEEDED_OUTPUT_REPEATABILITY_OBSERVED
  CONTRACTUAL_OUTPUT_DETERMINISM_CLAIMED
  ```

  後者是契約主張，不得滿足要求機械決定性的 claim。
- 固定負控加入「偽造 mechanistic evidence ref」以及「有契約、有 suite，但 suite 外輸出改變」。

四層重播界線本身正確，可以原封保留。

---

### R2-04 — REJECT

理由碼：`NOT_TESTABLE`, `WEAKENS_GUARANTEE`

一句話：四角色模型已修正字串漏洞，但受信任 attestation path 尚未存在；fixture 可以綠，不代表 production admission 能取得可信 actor。

最小修改：

1. 先拆出 bootstrap task，建立並實測 `AdmissionTrustRoot`：

   ```text
   trusted attestation issuer
   repository/ref
   workflow identity
   actor identity extraction rule
   trust-root revision/digest
   expiry/revocation
   ```

2. 必須實際證明 required workflow 不取自候選 PR 可寫的 ref。
3. genesis admission 必須有明示 ceremony：

   - 由控制端建立 trust-root revision；
   - 由不同 attested actor 核准第一份 manifest；
   - genesis evidence content-addressed 保存。

4. trust path 未閉合時：

   ```text
   新 admission → ADMISSION_TRUST_ROOT_UNAVAILABLE
   ```

   但 bootstrap ceremony 必須是另一條明示、一次性、可驗證的 transition，不能永遠死鎖。

5. role-separation claim 必須以前述 live trust-root probe 為前置；不能只靠本地簽章 fixture轉綠。

四角色與 `admission_decided_by != subject_changed_by` 可以保留。

---

### R2-05 — REJECT

理由碼：`CHANGES_INTERFACE`, `WEAKENS_GUARANTEE`

一句話：提案仍把 state owner 當成可任意 append `DisclosureRecorded` 的 event store；但 plan 03 的介面要求每個 command 經已釘 `MachinePlan` 取得合法 transition，不能由應用層直接追加新事件。

新 disclosure aggregate 目前沒有 MachineSpec，也沒有說明 crash 後如何取得相同 FeedbackPacket bytes。

最小修改：

- Create 一份明示 machine：

  ```text
  規格/判準/揭露帳.machine.json
  ```

- 定義 command／event：

  ```text
  ReserveDisclosure
  DisclosureRecorded
  DisclosureExhausted
  ```

- 應用層只能呼叫：

  ```text
  StateOwnerClient.execute(CommandEnvelope)
  ```

  不得直接 append event。

- 在 transition transaction 前，先把 canonical FeedbackPacket bytes 放入 CAS；event 必須記：

  ```text
  disclosure_id
  packet_content_ref
  packet_digest
  sealed_pool_lineage_id
  ordinal
  ```

- crash 後從 CAS 取回完全相同 bytes；不能依賴重新執行 reducer「大概會一樣」。
- machine 必須拒絕：

  - 同 disclosure id、不同 packet digest；
  - ordinal 超 cap；
  - lineage 不符；
  -未 commit 就 release。

- File count 仍可維持十檔內；新增 machine 檔後重新列完整清單。

Dwork 地基的強度標示已修正，可以保留；正式引用時應區分 Theorem 17 的有限 range bound 與 adaptive composition lemma。

---

### R2-06 — APPROVE

06B 的依賴、套件身分、終態與固定負控已補齊；新 plan 的分層與口徑可以寫入。

寫檔時必須維持四個細節：

- `scipy` 與直接 import 的 `numpy` 都列為 direct dependency，不能只依賴 scipy 的傳遞依賴。
- paired analysis 必須明寫 `paired=True`，resampling unit 是 case；同一 case 的 replicates 不能冒充獨立樣本。
- fingerprint 應綁實際安裝 artifact／environment 與完整 `uv.lock` digest；不能從 lock 裡任選一個未必安裝的 wheel hash。
- scratchpad 的「同 seed 兩次相同」只證明目前 pinned stack 可重播，不得升格成所有 scipy 版本的保證。

這些是寫入精度，不改提案方向，因此不構成 REJECT。

本輪我不另提 `R2-07(sol)`：目前最高優先的新增問題就是 R2-04 所暴露的 admission trust-root bootstrap；直接要求 fable 把它補進 R2-04 比另開一條互相競爭的提案更乾淨。
tokens used
41,889
## 三個特別問題

1. 是，`CLAUSE_COVERAGE_JOIN` 有偽陽性停滯，也有偽陽性進展：

   - clause 內部改善但尚未轉綠，會被算成停滯。
   - 候選 A 只通過 clause 1、候選 B 只通過 clause 2，跨候選 union 變成 `{1,2}`，卻沒有任何單一候選同時通過兩條。

   因此它不能承載泛稱的 `NO_PROGRESS`。

2. 我接受 fable 對 `EXACT_REPEAT` 的反駁。我的最小版只適合成為窄義、低成本的 `EXACT_REPEAT` 訊號，不能關閉一般無進展偵測缺口。把它當完整答案確實會形成幾乎不觸發的假保證。

3. 是，R2-04 目前會造成 bootstrap 死鎖。受信任 merge path 尚未閉合時，「所有新增 admission 都必須已有外部 attestation」只有兩種結果：第一份 admission 永遠建不了，或測試 fixture 綠、production 路徑其實不可用。

## 裁決總表

| 決議 | 我的票 | 理由碼 |
|---|---|---|
| R2-01 | REJECT | `FOUNDATION_MISREAD`, `INVARIANT_BREAK` |
| R2-02 | REJECT | `WEAKENS_GUARANTEE` |
| R2-03 | REJECT | `NOT_TESTABLE`, `WEAKENS_GUARANTEE` |
| R2-04 | REJECT | `NOT_TESTABLE`, `WEAKENS_GUARANTEE` |
| R2-05 | REJECT | `CHANGES_INTERFACE`, `WEAKENS_GUARANTEE` |
| R2-06 | APPROVE | — |

---

### R2-01 — REJECT

理由碼：`FOUNDATION_MISREAD`, `INVARIANT_BREAK`

一句話：deterministic primitive 不等於 exact measurement；一個 deterministic primitive 也可以計算 sample mean，其結果可重現但仍有抽樣不確定度。

此外，現有 Task 15 的 PrimitiveCatalog 沒有 `deterministic` 或 measurement-semantics 欄位。它目前只有：

```text
primitive_id
revision
implementation_digest
observation_type
effect_kind
required_isolation
fixed_controls
```

R2-01 卻假定 catalog 已能背書 exact，這個介面不存在。

最小修改：

- 把 `EXACT_BY_DEFINITION` 改成 `EXACT_OBSERVATION`。
- 准入條件不是單純 `deterministic=true`，而是：

  ```text
  對 pinned input artifact 的完整母體執行
  無 sampling
  無缺失值
  primitive 與 input bytes 全部釘 digest
  結果是該函式對該 artifact 的 exact output
  ```

- ESTIMATED primitive 即使 deterministic，也仍必須走 interval。
- 先修改 plan 01 Task 15，讓 catalog 具有封閉的：

  ```text
  result_semantics = EXACT_ARTIFACT_FUNCTION | ESTIMATOR
  ```

  並為「deterministic estimator 冒充 exact」加入固定負控。
- R2-01 再消費這個已存在的欄位；不能在 plan 09 散文裡假定它存在。

正確 DOI 已修復，該部分沒有問題。

---

### R2-02 — REJECT

理由碼：`WEAKENS_GUARANTEE`

一句話：跨候選的 accepted-clause union 既會誤殺真實改善，也會把不同候選各自通過的 clause 拼成一個不存在的「最佳候選」，不能取得 `NO_PROGRESS` 名稱。

最小修改：

- 不准跨候選 union clause coverage。
- `best_so_far` 必須指向一個實際 candidate verdict vector，或一個實際 Pareto frontier；不能是從多個候選拼出的虛構向量。
- v1 最簡單可採：

  ```text
  BEST_CANDIDATE_UNDER_FROZEN_ORDER
  ```

  Criterion revision 事前固定 clause priority／ordinal progress order；只有新候選在該 frozen order 下嚴格勝過目前 best candidate 才重置窗口。

- 如果 criterion 只提供 PASS/FAIL，無法表達「位置 A 到位置 B 更接近」，系統只能誠實回報 `NO_OBSERVED_PROGRESS`，不能聲稱知道真實無進展。
- terminal reason 與 claim 改成：

  ```text
  NO_OBSERVED_PROGRESS
  pursuit.retry.no-observed-progress-typed
  ```

- 固定負控補：

  - A 通過 clause 1、B 通過 clause 2，union 不得冒充單一最佳候選；
  - clause 內 ordinal 改善時，若 frozen measure 支援該 ordinal，窗口必須重置；
  - measure 不支援細粒度時，結果必須明示是 observational policy stop。

`K` 必填無預設可以保留。

---

### R2-03 — REJECT

理由碼：`NOT_TESTABLE`, `WEAKENS_GUARANTEE`

一句話：`PURE_REPLAYER` 有可測機制，但 `PINNED_DETERMINISTIC_ENGINE` 與 `BACKEND_CONTRACT_WITH_CONFORMANCE_SUITE` 目前只是名稱；任意 backend 填一個 ref 就可能取得過強能力。

有限 conformance suite 仍不能證明未來所有輸出決定性。它最多證明 suite 範圍內符合契約。

最小修改：

- v1 只准 `PURE_REPLAYER` 取得：

  ```text
  SEEDED_OUTPUT_DETERMINISM
  ```

- `PINNED_DETERMINISTIC_ENGINE` 與 `BACKEND_CONTRACT_WITH_CONFORMANCE_SUITE` 暫不放進可准入 enum；等各自有獨立 admission schema、checker 與固定負控後再以擴充加入。
- 外部 backend 目前最多取得：

  ```text
  SEEDED_OUTPUT_REPEATABILITY_OBSERVED
  CONTRACTUAL_OUTPUT_DETERMINISM_CLAIMED
  ```

  後者是契約主張，不得滿足要求機械決定性的 claim。
- 固定負控加入「偽造 mechanistic evidence ref」以及「有契約、有 suite，但 suite 外輸出改變」。

四層重播界線本身正確，可以原封保留。

---

### R2-04 — REJECT

理由碼：`NOT_TESTABLE`, `WEAKENS_GUARANTEE`

一句話：四角色模型已修正字串漏洞，但受信任 attestation path 尚未存在；fixture 可以綠，不代表 production admission 能取得可信 actor。

最小修改：

1. 先拆出 bootstrap task，建立並實測 `AdmissionTrustRoot`：

   ```text
   trusted attestation issuer
   repository/ref
   workflow identity
   actor identity extraction rule
   trust-root revision/digest
   expiry/revocation
   ```

2. 必須實際證明 required workflow 不取自候選 PR 可寫的 ref。
3. genesis admission 必須有明示 ceremony：

   - 由控制端建立 trust-root revision；
   - 由不同 attested actor 核准第一份 manifest；
   - genesis evidence content-addressed 保存。

4. trust path 未閉合時：

   ```text
   新 admission → ADMISSION_TRUST_ROOT_UNAVAILABLE
   ```

   但 bootstrap ceremony 必須是另一條明示、一次性、可驗證的 transition，不能永遠死鎖。

5. role-separation claim 必須以前述 live trust-root probe 為前置；不能只靠本地簽章 fixture轉綠。

四角色與 `admission_decided_by != subject_changed_by` 可以保留。

---

### R2-05 — REJECT

理由碼：`CHANGES_INTERFACE`, `WEAKENS_GUARANTEE`

一句話：提案仍把 state owner 當成可任意 append `DisclosureRecorded` 的 event store；但 plan 03 的介面要求每個 command 經已釘 `MachinePlan` 取得合法 transition，不能由應用層直接追加新事件。

新 disclosure aggregate 目前沒有 MachineSpec，也沒有說明 crash 後如何取得相同 FeedbackPacket bytes。

最小修改：

- Create 一份明示 machine：

  ```text
  規格/判準/揭露帳.machine.json
  ```

- 定義 command／event：

  ```text
  ReserveDisclosure
  DisclosureRecorded
  DisclosureExhausted
  ```

- 應用層只能呼叫：

  ```text
  StateOwnerClient.execute(CommandEnvelope)
  ```

  不得直接 append event。

- 在 transition transaction 前，先把 canonical FeedbackPacket bytes 放入 CAS；event 必須記：

  ```text
  disclosure_id
  packet_content_ref
  packet_digest
  sealed_pool_lineage_id
  ordinal
  ```

- crash 後從 CAS 取回完全相同 bytes；不能依賴重新執行 reducer「大概會一樣」。
- machine 必須拒絕：

  - 同 disclosure id、不同 packet digest；
  - ordinal 超 cap；
  - lineage 不符；
  -未 commit 就 release。

- File count 仍可維持十檔內；新增 machine 檔後重新列完整清單。

Dwork 地基的強度標示已修正，可以保留；正式引用時應區分 Theorem 17 的有限 range bound 與 adaptive composition lemma。

---

### R2-06 — APPROVE

06B 的依賴、套件身分、終態與固定負控已補齊；新 plan 的分層與口徑可以寫入。

寫檔時必須維持四個細節：

- `scipy` 與直接 import 的 `numpy` 都列為 direct dependency，不能只依賴 scipy 的傳遞依賴。
- paired analysis 必須明寫 `paired=True`，resampling unit 是 case；同一 case 的 replicates 不能冒充獨立樣本。
- fingerprint 應綁實際安裝 artifact／environment 與完整 `uv.lock` digest；不能從 lock 裡任選一個未必安裝的 wheel hash。
- scratchpad 的「同 seed 兩次相同」只證明目前 pinned stack 可重播，不得升格成所有 scipy 版本的保證。

這些是寫入精度，不改提案方向，因此不構成 REJECT。

本輪我不另提 `R2-07(sol)`：目前最高優先的新增問題就是 R2-04 所暴露的 admission trust-root bootstrap；直接要求 fable 把它補進 R2-04 比另開一條互相競爭的提案更乾淨。
