# CLAUDE.md

## 最高原則（凌駕一切）

1. **使用者不看 code。測試是他唯一能信任的代理人。** 凡需要讀 code 才成立的防護
   一律無效——任何行為保證都必須有可執行、會 fail 的測試背書；沒有測試背書的
   改動等於沒有保證。
2. **語言**：思考、回覆、命名、註解、文件、commit message 一律繁體中文。
   ASCII 例外：跨程序 semantic id、event／schema 欄位名、DB table／column、
   CLI executable 名、failure code、shell 變數名。中文可用於檔名、Python 識別字
   與顯示文字。
   （這條寫死在此。前一版把它委派給 `~/.claude/CLAUDE.md`，而那個檔從來不存在
   ——委派出去的規則等於沒有規則。）
3. **報告**：失敗與跳過明講，不讓「沒提到」變成「通過了」。完成且驗過才說完成。
4. **地基與加蓋**（2026-08-27 控制端裁定）：**官方與權威論點是地基，優先級高於本檔。**
   本檔與官方立場衝突時，改的是本檔。nova ＝ 業界標準（地基）＋ 控制端要的（加蓋）。

   **地基由兩層構成，缺一層就不算查過**：**官方是基準**（廠商與標準組織的正式文件），
   **權威補充在基準上**（同儕審查研究與公認實務者的論點）。
   **兩層都找過，才能說地基是多了還是缺了。** 只查官方就判「業界沒有」是常見誤判——
   官方文件通常只寫「怎麼用」，不寫「為什麼這樣才對」與「什麼時候會失效」，
   後兩者住在權威層。

   **nova 本身中立且共用。** 任何具體專案樣貌都只是 nova 完成後可以長成的樣子，
   **不得寫進規格、計畫或 schema**。舉例是用來說明運作方式的，不是需求。
   `nova[llm]` 的方括號是 **extras 標記**：nova 本體是「用軟體工程的方式把那幾門
   engineering 做**拆解／組合／擴充**」這件事，`[llm]` 是裝上去的一個 extra——
   所以 claude CLI 與 codex、gemini 平級。

   **加蓋的合法動作只有兩種**（第一版寫「只能增加拒絕」，被 `nova[llm]` 自己駁倒——
   安裝 extra 會讓原本 `UNSUPPORTED_*` 的請求變成可執行，接受集合**擴大**）：
   ① 對既有能力**增加拒絕**；
   ② 透過**已宣告、具命名空間、具版本、可協商的擴充點**增加新能力。
   **未理解該擴充的舊元件必須 fail-closed 或回 `UNSUPPORTED_CAPABILITY`，
   不得靜默忽略後誤判為成功。** 這叫語意單調，不是「接受集合只能縮小」。
   出處：MCP Extensions（extension 不得移除或改名欄位、改型別、改既有行為語意、
   增加新必填欄位）、PyPA dependency specifiers 的 extras。

   **地基不是「凍結某家廠商今天的 JSON」**——否則業界出新版本時 nova 反而不能跟進。
   不可破壞的是**已採用介面的語意與相容性規則**。

   **引不出官方出處的東西不是地基**，是 nova 的拆解決定／組合契約／額外拒絕。
   標錯的代價是拿沙子當混凝土。已知降級清單見 `交接.md` §十九。

## 這個專案在做什麼

nova 把 LLM 做成系統與結構化的軟體工程——**規矩由結構承載，對錯由測試裁定，
執行者只負責做**。「執行者」泛指任何不可靠的執行者（LLM 只是目前最常見的一種），
所以**驗收權不在執行者手上**：它自認完成不算完成，判準綠了才算。這也是為什麼
判準、帳、保護清單都放在它碰不到的地方。

nova 本體就是產品：它是宿主引擎，claude CLI 與 codex、gemini 平級，都只是後端的一種。

**現在是從零建的階段。** 規格是 `docs/計畫/` 那一批計畫檔，
**份數與 task 數不寫在這裡**——那是會過期的進度，本檔不承載。
要當下的數字就跑 `uv run python docs/計畫複驗.py`，它會印出來，而且十一項不變式同時驗過。
新 session 開工先讀 `交接.md`。

## 讀到「這件事沒有機制管、只靠人記得」時

正確反應是**補上機制**：模組＋會 fail 的測試＋供外部呼叫的薄殼。
不是繞過去，也不是寫一份文件叫別人記得。

**只以文件或 skill 形式存在的規範等於不存在。**（實例：舊 nova 某份規範宣稱
「由 hook 自動把關」，而那些 hook 從未存在過。宣稱有自動把關卻沒有，比沒有規範
更糟——讀的人會以為不用自己檢查。）

判準：一條規範若「能寫成會 fail 的測試」，它就該是測試而不是文字；
若「只能靠讀者自律」，它才留在文件裡。

## 每個 task 的節奏

先寫會紅的測試 → **實際跑到指定的失敗** → 最小實作 → 跑綠 → commit。
先寫 production code 再補測試，該 task 作廢重來。
沒看過它紅過，你不知道它到底在測什麼。

## 誰有權說「接受」

唯一的接受權在 **ClaimSpec 閘**。

- 規格作者：解釋原意、提出規格修訂，**不能宣告接受**
- 實作者：只改該 task 列出的 subject，**不能改已准入的 ClaimSpec、固定負控、
  `must_fail_exactly`**
- verifier：檢查覆蓋與恆真格，**不能宣告產品接受**

規格真的錯了就停下來走 RequirementChange，舊 claim 與證據不覆寫。
測試就是規格，誰都不能自己改題目。

## 不可違反

- 每個 object 預設拒絕 unknown fields。
- 候選執行者不能自報完成、延長 deadline、改 budget、改 criterion、啟用 constraint、
  改 effect receipt、寫 state DB。
- v1 isolation 明示 `COOPERATIVE_PROCESS`；能力不足只回 typed `UNSUPPORTED_*`，
  **不得靜默降級**。
- raw mutation kill rate 永遠不進驗收判準；只有事前命名的 mutation 被指定
  predicate 殺掉才有驗收權。**這條有外部權威背書**：Google 在 ICSE-SEIP '18
  "State of Mutation Testing at Google"（DOI 10.1145/3183519.3183521）明講他們不把
  mutation score 當指標或閘，理由是「unable to find a good way to surface it to the
  engineers in an actionable way」，加上「The question of equivalence is unfortunately
  undecidable」——分數型門檻天生把不可殺的 mutant 算進分母。
  （生態現況佐證：Stryker 的 `break` 門檻**預設 null**，官方逐字「never let your build
  fail」；PIT 的整數百分比門檻官方承認會讓分數靜默退化。有工具不等於有閘。）
- 燒錢測試三擇一：錄／播／明講跳過，不做無紀錄的裸真跑。
- 「全集」宣稱一律直接列舉目標型別，不從別的型別推導：列目錄用 `iterdir()` 過濾
  `is_dir()`、列類別走 `ClassDef`、數呼叫走 `ast.Attribute`、找環跑 SCC。
  （舊 nova 一晚同一種錯發作四次。）

## 不可機械化的判斷（住在這裡的理由：永遠不會變成測試）

- **口徑要小到「一次做得完」**：4 檔＋22 函式包成一份目標，執行者連兩次輸出計畫、
  零檔案變更；切成七份檔案級小目標後全部一次收斂。
- **「換個情境跑綠」不能判定假紅**：要證明的是原情境重跑也綠。
- **監看器事件是二手資料**：關鍵判斷回頭看一手來源（日誌檔、程序表、git 狀態）。
- **不要對執行者的自報照單全收**：包括其他 agent 回報的結果。

## 陷阱當 feedback 收，不當紀念碑立

實測踩過的坑記在 `docs/陷阱.md`，那是**待轉化的佇列**不是紀念碑。
每條坑的預設命運是變成機制：能寫成會 fail 的測試就去寫，寫完把發作情況與代價
搬進那格的 docstring，佇列那條就刪掉。刪除前提有二、缺一不可——
①機制存在 ②負控證明它抓得到那個壞。評估後決定不做的，要留下判斷理由與量測數字。

**進行中狀態進 `交接.md`，歷史進 git log。CLAUDE.md 本體不寫會過期的進度。**

## 結構

分層見 `docs/計畫/00-總覽.md`。依賴只能向下——上層可用下層，下層不得知道上層。
層的權威清單是 `架構/目錄規則.toml`（十三層，不是九層；是 `基礎設施` 不是 `設施`）。

這條規則有**兩個範圍不同的執法器**：

- **通則方向**（任意層之間）：`架構/檢查工程規範.py` 讀 `架構/目錄規則.toml`，
  由計畫 01 Task 3 建立，**已綠**。負控在 `架構/test_工程規範.py`：靜態違規邊、
  `importlib.import_module("上層.X")` 動態違規邊、非 literal target 各一格，
  再加一格「合法的下行依賴不被誤殺」防恆真。
- **DB bypass 特例**（上層 → `sqlite3`／`nova.基礎設施.狀態庫.*`）：
  `架構/依賴規則.toml`、`架構/檢查後端依賴.py` 與 `架構/test_依賴規則.py`，
  由計畫 03 Task 8 建立，**尚未存在**。

**閘已經接上自動執行點（2026-08-27，計畫 01 Task 13）。** 這一段原本寫「目前沒有任何
自動觸發器」，條件是「哪天真的接上，先確認觸發器存在且有測試背書，再改這一段」——
現在滿足了，所以改。

閘清單只有一份：`架構/目錄規則.toml` 的 `[[gate]]`（format／lint／types／placement／
plans／tests）。三處共讀，不各自維護：

- **`uv run python 工具/驗全部.py`** —— 單一本地入口。跑完每一道才回報，
  **不在第一個紅就停**（先停會讓後面的閘從此沒人跑過），任一紅即非零。
- **pre-commit hook** —— 由 `工具/裝_git_鉤子.py` 安裝。`.git/` 不在版控裡，
  所以 clone 之後**必須有人跑那支裝**，否則等於沒裝。
- **`.github/workflows/gates.yml`** —— push 與 PR 都跑。**檔名必須 ASCII**：
  實測叫 `驗收.yml` 時 GitHub 註冊成功、顯示 active、手動觸發也跑得起來，
  但 `push`／`pull_request` **一次都不觸發**，而 UI 上完全看不出異常。

**還是不准寫「不可能繞過」。** 五個確切的上限。前三個是人為決定，**第四、五個是機制漏洞**：

1. hook 可以被 `git commit --no-verify` 繞過。**2026-08-27 我自己就繞過一次**，
   把一個測試引用舊檔名的壞 commit 送進 main，CI 才抓下來。
2. hook 可能**根本沒裝**——`.git/` 不在版控裡，新 clone 預設沒有，
   要跑 `uv run python 工具/裝_git_鉤子.py`。
   （附帶：Git 官方逐字說 hook 沒有 executable bit 就被 `ignored`——**靜默**。
   `裝_git_鉤子.py` 哪次 chmod 失敗，hook 從此不跑而不會有人發現。這值得一格負控。）
3. **「紅了合不進去」2026-08-27 起成立，但有兩個人為出口。** ruleset `main-gates`：
   必經 PR、`gates` 必須綠、擋 force push 與刪除。**實測**：直推 main 得到
   `GH013 ... Changes must be made through a pull request.`；CI 紅的 PR 合併得到
   `the base branch policy prohibits the merge`。出口是 `gh pr merge --admin`
   （GitHub 官方明列的繞過通道）與 repo 設定隨時可被改掉。
   **這兩個是人為決定不是機制漏洞。** 業界的做法不是消滅它，是**記錄連續性**
   （SLSA Source Track），讓繞過留下痕跡並使 claim 自動降級。
4. **CI 跑的是候選者自己那一份 checker。這是機制漏洞，不需要任何人為決定。**
   **實測**（PR #8 的真實 CI log，2026-08-27）：
   `git checkout --progress --force refs/remotes/pull/8/merge` →
   `HEAD is now at d7d1587 Merge 2d93188... into 0f664a7...`。
   六道閘的程式（`架構/檢查工程規範.py`、`docs/計畫複驗.py`、pytest 收到的測試檔）
   **全部來自 PR 的 commit**，沒有任何一道去 base branch 讀基準。
   在同一個 PR 裡把 checker 改成 `raise SystemExit(0)`，required check 會綠。
   官方解法：ruleset workflows 可指定 workflow 檔**來自另一個 repo／另一個 ref**，
   讓閘的觸發與程式離開被閘管的人的寫入範圍。**尚未做，計畫 01 Task 16。**
   （我證到的是「跑的是哪一份 code」；「跑起來會綠」是從「沒有任何閘讀 base 基準」
   推出來的，**沒有實跑過破壞實驗**。）
5. **被 `if:` 跳過的 job 會被算成通過。** GitHub 官方對 required status check 的
   通過定義逐字是「must have a `successful`, `skipped`, or `neutral` status」。
   `gates` job 哪天加了條件式，閘會**靜默變成永遠綠**——這是「入口永遠回零」的 CI 版本。

**GitHub branch protection 預設不套用到 admin**（官方逐字「the restrictions of a branch
protection rule do not apply to people with admin permissions」）。裝了就以為擋得住自己
是最普遍的誤解；要另外開「Do not allow bypassing the above settings」。

負控實跑過四條（入口第一紅就停、入口永遠回零、CI 漏跑一道、hook 吞掉非零 exit），
外加防恆真格「閘全綠時 hook 不擋正常 commit」。claim 落點
`規格/工程/保證/閘必須自動執行.claim.json`。

領域與權威是唯一持有終態權的兩層；其餘每一層都可以被替換或重建而不改變任何
行為保證。**沒有自己生命週期的東西不是層，是資料。**
