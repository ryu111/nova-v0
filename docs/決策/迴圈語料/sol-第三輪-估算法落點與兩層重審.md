codex
這輪我會用 `superpowers:using-superpowers` 約束技能流程；內容本身是研究與架構裁定，不是要創作或改功能，所以不啟用 brainstorming，也不動檔案。我會先把「官方基準」與「研究／標準的權威理由」分開查，尤其不把相鄰概念誤報成直接證成。
exec
/bin/zsh -lc "sed -n '1,240p' /Users/sbu/.codex/plugins/cache/openai-curated-remote/superpowers/6.3.0/skills/using-superpowers/SKILL.md" in /Users/sbu/nova
 succeeded in 0ms:
---
name: using-superpowers
description: Use when starting any conversation - establishes how to find and use skills, requiring skill invocation before ANY response including clarifying questions
---

<SUBAGENT-STOP>
If you were dispatched as a subagent to execute a specific task, ignore this skill.
</SUBAGENT-STOP>

<EXTREMELY-IMPORTANT>
If you think there is even a 1% chance a skill might apply to what you are doing, you ABSOLUTELY MUST invoke the skill.

IF A SKILL APPLIES TO YOUR TASK, YOU DO NOT HAVE A CHOICE. YOU MUST USE IT.

This is not negotiable. You cannot rationalize your way out of this.
</EXTREMELY-IMPORTANT>

## The Rule

**Invoke relevant or requested skills BEFORE any response or action** — including clarifying questions, exploring the codebase, or checking files. If it turns out wrong for the situation, you don't have to use it.

**Before entering plan mode:** if you haven't already brainstormed, invoke the brainstorming skill first.

Then announce "Using [skill] to [purpose]" and follow the skill exactly. If it has a checklist, create a todo per item.

## Skill Priority

When multiple skills apply, process skills come first — they set the approach, then implementation skills (frontend-design, etc.) carry it out. Brainstorming and systematic-debugging are Superpowers' most common process skills, but the rule holds for any of them.

- "Let's build X" → superpowers:brainstorming first, then implementation skills.
- "Fix this bug" → superpowers:systematic-debugging first, then domain skills.

## Red Flags

These thoughts mean STOP—you're rationalizing:

| Thought | Reality |
|---------|---------|
| "This is just a simple question" | Questions are tasks. Check for skills. |
| "I need more context first" | Skill check comes BEFORE clarifying questions. |
| "Let me explore the codebase first" | Skills tell you HOW to explore. Check first. |
| "I can check git/files quickly" | Files lack conversation context. Check for skills. |
| "Let me gather information first" | Skills tell you HOW to gather information. |
| "This doesn't need a formal skill" | If a skill exists, use it. |
| "I remember this skill" | Skills evolve. Read current version. |
| "This doesn't count as a task" | Action = task. Check for skills. |
| "The skill is overkill" | Simple things become complex. Use it. |
| "I'll just do this one thing first" | Check BEFORE doing anything. |
| "This feels productive" | Undisciplined action wastes time. Skills prevent this. |
| "I know what that means" | Knowing the concept ≠ using the skill. Invoke it. |

## Platform Adaptation

If your harness appears here, read its reference file for special instructions:

- Codex: `references/codex-tools.md`
- Pi: `references/pi-tools.md`
- Antigravity: `references/antigravity-tools.md`
- Hermes Agent: `references/hermes-tools.md`

## User Instructions

User instructions (CLAUDE.md, AGENTS.md, GEMINI.md, etc, direct requests) take precedence over skills, which in turn override default behavior. Only skip skill workflows or instructions when your human partner has explicitly told you to.

exec
/bin/zsh -lc "sed -n '1,260p' /Users/sbu/.codex/plugins/cache/openai-curated-remote/superpowers/6.3.0/skills/using-superpowers/references/codex-tools.md" in /Users/sbu/nova
 succeeded in 0ms:
## Subagent dispatch requires multi-agent support

Add to your Codex config (`~/.codex/config.toml`):

```toml
[features]
multi_agent = true
```

This enables the multi-agent tools that skills like
`dispatching-parallel-agents` and `subagent-driven-development` use.
Which tools you get depends on the multi-agent version your model
preset selects (current presets run V2; older ones run V1). Trust your
actual tool list over any table — including this one — when they
disagree.

- **Spawning:** give children a clean context with
  `spawn_agent {fork_turns: "none"}`; the default `"all"` copies your
  entire transcript into the child. On Codex 0.145+, role files under
  `~/.codex/agents/` attach to isolated forks via `agent_type`.
  Full-history forks accept `model` and `reasoning_effort` overrides
  (only `agent_type` is refused there) — isolated forks are the SDD
  default for context hygiene, not because overrides require them.
- **Fix rounds:** resume the implementer with `followup_task` — it
  delivers your message, triggers a turn, and transparently reloads a
  child the harness evicted. Never dispatch a fresh implementer on the
  theory that a spawned agent cannot be messaged again; on V2 it
  always can.
- **Lifecycle:** V2 has no `close_agent`. Finished children are
  evicted automatically when slots are needed; leaving them unclosed
  costs nothing. Only V1 sessions have `close_agent` — there, close
  reviewers when their review returns, and close each implementer
  after its task's review passes.
- **Model names:** never copy a model name from a skill, table, or old
  session into `spawn_agent` without checking it against your current
  spawn allowlist — V2 accepts only V2-capable presets and hard-errors
  on the rest.

## Waiting on children

`wait_agent` is an event subscription, not a poll: a long wait wakes
the moment a child produces mailbox activity, with the same latency as
a short one. Short-timeout polling buys nothing and costs a tool call —
and a context rebill — per poll. In measured sessions, roughly
two-thirds of all wait calls were short polls that timed out.

- While you still have local work, do not wait at all. A completed
  child's final answer is pushed into your mailbox and arrives with
  your next turn.
- When you are genuinely idle with children outstanding, wait in
  bounded stretches: `wait_agent` with `timeout_ms` 300000-600000
  (5-10 minutes). After each stretch — wake or timeout — post one
  status line, run `list_agents`, and chase any child that finished
  without reporting. Never stack polls shorter than five minutes; the
  event subscription wakes a bounded stretch just as fast as a short
  one.
- Completion mail cannot wake an idle controller (it is delivered
  without triggering a turn); covering that idle window is
  `wait_agent`'s only job. A stretch that times out with no activity
  is your cue to reconcile, not to shorten the next stretch.

## Model routing on spawns

Every `spawn_agent` you issue — including when you are yourself a
spawned child running a fan-out — sets `model` AND `reasoning_effort`
explicitly, per the Model Selection rules of the skill you are
executing. Setting `model` alone is a trap: the child's effort
silently resets to that model's default, not to yours.

Ask your human partner to add a machine-level backstop to
`~/.codex/config.toml` so any spawn that slips through still routes to
a deliberate tier instead of silently inheriting the session's most
expensive model:

```toml
[agents]
default_subagent_model = "<a mid-tier model from your spawn allowlist>"
default_subagent_reasoning_effort = "medium"
```

## Environment Detection

Skills that create worktrees or finish branches should detect their
environment with read-only git commands before proceeding:

```bash
GIT_DIR=$(cd "$(git rev-parse --git-dir)" 2>/dev/null && pwd -P)
GIT_COMMON=$(cd "$(git rev-parse --git-common-dir)" 2>/dev/null && pwd -P)
BRANCH=$(git branch --show-current)
```

- `GIT_DIR != GIT_COMMON` → already in a linked worktree (skip creation)
- `BRANCH` empty → detached HEAD (cannot branch/push/PR from sandbox)

See `using-git-worktrees` Step 0 and `finishing-a-development-branch`
Step 1 for how each skill uses these signals.

## Codex App Finishing

When the sandbox blocks branch/push operations (detached HEAD in an
externally managed worktree), the agent commits all work and informs
the user to use the App's native controls:

- **"Create branch"** — names the branch, then commit/push/PR via App UI
- **"Hand off to local"** — transfers work to the user's local checkout

The agent can still run tests, stage files, and output suggested branch
names, commit messages, and PR descriptions for the user to copy.

web search: 
web search: scientific workflows reproducibility task node replay provenance workflow official paper DOI ...
web search: 
web search: Clark Wilson integrity model separation of duty DOI summary ...
web search: 
web search: NIST AI evaluation repeatability reproducibility metrics official ...
web search: 
web search: noninferiority trial confidence interval margin paired design authoritative FDA guidance ...
codex
初步校正已經很明確：你把「token 上界＋品質下界」叫成單一非劣性檢定，只說對了一半。品質那側是非劣性；token 那側是優越性或資源上界檢定。整體是有共同決策規則的雙端點、交集聯立判準，不能用一個平均值或一個 p-value 代替。接下來我會對照現在的計畫所有權，避免建議落點撞到既有 Create。
exec
/bin/zsh -lc 'rg -n "''^#|''^##|''^###|前置計畫|File Structure|Create:|RankingSchema|評估|度量|benchmark|基準" docs/計畫/00-總覽.md docs/計畫/07-* docs/計畫/09-* docs/計畫/10-* docs/計畫/19-* docs/計畫/20-* | head -n 500' in /Users/sbu/nova
 succeeded in 0ms:
docs/計畫/00-總覽.md:1:# nova 重做實作計畫總覽
docs/計畫/00-總覽.md:13:## Global Constraints
docs/計畫/00-總覽.md:21:- 【推論】新檔案必須先出現在active plan的`Create:`且恰命中一條`架構/目錄規則.toml`；未預見的新檔不能先落地再找理由。
docs/計畫/00-總覽.md:28:## 1. Brainstorming：拆法與採用理由
docs/計畫/00-總覽.md:30:【查證】官方 `brainstorming` 要求大型架構先拆成彼此可理解、可獨立測試的 sub-project；`writing-plans` 要求每個獨立子系統一份 plan，且 task 之前先鎖 File Structure。（來源：[brainstorming SKILL.md](https://github.com/obra/superpowers/blob/main/skills/brainstorming/SKILL.md)、[writing-plans SKILL.md](https://github.com/obra/superpowers/blob/main/skills/writing-plans/SKILL.md)。）
docs/計畫/00-總覽.md:42:## 2. 定期整併的新裁決：合併 representation，不縮 obligation
docs/計畫/00-總覽.md:81:## 3. 子系統清單
docs/計畫/00-總覽.md:91:| 06 | [判準評估與隔離回饋](./06-判準評估與隔離回饋.md) | 【推論】CriterionVersion／Evaluation、capability negotiation、雙測試池與 clause reducer 可獨立裁定。 | 【推論】01–05。 |
docs/計畫/00-總覽.md:109:## 4. 依賴圖
docs/計畫/00-總覽.md:149:## 5. 建議執行階段
docs/計畫/00-總覽.md:151:### Phase A：能力假設、三個信任根與持久證據（01、01B、02–04）
docs/計畫/00-總覽.md:157:### Phase B：可工作的領域核心（05–12）
docs/計畫/00-總覽.md:161:### Phase C：單一入口、外部世界與 view（13–18）
docs/計畫/00-總覽.md:165:### Phase D：反向力量與總驗收（19–20）
docs/計畫/00-總覽.md:171:## 6. 多執行者、角色分權與最晚裁定點
docs/計畫/00-總覽.md:173:### 6.1 多 writer 協調規則
docs/計畫/00-總覽.md:185:### 6.2 已證成的可平行點
docs/計畫/00-總覽.md:197:### 6.3 四種角色與唯一 acceptance authority
docs/計畫/00-總覽.md:208:### 6.4 執行者分派原則
docs/計畫/00-總覽.md:220:### 6.5 可以邊做邊定，但有最晚裁定點
docs/計畫/00-總覽.md:237:### 6.6 Day-one工程規範與資料夾落點已裁定
docs/計畫/00-總覽.md:262:【推論】placement decision依序問「是否transport→use case→垂直生命週期→橫向政策權威→generic machine→external adapter→infrastructure→leaf value→composition」。一檔命中兩項表示它有兩個變更原因，必須拆；不得用例外清單掩蓋。`架構/檢查工程規範.py`以path manifest、plan `Create:` catalog與AST import graph機械執法。
docs/計畫/00-總覽.md:266:### 6.7 本地9B可立即當開發執行者，但不是提前實作plan 17
docs/計畫/00-總覽.md:280:## 7. 前置未完成時會怎麼壞
docs/計畫/00-總覽.md:303:## 8. 全域 ClaimSpec 覆蓋規則
docs/計畫/00-總覽.md:313:## 9. Execution Handoff
docs/計畫/10-知識治理與快照.md:1:# 知識治理與快照 Implementation Plan
docs/計畫/10-知識治理與快照.md:13:## Global Constraints
docs/計畫/10-知識治理與快照.md:23:## 子系統規格
docs/計畫/10-知識治理與快照.md:37:## File Structure
docs/計畫/10-知識治理與快照.md:84:## Dependency Gate
docs/計畫/10-知識治理與快照.md:86:前置計畫：01 02 03 04 09
docs/計畫/10-知識治理與快照.md:92:### Task 1: 宣告 KnowledgeAssertion machine 與封閉 schema
docs/計畫/10-知識治理與快照.md:95:- Create: `規格/知識/知識.machine.json`
docs/計畫/10-知識治理與快照.md:96:- Create: `規格/知識/KnowledgeAssertion.schema.json`
docs/計畫/10-知識治理與快照.md:97:- Create: `規格/知識/初始知識政策.policy.json`
docs/計畫/10-知識治理與快照.md:98:- Create: `nova/權威/知識/模型.py`
docs/計畫/10-知識治理與快照.md:99:- Create: `nova/權威/知識/准入.py`
docs/計畫/10-知識治理與快照.md:100:- Create: `nova/權威/知識/端口.py`
docs/計畫/10-知識治理與快照.md:101:- Create: `nova/權威/知識/test_知識權威.py`
docs/計畫/10-知識治理與快照.md:148:### Task 2: 封死執行者自我准入
docs/計畫/10-知識治理與快照.md:151:- Create: `nova/應用/提案知識.py`
docs/計畫/10-知識治理與快照.md:152:- Create: `nova/應用/審核知識.py`
docs/計畫/10-知識治理與快照.md:153:- Create: `nova/應用/test_知識服務.py`
docs/計畫/10-知識治理與快照.md:154:- Create: `驗收/知識/測_准入邊界.py`
docs/計畫/10-知識治理與快照.md:155:- Create: `規格/知識/保證/執行者只能提案.claim.json`
docs/計畫/10-知識治理與快照.md:205:### Task 3: 建立可追溯的來源與衍生圖
docs/計畫/10-知識治理與快照.md:208:- Create: `nova/權威/知識/來源圖.py`
docs/計畫/10-知識治理與快照.md:261:### Task 4: 只從 ACTIVE assertions 建立 immutable snapshot
docs/計畫/10-知識治理與快照.md:264:- Create: `規格/知識/KnowledgeSnapshot.schema.json`
docs/計畫/10-知識治理與快照.md:265:- Create: `nova/權威/知識/檢索.py`
docs/計畫/10-知識治理與快照.md:266:- Create: `nova/權威/知識/快照.py`
docs/計畫/10-知識治理與快照.md:267:- Create: `nova/應用/建立知識快照.py`
docs/計畫/10-知識治理與快照.md:268:- Create: `驗收/知識/測_快照重播.py`
docs/計畫/10-知識治理與快照.md:269:- Create: `規格/知識/保證/未准入不可取用.claim.json`
docs/計畫/10-知識治理與快照.md:270:- Create: `規格/知識/保證/快照可重播.claim.json`
docs/計畫/10-知識治理與快照.md:317:### Task 5: 傳遞來源撤銷並通知在途 Work
docs/計畫/10-知識治理與快照.md:320:- Create: `nova/權威/知識/撤銷.py`
docs/計畫/10-知識治理與快照.md:321:- Create: `nova/應用/撤銷知識.py`
docs/計畫/10-知識治理與快照.md:323:- Create: `驗收/知識/測_撤銷傳遞.py`
docs/計畫/10-知識治理與快照.md:324:- Create: `規格/知識/保證/撤銷傳遞.claim.json`
docs/計畫/10-知識治理與快照.md:370:### Task 6: 讓索引可丟棄重建且不成第二份真相
docs/計畫/10-知識治理與快照.md:373:- Create: `nova/基礎設施/知識索引/sqlite.py`
docs/計畫/10-知識治理與快照.md:374:- Create: `nova/基礎設施/知識索引/重建.py`
docs/計畫/10-知識治理與快照.md:375:- Create: `nova/基礎設施/知識索引/test_索引.py`
docs/計畫/10-知識治理與快照.md:424:### Task 7: 機械阻止知識跨權威越寫
docs/計畫/10-知識治理與快照.md:427:- Create: `驗收/知識/測_跨權威越界.py`
docs/計畫/10-知識治理與快照.md:428:- Create: `規格/知識/保證/知識不得越權.claim.json`
docs/計畫/10-知識治理與快照.md:477:### Task 8: 固定 deterministic query policy 與索引重建語義
docs/計畫/10-知識治理與快照.md:480:- Create: `規格/知識/RetrievalSelectionPolicy.schema.json`
docs/計畫/10-知識治理與快照.md:481:- Create: `規格/知識/保證/範圍圖全量決定性.claim.json`
docs/計畫/10-知識治理與快照.md:482:- Create: `規格/知識/保證/索引重建語義同一.claim.json`
docs/計畫/10-知識治理與快照.md:483:- Create: `驗收/知識/測_決定性檢索政策.py`
docs/計畫/10-知識治理與快照.md:534:### Task 9: 拒絕context截斷、限制cache並建立retrieval反轉閘
docs/計畫/10-知識治理與快照.md:537:- Create: `規格/知識/保證/知識上下文不得靜默截斷.claim.json`
docs/計畫/10-知識治理與快照.md:538:- Create: `規格/知識/保證/快取只准加速.claim.json`
docs/計畫/10-知識治理與快照.md:539:- Create: `驗收/知識/測_retrieval反轉門檻.py`
docs/計畫/10-知識治理與快照.md:583:## Plan Exit Gate
docs/計畫/10-知識治理與快照.md:595:## Execution Handoff
docs/計畫/07-資源預算與供應商額度.md:1:# 資源預算與供應商額度 Implementation Plan
docs/計畫/07-資源預算與供應商額度.md:13:## Global Constraints
docs/計畫/07-資源預算與供應商額度.md:25:## 子系統規格
docs/計畫/07-資源預算與供應商額度.md:33:## File Structure
docs/計畫/07-資源預算與供應商額度.md:75:## Dependency Gate
docs/計畫/07-資源預算與供應商額度.md:77:前置計畫：01 02 03 04 05
docs/計畫/07-資源預算與供應商額度.md:83:### Task 1: 宣告 BudgetReservation machine 與整數帳
docs/計畫/07-資源預算與供應商額度.md:86:- Create: `規格/資源/資源保留.machine.json`
docs/計畫/07-資源預算與供應商額度.md:87:- Create: `nova/權威/資源/預算帳.py`
docs/計畫/07-資源預算與供應商額度.md:88:- Create: `nova/權威/資源/test_資源權威.py`
docs/計畫/07-資源預算與供應商額度.md:89:- Create: `nova/應用/保留資源.py`
docs/計畫/07-資源預算與供應商額度.md:90:- Create: `nova/應用/核銷資源.py`
docs/計畫/07-資源預算與供應商額度.md:91:- Create: `nova/應用/test_資源命令.py`
docs/計畫/07-資源預算與供應商額度.md:138:### Task 2: 釘住每筆 reservation 的 RateCard revision
docs/計畫/07-資源預算與供應商額度.md:141:- Create: `規格/資源/初始計價.policy.json`
docs/計畫/07-資源預算與供應商額度.md:142:- Create: `nova/權威/資源/計價.py`
docs/計畫/07-資源預算與供應商額度.md:144:- Create: `驗收/資源/測_計價與分配釘版.py`
docs/計畫/07-資源預算與供應商額度.md:145:- Create: `規格/資源/保證/計價逐保留釘版.claim.json`
docs/計畫/07-資源預算與供應商額度.md:146:- Create: `規格/資源/保證/後端成本一致.claim.json`
docs/計畫/07-資源預算與供應商額度.md:196:### Task 3: 建立 per-bucket 五態且不捏造 reset 後餘額
docs/計畫/07-資源預算與供應商額度.md:199:- Create: `規格/資源/供應商額度.machine.json`
docs/計畫/07-資源預算與供應商額度.md:200:- Create: `nova/權威/資源/額度觀測.py`
docs/計畫/07-資源預算與供應商額度.md:202:- Create: `驗收/資源/測_供應商額度五態.py`
docs/計畫/07-資源預算與供應商額度.md:203:- Create: `規格/資源/保證/額度五態誠實.claim.json`
docs/計畫/07-資源預算與供應商額度.md:255:### Task 4: 實作 metric gate 與 bucket topology
docs/計畫/07-資源預算與供應商額度.md:258:- Create: `規格/資源/額度拓撲.policy.json`
docs/計畫/07-資源預算與供應商額度.md:259:- Create: `nova/權威/資源/額度拓撲.py`
docs/計畫/07-資源預算與供應商額度.md:260:- Create: `nova/權威/資源/資格閘.py`
docs/計畫/07-資源預算與供應商額度.md:261:- Create: `驗收/資源/測_額度拓撲.py`
docs/計畫/07-資源預算與供應商額度.md:262:- Create: `規格/資源/保證/百分比額度有界.claim.json`
docs/計畫/07-資源預算與供應商額度.md:263:- Create: `規格/資源/保證/額度窗口拓撲.claim.json`
docs/計畫/07-資源預算與供應商額度.md:304:git commit -m "feat: 誠實評估額度指標與拓樸"
docs/計畫/07-資源預算與供應商額度.md:309:### Task 5: 讓 stale/rolled/cold observation probe 單飛且可恢復
docs/計畫/07-資源預算與供應商額度.md:315:- Create: `規格/資源/保證/額度探針單飛.claim.json`
docs/計畫/07-資源預算與供應商額度.md:362:### Task 6: 保留無 observation capability 的 blind fallback
docs/計畫/07-資源預算與供應商額度.md:365:- Create: `nova/權威/資源/盲派斷路.py`
docs/計畫/07-資源預算與供應商額度.md:367:- Create: `驗收/資源/測_盲派斷路.py`
docs/計畫/07-資源預算與供應商額度.md:368:- Create: `規格/資源/保證/不可觀測盲派單飛.claim.json`
docs/計畫/07-資源預算與供應商額度.md:417:### Task 7: 版本化 allocation policy 並對 Work 釘版
docs/計畫/07-資源預算與供應商額度.md:420:- Create: `規格/資源/初始後端分配.policy.json`
docs/計畫/07-資源預算與供應商額度.md:421:- Create: `nova/權威/資源/分配政策.py`
docs/計畫/07-資源預算與供應商額度.md:422:- Create: `nova/權威/資源/加權排程.py`
docs/計畫/07-資源預算與供應商額度.md:423:- Create: `nova/應用/調整後端比例.py`
docs/計畫/07-資源預算與供應商額度.md:426:- Create: `規格/資源/保證/分配政策逐工作釘版.claim.json`
docs/計畫/07-資源預算與供應商額度.md:474:### Task 8: 合成 live hard eligibility 並發布誠實事件
docs/計畫/07-資源預算與供應商額度.md:479:- Create: `驗收/資源/測_先保留後花費.py`
docs/計畫/07-資源預算與供應商額度.md:480:- Create: `規格/資源/保證/先保留後花費.claim.json`
docs/計畫/07-資源預算與供應商額度.md:530:### Task 9: 對 delegation tree 做完整 reserve 與核銷
docs/計畫/07-資源預算與供應商額度.md:537:- Create: `驗收/資源/測_代理樹成本.py`
docs/計畫/07-資源預算與供應商額度.md:538:- Create: `規格/資源/保證/代理樹成本不遺漏.claim.json`
docs/計畫/07-資源預算與供應商額度.md:563:## Plan Exit Gate
docs/計畫/07-資源預算與供應商額度.md:573:## Execution Handoff
docs/計畫/09-持久工作協調與選拔.md:1:# 持久工作協調與選拔 Implementation Plan
docs/計畫/09-持久工作協調與選拔.md:13:## Global Constraints
docs/計畫/09-持久工作協調與選拔.md:23:## 子系統規格
docs/計畫/09-持久工作協調與選拔.md:25:【推論】`RankingSchema` 是 ordered nonempty dimensions：每維必填 `score_id`、`value_type=INTEGER|DECIMAL`、`direction=ASC|DESC`、`missing=REJECT_CANDIDATE`；維度全相同時以 candidate digest ASCII ascending tie-break。自由文字不能參與 comparator。
docs/計畫/09-持久工作協調與選拔.md:31:## File Structure
docs/計畫/09-持久工作協調與選拔.md:37:├── RankingSchema.schema.json                 — ordered typed score dimensions。
docs/計畫/09-持久工作協調與選拔.md:76:## Dependency Gate
docs/計畫/09-持久工作協調與選拔.md:78:前置計畫：01 02 03 04 05 06 07 08
docs/計畫/09-持久工作協調與選拔.md:84:### Task 1: 宣告 Work machine、bounds 與 pinned creation contract
docs/計畫/09-持久工作協調與選拔.md:87:- Create: `規格/工作/工作.machine.json`
docs/計畫/09-持久工作協調與選拔.md:88:- Create: `規格/工作/WorkRequest.schema.json`
docs/計畫/09-持久工作協調與選拔.md:89:- Create: `nova/領域/工作/公開契約.py`
docs/計畫/09-持久工作協調與選拔.md:90:- Create: `nova/領域/工作/模型.py`
docs/計畫/09-持久工作協調與選拔.md:91:- Create: `nova/領域/工作/決策.py`
docs/計畫/09-持久工作協調與選拔.md:92:- Create: `nova/領域/工作/端口.py`
docs/計畫/09-持久工作協調與選拔.md:93:- Create: `nova/領域/工作/test_工作決策.py`
docs/計畫/09-持久工作協調與選拔.md:94:- Create: `nova/應用/建立工作.py`
docs/計畫/09-持久工作協調與選拔.md:95:- Create: `nova/應用/test_工作服務.py`
docs/計畫/09-持久工作協調與選拔.md:147:### Task 2: 用 FlowSpec 封死父子基數並拒絕一般 DAG
docs/計畫/09-持久工作協調與選拔.md:150:- Create: `規格/組合/軟體工程工作.flow.json`
docs/計畫/09-持久工作協調與選拔.md:151:- Create: `驗收/三層流程/測_父子非DAG.py`
docs/計畫/09-持久工作協調與選拔.md:152:- Create: `規格/工作/保證/父子非任意圖.claim.json`
docs/計畫/09-持久工作協調與選拔.md:197:### Task 3: 實作 portfolio fan-out 與原子 budget slicing
docs/計畫/09-持久工作協調與選拔.md:202:- Create: `nova/應用/推進工作.py`
docs/計畫/09-持久工作協調與選拔.md:204:- Create: `驗收/三層流程/測_平行追求.py`
docs/計畫/09-持久工作協調與選拔.md:250:### Task 4: 建立 deterministic BEST_BEFORE_DEADLINE 選拔
docs/計畫/09-持久工作協調與選拔.md:253:- Create: `規格/工作/最佳截止前.policy.json`
docs/計畫/09-持久工作協調與選拔.md:254:- Create: `規格/工作/RankingSchema.schema.json`
docs/計畫/09-持久工作協調與選拔.md:255:- Create: `nova/領域/工作/選拔.py`
docs/計畫/09-持久工作協調與選拔.md:256:- Create: `nova/領域/工作/test_選拔.py`
docs/計畫/09-持久工作協調與選拔.md:258:- Create: `驗收/三層流程/測_選拔截止.py`
docs/計畫/09-持久工作協調與選拔.md:259:- Create: `規格/工作/保證/最佳截止前選拔.claim.json`
docs/計畫/09-持久工作協調與選拔.md:298:git add 規格/工作/最佳截止前.policy.json 規格/工作/RankingSchema.schema.json 規格/工作/保證/最佳截止前選拔.claim.json nova/領域/工作/選拔.py nova/領域/工作/test_選拔.py nova/領域/工作/決策.py 驗收/三層流程/測_選拔截止.py
docs/計畫/09-持久工作協調與選拔.md:304:### Task 5: 固定 cutoff、取消 losers 與 5 秒 kill grace
docs/計畫/09-持久工作協調與選拔.md:356:### Task 6: 強制 7 天 absolute deadline 與 8,192 event terminal reserve
docs/計畫/09-持久工作協調與選拔.md:362:- Create: `驗收/三層流程/測_一定停止.py`
docs/計畫/09-持久工作協調與選拔.md:363:- Create: `規格/工作/保證/七天絕對期限.claim.json`
docs/計畫/09-持久工作協調與選拔.md:364:- Create: `規格/工作/保證/工作事件上限.claim.json`
docs/計畫/09-持久工作協調與選拔.md:412:### Task 7: 實作持久佇列、公平租約與全程序恢復
docs/計畫/09-持久工作協調與選拔.md:415:- Create: `nova/基礎設施/排程/持久佇列.py`
docs/計畫/09-持久工作協調與選拔.md:416:- Create: `nova/基礎設施/排程/worker.py`
docs/計畫/09-持久工作協調與選拔.md:417:- Create: `nova/基礎設施/排程/test_持久佇列.py`
docs/計畫/09-持久工作協調與選拔.md:419:- Create: `驗收/三層流程/測_全程序重啟.py`
docs/計畫/09-持久工作協調與選拔.md:420:- Create: `規格/工作/保證/崩潰重建.claim.json`
docs/計畫/09-持久工作協調與選拔.md:468:### Task 8: 讓健康缺陷只能提案普通維護 Work
docs/計畫/09-持久工作協調與選拔.md:471:- Create: `規格/組合/自我維護.flow.json`
docs/計畫/09-持久工作協調與選拔.md:472:- Create: `nova/領域/工作/維護提案.py`
docs/計畫/09-持久工作協調與選拔.md:473:- Create: `nova/應用/建立維護工作.py`
docs/計畫/09-持久工作協調與選拔.md:475:- Create: `驗收/三層流程/測_自我維護.py`
docs/計畫/09-持久工作協調與選拔.md:476:- Create: `規格/工作/保證/自我維護提案.claim.json`
docs/計畫/09-持久工作協調與選拔.md:521:## Plan Exit Gate
docs/計畫/09-持久工作協調與選拔.md:530:## Execution Handoff
docs/計畫/19-定期整併.md:1:# 定期整併 Implementation Plan
docs/計畫/19-定期整併.md:13:## Global Constraints
docs/計畫/19-定期整併.md:25:## 子系統規格
docs/計畫/19-定期整併.md:35:## File Structure
docs/計畫/19-定期整併.md:84:├── 評估整併.py                              — 呼叫 carried ClaimSpecs 與 controls。
docs/計畫/19-定期整併.md:99:## Dependency Gate
docs/計畫/19-定期整併.md:101:前置計畫：01 02 03 04 05 06 07 08 09 10 11 12 13
docs/計畫/19-定期整併.md:107:### Task 1: 建立不可變 GuaranteeObligation 與 ClaimCoverage
docs/計畫/19-定期整併.md:110:- Create: `規格/整併/GuaranteeObligation.schema.json`
docs/計畫/19-定期整併.md:111:- Create: `規格/整併/ClaimCoverage.schema.json`
docs/計畫/19-定期整併.md:112:- Create: `nova/權威/判準/保證義務.py`
docs/計畫/19-定期整併.md:113:- Create: `驗收/定期整併/測_義務與覆蓋.py`
docs/計畫/19-定期整併.md:114:- Create: `規格/整併/保證/義務識別不可變.claim.json`
docs/計畫/19-定期整併.md:170:### Task 2: 封閉 ClaimMergeSpec 的表達力與 blast radius
docs/計畫/19-定期整併.md:173:- Create: `規格/整併/ClaimMergeSpec.schema.json`
docs/計畫/19-定期整併.md:174:- Create: `nova/權威/判準/保證合併.py`
docs/計畫/19-定期整併.md:175:- Create: `nova/權威/判準/test_保證合併.py`
docs/計畫/19-定期整併.md:176:- Create: `驗收/定期整併/測_保證合併.py`
docs/計畫/19-定期整併.md:177:- Create: `規格/整併/保證/合併形態有界.claim.json`
docs/計畫/19-定期整併.md:239:### Task 3: 驗證 obligation inclusion 與固定 controls 原封承接
docs/計畫/19-定期整併.md:245:- Create: `規格/整併/保證/義務覆蓋不得縮減.claim.json`
docs/計畫/19-定期整併.md:246:- Create: `規格/整併/保證/固定負控原封承接.claim.json`
docs/計畫/19-定期整併.md:299:### Task 4: 指定突變不得被raw擊殺率取代
docs/計畫/19-定期整併.md:302:- Create: `規格/整併/保證/指定突變不看擊殺率.claim.json`
docs/計畫/19-定期整併.md:352:### Task 5: 原子啟用 successor 並把 sources 轉成可解析 alias
docs/計畫/19-定期整併.md:356:- Create: `nova/應用/准入整併.py`
docs/計畫/19-定期整併.md:357:- Create: `驗收/定期整併/測_alias與崩潰.py`
docs/計畫/19-定期整併.md:358:- Create: `規格/整併/保證/alias原子生效.claim.json`
docs/計畫/19-定期整併.md:416:### Task 6: 封住一 Work 一 merge 與 Guard 逃生非增加預算
docs/計畫/19-定期整併.md:419:- Create: `規格/整併/簡化工作.machine.json`
docs/計畫/19-定期整併.md:420:- Create: `nova/領域/工作/整併.py`
docs/計畫/19-定期整併.md:421:- Create: `nova/領域/工作/test_整併工作.py`
docs/計畫/19-定期整併.md:424:- Create: `規格/整併/保證/逃生預算不得增加.claim.json`
docs/計畫/19-定期整併.md:425:- Create: `規格/整併/保證/一工作一合併.claim.json`
docs/計畫/19-定期整併.md:479:### Task 7: 只記錄 structural signals，手動階段邊界才提案
docs/計畫/19-定期整併.md:482:- Create: `規格/整併/SimplificationTriggerPolicy.schema.json`
docs/計畫/19-定期整併.md:483:- Create: `規格/整併/手動階段邊界.policy.json`
docs/計畫/19-定期整併.md:484:- Create: `nova/維護/複雜度訊號.py`
docs/計畫/19-定期整併.md:485:- Create: `nova/維護/審查提案.py`
docs/計畫/19-定期整併.md:486:- Create: `nova/維護/test_訊號與提案.py`
docs/計畫/19-定期整併.md:487:- Create: `驗收/定期整併/測_訊號與review.py`
docs/計畫/19-定期整併.md:488:- Create: `規格/整併/保證/觸發只提案.claim.json`
docs/計畫/19-定期整併.md:539:### Task 8: review與ApplicationBoundary只能提出typed整併工作
docs/計畫/19-定期整併.md:542:- Create: `規格/介面/命令/提案整併.schema.json`
docs/計畫/19-定期整併.md:543:- Create: `規格/整併/保證/整併命令封閉.claim.json`
docs/計畫/19-定期整併.md:544:- Create: `規格/整併/保證/review只能提案.claim.json`
docs/計畫/19-定期整併.md:545:- Create: `nova/應用/提案整併.py`
docs/計畫/19-定期整併.md:546:- Create: `nova/應用/處理/整併.py`
docs/計畫/19-定期整併.md:598:### Task 9: 把真正的需求撤銷隔離成短效授權工作
docs/計畫/19-定期整併.md:601:- Create: `規格/整併/RequirementRevocation.schema.json`
docs/計畫/19-定期整併.md:602:- Create: `規格/整併/需求變更.machine.json`
docs/計畫/19-定期整併.md:603:- Create: `規格/組合/需求變更.flow.json`
docs/計畫/19-定期整併.md:604:- Create: `nova/權威/判準/需求撤銷.py`
docs/計畫/19-定期整併.md:605:- Create: `nova/領域/工作/需求變更.py`
docs/計畫/19-定期整併.md:607:- Create: `nova/應用/提案需求變更.py`
docs/計畫/19-定期整併.md:608:- Create: `驗收/定期整併/測_需求撤銷.py`
docs/計畫/19-定期整併.md:609:- Create: `規格/整併/保證/撤銷需求另走授權.claim.json`
docs/計畫/19-定期整併.md:665:### Task 10: 將需求變更commands綁exact Work revision
docs/計畫/19-定期整併.md:668:- Create: `規格/介面/命令/需求變更.schema.json`
docs/計畫/19-定期整併.md:669:- Create: `規格/整併/保證/需求變更命令綁定.claim.json`
docs/計畫/19-定期整併.md:670:- Create: `nova/應用/處理/需求變更.py`
docs/計畫/19-定期整併.md:716:### Task 11: 跑完整 SimplificationWork 與兩 claim 合一固定案例
docs/計畫/19-定期整併.md:719:- Create: `規格/組合/定期整併.flow.json`
docs/計畫/19-定期整併.md:720:- Create: `規格/介面/命令/裁決整併.schema.json`
docs/計畫/19-定期整併.md:721:- Create: `規格/整併/保證/端到端不退保.claim.json`
docs/計畫/19-定期整併.md:722:- Create: `nova/應用/評估整併.py`
docs/計畫/19-定期整併.md:724:- Create: `nova/應用/test_整併服務.py`
docs/計畫/19-定期整併.md:725:- Create: `驗收/定期整併/測_完整整併工作.py`
docs/計畫/19-定期整併.md:753:Expected: 【推論】FAIL with missing `評估整併` service／flow binding。
docs/計畫/19-定期整併.md:772:git add 規格/組合/定期整併.flow.json 規格/介面/命令/裁決整併.schema.json 規格/整併/保證/端到端不退保.claim.json nova/應用/評估整併.py nova/應用/准入整併.py nova/應用/處理/整併.py nova/應用/登錄.py nova/應用/test_整併服務.py 驗收/定期整併/測_完整整併工作.py
docs/計畫/19-定期整併.md:776:## Exit Gate
docs/計畫/19-定期整併.md:780:## Execution Handoff
docs/計畫/20-整體組裝與跨系統驗收.md:1:# 整體組裝與跨系統驗收 Implementation Plan
docs/計畫/20-整體組裝與跨系統驗收.md:13:## Global Constraints
docs/計畫/20-整體組裝與跨系統驗收.md:25:## 子系統規格
docs/計畫/20-整體組裝與跨系統驗收.md:35:## File Structure
docs/計畫/20-整體組裝與跨系統驗收.md:95:## Dependency Gate
docs/計畫/20-整體組裝與跨系統驗收.md:97:前置計畫：01 01B 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19
docs/計畫/20-整體組裝與跨系統驗收.md:103:### Task 1: 建立 exact-digest spec catalog 與 bootstrap closure
docs/計畫/20-整體組裝與跨系統驗收.md:106:- Create: `規格/語言/規格目錄.schema.json`
docs/計畫/20-整體組裝與跨系統驗收.md:107:- Create: `規格/目錄.json`
docs/計畫/20-整體組裝與跨系統驗收.md:108:- Create: `nova/狀態機/目錄.py`
docs/計畫/20-整體組裝與跨系統驗收.md:109:- Create: `nova/狀態機/test_目錄.py`
docs/計畫/20-整體組裝與跨系統驗收.md:111:- Create: `架構/test_規格引用.py`
docs/計畫/20-整體組裝與跨系統驗收.md:112:- Create: `工具/建規格目錄.py`
docs/計畫/20-整體組裝與跨系統驗收.md:113:- Create: `規格/組合/保證/規格目錄封閉.claim.json`
docs/計畫/20-整體組裝與跨系統驗收.md:171:### Task 2: 組裝 production process roots 並禁止 fake 注入
docs/計畫/20-整體組裝與跨系統驗收.md:174:- Create: `nova/啟動/設定.py`
docs/計畫/20-整體組裝與跨系統驗收.md:175:- Create: `nova/啟動/工作排程.py`
docs/計畫/20-整體組裝與跨系統驗收.md:176:- Create: `nova/啟動/evaluator.py`
docs/計畫/20-整體組裝與跨系統驗收.md:177:- Create: `nova/啟動/事件發布.py`
docs/計畫/20-整體組裝與跨系統驗收.md:178:- Create: `nova/啟動/效果轉送.py`
docs/計畫/20-整體組裝與跨系統驗收.md:179:- Create: `nova/啟動/備份.py`
docs/計畫/20-整體組裝與跨系統驗收.md:180:- Create: `nova/啟動/完整系統.py`
docs/計畫/20-整體組裝與跨系統驗收.md:182:- Create: `驗收/整體/測_規格目錄與啟動.py`
docs/計畫/20-整體組裝與跨系統驗收.md:183:- Create: `規格/組合/保證/production不得注入fake.claim.json`
docs/計畫/20-整體組裝與跨系統驗收.md:240:### Task 3: 將Application與CLI接到同一production root
docs/計畫/20-整體組裝與跨系統驗收.md:243:- Create: `規格/組合/保證/公開入口同一組裝.claim.json`
docs/計畫/20-整體組裝與跨系統驗收.md:297:### Task 4: 對五種 ExecutorBackend 跑同一契約矩陣
docs/計畫/20-整體組裝與跨系統驗收.md:300:- Create: `nova/啟動/後端登錄.py`
docs/計畫/20-整體組裝與跨系統驗收.md:301:- Create: `驗收/整體/fixtures/後端事件/replayer.jsonl`
docs/計畫/20-整體組裝與跨系統驗收.md:302:- Create: `驗收/整體/fixtures/後端事件/claude.jsonl`
docs/計畫/20-整體組裝與跨系統驗收.md:303:- Create: `驗收/整體/fixtures/後端事件/codex.jsonl`
docs/計畫/20-整體組裝與跨系統驗收.md:304:- Create: `驗收/整體/fixtures/後端事件/generic-cli.jsonl`
docs/計畫/20-整體組裝與跨系統驗收.md:305:- Create: `驗收/整體/fixtures/後端事件/local-model.jsonl`
docs/計畫/20-整體組裝與跨系統驗收.md:306:- Create: `驗收/整體/測_後端契約矩陣.py`
docs/計畫/20-整體組裝與跨系統驗收.md:307:- Create: `規格/組合/保證/後端共用契約矩陣.claim.json`
docs/計畫/20-整體組裝與跨系統驗收.md:360:### Task 5: 跑一個四策略 Work 的三層可信收斂
docs/計畫/20-整體組裝與跨系統驗收.md:363:- Create: `規格/組合/全系統.flow.json`
docs/計畫/20-整體組裝與跨系統驗收.md:364:- Create: `驗收/整體/fixtures/四策略工作.json`
docs/計畫/20-整體組裝與跨系統驗收.md:365:- Create: `驗收/整體/測_三層流程.py`
docs/計畫/20-整體組裝與跨系統驗收.md:366:- Create: `規格/組合/保證/三層可信收斂.claim.json`
docs/計畫/20-整體組裝與跨系統驗收.md:418:### Task 6: 對全部程序做 total SIGKILL 與持久重建矩陣
docs/計畫/20-整體組裝與跨系統驗收.md:421:- Create: `驗收/整體/測_全程序崩潰.py`
docs/計畫/20-整體組裝與跨系統驗收.md:422:- Create: `工具/跑強制終止矩陣.py`
docs/計畫/20-整體組裝與跨系統驗收.md:423:- Create: `規格/組合/保證/全程序崩潰重建.claim.json`
docs/計畫/20-整體組裝與跨系統驗收.md:481:### Task 7: 驗外部效果 crash gaps 與 backend update 誠實能力
docs/計畫/20-整體組裝與跨系統驗收.md:484:- Create: `驗收/整體/fixtures/外部效果.json`
docs/計畫/20-整體組裝與跨系統驗收.md:485:- Create: `驗收/整體/測_效果與更新.py`
docs/計畫/20-整體組裝與跨系統驗收.md:486:- Create: `規格/組合/保證/跨效果崩潰誠實.claim.json`
docs/計畫/20-整體組裝與跨系統驗收.md:537:### Task 8: 驗判準、知識、約束、資源跨面不靜默降級
docs/計畫/20-整體組裝與跨系統驗收.md:540:- Create: `驗收/整體/測_跨面邊界.py`
docs/計畫/20-整體組裝與跨系統驗收.md:541:- Create: `規格/組合/保證/跨面不靜默降級.claim.json`
docs/計畫/20-整體組裝與跨系統驗收.md:591:### Task 9: 實測 admission caps、soak、burst與事件發布 SLO
docs/計畫/20-整體組裝與跨系統驗收.md:594:- Create: `驗收/整體/測_workload封套.py`
docs/計畫/20-整體組裝與跨系統驗收.md:595:- Create: `工具/跑workload封套.py`
docs/計畫/20-整體組裝與跨系統驗收.md:596:- Create: `規格/組合/保證/workload封套.claim.json`
docs/計畫/20-整體組裝與跨系統驗收.md:656:### Task 10: 驗 checkpoint／segment／tail／backup 的跨層連續
docs/計畫/20-整體組裝與跨系統驗收.md:659:- Create: `驗收/整體/測_分層儲存與備份.py`
docs/計畫/20-整體組裝與跨系統驗收.md:660:- Create: `規格/組合/保證/分層備份連續.claim.json`
docs/計畫/20-整體組裝與跨系統驗收.md:714:### Task 11: 驗 browser 只靠 GraphBundle＋跨層事件流重建
docs/計畫/20-整體組裝與跨系統驗收.md:717:- Create: `驗收/整體/測_UI端到端.py`
docs/計畫/20-整體組裝與跨系統驗收.md:718:- Create: `規格/組合/保證/UI純事件整合.claim.json`
docs/計畫/20-整體組裝與跨系統驗收.md:770:### Task 12: 建立不會恆綠的 release gate 與交付證據
docs/計畫/20-整體組裝與跨系統驗收.md:773:- Create: `驗收/整體/fixtures/固定負控目錄.json`
docs/計畫/20-整體組裝與跨系統驗收.md:774:- Create: `驗收/整體/測_release負控.py`
docs/計畫/20-整體組裝與跨系統驗收.md:775:- Create: `工具/驗全系統.py`
docs/計畫/20-整體組裝與跨系統驗收.md:776:- Create: `規格/組合/保證/release負控完整.claim.json`
docs/計畫/20-整體組裝與跨系統驗收.md:846:### Task 13: 組合 core deployability 與 exact-backend live readiness
docs/計畫/20-整體組裝與跨系統驗收.md:849:- Create: `規格/組合/BackendReadiness.schema.json`
docs/計畫/20-整體組裝與跨系統驗收.md:850:- Create: `nova/啟動/部署資格.py`
docs/計畫/20-整體組裝與跨系統驗收.md:851:- Create: `驗收/整體/測_後端部署資格.py`
docs/計畫/20-整體組裝與跨系統驗收.md:852:- Create: `規格/組合/保證/啟用後端必有live證據.claim.json`
docs/計畫/20-整體組裝與跨系統驗收.md:881:## Exit Gate
docs/計畫/20-整體組裝與跨系統驗收.md:885:## Execution Handoff

exec
/bin/zsh -lc "sed -n '225,285p' docs/計畫/00-總覽.md && sed -n '20,100p' docs/計畫/06-判準評估與隔離回饋.md && sed -n '20,90p' docs/計畫/05-執行封套與後端契約.md 2>/dev/null || true && rg -n \"十三層|目錄規則|nova/權威\" docs/計畫/01-* docs/計畫/03-* | head -n 120" in /Users/sbu/nova
 succeeded in 0ms:
| 真實任務的後端分配比例 | 【推論】依 repo task-class evidence、額度與pinned policy，不寫死品牌順位。 | 第一次 execution reserve 前；未定則不派付費執行。 |
| 本地 runtime／artifact格式 | 【推論】維持plan 05 contract，不改上層。 | plan 17 Task 1；未定則local backend `NOT_ADMITTED`。 |
| 外部 endpoint delivery semantic | 【推論】每個endpoint明示at-least-once或at-most-once與冪等能力。 | 該endpoint admission前；未定不得relay。 |
| live credentials／network | 【推論】不是core前置。 | `BACKEND_READY[fingerprint]` 前；缺少則該backend `NOT_ADMITTED`，core仍可deploy。 |
| SQLite profile升級／換引擎 | 【推論】先用已定single-owner profile。 | soak/capacity ClaimSpec首次碰淘汰門檻時開migration Work；門檻前不得預先分叉雙寫。 |
| vector／hybrid retrieval | 【推論】v1禁止；full eligible context是baseline。 | plan 10 的rolling 30日且≥1,000 dispatch trigger後，經 `RetrievalSelectionWork` 的500-query五項gate；未過繼續full context。 |
| 自動simplification threshold | 【推論】v1固定 `MANUAL_STAGE_BOUNDARY`。 | 要自動化前的新policy revision；未定就永不自動觸發。 |
| experimental MCP Tasks版本 | 【推論】只屬MCP adapter negotiation，core用OperationRef/Receipt。 | plan 13 Task 9；未定就走普通poll/subscribe，不影響core。 |
| UI視覺樣式 | 【推論】不得改event、GraphBundle或reducer語義。 | plan 18對應view task；未定只影響呈現，不阻擋domain core。 |

【推論】必須在第一行 production code 前裁定的項目剩餘 **0**。上表不是未決設計；每列已有明確 default、deadline與逾時 typed outcome。

### 6.6 Day-one工程規範與資料夾落點已裁定

【推論】不新增`01A`。它若依賴01就太晚，若不依賴01則會與建立`pyproject.toml`的唯一owner衝突；把工程toolchain另做一個「子系統」只是假裝分離。plan 01 Task 1只擁有Python/pytest/mutation bootstrap，Tasks 2–4各自建立Ruff/mypy、placement/size與命名gate；ClaimSpec語言的domain work從Task 5才開始。

| 頂層 | 唯一職責 | 看似兩邊都通時的裁決 |
|---|---|---|
| `nova/` | 【推論】可被production import的Python runtime。 | runtime邏輯不能放`工具/`或`架構/`。 |
| `規格/` | 【推論】machine-consumed、content-addressed declarative contract/policy/claim。 | 若會執行I/O或判斷流程，它不是規格，移到owner runtime。 |
| `驗收/` | 【推論】只經public boundary的black-box tests與fixed fixtures。 | 近身白箱test跟著owner package；跨邊界保證才進驗收。 |
| `前端/` | 【推論】browser TypeScript、Web Components與static assets。 | server/application code不因服務UI而搬進前端。 |
| `工具/` | 【推論】operator/developer薄入口，只組參數並呼叫public application/architecture gate。 | 有domain decision就移回`nova/`；有repo policing就移`架構/`。 |
| `架構/` | 【推論】repo自身的static policy、AST/path/import checker與其tests。 | production不得import；runtime policy不放這裡。 |

| `nova/`層 | Placement predicate |
|---|---|
| `介面/` | 【推論】只做CLI/HTTP/MCP/Python等transport encoding與result mapping。 |
| `應用/` | 【推論】只做use-case choreography、transaction boundary與owner port調度，不產生domain truth。 |
| `領域/` | 【推論】擁有單一Work/Pursuit/Execution垂直生命週期的不變式與transition request。 |
| `權威/` | 【推論】擁有跨生命週期政策的一支准入／裁定／核銷／效果／知識寫權。 |
| `狀態機/` | 【推論】domain-neutral MachineSpec compiler/runtime/GraphIR，不知道nova aggregate。 |
| `介接/` | 【推論】外部executor/provider/runtime adapter與其normalization。 |
| `設施/` | 【推論】DB/filesystem/network/process/CAS等port implementation，不做owner decision。 |
| `核心/` | 【推論】無I/O、無生命週期權的leaf value、digest、clock types與codec。 |
| `啟動/` | 【推論】唯一concrete dependency composition root。 |

【推論】placement decision依序問「是否transport→use case→垂直生命週期→橫向政策權威→generic machine→external adapter→infrastructure→leaf value→composition」。一檔命中兩項表示它有兩個變更原因，必須拆；不得用例外清單掩蓋。`架構/檢查工程規範.py`以path manifest、plan `Create:` catalog與AST import graph機械執法。

【實測】靜態import checker曾被`importlib.import_module`完整繞過，因此新checker不能只走`ast.Import/ImportFrom`。literal `importlib.import_module`與`__import__`解析成普通dependency edge；`getattr`反射取得import API、拼接字串、變數或其他nonliteral module target一律禁止。抓不到的dynamic import不是「沒有邊」，而是`DYNAMIC_IMPORT_UNVERIFIABLE`。

### 6.7 本地9B可立即當開發執行者，但不是提前實作plan 17

【實測】本機cache存在`ornith-ai/Ornith-1.5-9B-MLX`原版、4bit與8bit三份，三者由oMLX在`127.0.0.1:8000`提供且`max_model_len=262144`。這只證明服務與artifact在線，不證明任何一份能守nova契約；port 8000是operational endpoint，不寫進產品backend contract。

【實測】本地推論不得套雲端token價格；缺本地憑證時若client fallback到雲端，會在沒有明確錯誤下消耗供應商額度；`~/Library/LaunchAgents`的launchd agent只在使用者登入session載入。day-one worker probe因此必須記endpoint=`127.0.0.1:8000`、拒絕任何非loopback resolved peer、將money cost固定為local compute evidence而非provider RateCard，並把「未登入所以服務未載入」分類為`LOCAL_RUNTIME_UNAVAILABLE`，不得fallback雲端。

【推論】本地模型作為「開發worker」不依賴plan 04–13；它是外部執行者，最低前置只有可呼叫的MLX runtime、read-only task packet、獨立worktree、wall/output limit、以及人工/ClaimSpec gate不把其自報完成當接受。plan 17的前置仍不變，因為那份計畫是在把本地模型變成nova內部正式backend，必須接CAS、Execution、Resource、Effect、Constraint與Application contracts。

【推論】day-one worker admission預設只測8bit；4bit與原版不進主派工。理由是既有repo實測顯示4bit長上下文的跨檔契約task在58分鐘零產出，而量化／rotating cache會改品質；MLX-LM官方也明示縮小rotating KV cache會降低品質。8bit仍只准四類工作：fixture生成、closed enum列舉、執行既有命令/read-only分類、單檔機械修改。

【推論】這個58分鐘結果不塞進plan 17的產品ClaimSpec；它測的是worker task fitness，不是LocalInferenceEngine contract。它進Execution Handoff的`CapabilityEvidence`：每個model artifact digest×quantization×context bucket×task class記`completed/correct/wall time/output bytes`。升級權限需要各task class至少20個事前固定cases、success≥0.90、p95 wall≤10分鐘、zero empty-output；任何一項不符維持`NOT_QUALIFIED_FOR_TASK_CLASS`。每次模型/runtime/template digest變更全數失效重測。

---

## 7. 前置未完成時會怎麼壞

| 缺少前置 | 後一份計畫會出現的假成功 |
|---|---|
| 01 ClaimSpec | 【推論】pytest 綠只能證明手寫 assertion 綠；fixed counterexample、typed harness error與 criterion ownership 都不存在。 |
| 02 MachineSpec | 【推論】state name 會散在 Python／UI，非法 edge 無法被 compiler 與 DB 雙重拒絕。 |

## 子系統規格

【推論】`CriterionDefinition` 指向 guidance cases 與 sealed cases 的 immutable refs；`EvaluationRun` 狀態為 `REQUESTED -> ISOLATION_CHECKED -> RUNNING -> REDUCED -> VERDICT_RECORDED`，另有 typed terminals `UNSUPPORTED_ISOLATION`、`HARNESS_FAULT`、`CANCELLED`。

【推論】`Verdict` 是 evaluation authority 的產物，包含每條 claim 的 typed result與 evidence refs；它不包含 ClaimSpec source bytes。`FeedbackPacket` 是衍生物，不是 verdict 本體。

【推論】v1 capability vocabulary 固定為 `SEPARATE_PROCESS`、`OMIT_SEALED_PATHS`、`ENV_ALLOWLIST`、`NO_INHERITED_FDS`、`NETWORK_POLICY_DECLARED`；其中前四項可以在目前部署提供，`NETWORK_DENY_ENFORCED`、`PROC_HIDE`、`UID_SEPARATION`、`MICROVM` 只可被宣告為 unsupported。

## File Structure

```text
規格/判準/
├── 評估.machine.json                         — evaluation lifecycle 與 typed terminals。
├── CriterionDefinition.schema.json           — guidance/sealed refs 與 admission metadata。
├── FeedbackPolicy.schema.json                 — clause-level reducer policy。
├── IsolationCapability.schema.json            — requirement/offer capability vocabulary。
└── 保證/
    ├── sealed內容不進候選.claim.json          — projection/env/argv 都不含 sealed refs。
    ├── 隔離不得靜默降級.claim.json            — unsupported capability typed terminal。
    ├── 回饋經reducer.claim.json               — assertion repr 不逐字外洩。
    └── 揭露即燒掉.claim.json                  — revealed case cannot be reused。
nova/權威/判準/
├── 定義.py                                   — immutable definition admission/read API。
├── 評估.py                                   — EvaluationAggregate 與 verdict creation。
├── 隔離協商.py                               — required subset offered 純判定。
├── 回饋閘.py                                 — raw result -> FeedbackPacket reducer。
├── 案例治理.py                               — ACTIVE/BURNED/REVOKED lifecycle。
└── test_判準權威.py                          — domain and admission tests。
nova/基礎設施/裁定執行/
├── 投影.py                                   — candidate/evaluator filesystem manifests。
├── 隔離執行.py                               — process/env/fd setup and offer evidence。
├── evaluator_entry.py                        — fresh-process TestPlan entry point。
└── test_隔離執行.py                          — argv/env/path leak tests。
nova/應用/
├── 執行判準.py                               — definition -> isolation -> evaluator -> verdict。
└── test_執行判準.py                          — orchestration and fault taxonomy。
驗收/判準/
├── fixtures/                                 — public guidance 與 private sealed fixture builders。
├── 測_雙測試池.py                            — candidate projection cannot enumerate sealed pool。
├── 測_隔離協商.py                            — requirement subset/no downgrade。
├── 測_回饋縮減.py                            — expected repr canary absent from packet。
└── 測_揭露燒毀.py                            — reveal then reuse direct rejection。
```

## Dependency Gate

前置計畫：01 02 03 04 05

【推論】必須先完成 plan 01–05。沒有 ClaimSpec control semantics，sealed negative 可能是假紅；沒有 MachineSpec/state owner，case burn 與 verdict 會在 crash 後分叉；沒有 CAS，原始 evidence 會被塞入 feedback；沒有 execution envelope，evaluator 自身沒有外部上限。缺任何一項都不能宣稱判準權在執行者之外。

---

### Task 1: 宣告 CriterionDefinition 與 Evaluation lifecycle

**Files:**
- Create: `規格/判準/評估.machine.json`
- Create: `規格/判準/CriterionDefinition.schema.json`
- Create: `nova/權威/判準/定義.py`
- Create: `nova/權威/判準/評估.py`
- Create: `nova/權威/判準/test_判準權威.py`

**Interfaces:**
- Produces: `CriterionDefinitionRef`、`CaseRef(pool, digest, lifecycle)`。
- Produces: `decide_evaluation(state, command) -> DomainEvent[]`。

**ClaimSpec:** 【推論】`criterion.lifecycle.definition-verdict-separated` 從紅轉綠。

**固定負控:** 【推論】在 mutable `EvaluationRun` object 內直接改 ClaimSpec expected value；model/schema 必須沒有該欄位並拒絕 unknown mutation。

- [ ] **Step 1: 寫 definition immutable／verdict separate 的 red tests**

```python
def test_評估執行不持有可寫判準內容() -> None:
    run = EvaluationRun.requested(definition_ref=fixed_definition_ref())
    assert not hasattr(run, "expected")
    with pytest.raises(FrozenInstanceError):
        run.definition_ref = other_ref()
```

- [ ] **Step 2: 跑測試確認 types/schema 缺失**
docs/計畫/01-可執行保證語言.md:23:- 【推論】import固定absolute-only、stdlib/third-party/first-party分組、module top-level、禁止wildcard與跨層捷徑；Ruff執行格式/順序，`架構/目錄規則.toml`與AST checker執行nova九層依賴。
docs/計畫/01-可執行保證語言.md:56:nova/權威/判準/
docs/計畫/01-可執行保證語言.md:74:架構/目錄規則.toml                            — 六頂層、nova十三層、suffix與import方向的唯一宣告。
docs/計畫/01-可執行保證語言.md:84:nova/權威/判準/原語目錄准入.py                 — catalog_ref → 原語目錄，或 typed 失敗。
docs/計畫/01-可執行保證語言.md:85:nova/權威/判準/test_原語目錄准入.py            — 自備目錄、同 id 不同 digest、缺負控。
docs/計畫/01-可執行保證語言.md:233:- Create: `架構/目錄規則.toml`
docs/計畫/01-可執行保證語言.md:257:- [ ] **Step 2: 跑紅測確認目錄規則與checker不存在**
docs/計畫/01-可執行保證語言.md:276:git add 架構/目錄規則.toml 架構/檢查工程規範.py 架構/test_工程規範.py 驗收/工具鏈/fixtures/錯置_repository.py 驗收/工具鏈/fixtures/超長函式.py 規格/工程/保證/檔案落點唯一.claim.json
docs/計畫/01-可執行保證語言.md:417:- Create: `nova/權威/判準/保證規格模型.py`
docs/計畫/01-可執行保證語言.md:495:git add 規格/語言 規格/介面/效果契約.schema.json 規格/工程/保證 nova/權威/判準/保證規格模型.py 驗收/保證規格語言/測_meta_schema.py
docs/計畫/01-可執行保證語言.md:504:- Create: `nova/權威/判準/保證規格編譯.py`
docs/計畫/01-可執行保證語言.md:507:- Create: `nova/權威/判準/test_保證規格語言.py`
docs/計畫/01-可執行保證語言.md:508:- Modify: `nova/權威/判準/保證規格模型.py`
docs/計畫/01-可執行保證語言.md:533:Run: `uv run pytest -q nova/權威/判準/test_保證規格語言.py`
docs/計畫/01-可執行保證語言.md:552:Run: `uv run pytest -q nova/權威/判準/test_保證規格語言.py`
docs/計畫/01-可執行保證語言.md:558:Run: `uv run pytest -q nova/權威/判準/test_保證規格語言.py::test_相同輸入編譯成相同_plan_digest -n 2`
docs/計畫/01-可執行保證語言.md:565:git add nova/權威/判準/保證規格編譯.py nova/基礎設施/裁定執行/原語.py nova/權威/判準/test_保證規格語言.py
docs/計畫/01-可執行保證語言.md:574:- Create: `nova/權威/判準/保證規格執行.py`
docs/計畫/01-可執行保證語言.md:578:- Modify: `nova/權威/判準/保證規格編譯.py`
docs/計畫/01-可執行保證語言.md:633:git add nova/權威/判準/保證規格執行.py nova/基礎設施/裁定執行/參考執行封套.py 驗收/保證規格語言/測_敏感度.py
docs/計畫/01-可執行保證語言.md:761:Run: `uv run pytest -q -n 2 驗收/工具鏈 驗收/保證規格語言 nova/核心 nova/權威/判準 nova/基礎設施/裁定執行`
docs/計畫/01-可執行保證語言.md:779:- Modify: `nova/權威/判準/保證規格模型.py`
docs/計畫/01-可執行保證語言.md:825:source_paths = ["nova/核心", "nova/權威/判準", "nova/基礎設施/裁定執行"]
docs/計畫/01-可執行保證語言.md:826:tests_dir = ["驗收/保證規格語言", "驗收/工具鏈", "nova/核心", "nova/權威/判準", "nova/基礎設施/裁定執行"]
docs/計畫/01-可執行保證語言.md:840:git add 規格/判準/保證/指定突變而非擊殺率.claim.json 驗收/保證規格語言/測_指定突變.py nova/權威/判準/保證規格模型.py 工具/驗工具鏈.py pyproject.toml
docs/計畫/01-可執行保證語言.md:890:- Modify: `架構/目錄規則.toml`
docs/計畫/01-可執行保證語言.md:897:- Forbids: 三處各自維護一份閘清單。清單是 `架構/目錄規則.toml` 的 `[gates]` 資料，三處都讀它。
docs/計畫/01-可執行保證語言.md:939:git add 工具/驗全部.py 工具/裝_git_鉤子.py .github 規格/工程/保證/閘必須自動執行.claim.json 架構/目錄規則.toml 架構/test_工程規範.py
docs/計畫/01-可執行保證語言.md:1010:- Create: `nova/權威/判準/原語目錄准入.py`
docs/計畫/01-可執行保證語言.md:1011:- Create: `nova/權威/判準/test_原語目錄准入.py`
docs/計畫/01-可執行保證語言.md:1013:- Modify: `nova/權威/判準/保證規格編譯.py`
docs/計畫/01-可執行保證語言.md:1025:`nova/權威/判準/test_保證規格語言.py::test_plan_digest_涵蓋四個輸入` 逐字證明換一份自備目錄
docs/計畫/01-可執行保證語言.md:1078:Run: `uv run pytest -q 驗收/保證規格語言/測_目錄准入.py nova/權威/判準/test_原語目錄准入.py`
docs/計畫/01-可執行保證語言.md:1085:git add 規格/語言/PrimitiveCatalog.schema.json 規格/語言/原語目錄.admitted.json 規格/語言/保證/原語目錄須經准入.claim.json nova/權威/判準/原語目錄准入.py nova/權威/判準/test_原語目錄准入.py 驗收/保證規格語言/測_目錄准入.py nova/權威/判準/保證規格編譯.py 工具/跑驗收.py
docs/計畫/01-可執行保證語言.md:1099:- Modify: `架構/目錄規則.toml`
docs/計畫/01-可執行保證語言.md:1183:git add 規格/驗收/ClaimAdmissionManifest.schema.json 規格/驗收/已准入保證.manifest.json 規格/工程/保證/已准入保證不可原地改弱.claim.json 架構/檢查已准入保證.py 架構/test_已准入保證.py 架構/目錄規則.toml .github/workflows/gates.yml
docs/計畫/01-可執行保證語言.md:1194:uv run ruff format --check . && uv run ruff check . && uv run mypy nova 架構 工具 && uv run python 架構/檢查工程規範.py && uv run python 架構/檢查已准入保證.py && uv run pytest -q -n 2 架構/test_工程規範.py 架構/test_已准入保證.py 驗收/工具鏈 驗收/保證規格語言 nova/核心 nova/權威/判準 nova/基礎設施/裁定執行

web search: 
web search: site:arxiv.org LLM evaluators favor own generations self preference bias arxiv ...
web search: 
web search: site:fda.gov non-inferiority clinical trials guidance prespecified margin confidence interval PDF ...
web search: 
web search: W3C SCXML recommendation state machine executable content specification ...
codex
先校正三件事：

1. nova 必須保持領域中立。視覺、隨機評估、知識等都只能是通用 observation/evaluator capability；任何特定產品、renderer 或 profile 都不得進核心規格。
2. 「技術是否值得用」不是 plan 07 的資源核銷問題。plan 07 只回答「能不能花、花了多少、還剩多少」；新能力回答「相對 baseline，某項技術是否在品質不劣的條件下改善資源效率」。
3. 你稱它為「非劣性檢定」只對一半：

   - 品質：非劣性檢定，證明 `quality_technique - quality_baseline > -Δq`。
   - token：優越性／上界檢定，證明 `token_technique / token_baseline < Rmax`。
   - 整體：雙端點的 intersection-union decision，兩條都過才接受。不是把兩個平均數揉成一個效益分數。

FDA 對非劣性設計的核心要求正是事前選定 margin，並用單側信賴界判斷；事後看到結果才選 margin 會失去可解釋性。[FDA《Non-Inferiority Clinical Trials》](https://www.fda.gov/regulatory-information/search-fda-guidance-documents/non-inferiority-clinical-trials)

---

# 校正一：中立化後的視覺機制

我上一輪提到具體 renderer／產品 profile 的地方全部撤回，改成以下通用形狀。

| 格 | 中立版本 |
|---|---|
| 地基 | 可重複的 observation capture、版本化 baseline、受控執行環境，以及 comparator；Playwright 只是此模式的一個官方實例，不是 nova 的領域假設。[Playwright Visual Comparisons](https://playwright.dev/docs/test-snapshots) |
| 拆解 | `ObservationProducer` 只產生 observation；`Comparator` 比較 observation；Criterion Authority 把比較結果 fold 成 clause verdict。三者分權。 |
| 組合 | `ObservationProtocolRef`、`ObservationArtifactRef`、`EnvironmentFingerprint`、`ComparatorRef`、`ThresholdPolicyRef`；不出現任何領域名詞。 |
| 擴充點 | 新 observation media type、新 capture adapter、新 comparator primitive，以 namespaced capability 加入。 |
| 加蓋 | protocol 未釘版、環境不符、threshold 在看到候選後變更、baseline 已揭露、adapter capability 不足時拒絕評估。 |

同理，不應存在「某類 product profile 把 visual capability 標成 REQUIRED」。正確介面是：

```text
CriterionDefinition.required_observation_capabilities[]
```

某個 criterion revision 可要求某項 capability；nova 核心不知道它服務哪個產品。能力缺失時回 `UNSUPPORTED_OBSERVATION_CAPABILITY`。

---

# A. 落點：新開 `06B-技術效益評測`

## 裁決

新開一份計畫，不掛在 07，也不塞進 06 或 09。

原因：

- 06 擁有「單一候選是否符合既定 criterion」。
- 07 擁有「資源保留、核銷、供應商額度與派工資格」。
- 09 擁有「已得到合法 score evidence 後如何選 winner」。
- 新能力擁有的是「對 baseline 與 treatment 做成對實驗，產出有不確定度的比較證據」。

它有自己的生命週期：

```text
DRAFT
→ DESIGN_FROZEN
→ RUNNING
→ EVIDENCE_SEALED
→ ANALYZED
→ ACCEPTED | REJECTED | INCONCLUSIVE | INVALIDATED
```

這不是 07 的一種帳，也不是 06 的一次普通 EvaluationRun。

建議檔名：

`docs/計畫/06B-技術效益評測.md`

前置計畫只依：

```text
前置計畫：01 02 03 04 05 06
```

不依 07。它消費 plan 05 已正規化的 `UsageEvidence`；若 plan 05 尚未能提供 tree-inclusive token evidence，則該 run 是 `USAGE_SCOPE_INCOMPLETE`，不是偷偷依賴 plan 07 的金額帳。

## 建議 Create 清單

```text
規格/評測/
├── TechniqueExperimentSpec.schema.json
├── TechniqueExperimentResult.schema.json
├── 技術效益評測.machine.json
└── 保證/
    ├── 技術效益雙端點事前凍結.claim.json
    └── 隨機實驗證據重播一致.claim.json

nova/權威/評測/
├── 模型.py
├── 准入.py
├── 分析.py
└── test_技術效益評測.py

nova/應用/
├── 執行技術效益評測.py
└── test_執行技術效益評測.py

驗收/評測/
├── fixtures/無效技術成對樣本.json
├── fixtures/省資源但品質退化.json
└── 測_技術效益雙端點.py
```

這超過單一 task 的十檔上限，所以計畫內至少拆成三個 task：

1. schema、machine 與 experiment admission；
2. deterministic analyzer 與統計固定負控；
3. application orchestration 與黑箱 ClaimSpec。

`架構/目錄規則.toml` 需由第一個 task `Modify`，讓 `nova/權威/評測/` 成為跨 Execution 的「比較證據准入與裁定」權威，不應塞進資源權威。

## ClaimSpec

主 claim：

```text
evaluation.technique.token-upper-quality-lower.predeclared
```

第二條只管重播：

```text
evaluation.technique.recorded-evidence-replay-deterministic
```

## 固定負控

主固定負控使用「無效技術」：

- baseline 與 treatment 的生成 bytes 不必相同；
- 每個 case 的 treatment token usage 與 baseline 來自同一分布，沒有事前要求的節省；
- 品質可以完全相同。

它必須紅在：

```text
token_ratio_upper_bound <= max_token_ratio
```

例如事前要求至少省 30%，則 `max_token_ratio=0.70`；無效技術的單側上界接近或高於 `1.0`，必須拒絕。

另一固定負控是「省 token 但品質退化」：

- token endpoint 通過；
- 品質差超過 `noninferiority_margin`。

它必須只紅在：

```text
quality_difference_lower_bound >= -quality_noninferiority_margin
```

這兩個負控分別證明兩條 predicate 都有牙，且不能用其中一條補償另一條。

---

# B. ClaimSpec／ExperimentSpec 的具體形狀

## 1. 不應直接擴充目前三個純量 judge

`EQUALS`／`NOT_EQUALS`／`LESS_THAN` 是 deterministic scalar primitive。統計推斷不是多加兩個 operator 就能完成，因為它需要：

- 配對資料；
- sampling unit；
- dependence structure；
- estimator；
- confidence procedure；
- missing-data policy；
- multiplicity policy；
- frozen analysis program。

正確形狀不是：

```json
{"operator": "NON_INFERIOR", "value": 0.95}
```

那會把整套實驗設計藏在 operator implementation 裡。

應加入一個經 PrimitiveCatalog 准入的高階 primitive，例如：

```text
PAIRED_DUAL_ENDPOINT_CI_DECISION_V1
```

ClaimSpec 只引用已凍結的 `TechniqueExperimentSpecRef` 與已 sealed 的 result bundle。

## 2. 必須事前釘住的欄位

```json
{
  "experiment_id": "exp.technique.example.v1",
  "revision": 1,

  "baseline_artifact_ref": {
    "semantic_id": "technique.baseline",
    "revision": 4,
    "digest": "sha256:..."
  },
  "treatment_artifact_ref": {
    "semantic_id": "technique.candidate",
    "revision": 1,
    "digest": "sha256:..."
  },

  "population": {
    "benchmark_set_ref": "cas:...",
    "benchmark_set_digest": "sha256:...",
    "sampling_unit": "CASE",
    "inclusion_policy_ref": "cas:...",
    "exclusion_policy": "NONE_AFTER_FREEZE"
  },

  "pairing": {
    "mode": "SAME_CASE_SAME_REPLICATE_BLOCK",
    "order_randomization": "BALANCED_WITHIN_CASE",
    "assignment_seed": 483921,
    "missing_pair": "REJECT_RUN"
  },

  "replication": {
    "replicates_per_case": 8,
    "model_sampling_seeds_ref": "cas:...",
    "warmup_runs": 1,
    "warmup_included": false
  },

  "fingerprints": {
    "executor_backend_required": true,
    "model_artifact_required": true,
    "prompt_family_required": true,
    "tool_policy_required": true,
    "context_manifest_required": true,
    "runtime_environment_required": true
  },

  "token_endpoint": {
    "measure": "DELEGATION_TREE_TOTAL_TOKENS",
    "effect": "RATIO_TREATMENT_OVER_BASELINE",
    "max_token_ratio": "0.70",
    "confidence_side": "UPPER_ONE_SIDED",
    "confidence_level": "0.975",
    "estimator": "PAIRED_LOG_RATIO_GEOMETRIC_MEAN",
    "max_interval_width": "0.15"
  },

  "quality_endpoint": {
    "metric_ref": "criterion-score.example.v3",
    "direction": "HIGHER_IS_BETTER",
    "effect": "PAIRED_TREATMENT_MINUS_BASELINE",
    "noninferiority_margin": "0.03",
    "confidence_side": "LOWER_ONE_SIDED",
    "confidence_level": "0.975",
    "estimator": "PAIRED_CASE_MEAN",
    "minimum_absolute_quality": "0.80"
  },

  "analysis": {
    "method": "PAIRED_CLUSTER_BOOTSTRAP_BCA_V1",
    "resampling_unit": "CASE",
    "bootstrap_repetitions": 10000,
    "analysis_seed": 928114,
    "analysis_implementation_digest": "sha256:...",
    "missing_data_policy": "INVALIDATE_EXPERIMENT",
    "outlier_policy": "NONE",
    "multiplicity_policy": "INTERSECTION_UNION_BOTH_MUST_PASS"
  },

  "decision": {
    "accept_if": [
      "token_endpoint.upper_bound <= 0.70",
      "token_endpoint.interval_width <= 0.15",
      "quality_endpoint.lower_bound >= -0.03",
      "quality_endpoint.treatment_lower_bound >= 0.80"
    ],
    "otherwise": "REJECT_OR_INCONCLUSIVE"
  }
}
```

這裡有幾個不能混淆的值：

- `max_token_ratio=0.70`：決策門檻，至少省 30%。
- `max_interval_width=0.15`：精度門檻，避免「省 0–90%」。
- 實際報告的 savings interval：由凍結算法產出，例如 `[0.31, 0.43]`；不是人在看到資料後填入。
- `quality_noninferiority_margin`：允許相對 baseline 最多退多少。
- `minimum_absolute_quality`：防止 baseline 本身很爛，導致 treatment 與爛 baseline「非劣」卻仍不可用。

最後一條很重要。只做相對非劣性會出現：

```text
baseline quality = 0.20
treatment quality = 0.20
```

統計上可能非劣，但根本沒有使用價值。因此需同時有相對 margin 與 absolute floor。

## 3. 配對與重複的原則

- 同一 benchmark case 必須同時跑 baseline 和 treatment。
- 執行順序必須 block-randomized，避免 cache、負載與時間漂移永遠偏向其中一方。
- 若 backend 能接受 seed，兩側使用事前配好的 seed；但 seed 只是 experiment input，不宣稱 provider 一定由此產生相同 bytes。
- 統計 sampling unit 預設是 case，不是每次 retry。對同一 case 的多次重跑不能假裝成獨立樣本。
- 若一個 case 的任一側缺失，v1 直接 `INVALIDATED`；不能只刪掉難看的 pair。
- sample size 不能固定寫死為一個普世數字。它必須由事前的最小可決策效果、預估變異、α、power 算出，並寫入 frozen spec。FDA 同樣要求 margin 與設計事前確定，而非看完資料補寫。[FDA 非劣性指引](https://www.fda.gov/media/78504/download)

MLCommons 的基準實務也把 performance 與 accuracy 分開測，並要求 accuracy threshold；這正好支持「速度／資源改善不能補償品質不合格」的雙軸形狀。[MLPerf Inference](https://docs.mlcommons.org/inference/)、[MLPerf Submission Guide](https://docs.mlcommons.org/inference/submission/)

## 4. 不要自己發明統計函式庫

nova 應擁有：

- frozen experiment protocol；
- evidence manifest；
- deterministic analysis invocation；
- pass/fail policy。

nova 不應重寫 bootstrap、信賴區間或非劣性統計演算法。應使用釘版的成熟統計實作，並把 package/version/code digest 納入 analysis fingerprint。否則會從「可驗收工程」滑成自製統計套件。

---

# C. 決定性重播與隨機模型不衝突

你的方向對，但界線還要再切成四層。

| 層 | 必須相同嗎？ |
|---|---|
| `ExperimentSpec → RunPlan` | 必須。相同 spec bytes、catalog revision 與 compiler revision，必須得到相同配對、順序、seed schedule 與 `run_plan_digest`。 |
| live invocation → model response | 不要求。即使 request bytes 與 seed 相同，遠端模型、服務端 batching、模型 revision 或 runtime 仍可能產生不同 response。 |
| 一次已完成 live run → EvidenceBundle | 必須 immutable。實際 request bytes、response bytes、usage evidence、fingerprints、timestamps 與 failure outcome 全部內容定址。 |
| 同一 EvidenceBundle → statistical result | 必須。相同 evidence bytes、analysis implementation digest 與 analysis seed，必須得到相同 interval、decision 與 result digest。 |

因此：

```text
replay_evidence(bundle_digest)
```

必須逐 byte 可重播；

```text
rerun_model(experiment_spec)
```

則是建立新的 `MeasurementRun`，不是 replay。

新的 live run 即使使用同一 ExperimentSpec，也必須有：

```text
new_run_id
new_evidence_bundle_digest
same_experiment_spec_digest
```

不能覆寫舊 run。

### seed 的精確地位

seed 是 request manifest 的一部分，但不是「輸出可重現保證」。它只證明 nova 送出同一 sampling request。若 provider 不承諾 seeded determinism，capability evidence 必須寫：

```text
SEEDED_REQUEST_SUPPORTED
SEEDED_OUTPUT_DETERMINISM_UNSUPPORTED
```

MLCommons 對可信 benchmark 的要求也包括固定模型版本、prompt、hyperparameters、hardware、random seeds、scoring 與 post-processing，並保存足以重建結果的證據；它沒有把「模型必須每次吐相同 bytes」當成唯一的 reproducibility 定義。[MLCommons：How to Tell When a Benchmark Is Worth Trusting](https://mlcommons.org/2026/08/benchmark-is-worth-trusting/)

---

# D. 十二項重新做「官方＋權威」審計

判讀：

- **夠**：兩層共同支撐方向；nova 仍需選具體介面。
- **缺一塊**：有相鄰官方或研究支持，但證不到原句的強度。
- **多了**：原句比兩層都要求得更強，或直接與既有做法衝突。

## 1. Harness 恰好由那十一個部件構成

- 官方：**沒有**唯一十一部件標準。Anthropic 只明確描述 augmented LLM 的 retrieval、tools、memory，以及 workflow／agent patterns。[Anthropic《Building Effective Agents》](https://www.anthropic.com/engineering/building-effective-agents)
- 權威：HarnessArch 有十一 primitive，但它是實務者 taxonomy，而且列項與我們先前引用的十一項不同；不是同儕審查標準。[HarnessArch](https://www.harnessarch.com/harness)
- 裁決：**多了**。

可保留「部件完整性 checklist」，不可宣稱「業界定義就是這十一個」。

## 2. Loop 恰好需要五個終止條件

- 官方：AWS 支持 timeout、bounded retry、backoff；workflow 系統普遍有 timeout/retry/cancellation，但沒有官方規定恰好五項。[AWS Builders’ Library](https://aws.amazon.com/builders-library/timeouts-retries-and-backoff-with-jitter/)
- 權威：ranking function 以映到 well-founded set 且每步下降來證明 termination；它證成「需有進展量」的形式概念。可驗證出處包括 DOI [10.1109/ICSTW.2013.75](https://doi.org/10.1109/ICSTW.2013.75) 與 DOI [10.1016/j.cl.2015.10.001](https://doi.org/10.1016/j.cl.2015.10.001)。
- 裁決：**缺一塊**。

Ranking function 不等於實務上的 stochastic `NO_PROGRESS` detector；它支撐「進展必須被定義」，不證明「連續三次無改善」是正確窗口。五項作為 nova policy 可用，不能叫普世必要且完備。

## 3. `MachineSpec` 必須是純宣告資料

- 官方：W3C SCXML 是正式 Recommendation，確實以文件宣告 state、transition、parallel/final 與執行語意；也容許 namespaced executable-content extension。[W3C SCXML](https://www.w3.org/TR/scxml/)
- 權威：statecharts 與 executable workflow 文獻支持把控制流顯式模型化，但不要求所有 guard 都不得有程式語意。
- 裁決：**夠，但原句要縮窄**。

可證成的是「控制拓撲與轉移語意必須存在於可解析、可版本化宣告中」；證不成「整個狀態機只能是無任何 executable extension 的資料」。nova 的封閉 guard DSL 是額外拒絕。

## 4. Graph 必須是 DAG

- 官方：部分 workflow 系統以 DAG 為核心；但 LangGraph 官方明確允許 loop、conditional edge、dynamic edge 與 parallel superstep。[LangGraph Graph API](https://langchain-ai.github.io/langgraph/concepts/multi_agent/)
- 權威：科學工作流常用 DAG，但 statechart、Petri net 與一般 workflow graph 都允許循環。
- 裁決：**多了，而且作為一般 graph 地基是錯的**。

nova 可以讓某一種 lifecycle ownership graph 是 acyclic，但不能重新定義 graph engineering 等於 DAG。

## 5. Node 必須可獨立重播

- 官方：W3C PROV 提供 entity/activity/agent provenance，但沒有規定每個 node 必須可獨立重跑。[W3C PROV](https://www.w3.org/TR/prov-overview/)
- 權威：CWLProv 明確指出 provenance 可支援針對單一步驟或 sub-workflow 的 inspection 與 automatic re-enactment，DOI [10.1093/gigascience/giz095](https://doi.org/10.1093/gigascience/giz095)。科學 workflow reproducibility 也要求保存 workflow、輸入與執行環境，DOI [10.1155/2015/243180](https://doi.org/10.1155/2015/243180)。
- 裁決：**缺一塊**。

權威層強力支持「可局部重演是好性質」，但不證明每一個任意 node 都能獨立重播；有些 node 含不可逆外部效果。正確規則是：

> pure/computational node 必須可由 pinned inputs 重演；effectful node 必須重播 receipt/projection，不得重做外部效果。

## 6. Edge 只承載依賴、不承載狀態

- 官方：LangGraph 明確說 state/message 沿 edge/channel 傳遞，conditional edge 依目前 state 路由。
- 權威：dataflow、Petri net、actor/message-passing 都允許邊或 channel 承載 token/message/data。
- 裁決：**多了，原句錯誤**。

應改成「edge 不擁有隱藏的權威狀態」；不應禁止顯式、typed、manifested payload。

## 7. `InvocationEnvelope`／`ContextManifest`／guard compiler 是業界既有介面

- 官方：CloudEvents、MCP envelopes、SCXML 等分別提供事件封套、協定消息、狀態機語意；沒有這三個 nova 名稱與其組合。
- 權威：design by contract、capability systems、reproducible builds 支持顯式輸入與環境 manifest，但沒有這個 exact schema。
- 裁決：**缺一塊**。

原則有地基，具體三件套是 nova 的組合發明。

## 8. `DelegationPolicy` 的具體欄位與 usage-scope 核銷

- 官方：Anthropic 官方多 agent 系統使用獨立 context windows，並實測 multi-agent 約為 chat 的 15 倍 token；Claude Code 也把 subagent 定義為 fresh conversation。[Anthropic Multi-Agent Research](https://www.anthropic.com/engineering/multi-agent-research-system)、[Claude Code agent loop](https://code.claude.com/docs/en/agent-sdk/agent-loop)
- 權威：多代理／分散式系統研究支持 bounded fan-out、資源歸屬與訊息隔離，但沒有跨所有 agent backend 的統一 usage envelope。
- 裁決：**缺一塊**。

需要 delegation policy 與 tree-inclusive accounting 的理由夠；`max_depth/max_children/model_set/per_branch_cap` 的 exact schema 是 nova。

## 9. 子代理摘要只能是 observation

- 官方：Anthropic 說 subagent 壓縮結果供 lead agent 使用，沒有說它具有權威終局，也沒有規定只能是 observation。
- 權威：Clark–Wilson 強調 well-formed transaction 與 separation of duty，原始論文 DOI [10.1109/SP.1987.10001](https://doi.org/10.1109/SP.1987.10001)；NASA IV&V 也要求技術、管理與財務獨立。[NASA-STD-8739.8B](https://standards.nasa.gov/standard/nasa/nasa-std-87398)
- 裁決：**缺一塊，但 nova 的結論合理**。

這些來源證成「生產者不能自我認證」；不直接證成資料型別一定叫 observation。正確說法是：

> subagent 輸出可以是 proposal/evidence/observation；除非另有獨立權威驗證，不得直接成為 authoritative verdict。

## 10. 不同廠商不等於技術獨立

- 官方：NASA IV&V 把獨立性分為 technical、managerial、financial；僅組織或供應商不同不足以證明 technical independence。[NASA-STD-8739.8B](https://standards.nasa.gov/sites/default/files/standards/NASA/B/0/NASA-STD-87398-Revision-B_1.pdf)
- 權威：LLM evaluator 會有 self-preference；Panickssery、Bowman、Feng，arXiv [2404.13076](https://arxiv.org/abs/2404.13076)。但後續研究也指出部分觀測可能受 evaluator quality confound 影響，因此不能把「不同模型家族」當充分條件，也不能把同家族直接判為必然不獨立。
- 裁決：**夠**。

技術獨立必須由訓練資料、模型家族、prompt/evidence path、工具、評估方法與已測偏誤共同證成；vendor label 至多是一項 metadata。

## 11. `PrimitiveCatalog` 與 `ProtectedClaimClosure` 的 exact manifest

- 官方：SLSA 要求 provenance 由 trusted control plane 產生或驗證，使用者控制的 build step 不得任意修改；GitHub protected branches 支援 required checks。
- 權威：Clark–Wilson、supply-chain provenance 與 reference-monitor 思想支持「准入集合不能由被驗者自備」。
- 裁決：**缺一塊**。

「要有可信 catalog／protected closure」理由充分；兩份 manifest 的 exact fields 是 nova 自己設計，沒有現成標準能直接拿來。

## 12. `disclosure_units` 能提供 reusable-holdout 的統計保證

- 官方：沒有。
- 權威：Reusable Holdout 明確處理 adaptive reuse，使用具 differential-privacy 性質的機制；arXiv [1506.02629](https://arxiv.org/abs/1506.02629)。
- 裁決：**多了，如果宣稱統計有效性；夠，如果只宣稱保守的有限 transcript cap**。

`disclosure_units` 可以是安全政策：

```text
超過 N 次就不再回饋
```

但不能宣稱它保持某個顯著水準或 generalization guarantee。要有那種保證，必須實作正式 privacy accountant／reusable holdout protocol。

---

# E. 兩層都查過後，仍屬 nova 自己發明的項目

以下不是「完全沒有先例」，而是找不到業界已定義的同形介面；風險最高的是具體組合，而非背後原則。

1. **ClaimSpec 的「固定反例＋`must_fail_exactly`＋正控」三件綁定語言。**  
   mutation testing、negative testing、design by contract 各自都有地基；我查不到把三者組成這個 admission unit 的標準。

2. **ProtectedClaimClosure 的 exact transitive closure。**  
   protected branch、attestation、provenance 都有；「一份 manifest 封住 claim、predicate、固定負控、primitive catalog、TestPlan 與 checker」是 nova 的組合。

3. **PrimitiveCatalog 作為 ClaimSpec compiler 的唯一准入根。**  
   allowlist、trusted registry、capability admission 都有；這個 exact compiler contract 是 nova。

4. **三種圖嚴格分立：lifecycle ownership graph／Execution delegation tree／artifact provenance DAG。**  
   三種圖分別都有先例；把它們列為不得互相升格的架構不變式，是 nova 的發明。

5. **把任何 executor backend——包括純函式 replayer——放在完全相同的 Execution contract 下。**  
   ports/adapters 有成熟地基；這個具體平級矩陣是 nova 的組合。

6. **以 transcript enum 的資訊暴露量管理 sealed feedback。**  
   若只是 finite cap，是 nova 保守機制；若想取得統計保證，目前不夠。

這些項目不能因為「沒有現成標準」就刪；但必須比有標準的部分多一級負控、實證與退出策略。

---

# F. nova 哪裡多做了或正在造輪子

## 1. 把所有 graph 壓成 DAG

這不是保守，是錯誤抽象。既有 graph/statechart 系統已處理 cycle、conditional transition、parallel state。nova 只需限制特定 graph 的權威與持久化語意，不需重新發明一個「所有圖必須 DAG」世界。

## 2. 宣稱 edge 不能承載狀態

既有 typed channel/message/state transition 已經解決這題。正確控制的是：

- payload schema；
- owner；
- provenance；
- reducer；
- idempotency。

禁止 edge payload 反而會逼人把資料藏進共享 mutable state。

## 3. 自製統計計算核心

這輪新增的效益評測若自己寫 bootstrap、非劣性 CI、power calculation，就是明確造輪子。nova 應只固定 protocol、呼叫已釘版統計實作、驗證輸入輸出與保存證據。

## 4. 把 harness taxonomy 變成 schema

十一部件清單適合 gap analysis，不值得變成 `HarnessComponentKind` 封閉 enum。不同官方系統會用不同邊界，封閉 taxonomy 只會讓 nova 忙著替名詞維持 mapping。

## 5. 為每一種 benchmark 重建 load generator

MLPerf 已證明 load generator、performance run、accuracy run、compliance checker 的分離形狀。nova 應建立通用 experiment port，能包裝既有 benchmark runner，不應要求所有評測改寫成 nova 原生測試。[MLPerf Submission Guide](https://docs.mlcommons.org/inference/submission/)

## 6. 要求 live stochastic model byte-identical

這會把可重播性用錯地方。應重播的是：

- frozen run plan；
- 已錄下的 request/response/evidence；
- deterministic analysis。

不是要求外部隨機系統重新取樣時重現舊 bytes。

---

最終裁決是：

- plan 07 不刪，但從「技術價值判定」退回資源安全與派工平衡。
- 技術是否值得使用，新開 06B，以比較實驗為獨立權威生命週期。
- 品質採非劣性；token 採資源比率上界；兩者 AND，另有 interval-width 與 absolute-quality floor。
- nova 保證 experiment specification、錄得證據與分析可重播；不保證 live stochastic executor 重跑產生相同 bytes。
- 十二項中，真正得到兩層充分支持的是「宣告式控制拓撲」與「供應商不同不構成技術獨立」；多數其餘項目有原則地基，但 nova 的 exact schema 仍是自己的組合責任。
tokens used
130,291
先校正三件事：

1. nova 必須保持領域中立。視覺、隨機評估、知識等都只能是通用 observation/evaluator capability；任何特定產品、renderer 或 profile 都不得進核心規格。
2. 「技術是否值得用」不是 plan 07 的資源核銷問題。plan 07 只回答「能不能花、花了多少、還剩多少」；新能力回答「相對 baseline，某項技術是否在品質不劣的條件下改善資源效率」。
3. 你稱它為「非劣性檢定」只對一半：

   - 品質：非劣性檢定，證明 `quality_technique - quality_baseline > -Δq`。
   - token：優越性／上界檢定，證明 `token_technique / token_baseline < Rmax`。
   - 整體：雙端點的 intersection-union decision，兩條都過才接受。不是把兩個平均數揉成一個效益分數。

FDA 對非劣性設計的核心要求正是事前選定 margin，並用單側信賴界判斷；事後看到結果才選 margin 會失去可解釋性。[FDA《Non-Inferiority Clinical Trials》](https://www.fda.gov/regulatory-information/search-fda-guidance-documents/non-inferiority-clinical-trials)

---

# 校正一：中立化後的視覺機制

我上一輪提到具體 renderer／產品 profile 的地方全部撤回，改成以下通用形狀。

| 格 | 中立版本 |
|---|---|
| 地基 | 可重複的 observation capture、版本化 baseline、受控執行環境，以及 comparator；Playwright 只是此模式的一個官方實例，不是 nova 的領域假設。[Playwright Visual Comparisons](https://playwright.dev/docs/test-snapshots) |
| 拆解 | `ObservationProducer` 只產生 observation；`Comparator` 比較 observation；Criterion Authority 把比較結果 fold 成 clause verdict。三者分權。 |
| 組合 | `ObservationProtocolRef`、`ObservationArtifactRef`、`EnvironmentFingerprint`、`ComparatorRef`、`ThresholdPolicyRef`；不出現任何領域名詞。 |
| 擴充點 | 新 observation media type、新 capture adapter、新 comparator primitive，以 namespaced capability 加入。 |
| 加蓋 | protocol 未釘版、環境不符、threshold 在看到候選後變更、baseline 已揭露、adapter capability 不足時拒絕評估。 |

同理，不應存在「某類 product profile 把 visual capability 標成 REQUIRED」。正確介面是：

```text
CriterionDefinition.required_observation_capabilities[]
```

某個 criterion revision 可要求某項 capability；nova 核心不知道它服務哪個產品。能力缺失時回 `UNSUPPORTED_OBSERVATION_CAPABILITY`。

---

# A. 落點：新開 `06B-技術效益評測`

## 裁決

新開一份計畫，不掛在 07，也不塞進 06 或 09。

原因：

- 06 擁有「單一候選是否符合既定 criterion」。
- 07 擁有「資源保留、核銷、供應商額度與派工資格」。
- 09 擁有「已得到合法 score evidence 後如何選 winner」。
- 新能力擁有的是「對 baseline 與 treatment 做成對實驗，產出有不確定度的比較證據」。

它有自己的生命週期：

```text
DRAFT
→ DESIGN_FROZEN
→ RUNNING
→ EVIDENCE_SEALED
→ ANALYZED
→ ACCEPTED | REJECTED | INCONCLUSIVE | INVALIDATED
```

這不是 07 的一種帳，也不是 06 的一次普通 EvaluationRun。

建議檔名：

`docs/計畫/06B-技術效益評測.md`

前置計畫只依：

```text
前置計畫：01 02 03 04 05 06
```

不依 07。它消費 plan 05 已正規化的 `UsageEvidence`；若 plan 05 尚未能提供 tree-inclusive token evidence，則該 run 是 `USAGE_SCOPE_INCOMPLETE`，不是偷偷依賴 plan 07 的金額帳。

## 建議 Create 清單

```text
規格/評測/
├── TechniqueExperimentSpec.schema.json
├── TechniqueExperimentResult.schema.json
├── 技術效益評測.machine.json
└── 保證/
    ├── 技術效益雙端點事前凍結.claim.json
    └── 隨機實驗證據重播一致.claim.json

nova/權威/評測/
├── 模型.py
├── 准入.py
├── 分析.py
└── test_技術效益評測.py

nova/應用/
├── 執行技術效益評測.py
└── test_執行技術效益評測.py

驗收/評測/
├── fixtures/無效技術成對樣本.json
├── fixtures/省資源但品質退化.json
└── 測_技術效益雙端點.py
```

這超過單一 task 的十檔上限，所以計畫內至少拆成三個 task：

1. schema、machine 與 experiment admission；
2. deterministic analyzer 與統計固定負控；
3. application orchestration 與黑箱 ClaimSpec。

`架構/目錄規則.toml` 需由第一個 task `Modify`，讓 `nova/權威/評測/` 成為跨 Execution 的「比較證據准入與裁定」權威，不應塞進資源權威。

## ClaimSpec

主 claim：

```text
evaluation.technique.token-upper-quality-lower.predeclared
```

第二條只管重播：

```text
evaluation.technique.recorded-evidence-replay-deterministic
```

## 固定負控

主固定負控使用「無效技術」：

- baseline 與 treatment 的生成 bytes 不必相同；
- 每個 case 的 treatment token usage 與 baseline 來自同一分布，沒有事前要求的節省；
- 品質可以完全相同。

它必須紅在：

```text
token_ratio_upper_bound <= max_token_ratio
```

例如事前要求至少省 30%，則 `max_token_ratio=0.70`；無效技術的單側上界接近或高於 `1.0`，必須拒絕。

另一固定負控是「省 token 但品質退化」：

- token endpoint 通過；
- 品質差超過 `noninferiority_margin`。

它必須只紅在：

```text
quality_difference_lower_bound >= -quality_noninferiority_margin
```

這兩個負控分別證明兩條 predicate 都有牙，且不能用其中一條補償另一條。

---

# B. ClaimSpec／ExperimentSpec 的具體形狀

## 1. 不應直接擴充目前三個純量 judge

`EQUALS`／`NOT_EQUALS`／`LESS_THAN` 是 deterministic scalar primitive。統計推斷不是多加兩個 operator 就能完成，因為它需要：

- 配對資料；
- sampling unit；
- dependence structure；
- estimator；
- confidence procedure；
- missing-data policy；
- multiplicity policy；
- frozen analysis program。

正確形狀不是：

```json
{"operator": "NON_INFERIOR", "value": 0.95}
```

那會把整套實驗設計藏在 operator implementation 裡。

應加入一個經 PrimitiveCatalog 准入的高階 primitive，例如：

```text
PAIRED_DUAL_ENDPOINT_CI_DECISION_V1
```

ClaimSpec 只引用已凍結的 `TechniqueExperimentSpecRef` 與已 sealed 的 result bundle。

## 2. 必須事前釘住的欄位

```json
{
  "experiment_id": "exp.technique.example.v1",
  "revision": 1,

  "baseline_artifact_ref": {
    "semantic_id": "technique.baseline",
    "revision": 4,
    "digest": "sha256:..."
  },
  "treatment_artifact_ref": {
    "semantic_id": "technique.candidate",
    "revision": 1,
    "digest": "sha256:..."
  },

  "population": {
    "benchmark_set_ref": "cas:...",
    "benchmark_set_digest": "sha256:...",
    "sampling_unit": "CASE",
    "inclusion_policy_ref": "cas:...",
    "exclusion_policy": "NONE_AFTER_FREEZE"
  },

  "pairing": {
    "mode": "SAME_CASE_SAME_REPLICATE_BLOCK",
    "order_randomization": "BALANCED_WITHIN_CASE",
    "assignment_seed": 483921,
    "missing_pair": "REJECT_RUN"
  },

  "replication": {
    "replicates_per_case": 8,
    "model_sampling_seeds_ref": "cas:...",
    "warmup_runs": 1,
    "warmup_included": false
  },

  "fingerprints": {
    "executor_backend_required": true,
    "model_artifact_required": true,
    "prompt_family_required": true,
    "tool_policy_required": true,
    "context_manifest_required": true,
    "runtime_environment_required": true
  },

  "token_endpoint": {
    "measure": "DELEGATION_TREE_TOTAL_TOKENS",
    "effect": "RATIO_TREATMENT_OVER_BASELINE",
    "max_token_ratio": "0.70",
    "confidence_side": "UPPER_ONE_SIDED",
    "confidence_level": "0.975",
    "estimator": "PAIRED_LOG_RATIO_GEOMETRIC_MEAN",
    "max_interval_width": "0.15"
  },

  "quality_endpoint": {
    "metric_ref": "criterion-score.example.v3",
    "direction": "HIGHER_IS_BETTER",
    "effect": "PAIRED_TREATMENT_MINUS_BASELINE",
    "noninferiority_margin": "0.03",
    "confidence_side": "LOWER_ONE_SIDED",
    "confidence_level": "0.975",
    "estimator": "PAIRED_CASE_MEAN",
    "minimum_absolute_quality": "0.80"
  },

  "analysis": {
    "method": "PAIRED_CLUSTER_BOOTSTRAP_BCA_V1",
    "resampling_unit": "CASE",
    "bootstrap_repetitions": 10000,
    "analysis_seed": 928114,
    "analysis_implementation_digest": "sha256:...",
    "missing_data_policy": "INVALIDATE_EXPERIMENT",
    "outlier_policy": "NONE",
    "multiplicity_policy": "INTERSECTION_UNION_BOTH_MUST_PASS"
  },

  "decision": {
    "accept_if": [
      "token_endpoint.upper_bound <= 0.70",
      "token_endpoint.interval_width <= 0.15",
      "quality_endpoint.lower_bound >= -0.03",
      "quality_endpoint.treatment_lower_bound >= 0.80"
    ],
    "otherwise": "REJECT_OR_INCONCLUSIVE"
  }
}
```

這裡有幾個不能混淆的值：

- `max_token_ratio=0.70`：決策門檻，至少省 30%。
- `max_interval_width=0.15`：精度門檻，避免「省 0–90%」。
- 實際報告的 savings interval：由凍結算法產出，例如 `[0.31, 0.43]`；不是人在看到資料後填入。
- `quality_noninferiority_margin`：允許相對 baseline 最多退多少。
- `minimum_absolute_quality`：防止 baseline 本身很爛，導致 treatment 與爛 baseline「非劣」卻仍不可用。

最後一條很重要。只做相對非劣性會出現：

```text
baseline quality = 0.20
treatment quality = 0.20
```

統計上可能非劣，但根本沒有使用價值。因此需同時有相對 margin 與 absolute floor。

## 3. 配對與重複的原則

- 同一 benchmark case 必須同時跑 baseline 和 treatment。
- 執行順序必須 block-randomized，避免 cache、負載與時間漂移永遠偏向其中一方。
- 若 backend 能接受 seed，兩側使用事前配好的 seed；但 seed 只是 experiment input，不宣稱 provider 一定由此產生相同 bytes。
- 統計 sampling unit 預設是 case，不是每次 retry。對同一 case 的多次重跑不能假裝成獨立樣本。
- 若一個 case 的任一側缺失，v1 直接 `INVALIDATED`；不能只刪掉難看的 pair。
- sample size 不能固定寫死為一個普世數字。它必須由事前的最小可決策效果、預估變異、α、power 算出，並寫入 frozen spec。FDA 同樣要求 margin 與設計事前確定，而非看完資料補寫。[FDA 非劣性指引](https://www.fda.gov/media/78504/download)

MLCommons 的基準實務也把 performance 與 accuracy 分開測，並要求 accuracy threshold；這正好支持「速度／資源改善不能補償品質不合格」的雙軸形狀。[MLPerf Inference](https://docs.mlcommons.org/inference/)、[MLPerf Submission Guide](https://docs.mlcommons.org/inference/submission/)

## 4. 不要自己發明統計函式庫

nova 應擁有：

- frozen experiment protocol；
- evidence manifest；
- deterministic analysis invocation；
- pass/fail policy。

nova 不應重寫 bootstrap、信賴區間或非劣性統計演算法。應使用釘版的成熟統計實作，並把 package/version/code digest 納入 analysis fingerprint。否則會從「可驗收工程」滑成自製統計套件。

---

# C. 決定性重播與隨機模型不衝突

你的方向對，但界線還要再切成四層。

| 層 | 必須相同嗎？ |
|---|---|
| `ExperimentSpec → RunPlan` | 必須。相同 spec bytes、catalog revision 與 compiler revision，必須得到相同配對、順序、seed schedule 與 `run_plan_digest`。 |
| live invocation → model response | 不要求。即使 request bytes 與 seed 相同，遠端模型、服務端 batching、模型 revision 或 runtime 仍可能產生不同 response。 |
| 一次已完成 live run → EvidenceBundle | 必須 immutable。實際 request bytes、response bytes、usage evidence、fingerprints、timestamps 與 failure outcome 全部內容定址。 |
| 同一 EvidenceBundle → statistical result | 必須。相同 evidence bytes、analysis implementation digest 與 analysis seed，必須得到相同 interval、decision 與 result digest。 |

因此：

```text
replay_evidence(bundle_digest)
```

必須逐 byte 可重播；

```text
rerun_model(experiment_spec)
```

則是建立新的 `MeasurementRun`，不是 replay。

新的 live run 即使使用同一 ExperimentSpec，也必須有：

```text
new_run_id
new_evidence_bundle_digest
same_experiment_spec_digest
```

不能覆寫舊 run。

### seed 的精確地位

seed 是 request manifest 的一部分，但不是「輸出可重現保證」。它只證明 nova 送出同一 sampling request。若 provider 不承諾 seeded determinism，capability evidence 必須寫：

```text
SEEDED_REQUEST_SUPPORTED
SEEDED_OUTPUT_DETERMINISM_UNSUPPORTED
```

MLCommons 對可信 benchmark 的要求也包括固定模型版本、prompt、hyperparameters、hardware、random seeds、scoring 與 post-processing，並保存足以重建結果的證據；它沒有把「模型必須每次吐相同 bytes」當成唯一的 reproducibility 定義。[MLCommons：How to Tell When a Benchmark Is Worth Trusting](https://mlcommons.org/2026/08/benchmark-is-worth-trusting/)

---

# D. 十二項重新做「官方＋權威」審計

判讀：

- **夠**：兩層共同支撐方向；nova 仍需選具體介面。
- **缺一塊**：有相鄰官方或研究支持，但證不到原句的強度。
- **多了**：原句比兩層都要求得更強，或直接與既有做法衝突。

## 1. Harness 恰好由那十一個部件構成

- 官方：**沒有**唯一十一部件標準。Anthropic 只明確描述 augmented LLM 的 retrieval、tools、memory，以及 workflow／agent patterns。[Anthropic《Building Effective Agents》](https://www.anthropic.com/engineering/building-effective-agents)
- 權威：HarnessArch 有十一 primitive，但它是實務者 taxonomy，而且列項與我們先前引用的十一項不同；不是同儕審查標準。[HarnessArch](https://www.harnessarch.com/harness)
- 裁決：**多了**。

可保留「部件完整性 checklist」，不可宣稱「業界定義就是這十一個」。

## 2. Loop 恰好需要五個終止條件

- 官方：AWS 支持 timeout、bounded retry、backoff；workflow 系統普遍有 timeout/retry/cancellation，但沒有官方規定恰好五項。[AWS Builders’ Library](https://aws.amazon.com/builders-library/timeouts-retries-and-backoff-with-jitter/)
- 權威：ranking function 以映到 well-founded set 且每步下降來證明 termination；它證成「需有進展量」的形式概念。可驗證出處包括 DOI [10.1109/ICSTW.2013.75](https://doi.org/10.1109/ICSTW.2013.75) 與 DOI [10.1016/j.cl.2015.10.001](https://doi.org/10.1016/j.cl.2015.10.001)。
- 裁決：**缺一塊**。

Ranking function 不等於實務上的 stochastic `NO_PROGRESS` detector；它支撐「進展必須被定義」，不證明「連續三次無改善」是正確窗口。五項作為 nova policy 可用，不能叫普世必要且完備。

## 3. `MachineSpec` 必須是純宣告資料

- 官方：W3C SCXML 是正式 Recommendation，確實以文件宣告 state、transition、parallel/final 與執行語意；也容許 namespaced executable-content extension。[W3C SCXML](https://www.w3.org/TR/scxml/)
- 權威：statecharts 與 executable workflow 文獻支持把控制流顯式模型化，但不要求所有 guard 都不得有程式語意。
- 裁決：**夠，但原句要縮窄**。

可證成的是「控制拓撲與轉移語意必須存在於可解析、可版本化宣告中」；證不成「整個狀態機只能是無任何 executable extension 的資料」。nova 的封閉 guard DSL 是額外拒絕。

## 4. Graph 必須是 DAG

- 官方：部分 workflow 系統以 DAG 為核心；但 LangGraph 官方明確允許 loop、conditional edge、dynamic edge 與 parallel superstep。[LangGraph Graph API](https://langchain-ai.github.io/langgraph/concepts/multi_agent/)
- 權威：科學工作流常用 DAG，但 statechart、Petri net 與一般 workflow graph 都允許循環。
- 裁決：**多了，而且作為一般 graph 地基是錯的**。

nova 可以讓某一種 lifecycle ownership graph 是 acyclic，但不能重新定義 graph engineering 等於 DAG。

## 5. Node 必須可獨立重播

- 官方：W3C PROV 提供 entity/activity/agent provenance，但沒有規定每個 node 必須可獨立重跑。[W3C PROV](https://www.w3.org/TR/prov-overview/)
- 權威：CWLProv 明確指出 provenance 可支援針對單一步驟或 sub-workflow 的 inspection 與 automatic re-enactment，DOI [10.1093/gigascience/giz095](https://doi.org/10.1093/gigascience/giz095)。科學 workflow reproducibility 也要求保存 workflow、輸入與執行環境，DOI [10.1155/2015/243180](https://doi.org/10.1155/2015/243180)。
- 裁決：**缺一塊**。

權威層強力支持「可局部重演是好性質」，但不證明每一個任意 node 都能獨立重播；有些 node 含不可逆外部效果。正確規則是：

> pure/computational node 必須可由 pinned inputs 重演；effectful node 必須重播 receipt/projection，不得重做外部效果。

## 6. Edge 只承載依賴、不承載狀態

- 官方：LangGraph 明確說 state/message 沿 edge/channel 傳遞，conditional edge 依目前 state 路由。
- 權威：dataflow、Petri net、actor/message-passing 都允許邊或 channel 承載 token/message/data。
- 裁決：**多了，原句錯誤**。

應改成「edge 不擁有隱藏的權威狀態」；不應禁止顯式、typed、manifested payload。

## 7. `InvocationEnvelope`／`ContextManifest`／guard compiler 是業界既有介面

- 官方：CloudEvents、MCP envelopes、SCXML 等分別提供事件封套、協定消息、狀態機語意；沒有這三個 nova 名稱與其組合。
- 權威：design by contract、capability systems、reproducible builds 支持顯式輸入與環境 manifest，但沒有這個 exact schema。
- 裁決：**缺一塊**。

原則有地基，具體三件套是 nova 的組合發明。

## 8. `DelegationPolicy` 的具體欄位與 usage-scope 核銷

- 官方：Anthropic 官方多 agent 系統使用獨立 context windows，並實測 multi-agent 約為 chat 的 15 倍 token；Claude Code 也把 subagent 定義為 fresh conversation。[Anthropic Multi-Agent Research](https://www.anthropic.com/engineering/multi-agent-research-system)、[Claude Code agent loop](https://code.claude.com/docs/en/agent-sdk/agent-loop)
- 權威：多代理／分散式系統研究支持 bounded fan-out、資源歸屬與訊息隔離，但沒有跨所有 agent backend 的統一 usage envelope。
- 裁決：**缺一塊**。

需要 delegation policy 與 tree-inclusive accounting 的理由夠；`max_depth/max_children/model_set/per_branch_cap` 的 exact schema 是 nova。

## 9. 子代理摘要只能是 observation

- 官方：Anthropic 說 subagent 壓縮結果供 lead agent 使用，沒有說它具有權威終局，也沒有規定只能是 observation。
- 權威：Clark–Wilson 強調 well-formed transaction 與 separation of duty，原始論文 DOI [10.1109/SP.1987.10001](https://doi.org/10.1109/SP.1987.10001)；NASA IV&V 也要求技術、管理與財務獨立。[NASA-STD-8739.8B](https://standards.nasa.gov/standard/nasa/nasa-std-87398)
- 裁決：**缺一塊，但 nova 的結論合理**。

這些來源證成「生產者不能自我認證」；不直接證成資料型別一定叫 observation。正確說法是：

> subagent 輸出可以是 proposal/evidence/observation；除非另有獨立權威驗證，不得直接成為 authoritative verdict。

## 10. 不同廠商不等於技術獨立

- 官方：NASA IV&V 把獨立性分為 technical、managerial、financial；僅組織或供應商不同不足以證明 technical independence。[NASA-STD-8739.8B](https://standards.nasa.gov/sites/default/files/standards/NASA/B/0/NASA-STD-87398-Revision-B_1.pdf)
- 權威：LLM evaluator 會有 self-preference；Panickssery、Bowman、Feng，arXiv [2404.13076](https://arxiv.org/abs/2404.13076)。但後續研究也指出部分觀測可能受 evaluator quality confound 影響，因此不能把「不同模型家族」當充分條件，也不能把同家族直接判為必然不獨立。
- 裁決：**夠**。

技術獨立必須由訓練資料、模型家族、prompt/evidence path、工具、評估方法與已測偏誤共同證成；vendor label 至多是一項 metadata。

## 11. `PrimitiveCatalog` 與 `ProtectedClaimClosure` 的 exact manifest

- 官方：SLSA 要求 provenance 由 trusted control plane 產生或驗證，使用者控制的 build step 不得任意修改；GitHub protected branches 支援 required checks。
- 權威：Clark–Wilson、supply-chain provenance 與 reference-monitor 思想支持「准入集合不能由被驗者自備」。
- 裁決：**缺一塊**。

「要有可信 catalog／protected closure」理由充分；兩份 manifest 的 exact fields 是 nova 自己設計，沒有現成標準能直接拿來。

## 12. `disclosure_units` 能提供 reusable-holdout 的統計保證

- 官方：沒有。
- 權威：Reusable Holdout 明確處理 adaptive reuse，使用具 differential-privacy 性質的機制；arXiv [1506.02629](https://arxiv.org/abs/1506.02629)。
- 裁決：**多了，如果宣稱統計有效性；夠，如果只宣稱保守的有限 transcript cap**。

`disclosure_units` 可以是安全政策：

```text
超過 N 次就不再回饋
```

但不能宣稱它保持某個顯著水準或 generalization guarantee。要有那種保證，必須實作正式 privacy accountant／reusable holdout protocol。

---

# E. 兩層都查過後，仍屬 nova 自己發明的項目

以下不是「完全沒有先例」，而是找不到業界已定義的同形介面；風險最高的是具體組合，而非背後原則。

1. **ClaimSpec 的「固定反例＋`must_fail_exactly`＋正控」三件綁定語言。**  
   mutation testing、negative testing、design by contract 各自都有地基；我查不到把三者組成這個 admission unit 的標準。

2. **ProtectedClaimClosure 的 exact transitive closure。**  
   protected branch、attestation、provenance 都有；「一份 manifest 封住 claim、predicate、固定負控、primitive catalog、TestPlan 與 checker」是 nova 的組合。

3. **PrimitiveCatalog 作為 ClaimSpec compiler 的唯一准入根。**  
   allowlist、trusted registry、capability admission 都有；這個 exact compiler contract 是 nova。

4. **三種圖嚴格分立：lifecycle ownership graph／Execution delegation tree／artifact provenance DAG。**  
   三種圖分別都有先例；把它們列為不得互相升格的架構不變式，是 nova 的發明。

5. **把任何 executor backend——包括純函式 replayer——放在完全相同的 Execution contract 下。**  
   ports/adapters 有成熟地基；這個具體平級矩陣是 nova 的組合。

6. **以 transcript enum 的資訊暴露量管理 sealed feedback。**  
   若只是 finite cap，是 nova 保守機制；若想取得統計保證，目前不夠。

這些項目不能因為「沒有現成標準」就刪；但必須比有標準的部分多一級負控、實證與退出策略。

---

# F. nova 哪裡多做了或正在造輪子

## 1. 把所有 graph 壓成 DAG

這不是保守，是錯誤抽象。既有 graph/statechart 系統已處理 cycle、conditional transition、parallel state。nova 只需限制特定 graph 的權威與持久化語意，不需重新發明一個「所有圖必須 DAG」世界。

## 2. 宣稱 edge 不能承載狀態

既有 typed channel/message/state transition 已經解決這題。正確控制的是：

- payload schema；
- owner；
- provenance；
- reducer；
- idempotency。

禁止 edge payload 反而會逼人把資料藏進共享 mutable state。

## 3. 自製統計計算核心

這輪新增的效益評測若自己寫 bootstrap、非劣性 CI、power calculation，就是明確造輪子。nova 應只固定 protocol、呼叫已釘版統計實作、驗證輸入輸出與保存證據。

## 4. 把 harness taxonomy 變成 schema

十一部件清單適合 gap analysis，不值得變成 `HarnessComponentKind` 封閉 enum。不同官方系統會用不同邊界，封閉 taxonomy 只會讓 nova 忙著替名詞維持 mapping。

## 5. 為每一種 benchmark 重建 load generator

MLPerf 已證明 load generator、performance run、accuracy run、compliance checker 的分離形狀。nova 應建立通用 experiment port，能包裝既有 benchmark runner，不應要求所有評測改寫成 nova 原生測試。[MLPerf Submission Guide](https://docs.mlcommons.org/inference/submission/)

## 6. 要求 live stochastic model byte-identical

這會把可重播性用錯地方。應重播的是：

- frozen run plan；
- 已錄下的 request/response/evidence；
- deterministic analysis。

不是要求外部隨機系統重新取樣時重現舊 bytes。

---

最終裁決是：

- plan 07 不刪，但從「技術價值判定」退回資源安全與派工平衡。
- 技術是否值得使用，新開 06B，以比較實驗為獨立權威生命週期。
- 品質採非劣性；token 採資源比率上界；兩者 AND，另有 interval-width 與 absolute-quality floor。
- nova 保證 experiment specification、錄得證據與分析可重播；不保證 live stochastic executor 重跑產生相同 bytes。
- 十二項中，真正得到兩層充分支持的是「宣告式控制拓撲」與「供應商不同不構成技術獨立」；多數其餘項目有原則地基，但 nova 的 exact schema 仍是自己的組合責任。
