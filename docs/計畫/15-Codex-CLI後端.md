# Codex CLI 後端 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:subagent-driven-development` (recommended) or `superpowers:executing-plans` to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 【推論】以固定argv與JSONL protocol把Codex CLI接成ExecutorBackend，逐bucket解析`token_count.rate_limits`、隔離使用者設定與session副作用、保留外部限額/終態權，並誠實拒絕不符合pinned-target契約的內建self-update。

**Architecture:** 【推論】adapter以`codex exec` non-interactive mode從stdin送InvocationEnvelope、以`--json`讀newline-delimited events、以`--ephemeral`避免session rollout檔。程序仍由ExecutionEnvelope監督；Codex sandbox只是defense-in-depth。manifest由executable digest/version/help/model/protocol與明示capabilities組成。rate-limit parser只讀typed JSONL event，資源權威再做五態/topology判斷。

**Tech Stack:** 【推論】CPython 3.14.7、pinned Codex CLI executable、async subprocess/JSONL、plan 05 backend contract、plan 07 quota types、plan 12 context contract、CAS raw streams。

**Spec:** 【查證】官方OpenAI文件把`codex exec`列為stable non-interactive command，`--json`輸出JSONL、`--ephemeral`不持久session rollout、`--ignore-user-config`忽略使用者config、`--sandbox workspace-write`設定內層sandbox；同一reference顯示`codex update`沒有target-version參數，因此不能滿足本系統pinned update契約。[OpenAI Codex CLI command reference](https://developers.openai.com/codex/cli/reference)。額度event shape依[控制端實抓資料](../控制端審查.md#codexsession-紀錄的-token_count-事件帶-rate_limits)。

## Global Constraints

- 【推論】production argv固定從typed builder產生，不接受shell string或caller追加任意flags。
- 【推論】固定禁止`--dangerously-bypass-approvals-and-sandbox`、`--yolo`、`danger-full-access`、`--last`與從任意目錄resume。
- 【推論】v1 base argv為`codex exec --json --ephemeral --ignore-user-config --ignore-rules --strict-config --ask-for-approval never --sandbox workspace-write --cd <workspace> --model <pinned-model> -`；prompt只由stdin送入。
- 【推論】`--sandbox workspace-write`不是敵意隔離證明；system offer仍只有實際host probe capabilities。
- 【推論】JSONL unknown event不drop，保存raw CAS並發`PROTOCOL_FAULT`；自由stdout文字沒有terminal/quota裁定權。
- 【推論】primary、secondary、credits各為獨立QuotaBucket；plan_type只是metadata，spend control/reached type是typed status，不把used percent換成absolute餘額。
- 【推論】`codex update` v1不納入EffectEndpoint，manifest明示`update=UNSUPPORTED_UPDATE`；UI不得顯示可更新按鈕。若未來有exact-target installer，需新fingerprint/adapter revision與plan 11全套重驗。

## File Structure

```text
nova/介接/執行者後端/codex_cli/
├── manifest.py                               — executable/version/help/model/protocol capability fingerprint。
├── argv.py                                   — closed non-interactive argv builder/forbidden flags。
├── 執行.py                                   — process/JSONL→BackendEvent stream。
├── jsonl.py                                  — closed event decoder/raw evidence refs。
├── 額度.py                                   — token_count.rate_limits→per-bucket observations。
├── 上下文.py                                 — stdin initial segment/context offer。
├── 更新.py                                   — explicit UnsupportedPinnedUpdate adapter result only。
└── test_契約.py                              — shared contract plus Codex-specific matrix。
規格/執行/保證/後端/
├── codex-manifest完整.claim.json              — executable/model/protocol drift changes fingerprint。
├── codex-argv封閉.claim.json                 — exact flags/no shell/no dangerous overrides。
├── codex-jsonl契約.claim.json                — closed event stream/unknown fault/no self-terminal。
└── codex上下文與更新誠實.claim.json           — initial only; pinned update unsupported。
規格/資源/保證/codex額度逐bucket.claim.json   — primary/secondary/credits/status mapping。
驗收/後端/codex_cli/
├── fake_codex.py                             — executable JSONL/exit/signal/update fixtures。
├── fixtures/*.jsonl                         — frozen normal/quota/unknown/malformed event streams。
├── 測_manifest與argv.py                     — fingerprint/flags/env/config isolation。
├── 測_jsonl執行.py                          — ordering/error/cancel/output caps。
├── 測_額度.py                               — bucket topology/reset/credits/spend controls。
├── 測_上下文.py                             — stdin exact bytes/reassert unsupported。
└── 測_更新能力.py                           — self-update cannot claim pinned target。
```

## Dependency Gate

前置計畫：05 06 07 11 12 13

【推論】必須完成plan 05–07、11–13。adapter不直接呼叫application或resource repository；它只發BackendEvent/QuotaObservation並接InvocationEnvelope。前置未綠就接CLI，JSONL的版本細節會被誤當領域模型，`codex update`也會繞過Effect Authority。

---

### Task 1: 建立executable fingerprint與closed argv builder

**Files:**
- Create: `nova/介接/執行者後端/codex_cli/manifest.py`
- Create: `nova/介接/執行者後端/codex_cli/argv.py`
- Create: `驗收/後端/codex_cli/fake_codex.py`
- Create: `驗收/後端/codex_cli/測_manifest與argv.py`
- Create: `規格/執行/保證/後端/codex-manifest完整.claim.json`
- Create: `規格/執行/保證/後端/codex-argv封閉.claim.json`

**Interfaces:**
- Produces: `probe_codex(executable, model_id) -> BackendManifest`。
- Produces: `build_exec_argv(request, workspace) -> tuple[str, ...]` exactly matching Global Constraints。

**ClaimSpec:** 【推論】`backend.codex-cli.manifest.fingerprint-complete` 與 `backend.codex-cli.argv.closed-and-safe` 從紅轉綠。

**固定負控:** 【推論】executable bytes/help/model改但fingerprint不變；caller注入`--yolo`/shell metacharacters/`--last`/extra add-dir；兩claims direct red。

- [ ] **Step 1: 寫fingerprint sensitivity與exact argv snapshot red**

```python
def test_exec_argv_is_exact_and_reads_prompt_from_stdin() -> None:
    assert build_exec_argv(fixed_request(), Path("/work")) == ("codex","exec","--json","--ephemeral","--ignore-user-config","--ignore-rules","--strict-config","--ask-for-approval","never","--sandbox","workspace-write","--cd","/work","--model","model-pinned","-")
```

- [ ] **Step 2: 跑tests確認modules缺失**

Run: `uv run pytest -q 驗收/後端/codex_cli/測_manifest與argv.py`

Expected: 【推論】FAIL。

- [ ] **Step 3: 寫resolved executable digest/version/help hash/capabilities與nonextensible builder**

```python
fingerprint = sha256_ref(canonical_json_bytes({"executable_sha256":hash_file(binary),"version":version_output,"exec_help_sha256":sha256_ref(help_bytes),"model":model_id,"adapter":ADAPTER_REVISION}))
```

- [ ] **Step 4: 跑兩份ClaimSpec**

Run: `uv run pytest -q 驗收/後端/codex_cli/測_manifest與argv.py && uv run python 工具/跑驗收.py --claim backend.codex-cli.manifest.fingerprint-complete --claim backend.codex-cli.argv.closed-and-safe`

Expected: 【推論】PASS；all injected flags direct red。

- [ ] **Step 5: Commit**

```bash
git add nova/介接/執行者後端/codex_cli/manifest.py nova/介接/執行者後端/codex_cli/argv.py 驗收/後端/codex_cli/fake_codex.py 驗收/後端/codex_cli/測_manifest與argv.py 規格/執行/保證/後端/codex-manifest完整.claim.json 規格/執行/保證/後端/codex-argv封閉.claim.json
git commit -m "feat: 為 Codex CLI 的呼叫建立指紋並加約束"
```

---

### Task 2: 寫closed JSONL decoder與raw evidence保存

**Files:**
- Create: `nova/介接/執行者後端/codex_cli/jsonl.py`
- Create: `驗收/後端/codex_cli/fixtures/normal.jsonl`
- Create: `驗收/後端/codex_cli/fixtures/quota.jsonl`
- Create: `驗收/後端/codex_cli/fixtures/unknown.jsonl`
- Create: `驗收/後端/codex_cli/fixtures/malformed.jsonl`
- Create: `驗收/後端/codex_cli/測_jsonl執行.py`

**Interfaces:**
- Produces: `decode_jsonl_line(bytes) -> CodexEvent|ProtocolFault`。
- Persists: every raw line CAS ref, event index, observed monotonic time。

**ClaimSpec:** 【推論】`backend.codex-cli.jsonl.closed-decoder` 從紅轉綠。

**固定負控:** 【推論】unknown type被drop、malformed JSON被當assistant text、超過line byte limit仍buffer、duplicate event id重複套用；direct red。

- [ ] **Step 1: 寫四frozen streams decoder red**

```python
def test_unknown_event_becomes_protocol_fault() -> None:
    event = decode_jsonl_line(load_fixture("unknown.jsonl").splitlines()[0])
    assert event.code == "UNKNOWN_CODEX_EVENT"
```

- [ ] **Step 2: 跑tests確認decoder缺失**

Run: `uv run pytest -q 驗收/後端/codex_cli/測_jsonl執行.py -k decoder`

Expected: 【推論】FAIL。

- [ ] **Step 3: 寫line cap/schema/tagged union/dedupe key**

```python
if len(line) > MAX_JSONL_LINE_BYTES:
    return ProtocolFault("JSONL_LINE_LIMIT")
```

- [ ] **Step 4: 跑decoder ClaimSpec**

Run: `uv run pytest -q 驗收/後端/codex_cli/測_jsonl執行.py -k decoder && uv run python 工具/跑驗收.py --claim backend.codex-cli.jsonl.closed-decoder`

Expected: 【推論】PASS；raw refs present even for faults。

- [ ] **Step 5: Commit**

```bash
git add nova/介接/執行者後端/codex_cli/jsonl.py 驗收/後端/codex_cli/fixtures 驗收/後端/codex_cli/測_jsonl執行.py
git commit -m "feat: 解碼 Codex 的 JSONL 事件"
```

---

### Task 3: 實作process adapter並通過共用execution/cancel契約

**Files:**
- Create: `nova/介接/執行者後端/codex_cli/執行.py`
- Create: `nova/介接/執行者後端/codex_cli/test_契約.py`
- Modify: `驗收/後端/codex_cli/測_jsonl執行.py`
- Create: `規格/執行/保證/後端/codex-jsonl契約.claim.json`

**Interfaces:**
- Implements: `ExecutorBackend.events(request)` via ProcessSupervisor/BoundedByteCollector。
- Maps: Codex JSONL progress/item/tool/usage/final/error to BackendEvent; exit evidence separate。

**ClaimSpec:** 【推論】`backend.codex-cli.execution.protocol-parity` 從紅轉綠。

**固定負控:** 【推論】final message直接terminal SUCCEEDED、exit nonzero前的success event被採信、SIGTERM忽略後孫程序存活、stderr爆量；共用suite direct red。

- [ ] **Step 1: 寫fake executable lifecycle/cancel red**

```python
async def test_final_event_does_not_write_execution_terminal() -> None:
    events = await collect(codex_backend(fake_codex("final-then-exit-9")))
    assert any(e.kind is BackendEventKind.BACKEND_COMPLETION_OBSERVED for e in events)
    assert all(not isinstance(e, ExecutionTerminated) for e in events)
```

- [ ] **Step 2: 跑shared suite確認adapter缺失**

Run: `uv run pytest -q nova/介接/執行者後端/codex_cli/test_契約.py 驗收/後端/codex_cli/測_jsonl執行.py`

Expected: 【推論】FAIL。

- [ ] **Step 3: 寫stdin bytes、async line stream、process-group cancellation與exit event**

```python
proc = await supervisor.spawn(argv=build_exec_argv(request, workspace), stdin=request.invocation_bytes, env_allowlist=CODEX_ENV_ALLOWLIST)
```

- [ ] **Step 4: 跑common/ClaimSpec**

Run: `uv run pytest -q nova/介接/執行者後端/codex_cli/test_契約.py 驗收/後端/codex_cli/測_jsonl執行.py -n 2 && uv run python 工具/跑驗收.py --claim backend.codex-cli.execution.protocol-parity`

Expected: 【推論】PASS；external envelope determines terminal。

- [ ] **Step 5: Commit**

```bash
git add nova/介接/執行者後端/codex_cli/執行.py nova/介接/執行者後端/codex_cli/test_契約.py 驗收/後端/codex_cli/測_jsonl執行.py 規格/執行/保證/後端/codex-jsonl契約.claim.json
git commit -m "feat: 讓 Codex CLI 走執行封套"
```

---

### Task 4: 解析token_count.rate_limits成per-bucket evidence

**Files:**
- Create: `nova/介接/執行者後端/codex_cli/額度.py`
- Create: `驗收/後端/codex_cli/測_額度.py`
- Create: `規格/資源/保證/codex額度逐bucket.claim.json`

**Interfaces:**
- Produces: primary/secondary `FRACTION_USED` windows and credits `ABSOLUTE_REMAINING|STATUS_ONLY` observations。
- Preserves: window_minutes、resets_at、plan_type、spend_control_reached、rate_limit_reached_type、source event/session refs。

**ClaimSpec:** 【推論】`resource.provider-quota.codex-token-count-per-bucket` 從紅轉綠。

**固定負控:** 【推論】primary/secondary扁平化、47%換成假token餘額、credits balance字串用float、null secondary當NOT_APPLICABLE、reset後推full；direct red。

- [ ] **Step 1: 寫user-provided event/nullable/credits boundary red**

```python
def test_used_percent_remains_fraction_not_absolute_remaining() -> None:
    observations = parse_rate_limits(load_fixture_event("quota.jsonl"))
    primary = find_bucket(observations, "primary")
    assert primary.utilization == Decimal("0.47") and primary.remaining is None
```

- [ ] **Step 2: 跑tests確認parser缺失**

Run: `uv run pytest -q 驗收/後端/codex_cli/測_額度.py`

Expected: 【推論】FAIL。

- [ ] **Step 3: 寫Decimal typed parser/topology與raw ref**

```python
used = Decimal(str(bucket["used_percent"])) / Decimal(100)
```

- [ ] **Step 4: 跑resource suite/ClaimSpec**

Run: `uv run pytest -q 驗收/後端/codex_cli/測_額度.py 驗收/資源/測_供應商額度五態.py 驗收/資源/測_額度拓撲.py && uv run python 工具/跑驗收.py --claim resource.provider-quota.codex-token-count-per-bucket`

Expected: 【推論】PASS；每bucket state由Resource Authority clock分類，不由adapter填fresh/stale。

- [ ] **Step 5: Commit**

```bash
git add nova/介接/執行者後端/codex_cli/額度.py 驗收/後端/codex_cli/測_額度.py 規格/資源/保證/codex額度逐bucket.claim.json
git commit -m "feat: 觀測 Codex 的額度 bucket"
```

---

### Task 5: 隔離config/session並誠實宣告context能力

**Files:**
- Create: `nova/介接/執行者後端/codex_cli/上下文.py`
- Modify: `nova/介接/執行者後端/codex_cli/manifest.py`
- Create: `驗收/後端/codex_cli/測_上下文.py`

**Interfaces:**
- Produces: exact initial stdin bytes; candidate workspace/env allowlist; no rollout files。
- Offers: INVOCATION_START; reassert false; meter only with proven upper-bound/capacity evidence。

**ClaimSpec:** 【推論】`backend.codex-cli.context-and-config-isolated` 從紅轉綠。

**固定負控:** 【推論】讀使用者config/execpolicy、寫session rollout到共享home、載入workspace外AGENTS、宣告compaction reassert、平均token估算；direct red/unsupported。

- [ ] **Step 1: 寫poisoned config/rules/home fixture red**

```python
def test_user_config_and_rules_do_not_change_argv_or_prompt() -> None:
    poisoned = run_with_poisoned_user_codex_home()
    clean = run_with_empty_user_codex_home()
    assert poisoned.captured_invocation == clean.captured_invocation
```

- [ ] **Step 2: 跑tests確認ambient config滲入**

Run: `uv run pytest -q 驗收/後端/codex_cli/測_上下文.py`

Expected: 【推論】FAIL。

- [ ] **Step 3: 寫ephemeral CODEX_HOME projection/env allowlist與context offer**

```python
env = build_env_allowlist(base_env, CODEX_HOME=ephemeral_auth_projection, NO_COLOR="1")
```

- [ ] **Step 4: 跑context/ClaimSpec**

Run: `uv run pytest -q 驗收/後端/codex_cli/測_上下文.py && uv run python 工具/跑驗收.py --claim backend.codex-cli.context-and-config-isolated`

Expected: 【推論】PASS；auth可用但user config/rules/session state不可變更semantic input。

- [ ] **Step 5: Commit**

```bash
git add nova/介接/執行者後端/codex_cli/上下文.py nova/介接/執行者後端/codex_cli/manifest.py 驗收/後端/codex_cli/測_上下文.py
git commit -m "feat: 隔離 Codex CLI 的脈絡與設定"
```

---

### Task 6: 把無target的self-update固定為unsupported

**Files:**
- Create: `nova/介接/執行者後端/codex_cli/更新.py`
- Create: `驗收/後端/codex_cli/測_更新能力.py`
- Create: `規格/執行/保證/後端/codex上下文與更新誠實.claim.json`

**Interfaces:**
- Produces: `request_pinned_update(target_version) -> UnsupportedUpdate(reason="NO_EXACT_TARGET_INSTALLER")`。
- Manifest: update capability false; no effect endpoint registration。

**ClaimSpec:** 【推論】`backend.codex-cli.update-capability-honest` 從紅轉綠。

**固定負控:** 【推論】adapter執行`codex update`、`latest`或無target package command後宣告pinned success；effect contract/direct control red。

- [ ] **Step 1: 寫no-endpoint/no-command red**

```python
def test_builtin_self_update_is_not_registered_as_pinned_updater() -> None:
    manifest = probe_manifest(fake_codex())
    assert not manifest.update_capability.supported
    assert endpoint_registry.find(manifest.backend_id, "install-pinned-version") is None
```

- [ ] **Step 2: 跑tests確認optimistic updater**

Run: `uv run pytest -q 驗收/後端/codex_cli/測_更新能力.py`

Expected: 【推論】FAIL if any self-update path is advertised。

- [ ] **Step 3: 寫typed unsupported result與UI capability event**

```python
def request_pinned_update(target_version: str) -> UnsupportedUpdate:
    return UnsupportedUpdate("NO_EXACT_TARGET_INSTALLER")
```

- [ ] **Step 4: 跑ClaimSpec**

Run: `uv run pytest -q 驗收/後端/codex_cli/測_更新能力.py && uv run python 工具/跑驗收.py --claim backend.codex-cli.update-capability-honest`

Expected: 【推論】PASS；fake latest updater negative direct red。

- [ ] **Step 5: Commit**

```bash
git add nova/介接/執行者後端/codex_cli/更新.py 驗收/後端/codex_cli/測_更新能力.py 規格/執行/保證/後端/codex上下文與更新誠實.claim.json
git commit -m "feat: 拒絕沒釘住版本的 Codex 自我更新"
```

---

### Task 7: 跑完整Codex adapter contract/negative matrix

**Files:**
- Modify: `nova/介接/執行者後端/codex_cli/test_契約.py`
- Modify: `驗收/後端/codex_cli/測_jsonl執行.py`

**Interfaces:**
- Instantiates: shared backend suite, quota suite, context suite, no-criterion projection, process cleanup。

**ClaimSpec:** 【推論】`backend.codex-cli.full-contract-matrix` 從紅轉綠。

**固定負控:** 【推論】named faulty adapters：shell argv、drop unknown JSONL、self-terminal、flatten quota、ambient config、fake update；指定tests各殺一個，不能用mutmut總擊殺率。

- [ ] **Step 1: 登錄六個predeclared faulty subjects/tests**

```python
FAULTY_SUBJECTS = (ShellArgvCodex, DropUnknownCodex, SelfTerminalCodex, FlattenQuotaCodex, AmbientConfigCodex, LatestUpdaterCodex)
```

- [ ] **Step 2: 跑negative tests確認每個faulty subject至少有指定direct red**

Run: `uv run pytest -q nova/介接/執行者後端/codex_cli/test_契約.py 驗收/後端/codex_cli -k negative`

Expected: 【推論】PASS only when every named mutation is killed by its designated test；若actual尚未完成則overall red。

- [ ] **Step 3: 跑完整suite/ClaimSpecs**

Run: `uv run pytest -q nova/介接/執行者後端/codex_cli 驗收/後端/codex_cli -n 2 && uv run python 工具/跑驗收.py --prefix backend.codex-cli. --claim resource.provider-quota.codex-token-count-per-bucket`

Expected: 【推論】PASS；actuals green, named negatives direct red。

- [ ] **Step 4: Commit**

```bash
git add nova/介接/執行者後端/codex_cli/test_契約.py 驗收/後端/codex_cli/測_jsonl執行.py
git commit -m "test: 驗證 Codex CLI adapter 的完整契約"
```

## Plan Exit Gate

- 【推論】argv固定、stdin prompt、JSONL、ephemeral/config/rules isolation與process cleanup全成立。
- 【推論】primary/secondary/credits分bucket，used percent不轉假absolute，reset不推full。
- 【推論】inner Codex sandbox不冒充system hostile isolation；context reassert/meter只按evidence宣告。
- 【推論】官方self-update因無exact target而typed unsupported，沒有EffectEndpoint或UI假按鈕。
- 【推論】六個事前named faulty adapters各被指定test殺掉，不採mutation kill rate。
- 【推論】`uv run pytest -q nova/介接/執行者後端/codex_cli 驗收/後端/codex_cli -n 2` 與本plan ClaimSpecs綠。

## Execution Handoff

【推論】官方command reference是argv選擇的查證來源；實作者仍需對鎖定的實際binary跑`--version`與`exec --help`並把digest納fingerprint。若某版移除任一flag，backend admission fail，不准靜默換成較弱argv。
