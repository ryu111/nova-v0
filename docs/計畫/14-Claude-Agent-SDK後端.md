# Claude Agent SDK 後端 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:subagent-driven-development` (recommended) or `superpowers:executing-plans` to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 【推論】把 Claude Agent SDK 接成與重播器相同的 ExecutorBackend：manifest/fingerprint完整、SDK typed events正規化、工具授權／結構輸出／delegation契約不降級、外部封套仍掌握限額與終態、RateLimitEvent逐bucket寫入資源證據、上下文能力不誇大。

**Architecture:** 【推論】adapter只負責SDK I/O與typed normalization，不讀判準registry、不決定retry/terminal/budget/quota eligibility。`manifest.py`由實際probe產生immutable capability fingerprint；`執行.py`把SDK messages轉BackendEvent；`額度.py`把每次push RateLimitEvent轉QuotaObservation；`上下文.py`只承諾可由trusted observer驗證的INVOCATION_START delivery，沒有turn-boundary reassert時明示unsupported。

**Tech Stack:** 【推論】CPython 3.14.7、`claude-agent-sdk` pinned dependency、asyncio、plan 05 backend contract suite、plan 07 quota types、plan 12 context adapter contract、CAS raw evidence。

**Spec:** 【查證】本檔「子系統規格」；Claude額度事件欄位依[控制端第一手查證](../控制端審查.md#一我查證後推翻的額度是可觀測的)，其列出`RateLimitEvent/RateLimitInfo`的status、utilization、resets_at、rate_limit_type與overage欄位。

## Global Constraints

- 【推論】SDK/CLI/model/protocol任一可觀測版本改變就改fingerprint；在途Pursuit不原地接受新fingerprint。
- 【推論】SDK事件中的result/success只是BackendEvent；ExecutionEnvelope仍依process/SDK completion evidence與外部counters寫terminal。
- 【推論】RateLimitEvent是execution期間push observation，不是query端點；冷啟動保持NEVER_OBSERVED並走有界probe。
- 【推論】`rate_limit_type`每個值各建QuotaBucket；five-hour、seven-day、model-specific是included channel ALL_OF，overage是預設不允許的替代spend channel。
- 【推論】`raw`完整dict只進CAS evidence，不可越過typed parser直接改eligibility。
- 【推論】adapter不掛載sealed criterion、不取得ConstraintSpec registry；只收InvocationEnvelope與workspace projection。
- 【推論】v1 manifest明示`update=UNSUPPORTED_UPDATE`，除非未來exact-target installer另通過plan 11契約；不得把「更新到最新」冒充pinned update。
- 【推論】v1 `setting_sources=[]`；任何非空 source 都必須 exact allowlist、內容定址，且 filesystem settings、effective hooks/tools/MCP servers/agent definitions/permission mode 的 catalog digest 全部納入 fingerprint。
- 【推論】`allowed_tools/disallowed_tools` 是 static filter，`can_use_tool/PreToolUse` 映射 `PRE_TOOL_DECISION`；它只攔 SDK tool path，不宣稱能攔 direct syscall/network。
- 【推論】SDK root `usage` 不得冒充代理樹總額；adapter優先保存 provider tree-total／per-model evidence及scope，證據不足回 `UNKNOWN`。

## File Structure

```text
nova/介接/執行者後端/claude_agent_sdk/
├── manifest.py                               — SDK/CLI/model/protocol/context/quota fingerprint probe。
├── 執行.py                                   — SDK session/events→BackendEvent stream。
├── 額度.py                                   — RateLimitEvent→per-bucket QuotaObservation。
├── 上下文.py                                 — initial policy segment binding/conservative meter offer。
├── 錯誤.py                                   — SDK exceptions→closed backend fault taxonomy。
└── test_契約.py                              — shared contract suite plus Claude-specific controls。
規格/執行/保證/後端/
├── claude-manifest完整.claim.json             — no unknown/missing fingerprint capability。
├── claude執行契約.claim.json                 — common request/event/cancel/limit parity。
├── claude上下文能力誠實.claim.json           — initial delivery only; no false reassert/update。
└── claude不讀判準.claim.json                 — invocation projection excludes criterion refs。
規格/資源/保證/claude額度逐bucket.claim.json  — typed rate-limit mapping/topology/raw isolation。
驗收/後端/claude_agent_sdk/
├── 假SDK.py                                  — deterministic typed SDK event/session fixture。
├── 測_manifest.py                            — fingerprint/capability/version drift。
├── 測_執行.py                               — event ordering/cancel/error/output caps。
├── 測_額度.py                               — all rate_limit_type/overage/boundary values。
├── 測_上下文.py                             — exact initial bytes/meter/reassert unsupported。
└── 測_投影.py                               — sealed paths/env/registry absent。
```

## Dependency Gate

前置計畫：01B 05 06 07 12 13

【推論】必須完成plan 01B、05–07、12、13；plan 11提供update capability語義但本adapter v1不提供它。重播器共用suite是唯一adapter contract，不另抄一份Claude版。01B 的 pinned static probe 未綠或 exact fingerprint 沒有有效 live evidence時，Claude只能 `NOT_ADMITTED`。

---

### Task 1: 釘SDK依賴並建立完整capability fingerprint

**Files:**
- Modify: `pyproject.toml`
- Modify: `uv.lock`
- Create: `nova/介接/執行者後端/claude_agent_sdk/manifest.py`
- Create: `驗收/後端/claude_agent_sdk/假SDK.py`
- Create: `驗收/後端/claude_agent_sdk/測_manifest.py`
- Create: `規格/執行/保證/後端/claude-manifest完整.claim.json`

**Interfaces:**
- Produces: `probe_manifest(sdk_runtime) -> BackendManifest`。
- Fingerprint inputs: SDK distribution version、underlying CLI/runtime version、model id/catalog digest、event protocol revision、adapter revision、quota/context/update capability values。

**ClaimSpec:** 【推論】`backend.claude-agent-sdk.manifest.fingerprint-complete` 從紅轉綠。

**固定負控:** 【推論】改SDK version/CLI version/model id任一項卻fingerprint不變，或capability留UNKNOWN；manifest admission direct red。

- [ ] **Step 1: 寫one-field-at-a-time fingerprint sensitivity red**

```python
@pytest.mark.parametrize("field", ["sdk_version", "cli_version", "model_id", "protocol_revision"])
def test_fingerprint_changes_with_runtime_fact(field: str) -> None:
    baseline = admitted_manifest_fixture()
    changed = change_runtime_fact(baseline, field)
    assert capability_fingerprint(changed) != capability_fingerprint(baseline)
```

- [ ] **Step 2: 跑tests確認manifest缺失**

Run: `uv run pytest -q 驗收/後端/claude_agent_sdk/測_manifest.py`

Expected: 【推論】FAIL。

- [ ] **Step 3: 寫probe/canonical manifest且無UNKNOWN capability**

```python
fingerprint = sha256_ref(canonical_json_bytes({"sdk":sdk_version,"cli":cli_version,"model":model_id,"protocol":EVENT_PROTOCOL_REVISION,"adapter":ADAPTER_REVISION}))
```

- [ ] **Step 4: 鎖依賴並跑ClaimSpec**

Run: `uv lock && uv run pytest -q 驗收/後端/claude_agent_sdk/測_manifest.py && uv run python 工具/跑驗收.py --claim backend.claude-agent-sdk.manifest.fingerprint-complete`

Expected: 【推論】PASS；missing/UNKNOWN/fingerprint-insensitive controls direct red。

- [ ] **Step 5: Commit**

```bash
git add pyproject.toml uv.lock nova/介接/執行者後端/claude_agent_sdk/manifest.py 驗收/後端/claude_agent_sdk/假SDK.py 驗收/後端/claude_agent_sdk/測_manifest.py 規格/執行/保證/後端/claude-manifest完整.claim.json
git commit -m "feat: fingerprint Claude Agent SDK backend"
```

---

### Task 2: 將SDK typed stream正規化成共用BackendEvent

**Files:**
- Create: `nova/介接/執行者後端/claude_agent_sdk/執行.py`
- Create: `nova/介接/執行者後端/claude_agent_sdk/錯誤.py`
- Create: `nova/介接/執行者後端/claude_agent_sdk/test_契約.py`
- Create: `驗收/後端/claude_agent_sdk/測_執行.py`
- Create: `規格/執行/保證/後端/claude執行契約.claim.json`

**Interfaces:**
- Implements: `ExecutorBackend.events(ExecutionRequest) -> AsyncIterator[BackendEvent]`。
- Maps: session started/message/tool intent/tool result/usage/result/error to closed event kinds。

**ClaimSpec:** 【推論】`backend.claude-agent-sdk.execution.protocol-parity` 從紅轉綠。

**固定負控:** 【推論】未知SDK message被drop、SDK result success直接寫SUCCEEDED、自由exception string冒充typed fault、event在STARTED前出現；common suite direct red。

- [ ] **Step 1: 寫full typed fixture stream與unknown-event red**

```python
async def test_unknown_sdk_message_is_protocol_fault_not_dropped() -> None:
    events = await collect(adapter(fake_sdk(events=[UnknownSdkMessage()])))
    assert events[-1].kind is BackendEventKind.PROTOCOL_FAULT
```

- [ ] **Step 2: 跑shared suite確認adapter缺失**

Run: `uv run pytest -q nova/介接/執行者後端/claude_agent_sdk/test_契約.py 驗收/後端/claude_agent_sdk/測_執行.py`

Expected: 【推論】FAIL。

- [ ] **Step 3: 寫exhaustive typed dispatcher與error union**

```python
match sdk_event:
    case SdkAssistantMessage(text=text): yield MessageObserved(text=text)
    case SdkToolUse(tool_name=name, input_payload=payload): yield ToolCallObserved(tool_name=name, input_payload=payload)
    case SdkResult(stop_reason=reason, usage=usage): yield BackendCompletionObserved(stop_reason=reason, usage=usage)
    case _: yield ProtocolFaultObserved(code="UNKNOWN_SDK_EVENT")
```

- [ ] **Step 4: 跑shared contract/ClaimSpec**

Run: `uv run pytest -q nova/介接/執行者後端/claude_agent_sdk/test_契約.py 驗收/後端/claude_agent_sdk/測_執行.py -n 2 && uv run python 工具/跑驗收.py --claim backend.claude-agent-sdk.execution.protocol-parity`

Expected: 【推論】PASS；adapter沒有ExecutionTerminal writer。

- [ ] **Step 5: Commit**

```bash
git add nova/介接/執行者後端/claude_agent_sdk 驗收/後端/claude_agent_sdk/測_執行.py 規格/執行/保證/後端/claude執行契約.claim.json
git commit -m "feat: adapt Claude SDK execution events"
```

---

### Task 3: 讓外部封套可取消SDK且限額仍由父層掌握

**Files:**
- Modify: `nova/介接/執行者後端/claude_agent_sdk/執行.py`
- Modify: `驗收/後端/claude_agent_sdk/假SDK.py`
- Modify: `驗收/後端/claude_agent_sdk/測_執行.py`

**Interfaces:**
- Consumes: cancellation token from ExecutionEnvelope; closes SDK session and lets process supervisor escalate。
- Emits: observed usage/round/tool counts only; cannot alter request limits。

**ClaimSpec:** 【推論】`backend.claude-agent-sdk.external-limit-control` 從紅轉綠。

**固定負控:** 【推論】fake SDK ignorescancel/returns altered limits/keepschild task alive；wall deadline仍terminal且所有tasks/processes終止，request limit digest不變。

- [ ] **Step 1: 寫ignore-cancel/limit-tamper red**

```python
async def test_sdk_cannot_extend_wall_deadline() -> None:
    result = await run_enveloped(fake_sdk(ignore_cancel=True), limits=limits(wall_ms=200))
    assert result.terminal is ExecutionTerminal.TIMED_OUT
```

- [ ] **Step 2: 跑tests確認SDK task可能存活**

Run: `uv run pytest -q 驗收/後端/claude_agent_sdk/測_執行.py -k 'cancel or limit'`

Expected: 【推論】FAIL。

- [ ] **Step 3: 寫structured task group cleanup/cancel forwarding**

```python
async with asyncio.TaskGroup() as group:
    session_task = group.create_task(run_sdk_session(request))
    group.create_task(cancel_session_when_requested(session_task, cancellation))
```

- [ ] **Step 4: 跑外部limit ClaimSpec與leak probe**

Run: `uv run pytest -q 驗收/後端/claude_agent_sdk/測_執行.py -k 'cancel or limit' && uv run python 工具/跑驗收.py --claim backend.claude-agent-sdk.external-limit-control`

Expected: 【推論】PASS；active task count回baseline。

- [ ] **Step 5: Commit**

```bash
git add nova/介接/執行者後端/claude_agent_sdk/執行.py 驗收/後端/claude_agent_sdk/假SDK.py 驗收/後端/claude_agent_sdk/測_執行.py
git commit -m "feat: cancel Claude SDK through execution envelope"
```

---

### Task 4: 將RateLimitEvent逐bucket寫成誠實quota evidence

**Files:**
- Create: `nova/介接/執行者後端/claude_agent_sdk/額度.py`
- Create: `驗收/後端/claude_agent_sdk/測_額度.py`
- Create: `規格/資源/保證/claude額度逐bucket.claim.json`

**Interfaces:**
- Produces: `parse_rate_limit_event(event, observed_at, session_id) -> tuple[QuotaObservation, ...]`。
- Maps status allowed/warning/rejected; utilization Decimal 0..1; reset unix time; overage typed fields。

**ClaimSpec:** 【推論】`resource.provider-quota.claude-rate-limit-event-per-bucket` 從紅轉綠。

**固定負控:** 【推論】把five_hour/seven_day合成單一backend state、把utilization換算假absolute remaining、reset後推100%剩餘、raw field直接覆寫typed status；全部direct red。

- [ ] **Step 1: 寫all documented rate_limit_type/status/overage fixtures red**

```python
def test_five_hour_and_seven_day_remain_separate_buckets() -> None:
    observations = parse_many([rate_event("five_hour", .2), rate_event("seven_day", .8)])
    assert {o.bucket_id for o in observations} == {"five_hour", "seven_day"}
```

- [ ] **Step 2: 跑tests確認parser缺失**

Run: `uv run pytest -q 驗收/後端/claude_agent_sdk/測_額度.py`

Expected: 【推論】FAIL。

- [ ] **Step 3: 寫typed mapping、raw CAS evidence與topology fragment**

```python
return QuotaObservation(bucket_id=BucketId(info.rate_limit_type), metric_kind=MetricKind.FRACTION_USED, utilization=Decimal(str(info.utilization)), provider_status=map_status(info.status), resets_at=from_unix(info.resets_at), source_event_ref=raw_ref)
```

- [ ] **Step 4: 跑quota five-state/topology/ClaimSpec**

Run: `uv run pytest -q 驗收/後端/claude_agent_sdk/測_額度.py 驗收/資源/測_供應商額度五態.py 驗收/資源/測_額度拓撲.py && uv run python 工具/跑驗收.py --claim resource.provider-quota.claude-rate-limit-event-per-bucket`

Expected: 【推論】PASS；event missing後仍cold/stale semantics，adapter不fabricate query response。

- [ ] **Step 5: Commit**

```bash
git add nova/介接/執行者後端/claude_agent_sdk/額度.py 驗收/後端/claude_agent_sdk/測_額度.py 規格/資源/保證/claude額度逐bucket.claim.json
git commit -m "feat: observe Claude quota per bucket"
```

---

### Task 5: 誠實宣告初始上下文、meter與不支援重掛/更新

**Files:**
- Create: `nova/介接/執行者後端/claude_agent_sdk/上下文.py`
- Modify: `nova/介接/執行者後端/claude_agent_sdk/manifest.py`
- Create: `驗收/後端/claude_agent_sdk/測_上下文.py`
- Create: `規格/執行/保證/後端/claude上下文能力誠實.claim.json`

**Interfaces:**
- Produces: initial policy segment exact bytes to SDK configuration。
- Offers: `INVOCATION_START`; offers conservative meter only with pinned nonempty-byte tokenizer/capacity evidence; does not offer `TURN_BOUNDARY_CONTROL`, `CONTEXT_SEGMENT_REASSERTION`, or pinned update。

**ClaimSpec:** 【推論】`backend.claude-agent-sdk.context-capabilities-honest` 從紅轉綠。

**固定負控:** 【推論】只在first message注入卻宣告reassert、opaque tokenizer卻用平均tokens估算、`latest` updater宣告pinned、SDK把policy text放可被history compaction改寫區；contract direct red/unsupported。

- [ ] **Step 1: 寫exact outbound bytes/capability-offer red**

```python
def test_manifest_does_not_claim_turn_reassertion() -> None:
    assert Capability.CONTEXT_SEGMENT_REASSERTION not in probe_manifest(fake_sdk()).capabilities
```

- [ ] **Step 2: 跑tests確認optimistic capabilities**

Run: `uv run pytest -q 驗收/後端/claude_agent_sdk/測_上下文.py`

Expected: 【推論】FAIL。

- [ ] **Step 3: 寫machine-owned initial segment與meter evidence gate**

```python
def context_offer(probe: SdkProbe) -> ContextOffer:
    meter = Utf8ByteTokenUpperBoundMeter(probe.capacity) if probe.nonempty_byte_tokenization_proven else None
    return ContextOffer(invocation_start=True, meter=meter, turn_reassert=False)
```

- [ ] **Step 4: 跑context contract/ClaimSpec**

Run: `uv run pytest -q 驗收/後端/claude_agent_sdk/測_上下文.py 驗收/約束/test_壓縮重注入.py && uv run python 工具/跑驗收.py --claim backend.claude-agent-sdk.context-capabilities-honest`

Expected: 【推論】PASS；無meter evidence時required advisory dispatch typed unsupported，不猜。

- [ ] **Step 5: Commit**

```bash
git add nova/介接/執行者後端/claude_agent_sdk/上下文.py nova/介接/執行者後端/claude_agent_sdk/manifest.py 驗收/後端/claude_agent_sdk/測_上下文.py 規格/執行/保證/後端/claude上下文能力誠實.claim.json
git commit -m "feat: declare Claude context capabilities honestly"
```

---

### Task 6: 證明candidate projection不含判準並跑完整adapter matrix

**Files:**
- Create: `驗收/後端/claude_agent_sdk/測_投影.py`
- Create: `規格/執行/保證/後端/claude不讀判準.claim.json`
- Modify: `nova/介接/執行者後端/claude_agent_sdk/test_契約.py`

**Interfaces:**
- Consumes: InvocationEnvelope/workspace projection only。
- Forbids: CriterionDefinition/CaseRef/Constraint registry/authority repository imports or paths。

**ClaimSpec:** 【推論】`backend.claude-agent-sdk.projection-no-criterion-content` 從紅轉綠。

**固定負控:** 【推論】sealed canary出現在SDK options/env/workspace/argv、adapter import Knowledge/Criterion registry、raw quota event含expected test data被拼prompt；direct red。

- [ ] **Step 1: 寫visible-bytes/import graph red**

```python
def test_sdk_invocation_contains_no_sealed_canary() -> None:
    invocation = capture_sdk_invocation(two_pool_fixture())
    assert SEALED_CANARY.encode() not in invocation.all_visible_bytes
```

- [ ] **Step 2: 跑projection tests確認leak fixture有牙**

Run: `uv run pytest -q 驗收/後端/claude_agent_sdk/測_投影.py`

Expected: 【推論】FAIL on intentionally leaky adapter subject。

- [ ] **Step 3: 收窄adapter constructor/inputs與architecture rule**

```python
class ClaudeAgentSdkBackend:
    def __init__(self, sdk_factory: SdkFactory, manifest: BackendManifest) -> None:
        self._sdk_factory = sdk_factory
        self.manifest = manifest
```

- [ ] **Step 4: 跑完整shared/Claude/resource/context/ClaimSpecs**

Run: `uv run pytest -q nova/介接/執行者後端/claude_agent_sdk 驗收/後端/claude_agent_sdk -n 2 && uv run python 工具/跑驗收.py --prefix backend.claude-agent-sdk. --claim resource.provider-quota.claude-rate-limit-event-per-bucket`

Expected: 【推論】PASS；all shared backend cases與Claude-specific controls綠。

- [ ] **Step 5: Commit**

```bash
git add 驗收/後端/claude_agent_sdk/測_投影.py 規格/執行/保證/後端/claude不讀判準.claim.json nova/介接/執行者後端/claude_agent_sdk/test_契約.py
git commit -m "test: verify Claude adapter isolation and parity"
```

---

### Task 7: 映射 SDK 工具、輸出、代理成本並封閉 ambient settings

**Files:**
- Modify: `nova/介接/執行者後端/claude_agent_sdk/manifest.py`
- Modify: `nova/介接/執行者後端/claude_agent_sdk/執行.py`
- Create: `nova/介接/執行者後端/claude_agent_sdk/工具.py`
- Create: `nova/介接/執行者後端/claude_agent_sdk/結構輸出.py`
- Create: `nova/介接/執行者後端/claude_agent_sdk/成本.py`
- Modify: `驗收/後端/claude_agent_sdk/假SDK.py`
- Create: `驗收/後端/claude_agent_sdk/測_工具輸出與成本.py`
- Create: `規格/執行/保證/後端/claude工具輸出契約.claim.json`
- Create: `規格/資源/保證/claude代理樹成本完整.claim.json`
- Modify: `驗收/資源/測_代理樹成本.py`

**Interfaces:**
- Maps: plan 01B semantic policies to exact pinned SDK `allowed_tools/disallowed_tools`、`can_use_tool/PreToolUse`、`output_format`（或 pinned 版本明示的等價 structured-output option）and agent definitions。
- Fingerprints: empty-or-content-addressed setting sources plus effective settings/hooks/tools/MCP/agents/permission catalog。
- Emits: tree-total provider cost/per-model usage evidence with honest scope; root usage remains ROOT_ONLY。

**ClaimSpec:** 【推論】`backend.claude-agent-sdk.tool-output-contract` 與 `resource.cost.claude-delegation-tree-complete` 從紅轉綠。

**固定負控:** 【推論】`bypassPermissions` 路徑略過 deny callback、malformed structured output被當成功、ambient project setting改變但fingerprint不變、root 1/subagent 4/tree total 5 被核銷成1；各自 direct red。

- [ ] **Step 1: 寫 deny invocation counter、schema、ambient one-field digest與1+4=5 red**
- [ ] **Step 2: 跑 `uv run pytest -q 驗收/後端/claude_agent_sdk/測_工具輸出與成本.py 驗收/資源/測_代理樹成本.py`**

Expected: 【推論】FAIL；SDK options 尚未映射 capability policies、ambient catalog未封閉、usage仍可能少算subagent。

- [ ] **Step 3: 寫 exact option/hook mapping、output validator、settings closure與scoped cost evidence**
- [ ] **Step 4: 跑 plan 01B shared contract、Claude suite、resource cost ClaimSpecs，確認 PASS**
- [ ] **Step 5: Commit**

```bash
git add nova/介接/執行者後端/claude_agent_sdk 驗收/後端/claude_agent_sdk/假SDK.py 驗收/後端/claude_agent_sdk/測_工具輸出與成本.py 驗收/資源/測_代理樹成本.py 規格/執行/保證/後端/claude工具輸出契約.claim.json 規格/資源/保證/claude代理樹成本完整.claim.json
git commit -m "feat: map Claude SDK capability and tree cost contracts"
```

## Plan Exit Gate

- 【推論】manifest fingerprint對SDK/CLI/model/protocol敏感且無UNKNOWN capability。
- 【推論】SDK typed events通過重播器同一contract；adapter沒有terminal/budget/verdict寫權。
- 【推論】RateLimitEvent逐bucket/metric/status/topology保存，冷啟動/rollover不造remaining。
- 【推論】initial context delivery可驗；reassert/update/meter能力不足時誠實unsupported。
- 【推論】candidate-visible projection不含sealed criterion或registry。
- 【推論】SDK tool deny與structured output通過共用能力契約；ambient settings封閉並進fingerprint，代理樹成本不遺漏。
- 【推論】`uv run pytest -q nova/介接/執行者後端/claude_agent_sdk 驗收/後端/claude_agent_sdk -n 2` 與本plan ClaimSpecs綠。

## Execution Handoff

【推論】實作者不得用live付費SDK跑unit suite；所有protocol/quota/error cases先由假SDK決定性重播，另設明示opt-in smoke test但不作CI必要條件。manifest/context capability只有probe evidence成立才true，不以SDK品牌猜能力。
