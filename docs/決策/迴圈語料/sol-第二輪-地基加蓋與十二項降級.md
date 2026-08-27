codex
我不會直接接受「加蓋只能增加拒絕」：`nova[llm]` 本身就是反例——安裝 extra 會把原本 `UNSUPPORTED` 的請求變成可執行，接受集合會擴大。我要先用官方規格中的 capability negotiation／extension 規則校正這條判準，再逐格區分「地基」「官方容許的擴充」「nova 額外拒絕」。
web search: 
web search: Anthropic building effective agents workflows agents orchestrator workers evaluator optimizer official ...
context compacted
web search: 
web search: site:packaging.python.org dependency specifiers extras optional dependencies official ...
codex
先下結論：我不同意「加蓋只能增加拒絕，不能改變介面」的字面版本；方向對，但少了一種合法動作——透過既有擴充點增加能力。

`nova[llm]` 本身就是反例：安裝 extra 後，原先 `UNSUPPORTED_BACKEND` 的請求變成可執行，接受集合擴大。這不是破壞地基，而是標準的可選能力擴充。Python Packaging 規格明定 extras 用來增加 optional dependencies；MCP 也允許經 capability negotiation 啟用不改核心協定的 extension。[PyPA extras 規格](https://packaging.python.org/en/latest/specifications/dependency-specifiers/)、[MCP Extensions](https://modelcontextprotocol.io/extensions/overview)

我建議把判準改成：

> 加蓋不得改變既有介面的語意與既有保證；可以：
>
> 1. 對既有能力增加拒絕；
> 2. 透過已宣告、具命名空間、具版本、可協商的擴充點增加新能力。
>
> 未理解擴充的舊元件必須 fail-closed 或回 `UNSUPPORTED_CAPABILITY`，不得把擴充靜默忽略後誤判為成功。

這是「語意單調」，不是「接受集合只能縮小」。

MCP 的官方擴充規則也直接支持這個修正版：extension 不得移除或改名欄位、改型別、改既有行為語意、增加新的必填欄位；支援則經 capabilities 協商。[MCP Extensions](https://modelcontextprotocol.io/extensions/overview)

---

## 一、上一輪解法重新拆成五格

### 1. Prompt artifact／PromptFamily

| 格 | 定案 |
|---|---|
| 地基 | AWS Bedrock Prompt Management 把 prompt 做成可建立版本、帶 variables、variants 與模型設定的資源；OpenAI Agents SDK 的 `Prompt` 也具 `id`、`version`、`variables`。這證成「prompt 是版本化 artifact」，但不證成 nova 的具體欄位。[AWS Prompt Management](https://docs.aws.amazon.com/bedrock/latest/userguide/prompt-management.html)、[OpenAI Agents SDK prompts](https://openai.github.io/openai-agents-python/ref/prompts/) |
| 拆解 | `PromptFamily` 擁有可重用、已准入的提示內容；`PromptPlan` 擁有單次 invocation 的組裝結果；backend adapter 只負責把 plan 映到原生 channel，不擁有 prompt 語意；Pursuit 只固定引用，不得原地改內容。這是 nova 的拆解，不是官方名詞。 |
| 組合 | `PromptFamilyRef(id, revision, digest)` → `PromptPlan(ordered_segments, variable_bindings, tool_policy_ref)` → `ContextManifest`／outbound digest。segment 必須標 `required_capability`；不能映射時回 `UNSUPPORTED_PROMPT_SEGMENTATION`。 |
| 擴充點 | 新 PromptFamily revision、新 namespaced segment kind、新 backend mapping。新 segment kind 必須經 capability negotiation；舊 adapter 不認得就拒絕，不能串成 blob 冒充等價。 |
| 加蓋 | nova 額外拒絕 floating `latest`、同 ref 不同 bytes、缺 digest、必要 channel 映射不成立、實際 outbound bytes 與 manifest 不符。沒有改 AWS/OpenAI 的 prompt 介面，只縮小 nova 接受的 artifact 與 invocation。 |

修正：`PromptPlan`、`ContextManifest`、segment 權限分類都不是業界既定介面，是 nova 的組合契約。

### 2. 分數來源／ScoreEvidence

| 格 | 定案 |
|---|---|
| 地基 | W3C PROV 把 provenance 表成 Entity／Activity／Agent，供可靠性與信任判斷；Vertex ML Metadata 記錄 artifact、execution、event，以及評估資料、程式與 metric 的 lineage。Vertex 的模型裁判校準另要求以 human ratings 作 ground truth 並報 balanced accuracy、F1、confusion matrix。[W3C PROV](https://www.w3.org/TR/prov-overview/)、[Vertex ML Metadata](https://cloud.google.com/vertex-ai/docs/ml-metadata/introduction)、[Vertex Judge Calibration](https://docs.cloud.google.com/vertex-ai/generative-ai/docs/models/evaluate-judge-model) |
| 拆解 | Evaluation Authority 產生分數證據；Ranking comparator 只消費已准入的證據引用；candidate／executor 不得自報具有排序權的分數。 |
| 組合 | `ScoreEvidence` 至少綁 `candidate_digest`、`criterion_revision`、`evaluator_revision`、`metric_id`、`run_id`、`value`、`evidence_refs`。`RankingDimension` 指定允許的 `score_source_policy`，不能直接接裸數值。 |
| 擴充點 | 新 evaluator kind 或 metric 以 versioned schema 產出相同 evidence envelope；LLM judge、視覺 comparator、規則 evaluator 都是 producer adapter。 |
| 加蓋 | 拒絕裸分數、candidate/revision 對不上、來源不在 allowlist、政策要求校準但無校準證據的 judge score。沒有重新定義「分數」；nova 拒絕缺 provenance 的分數取得排序權。 |

這裡若現有 nova comparator 只收數字，改成 evidence ref 看似改介面；但那不是「修改業界介面」，而是補上目前未完成的 nova 組合契約。不可把殘缺的既有計畫誤認成地基。

### 3. sealed feedback 的資訊預算

| 格 | 定案 |
|---|---|
| 地基 | Reusable Holdout 證明：對同一 holdout 做適應性查詢會破壞一般化保證；可用具差分隱私性質的釋出機制安全重用。這是統計地基。[Reusable Holdout 論文](https://arxiv.org/abs/1506.02629)、[IBM Research 摘要](https://research.ibm.com/publications/the-reusable-holdout-preserving-validity-in-adaptive-data-analysis) |
| 拆解 | Criterion Authority 擁有 sealed pool 與 release ledger；feedback reducer 只產生允許揭露的 packet；Pursuit／executor 不知道剩餘案例內容，也不能重置 ledger。 |
| 組合 | `FeedbackDisclosurePolicy` ＋ `DisclosureLedger` ＋ `FeedbackPacketManifest`；ledger key 必須跨同一 sealed pool 的 sibling／superseding Pursuit 累積，不能用開新 Pursuit 洗額度。 |
| 擴充點 | `disclosure_mechanism` SPI：v1 可用保守的 `FINITE_TRANSCRIPT_CAP`；未來才加入經驗證的 `DP_REUSABLE_HOLDOUT` 與 privacy accountant。 |
| 加蓋 | 超過資訊釋出上限、ledger 不可證明完整、或想跨 Pursuit 重置時拒絕 feedback／燒掉 pool。沒有改 reusable-holdout 的介面；但 `disclosure_units` 是 nova 自訂保守策略，不得宣稱它具有 DP 的統計保證。 |

重要更正：單純把 enum 欄位換算 bit 數，只是資訊暴露上界，不是正式 reusable-holdout 保證。沒有 epsilon/delta accountant，就不能掛該地基的招牌。

### 4. 視覺判準

| 格 | 定案 |
|---|---|
| 地基 | Playwright 官方 visual comparison 以 reference screenshot 比較實際輸出，也明講 OS、版本、硬體、headless mode 等會影響 rendering，baseline 應在相同環境生成。[Playwright Visual Comparisons](https://playwright.dev/docs/test-snapshots) |
| 拆解 | Criterion Authority 擁有 protocol 與終局 verdict；capture adapter 只擷取畫面與環境證據；comparator adapter 算差異；renderer 不得自行決定 pass。 |
| 組合 | `VisualCase` 引用 sealed baseline；`VisualEvaluationProtocol` 固定 capture steps、viewport、font/render environment fingerprint、comparator、threshold 與 revision；輸出 `VisualEvidence` 再由 criterion fold 成 verdict。 |
| 擴充點 | Playwright、遊戲 renderer、影片序列、VLM judge 都透過 evaluator port 加入，各自宣告 capability；核心不內建 Playwright 語意。 |
| 加蓋 | baseline 揭露、評估後調 threshold、環境 fingerprint 不符、缺 pinned font、capture protocol 漂移一律拒絕。這些是對 Playwright 可能仍可執行的比較增加拒絕，沒有改 pixel comparator 的意義。 |

「驗 node/edge ids 而非像素」只能是某一類圖表的 adapter policy，不能升格成所有視覺評估的地基。

### 5. 原語目錄／PrimitiveCatalog

| 格 | 定案 |
|---|---|
| 地基 | 最小權限與 allowlist 是 OWASP 的安全控制；SLSA 則要求可信 builder 與可驗證 provenance。但「PrimitiveCatalog」這個物件沒有業界官方標準，是 nova 的組合設計。[OWASP Excessive Agency](https://genai.owasp.org/llmrisk/llm062025-excessive-agency/)、[SLSA Build Provenance](https://slsa.dev/spec/v1.0/provenance) |
| 拆解 | Definition／Admission Authority 擁有原語集合與 revision；compiler 只消費已准入 catalog ref；呼叫端不得提交一份自備 catalog；原語 implementation 不得准入自己。 |
| 組合 | `PrimitiveCatalogManifest` 固定 catalog revision、primitive id、implementation digest、input/output type、effect class、required isolation、negative-control ref。`compile_claim` 接 `catalog_ref`，不是任意 catalog object。 |
| 擴充點 | 新 primitive 使用 namespaced id、新 revision、獨立 admission；不得改既有 primitive id 的語意。 |
| 加蓋 | 拒絕 caller-supplied catalog、同 id 不同 digest、缺負控、執法能力不足、未准入 primitive。這完全符合「增加拒絕」。 |

這一項的「地基」欄只能證成 allowlist／provenance 原則，證不成 manifest 的具體形狀；具體形狀是 nova。

### 6. ProtectedClaimClosure

| 格 | 定案 |
|---|---|
| 地基 | GitHub protected branches／required status checks 可要求檢查成功才合併，也能鎖定 status check 的預期來源；NIST SSDF、SLSA 提供 artifact integrity 與 provenance 原則。[GitHub Protected Branches](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches)、[NIST SSDF](https://csrc.nist.gov/pubs/sp/800/218/final) |
| 拆解 | 規格作者建立 candidate claim；Admission Authority 核准 revision；protected-base verifier 擁有已准入 closure；實作者只改 subject。PR 內的檔案不能自行聲稱自己沒被改弱。 |
| 組合 | `ProtectedClaimClosureManifest` 綁 `claim_id/revision/digest`、predicate／fixed counterexample／primitive catalog digests、TestPlan digest、admission evidence、required-check identity。 |
| 擴充點 | 新 claim 或 successor revision 產生新 closure；舊 closure append-only 保留。RequirementChange 是合法替換路徑。 |
| 加蓋 | 若 PR 修改 closure 內任一 artifact，卻沒有獨立 RequirementChange admission，required check 必須紅；新增 claim 不受舊 closure 禁寫，但不能冒充已准入。這不改 GitHub 介面，只增加合併拒絕條件。 |

---

## 二、五門 engineering 的逐格校正

### Harness

| 格 | 校正 |
|---|---|
| 地基 | 「十一部件」不能當官方地基。目前能找到的是 HarnessArch 的私人 taxonomy，而且它列的是 Instructions、Context Delivery、Context Management、Tool Interfaces、Execution Environment、Durable State、Orchestration、Sub-agents、Skills、Verification & Observability、Evolution，並不是你列的那十一項。[HarnessArch](https://www.harnessarch.com/harness) 因此應降為參考分類，不是官方標準。Anthropic 官方只明確說 augmented LLM 通常由 retrieval、tools、memory 等能力增強，沒有頒布唯一十一部件表。[Anthropic Building Effective Agents](https://www.anthropic.com/engineering/building-effective-agents) |
| 拆解 | 應拆為 execution supervision、context assembly、tool mediation、state、evaluation、adapter；這是 nova 自己的軟體分解，不是假裝業界標準。 |
| 組合 | `InvocationEnvelope` ＋ immutable `ContextManifest` 是合理的 nova 契約，但沒有官方出處。 |
| 擴充點 | backend adapter port 正確；optional extra 增加 backend capability 有 PyPA extras 與 capability negotiation 類比支撐。 |
| 加蓋 | 「驗收權不在執行者」與 `UNSUPPORTED_*` 不靜默降級是 nova 的額外拒絕。它們不改 backend 原生介面。 |

結論：你填的 harness「地基」過度聲稱。應寫成「多份官方實踐的聯集」，不能寫成「業界正式十一部件」。

### Loop

| 格 | 校正 |
|---|---|
| 地基 | 硬 timeout、bounded retries、backoff、budget 是成熟運維做法；AWS 官方有 timeout/retry/backoff 指引。但「硬迭代／成本／無進展／目標／逾時恰好五項」來自 Data Science Dojo 文章，不是官方標準，必須降級成權威實務建議。[AWS Builders’ Library：Timeouts, retries and backoff](https://aws.amazon.com/builders-library/timeouts-retries-and-backoff-with-jitter/) |
| 拆解 | `MachineSpec` 必須是宣告資料，是 nova 為可檢視、可 lint、可重播做的選擇；不是通用 loop 定義。 |
| 組合 | guard compiler 是 nova 契約。官方地基只要求執行語意清楚，沒有指定必須 compiler。 |
| 擴充點 | versioned predicate registry 可加入新終止 predicate；新 predicate 不得改既有 predicate 語意。 |
| 加蓋 | executor 不能延長 deadline、改 budget、改 criterion；未知 predicate fail-closed。這是合法增加拒絕。 |

「新終止 predicate 以資料加入」也不能無條件成立：若 predicate 需要新觀測能力，必須同時協商 capability，不能只塞資料。

### Graph

| 格 | 校正 |
|---|---|
| 地基 | 你填的「DAG 排程、依賴、可並行性、關鍵路徑」只是 workflow graph 的一個子類，不是完整地基。LangGraph 官方允許循環、conditional edge、dynamic edge、shared state 與 parallel supersteps；其基本分解是 State／Nodes／Edges。[LangGraph Graph API](https://langchain-ai.github.io/langgraph/concepts/multi_agent/) |
| 拆解 | 「node 是可獨立重播單位」沒有官方普遍出處，是 nova 的限制；LangGraph node 可以做 side effect，未必可獨立重播。 |
| 組合 | 「邊只承載依賴不承載狀態」不正確。LangGraph 明說 message/state 沿 edge 傳遞；conditional edge 也依 state 路由。應改為：「邊擁有合法路由語意；state payload 經明確 schema/channel 傳遞，不把隱藏 mutable state 塞進 edge implementation。」 |
| 擴充點 | 新 node type、edge predicate、state channel 經 graph schema version 加入；動態 fan-out 可用顯式 `Send` 類契約，而不是讓 executor 私自改 graph。 |
| 加蓋 | executor 的實際 trace 不能自動升格成持久 graph definition；未准入 edge 拒絕。這是 nova 限制，不改 graph 的基本介面。 |

因此 graph 這格有兩項必改：不能把 DAG 當全部，不能宣稱 edge 不承載狀態。

### Agentic

| 格 | 校正 |
|---|---|
| 地基 | Anthropic 官方區分 workflow 與 agent，並提出 prompt chaining、routing、parallelization、orchestrator-workers、evaluator-optimizer 五種 workflow pattern；文章另有 augmented LLM 與 autonomous agents，因此「Anthropic 五模式」應精確寫成「五種 workflow pattern」，不是 agentic systems 的完整分類。[Anthropic Building Effective Agents](https://www.anthropic.com/engineering/building-effective-agents) |
| 拆解 | agent 是 Execution 內可替換求解器、不掌握控制平面，是 nova 的架構裁定，不是 Anthropic 對 agent 的定義。它與官方「agent 自主選擇工具，但外部擁有目標與護欄」相容。 |
| 組合 | Execution contract 必須分開 goal、scope、tool capability、resource envelope、observation/result；具體 schema 是 nova。 |
| 擴充點 | 新 agent backend 透過 capability-negotiated adapter 加入；支持不同工具、structured output、delegation、prompt segmentation。 |
| 加蓋 | agent 不得擴 scope、宣告 Work 完成、改 receipt、寫權威 state。這些是 nova 拒絕，不是官方 agent 定義。 |

「工具授權」有官方安全實踐支持，但不是 Anthropic 五模式的一部分，兩個來源不能黏成同一條官方地基。

### Multi-agent

| 格 | 校正 |
|---|---|
| 地基 | Anthropic 官方研究支持 orchestrator-worker、平行 subagent、各自 prompt/tool/context、以及高 token 成本；並指出它適合 breadth-first、可獨立探索的工作，不適合需要高度共享 context、強依賴的 coding 類工作。[Anthropic Multi-Agent Research System](https://www.anthropic.com/engineering/multi-agent-research-system) |
| 拆解 | delegation tree 屬單一 Execution；lifecycle ownership graph 與 artifact provenance DAG 分開。這是 nova 的必要拆解，不是 Anthropic 的正式三圖模型。 |
| 組合 | `DelegationPolicy`、child invocation envelope、tree-inclusive usage evidence、fan-out/depth/model bounds。這些具體契約沒有單一官方規格，是 nova 組合。 |
| 擴充點 | backend 可宣告 `DELEGATION` capability；新 delegation strategy 經 versioned policy kind 加入。沒有能力就拒絕，不能模擬成未計價背景工作。 |
| 加蓋 | child summary 只是 observation；不得取得 completion／budget／criterion authority。「不同廠商不等於技術獨立」也是 nova 的證據政策，不是 Anthropic 官方定義。 |

你原本填的「delegation policy、context isolation、fan-out、usage scope 歸屬」不能整包掛成業界地基。官方只支撐多代理的模式、收益、成本與適用條件；具體權威與核銷規則是 nova 自己的工程解。

---

## 三、哪些東西必須降級

以下目前引不出能支撐其完整語意的官方出處，不能再稱為地基：

- harness 恰好由你列的十一個部件構成。
- loop 恰好有五個「必要」終止條件。
- `MachineSpec` 必須是純宣告資料。
- graph 必須是 DAG。
- graph node 必須可獨立重播。
- edge 只承載依賴、不承載狀態。
- `InvocationEnvelope`、`ContextManifest`、guard compiler 是業界既有介面。
- `DelegationPolicy` 的具體欄位與 usage-scope 核銷規則。
- 子代理摘要只能是 observation。
- 不同廠商不等於技術獨立。
- `PrimitiveCatalog` 與 `ProtectedClaimClosure` 的具體 manifest。
- disclosure units 能提供 reusable-holdout 的統計保證。

它們不必刪；正確標籤是：

- nova 的拆解決定；
- nova 的組合契約；
- nova 額外拒絕；
- 或待驗證的擴充政策。

最後，地基也不能理解成「永遠凍結某家廠商今天的 JSON」。真正不可破壞的是已採用介面的語意與相容性規則。否則業界正式推出新版本時，nova 反而不能跟進。正確的不變式是：

> 既有版本語意不改；新能力走新版本或協商式擴充；nova 的政策只能拒絕既有請求，不能把既有拒絕偷偷翻成接受。安裝明示 extra 或協商成功則可以增加能力。
tokens used
69,332
先下結論：我不同意「加蓋只能增加拒絕，不能改變介面」的字面版本；方向對，但少了一種合法動作——透過既有擴充點增加能力。

`nova[llm]` 本身就是反例：安裝 extra 後，原先 `UNSUPPORTED_BACKEND` 的請求變成可執行，接受集合擴大。這不是破壞地基，而是標準的可選能力擴充。Python Packaging 規格明定 extras 用來增加 optional dependencies；MCP 也允許經 capability negotiation 啟用不改核心協定的 extension。[PyPA extras 規格](https://packaging.python.org/en/latest/specifications/dependency-specifiers/)、[MCP Extensions](https://modelcontextprotocol.io/extensions/overview)

我建議把判準改成：

> 加蓋不得改變既有介面的語意與既有保證；可以：
>
> 1. 對既有能力增加拒絕；
> 2. 透過已宣告、具命名空間、具版本、可協商的擴充點增加新能力。
>
> 未理解擴充的舊元件必須 fail-closed 或回 `UNSUPPORTED_CAPABILITY`，不得把擴充靜默忽略後誤判為成功。

這是「語意單調」，不是「接受集合只能縮小」。

MCP 的官方擴充規則也直接支持這個修正版：extension 不得移除或改名欄位、改型別、改既有行為語意、增加新的必填欄位；支援則經 capabilities 協商。[MCP Extensions](https://modelcontextprotocol.io/extensions/overview)

---

## 一、上一輪解法重新拆成五格

### 1. Prompt artifact／PromptFamily

| 格 | 定案 |
|---|---|
| 地基 | AWS Bedrock Prompt Management 把 prompt 做成可建立版本、帶 variables、variants 與模型設定的資源；OpenAI Agents SDK 的 `Prompt` 也具 `id`、`version`、`variables`。這證成「prompt 是版本化 artifact」，但不證成 nova 的具體欄位。[AWS Prompt Management](https://docs.aws.amazon.com/bedrock/latest/userguide/prompt-management.html)、[OpenAI Agents SDK prompts](https://openai.github.io/openai-agents-python/ref/prompts/) |
| 拆解 | `PromptFamily` 擁有可重用、已准入的提示內容；`PromptPlan` 擁有單次 invocation 的組裝結果；backend adapter 只負責把 plan 映到原生 channel，不擁有 prompt 語意；Pursuit 只固定引用，不得原地改內容。這是 nova 的拆解，不是官方名詞。 |
| 組合 | `PromptFamilyRef(id, revision, digest)` → `PromptPlan(ordered_segments, variable_bindings, tool_policy_ref)` → `ContextManifest`／outbound digest。segment 必須標 `required_capability`；不能映射時回 `UNSUPPORTED_PROMPT_SEGMENTATION`。 |
| 擴充點 | 新 PromptFamily revision、新 namespaced segment kind、新 backend mapping。新 segment kind 必須經 capability negotiation；舊 adapter 不認得就拒絕，不能串成 blob 冒充等價。 |
| 加蓋 | nova 額外拒絕 floating `latest`、同 ref 不同 bytes、缺 digest、必要 channel 映射不成立、實際 outbound bytes 與 manifest 不符。沒有改 AWS/OpenAI 的 prompt 介面，只縮小 nova 接受的 artifact 與 invocation。 |

修正：`PromptPlan`、`ContextManifest`、segment 權限分類都不是業界既定介面，是 nova 的組合契約。

### 2. 分數來源／ScoreEvidence

| 格 | 定案 |
|---|---|
| 地基 | W3C PROV 把 provenance 表成 Entity／Activity／Agent，供可靠性與信任判斷；Vertex ML Metadata 記錄 artifact、execution、event，以及評估資料、程式與 metric 的 lineage。Vertex 的模型裁判校準另要求以 human ratings 作 ground truth 並報 balanced accuracy、F1、confusion matrix。[W3C PROV](https://www.w3.org/TR/prov-overview/)、[Vertex ML Metadata](https://cloud.google.com/vertex-ai/docs/ml-metadata/introduction)、[Vertex Judge Calibration](https://docs.cloud.google.com/vertex-ai/generative-ai/docs/models/evaluate-judge-model) |
| 拆解 | Evaluation Authority 產生分數證據；Ranking comparator 只消費已准入的證據引用；candidate／executor 不得自報具有排序權的分數。 |
| 組合 | `ScoreEvidence` 至少綁 `candidate_digest`、`criterion_revision`、`evaluator_revision`、`metric_id`、`run_id`、`value`、`evidence_refs`。`RankingDimension` 指定允許的 `score_source_policy`，不能直接接裸數值。 |
| 擴充點 | 新 evaluator kind 或 metric 以 versioned schema 產出相同 evidence envelope；LLM judge、視覺 comparator、規則 evaluator 都是 producer adapter。 |
| 加蓋 | 拒絕裸分數、candidate/revision 對不上、來源不在 allowlist、政策要求校準但無校準證據的 judge score。沒有重新定義「分數」；nova 拒絕缺 provenance 的分數取得排序權。 |

這裡若現有 nova comparator 只收數字，改成 evidence ref 看似改介面；但那不是「修改業界介面」，而是補上目前未完成的 nova 組合契約。不可把殘缺的既有計畫誤認成地基。

### 3. sealed feedback 的資訊預算

| 格 | 定案 |
|---|---|
| 地基 | Reusable Holdout 證明：對同一 holdout 做適應性查詢會破壞一般化保證；可用具差分隱私性質的釋出機制安全重用。這是統計地基。[Reusable Holdout 論文](https://arxiv.org/abs/1506.02629)、[IBM Research 摘要](https://research.ibm.com/publications/the-reusable-holdout-preserving-validity-in-adaptive-data-analysis) |
| 拆解 | Criterion Authority 擁有 sealed pool 與 release ledger；feedback reducer 只產生允許揭露的 packet；Pursuit／executor 不知道剩餘案例內容，也不能重置 ledger。 |
| 組合 | `FeedbackDisclosurePolicy` ＋ `DisclosureLedger` ＋ `FeedbackPacketManifest`；ledger key 必須跨同一 sealed pool 的 sibling／superseding Pursuit 累積，不能用開新 Pursuit 洗額度。 |
| 擴充點 | `disclosure_mechanism` SPI：v1 可用保守的 `FINITE_TRANSCRIPT_CAP`；未來才加入經驗證的 `DP_REUSABLE_HOLDOUT` 與 privacy accountant。 |
| 加蓋 | 超過資訊釋出上限、ledger 不可證明完整、或想跨 Pursuit 重置時拒絕 feedback／燒掉 pool。沒有改 reusable-holdout 的介面；但 `disclosure_units` 是 nova 自訂保守策略，不得宣稱它具有 DP 的統計保證。 |

重要更正：單純把 enum 欄位換算 bit 數，只是資訊暴露上界，不是正式 reusable-holdout 保證。沒有 epsilon/delta accountant，就不能掛該地基的招牌。

### 4. 視覺判準

| 格 | 定案 |
|---|---|
| 地基 | Playwright 官方 visual comparison 以 reference screenshot 比較實際輸出，也明講 OS、版本、硬體、headless mode 等會影響 rendering，baseline 應在相同環境生成。[Playwright Visual Comparisons](https://playwright.dev/docs/test-snapshots) |
| 拆解 | Criterion Authority 擁有 protocol 與終局 verdict；capture adapter 只擷取畫面與環境證據；comparator adapter 算差異；renderer 不得自行決定 pass。 |
| 組合 | `VisualCase` 引用 sealed baseline；`VisualEvaluationProtocol` 固定 capture steps、viewport、font/render environment fingerprint、comparator、threshold 與 revision；輸出 `VisualEvidence` 再由 criterion fold 成 verdict。 |
| 擴充點 | Playwright、遊戲 renderer、影片序列、VLM judge 都透過 evaluator port 加入，各自宣告 capability；核心不內建 Playwright 語意。 |
| 加蓋 | baseline 揭露、評估後調 threshold、環境 fingerprint 不符、缺 pinned font、capture protocol 漂移一律拒絕。這些是對 Playwright 可能仍可執行的比較增加拒絕，沒有改 pixel comparator 的意義。 |

「驗 node/edge ids 而非像素」只能是某一類圖表的 adapter policy，不能升格成所有視覺評估的地基。

### 5. 原語目錄／PrimitiveCatalog

| 格 | 定案 |
|---|---|
| 地基 | 最小權限與 allowlist 是 OWASP 的安全控制；SLSA 則要求可信 builder 與可驗證 provenance。但「PrimitiveCatalog」這個物件沒有業界官方標準，是 nova 的組合設計。[OWASP Excessive Agency](https://genai.owasp.org/llmrisk/llm062025-excessive-agency/)、[SLSA Build Provenance](https://slsa.dev/spec/v1.0/provenance) |
| 拆解 | Definition／Admission Authority 擁有原語集合與 revision；compiler 只消費已准入 catalog ref；呼叫端不得提交一份自備 catalog；原語 implementation 不得准入自己。 |
| 組合 | `PrimitiveCatalogManifest` 固定 catalog revision、primitive id、implementation digest、input/output type、effect class、required isolation、negative-control ref。`compile_claim` 接 `catalog_ref`，不是任意 catalog object。 |
| 擴充點 | 新 primitive 使用 namespaced id、新 revision、獨立 admission；不得改既有 primitive id 的語意。 |
| 加蓋 | 拒絕 caller-supplied catalog、同 id 不同 digest、缺負控、執法能力不足、未准入 primitive。這完全符合「增加拒絕」。 |

這一項的「地基」欄只能證成 allowlist／provenance 原則，證不成 manifest 的具體形狀；具體形狀是 nova。

### 6. ProtectedClaimClosure

| 格 | 定案 |
|---|---|
| 地基 | GitHub protected branches／required status checks 可要求檢查成功才合併，也能鎖定 status check 的預期來源；NIST SSDF、SLSA 提供 artifact integrity 與 provenance 原則。[GitHub Protected Branches](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches)、[NIST SSDF](https://csrc.nist.gov/pubs/sp/800/218/final) |
| 拆解 | 規格作者建立 candidate claim；Admission Authority 核准 revision；protected-base verifier 擁有已准入 closure；實作者只改 subject。PR 內的檔案不能自行聲稱自己沒被改弱。 |
| 組合 | `ProtectedClaimClosureManifest` 綁 `claim_id/revision/digest`、predicate／fixed counterexample／primitive catalog digests、TestPlan digest、admission evidence、required-check identity。 |
| 擴充點 | 新 claim 或 successor revision 產生新 closure；舊 closure append-only 保留。RequirementChange 是合法替換路徑。 |
| 加蓋 | 若 PR 修改 closure 內任一 artifact，卻沒有獨立 RequirementChange admission，required check 必須紅；新增 claim 不受舊 closure 禁寫，但不能冒充已准入。這不改 GitHub 介面，只增加合併拒絕條件。 |

---

## 二、五門 engineering 的逐格校正

### Harness

| 格 | 校正 |
|---|---|
| 地基 | 「十一部件」不能當官方地基。目前能找到的是 HarnessArch 的私人 taxonomy，而且它列的是 Instructions、Context Delivery、Context Management、Tool Interfaces、Execution Environment、Durable State、Orchestration、Sub-agents、Skills、Verification & Observability、Evolution，並不是你列的那十一項。[HarnessArch](https://www.harnessarch.com/harness) 因此應降為參考分類，不是官方標準。Anthropic 官方只明確說 augmented LLM 通常由 retrieval、tools、memory 等能力增強，沒有頒布唯一十一部件表。[Anthropic Building Effective Agents](https://www.anthropic.com/engineering/building-effective-agents) |
| 拆解 | 應拆為 execution supervision、context assembly、tool mediation、state、evaluation、adapter；這是 nova 自己的軟體分解，不是假裝業界標準。 |
| 組合 | `InvocationEnvelope` ＋ immutable `ContextManifest` 是合理的 nova 契約，但沒有官方出處。 |
| 擴充點 | backend adapter port 正確；optional extra 增加 backend capability 有 PyPA extras 與 capability negotiation 類比支撐。 |
| 加蓋 | 「驗收權不在執行者」與 `UNSUPPORTED_*` 不靜默降級是 nova 的額外拒絕。它們不改 backend 原生介面。 |

結論：你填的 harness「地基」過度聲稱。應寫成「多份官方實踐的聯集」，不能寫成「業界正式十一部件」。

### Loop

| 格 | 校正 |
|---|---|
| 地基 | 硬 timeout、bounded retries、backoff、budget 是成熟運維做法；AWS 官方有 timeout/retry/backoff 指引。但「硬迭代／成本／無進展／目標／逾時恰好五項」來自 Data Science Dojo 文章，不是官方標準，必須降級成權威實務建議。[AWS Builders’ Library：Timeouts, retries and backoff](https://aws.amazon.com/builders-library/timeouts-retries-and-backoff-with-jitter/) |
| 拆解 | `MachineSpec` 必須是宣告資料，是 nova 為可檢視、可 lint、可重播做的選擇；不是通用 loop 定義。 |
| 組合 | guard compiler 是 nova 契約。官方地基只要求執行語意清楚，沒有指定必須 compiler。 |
| 擴充點 | versioned predicate registry 可加入新終止 predicate；新 predicate 不得改既有 predicate 語意。 |
| 加蓋 | executor 不能延長 deadline、改 budget、改 criterion；未知 predicate fail-closed。這是合法增加拒絕。 |

「新終止 predicate 以資料加入」也不能無條件成立：若 predicate 需要新觀測能力，必須同時協商 capability，不能只塞資料。

### Graph

| 格 | 校正 |
|---|---|
| 地基 | 你填的「DAG 排程、依賴、可並行性、關鍵路徑」只是 workflow graph 的一個子類，不是完整地基。LangGraph 官方允許循環、conditional edge、dynamic edge、shared state 與 parallel supersteps；其基本分解是 State／Nodes／Edges。[LangGraph Graph API](https://langchain-ai.github.io/langgraph/concepts/multi_agent/) |
| 拆解 | 「node 是可獨立重播單位」沒有官方普遍出處，是 nova 的限制；LangGraph node 可以做 side effect，未必可獨立重播。 |
| 組合 | 「邊只承載依賴不承載狀態」不正確。LangGraph 明說 message/state 沿 edge 傳遞；conditional edge 也依 state 路由。應改為：「邊擁有合法路由語意；state payload 經明確 schema/channel 傳遞，不把隱藏 mutable state 塞進 edge implementation。」 |
| 擴充點 | 新 node type、edge predicate、state channel 經 graph schema version 加入；動態 fan-out 可用顯式 `Send` 類契約，而不是讓 executor 私自改 graph。 |
| 加蓋 | executor 的實際 trace 不能自動升格成持久 graph definition；未准入 edge 拒絕。這是 nova 限制，不改 graph 的基本介面。 |

因此 graph 這格有兩項必改：不能把 DAG 當全部，不能宣稱 edge 不承載狀態。

### Agentic

| 格 | 校正 |
|---|---|
| 地基 | Anthropic 官方區分 workflow 與 agent，並提出 prompt chaining、routing、parallelization、orchestrator-workers、evaluator-optimizer 五種 workflow pattern；文章另有 augmented LLM 與 autonomous agents，因此「Anthropic 五模式」應精確寫成「五種 workflow pattern」，不是 agentic systems 的完整分類。[Anthropic Building Effective Agents](https://www.anthropic.com/engineering/building-effective-agents) |
| 拆解 | agent 是 Execution 內可替換求解器、不掌握控制平面，是 nova 的架構裁定，不是 Anthropic 對 agent 的定義。它與官方「agent 自主選擇工具，但外部擁有目標與護欄」相容。 |
| 組合 | Execution contract 必須分開 goal、scope、tool capability、resource envelope、observation/result；具體 schema 是 nova。 |
| 擴充點 | 新 agent backend 透過 capability-negotiated adapter 加入；支持不同工具、structured output、delegation、prompt segmentation。 |
| 加蓋 | agent 不得擴 scope、宣告 Work 完成、改 receipt、寫權威 state。這些是 nova 拒絕，不是官方 agent 定義。 |

「工具授權」有官方安全實踐支持，但不是 Anthropic 五模式的一部分，兩個來源不能黏成同一條官方地基。

### Multi-agent

| 格 | 校正 |
|---|---|
| 地基 | Anthropic 官方研究支持 orchestrator-worker、平行 subagent、各自 prompt/tool/context、以及高 token 成本；並指出它適合 breadth-first、可獨立探索的工作，不適合需要高度共享 context、強依賴的 coding 類工作。[Anthropic Multi-Agent Research System](https://www.anthropic.com/engineering/multi-agent-research-system) |
| 拆解 | delegation tree 屬單一 Execution；lifecycle ownership graph 與 artifact provenance DAG 分開。這是 nova 的必要拆解，不是 Anthropic 的正式三圖模型。 |
| 組合 | `DelegationPolicy`、child invocation envelope、tree-inclusive usage evidence、fan-out/depth/model bounds。這些具體契約沒有單一官方規格，是 nova 組合。 |
| 擴充點 | backend 可宣告 `DELEGATION` capability；新 delegation strategy 經 versioned policy kind 加入。沒有能力就拒絕，不能模擬成未計價背景工作。 |
| 加蓋 | child summary 只是 observation；不得取得 completion／budget／criterion authority。「不同廠商不等於技術獨立」也是 nova 的證據政策，不是 Anthropic 官方定義。 |

你原本填的「delegation policy、context isolation、fan-out、usage scope 歸屬」不能整包掛成業界地基。官方只支撐多代理的模式、收益、成本與適用條件；具體權威與核銷規則是 nova 自己的工程解。

---

## 三、哪些東西必須降級

以下目前引不出能支撐其完整語意的官方出處，不能再稱為地基：

- harness 恰好由你列的十一個部件構成。
- loop 恰好有五個「必要」終止條件。
- `MachineSpec` 必須是純宣告資料。
- graph 必須是 DAG。
- graph node 必須可獨立重播。
- edge 只承載依賴、不承載狀態。
- `InvocationEnvelope`、`ContextManifest`、guard compiler 是業界既有介面。
- `DelegationPolicy` 的具體欄位與 usage-scope 核銷規則。
- 子代理摘要只能是 observation。
- 不同廠商不等於技術獨立。
- `PrimitiveCatalog` 與 `ProtectedClaimClosure` 的具體 manifest。
- disclosure units 能提供 reusable-holdout 的統計保證。

它們不必刪；正確標籤是：

- nova 的拆解決定；
- nova 的組合契約；
- nova 額外拒絕；
- 或待驗證的擴充政策。

最後，地基也不能理解成「永遠凍結某家廠商今天的 JSON」。真正不可破壞的是已採用介面的語意與相容性規則。否則業界正式推出新版本時，nova 反而不能跟進。正確的不變式是：

> 既有版本語意不改；新能力走新版本或協商式擴充；nova 的政策只能拒絕既有請求，不能把既有拒絕偷偷翻成接受。安裝明示 extra 或協商成功則可以增加能力。
