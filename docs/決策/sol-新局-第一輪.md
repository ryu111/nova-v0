# 新局第一輪：從生命週期切層、拆掉舊系統殘影

## 0. 範圍與總判決

【查證】本輪只使用題目本身、[五學科研究](../設計/五學科/)及四份重做文件；沒有讀取題目禁止的既有實作、測試、交接或其他設計文件。（來源：本輪工具讀取紀錄與題目允許清單。）

【推論】因此本文不能、也不會聲稱任何既有程式「現在怎麼運作」；對舊系統的判斷只來自四份重做文件自己留下的語言指紋。

【查證】我的切層資格在讀取《邊界裁定》的結論前先固定為：一層必須擁有可辨識的生命週期物件、自己的狀態與終態、崩潰後的恢復責任，並透過可替換契約組合下一層；只有 helper、policy、profile 或資料欄位者不算。（來源：本輪閱讀《邊界裁定》前的工作紀錄。）

【推論】這個先後順序足以區分本輪的「獨立得到」和「看完後合理化」，但不證明三層結論唯一。

【推論】總判決如下：

- 【推論】垂直組合仍是三層，但應叫「執行封套／目標追求／持久工作協調」，不是「執行器／迴圈／圖」。數量相同是獨立收斂；第三層叫「圖」則把可選資料結構冒充成必要本體。
- 【推論】判準保管、預算核銷、外部副作用交付是三個橫向控制面，不是第四、第五、第六個垂直層。它們各有生命週期，但不因此自動取得「層」的資格。
- 【推論】《重做規矩》是一份遷移期語言清洗規則，不是新系統規格，而且它自己保留了一整張舊名詞羅塞塔石碑；《主動性》把四種能力排成四層，是分類錯誤；《選型原則》後半是舊系統驗屍紀錄；《儲存選型》用漏算的寫入模型和測試方便性把結論預先做成了 SQLite。
- 【推論】SQLite 仍可能是正解，但「低三個數量級」沒有被證成，「不用多連線 WAL」也不是一個完整拓撲。必須先裁定誰持有連線、讀交易多長、是否跨主機，再選 journal mode 與引擎。
- 【推論】「判準完全不洩漏」和「有反覆回饋」不能同時成立；連一個 pass/fail bit 都是資訊。可實作的解法不是假裝零洩漏，而是公開規格、雙測試池、隔離裁定域、固定低頻寬回饋、查詢額度，以及「揭露即燒掉」。

---

## 1. 從生命週期物件重新切層

### 1.1 什麼才有資格叫一層

【推論】「有自己的 lifecycle」是必要條件，不是充分條件。否則 CriterionVersion、BudgetReservation、Lease、OutboxIntent 全都能各自升格，系統最後會變成把每張有 status 欄位的表都叫一層。

【推論】本輪採用四個合取條件：

1. 【推論】它擁有穩定身分與獨立生命週期：有建立、進展、封閉終態，且終態不是呼叫端臨時計算出來的。
2. 【推論】它擁有一組不可下推的保證：拿掉它，下層即使完全正確也無法補回那些保證。
3. 【推論】它透過窄且可替換的契約，調用或組合下一層的多個生命週期；只被「附帶查詢」不算。
4. 【推論】它對自己的權威狀態負責：崩潰後知道從哪裡恢復、誰可寫、何時永遠不再重啟。

【推論】這四條是在判斷「垂直組合層」。安全域、儲存元件、傳輸元件仍可能極其重要，但重要不等於位於同一條組合軸上。

### 1.2 問題裡真正出現的生命週期物件

| 生命週期物件 | 自己要回答的問題 | 是否成為垂直層 |
|---|---|---|
| 一次受限執行 | 誰啟動、外部上限是多少、如何停止、是哪一種終態 | 【推論】是；它是所有後端共同的最小可信封套。 |
| 一個目標的追求 | 何時再試、用哪版判準、何時成立或耗盡 | 【推論】是；單次執行成功不能回答目標是否成立。 |
| 一件持久工作／工作集合 | 誰可領取、依賴何時滿足、崩潰後何時重派、何時封存 | 【推論】是；它組合多個目標追求並負責跨程序推進。 |
| 判準版本與裁定 | 哪版有效、是否洩漏、結果是否可信 | 【推論】不是垂直層，但必須是獨立信任域；它不以反覆調用下層生命週期為主要職責。 |
| 預算保留與核銷 | 額度何時保留、結算、釋放或拒絕 | 【推論】不是垂直層；它是每個花費點都要經過的控制面。 |
| 租約 | 誰暫時有權寫、何時過期、舊持有者如何被 fencing | 【推論】不是垂直層；它是持久協調內的權限物件。 |
| 外部效果意圖 | 何時入 outbox、派送幾次、何時死信 | 【推論】不是同一條垂直層；它是工作協調之後的交付子系統。 |
| 維護提案 | 誰發現、誰驗證、誰批准、是否變成工作 | 【推論】不是新層；它是一種工作來源與工作型別。 |

### 1.3 三個垂直層

#### 第一層：執行封套（Execution Envelope）

【推論】它的物件是 Execution：一次對不可靠執行者的受限呼叫，而不是「一個 agent」。後端只是能力適配器；Claude Agent SDK、CLI agent、本地模型、純函式重播器都必須落在同一個 Start／Observe／Stop 契約下。

【推論】最低限度的權威輸入包括不可由執行者改寫的 deadline、回合額度、金額／token 額度、允許能力、輸入快照與 execution id。外部監督者持有時鐘、計數器、子程序或遠端取消權；把倒數器放進 prompt 等於沒有上限。

【推論】終態至少要區分 SUCCEEDED、FAILED、TIMED_OUT、TURN_LIMIT、SPEND_LIMIT、CANCELLED、BACKEND_ERROR、SUPERVISOR_ERROR。SUCCEEDED 只表示這次封套正常產出，不表示目標被接受。

【推論】本層不可決定「工作完成」；它只能產出有 provenance 的候選結果、實際用量與封套終態。否則執行者又拿回驗收權。

#### 第二層：目標追求（Goal Pursuit）

【推論】它的物件是 Pursuit：一個目標、固定或明確升版的判準版本、總預算，以及零到多次 Execution。它決定下一次嘗試的輸入，但無權更改隱藏判準內容。

【推論】終態至少要區分 SATISFIED、ATTEMPT_LIMIT、DEADLINE_EXHAUSTED、SPEND_EXHAUSTED、CANCELLED、CRITERION_ERROR、POLICY_STOP。把所有非成功都壓成 failed，會使「東西做錯」與「裁判壞掉」不可核銷也不可恢復。

【推論】「保證一定會停」必須來自外部可單調耗盡的總額度，而不是「看起來沒有進展」。每次進入 Execution 前先原子保留最壞成本或一個可證明有限的配額；沒有剩餘額度就直接進封閉終態。

【推論】本層組合第一層，因為同一 Pursuit 可替換後端、換提示策略、重播既有結果，卻不改變「何時算成立」的權威。

#### 第三層：持久工作協調（Durable Work Coordination）

【推論】它的物件是 WorkItem 或 WorkflowInstance：跨程序、跨崩潰存在的工作。最小形態可以只是待辦佇列；只有需求真的出現依賴、fan-out、join 或補償時才需要 DAG。因此「圖」是此層可能採用的表示，不是此層存在的理由。

【推論】終態至少要區分 COMPLETED、FAILED_FINAL、QUARANTINED、CANCELLED；非終態可包含 READY、LEASED、RUNNING、WAITING、RETRY_DUE。租約必須有到期時間與遞增 fencing token，否則已失去租約的程序仍可能晚到覆寫。

【推論】SIGKILL 後重建不能依賴 worker 記憶、程序內 Observable、主 agent 對話或未落盤 callback。可重建集合必須由持久狀態純查詢得到，例如「非終態且無有效租約／計時已到」。

【推論】此層組合零到多個 Pursuit，也持有 outbox 意圖與依賴狀態；但外部效果的交付仍遵守題目已裁定的 at-least-once 或 at-most-once，不得宣稱端到端 exactly-once。

### 1.4 三個橫向控制面

【推論】判準裁定面必須和執行者分開信任域。它可以在邏輯上服務 Pursuit，部署上卻不能和執行者共用可讀檔案、同一 interpreter 或可回看的 raw stack；否則「第二層擁有判準」會被誤實作成「執行者同程序可 introspect 判準」。

【推論】預算面要定義共同核銷貨幣與保留協議，而不是要求所有後端原生回報相同欄位。可採 money_minor_units、wall_ms、turns、backend_units 的多維上限；只有可由外部觀測或供應商帳單核對的量才有權阻止下一次花費。

【推論】效果交付面以 outbox row 為權威，派送器只持租約。目的端有 idempotency key 才可選 at-least-once；若目的端不能去重且重複傷害大，選 at-most-once 並接受遺失窗口。這不是工程缺陷，而是不可跨交易邊界的代價。

### 1.5 與《邊界裁定》的比較：哪裡一樣，哪裡誰錯

【查證】[《邊界裁定》](../設計/五學科/邊界裁定.md)把獨立生命週期、單一寫入者、花費點與終態當成邊界工具，最後保留 H／L／G，並把 agentic 與 multi-agent 分別下沉為執行形態及圖的 profile。

【推論】三層數量相同，而且「agentic 不另成層、multi-agent 不另成層」的結論是研究文件較對：換成 CLI、本地模型或重播器不應改變上層生命週期；一個工作有一位或多位執行者也只是協調策略。

【推論】名稱與第三層的本體則是本文較對。「Loop」描述控制流手法，不是被管理的東西；「Graph」描述資料結構，卻連最小需求「多件互不相依的工作可跨崩潰推進」都不必用圖。用 Pursuit 與 Durable Work 命名，才不會先替實作下注。

【推論】《邊界裁定》只用「有獨立 lifecycle」仍不夠。BudgetReservation 和 OutboxIntent 明明都有 lifecycle，卻不應和 Execution／Pursuit／Work 並列成垂直組合層。本文加上的「不可下推保證＋組合下層＋權威恢復」能排除這種層數膨脹。

【推論】判準裁定雖不升為第四個垂直層，卻必須升為獨立安全邊界。若研究中的 L 同時拿著隱藏判準又執行候選程式，邏輯分層正確也會在程序邊界上全毀。

【查證】[graph.json](../設計/五學科/graph.json)的核心不變量把外部 effects 寫成等同 exactly-once，內文另又承認資料庫與外部世界只能兩階段交付；題目性質 7 已明確裁掉這個幻想。

【推論】因此本輪不是照抄 H／L／G：我在讀結論前獨立得到三個生命週期物件；研究只在事後提供了反例與比較詞彙。碰巧相同的是數量，不相同的是資格判準、第三層本體，以及判準安全域的地位。

【需裁定】是否要求第三層第一版就支援一般 DAG：

- 【需裁定】選項 A：只做持久佇列＋顯式父子關係。代價是複雜 join／補償要稍後加入；好處是每個新增狀態都由真需求拉出來。若首批使用情境已需要跨分支 join、拓撲取消或動態 fan-out，判斷會反過來。
- 【需裁定】選項 B：一開始做一般 DAG。代價是循環檢查、拓撲狀態、部分失敗語義與遷移成本立刻進核心。若已經有至少兩種無法以父子工作表達的工作流，這筆成本才合理。

---

## 2. 錨定審計：四份文件逐段拆

### 2.0 判讀符號

【推論】下表用三種罪名，不用委婉語：

- 【推論】「前情依賴」：沒有舊系統知識就不知道名詞指誰、為何存在或句子在反駁什麼。
- 【推論】「修舊」：決定的主要論證是修補既有缺陷，沒有從本題性質重新推導。
- 【推論】「可刪前提」：作者把某個舊概念當作新世界必有，但第一性需求根本不要求它存在。

### 2.1 《重做規矩.md》

| 段落 | 語言破綻 | 判決 |
|---|---|---|
| [L1–4](./重做規矩.md) | 「重做不是修改」「舊元件→新元件」 | 【推論】前兩句可獨立理解，但整份文件的核心目標是阻止遷移式寫作，不是描述新系統的任何行為保證。它是工作方法，不是架構。 |
| L6–21 | 禁止「現況、仍然、改成、不再、已經有、原本的、那條路、它現在會」 | 【推論】這段抓到真正的 delta 語病，應保留成審稿 lint；但它不能替代需求推導。禁止某些字不會自動消除概念錨定。 |
| L23–37 | 「不得沿用舊名字」，接著完整列出偏離棘輪、收爐帳、待實作集合、保護清單、竄改稽核、三權分立及其舊責任 | 【推論】這段自己違反自己的 outsider test。陌生讀者完全不知道這些名字的外延，熟悉舊系統者則得到一張一對一翻譯表。這不是去錨定，是替錨下索引。整張表應移出新設計文件。 |
| L39–45 | BQ1／BQ2／BQ3、十九期、舊契約、舊檔案 | 【推論】純前情依賴，且沒有任何新需求可由這些代號推出。這一段只屬於遷移清冊；放在新設計規矩裡就是污染源。 |
| L47–52 | 「nova 曾經怎麼做」「舊測試」「舊 cohort」「證明不可重播」 | 【推論】純修舊。若「不可重播」是一般風險，應改寫成新要求：每個裁定輸入須有不可變快照與版本；不需要講誰以前失敗過。 |
| L54–59 | outsider test 與唯一例外 | 【推論】測試本身合理，但「唯一例外」又允許文件透過附錄攜帶舊概念。真正標準應是：刪除所有舊名後，需求、狀態與不變量仍完整；做不到就不是新設計。 |

【推論】不留情的結論：這份規矩本身未通過它自己的規矩。它一面禁止翻譯舊詞，一面保存舊詞、舊期別、舊契約和舊測試的全套索引。最乾淨的處置是把它降格成「重做寫作 lint」，新架構只保留一條：所有名詞須能由生命週期物件或可執行性質獨立定義。

【推論】其中被當成前提但新設計未必需要的概念包括：

- 【推論】「偏離棘輪／只保留最好值」只適用有可比較單調分數的問題；布林契約、互相衝突的品質維度、或規格升版都不保證存在全序。
- 【推論】「待實作集合」是某種修復流程的資料結構，不是可信工程的一般本體；新系統只需要 WorkItem 能表達目標和終態。
- 【推論】「三權分立」是安全目的的比喻，不是三個固定模組。真正需求是提案者、執行者、裁定者的權限不可讓同一不可信主體串通取得；部署可以是二、三或更多信任域。

### 2.2 《主動性.md》

| 段落 | 語言破綻 | 判決 |
|---|---|---|
| [L1–9](./主動性.md) | 「主動性有四層」：自動推進、自主喚醒、主動送達、自主發現 | 【推論】這不是四層，是四項 capability。沒有一項在文中被定義出穩定 id、封閉終態與組合下一層的契約。把 feature 排成階梯不會變成 architecture。 |
| L13–30 | router、題目→派實作、候選→裁定、收官、下一代、outbox | 【推論】「router」與那些轉移沒有自足資料模型，是前情依賴。Outbox 也不是自動推進的必備物；只有狀態提交與外部派送跨交易時才需要。若下一步只是同庫狀態轉移，一個交易即可。 |
| L33–45 | 「長駐程序＋持久計時器＋租約」 | 【推論】把長駐程序當必然是可刪前提。外部 scheduler、serverless alarm、cron 加輪詢同樣能喚醒持久狀態；需求只要求 timer intent 持久化與重複喚醒安全。 |
| L49–73 | 「main agent」「QC 控制端收件匣」「READY credit」「零爐＝空閒」「任意 harness」 | 【推論】這整段沒有舊拓撲就讀不懂，是最重的錨。它不是「主動送達」的一般設計，而是某個既有 UI／控制端的接線說明。新設計只需 DeliveryEndpoint 契約、idempotency key、回執語義與失敗策略。 |
| L49–73 | 「確認動作收到後 ACK」 | 【推論】仍偷渡原子性幻想。外部動作與 ACK 不在同一交易：先動作後 ACK 是 at-least-once；先 ACK 後動作是 at-most-once。文件必須逐 endpoint 選一個，不能用「收到」把窗口抹掉。 |
| L77–96 | 「自主發現＝判準生成」「知道什麼叫好，等於知道下一步」 | 【推論】這個等號錯。異常偵測可先提出「疑似退化」而尚未有完整驗收判準；反過來，已有判準也不代表知道哪個修法值得做。Goal discovery、criterion authoring、proposal validation 是三個不同責任。 |
| L99–120 | 恆真格、零呼叫端原語、未接線能力、單調度量、停滯的爐 | 【推論】前四個大多是舊系統特定 lint 名詞；「停滯的爐」尤其無前情即失義。可泛化的只有：系統要對已宣告的不變量跑外部探針、偵測無進展並產生不受信任的 MaintenanceProposal。 |
| L99–120 | 「系統健康有客觀答案」 | 【推論】過度宣稱。資料損壞、死租約可客觀判定；backlog 太舊、進步太慢、成本太高都需要政策門檻。門檻若沒版本化，所謂客觀只是作者偏好藏在常數裡。 |
| L122–139 | 只產提案、orphan-9、dead letter、READY | 【推論】「只產提案」從性質 6 可推出，應保留；orphan-9 與 READY 是前情依賴，dead letter 則是一般交付概念。三者混寫讓通用原則替舊實作背書。 |
| L143–159 | router→QC→喚醒、探索器、現況差距、產業常態 | 【推論】這是落地順序與舊系統 gap list，不是從零設計。尤其「先接哪個現成元件」會直接把新邊界扭成舊檔案的形狀，應整段移出架構文件。 |

【推論】不留情的結論：這份文件最嚴重的錯不是用了舊名字，而是把「目前接得上的四種能力」誤稱為「四層」，再用 QC、READY、零爐、router 的接線順序替這個分類作證。它寫的是產品 backlog，不是 ontology。

【推論】AST 找「零呼叫端」只能是特定語言與靜態 dispatch 下的 lint；reflection、plugin registry、設定式路由、FFI 都能讓它誤報。若把它升成自我維護的普遍判準，會把實作便利誤當真理。

【推論】自我維護的最小可信形態應是：外部或隔離的 observer 產生帶證據的提案；提案進入普通 WorkItem；其修改仍經隱藏判準裁定。讓被觀測系統自己宣稱「我健康」只是把驗收權還給被驗收者。

### 2.3 《選型原則.md》

| 段落 | 語言破綻 | 判決 |
|---|---|---|
| [L1–24](./選型原則.md) | 三個過濾器：「綁定不變量」「狀態與持久不變量無關」「失敗須交出 stack」 | 【推論】方向是降低依賴，但第一條過度僵硬：型別／parser／driver 可以靠縮小錯誤面、改善安全或效能而有價值，不必單獨承載一條不變量。第二條把「非權威的暫存狀態」也疑似判死刑；真正禁的是只存在記憶體且恢復所必需的狀態。第三條應要求結構化失敗契約，不是 raw stack；raw stack 會洩漏秘密，跨程序服務也未必能提供。 |
| L28–40 | RxPy「所有狀態在記憶體」「第二套控制流等於兩本帳」 | 【推論】這是稻草人。Observable 可以讀持久來源；真正問題是不能讓它成為權威狀態。兩套控制流增加認知成本，但不等於兩本持久真相，這是把程式結構和資料權威混為一談。拒絕 RxPy 可以，這個證明不行。 |
| L42–51 | 「已經用 anyio／asyncio」「consumer 是另一個 process」 | 【推論】明確前情依賴與修舊。從零應先問是否需要程序內 reactive composition；「已有另一套」只能出現在遷移決策，不能當新架構公理。 |
| L55–68 | SQLite、Hypothesis、mutation、Pydantic、tenacity、Celery／RQ、OpenTelemetry 的即決表 | 【推論】Hypothesis／mutation 可直接服務「測試真的會 fail」；其餘仍需按拓撲裁定。對 tenacity 的全面拒絕不成立：若 retry 只包單次 transport、共用外部預算且不持有 domain state，它不會自動創造第二套真相。Celery／RQ 的 broker state 也不必是 domain truth；它可只是可丟失喚醒。可能不值得用，但文件給錯了理由。 |
| L71–86 | 「sol 第三輪修正」、H／L／G、A 與 M 的安置、外部副作用修正 | 【推論】純粹是前一輪辯論的 delta。沒有那些輪次就不知道在修誰；而且它把尚需論證的 H／L／G 當成候選庫篩選的固定座標。整段應逐出「選型原則」。 |
| L87–108 | SQLite 3.50.4、crash 實驗、損毀抽樣、pytest 隔離 | 【推論】這是一次局部實驗紀錄，不是通用選型原則。它只覆蓋某個版本、某種 crash 點與某個檔案系統；沒有 disk-full、長讀交易、checkpoint、備份還原、半派送 outbox 等失敗面，不能替整個引擎背書。 |
| L109–127 | 探索／取得、真正 dispatch、AST manifest、各層測試數、kill-grid 5.63% | 【推論】沒有既有 repo 完全讀不懂，而且全是舊系統盤點。這是最明顯的污染證據：文件標題叫「選型原則」，內容卻在數舊程式的呼叫點和測試比例。應整段刪離新設計。 |
| L130–135 | 「sol 第四輪」「sub-agent 訊息」「未讀」 | 【推論】這是會議 TODO，不是設計。保留它只會讓下一位作者繼續沿著前一輪的問題清單走，而不是重新驗證問題是否存在。 |

【推論】不留情的結論：L71 之後不是「有一點錨定」，而是舊系統驗屍報告塞錯目錄。把它留在選型文件中，任何後來者都會被迫把「現有 dispatch、現有版本、現有測試比例」誤認成新架構限制。

【推論】可救回的選型原則只有三條：權威狀態可從持久記錄重建；依賴失敗必須轉成系統自己的型別化結果；每個引擎／框架都要接受相同的 crash、併發、預算與負控契約。是否「方便」可以是次要分數，不能冒充不變量。

### 2.4 《儲存選型.md》

| 段落 | 語言破綻 | 判決 |
|---|---|---|
| [L1–20](./儲存選型.md) | 一次 attempt 幾分鐘、16 個並行、每 attempt 一個交易、低於 SQLite 三個數量級 | 【推論】這不是需求推導，而是先把寫入單位定義得足夠粗，再宣布吞吐無關。題目明說回合、花費、跨崩潰、租約、outbox；這些都會在 attempt 內產生寫入。純函式重播器甚至可讓 attempt 以毫秒計，直接推翻「幾分鐘」前提。 |
| L25–38 | 「六個不變量」、CAS、claim、global constraint、lease、notification、test isolation | 【推論】「六個」沒有在本文件自足定義，是前情依賴；比較軸本身多數合理，但漏了備份還原、磁碟滿、schema migration、版本升級、長讀交易、跨主機與觀測成本的明確權重。 |
| L43–59 | SQLite single-writer、WAL-reset 風險、因此不開多連線 WAL | 【推論】「多連線 WAL」不是可操作的拓撲描述。WAL 是資料庫檔的持久模式，不是某條連線的開關；真正決策是單一 owner process／單一 connection、或多程序直接連線，再加讀交易長度與 checkpoint 策略。 |
| L60–84 | PostgreSQL 的 xmin CAS、SKIP LOCKED、advisory lock＝lease、NOTIFY、測試與維運成本 | 【推論】比較被寫歪了。xmin 不宜充當長期應用版本；advisory lock 沒有 TTL 與 fencing，不是 lease；NOTIFY 不是持久佇列。反過來，測試也不必每例起一個 server。這些錯誤讓 PostgreSQL 看起來既過重又神奇地自帶所有語義。 |
| L85–95 | MySQL「沒有更好」、DuckDB 適合小而高頻、libSQL「現在沒有 HA 需求」 | 【推論】三個都是結論先行。MySQL 沒有逐軸比較；文件前面才說低頻，這裡又用高頻評 DuckDB；「現在沒有」是最標準的 delta 語句。可以淘汰，但必須用本題的交易、鎖、崩潰與部署需求淘汰。 |
| L98–118 | 「SQLite 勝出」「我們的 cadence」「測試隔離是壓倒性差異」 | 【推論】這段把作者方便當決定性架構理由。測試體驗很重要，但若每個測試用自己的 SQLite 檔，剛好會掩蓋 production 最重要的共享鎖、claim、lease、CAS 與 crash 競態。快而不相似的測試不是信任代理人。 |
| L120–140 | 第二台機器、每秒 100 次寫入、跨機一致性；port／adapter | 【推論】翻轉條件太晚且太窄：長讀造成 writer starvation、備份窗口、磁碟滿、檔案鎖語義、單 writer owner 成為瓶頸，都可在 100 writes/s 以前翻轉。Port／adapter 是合理隔離，但 SQL 語義差異不會因介面叫 port 就消失。 |
| L144–153 | 「下一步」「先用 SQLite」「再回答是否開 WAL」 | 【推論】至少承認需要量測，但順序仍倒置：先寫 SQLite adapter 會讓 schema、claim 與 transaction boundary 自然貼住 SQLite，再把這個既成形狀當量測結果。應先定 workload envelope 與故障試驗，再寫最薄的兩個可丟棄 spike。 |

【推論】不留情的結論：這份文件沒有比較「符合題目性質的持久狀態拓撲」，它比較的是「SQLite 的最佳故事」和「PostgreSQL 的最麻煩故事」。SQLite 可能仍贏，但目前勝出的只是敘事。

---

## 3. 攻擊儲存選型

### 3.1 「低三個數量級」漏算了什麼

【推論】若每個 attempt 只在結束時寫一次，題目中的硬預算、崩潰恢復、租約與 outbox 就沒有可執行載體。更接近下界的寫入模型是：

    每次 attempt 寫入量 ≥
      啟動／終態
      ＋ 每次付費呼叫的 reserve／settle
      ＋ 每個必須可重播的回合或工具事件
      ＋ ceil(執行時間／租約續租週期)
      ＋ 每個判準階段的開始／結果
      ＋ 每個外部效果的 enqueue／claim／attempt／delivered
      ＋ retry、timer、quarantine 與審批轉移

【推論】漏掉的具體來源至少有：

- 【推論】模型、工具、子執行者每次花費前的預算保留，以及帳單到達後的結算／校正。
- 【推論】Execution、Pursuit、Work 三層各自的狀態轉移與終態；不能只記最外層一筆。
- 【推論】claim、lease heartbeat、續租、過期回收與 fencing token；並行愈高，這些不是常數一筆。
- 【推論】outbox 建立、領取、派送嘗試、回執、重試、死信；一次工作可有多個效果。
- 【推論】持久 timer、審批、依賴解除、fan-out／join、判準版本與 artifact provenance。
- 【推論】自我維護掃描、異常提案、信任標籤、backfill、schema migration 及核銷修正。
- 【推論】測試本身：property-based、mutation、kill-point matrix 和純函式重播可能比線上工作快幾個數量級，正是最容易撞出鎖與交易錯誤的負載。

【推論】平均每秒寫入仍是錯的主要指標。SIGKILL 後大量 lease 同時過期、排程 tick 同時釋放 timer、供應商用量批次回補、outbox 目的端恢復，都會造成 burst；要量的是 production 拓撲下的 p95／p99 transaction latency、SQLITE_BUSY 比率、最長讀鎖與恢復時間。

【查證】[原文件 L8–19](./儲存選型.md)沒有把「約 1000 durable commits/s」綁到可重現的硬體、檔案系統、同步等級、交易大小、連線拓撲或 benchmark script。

【推論】因此即使數字碰巧正確，也不能外推成三個數量級的安全餘裕。

### 3.2 不開 WAL 的論證目前站不住

【查證】SQLite 官方說明指出：rollback mode 下只能有一個 writer，且 writer 在提交時可能因其他連線仍持 read transaction 而收到 SQLITE_BUSY；WAL 的主要收益正是 readers 與 writer 可同時進行，但仍只有一個 writer。[Transactions](https://sqlite.org/lang_transaction.html)；[Isolation](https://www.sqlite.org/isolation.html)；[WAL](https://www.sqlite.org/wal.html)。

【推論】所以問題不是「寫入率遠低於峰值」，而是「是否有長讀交易與多程序直連」。一個匯出報表、診斷查詢或掃描型維護工作就可能讓低頻 writer 卡住；平均 0.1 writes/s 也救不了 deadline 已到的那一次提交。

【查證】WAL mode 是同一資料庫檔的持久屬性，重新開啟資料庫後仍保持，所有連線都會面對同一 journal mode。[SQLite WAL persistence](https://www.sqlite.org/wal.html#persistence_of_wal_mode)。

【推論】因此「不啟用多連線 WAL」語義不完整。可實作的選項其實是：

- 【推論】單一 state-owner process＋單一 connection＋rollback journal，所有 worker 用高階 command 經 IPC 請求；或
- 【推論】多程序／多 connection 直連＋rollback journal，接受並正確重試 BUSY；或
- 【推論】多 connection＋WAL，明確管理 checkpoint、長 reader、WAL／SHM 檔與版本。

【查證】SQLite 目前官方文件記載的 WAL-reset 罕見損毀問題受影響範圍是 3.7.0 至 3.51.2，修正在 3.51.3，另有 3.44.6 與 3.50.7 backport。[SQLite WAL bug notice](https://www.sqlite.org/wal.html)。

【推論】因此把 3.50.4 的風險永久化成「不用 WAL」已過時；正確處置是固定到已修版本，然後按連線拓撲重新量測。

【需裁定】journal mode 與連線拓撲：

- 【需裁定】選項 A：單一 owner process／connection＋rollback journal。代價是多一個必須監督的 IPC 服務，所有 command 受同一排隊點影響；好處是寫入權威最簡單。若有長讀、worker 必須直接做查詢、或 owner 無法承受批次 burst，判斷轉向 B。
- 【需裁定】選項 B：固定在已修版本的 SQLite＋WAL＋受限 connection pool。代價是 checkpoint、長 reader、WAL／SHM 備份與版本管理；好處是讀寫並行。若部署可保證全部狀態操作經單一 owner 且讀交易極短，判斷轉回 A。
- 【需裁定】選項 C：多程序直接連 SQLite rollback mode。代價是 BUSY handling 和讀寫互阻成為每個呼叫端的共同責任；除非量測證明競態極低且所有交易極短，否則這是三者中最差的默認值。

### 3.3 「測試隔離」不是壓倒性架構理由

【推論】測試速度與隔離是正當成本，但不能覆蓋 production 語義。每個 test worker 一個暫存 SQLite 檔，會消除恰好需要驗證的共享 claim、lost update、lease expiry、long reader、checkpoint 與 crash recovery 競態。

【推論】正確做法是兩層測試，而不是拿其中一層替引擎投票：

- 【推論】大量快速模型／property 測試：每例獨立資料庫或純函式 reference model，追求可縮減與高覆蓋。
- 【推論】較少但不可省的 production-topology 測試：和實際 journal mode、連線數、owner process、同步等級一致；在交易邊界注入 SIGKILL、BUSY、disk-full、重複派送與時鐘推進。

【查證】PostgreSQL 可以在一個測試 server 上建立多個隔離 database，並由 template database 複製初始狀態；「使用 PostgreSQL 就必須每個測試啟一台 server」不是事實。[CREATE DATABASE](https://www.postgresql.org/docs/current/sql-createdatabase.html)。

【推論】PostgreSQL 測試仍比單檔 SQLite 重：需要 server lifecycle、連線清理、database 建立／刪除與 CI image。這是合理扣分，但只是總成本一欄，不能壓倒更高權重的故障與部署語義。

【查證】SQLite 也不是零維運。官方列出把資料庫檔與 rollback journal／WAL 分離、交易中直接複製檔案、錯誤檔案鎖與磁碟同步等損毀途徑，並要求使用正確的 backup 機制。[How To Corrupt An SQLite Database File](https://www.sqlite.org/howtocorrupt.html)。

【推論】因此測試隔離的裁定原則應是：先選能滿足 production failure model 的拓撲，再要求測試 harness 低成本重建它；不能反過來選最容易造假的測試環境。

### 3.4 PostgreSQL 比較中的三個技術錯位

【查證】xmin 是 PostgreSQL 內部 system column，表示插入該 row version 的 transaction identity；transaction ID 會 wraparound。[System Columns](https://www.postgresql.org/docs/current/ddl-system-columns.html)。

【推論】把 xmin 當應用層永久 CAS 版本會綁死內部語義；應用應使用明確遞增 version 或 fencing_token。

【查證】session-level advisory lock 持有到顯式釋放或 session 結束，transaction-level advisory lock 持有到交易結束；它沒有 TTL、renewal 或 fencing epoch。[Advisory Lock Functions](https://www.postgresql.org/docs/current/functions-admin.html#FUNCTIONS-ADVISORY-LOCKS)；[Explicit Locking](https://www.postgresql.org/docs/current/explicit-locking.html)。

【推論】所以 advisory lock 不是 lease。活著但卡死的 session 可一直持鎖；即使連線斷掉釋放鎖，也沒有阻止舊 worker 的晚到外部效果。正確 lease 仍需 expires_at＋遞增 fencing token＋條件更新。

【查證】SKIP LOCKED 提供不一致視圖，官方明示它適合 queue-like table 的多 consumer，而不適合一般一致性讀取。[SELECT locking clause](https://www.postgresql.org/docs/current/sql-select.html)。

【推論】它能簡化 claim，不會替代 global constraint、租約或終態機。原文件把一個 SQL primitive 寫得太像完整協調協議。

【查證】NOTIFY 在交易提交後才送達，且只是一種通知機制，不是持久工作佇列。[NOTIFY](https://www.postgresql.org/docs/current/sql-notify.html)。

【推論】可靠設計仍以表中的 work／outbox 為真相，NOTIFY 只作低延遲喚醒；listener 重連後必須重掃持久狀態。

### 3.5 沒被認真比較的引擎與形態

| 選項 | 真正優勢 | 真正代價 | 何時值得反轉 |
|---|---|---|---|
| SQLite＋專用 state owner | 【推論】單 writer 從「鎖限制」變成明確所有權；可在一台機器上把高階 command 原子化。SQLite 官方也把 app server 序列化請求與資料分片列為適用形態。[Appropriate Uses](https://www.sqlite.org/whentouse.html) | 【推論】要自建 IPC、監督、backpressure、備份與讀模型；owner 是可恢復的單點。 | 【需裁定】單機、資料量小、寫 command 可排隊時優先；只要跨主機寫入或長分析讀成常態，就反轉。 |
| PostgreSQL | 【推論】成熟 client/server 併發、transactional claim、跨主機 client、備份與管理工具；較貼近多程序共同存取。 | 【推論】服務生命週期、升級、連線池、CI 與本機開發成本更高；仍要自己做 lease、outbox、狀態機。 | 【需裁定】一旦狀態 owner 不再單機、需要多 writer／HA／遠端存取，預設應反轉到它；若產品明確是單機工具，則不必付這筆稅。 |
| SQLite 分片（每 workspace／tenant／work domain 一檔） | 【推論】把單 writer 衝突局部化，備份／搬移單位清楚。 | 【推論】跨分片交易、全域預算與查詢變難；檔案數、migration、清理與開檔上限成新問題。 | 【需裁定】工作域天然獨立且全域約束極少時成立；若有全域花費上限或跨工作依賴，判斷反轉。 |
| FoundationDB | 【查證】提供分散式 ordered key-value 與嚴格 serializable transaction；但交易有約五秒限制，且需要自己建立資料模型與索引。[Developer Guide](https://apple.github.io/foundationdb/developer-guide.html)；[Known Limitations](https://apple.github.io/foundationdb/known-limitations.html) | 【推論】維運、資料建模、查詢與人才成本遠超本題目前已知規模。 | 【需裁定】只有當跨機強交易與水平擴張成硬需求，而 PostgreSQL 的單 primary 模型已被量測否決，才值得。 |
| Actor-per-work-item／Durable Object 類形態 | 【查證】Cloudflare Durable Objects 提供單一 object 的序列化執行、transactional storage 與 alarm；SQLite storage 仍是 object-local。[SQLite-backed Durable Objects](https://developers.cloudflare.com/durable-objects/api/sqlite-storage-api/) | 【推論】把 owner lifecycle 外包很契合工作物件，但交易只在 object 內，跨 object 全域預算與 outbox 仍難；另有供應商與 runtime 鎖定。 | 【需裁定】若產品本來就部署在該 edge runtime 且工作可天然分區，判斷反轉；一般本地 harness 不應為此遷移平台。 |
| Durable workflow runtime（例如 Temporal） | 【查證】Temporal 的定位是把 workflow execution 持久化，使程序在 crash 後繼續。[Temporal documentation](https://docs.temporal.io/) | 【推論】它可承接 timer、retry 與 workflow history，卻不能替代隱藏判準、成本真相、目的端 idempotency；還要付 deterministic workflow、版本升級與服務成本。 | 【需裁定】若團隊已營運該平台，或長時 workflow／timer 的複雜度超過 domain logic，才可能勝過自建第三層。 |
| LMDB／MDBX／RocksDB 類嵌入式 KV | 【推論】可改變寫入與讀取特性，但會失去現成 SQL constraint、migration、診斷與 queue query；本題仍須自行重建 CAS、lease、outbox。 | 【推論】除非 profile 顯示 SQLite 的 B-tree／SQL 層是瓶頸，否則只是用更多自製機制換掉熟悉風險。 | 【需裁定】只有可重現 benchmark 證明 SQL 引擎本身而非鎖拓撲是瓶頸時反轉。 |

### 3.6 本輪的儲存結論

【推論】SQLite 是「尚未被淘汰的候選」，不是「已勝出」。以目前題目唯一明確的部署資訊，最可辯護的暫定形態是單機 SQLite＋專用 state owner；journal mode 要由固定版本下的長讀與 crash 實驗裁定，不能預先禁止 WAL。

【需裁定】正式選型必須先補 workload envelope，至少給出：最大同時 Pursuit、每次付費呼叫數、事件持久粒度、lease 週期、最長讀交易、outbox fan-out、允許恢復時間、是否跨主機、資料保留量、備份 RPO／RTO。

- 【需裁定】選項 A：上述 envelope 明確是單機、短讀、低 burst。代價是未來跨機要換 adapter 與資料；先採 SQLite state owner。若任一跨機 writer、長讀或 HA 成硬需求，結論反轉。
- 【需裁定】選項 B：envelope 未知但產品近期就需多程序遠端連線。代價是先付 PostgreSQL 維運與測試成本；換來少一次高風險資料層遷移。若後來證明永遠是單機 CLI，結論反轉。
- 【需裁定】選項 C：先做兩個不超過一週的 disposable spike，在完全相同的狀態機與 kill matrix 下比較 SQLite owner 和 PostgreSQL。代價是短期重工；若時程連這個風險試驗都容不下，就必須明講選擇是賭注而不是查證。

---

## 4. 性質 4：隱藏判準與有用回饋的衝突

### 4.1 先承認不可能三角

【推論】若「判準內容不得被執行者讀取」被解釋成「執行者從任何通道都得不到和判準相關的資訊」，那它與反覆回饋在資訊論上直接矛盾。pass／fail 本身就是一個 bit；允許適應式重試，執行者就能把系統當 oracle 查詢。

【推論】還有一個常被漏掉的更硬限制：待測程式若要處理隱藏輸入，執行中的程式必然暫時看見該輸入。一般軟體無法同時「看不到輸入」又「依輸入計算」。可合理保證的是：隱藏測試原始碼、期望值與完整案例不進入 LLM／CLI agent 的下一輪上下文；候選程式執行時收到的刺激不能經網路、持久檔案、raw log、回傳值或 timing 被帶回執行者。

【推論】若威脅模型連「候選程式在 RAM 內暫時看到輸入」都不允許，普通 sandbox 無解，只剩受信任執行環境、特殊密碼學或把待測界面限制到可安全計算的極小 DSL；這會把通用軟體工程問題換成另一個問題。

【查證】[loop.json](../設計/五學科/loop.json)已把完整失敗訊息、反例、分級分數與 pass/fail 視為不同梯度／洩漏取捨，並建議公開迭代訊號與保留集混合。

【推論】這支持「回饋是可預算的資訊通道」，不支持「做字串遮罩就等於不洩漏」。

【查證】SpecBench 報告可見測試被優化後，held-out 規格仍存在明顯落差。[SpecBench](https://arxiv.org/abs/2605.21384)。

【推論】這說明只靠同一組可見測試會把通過測試和滿足規格混為一談。

### 4.2 先把「規格」和「秘密案例」分開

【推論】正確行為的公開契約必須公開。若「輸入為空時應回傳空集合」本身是需求，就不應把空集合藏在 assertion repr 裡逼執行者猜；那不是防作弊，是未給規格。

【推論】可以隱藏的是：

- 【推論】測試原始碼、檔名、行號、seed、具體輸入、具體期望值與判定實作。
- 【推論】哪些邊界案例在本輪被抽到、保留集的組成、mutation 與 metamorphic relation 的私有實例。
- 【推論】原始 stdout／stderr、assert diff、stack trace、snapshot、coverage path 與任何能定位秘密資料的長度／時間差。

【推論】不能隱藏的是：

- 【推論】公開 RequirementClause 的語義、合法輸入空間、資源限制與錯誤模型。
- 【推論】執行者被允許修改的 artifact、公開 build／type／lint 規則，以及回饋 schema。
- 【推論】哪些終態可能出現、每輪最多洩漏哪類訊號、查詢與總預算如何耗盡。

### 4.3 可實作架構：雙測試池＋隔離裁定域＋洩漏閘門

【推論】最小資料流應是：

    Executor  ──候選 artifact digest──>  Sealed Evaluator
       ^                                      |
       |                                      v
       └──固定 schema、限額回饋──  Feedback Gateway
                                              |
                                     raw evidence 留在秘密域

【推論】四個角色的責任如下：

1. 【推論】Guidance Suite：由公開規格導出，可讓執行者直接跑，給完整 compiler／type／公開 assertion 訊息。它提供大部分梯度，但沒有最終驗收權。
2. 【推論】Held-out Adjudication Suite：只有裁定服務可讀，擁有 criterion_version；它對 frozen artifact digest 執行，結果綁定該 digest，不接受執行者上報的「我已通過」。
3. 【推論】Isolated Candidate Sandbox：只掛載候選 artifact 與必要 runtime；不掛載測試檔、期望值或 secret store，禁止 network、ptrace、host process inspection 與持久 workspace 寫入。每次裁定後銷毀。
4. 【推論】Feedback Gateway：唯一能讀 raw test result 的元件；依預先登記的公開 clause mapping 做降維，不能把測試 runner 的字串直接透傳。

【推論】任意 Python／JavaScript 候選都不能和隱藏測試跑在同一 interpreter。候選程式能 inspect stack、module cache、caller source 或 monkey-patch assertion。裁定 driver 應在可信程序，透過窄 RPC／stdin protocol 驅動另一個 sandbox；候選的輸出由 driver 判定後丟棄，不能原樣回給執行者。

【推論】若測試的是只能 in-process 呼叫的 library API，必須改用更強的 process／microVM 隔離，或承認該 interface 無法抵抗惡意候選，只能抵抗「非刻意偷看」的執行者。安全聲明必須寫出這個差別。

### 4.4 回饋型別：不傳 assertion repr

【推論】裁定域內保留完整 Evidence，但對執行者只輸出如下概念型別：

    Feedback
      candidate_digest
      criterion_version
      decision: NOT_MET | CRITERION_ERROR | QUERY_EXHAUSTED
      public_clause_ids: 最多 K 個、固定排序
      stage: BUILD | CONTRACT | BEHAVIOR | RESOURCE
      failure_class: 固定 enum
      actual_shape: NONE | TYPE | LENGTH_BUCKET | RANGE_BUCKET
      disclosure_units_used
      attempts_left

【推論】明確禁止欄位包括 hidden test name／path／line、hidden input、expected literal、assert diff、hidden stack、raw stdout／stderr、coverage、精確耗時與未經白名單的自由文字。candidate_locations 只有在位置完全由公開 artifact 的靜態工具產生時才可回傳。

【推論】CRITERION_ERROR 必須和 NOT_MET 分開。測試 runner crash、秘密 fixture 壞掉、裁定服務超時或 output parser 不認得格式時，不能把 stderr 當梯度，更不能誤判候選失敗；它應進明確的裁判故障終態，且不扣候選的行為失敗分。

【推論】clause id 也會洩漏，因此每輪最多 K 個、固定順序、固定長度，且 clause 本身必須是公開契約。若同一輪回傳全部失敗集合，集合大小與交集就能成為高頻寬 oracle。

### 4.5 「揭露即燒掉」規則

【推論】只要任何 hidden case 的具體 input、expected、diff 或足以重建答案的 counterexample 被回饋，該 case 就從那一刻起失去最終裁定資格，永久轉入 Guidance Suite。不能一面把答案告訴執行者，一面繼續叫它 held-out。

【推論】要維持梯度，裁定者可從同一公開條款生成新的 sibling case、metamorphic instance 或不同私有 seed 補位；若沒有可再生案例，就只能降低回饋粒度，不能假裝秘密仍在。

【推論】最終 SATISFIED 應綁定 candidate_digest、criterion_version、evaluator_version 與 sealed-suite digest，由裁定域寫入權威狀態。任何判準升版都使舊 verdict 只對舊版本有效；不得默默沿用。

### 4.6 洩漏預算與梯度代價

【推論】若每次 hidden 查詢最多有 B 種可觀測回覆，最多允許 R 次，忽略 timing 等側通道時，顯式通道上界是 R × log₂(B) bits。這不是完整安全證明，但至少把「回饋很多／很少」變成可核銷量。

【推論】代價不能誠實地寫成固定「梯度弱 30%」；它依問題空間而變：

- 【推論】build、syntax、type 與公開 contract 錯誤：完整回饋都來自公開資料，梯度幾乎不必削弱。
- 【推論】Guidance Suite 行為錯誤：仍可給完整 diff，梯度也幾乎不變，但只保證公開案例。
- 【推論】Held-out 精確相等錯誤：完整 expected 往往讓下一輪直接答對；只給 pass/fail，若答案有 N 個無序候選，最壞可需 N 次，平均約 N／2 次試探。
- 【推論】若回饋提供「太大／太小」三值方向，對有序 N 個候選可能恢復到約 log₂(N) 次；所以一個看似無害的 range bucket 已是很強 oracle。
- 【推論】只給公開 clause id＋粗 failure class，通常能指出錯的需求面，不能指出反例；它保留修正方向，犧牲局部定位速度。實際成本要以 full-feedback 與 gated-feedback 的相同任務 A/B 測量 attempt 數、wall time、花費與 held-out 通過率。

【推論】真正的安全槓桿不是把 expected 字串換成「***」。候選可透過 repr 變形、長度、例外型別、排序、stack、timing 或刻意回顯輸入重建資訊。必須先隔離 raw evidence，再由封閉 enum 重新產生回饋；字串 regex redaction 只能當最後一道防呆。

### 4.7 必須會轉紅的負控

【推論】以下不是建議清單，而是性質 4 的最小可執行背書；每一條都要有把防護故意移除後會 fail 的負控：

1. 【推論】在 hidden source、input、expected 各放不同高熵 sentinel；攔截所有送給執行者的 prompt、feedback、artifact、telemetry 與持久 workspace，任何 sentinel 出現即 fail。負控：啟用 verbose assertion reporter，測試必須轉紅。
2. 【推論】讓 assertion repr、exception message、test name 和 path 都含 sentinel；正常 feedback 必須仍符合封閉 schema。負控：把 raw stderr 接回 feedback，測試必須轉紅。
3. 【推論】候選程式輸出偽造的 PASS、Feedback JSON、secret-like 字串與超長內容；裁定狀態只能由 evaluator 的權威 channel 改變。負控：讓 parser 接受候選 stdout，測試必須轉紅。
4. 【推論】候選嘗試讀測試 mount、proc、父程序 stack、network、共享暫存檔並把資料寫回 artifact；所有路徑應被阻止，裁定後 workspace 應無新增可見資料。負控：掛入 hidden directory 或重用 workspace，測試必須轉紅。
5. 【推論】故意讓 evaluator crash、timeout、產出 malformed evidence；結果必須是 CRITERION_ERROR，且沒有 raw 訊息。負控：把 nonzero exit 一律映成 NOT_MET，測試必須轉紅。
6. 【推論】揭露一個精確 counterexample 後，該 case 的 id 必須出現在 revoked adjudication set，最終通過不得再靠它計票。負控：拿掉 revoke transition，測試必須轉紅。
7. 【推論】同一執行者連續做超額 adaptive query；第 R＋1 次在啟動 evaluator 前就進 QUERY_EXHAUSTED。負控：只在回覆後計數，並模擬 crash 重試，測試必須抓出多一次 oracle query。
8. 【推論】對內容相同但 raw stack／輸出長度不同的失敗，外部可見 response size 與 bucket 必須相同；若威脅模型包含 timing，回覆時間也要分桶或 padding。負控：透傳精確時長，統計測試必須能區分兩組。
9. 【推論】把 Guidance Suite 全部 hard-code 通過、但違反公開 property 的其他生成案例；held-out 必須拒絕。負控：拿掉 held-out generator，測試必須出現假綠。

### 4.8 本輪建議與反轉條件

【需裁定】回饋策略：

- 【需裁定】選項 A：雙測試池＋clause-level gated feedback，本文建議的預設。代價是要維護公開 clause mapping、隔離 evaluator、回饋 reducer 與可再生 hidden cases；定位比完整 diff 慢。若 threat model 只包含無意洩漏且測試本身就是公開規格，判斷可轉向 C。
- 【需裁定】選項 B：hidden suite 只給最終 pass/fail，不在同一 Pursuit 重試。代價是梯度最弱，許多合理工作會耗盡；好處是 oracle 頻寬最低。若判準不可再生、價值高、候選可惡意探測或洩漏後損失不可接受，判斷轉向 B。
- 【需裁定】選項 C：完整失敗訊息回饋，並承認這些 tests 從第一次失敗起就是公開 guidance。代價是必須另有真正 held-out 的最終裁定，否則只證明對可見答案過擬合。若所有行為規格和案例本來就應公開、作弊無收益，這是最快的選擇。

【推論】不應選的假選項是「同一套 hidden tests 繼續當裁判，但把 expected 用 regex 遮掉」。它既損失梯度，又沒有安全邊界；碰到自訂 repr、stack、長度或候選主動 exfiltration 就破。

---

## 5. 需要現在裁定的最小清單

【需裁定】層的第一版範圍：持久佇列＋父子工作，或一般 DAG。代價與反轉條件見 1.5；本輪建議前者。

【需裁定】狀態存取拓撲：SQLite 專用 state owner、SQLite WAL 多連線、或 PostgreSQL。代價與反轉條件見 3.2、3.5、3.6；沒有 workload envelope 前，不准把 SQLite 寫成已定案。

【需裁定】判準威脅模型：防「LLM 無意看到 raw failure」還是防「候選程式主動竊取 hidden case」。前者可用分程序＋reducer；後者需要嚴格 sandbox／microVM、無網路、一次性檔案系統與側通道預算。若候選不是敵意程式且執行環境可信，成本判斷會轉向較輕隔離。

【需裁定】hidden feedback 選 A／B／C。代價與反轉條件見 4.8；本輪建議 A，且任何具體案例一經揭露立即燒掉。

【需裁定】外部 endpoint 逐一選 at-least-once 或 at-most-once。前者代價是目的端必須持久去重，後者代價是可能漏送；只有目的端提供以 idempotency key 綁定效果的原子 API 時，才能在那個 endpoint 的語義內近似 exactly-once。若目的端能力改變，裁定才反轉。

---

## 6. 對四份文件的處置建議

【推論】《重做規矩.md》：降格為遷移期寫作 lint；刪除舊名詞對照表、期別與舊契約索引。若必須保留歷史，只能放在不會被新設計引用的 migration notebook。

【推論】《主動性.md》：整份改寫成「維護提案的工作來源」。刪掉四層宣稱與 QC／READY／零爐／main-agent 接線；保留 timer、observer、delivery endpoint 的性質，但分別放回持久工作、提案與 outbox。

【推論】《選型原則.md》：L71 之後全部移出。前半重寫為權威狀態、型別化失敗、production-topology 驗證三條；不要用「有沒有直接綁一條 invariant」當唯一准入證。

【推論】《儲存選型.md》：撤回「SQLite 勝出」與「不啟用多連線 WAL」。先寫 workload／failure envelope，修正 PostgreSQL 的 xmin、advisory lock、NOTIFY 說法，再以同一 kill matrix 比較兩個 disposable spike。

【推論】最重要的刪除不是字詞，而是推理路徑：凡是「因為舊系統已經有 X，所以新系統應把 X 接好」都不能進架構核心。新局只接受「因為某個可執行性質若沒有 X 就會出現可展示的反例，所以需要 X」。
