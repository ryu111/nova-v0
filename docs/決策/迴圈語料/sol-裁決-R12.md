codex
我會逐行檢查 R12-00 的自測封裝與實際接線；R12-02 涉及 Codex 現行能力，我會依 `openai-docs` 技能只查官方文件，確認「無 pre-tool callback」是已證明的否定，還是尚未找到能力的暫定觀測。其餘兩條按現有計畫證據裁決。
exec
/bin/zsh -lc "sed -n '1,260p' /Users/sbu/.codex/skills/.system/openai-docs/SKILL.md; sed -n '1,220p' /private/tmp/fable-R12-mock/fable-R12-複驗器.diff; rg -n -C 4 'PRE_TOOL_DECISION|ask-for-approval|no-criterion|Task 8|malformed-sdk-payload' /private/tmp/fable-R12-mock/docs/計畫/{14-Claude-Agent-SDK後端.md,15-Codex-CLI後端.md}" in /Users/sbu/nova
 succeeded in 0ms:
---
name: "openai-docs"
description: "Use for Codex models/pricing, scheduled tasks, skills, settings, setup, troubleshooting, customization, automations, and self-knowledge—including 'you,' 'your,' 'this app,' or 'this coding agent' when they refer to Codex—and for OpenAI APIs/products and ChatGPT Work. Also use for model choice/migration, prompting, SDKs, Responses, Realtime, agents, evals, and Chat/Work/Codex comparisons. Do not use for generic app/software tasks that merely mention Codex."
metadata:
  short-description: "Codex models/pricing, scheduled tasks, skills, settings, setup, troubleshooting, and self-knowledge; OpenAI APIs and ChatGPT Work. 'You'/'this app' means Codex only."
---

# OpenAI Docs

Provide current, cited OpenAI product, API, model, and Codex guidance. Read zero or one primary reference.

**First substantive action:** Search the user's exact requested official OpenAI documentation topic and any explicitly named model using a concise, topic-specific query of 2-6 essential terms. When an already-available direct official documentation search and page-retrieval capability is present, use it first: search, then fetch or open the matching official page before general web search. Otherwise, immediately use official-domain web search, then actually open or fetch the relevant official page. Complete this source order before reading a reference, inspecting local or repository files, running a Codex manual or model resolver, drafting a plan, or answering from memory. Use the actual fetched page, not a search snippet or an unopened link. If one official search or page does not establish the answer, search another appropriate official domain and actually open or fetch the result. Preserve the exact requested model; never substitute a newer model.

**Only exception:** An explicitly requested, genuinely broad, cross-topic Codex setup, orientation, or system-map synthesis may use the manual first when shell execution and an allowed temporary cache are available. A specific Codex feature, setting, command, error, model, or requested citation remains docs-first. Mixed Chat/Work/Codex comparisons are official documentation questions, not manual-first Codex requests.

For generic software tasks, answer the software task directly. OpenAI implementation, debugging, SDK, API, prompting, agent, and eval requests are not generic.

For a straightforward factual or citation-only request, follow the source order and do not read a route reference. This includes straightforward API facts, ChatGPT Work or mixed Chat/Work/Codex comparisons, model tiers, aliases, Pro mode, reasoning settings, factual migration baselines, and narrow Codex facts. Prioritize `learn.chatgpt.com` for ChatGPT Work.

## Choose one primary route

Use the first matching route, and read its reference only when the requested task needs that specialized workflow:

- **Explicitly requested local documentation integration:** Read [integration guidance](references/mcp-diagnostics.md) only when the user explicitly requests that local integration.
- **Model migration, upgrades, or model-specific prompting:** Read [model-migration.md](references/model-migration.md) for actual migration planning, implementation, dynamic target resolution, or prompt changes. Preserve an explicitly requested target.
- **Model selection and comparisons:** Read [model-selection.md](references/model-selection.md) only when nuanced current, latest, default, cost, latency, quality, or modality tradeoffs need more guidance. Do not run a migration resolver for selection alone.
- **Product, API, ChatGPT Work, and mixed Chat/Work/Codex documentation:** Read [official-docs.md](references/official-docs.md) only when fetched official pages leave source selection, API schemas, or the requested implementation unresolved. This route is not manual-first.
- **Explicitly broad Codex setup, orientation, or cross-topic synthesis:** Read [codex-self-knowledge.md](references/codex-self-knowledge.md) when the eligible Codex manual or deeper Codex procedures are needed.

Read at most one primary reference. Do not open every route, bundled model guide, or helper script. Read a supporting reference or run a helper only when the chosen workflow demonstrably needs it.

## Source and execution boundaries

- Search, open, fetch, and cite only `developers.openai.com`, `platform.openai.com`, and `learn.chatgpt.com`. Cite the page that supports the claim. State uncertainty when official sources do not establish pricing, availability, account access, limits, or behavior.
- Preserve an explicitly requested model for selection, migration, and prompting. Resolve an unspecified latest or current migration target only after searching and fetching current official guidance.
- Use `references/latest-model.md` only as a disclosed fallback after current official model guidance does not answer the question. Read `references/upgrading-to-gpt-5p6-sol.md` only for an actual, requested GPT-5.6-family migration; read `references/prompting-guide.md` only for requested prompting work.
- Before building, running, editing, debugging, or testing an API-backed app or tool, use `openai-platform-api-key` first when available. Documentation, conceptual examples, model selection, and read-only guidance do not require an API key.
- Say "OpenAI Docs" or "official OpenAI documentation" in user-facing answers. Keep exact official citations and examples concise.
--- B/計畫複驗.py	2026-08-28 02:33:44
+++ 草稿/計畫複驗.py	2026-08-28 02:38:18
@@ -283,7 +283,7 @@
 
 
 BINDING_ID白名單 = frozenset({'execution-envelope.reference', 'execution-envelope.production'})
-未遷移基線 = 131  # R4-01 給 09 Task 4、R4-02 給 05 Task 7 各補落點行後自 133 減二；新開 task 全帶落點行不計入
+未遷移基線 = 130  # R12-01 給 12 Task 9 補落點行後自 131 減一  # R4-01 給 09 Task 4、R4-02 給 05 Task 7 各補落點行後自 133 減二；新開 task 全帶落點行不計入
 ID樣式 = re.compile(r'^[a-z][a-z0-9]*(?:[.-][a-z0-9]+)+$')
 
 
@@ -423,7 +423,36 @@
     return 總
 
 
+def 自測():
+    """對 docs/計畫複驗自測/<情境>/ 逐一跑本執法器，斷言非零且輸出含 預期.txt 的字串。
+
+    存在理由（R11 實測）：真撞號修好之後，「執法器抓得到撞號」就只剩程式碼、沒有長期
+    牙齒——負控 fixture 不能只活在暫存目錄。fixture 只保證目標訊息出現；
+    其他不變式在最小 fixture 上本來就會紅（如 I10 基線），不計。"""
+    import subprocess
+    根目錄 = os.path.dirname(os.path.abspath(__file__))
+    自測根 = os.path.join(根目錄, '計畫複驗自測')
+    情境們 = sorted(d for d in glob.glob(os.path.join(自測根, '*')) if os.path.isdir(d))
+    if not 情境們:
+        print('自測：找不到任何情境目錄', file=sys.stderr); return 2
+    壞 = 0
+    for 情境 in 情境們:
+        預期 = open(os.path.join(情境, '預期.txt'), encoding='utf-8').read().strip()
+        跑 = subprocess.run([sys.executable, os.path.abspath(__file__), 情境],
+                            capture_output=True, text=True)
+        中 = 預期 in (跑.stdout + 跑.stderr)
+        if 跑.returncode == 0 or not 中:
+            壞 += 1
+            print(f'自測 ✗ {os.path.basename(情境)}：exit={跑.returncode}，'
+                  f'預期字串{"有" if 中 else "沒"}出現')
+        else:
+            print(f'自測 ✓ {os.path.basename(情境)}：非零且含「{預期}」')
+    return 1 if 壞 else 0
+
+
 def main():
+    if sys.argv[1:] == ['--自測']:
+        return 自測()
     檔 = 計畫檔()
     if not 檔:
         print('找不到計畫檔', file=sys.stderr); return 2
--- /dev/null	2026-08-28 02:38:53
+++ 計畫複驗自測/撞號/01-範例.md	2026-08-28 02:38:18
@@ -0,0 +1,27 @@
+# 範例 Implementation Plan
+
+前置計畫：無
+
+### Task 1: 第一格
+
+**ClaimSpec:** 【推論】`example.first` 從紅轉綠。
+
+**固定負控:** 【推論】示例。
+
+Expected: 【推論】FAIL。
+
+```bash
+git commit -m "feat: 第一格"
+```
+
+### Task 1: 撞號的第二格
+
+**ClaimSpec:** 【推論】`example.second` 從紅轉綠。
+
+**固定負控:** 【推論】示例。
+
+Expected: 【推論】FAIL。
+
+```bash
+git commit -m "feat: 第二格"
+```
--- /dev/null	2026-08-28 02:38:53
+++ 計畫複驗自測/撞號/預期.txt	2026-08-28 02:38:18
@@ -0,0 +1 @@
+I6 task 標題序號與位置不符
\ No newline at end of file
/private/tmp/fable-R12-mock/docs/計畫/14-Claude-Agent-SDK後端.md-19-- 【推論】`raw`完整dict只進CAS evidence，不可越過typed parser直接改eligibility。
/private/tmp/fable-R12-mock/docs/計畫/14-Claude-Agent-SDK後端.md-20-- 【推論】adapter不掛載sealed criterion、不取得ConstraintSpec registry；只收InvocationEnvelope與workspace projection。
/private/tmp/fable-R12-mock/docs/計畫/14-Claude-Agent-SDK後端.md-21-- 【推論】v1 manifest明示`update=UNSUPPORTED_UPDATE`，除非未來exact-target installer另通過plan 11契約；不得把「更新到最新」冒充pinned update。
/private/tmp/fable-R12-mock/docs/計畫/14-Claude-Agent-SDK後端.md-22-- 【推論】v1 `setting_sources=[]`；任何非空 source 都必須 exact allowlist、內容定址，且 filesystem settings、effective hooks/tools/MCP servers/agent definitions/permission mode 的 catalog digest 全部納入 fingerprint。
/private/tmp/fable-R12-mock/docs/計畫/14-Claude-Agent-SDK後端.md:23:- 【推論】`allowed_tools/disallowed_tools` 是 static filter，`can_use_tool/PreToolUse` 映射 `PRE_TOOL_DECISION`；它只攔 SDK tool path，不宣稱能攔 direct syscall/network。
/private/tmp/fable-R12-mock/docs/計畫/14-Claude-Agent-SDK後端.md-24-- 【推論】SDK root `usage` 不得冒充代理樹總額；adapter優先保存 provider tree-total／per-model evidence及scope，證據不足回 `UNKNOWN`。
/private/tmp/fable-R12-mock/docs/計畫/14-Claude-Agent-SDK後端.md-25-
/private/tmp/fable-R12-mock/docs/計畫/14-Claude-Agent-SDK後端.md-26-## File Structure
/private/tmp/fable-R12-mock/docs/計畫/14-Claude-Agent-SDK後端.md-27-
--
/private/tmp/fable-R12-mock/docs/計畫/14-Claude-Agent-SDK後端.md-126-
/private/tmp/fable-R12-mock/docs/計畫/14-Claude-Agent-SDK後端.md-127-**ClaimSpec:** 【推論】`backend.claude-agent-sdk.execution.protocol-parity` 從紅轉綠。
/private/tmp/fable-R12-mock/docs/計畫/14-Claude-Agent-SDK後端.md-128-
/private/tmp/fable-R12-mock/docs/計畫/14-Claude-Agent-SDK後端.md-129-**固定負控:** 【推論】未知SDK message被drop、SDK result success直接寫SUCCEEDED、自由exception string冒充typed fault、event在STARTED前出現；common suite direct red。
/private/tmp/fable-R12-mock/docs/計畫/14-Claude-Agent-SDK後端.md:130:`malformed-sdk-payload`：缺必填欄位／非法 enum 的 SDK message 必須成
/private/tmp/fable-R12-mock/docs/計畫/14-Claude-Agent-SDK後端.md-131-`PROTOCOL_FAULT`，不得被當 assistant text——15 的 `malformed.jsonl` 對稱格
/private/tmp/fable-R12-mock/docs/計畫/14-Claude-Agent-SDK後端.md-132-（R12 交叉比對：14 只殺 unknown、不殺 malformed 的不對稱）。
/private/tmp/fable-R12-mock/docs/計畫/14-Claude-Agent-SDK後端.md-133-
/private/tmp/fable-R12-mock/docs/計畫/14-Claude-Agent-SDK後端.md-134-- [ ] **Step 1: 寫full typed fixture stream與unknown-event red**
--
/private/tmp/fable-R12-mock/docs/計畫/14-Claude-Agent-SDK後端.md-334-**Interfaces:**
/private/tmp/fable-R12-mock/docs/計畫/14-Claude-Agent-SDK後端.md-335-- Consumes: InvocationEnvelope/workspace projection only。
/private/tmp/fable-R12-mock/docs/計畫/14-Claude-Agent-SDK後端.md-336-- Forbids: CriterionDefinition/CaseRef/Constraint registry/authority repository imports or paths。
/private/tmp/fable-R12-mock/docs/計畫/14-Claude-Agent-SDK後端.md-337-
/private/tmp/fable-R12-mock/docs/計畫/14-Claude-Agent-SDK後端.md:338:**ClaimSpec:** 【推論】`backend.claude-agent-sdk.projection-no-criterion-content` 從紅轉綠。
/private/tmp/fable-R12-mock/docs/計畫/14-Claude-Agent-SDK後端.md-339-
/private/tmp/fable-R12-mock/docs/計畫/14-Claude-Agent-SDK後端.md-340-**固定負控:** 【推論】sealed canary出現在SDK options/env/workspace/argv、adapter import Knowledge/Criterion registry、raw quota event含expected test data被拼prompt；direct red。
/private/tmp/fable-R12-mock/docs/計畫/14-Claude-Agent-SDK後端.md-341-
/private/tmp/fable-R12-mock/docs/計畫/14-Claude-Agent-SDK後端.md-342-- [ ] **Step 1: 寫visible-bytes/import graph red**
--
/private/tmp/fable-R12-mock/docs/計畫/15-Codex-CLI後端.md-13-## Global Constraints
/private/tmp/fable-R12-mock/docs/計畫/15-Codex-CLI後端.md-14-
/private/tmp/fable-R12-mock/docs/計畫/15-Codex-CLI後端.md-15-- 【推論】production argv固定從typed builder產生，不接受shell string或caller追加任意flags。
/private/tmp/fable-R12-mock/docs/計畫/15-Codex-CLI後端.md-16-- 【推論】固定禁止`--dangerously-bypass-approvals-and-sandbox`、`--yolo`、`danger-full-access`、`--last`與從任意目錄resume。
/private/tmp/fable-R12-mock/docs/計畫/15-Codex-CLI後端.md:17:- 【推論】v1 base argv為`codex exec --json --ephemeral --ignore-user-config --ignore-rules --strict-config --ask-for-approval never --sandbox workspace-write --cd <workspace> --model <pinned-model> -`；prompt只由stdin送入。
/private/tmp/fable-R12-mock/docs/計畫/15-Codex-CLI後端.md-18-- 【推論】`--sandbox workspace-write`不是敵意隔離證明；system offer仍只有實際host probe capabilities。
/private/tmp/fable-R12-mock/docs/計畫/15-Codex-CLI後端.md-19-- 【推論】JSONL unknown event不drop，保存raw CAS並發`PROTOCOL_FAULT`；自由stdout文字沒有terminal/quota裁定權。
/private/tmp/fable-R12-mock/docs/計畫/15-Codex-CLI後端.md-20-- 【推論】primary、secondary、credits各為獨立QuotaBucket；plan_type只是metadata，spend control/reached type是typed status，不把used percent換成absolute餘額。
/private/tmp/fable-R12-mock/docs/計畫/15-Codex-CLI後端.md-21-- 【推論】`codex update` v1不納入EffectEndpoint，manifest明示`update=UNSUPPORTED_UPDATE`；UI不得顯示可更新按鈕。若未來有exact-target installer，需新fingerprint/adapter revision與plan 11全套重驗。
--
/private/tmp/fable-R12-mock/docs/計畫/15-Codex-CLI後端.md-54-## Dependency Gate
/private/tmp/fable-R12-mock/docs/計畫/15-Codex-CLI後端.md-55-
/private/tmp/fable-R12-mock/docs/計畫/15-Codex-CLI後端.md-56-前置計畫：01B 05 06 07 11 12 13
/private/tmp/fable-R12-mock/docs/計畫/15-Codex-CLI後端.md-57-
/private/tmp/fable-R12-mock/docs/計畫/15-Codex-CLI後端.md:58:【推論】必須完成plan 01B、05–07、11–13——能力字彙（`PRE_TOOL_DECISION`／
/private/tmp/fable-R12-mock/docs/計畫/15-Codex-CLI後端.md-59-`NATIVE_STRUCTURED_OUTPUT`／`DELEGATION`／usage scope）的來源是 01B，
/private/tmp/fable-R12-mock/docs/計畫/15-Codex-CLI後端.md-60-缺它 manifest 的能力宣告就沒有 typed 主詞（R12 覆蓋審修正：原前置漏 01B）。adapter不直接呼叫application或resource repository；它只發BackendEvent/QuotaObservation並接InvocationEnvelope。前置未綠就接CLI，JSONL的版本細節會被誤當領域模型，`codex update`也會繞過Effect Authority。
/private/tmp/fable-R12-mock/docs/計畫/15-Codex-CLI後端.md-61-
/private/tmp/fable-R12-mock/docs/計畫/15-Codex-CLI後端.md-62----
--
/private/tmp/fable-R12-mock/docs/計畫/15-Codex-CLI後端.md-82-- [ ] **Step 1: 寫fingerprint sensitivity與exact argv snapshot red**
/private/tmp/fable-R12-mock/docs/計畫/15-Codex-CLI後端.md-83-
/private/tmp/fable-R12-mock/docs/計畫/15-Codex-CLI後端.md-84-```python
/private/tmp/fable-R12-mock/docs/計畫/15-Codex-CLI後端.md-85-def test_exec_argv_is_exact_and_reads_prompt_from_stdin() -> None:
/private/tmp/fable-R12-mock/docs/計畫/15-Codex-CLI後端.md:86:    assert build_exec_argv(fixed_request(), Path("/work")) == ("codex","exec","--json","--ephemeral","--ignore-user-config","--ignore-rules","--strict-config","--ask-for-approval","never","--sandbox","workspace-write","--cd","/work","--model","model-pinned","-")
/private/tmp/fable-R12-mock/docs/計畫/15-Codex-CLI後端.md-87-```
/private/tmp/fable-R12-mock/docs/計畫/15-Codex-CLI後端.md-88-
/private/tmp/fable-R12-mock/docs/計畫/15-Codex-CLI後端.md-89-- [ ] **Step 2: 跑tests確認modules缺失**
/private/tmp/fable-R12-mock/docs/計畫/15-Codex-CLI後端.md-90-
--
/private/tmp/fable-R12-mock/docs/計畫/15-Codex-CLI後端.md-379-- Modify: `nova/介接/執行者後端/codex_cli/test_契約.py`
/private/tmp/fable-R12-mock/docs/計畫/15-Codex-CLI後端.md-380-- Modify: `驗收/後端/codex_cli/測_jsonl執行.py`
/private/tmp/fable-R12-mock/docs/計畫/15-Codex-CLI後端.md-381-
/private/tmp/fable-R12-mock/docs/計畫/15-Codex-CLI後端.md-382-**Interfaces:**
/private/tmp/fable-R12-mock/docs/計畫/15-Codex-CLI後端.md:383:- Instantiates: shared backend suite, quota suite, context suite, no-criterion projection, process cleanup。
/private/tmp/fable-R12-mock/docs/計畫/15-Codex-CLI後端.md-384-
/private/tmp/fable-R12-mock/docs/計畫/15-Codex-CLI後端.md-385-**ClaimSpec:** 【推論】`backend.codex-cli.full-contract-matrix` 從紅轉綠。
/private/tmp/fable-R12-mock/docs/計畫/15-Codex-CLI後端.md-386-
/private/tmp/fable-R12-mock/docs/計畫/15-Codex-CLI後端.md-387-**固定負控:** 【推論】named faulty adapters：shell argv、drop unknown JSONL、self-terminal、flatten quota、ambient config、fake update；指定tests各殺一個，不能用mutmut總擊殺率。
--
/private/tmp/fable-R12-mock/docs/計畫/15-Codex-CLI後端.md-410-git add nova/介接/執行者後端/codex_cli/test_契約.py 驗收/後端/codex_cli/測_jsonl執行.py
/private/tmp/fable-R12-mock/docs/計畫/15-Codex-CLI後端.md-411-git commit -m "test: 驗證 Codex CLI adapter 的完整契約"
/private/tmp/fable-R12-mock/docs/計畫/15-Codex-CLI後端.md-412-```
/private/tmp/fable-R12-mock/docs/計畫/15-Codex-CLI後端.md-413-
/private/tmp/fable-R12-mock/docs/計畫/15-Codex-CLI後端.md:414:### Task 8: 能力宣告誠實且投影不含判準（與計畫 14 對稱）
/private/tmp/fable-R12-mock/docs/計畫/15-Codex-CLI後端.md-415-
/private/tmp/fable-R12-mock/docs/計畫/15-Codex-CLI後端.md-416-**Files:**
/private/tmp/fable-R12-mock/docs/計畫/15-Codex-CLI後端.md-417-- Create: `驗收/後端/codex_cli/測_投影.py`
/private/tmp/fable-R12-mock/docs/計畫/15-Codex-CLI後端.md-418-- Create: `規格/執行/保證/後端/codex不讀判準.claim.json`
--
/private/tmp/fable-R12-mock/docs/計畫/15-Codex-CLI後端.md-421-- Modify: `nova/介接/執行者後端/codex_cli/test_契約.py`
/private/tmp/fable-R12-mock/docs/計畫/15-Codex-CLI後端.md-422-
/private/tmp/fable-R12-mock/docs/計畫/15-Codex-CLI後端.md-423-**Interfaces:**
/private/tmp/fable-R12-mock/docs/計畫/15-Codex-CLI後端.md-424-- Produces: manifest 對 01B 四類能力**逐項宣告並帶機制證據**：
/private/tmp/fable-R12-mock/docs/計畫/15-Codex-CLI後端.md:425:  `PRE_TOOL_DECISION`＝**unsupported**（Codex CLI 無 pre-tool callback；
/private/tmp/fable-R12-mock/docs/計畫/15-Codex-CLI後端.md:426:  `--ask-for-approval never` 是關掉核准、不是提供 callback）；
/private/tmp/fable-R12-mock/docs/計畫/15-Codex-CLI後端.md-427-  `NATIVE_STRUCTURED_OUTPUT`＝依 pinned binary probe，無證據即 unsupported；
/private/tmp/fable-R12-mock/docs/計畫/15-Codex-CLI後端.md-428-  `DELEGATION`＝unsupported（v1 無受控子代理契約）；usage scope＝`ROOT_ONLY`
/private/tmp/fable-R12-mock/docs/計畫/15-Codex-CLI後端.md-429-  誠實宣告，**不得升格 tree total**。宣告 true 而無 probe 證據必須紅。
/private/tmp/fable-R12-mock/docs/計畫/15-Codex-CLI後端.md:430:- Produces: no-criterion projection——sealed canary 不得出現在 argv／env／stdin／
/private/tmp/fable-R12-mock/docs/計畫/15-Codex-CLI後端.md-431-  workspace；adapter 不 import criterion／constraint registry。
/private/tmp/fable-R12-mock/docs/計畫/15-Codex-CLI後端.md-432-  （R12 覆蓋審修正：14 有 `claude不讀判準` claim 與 `測_投影.py`，15 只在 T7 的
/private/tmp/fable-R12-mock/docs/計畫/15-Codex-CLI後端.md:433:  Interfaces 提了一句「no-criterion projection」——**無檔案、無 claim、無 fixture**；
/private/tmp/fable-R12-mock/docs/計畫/15-Codex-CLI後端.md-434-  adapter 家族的不對稱缺口。本 task 也讓 T7 matrix 的那個名詞從此有主體。）
/private/tmp/fable-R12-mock/docs/計畫/15-Codex-CLI後端.md-435-
/private/tmp/fable-R12-mock/docs/計畫/15-Codex-CLI後端.md:436:**ClaimSpec:** 【推論】`backend.codex-cli.capabilities-honest` 與 `backend.codex-cli.projection-no-criterion-content` 從紅轉綠。
/private/tmp/fable-R12-mock/docs/計畫/15-Codex-CLI後端.md-437-
/private/tmp/fable-R12-mock/docs/計畫/15-Codex-CLI後端.md:438:**ClaimSpec落點:** `backend.codex-cli.capabilities-honest` → `規格/執行/保證/後端/codex能力誠實.claim.json`（本 task Create）；`backend.codex-cli.projection-no-criterion-content` → `規格/執行/保證/後端/codex不讀判準.claim.json`（本 task Create）
/private/tmp/fable-R12-mock/docs/計畫/15-Codex-CLI後端.md-439-
/private/tmp/fable-R12-mock/docs/計畫/15-Codex-CLI後端.md:440:**固定負控:** 【推論】四格。`optimistic-capability`：`PRE_TOOL_DECISION` 或
/private/tmp/fable-R12-mock/docs/計畫/15-Codex-CLI後端.md-441-`DELEGATION` 宣告 true 而無機制證據的 manifest 變體，必須紅在
/private/tmp/fable-R12-mock/docs/計畫/15-Codex-CLI後端.md-442-`capability_requires_mechanism_evidence`。`usage-scope-upgraded`：root usage 標成
/private/tmp/fable-R12-mock/docs/計畫/15-Codex-CLI後端.md-443-`DELEGATION_TREE_TOTAL` 的變體，必須紅在 `usage_scope_not_upgraded`。
/private/tmp/fable-R12-mock/docs/計畫/15-Codex-CLI後端.md-444-`sealed-canary-in-invocation`：canary 出現在 stdin／env／argv／workspace 任一，
--
/private/tmp/fable-R12-mock/docs/計畫/15-Codex-CLI後端.md-450-- [ ] **Step 1: 寫四個負控與防恆真格的 red tests**
/private/tmp/fable-R12-mock/docs/計畫/15-Codex-CLI後端.md-451-
/private/tmp/fable-R12-mock/docs/計畫/15-Codex-CLI後端.md-452-```python
/private/tmp/fable-R12-mock/docs/計畫/15-Codex-CLI後端.md-453-def test_樂觀宣告的能力必須被拒() -> None:
/private/tmp/fable-R12-mock/docs/計畫/15-Codex-CLI後端.md:454:    變體 = manifest變體(PRE_TOOL_DECISION=True, 證據=None)
/private/tmp/fable-R12-mock/docs/計畫/15-Codex-CLI後端.md-455-    assert 驗manifest(變體).code == "CAPABILITY_REQUIRES_MECHANISM_EVIDENCE"
/private/tmp/fable-R12-mock/docs/計畫/15-Codex-CLI後端.md-456-
/private/tmp/fable-R12-mock/docs/計畫/15-Codex-CLI後端.md-457-def test_呼叫不含封存金絲雀() -> None:
/private/tmp/fable-R12-mock/docs/計畫/15-Codex-CLI後端.md-458-    呼叫 = 捕捉codex呼叫(雙池fixture())
--
/private/tmp/fable-R12-mock/docs/計畫/15-Codex-CLI後端.md-468-- [ ] **Step 3: 寫能力宣告、證據 gate 與投影收窄**
/private/tmp/fable-R12-mock/docs/計畫/15-Codex-CLI後端.md-469-
/private/tmp/fable-R12-mock/docs/計畫/15-Codex-CLI後端.md-470-- [ ] **Step 4: 跑四個負控、防恆真格與兩份 ClaimSpec**
/private/tmp/fable-R12-mock/docs/計畫/15-Codex-CLI後端.md-471-
/private/tmp/fable-R12-mock/docs/計畫/15-Codex-CLI後端.md:472:Run: `uv run pytest -q 驗收/後端/codex_cli/測_投影.py nova/介接/執行者後端/codex_cli/test_契約.py && uv run python 工具/跑驗收.py --claim backend.codex-cli.capabilities-honest --claim backend.codex-cli.projection-no-criterion-content`
/private/tmp/fable-R12-mock/docs/計畫/15-Codex-CLI後端.md-473-
/private/tmp/fable-R12-mock/docs/計畫/15-Codex-CLI後端.md-474-Expected: 【推論】PASS；四個負控各紅在自己宣告的 predicate。
/private/tmp/fable-R12-mock/docs/計畫/15-Codex-CLI後端.md-475-
/private/tmp/fable-R12-mock/docs/計畫/15-Codex-CLI後端.md-476-- [ ] **Step 5: Commit**

web search: 
web search: site:developers.openai.com/codex CLI ask-for-approval hooks pre tool callback exec JSON ...
web search: 
web search: site:developers.openai.com/codex/config-reference approval_policy notify hooks ...
context compacted
codex
我會直接依目前 main 與四份 diff 裁決；其中 R12-00 我會把「diff 封裝是否可直接套用」和「自測是否進 required gate」視為兩個獨立的機制條件。R12-02 則依官方資料能支持的強度審，不把文件未記載當成能力不存在的證明。
exec
/bin/zsh -lc "sed -n '1,260p' /Users/sbu/.codex/skills/.system/../.system 2>/dev/null || true
sed -n '1,240p' /Users/sbu/.codex/skills/.system/openai-docs/SKILL.md
sed -n '1,180p' /Users/sbu/nova/scratchpad/fable-R12-複驗器.diff 2>/dev/null || true
rg -n \"--自測|計畫複驗自測|\\[\\[gate\\]\\]|PRE_TOOL_DECISION|ask-for-approval|Task 8|malformed-sdk-payload|Task 9\" docs/計畫複驗.py 架構/目錄規則.toml docs/計畫/12-* docs/計畫/14-* docs/計畫/15-* /private/tmp/fable-R12-mock 2>/dev/null | head -240" in /Users/sbu/nova
 succeeded in 0ms:
---
name: "openai-docs"
description: "Use for Codex models/pricing, scheduled tasks, skills, settings, setup, troubleshooting, customization, automations, and self-knowledge—including 'you,' 'your,' 'this app,' or 'this coding agent' when they refer to Codex—and for OpenAI APIs/products and ChatGPT Work. Also use for model choice/migration, prompting, SDKs, Responses, Realtime, agents, evals, and Chat/Work/Codex comparisons. Do not use for generic app/software tasks that merely mention Codex."
metadata:
  short-description: "Codex models/pricing, scheduled tasks, skills, settings, setup, troubleshooting, and self-knowledge; OpenAI APIs and ChatGPT Work. 'You'/'this app' means Codex only."
---

# OpenAI Docs

Provide current, cited OpenAI product, API, model, and Codex guidance. Read zero or one primary reference.

**First substantive action:** Search the user's exact requested official OpenAI documentation topic and any explicitly named model using a concise, topic-specific query of 2-6 essential terms. When an already-available direct official documentation search and page-retrieval capability is present, use it first: search, then fetch or open the matching official page before general web search. Otherwise, immediately use official-domain web search, then actually open or fetch the relevant official page. Complete this source order before reading a reference, inspecting local or repository files, running a Codex manual or model resolver, drafting a plan, or answering from memory. Use the actual fetched page, not a search snippet or an unopened link. If one official search or page does not establish the answer, search another appropriate official domain and actually open or fetch the result. Preserve the exact requested model; never substitute a newer model.

**Only exception:** An explicitly requested, genuinely broad, cross-topic Codex setup, orientation, or system-map synthesis may use the manual first when shell execution and an allowed temporary cache are available. A specific Codex feature, setting, command, error, model, or requested citation remains docs-first. Mixed Chat/Work/Codex comparisons are official documentation questions, not manual-first Codex requests.

For generic software tasks, answer the software task directly. OpenAI implementation, debugging, SDK, API, prompting, agent, and eval requests are not generic.

For a straightforward factual or citation-only request, follow the source order and do not read a route reference. This includes straightforward API facts, ChatGPT Work or mixed Chat/Work/Codex comparisons, model tiers, aliases, Pro mode, reasoning settings, factual migration baselines, and narrow Codex facts. Prioritize `learn.chatgpt.com` for ChatGPT Work.

## Choose one primary route

Use the first matching route, and read its reference only when the requested task needs that specialized workflow:

- **Explicitly requested local documentation integration:** Read [integration guidance](references/mcp-diagnostics.md) only when the user explicitly requests that local integration.
- **Model migration, upgrades, or model-specific prompting:** Read [model-migration.md](references/model-migration.md) for actual migration planning, implementation, dynamic target resolution, or prompt changes. Preserve an explicitly requested target.
- **Model selection and comparisons:** Read [model-selection.md](references/model-selection.md) only when nuanced current, latest, default, cost, latency, quality, or modality tradeoffs need more guidance. Do not run a migration resolver for selection alone.
- **Product, API, ChatGPT Work, and mixed Chat/Work/Codex documentation:** Read [official-docs.md](references/official-docs.md) only when fetched official pages leave source selection, API schemas, or the requested implementation unresolved. This route is not manual-first.
- **Explicitly broad Codex setup, orientation, or cross-topic synthesis:** Read [codex-self-knowledge.md](references/codex-self-knowledge.md) when the eligible Codex manual or deeper Codex procedures are needed.

Read at most one primary reference. Do not open every route, bundled model guide, or helper script. Read a supporting reference or run a helper only when the chosen workflow demonstrably needs it.

## Source and execution boundaries

- Search, open, fetch, and cite only `developers.openai.com`, `platform.openai.com`, and `learn.chatgpt.com`. Cite the page that supports the claim. State uncertainty when official sources do not establish pricing, availability, account access, limits, or behavior.
- Preserve an explicitly requested model for selection, migration, and prompting. Resolve an unspecified latest or current migration target only after searching and fetching current official guidance.
- Use `references/latest-model.md` only as a disclosed fallback after current official model guidance does not answer the question. Read `references/upgrading-to-gpt-5p6-sol.md` only for an actual, requested GPT-5.6-family migration; read `references/prompting-guide.md` only for requested prompting work.
- Before building, running, editing, debugging, or testing an API-backed app or tool, use `openai-platform-api-key` first when available. Documentation, conceptual examples, model selection, and read-only guidance do not require an API key.
- Say "OpenAI Docs" or "official OpenAI documentation" in user-facing answers. Keep exact official citations and examples concise.

web search: 
web search: site:developers.openai.com/codex CLI ask-for-approval never hooks pre tool callback ...
codex
裁決如下。

- **R12-00：APPROVE（附兩項寫入條件）**  
  自測確實能在執法器漏抓撞號時轉紅，具備真牙齒。寫入時必須：
  1. 重新產生正確路徑的 diff，fixture 必須落在 `docs/計畫複驗自測/撞號/`，不得依賴人工搬移。
  2. 同一批將 `uv run python docs/計畫複驗.py --自測` 接入 required gate；若閘清單只有控制端能改，就標成 **Authority Step**，且接入前 R12-00 不得宣告完成。

- **R12-01：APPROVE**  
  claim 檔、兩支紅測的修改落點與落點行補齊，正好修掉「claim 與測試都沒有家」的結構缺口。

- **R12-02：APPROVE（附必要措辭條件）**  
  01B 前置、能力逐項映射與 no-criterion 投影都有可執法主體；但必須把「Codex CLI 無 pre-tool callback」改成：  
  **「v1 adapter 沒有已准入、可驗證的 PRE_TOOL_DECISION 機制，因此宣告 unsupported。」**  
  官方文件沒有記載某介面，不能證明該介面不存在；`--ask-for-approval never` 也只能證明核准策略設定，不能證明沒有 callback。未來只有 pinned binary/API probe 與對應負控能把它升為 supported。這也適用於 `DELEGATION`。我查到的官方 OpenAI 文件不足以支撐原本那個否定性產品宣稱，因此不能原句寫入。[OpenAI Developers](https://developers.openai.com/)

- **R12-03：APPROVE**  
  `malformed-sdk-payload` 直接補上 14 對 malformed／非法 enum 的缺失殺手，且不把畸形資料降格成普通 assistant text。

三件裁量的直接答案：

1. **`--自測` 現在就該進閘。**  
   可以由控制端執行設定，但不能只留下手動指令。未接入前，它是可用的診斷工具，不是持續保護機制。

2. **R12-02 的誠實邊界原樣不夠。**  
   「沒 probe」可以誠實揭露證據不足，卻不能同時斷言產品不存在該能力。改成「本 adapter 尚無已准入機制，故 fail-closed 宣告 unsupported」即可通過；實際產品能力值留給 pinned probe 決定。

3. **R12-01 是真缺口。**  
   零 Create 使 ClaimSpec 無落點、紅測無可修改檔案；原先即使散文完整，也沒有可交付、可轉紅的主體。補法正確。
tokens used
128,662
裁決如下。

- **R12-00：APPROVE（附兩項寫入條件）**  
  自測確實能在執法器漏抓撞號時轉紅，具備真牙齒。寫入時必須：
  1. 重新產生正確路徑的 diff，fixture 必須落在 `docs/計畫複驗自測/撞號/`，不得依賴人工搬移。
  2. 同一批將 `uv run python docs/計畫複驗.py --自測` 接入 required gate；若閘清單只有控制端能改，就標成 **Authority Step**，且接入前 R12-00 不得宣告完成。

- **R12-01：APPROVE**  
  claim 檔、兩支紅測的修改落點與落點行補齊，正好修掉「claim 與測試都沒有家」的結構缺口。

- **R12-02：APPROVE（附必要措辭條件）**  
  01B 前置、能力逐項映射與 no-criterion 投影都有可執法主體；但必須把「Codex CLI 無 pre-tool callback」改成：  
  **「v1 adapter 沒有已准入、可驗證的 PRE_TOOL_DECISION 機制，因此宣告 unsupported。」**  
  官方文件沒有記載某介面，不能證明該介面不存在；`--ask-for-approval never` 也只能證明核准策略設定，不能證明沒有 callback。未來只有 pinned binary/API probe 與對應負控能把它升為 supported。這也適用於 `DELEGATION`。我查到的官方 OpenAI 文件不足以支撐原本那個否定性產品宣稱，因此不能原句寫入。[OpenAI Developers](https://developers.openai.com/)

- **R12-03：APPROVE**  
  `malformed-sdk-payload` 直接補上 14 對 malformed／非法 enum 的缺失殺手，且不把畸形資料降格成普通 assistant text。

三件裁量的直接答案：

1. **`--自測` 現在就該進閘。**  
   可以由控制端執行設定，但不能只留下手動指令。未接入前，它是可用的診斷工具，不是持續保護機制。

2. **R12-02 的誠實邊界原樣不夠。**  
   「沒 probe」可以誠實揭露證據不足，卻不能同時斷言產品不存在該能力。改成「本 adapter 尚無已准入機制，故 fail-closed 宣告 unsupported」即可通過；實際產品能力值留給 pinned probe 決定。

3. **R12-01 是真缺口。**  
   零 Create 使 ClaimSpec 無落點、紅測無可修改檔案；原先即使散文完整，也沒有可交付、可轉紅的主體。補法正確。
