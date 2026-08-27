# 通用 CLI 後端 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:subagent-driven-development` (recommended) or `superpowers:executing-plans` to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 【推論】以可准入的BackendSpec支援agy等其他CLI型agent，而不為每個CLI複製領域語義：固定executable digest、closed argv token template、typed event/exit grammar、明示quota/context/update capability，任何無法觀測的能力都走既有typed弱路徑。

**Architecture:** 【推論】通用CLI不是任意command runner。Definition source是immutable `CliBackendSpec`，compiler只接受封閉placeholder與protocol modes，產生`CompiledCliBackendPlan`；runtime plan經ProcessSupervisor啟動argv、以stdin送prompt、以schema/exit map正規化events。新增CLI先以自己的fake/live conformance evidence admit spec和fingerprint，才能加入backend registry。

**Tech Stack:** 【推論】CPython 3.14.7、JSON Schema、async subprocess、typed argv templates、JSONL/exit-code protocols、plan 05共用adapter suite、plan 07 quota modes、plan 11 updater endpoint、plan 12 context contract。

**Spec:** 【查證】本檔「子系統規格」，以及[第三輪adapter同址與最小檔案單位](../sol-新局-第三輪.md#22-完整目錄樹)、[第四輪quota capability與constraint要求](../sol-新局-第四輪.md)。

## Global Constraints

- 【推論】spec不接受shell string、pipeline、redirect、glob、env interpolation或command substitution；argv是literal tokens加closed placeholders。
- 【推論】allowed placeholders v1固定`{workspace}`、`{model}`、`{input_file}`、`{output_file}`、`{session_id}`；prompt預設stdin，template不能引用secret/env值。
- 【推論】executable必須resolved absolute path+SHA-256+version probe evidence；PATH lookup只在admission時做，runtime不用PATH重新解決。
- 【推論】event protocol只能`JSONL_SCHEMA`或`FINAL_STDOUT`；後者只提供started/output/exit，不宣告round/tool/usage/quota observations。
- 【推論】quota capability必填`NOT_APPLICABLE|PUSH_OBSERVED|REJECTION_ONLY|UNOBSERVABLE`，沒有UNKNOWN。PUSH_OBSERVED必須有typed JSON pointer/schema mapping；rejection不能靠自由substring。
- 【推論】pinned update只有exact target token、bounded attempts與post-version/fingerprint probe全通過才supported；`latest`/無target一律unsupported。
- 【推論】backend-native safety hook只是defense-in-depth，不能滿足system-owned constraint gate claim。

## 子系統規格

【推論】`CliBackendSpec`固定：identity/revision/executable_ref/version_probe/model policy/run argv template/input mode/event protocol/error map/quota declaration/context offer/update declaration/env allowlist/working-dir policy/capability claims/ClaimRefs。source無`ACTIVE`欄位。

【推論】JSONL mapping只接受JSON Pointer到closed target fields與enum maps；不接受embedded Python/JQ/regex。無法表示的vendor event要做專用adapter，不把arbitrary code塞進spec。

【推論】FINAL_STDOUT backend仍可被外部wall/output/process limit控制，但若manifest無usage upper bound/rate card就不能成paid dispatch；能力缺失不由adapter猜補。

## File Structure

```text
規格/語言/CliBackendSpec.schema.json           — closed CLI backend declaration language。
規格/介面/CLI事件.schema.json                  — normalized CLI JSONL mapping targets。
規格/執行/保證/後端/
├── 通用cli宣告封閉.claim.json                — no shell/unknown placeholder/arbitrary decoder。
├── 通用cli執行契約.claim.json                — common limits/events/terminal authority parity。
├── 通用cli能力誠實.claim.json                — protocol/quota/context missing stays missing。
└── 通用cli固定更新.claim.json                — exact target/convergent/post-probe only。
nova/介接/執行者後端/通用_cli/
├── 公開契約.py                               — CliBackendSpec/CompiledPlan value types。
├── 載入.py                                   — schema/ref/digest/control evidence resolution。
├── argv.py                                   — literal token compiler/placeholder substitution。
├── protocol.py                               — JSONL_SCHEMA/FINAL_STDOUT closed decoders。
├── manifest.py                               — spec+actual executable probes→BackendManifest。
├── 執行.py                                   — compiled plan→BackendEvent stream。
├── 額度.py                                   — push/rejection/unobservable/not-applicable mapping。
├── 上下文.py                                 — initial/reassert/meter capability binding。
├── 更新.py                                   — optional pinned installer endpoint adapter。
└── test_契約.py                              — language/common/protocol/capability contract suite。
驗收/後端/通用_cli/
├── fixture_agent.py                          — executable fixture with selectable modes。
├── fixtures/
│   ├── fixture-jsonl.backend.json            — fully typed JSONL example。
│   ├── fixture-final.backend.json            — final stdout limited-capability example。
│   ├── fixture-rejection.backend.json        — rejection-only quota example。
│   └── fixture-updater.backend.json          — exact-target convergent updater example。
├── 測_宣告語言.py                            — schema/argv/decoder/update admission controls。
├── 測_執行契約.py                            — shared suite for JSONL/final modes。
├── 測_能力降級.py                            — no silent upgrade across modes。
└── 測_固定更新.py                            — duplicate/crash/version/fingerprint matrix。
```

## Dependency Gate

前置計畫：05 06 07 11 12 13

【推論】必須完成plan 05–07、11–13。專用Claude/Codex plans不是前置；它們與本plan平行並證明何時該用專用parser。若在共用backend contract前做「任意CLI command」，shell/exit code會變成另一套終態與安全模型，無法跨後端一致。

---

### Task 1: 寫closed CliBackendSpec schema與loader

**Files:**
- Create: `規格/語言/CliBackendSpec.schema.json`
- Create: `規格/介面/CLI事件.schema.json`
- Create: `nova/介接/執行者後端/通用_cli/公開契約.py`
- Create: `nova/介接/執行者後端/通用_cli/載入.py`
- Create: `驗收/後端/通用_cli/fixtures/fixture-jsonl.backend.json`
- Create: `驗收/後端/通用_cli/測_宣告語言.py`
- Create: `規格/執行/保證/後端/通用cli宣告封閉.claim.json`

**Interfaces:**
- Produces: `load_cli_backend_spec(bytes, catalogs) -> CliBackendSpec`。
- Rejects: source status, unknown fields/modes, missing ClaimRefs, unpinned executable ref。

**ClaimSpec:** 【推論】`backend.generic-cli.spec.closed-and-pinned` 從紅轉綠。

**固定負控:** 【推論】command=`"agy --foo | tee x"`、executable=`agy` without digest、decoder=`python:parse()`、quota mode UNKNOWN、source ACTIVE；five admission direct red。

- [ ] **Step 1: 寫五invalid specs red**

```python
@pytest.mark.parametrize("fixture", ["shell-string", "unpinned-executable", "arbitrary-decoder", "unknown-quota", "source-active"])
def test_invalid_cli_spec_is_rejected(fixture: str) -> None:
    assert load_cli_backend_fixture(fixture).kind == "REJECTED"
```

- [ ] **Step 2: 跑tests確認loader/schema缺失**

Run: `uv run pytest -q 驗收/後端/通用_cli/測_宣告語言.py`

Expected: 【推論】FAIL。

- [ ] **Step 3: 寫closed schema/immutable refs/versioned model**

```python
@dataclass(frozen=True, slots=True)
class ExecutableRef:
    absolute_path: Path
    sha256: Sha256Ref
    version_probe_argv: tuple[str, ...]
```

- [ ] **Step 4: 跑ClaimSpec**

Run: `uv run pytest -q 驗收/後端/通用_cli/測_宣告語言.py && uv run python 工具/跑驗收.py --claim backend.generic-cli.spec.closed-and-pinned`

Expected: 【推論】PASS；five fixed controls direct red。

- [ ] **Step 5: Commit**

```bash
git add 規格/語言/CliBackendSpec.schema.json 規格/介面/CLI事件.schema.json nova/介接/執行者後端/通用_cli/公開契約.py nova/介接/執行者後端/通用_cli/載入.py 驗收/後端/通用_cli/fixtures/fixture-jsonl.backend.json 驗收/後端/通用_cli/測_宣告語言.py 規格/執行/保證/後端/通用cli宣告封閉.claim.json
git commit -m "feat: 定義封閉的通用 CLI 後端規格"
```

---

### Task 2: 編譯literal argv templates且runtime不重新PATH lookup

**Files:**
- Create: `nova/介接/執行者後端/通用_cli/argv.py`
- Create: `nova/介接/執行者後端/通用_cli/manifest.py`
- Modify: `驗收/後端/通用_cli/測_宣告語言.py`

**Interfaces:**
- Produces: `compile_argv(spec, immutable_runtime_facts) -> tuple[str,...]`。
- Produces: actual executable digest/version/help probes included in manifest fingerprint。

**ClaimSpec:** 【推論】`backend.generic-cli.argv.literal-and-resolved` 從紅轉綠。

**固定負控:** 【推論】placeholder value含`;rm`仍只能一個literal argv token、PATH中同名binary被替換、unknown `{env:SECRET}`、workspace相對逃逸；direct red/no command execution。

- [ ] **Step 1: 寫injection/PATH swap/path escape red**

```python
def test_placeholder_is_one_literal_argv_token() -> None:
    argv = compile_argv(spec_with("--model", "{model}"), facts(model="x;touch /tmp/pwn"))
    assert argv[-1] == "x;touch /tmp/pwn"
```

- [ ] **Step 2: 跑tests確認shell interpolation/PATH lookup**

Run: `uv run pytest -q 驗收/後端/通用_cli/測_宣告語言.py -k argv`

Expected: 【推論】FAIL。

- [ ] **Step 3: 寫token AST/allowlisted substitution/resolved executable verification**

```python
if hash_file(spec.executable.absolute_path) != spec.executable.sha256:
    raise BackendFingerprintChanged("EXECUTABLE_DIGEST_MISMATCH")
```

- [ ] **Step 4: 跑argv ClaimSpec**

Run: `uv run pytest -q 驗收/後端/通用_cli/測_宣告語言.py -k argv && uv run python 工具/跑驗收.py --claim backend.generic-cli.argv.literal-and-resolved`

Expected: 【推論】PASS；injected semicolon從未被shell執行。

- [ ] **Step 5: Commit**

```bash
git add nova/介接/執行者後端/通用_cli/argv.py nova/介接/執行者後端/通用_cli/manifest.py 驗收/後端/通用_cli/測_宣告語言.py
git commit -m "feat: 編譯 literal 的 CLI argv 樣板"
```

---

### Task 3: 實作JSONL_SCHEMA與FINAL_STDOUT兩種protocol

**Files:**
- Create: `nova/介接/執行者後端/通用_cli/protocol.py`
- Create: `nova/介接/執行者後端/通用_cli/執行.py`
- Create: `nova/介接/執行者後端/通用_cli/test_契約.py`
- Create: `驗收/後端/通用_cli/fixture_agent.py`
- Create: `驗收/後端/通用_cli/fixtures/fixture-final.backend.json`
- Create: `驗收/後端/通用_cli/測_執行契約.py`
- Create: `規格/執行/保證/後端/通用cli執行契約.claim.json`

**Interfaces:**
- Implements: common `ExecutorBackend.events` for both protocol modes。
- JSONL mapper: closed JSON pointers/enums; FINAL mapper: started/output/exit only。

**ClaimSpec:** 【推論】`backend.generic-cli.execution.protocol-parity` 從紅轉綠。

**固定負控:** 【推論】FINAL mode宣告tool/round/quota events、unknown JSONL dropped、exit0 self-success terminal、unbounded stdout；common suite direct red。

- [ ] **Step 1: 寫same behavioral fixtures through both modes red**

```python
@pytest.mark.parametrize("spec_name", ["fixture-jsonl", "fixture-final"])
async def test_both_modes_obey_common_backend_contract(spec_name: str) -> None:
    report = await run_common_backend_contract(build_fixture_backend(spec_name))
    assert report.accepted
```

- [ ] **Step 2: 跑shared suite確認runtime缺失**

Run: `uv run pytest -q 驗收/後端/通用_cli/測_執行契約.py`

Expected: 【推論】FAIL。

- [ ] **Step 3: 寫bounded process stream與closed mappings**

```python
decoder = JsonlSchemaDecoder(plan.event_mapping) if plan.protocol is JSONL_SCHEMA else FinalStdoutDecoder()
```

- [ ] **Step 4: 跑common/ClaimSpec**

Run: `uv run pytest -q nova/介接/執行者後端/通用_cli/test_契約.py 驗收/後端/通用_cli/測_執行契約.py -n 2 && uv run python 工具/跑驗收.py --claim backend.generic-cli.execution.protocol-parity`

Expected: 【推論】PASS；FINAL capability set是JSONL fixture真子集。

- [ ] **Step 5: Commit**

```bash
git add nova/介接/執行者後端/通用_cli/protocol.py nova/介接/執行者後端/通用_cli/執行.py nova/介接/執行者後端/通用_cli/test_契約.py 驗收/後端/通用_cli 規格/執行/保證/後端/通用cli執行契約.claim.json
git commit -m "feat: 執行帶型別的通用 CLI 協定"
```

---

### Task 4: 讓quota四種capability走唯一typed branch

**Files:**
- Create: `nova/介接/執行者後端/通用_cli/額度.py`
- Create: `驗收/後端/通用_cli/fixtures/fixture-rejection.backend.json`
- Create: `驗收/後端/通用_cli/測_能力降級.py`
- Create: `規格/執行/保證/後端/通用cli能力誠實.claim.json`

**Interfaces:**
- Produces: PUSH_OBSERVED typed observations; REJECTION_ONLY typed rejection; UNOBSERVABLE no values; NOT_APPLICABLE no provider gate。

**ClaimSpec:** 【推論】`backend.generic-cli.capabilities.no-silent-upgrade` 從紅轉綠。

**固定負控:** 【推論】自由stderr含"rate"被當typed rejection、UNOBSERVABLE產生remaining、null event把PUSH_OBSERVED降blind、NOT_APPLICABLE繞過本地budget；direct red。

- [ ] **Step 1: 寫four-mode truth table red**

```python
@pytest.mark.parametrize(("mode","allowed_outputs"), [("PUSH_OBSERVED",{"observation","rejection"}),("REJECTION_ONLY",{"rejection"}),("UNOBSERVABLE",set()),("NOT_APPLICABLE",set())])
def test_quota_mode_output_set(mode: str, allowed_outputs: set[str]) -> None:
    outputs = {item.kind for item in normalize_quota_fixture(mode)}
    assert outputs == allowed_outputs
```

- [ ] **Step 2: 跑tests確認substring/parser猜測**

Run: `uv run pytest -q 驗收/後端/通用_cli/測_能力降級.py -k quota`

Expected: 【推論】FAIL。

- [ ] **Step 3: 寫mode-dispatched typed mapping且manifest immutable**

```python
match spec.quota.mode:
    case PUSH_OBSERVED: return map_json_pointer_event(event)
    case REJECTION_ONLY: return map_exact_exit_or_json_code(event)
    case UNOBSERVABLE | NOT_APPLICABLE: return ()
```

- [ ] **Step 4: 跑resource/ClaimSpec**

Run: `uv run pytest -q 驗收/後端/通用_cli/測_能力降級.py 驗收/資源/測_盲派斷路.py && uv run python 工具/跑驗收.py --claim backend.generic-cli.capabilities.no-silent-upgrade`

Expected: 【推論】PASS；local budget reserve仍適用所有mode。

- [ ] **Step 5: Commit**

```bash
git add nova/介接/執行者後端/通用_cli/額度.py 驗收/後端/通用_cli/fixtures/fixture-rejection.backend.json 驗收/後端/通用_cli/測_能力降級.py 規格/執行/保證/後端/通用cli能力誠實.claim.json
git commit -m "feat: 綁定通用 CLI 的額度能力"
```

---

### Task 5: 綁定context meter/reassert能力而不讓CLI自行選規則

**Files:**
- Create: `nova/介接/執行者後端/通用_cli/上下文.py`
- Modify: `nova/介接/執行者後端/通用_cli/manifest.py`
- Modify: `驗收/後端/通用_cli/測_能力降級.py`

**Interfaces:**
- Consumes: already assembled InvocationEnvelope only。
- Context offer: initial delivery required; meter/reassert true only with spec evidence and protocol mapping。

**ClaimSpec:** 【推論】`backend.generic-cli.context-plan-consumer-only` 從紅轉綠。

**固定負控:** 【推論】adapter查Constraint/Knowledge registry、caller重新排序advisories、FINAL mode宣告turn reassert、meter無upper-bound proof；architecture/contract direct red或unsupported。

- [ ] **Step 1: 寫constructor/public-input與capability red**

```python
def test_generic_cli_has_no_constraint_catalog_dependency() -> None:
    assert constructor_parameters(GenericCliBackend) == {"compiled_plan","supervisor","content_store"}
```

- [ ] **Step 2: 跑tests確認adapter可能live選context**

Run: `uv run pytest -q 驗收/後端/通用_cli/測_能力降級.py -k context`

Expected: 【推論】FAIL。

- [ ] **Step 3: 寫envelope-only binding與capability evidence checks**

```python
if spec.context.reassert and spec.event_protocol.mode is not JSONL_SCHEMA:
    raise CliSpecAdmissionError("REASSERT_REQUIRES_TYPED_TURN_BOUNDARY")
```

- [ ] **Step 4: 跑context ClaimSpec**

Run: `uv run pytest -q 驗收/後端/通用_cli/測_能力降級.py && uv run python 工具/跑驗收.py --claim backend.generic-cli.context-plan-consumer-only`

Expected: 【推論】PASS；backend never sees registry/scope/priority logic。

- [ ] **Step 5: Commit**

```bash
git add nova/介接/執行者後端/通用_cli/上下文.py nova/介接/執行者後端/通用_cli/manifest.py 驗收/後端/通用_cli/測_能力降級.py
git commit -m "feat: 綁定通用 CLI 的脈絡能力"
```

---

### Task 6: 只准exact-target convergent updater

**Files:**
- Create: `nova/介接/執行者後端/通用_cli/更新.py`
- Create: `驗收/後端/通用_cli/fixtures/fixture-updater.backend.json`
- Create: `驗收/後端/通用_cli/測_固定更新.py`
- Create: `規格/執行/保證/後端/通用cli固定更新.claim.json`

**Interfaces:**
- Implements: plan 11 updater endpoint with exact `{target_version}` argv token and post-probe version/fingerprint。
- Requires: same target+key repeated converges; no target/latest disables update capability。

**ClaimSpec:** 【推論】`backend.generic-cli.update.pinned-convergent-verified` 從紅轉綠。

**固定負控:** 【推論】template缺target placeholder、接受latest、exit0不probe、same key different target、install後crash留下unverified available；direct red/quarantine。

- [ ] **Step 1: 寫admission/idempotency/crash red matrix**

```python
def test_update_template_must_contain_exact_target_once() -> None:
    assert compile_update_spec(template=("agent","update","latest")).reason == "EXACT_TARGET_REQUIRED"
```

- [ ] **Step 2: 跑tests確認optimistic updater**

Run: `uv run pytest -q 驗收/後端/通用_cli/測_固定更新.py`

Expected: 【推論】FAIL。

- [ ] **Step 3: 寫target-bound key/argv、convergent send與post-probe**

```python
key = sha256_ref(canonical_json_bytes((backend_id, target_version, request_id)))
```

- [ ] **Step 4: 跑effect/ClaimSpec**

Run: `uv run pytest -q 驗收/後端/通用_cli/測_固定更新.py 驗收/外部效果/測_後端更新.py && uv run python 工具/跑驗收.py --claim backend.generic-cli.update.pinned-convergent-verified`

Expected: 【推論】PASS；mismatch remains QUARANTINED, no old Pursuit rebase。

- [ ] **Step 5: Commit**

```bash
git add nova/介接/執行者後端/通用_cli/更新.py 驗收/後端/通用_cli/fixtures/fixture-updater.backend.json 驗收/後端/通用_cli/測_固定更新.py 規格/執行/保證/後端/通用cli固定更新.claim.json
git commit -m "feat: 支援可驗證且釘住版本的 CLI 更新"
```

---

### Task 7: 建立BackendSpec admission與named-fault matrix

**Files:**
- Modify: `nova/介接/執行者後端/通用_cli/載入.py`
- Modify: `nova/介接/執行者後端/通用_cli/test_契約.py`
- Modify: `驗收/後端/通用_cli/測_宣告語言.py`

**Interfaces:**
- Produces: `admit_backend_spec(spec_ref, executable_probe, claim_evidence) -> BackendManifestRef|Rejected`。
- Requires: all claimed capabilities' designated controls green/red before registry activation。

**ClaimSpec:** 【推論】`backend.generic-cli.admission.evidence-closed` 從紅轉綠。

**固定負控:** 【推論】predeclared faulty plans：shell runner、drop unknown event、fake quota、fake reassert、latest updater；每個由指定test殺，不能用總mutation rate或人工勾選。

- [ ] **Step 1: 寫claim/control closure與五faulty plans**

```python
FAULTY_PLANS = (ShellPlan(), DropUnknownPlan(), FabricateQuotaPlan(), FakeReassertPlan(), LatestUpdatePlan())
```

- [ ] **Step 2: 跑negative suite確認designated kills**

Run: `uv run pytest -q nova/介接/執行者後端/通用_cli/test_契約.py 驗收/後端/通用_cli -k negative`

Expected: 【推論】每個faulty plan至少一個指定direct red；actual plan全綠才overall pass。

- [ ] **Step 3: 跑完整generic CLI suite/ClaimSpecs**

Run: `uv run pytest -q nova/介接/執行者後端/通用_cli 驗收/後端/通用_cli -n 2 && uv run python 工具/跑驗收.py --prefix backend.generic-cli.`

Expected: 【推論】PASS；兩fixture runtime modes與四quota branches都有contract evidence。

- [ ] **Step 4: Commit**

```bash
git add nova/介接/執行者後端/通用_cli/載入.py nova/介接/執行者後端/通用_cli/test_契約.py 驗收/後端/通用_cli/測_宣告語言.py
git commit -m "feat: 通用 CLI 後端憑證據准入"
```

## Plan Exit Gate

- 【推論】CliBackendSpec封閉、executable pinned、argv literal，沒有shell或arbitrary parser escape。
- 【推論】JSONL與FINAL modes通過同一Execution contract，能力集合如實不同。
- 【推論】quota四modes不互相偷降/升級，結構性unobservable只走blind-bounded。
- 【推論】context adapter只消費assembled envelope；reassert/meter無證據則unsupported。
- 【推論】exact-target updater重送收斂/verify，無target就不advertise。
- 【推論】五個named faulty plans各由指定test殺掉。
- 【推論】`uv run pytest -q nova/介接/執行者後端/通用_cli 驗收/後端/通用_cli -n 2` 與本plan ClaimSpecs綠。

## Execution Handoff

【推論】要接agy時，不改通用runtime：新增一份owner-reviewed CliBackendSpec、agy executable probe evidence與該spec的contract test instance。若agy事件語義無法用closed JSON pointer/enum map表達，就建立專用`agy_cli/`adapter；不准把Python escape塞回spec。
