# Claude Agent SDK 研究筆記（2026-08-26 起，邊讀邊記）

來源：`claude.com/blog/a-harness-for-every-task-dynamic-workflows-in-claude-code`
＋ `code.claude.com/docs/*/agent-sdk/*`（31 頁，逐頁取）。
本檔只記**對 nova 有決策影響**的事實，並在每條後面標 nova 的落差。
標記：【SDK】＝文件事實　【一手】＝我在本 repo 實測／讀碼　【推論】＝我的判斷。

---

## 0. 最關鍵的三件事（先講結論）

### 0-1　nova 完全沒讀 `ResultMessage.subtype`——這是會沉默吃掉失敗的缺陷

【SDK】`ResultMessage.subtype` ∈ `success` / `error_max_turns` / `error_max_budget_usd`
/ `error_during_execution` / `error_max_structured_output_retries`。
**`result` 欄位只在 `success` 時存在。**
【SDK】單發 `query()` 在 yield 完 error result 之後**會 raise**；底層程序也以非零退出。
【SDK】session crash 時的 `error_during_execution`：`usage`／`total_cost_usd`／`model_usage`
**可能全部歸零**，`stop_reason` 為 `null`，程序直接退出。

【一手】`grep -rn subtype src/`：nova 產品碼只有 `後端/重播.py` 用到（錄放序列化），
**執行路徑完全不讀**。`後端/claude輔助.py:127` 是 `文字 = 訊.result or ""`。
【一手】`stop_reason`、`model_usage` 在整個 repo（src＋tests）**零出現**。
【一手】所有測試都寫死 `subtype="success"`——失敗子型別**零覆蓋、零處理**。

【推論】後果：預算熔斷或 crash 回來的那一輪，nova 看到的是
**「成功但輸出是空字串」**。這正是 `後端/codex.py:10` 記過的
「agy 5h 額度耗盡致候選白卷停滯」的同一種病，只是 claude 這條路上**完全無聲**。

### 0-2　`usage` 不含子代理——nova 記的用量結構性低估

【SDK】三個結果層欄位對子代理的口徑不同：
`usage` **排除**子代理；`total_cost_usd` **包含**；`model_usage` **包含且按模型拆分**。
【一手】nova 有設 `子代理`（`後端/claude.py:95`），而 `claude輔助.py:135` 記的是 `usage`。
成本用的是 `total_cost_usd`（對），但**用量帳低估**。

### 0-3　逾時：**SDK 明講它沒有總時限**——nova 自建監督式執行器是對的

【SDK】環境變數（走 `options.env`）：
- `API_TIMEOUT_MS`（單請求，預設 600000）
- `CLAUDE_CODE_MAX_RETRIES`（預設 10，上限 15）
- `CLAUDE_ASYNC_AGENT_STALL_TIMEOUT_MS`（**子代理停滯看門狗**，預設 600000）
- `CLAUDE_ENABLE_STREAM_WATCHDOG`、`CLAUDE_STREAM_IDLE_TIMEOUT_MS`（預設／最小 300000）
- `max_turns`（回合上限）、`max_budget_usd`（花費上限，**含子代理**）

**【更正 2026-08-26】我一開始把這幾個旋鈕當成「供應商版的外部逾時」，讀到 hosting 頁才發現不是。**
`agent-sdk/hosting` 的「Known limitations」表白紙黑字寫兩條：

| 限制 | 文件原話 |
|---|---|
| **No top-level session timeout** | 「A session does not time out on its own.」只能用 `maxTurns` 界定回合數 |
| **No per-subagent wall-clock deadline** | `CLAUDE_ASYNC_AGENT_STALL_TIMEOUT_MS` 是**停滯**看門狗（只對 `run_in_background` 子代理、
輸出停了才觸發），**「it is not a total-runtime deadline」** |

【推論】所以計畫書第 0-1 期的推導**成立而且被供應商文件正面背書**：
真正的牆鐘上限只能由外部程序群組強制，SDK 自己不提供。
`max_turns` 與 `max_budget_usd` 是**另外兩個軸**（回合／花費），該一起設，
但它們替代不了時間軸。三軸都要。

---

## 1. `ClaudeAgentOptions` 全欄位 vs nova 實際傳入

【一手】nova `後端/claude.py:100` 只傳：`permission_mode`／`model`／`cwd`／`plugins`
／`system_prompt`／`resume`，加上 extra_options 裡的 `max_budget_usd`、`子代理`→`agents`、`hooks`。

**沒用到而對 nova 有直接意義的：**

| 欄位 | 對 nova 的意義 |
|---|---|
| `max_turns` | 回合上限。nova 只有秒數上限，沒有回合上限 |
| `effort`（low/medium/high/xhigh/max） | codex 走 `model_reasoning_effort=max`，**claude 這條路完全沒有對等旋鈕** |
| `fallback_model` | 主模型失敗時的退路 |
| `output_format` | 結構化輸出（見 §3），nova 現在靠自由文字 |
| `session_id`（指定 UUID） | 可讓 `loop_id` ↔ session 決定性對應 |
| `fork_session` | **直接回答「出題被打回要用原 session 還是新 session」** |
| `resume_session_at`（載入到某 message UUID） | 精確回捲到被打回那一輪之前 |
| `resume_drops_turn`（丟掉某個 user prompt 的那一輪） | 打回時「把那次出題整輪拿掉」 |
| `can_use_tool` | 逐次工具裁決回呼；nova 只有 `permission_mode` 全有全無 |
| `setting_sources` | 見 §2，**預設值有安全含義** |
| `skills` | `"all"`／名單／`[]` |
| `sandbox`（`SandboxSettings`） | 沙箱 |
| `task_budget` | **API 側** token 預算（相對於 client 側估算的 `max_budget_usd`） |
| `session_store` | 見 §4，可耐久鏡像 transcript |
| `stderr` 回呼／`max_buffer_size` | `平台/工具執行.py:117` 把 stdout 讀進記憶體的問題，SDK 這邊有現成解 |
| `add_dirs` | 額外可存取目錄 |
| `enable_file_checkpointing` | 見 §5 |
| `strict_mcp_config` | 見 §2 的 claude.ai connector 洩漏 |

## 2. `setting_sources` 的預設值有安全含義

【SDK】**省略 `settingSources` ＝ `["user", "project", "local"]`。**
會載入：`<cwd>/CLAUDE.md`（含所有父目錄）、`.claude/rules/*.md`、
`<cwd>/.claude/settings.json` 的 hooks、專案與使用者的 skills／commands／agents、
`~/.claude/CLAUDE.md`、`~/.claude/rules/*.md`、`CLAUDE.local.md`。

【一手】nova 沒設這個欄位 → 候選 session 在 worktree 裡跑時，
**會載入 worktree 內的 `.claude/settings.json` hooks 與 `.claude/agents/`**。
【推論】那是一條逃逸面：候選能改 worktree 裡的 `.claude/`（它不在保護清單裡），
下一輪就會被載進來執行。與 repo「防忘記／出錯，不防蓄意」的立場**還算一致**，
但這條沒被記錄過，該進 `docs/陷阱.md` 或變成保護清單的一員。

【SDK】**不受 `settingSources` 控制、一律會讀的**：
- managed policy settings
- `~/.claude.json` 全域設定（只能用 `CLAUDE_CONFIG_DIR` 搬走）
- **auto memory：`~/.claude/projects/<project>/memory/` 會載進 system prompt**，
  且 agent 用一般 `Write`/`Edit` 就能往那寫（關法：`autoMemoryEnabled: false`
  或 `CLAUDE_CODE_DISABLE_AUTO_MEMORY=1`）
- claude.ai MCP connectors（關法：`strictMcpConfig: true` 等）

【推論】**這是 nova 目前最沒被看見的污染通道**：候選 session 會讀到（也能寫入）
我這個控制端的記憶目錄。`mcp_servers={}` 不會擋掉 connector。
文件自己的 Warning 就是「不要靠 `query()` 預設值做多租戶隔離」——
而 nova 的出題／實作／裁定三權分立，本質上就是多租戶隔離。

## 3. 結構化輸出（`output_format`）

【SDK】`{"type": "json_schema", "schema": <JSON Schema>}`；結果在
`ResultMessage.structured_output`。**只吃 JSON Schema draft-07**（Zod 要
`target: "draft-7"`；Pydantic 用 `.model_json_schema()`）。
無效 schema 在 v2.1.205 起**啟動即失敗並指名問題**（更早版本是靜默忽略、退回自由文字）。
`format` 關鍵字只當註解、不強制。
失敗子型別 `error_max_structured_output_retries`（驗證連續失敗，**或 model fallback
把已完成的輸出撤回而沒有成功重試**——要看 result 的 `errors` 清單才分得出兩者）。
**`subtype == "success"` 但 `structured_output` 缺席也要當失敗處理。**

【推論】nova 的角色薄殼契約是「stdout 永遠是單一 JSON object」，那是自己用
prompt 約束模型再自己解析。`output_format` 是同一件事的原生版本，
且有 retry 與明確的失敗子型別。

## 4. `SessionStore`：供應商提供的耐久 outbox，附一致性測試套件

【SDK】`SessionStore` protocol：必要 `append(key, entries)` / `load(key)`；
選配 `list_sessions` / `list_session_summaries` / `delete` / `list_subkeys`。
`SessionKey = {project_key, session_id, subpath?}`，`subpath` 是子代理 transcript。
【SDK】**雙寫架構**：子程序一定先寫本機磁碟，SDK 再把同一批轉給 `append()`——
store 是本機 transcript 的鏡像，不是替代品。
- 全新 session／store 沒有該 session：本機那份存活，store 收到副本
- **從 store resume 的跑**：跑完刪掉本機副本，**store 是唯一耐久副本**
【SDK】**鏡像寫是 best-effort**：`append()` 被拒最多重試三次（逾時不重試，因為原呼叫可能仍會落地）；
仍失敗就記錄、往 iterator 送一則 `{type:"system", subtype:"mirror_error"}`、**丟掉該批**、繼續跑。
重試會重送已落地的項目，所以 `append()` **要自己按 `entry.uuid` 去重**。
【SDK】Python 套件內附一致性測試套件：`claude_agent_sdk.testing.run_session_store_conformance`。
【SDK】`fork_session` 不是位元複製：會重寫每個 `sessionId` 並重映射 message UUID。
【SDK】`get_session_messages` 回的是**壓縮後**的訊息鏈；要原始要 `store.load(key)`。

【推論】這與 sol 的 QO／QC 設計正面相關，而且**「三本 ack 帳要分開」在這裡已經是既成事實**：
本機寫 ≠ 鏡像 ack ≠ 消費完成。`mirror_error` 就是 sol 說的「投遞失敗不得記成成功 ack」的原生形態。
nova 要嘛接上它，要嘛明講為什麼不接。

## 5. File checkpointing vs nova 的 worktree

【SDK】`enable_file_checkpointing=True` ＋ `extra_args={"replay-user-messages": None}`；
checkpoint UUID 來自 `UserMessage.uuid`；`rewind_files(uuid)` 回捲。
**限制**：只追 `Write`/`Edit`/`NotebookEdit`；**Bash 改的不算**；
**子代理改的不算**（除了 foreground 的 `context: fork` skill）；只在同一 session 內；
只回捲檔案內容，不回捲目錄的建立／移動／刪除。

【推論】nova 用 disposable worktree ＋ git 是**對的選擇**，不該換成 checkpointing——
候選大量用 Bash，而 Bash 的改動 checkpointing 抓不到。這一條可以直接寫進設計理由。

## 6. 子代理的上限與注入防護

【SDK】`AgentDefinition` 欄位：`description`(必)／`prompt`(必)／`tools`／`disallowedTools`
／`model`（含 `'inherit'`）／`skills`／`memory`／`mcpServers`／`initialPrompt`
／`maxTurns`／`background`／`effort`／`permissionMode`。
（Python SDK 保留 camelCase 拼法以對齊 wire format。）
【SDK】v2.1.198 起**子代理預設在背景跑**；Agent 工具呼叫省略 `run_in_background` 即背景。
【SDK】上限三軸：
- 深度 `CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH`（預設 3）
- 併發 `CLAUDE_CODE_MAX_CONCURRENT_SUBAGENTS`（預設 20）
- 花費 `max_budget_usd`（達標時：拒絕再開子代理、**停掉還在跑的背景子代理**、以
  `error_max_budget_usd` 結束）
【SDK】**Opus 5 比舊模型更愛派子代理**，所以這三個上限在 Opus 5 上最要緊。
用 `claude_code` preset 時 Claude Code 會自己加一行「除非被要求否則別呼叫 Agent」；
**用自訂 systemPrompt 就沒有那行**。
【SDK】v2.1.210 起會掃子代理最終訊息裡的「指令狀」樣式（控制標籤仿冒、權限設定提及、
`Human:`/`Assistant:` turn marker），加反斜線中和並前置 `[harness: ...]` 標記，**不刪不改寫**。

【推論】nova 的 `後端/claude.py` 用的是 `{"type":"preset","preset":"claude_code","append":...}`
（有 preset，所以那行防呆在）。但 nova **沒設**深度與併發上限，
而 `平台/爐身分.py` 的 `每爐核數=3` 併發餘裕閘是在**爐**這一層算的，
和 SDK 在 **session 內**生出來的 20 個子代理是**兩個不相干的軸**——
今晚已知的「餘裕閘低估四倍」之外還有這一層完全沒被算進去。

## 7. 部落格：dynamic workflows

【SDK】它要解的三個失敗模式，逐條對到 nova：
| 失敗模式 | 內容 | nova 的對應 |
|---|---|---|
| **agentic laziness** | 部分完成就宣稱做完（「50 項安全審查做了 35 項」） | 判準綠了才算＝已解 |
| **self-preferential bias** | 「特別是被要求依 rubric 自我驗證時，偏好自己的結果」 | 三權分立＝已解，**而且這是供應商認證的失敗模式** |
| **goal drift** | 多輪後對原目標的保真度流失，**尤其在壓縮之後** | **未解**：nova 把目標敘述放在 prompt 裡，壓縮後就沒了 |

【SDK】對應解法（文件明講）：**「持久性規則屬於 CLAUDE.md，不屬於初始 prompt，
因為 CLAUDE.md 每個請求都會重新注入。」** 另有 `PreCompact` hook、
`compact_boundary` 訊息、可在 CLAUDE.md 寫「壓縮時要保留什麼」的段落。

【推論】**這是 nova 目前最便宜的一個大改善**：目標檔的敘述與判準應該以
CLAUDE.md／rules 的形式進候選 worktree，而不是只塞在 prompt 開頭。
nova 已經有「規則目錄／記憶目錄 → system_prompt append」的機制（`claude.py:63`），
但 append 進 system prompt 與 CLAUDE.md 的壓縮存活性不同——這點要驗。

【SDK】六種可組合的結構：classify-and-act／fan-out-and-synthesize／
**adversarial verification**／generate-and-filter／**tournament**／loop-until-done。
另有 quarantine pattern（讀不可信內容的 agent 不得有高權限動作）。
【SDK】**靜態 vs 動態**：「靜態工作流（用 Agent SDK 或 `claude -p` 建的）必須處理所有
邊界情況，因此是通用的」；動態工作流讓模型當場為這個任務寫 harness。
**【更正 2026-08-26 · 一手驗過】** 我原本寫「`Workflow` 工具只在 TypeScript SDK，Python 沒有」——**錯的**。
`agent-sdk/subagents` 那句話講的是**TS 參考文件有列該工具的 schema**，不是可用性。
`/docs/en/workflows` 明講 workflows 在「CLI、Desktop、IDE 擴充、`claude -p` 與 **Agent SDK**」上都可用。

一手驗證（本機）：
```
uv run python -c "import claude_agent_sdk, pathlib; ..."   → 0.2.144，自帶 _bundled/claude
.venv/.../claude_agent_sdk/_bundled/claude --version        → 2.1.239 (Claude Code)
grep -ao '"Workflow"' <bundled binary>                      → 命中
grep -ao 'CLAUDE_CODE_DISABLE_WORKFLOWS' <bundled binary>    → 命中
```
Python SDK **自帶**一個 CLI 二進位（324 MB），`_find_cli` 優先用它、找不到才退回 PATH 上的 `claude`。
那個 binary 版本 ≥ 2.1.154，裡面有 Workflow 工具與它的關閉設定。
**結論：nova 用 Python 也能開動態工作流**，把 `"Workflow"` 放進 `allowed_tools` 即可。
（順帶：`nova 部署` 的「安裝版是複本、不重裝就是舊 code」那條，在這裡多一層——
**SDK 版本決定 CLI 版本**，`uv sync` 不動就是舊 CLI。本機 PATH 上是 2.1.240，SDK 自帶的是 2.1.239。）

【推論】這對 nova 是**戰略級的一句話**：nova 是一個靜態 harness，
而供應商的論點是靜態 harness 必然通用因而次佳。nova 的反論應該是
「nova 的價值不在編排形狀，在**驗收權外置**」——動態 workflow 解的是
laziness 與 bias，但它沒有解「誰有權說這件事做完了」。這一點要跟 sol 對打。
另外：**Python SDK 沒有 `Workflow` 工具**，所以「nova 直接用動態工作流」這條路
目前在 Python 上不存在，只能自建或走 TS。

---

## 待查（下一批）
permissions / custom-tools / mcp / tool-search / observability / todo-tracking
/ streaming-vs-single-mode / modifying-system-prompts / hosting / secure-deployment
/ skills / plugins / migration-guide / typescript（比對 Python 缺什麼）

---

## 7. 權限求值順序：hooks 在第一步，而且 deny 穿透 bypassPermissions

【SDK】順序是 **hooks → deny 規則 → ask 規則 → permission mode → allow 規則 → `canUseTool`**。
- hook 的 **deny 在 `bypassPermissions` 下仍然生效**；hook 的 allow **不會**跳過 deny／ask。
- `disallowed_tools` 的 scoped deny（如 `Bash(rm *)`）**在每個模式下都擋**，含 `bypassPermissions`。
- 裸名 deny（`Bash`）是把工具**從 context 移除**，模型根本看不到。
- `allowed_tools` **不約束 `bypassPermissions`**：沒列的工具照樣被批准。要擋只能用 `disallowed_tools`。
- **被提早批准的工具永遠不會到 `canUseTool`**——放在那裡的檢查會被靜默跳過。
  文件原話：「For checks that must run on every tool call, use a `PreToolUse` hook.」
- `Edit(path)` 規則管**所有寫檔的內建工具**（含 `Write`、`NotebookEdit`）；`Write(path)` 規則永遠不會被比對到。
- 路徑錨點：`//abs/**` 是磁碟絕對路徑；`/abs/**` 錨在規則來源（對 `allowed_tools` 而言是工作目錄）。

【推論】**這對 nova 的信任邊界是一次實質升級。**
CLAUDE.md 現在寫「副作用政策是宣告式防線，bypassPermissions 下不防蓄意」，
而候選正是跑在 bypassPermissions。`PreToolUse` hook ＋ scoped `disallowed_tools`
是**同一個目的但在 bypassPermissions 下仍成立**的機制。
「徹底隔離屬權限收斂 blocked 期」這個結論可能該往前挪。

【SDK】子代理**繼承父 session 的 permission mode**；`AgentDefinition.permissionMode`
可覆寫，**但父層是 `bypassPermissions`／`acceptEdits`／`auto` 時不可覆寫**。
文件警告：子代理的 system prompt 可能更寬鬆，繼承 bypassPermissions 等於給它完整自主系統存取。

## 8. 多租戶隔離：文件給了完整配方，而 nova 的三權分立就是多租戶

【SDK】`agent-sdk/hosting` 的隔離配方（逐條）：
```python
options = ClaudeAgentOptions(
    cwd=tenant_dir,              # 每租戶獨立工作目錄
    setting_sources=[],          # 不載任何檔案系統設定
    env={
        "CLAUDE_CONFIG_DIR": config_dir,          # 每租戶獨立 ~/.claude
        "CLAUDE_CODE_DISABLE_AUTO_MEMORY": "1",   # 關掉 auto memory
    },
)
```
再加上：`strict_mcp_config=True`（擋 claude.ai connector）、
出向 proxy 的每租戶規則。

【SDK】狀態落在本機磁碟、**不會**跨重啟存活的三種：
session transcripts（`~/.claude/projects/`）、`CLAUDE.md` memory、工作目錄產物。
`SessionStore` **只鏡像 transcript**，不含 CLAUDE.md 與工作目錄產物。

## 9. dynamic workflow 的執行語意（獨立佐證了 nova 的「小口徑」原則）

【SDK】resume 規則：重播依 agent **啟動順序**；快取停在第一個沒跑完的 agent，
**在它之後啟動的全部重跑，即使已經跑完**。
文件結論：「A workflow that fans work out across many small agents therefore
preserves more progress than one long agent.」
→ 這與 nova 的「目標檔口徑要小到一次做得完」是同一條物理，供應商自己也踩到了。

【SDK】其他硬限制：
- script **不能碰檔案系統或 shell**、不能 `import()`（只有 agent 能做事）
- 最多 **16 併發**（CPU 少時更少），單次 **1000 agent** 上限
- resume **只在同一個 Claude Code session 內**；退出就重跑
- workflow 的子代理**一律 `acceptEdits`**並繼承 tool allowlist，不管 session 模式
- fan-out 的 prompt cache：同 model／effort／agent type／tools／schema／cwd 的 agent
  共用前綴快取；Claude Code 會 hold 住後續 agent 最多
  `CLAUDE_CODE_WORKFLOW_PREFIX_STAGGER_MS`（預設 5000ms）讓它們讀到第一個的快取
- workflow agent 的快取**不在主對話的 TTL bucket**，預設 5 分鐘（`subagentPromptCacheTtl` 可設 `1h`）
- size guideline：`small`<5 ／`medium`<15（預設）／`large`<50 ／`unrestricted`

## 10. 其他對 nova 有用的零件

- **`structured_output` 的 Python 限制**：`@tool` 裝飾器**只轉發 `content` 與 `is_error`**；
  要回 `structuredContent` 得改跑獨立 MCP server。
- **`readOnlyHint`** 決定自訂工具能不能與其他唯讀工具**平行**呼叫（預設 sequential）。
- **工具錯誤不會中斷 agent loop**：handler 拋例外會被轉成 error result，Claude 看到原始訊息後繼續。
  回 `is_error: True` 才能自己組要讓 Claude 讀到的訊息。
- **`tools` vs `allowed_tools` 是兩層**：`tools` 管**可見性**（不在清單就從 context 移除），
  `allowed_tools` 管**權限**（不在清單仍可見、只是要過權限流）。
- **streaming input mode**：Python 用 `ClaudeSDKClient`。單發模式**不支援**圖片附件、
  動態排隊、即時中斷、自然多輪。Python 的 generator 例外**只記在 debug log 且 session 靜默卡住**
  ——這正是 nova 該警惕的形狀（背景卡死無聲）。
- **OTEL**：`claude_code.interaction` / `llm_request` / `tool` / `hook` span，
  子代理 span 巢狀在父 agent 的 `claude_code.tool` 底下 → **整條派工鏈是同一個 trace**。
  SDK 自動注 `TRACEPARENT` 進子程序，**並轉發給每個 Bash 指令**。
  預設不記內容；`OTEL_LOG_USER_PROMPTS` / `OTEL_LOG_TOOL_DETAILS` / `OTEL_LOG_TOOL_CONTENT`
  / `OTEL_LOG_RAW_API_BODIES` 才會記。
- **`excludeDynamicSections`**：preset 會把 cwd／是否 git repo／平台／shell／OS 版本／
  auto memory 路徑嵌進 system prompt，導致**不同工作目錄的 session 無法共用 prompt cache**。
  開這個選項會把那段挪到第一則 user message。
  → **對 nova 是直接的省錢項**：每個候選 worktree 路徑都不同，現在每爐都是 cache miss。
- **`SystemPromptFile`**：Python 把 string prompt 當**單一命令列參數**傳給 CLI 子程序，
  超過 OS 參數長度上限會在 spawn 前就失敗（Linux: `Argument list too long`）。
  大 prompt 要用 `system_prompt={"type":"file","path":...}`。
  → nova 的目標敘述會越長越大，這是個會突然爆掉的邊界。
