# 新局第五輪：雙方簽字——額度證據、分層儲存、Guard 邊界與 Python 實測

## 0. 先簽結論

【推論】我接受你第五節的五項定案條件。你的事件容量反例成立，保留期必須落成不同生命週期的儲存層，Guard 必須是封閉語言，工具鏈不能靠版本宣傳判定。額度部分採你的五種情況，但修正一個會說謊的名字與語義：`now > resets_at` 只能證明**舊窗口已結束**，不能證明新窗口仍是滿額；因此 `INFERRED` 改名為 `WINDOW_ROLLED_UNOBSERVED`，只開一個有界探測名額，不產生 inferred remaining。

【推論】我不同意的只有兩個窄句，不影響你的五項條件成立：第一，五態是**每一個 quota bucket 的證據態**，不是整個 backend 的單一狀態；第二，有版本化 recovery checkpoint 後，權威 SQLite 的 hot history 長度由 checkpoint／archive protocol 決定，不必等於完整 Work 年齡。Work 本身仍有外部 7 天 absolute deadline（pause 不停鐘），所以完整 active lineage 一定落在 90 天 warm retention 內；非終態 recovery checkpoint 則保留到終結後 24 小時。

【推論】未決條目數為 **0**。SQLite single-owner／rollback 的權威狀態庫不翻案；第三輪「v1 不 compact／delete 領域事件」翻案；CPython 固定為 **3.14.7**，四項 day-one 工具全部實跑通過。依你明列的充分條件，加上我在此對修正版的明示同意，這一版完成雙方簽字。

| 你的簽字條件 | 本輪處置 | 結果 |
|---|---|---|
| 額度五態或更好的模型 | 【推論】保留五種證據態，改成 per-bucket，修正 reset 推論，加入 bucket topology。 | 【推論】成立。 |
| steady event rate 與乘積 | 【推論】新增 0.5 tx/s、4 events/tx、2 events/s 與 byte charge；所有 24h／90d／365d 乘積列在第 2 節。 | 【推論】成立。 |
| 保留分層也是儲存分層 | 【推論】hot state、warm operational segments、cold audit／raw／artifact pins 分開；共用 CAS bytes 也有不同 pin ledger。 | 【推論】成立。 |
| Guard 邊界與逃生路徑 | 【推論】封閉 AST、精確 proof domain、禁止項、拒絕路徑及 custom producer 硬預算都列在第 3 節。 | 【推論】成立。 |
| Python 工具鏈實測 | 【實測】3.14.7 上 pytest＋Hypothesis＋xdist 通過；mutmut 產生 12 個 mutant 並殺掉 12 個。 | 【推論】成立。 |

---

## 1. 額度：接受五種情況，但狀態的主詞必須改對

### 1.1 你推翻了什麼

【查證】本輪輸入提供兩份直接觀測：Claude Agent SDK 的 `RateLimitEvent`／`RateLimitInfo` 帶 `status`、`utilization`、`resets_at`、多種 `rate_limit_type` 與 overage 欄位；codex session 的 `token_count.rate_limits` 帶 primary window、credits、plan 與 reset time。兩者共同點是額度隨執行事件送出，不是獨立 query endpoint。（來源：本輪第二節所列 SDK 型別與實際 codex event。）

【推論】因此第四輪用來處理「沒有 observation 能力」的 `BLIND_BOUNDED` 不能再當 Claude／codex 的主路徑。它仍是本地之外、只會回 rate-limit rejection 或完全沒有 quota signal 的 backend fallback；Claude／codex 主路徑改為 **push-observed＋有界 observation probe**。

【推論】冷啟動與陳舊觀測確實不能用舊三態講清楚；你抓到 reset boundary 也能提供資訊。但 `resets_at` 沒有證明重置後沒有別的 client 已經消耗，也沒有提供 provider atomic reservation。把它叫「推定已滿」會讓 UI 與派工閘共同說謊。

### 1.2 正式模型：每個 bucket 五種證據態

【推論】額度的最小單位是 `QuotaBucket`。Claude 的 five-hour、seven-day、model-specific、overage，或 codex 的 primary、secondary、credits，必須各有自己的觀測；backend summary 是政策函式的輸出，不覆寫 bucket evidence。

```text
QuotaBucketEvidence
  backend_id: BackendId
  account_scope: AccountScopeId
  bucket_id: provider-stable id
  bucket_kind: RATE_WINDOW | CREDITS | OVERAGE
  metric_kind: FRACTION_USED | ABSOLUTE_REMAINING | STATUS_ONLY
  evidence_state:
    NOT_APPLICABLE
    OBSERVED_FRESH
    OBSERVED_STALE_SAME_WINDOW
    WINDOW_ROLLED_UNOBSERVED
    NEVER_OBSERVED
  provider_status?: ALLOWED | ALLOWED_WARNING | REJECTED
  utilization?: Decimal[0, 1]
  remaining?: Quantity
  observed_at?: Instant
  resets_at?: Instant
  source_event_digest?: Sha256
  source_session_id?: SessionId
```

| 證據態 | 精確條件 | UI 可說什麼 | 派工閘 |
|---|---|---|---|
| `NOT_APPLICABLE` | 【推論】admitted backend manifest 明示此 bucket／backend 沒有外部 quota 概念。 | 【推論】顯示「不適用」，不能畫無限大。 | 【推論】不參與 provider-quota 判斷；自有預算仍照常 reserve。 |
| `OBSERVED_FRESH` | 【推論】有型別化 observation，`now - observed_at ≤ 300s`，且尚未越過 `resets_at + 60s` clock-skew guard。 | 【推論】顯示值、metric kind、窗口、觀測時間、來源與 `KNOWN` 人類標籤。 | 【推論】先套 provider status，再依 metric kind 套第 1.3 節政策；只有 absolute metric 才能聲稱 worst-case sufficient。warning 至少降成 single-flight；rejected 封鎖。 |
| `OBSERVED_STALE_SAME_WINDOW` | 【推論】有 observation，已超過 300 秒，且 `now < resets_at + 60s`；沒有 `resets_at` 也落這態。 | 【推論】顯示最後值及 `STALE`，不得顯示成 current remaining。 | 【推論】最後 utilization 最多只是「已用量下界／剩餘量上界」；不准普通派工。若最後已 rejected，等 reset；否則每 15 分鐘最多放一個真實工作作 observation probe。 |
| `WINDOW_ROLLED_UNOBSERVED` | 【推論】既有 observation 的 `resets_at + 60s ≤ now`，但新窗口還沒有 observation。 | 【推論】顯示「舊窗口已過；新窗口未觀測」，不得顯示 0% used 或 100% remaining。 | 【推論】立即允許一個 probe，之後仍每 15 分鐘最多一個；沒有新 observation 就不能升 `OBSERVED_FRESH`。 |
| `NEVER_OBSERVED` | 【推論】該 account／bucket 從未收到 observation。 | 【推論】顯示 `UNKNOWN／冷啟動`。 | 【推論】允許一個有界 cold-start probe；若一律拒絕，觀測只能在 execution 中出現的 backend 會永久死鎖。 |

【推論】300 秒是 v1 的 observation freshness policy；60 秒只容忍 wall-clock 與 provider reset time 的偏差。TimeAuthority 不確定度若超過 60 秒，就不准進 `WINDOW_ROLLED_UNOBSERVED`，維持 stale。這兩個值都在 immutable ResourcePolicy revision 中，不能由 adapter 自己延長。

【推論】probe 不是免費 ping，也不是繞過帳。它就是佇列中下一個合格 Execution，先按自己的最壞成本 reserve，標 `quota_probe=true`，同一 backend／account 同時最多一個。成功但完全沒有 quota event 時，工作成果照常處理，額度證據仍不升級；後續維持 single-flight probe 路徑。這把未知造成的暴露限制在一個在途呼叫，而不捏造剩餘量。

【推論】Claude 的 `utilization` 與 codex 的 `used_percent` 沒有給 quota denominator，也沒有公開「這個 Execution 最壞會吃幾個百分點」的換算。因此它們能誠實提供 fractional headroom，**不能**證明本次 worst-case units 一定放得下。只有 adapter 同時提供 compatible absolute remaining／request units 時，才可跑「remaining 扣 in-flight reserve」；把百分比硬換成 tokens 是另一種偽造。

### 1.3 多窗口不能用「最差狀態 wins」草率壓平

【推論】backend manifest 還必須宣告 `QuotaTopology`：included channel 中哪些 bucket 是 `ALL_OF` 的硬窗口，哪些 credits／overage 是替代 channel。ResourcePolicy 再明示允許哪些 channel。否則 seven-day 已滿但 overage 可用、或 primary 與 secondary 同時約束時，單一五態都會判錯。

```text
QuotaTopology
  channels:
    - id: included
      requires_all: [five_hour, seven_day, optional_model_window]
    - id: overage
      requires_all: [overage_status, credit_balance]
      spend_channel: PROVIDER_OVERAGE

ResourcePolicy
  allowed_channels: [included]       # v1 預設；不默認花 overage
  overage_hard_cap: Money | null
  fraction_normal_below: 0.80
  fraction_single_flight_below: 0.95
```

【推論】v1 預設不啟用 overage／credits 支出；要啟用必須產生新 ResourcePolicy revision、自己的金額硬上限與 UI event。quota topology 只描述外部限制的形狀，不能自行取得花錢權。

【推論】fresh bucket 的 metric gate 固定如下：`ABSOLUTE_REMAINING` 才檢查 `remaining - in_flight_worst_case ≥ request_worst_case`；`FRACTION_USED < 0.80` 可普通派工，`0.80 ≤ used < 0.95` 只可 single-flight，`used ≥ 0.95` 只可每 15 分鐘一個 probe；`STATUS_ONLY/ALLOWED` 永遠 single-flight。`ALLOWED_WARNING` 至少 single-flight，`REJECTED` 在同一窗口零派工。這些門檻是保守 policy，不冒充「白卷絕不發生」的 provider guarantee。

【推論】UI 同時呈現各 bucket、聚合 eligibility、本地 budget 與所有 in-flight reservation。它不得把 provider observation 當權威帳，也不得把 fresh observation 描述成 provider 已替本次 execution 保留額度；外部 client 仍可在觀測與派工之間競態。

### 1.4 對第四輪規格的精確變動

| Semantic id | 處置 |
|---|---|
| `resource.provider-quota.observable.fresh-required` | 【推論】修改：freshness 改為 per-bucket，失鮮只可走 single-flight probe，不再一概永久零派工。 |
| `resource.provider-quota.observable.worst-case-sufficient` | 【推論】修改：只適用 `ABSOLUTE_REMAINING` 且 units compatible 的 bucket；依 `QuotaTopology` 計算並扣本地已在途 worst-case units。percentage／status-only 不得拿此 claim。 |
| `resource.provider-quota.observable.fractional-headroom-bounded` | 【推論】新增：80%／95% 三段政策與 warning／rejected 優先規則；負控證明 percentage 不被換算成假 absolute units。 |
| `resource.provider-quota.window-rollover-not-full` | 【推論】新增：固定反例是在 reset 後由另一 client 先耗盡；閘不得產生 inferred remaining 或普通派工。 |
| `resource.provider-quota.observation-probe.single-flight` | 【推論】新增：fresh／stale／rolled／never 的 probe matrix、15 分鐘間隔與 crash reclaim。 |
| `resource.provider-quota.bucket-topology-policy` | 【推論】新增：ALL_OF 窗口與 optional spend channel 不得被扁平化。 |
| `resource.provider-quota.unobservable.no-fabricated-value` | 【推論】保留：只管根本沒有可靠 observation capability 的 backend。 |
| `resource.provider-quota.blind-dispatch.single-flight` | 【推論】保留：降為無 observation capability 的 fallback，不再描述 Claude／codex 主路徑。 |
| `view.provider-quota.observability-truthful` | 【推論】修改：顯示 per-bucket 五態、reset rollover、policy channel 與 aggregate eligibility。 |

---

## 2. Envelope 與儲存：你的乘法成立，第三輪必須翻案

### 2.1 反例判決

【實測】以二進位 GiB 重算，`5 events/s × 300 B × 90 days ÷ 2^30 = 10.862947 GiB`。你表中的 5/s、300 B 已穿過 10 GiB 是對的；50/s、300 B 則是 108.629 GiB 左右。

【推論】原 envelope 的錯不只少了「預期穩態」一欄。它還把 **tx/s、events/tx、serialized bytes/event、SQLite on-disk amplification、CAS bytes 與 retention horizon** 混成互不相乘的數字。一筆 transaction 可同時寫 transition、reserve、effect intent、lease 與 observation；所以用 `tx/s = events/s` 甚至可能低估。

【推論】先前漏算的寫入來源至少包括：每 transaction 多事件、1 秒／64 KiB raw stream chunks、quota observations、lease renew／takeover、outbox intent／receipt、budget reserve／settle、criterion evidence refs、checkpoint 與 segment manifests。raw stream 與 artifacts 不該進 SQLite，但它們仍會吃 CAS、backup inventory、GC 與保留額度；搬出 DB 不等於不存在。

### 2.2 修正版 v1 envelope：上限與穩態分開

| 欄位 | v1 初值 | 選值理由 | 被打破時先撞什麼 |
|---|---|---|---|
| 預期 owner transaction rate | 【推論】24 小時 rolling mean `≤ 0.5 tx/s`。 | 【推論】8 個 running Execution 的語義事件不是 token 流；把一般負載與壓測帽分開。 | 【推論】lease／effect／tool 粒度過細時先升高。 |
| 預期 events/transaction | 【推論】mean `≤ 4`；單一 transaction hard max `32`。 | 【推論】容納 transition＋ledger＋effect 等原子組合，同時阻止一次 command 無界 fan-out。 | 【推論】批次 child/effect command 先被 `EVENT_FANOUT_LIMIT` 拒絕。 |
| 預期 operational event rate | 【推論】24 小時 rolling mean `≤ 2 events/s`；這是 retention sizing 的主數字。 | 【推論】由前兩欄相乘，現在可機械檢查。 | 【推論】超過 2/s 連續 24 小時先使 90 天 warm tier 越過容量線。 |
| 每 Work operational events | 【推論】hard max `8,192`，不含已外置的 raw stream chunks；第 8,192 槽保留給 terminal。 | 【推論】既有 8 Pursuit／1,024 paid-call 上限仍需要 intent、result、transition 與 ledger 餘裕；同時替單一 Work 的 archive 佔用封頂。 | 【推論】已有 8,191 events 時再要求非終態 event，owner 改寫成第 8,192 筆 typed `EVENT_LIMIT` terminal；不能繞去 per-token event。 |
| Work absolute lifetime | 【推論】建立後最多 `7 days`，包含 PAUSED 時間；到點由外部 timer 使 Work 進 typed `DEADLINE_EXHAUSTED`。 | 【推論】「可暫停接手」不是「可以永久不終止」；7 天仍容許跨日換後端，並守住整體一定停止與 90 天 replay。 | 【推論】要保留同一 lineage 超過 7 天時，必須升 WorkPolicy revision；v1 到期後只能建立明示 successor Work。 |
| event bytes | 【推論】預期 serialized mean `≤ 512 B`；retention sizing charge `1,024 B/event`；單筆 hard max仍為 `64 KiB`。 | 【推論】512 B 是預期值，1 KiB 為 framing／schema metadata 餘裕，64 KiB 只是拒絕巨型 state payload 的上限。 | 【推論】高體積 verdict／error detail 未外置 CAS 時先打破 mean。 |
| hot SQLite charge | 【推論】壓測按 `4,096 B/event` 計，包含 page、index、head／manifest 與 free-space amplification。 | 【推論】不再拿 JSON bytes 冒充 SQLite 檔案增量；實作後以 `page_count × page_size` 實測替換，但只能收緊 admission 或升版 envelope。 | 【推論】索引過多、VACUUM 策略或小 transaction page churn 先超出。 |
| 持續壓測 | 【推論】`50 tx/s` 明定為 **60 分鐘 soak**，mean 4 events/tx；不是永遠穩態。 | 【推論】保留原本選引擎的高壓要求，又停止用無限時間的「持續」與固定磁碟帽互相矛盾。 | 【推論】一小時內 hot DB 預估增加 2.747 GiB；先撞 write latency／hot soft point。 |
| burst | 【推論】`200 tx/s × 10s`，30 秒清 backlog，mean 4 events/tx。 | 【推論】保留 lease storm／restart fan-in 測試。 | 【推論】owner queue 與 p99 先撞，不是 90 天容量。 |
| segment／checkpoint | 【推論】event segment 每 1 小時或 64 MiB uncompressed 先到者 seal；每個非終態 aggregate 每 256 transitions 或 1 小時建立 recovery checkpoint，先到者。 | 【推論】使 hot horizon 與長期 Work 年齡脫鉤，又限制重播 suffix。 | 【推論】checkpoint 太大或 fold 太慢先撞 recovery SLO。 |
| hot overlap | 【推論】已 seal 且 checkpoint 覆蓋的 event 仍在 SQLite 保留 24 小時，之後才可 prune。 | 【推論】給 crash、backup、publisher 與回滾一個完整交疊窗口。 | 【推論】長 outage 超過 24 小時時仍可讀 warm segment，但維護操作會變慢。 |
| hot SQLite points | 【推論】4 GiB target、8 GiB soft maintenance、10 GiB hard stop ordinary admission。 | 【推論】steady 24h 與一小時 soak 都有數倍餘裕；10 GiB 不再承擔 90 天歷史。 | 【推論】archive／checkpoint worker 停擺最先把 hot 推到 8／10 GiB。 |
| tail cache | 【推論】`min(最近 7 天, 2 GiB)`；更舊但仍在 90 天內的 cursor 透明改讀 warm segments。 | 【推論】UI 熱路徑保留便宜 SQLite WAL，cache 不取得 retention 權威。 | 【推論】高事件率只縮短 cache 時間，不縮短 90 天可回放承諾。 |

【推論】50 tx/s 若仍被要求「無限期 production steady」，就不能同時固定 10 GiB hot 與有限 archive；那會變成持續外送的 log-service workload，需重新比較 PostgreSQL／專用 segment service。v1 現在沒有偷藏這個矛盾：steady 與 soak 各有明確時間窗。

### 2.3 乘積重新檢查

| 算式 | 結果 | 對應容量決定 |
|---|---:|---|
| `2 events/s × 512 B × 90d` | 【實測】7.415771 GiB | 【推論】operational archive 的 expected footprint。 |
| `2 events/s × 1,024 B × 90d` | 【實測】14.831543 GiB | 【推論】operational archive sizing footprint；16 GiB soft、20 GiB hard。 |
| `2 events/s × 4,096 B × 24h` | 【實測】0.659180 GiB | 【推論】hot journal steady overlap 的保守 charge；低於 4 GiB target。 |
| `50 tx/s × 4 events/tx × 4,096 B × 1h` | 【實測】2.746582 GiB | 【推論】soak 的 hot 增量；仍低於 4 GiB target，未計 base state 時由 8 GiB soft point 承接。 |
| `200 tx/s × 4 × 1,024 B × 10s` | 【實測】7.812500 MiB | 【推論】burst 對長期 archive 很小，主要驗 write queue。 |
| `0.2 audit records/s × 1,024 B × 365d` | 【實測】6.015015 GiB | 【推論】cold audit expected footprint；12 GiB soft、16 GiB hard。 |
| `100 Executions/day × 20 MiB raw × 30d` | 【實測】58.593750 GiB | 【推論】raw-log CAS expected footprint；每 Execution 64 MiB hard cap，64 GiB soft、80 GiB hard。 |
| `10 accepted artifacts/day × 4 MiB × 365d` | 【實測】14.257812 GiB | 【推論】accepted-artifact expected footprint；每 artifact 256 MiB hard cap，24 GiB soft、32 GiB hard。 |

【推論】上述 raw／artifact 數字是 v1 admission envelope，不是假裝量到的生產分布。實際 rolling mean 一旦超出就產生 maintenance evidence；hard point 到達時停止普通新 Work，不能提前刪資料來假裝仍符合 retention。

### 2.4 保留分層現在就是儲存分層

| 儲存層 | 住什麼 | 保留／上限 | 權威語義 |
|---|---|---|---|
| hot authoritative state SQLite／rollback | 【推論】aggregate heads、lease、unsettled resource/effect、unsealed events、24h overlap、segment manifest、非終態 recovery checkpoint refs。 | 【推論】checkpoint ref 保留到 aggregate 終態後 24h；event overlap 24h；4／8／10 GiB。 | 【推論】唯一 mutable state owner；不承擔 90 天 UI history。 |
| warm operational event segments in CAS | 【推論】canonical event envelopes、連續 `global_seq` range、schema／machine digests 與 segment predecessor。 | 【推論】完整 operational log 90 天；16／20 GiB。 | 【推論】segment bytes immutable；7 天 Work deadline 保證 active Work 從 genesis 的純 event fold 不會遇到 retention gap；是否屬於 log 由 state-owned manifest 決定。 |
| rebuildable tail SQLite／WAL | 【推論】最近 7 天或 2 GiB 的 range cache與 publisher cursor。 | 【推論】可隨時砍掉重建；不是 retention store。 | 【推論】UI 長讀只碰它或 warm segment reader，永不碰 state-owner transaction。 |
| cold audit segments／pins | 【推論】verdict、budget ledger、ClaimSpec／criterion provenance、effect receipts 的 audit subset。 | 【推論】365 天；12／16 GiB。 | 【推論】與 operational pin 分離；90 天後仍被 audit pin 引用的 CAS bytes 不 GC。 |
| raw executor-log CAS pins | 【推論】1 秒／64 KiB chunks 與 execution manifest。 | 【推論】30 天；64／80 GiB；單 Execution 64 MiB。 | 【推論】不是 event row，也不得拖進權威 transaction。 |
| accepted-artifact CAS pins | 【推論】被 verdict 接受並明示 pin 的 artifacts。 | 【推論】365 天；24／32 GiB；單 artifact 256 MiB。 | 【推論】artifact pin 與 raw-log pin 分離；相同 blob 可物理去重，但各 retention ledger 都要到期才 GC。 |

【推論】我接受你「保留分層必須同時是儲存分層」的核心。修正只在一點：不要求每層使用不同引擎或不同磁碟；同一 CAS 可以物理去重，但 namespace、manifest、pin、容量帳與 GC eligibility 必須分層，否則最短 retention 會誤刪最長 retention。

【推論】你說「未完成 Work 的長度要有上界」是對的，本輪把上界定為 7 天；我只修正它不是 hot SQLite history 的計算式。hot recovery 用 checkpoint＋suffix，warm event store 保留完整 90 天，因此 active Work 可從 genesis 做 UI 純 fold。Work 到 deadline 必須終態，不能靠 PAUSED 逃過；到期後若仍要追同一產品目標，建立帶 predecessor lineage 的新 Work，而不是把舊 Work 偷偷續命。

### 2.5 seal／checkpoint／prune 的唯一合法順序

【推論】邏輯上的權威 event log 定義為：`hot committed range + state-owned committed SegmentManifest 所引用且 hash 正確的 CAS segments`。head 與 checkpoint 是可驗衍生物，不是第二份 event truth。

1. 【推論】archive worker 從 read port 取連續 range，canonical encode，先把 segment blob 寫入 CAS。
2. 【推論】worker 重新讀 blob，驗 digest、event count、首尾 `global_seq`、predecessor digest 與每筆 schema／machine ref。
3. 【推論】state owner 用一筆 transaction 插入 immutable `SegmentManifest`；range overlap 或缺口由 unique／check constraint 拒絕。
4. 【推論】aggregate checkpoint blob 同樣 blob-first；manifest 固定 `aggregate_seq`、machine digest、fold-code digest、state digest 與被覆蓋 segment cursor。`checkpoint + suffix` 必須與 genesis full replay 等價。
5. 【推論】只有 manifest committed、checkpoint 覆蓋、tail publisher 已越過 range、且 24h overlap 已過，pruner 才能以 bounded transaction 刪 hot event rows；刪除不碰 aggregate head。
6. 【推論】90／365／30 天到期只撤對應 retention pin；非終態 recovery checkpoint 在 Work 終結後 24 小時前不得撤。CAS GC 只刪沒有任何 recovery／audit／artifact pin 的 blob；hard capacity 到點不准縮短 retention。

【推論】每個箭頭前後都要 SIGKILL：blob orphan 可 GC；沒有 manifest 的 blob不屬於 log；manifest 不得指缺 blob；prune 前 crash 可重做；prune 後必須由 segment＋checkpoint 重建。這組負控通過以前，不准啟用 production prune。

【推論】這一裁決撤銷第三輪第 2.8／4.4 的「v1 不 compact／delete 領域事件」以及「尾隨庫只從仍在 state DB 的完整 journal 重建」。新的尾隨庫可由 warm segments＋hot suffix 重建；`subscribe(after_global_seq)` 在 90 天內跨 segment／tail 邊界不得多送、漏送或改 event bytes。

### 2.6 新增／修改的儲存保證

| Semantic id | 處置 |
|---|---|
| `storage.operational-event.retention-tiered` | 【推論】新增：hot／warm／cold pin 與 24h／90d／365d lifecycle 可執行。 |
| `storage.event-segment.publish-before-prune` | 【推論】新增：六步 crash matrix，manifest 不可指缺 blob，未 commit segment 不得進 logical log。 |
| `storage.recovery.checkpoint-suffix-equivalent` | 【推論】新增：隨機 event prefix 與故意腐敗 checkpoint 都要驗 full replay 等價。 |
| `storage.retention.no-early-delete-at-cap` | 【推論】新增：容量 hard point 只能停普通 admission／提 maintenance，不得縮 retention。 |
| `view.event-stream.segment-tail-contiguous` | 【推論】新增：90 天內跨 warm／tail 的 cursor exactly-contiguous，transport 仍可 at-least-once。 |
| `work.crash-rebuild.persisted-only` | 【推論】修改：recovery source 明列 checkpoint、segment manifest／CAS 與 hot suffix，不再假定完整 history 永住 SQLite。 |
| `work.lifetime.absolute-seven-day` | 【推論】新增：fake clock 跨過 7 天時，RUNNING／PAUSED 都只能進 `DEADLINE_EXHAUSTED`；executor 與 operator 不能延鐘。 |
| `work.operational-event-limit` | 【推論】新增：第 8,192 槽只准 terminal；8,191 後的非終態 stimulus 必須產生 `EVENT_LIMIT`，任何第 8,193 筆都被 DB constraint 拒絕；raw CAS chunk 不誤計、domain event 不漏計。 |

---

## 3. Guard v1：能表達什麼、絕對不能塞什麼

### 3.1 核心裁決

【推論】「狀態機是宣告資料」保留，但範圍說窄：**狀態、trigger、edge、terminal、guard composition 與跨層 binding 是宣告資料；期限計時、預算核准、候選排名與 provider fault normalization 由各自權威產生型別化事件。** 狀態機不必、也不該成為所有業務演算法的程式語言。

【推論】Guard AST 永久禁止 function name、module path、Python expression、shell、eval、callback id。runtime 只解釋編譯後的封閉 `GuardPlan`；第一個真 guard 不能偷偷開 arbitrary-code 缺口。

### 3.2 型別與封閉運算子

【推論】`nova.guard/1.0` 只有三種 scalar domain：`BOOL`、最多 32 個 symbol 的 `ENUM`、以及帶 `min`／`max`／`unit` 的 `BOUNDED_INT`。optional 不是 `null`；必須建模成 enum variant。Fact binding 只能指向 admitted trigger payload 或 aggregate snapshot schema 中的 scalar JSON Pointer，不能指向計算函式。

```ebnf
guard       = all | any | not | atom ;
all         = { "op":"ALL", "args":[ guard, guard, {guard} ] } ;
any         = { "op":"ANY", "args":[ guard, guard, {guard} ] } ;
not         = { "op":"NOT", "arg":guard } ;
atom        = bool_is | equal | not_equal | in_set | not_in_set | ordered ;
bool_is     = { "op":"BOOL_IS", "fact":fact_ref, "value":boolean } ;
equal       = { "op":"EQ", "fact":fact_ref, "value":typed_literal } ;
not_equal   = { "op":"NE", "fact":fact_ref, "value":typed_literal } ;
in_set      = { "op":"IN", "fact":enum_fact_ref, "values":[enum_literal...] } ;
not_in_set  = { "op":"NOT_IN", "fact":enum_fact_ref, "values":[enum_literal...] } ;
ordered     = { "op":("LT"|"LTE"|"GT"|"GTE"),
                "fact":bounded_int_ref, "value":same_unit_literal } ;
```

【推論】結構硬上限為 AST depth 8、nodes 64、每個 `ALL／ANY` 2–16 children、每個 set 1–32 values、每 machine 32 facts。comparison 右側只能是同型 typed literal；不能 fact-to-fact compare。所有 unknown field／operator／unit／fact ref 直接 `UNSUPPORTED_GUARD`。

### 3.3 明確不能表達的東西

【推論】Guard v1 不能表達：加減乘除、aggregation、collection traversal、字串／regex、浮點、動態 lookup、跨 aggregate query、fact-to-fact 比較、時間讀取、亂數、I/O、網路、例外捕捉、迴圈、遞迴、使用者函式、模型呼叫或人類自然語言。

【推論】下面四個「第一個真 guard」不直接塞成複雜式子：

| 問題 | 正確建模 |
|---|---|
| deadline | 【推論】可信 Timer Authority 到點發 `deadline.reached` trigger；Guard 不讀 `now`。 |
| budget | 【推論】Resource Authority 先做 reserve，發 `reservation.granted／denied(reason)`；Guard 只看 enum reason。 |
| child verdict／selection | 【推論】Evaluation／Work selection 產生 `selection.completed(outcome, evidence_ref)`；Guard 不重做排名。 |
| backend fault | 【推論】adapter 先依 admitted fault taxonomy 正規化成 enum event；unknown fault 明確是 `UNCLASSIFIED_BACKEND_FAULT`，不是自由文字 guard。 |

【推論】這不是把複雜度藏起來：產生 typed event 的 authority 仍須有自己的 MachineSpec／DecisionTableSpec、ClaimSpec、source digest 與負控；它只是不取得改寫 consumer state machine edge 的權力。

### 3.4 互斥與完備怎麼機械證明

【推論】compiler 對每個 `(state, trigger)` 建 finite proof cells：BOOL 為兩格；ENUM 每 symbol 一格；BOUNDED_INT 只按 guard 出現的 literals 切成等價 interval／point。因為語言沒有 arithmetic 或 fact-to-fact relation，每一 cell 內所有 predicate 結果固定。

【推論】所有 facts 的 Cartesian cells 上，每一格必須**恰有一條** edge 為 true；0 條回 `GUARD_NOT_EXHAUSTIVE` 並給 witness，2 條以上回 `GUARD_OVERLAP` 並給 witness。proof cells hard max 4,096；超過回 `GUARD_DOMAIN_TOO_LARGE`，不能跳過 proof 或降成抽樣。

【推論】admission 另做：dangling fact／edge、型別與 unit、terminal 無 outgoing、nonterminal 至少一條 outgoing、reachability、可達 terminal、AST limits、trigger payload schema closure。runtime 只接受帶 admitted MachineSpec digest 的 compiled plan；state transaction 的 transition composite FK 仍是第二道執法，沒有宣告的 tuple 永遠 commit 不了。

### 3.5 表達不了時的逃生路徑

1. 【推論】先把需求改成擁有該判斷的 authority 所發出的 typed outcome event。這是正常分權，不算 escape。
2. 【推論】若是同一 authority 內有限 cases，建立 `DecisionTableSpec`：輸入仍是上述 scalar facts，rows 使用相同 Guard AST，輸出一個 enum；同樣必須 4,096 cells 內互斥完備。這仍是宣告資料，不算 escape。
3. 【推論】若連有限 decision table 都表達不了，MachineSpec admission 先回 `UNSUPPORTED_GUARD`。要嘛升 `nova.guard` 語言版本並替新 primitive 建正負控，要嘛建立**圖上明示**的 `CustomDecisionProducer`：pure deterministic、無 clock／I/O／random，輸入輸出皆有 schema，binary/source digest 固定，輸出 typed event，且有 positive、negative、property、mutation controls。它不能回 edge id，也不能直接寫 aggregate。
4. 【推論】只有產品語義本來就要求人判斷，才可宣告 `AWAITING_HUMAN_DECISION` 節點；它必須有 deadline 與 default typed terminal。不能因 DSL 不夠就偽造一個人類節點。

【推論】`CustomDecisionProducer` 的 v1 硬預算：每份 MachineSpec 最多 **1** 個 active producer revision，全系統 bootstrap catalog 最多 **3** 個；若該 machine 有 `N` 條非終態 edges，依賴 custom output 的 edges 最多 `max(1, floor(N / 5))`。第二個 producer、全域第四個、或 edge count 超式任一成立即 `GUARD_ESCAPE_BUDGET_EXCEEDED`；必須升 Guard 語言或重新切 authority，不能請 reviewer 勾一個 waiver。

【推論】這個數字不是宣稱 3 有自然法則，而是一條 architecture fitness function：三個 lifecycle machine 各容許一個真正特殊的演算法；若每個 machine 都開始長第二個，宣告層已失去可分析性。typed authority event 與可完整證明的 DecisionTableSpec 不計入此額度，因此不會為了躲 count 把 deadline／budget 再塞回 guard。

### 3.6 Guard 的 executable guarantees

| Semantic id | 處置 |
|---|---|
| `machine.guard.closed-ast` | 【推論】新增：所有 arbitrary code／unknown op fixture admission 轉紅。 |
| `machine.guard.partition-total-exclusive` | 【推論】新增：overlap interval、enum hole、unit mismatch、4,097 cells 各有固定紅例與 witness。 |
| `machine.guard.typed-authority-outcome` | 【推論】新增：deadline／budget／selection／fault 只能由釘版 producer event 進 machine。 |
| `machine.guard.custom-decision-budget` | 【推論】新增：1 per machine、3 global、`max(1, floor(N/5))` edges 三條均機械執法。 |
| `machine.runtime.declared-transition-only` | 【推論】修改：compiled GuardPlan digest＋DB composite FK 同時驗非法轉移。 |

---

## 4. CPython 3.14：不是「看起來支援」，是真的跑過

### 4.1 測試環境與版本

【實測】`python3.14` 不在 shell `PATH`，但 `uv 0.12.5` 的 installed interpreter 清單包含 `/Users/sbu/.local/share/uv/python/cpython-3.14-macos-aarch64-none/bin/python3.14`；直接執行得到 **CPython 3.14.7**、Clang 22.1.3。

【實測】實際載入並執行的套件版本為：pytest **9.1.1**、Hypothesis **6.165.10**、pytest-xdist **3.8.0**、execnet **2.1.2**、mutmut **3.7.0**。它們來自本機 uv cache；Hypothesis 使用的 cache bundle 含 CPython 3.14 native extension，並由 3.14.7 實際 import 成功。

【實測】嘗試從 PyPI 建全新環境時，sandbox DNS 阻止連到 `pypi.org`；錯誤發生在抓 pytest metadata，沒有發生 dependency／wheel／Python-version rejection。這次失敗只證明當下網路不可用，不算相容性紅燈，也不拿來冒充 clean-install 綠燈。

### 4.2 真正跑了什麼

【實測】在 `/private/tmp` 建 ephemeral probe：一個三分支 `classify()`、一個 `double()`，一個普通 pytest case，加一個 Hypothesis `@given(st.integers())` property。以 `python3.14 -m pytest -n 2` 啟動兩個 xdist workers，結果為 **2 passed in 3.07s，exit 0**。

【實測】同一 probe 由 `python3.14 -m mutmut run` 做 mutation testing：**1 file mutated、12 mutants generated、12 killed、0 survived／timeout／suspicious，exit 0**；`mutmut results` 也 exit 0。這不是只跑 `--version`。

【實測】mutmut 在 macOS 上印出一個 `os.fork()` from multi-threaded process 的 `DeprecationWarning`，但 generation、forced-fail self-check 與 12 個 mutation 都完成。這是要保留的升版探針，不是本次不相容。

【實測】所有 ephemeral probe 都已刪除；另行建立的 `/private/tmp/nova-py314-probe` 與 `/private/tmp/nova-uv-cache` 也已逐一路徑刪除並確認不存在。repo 沒留下 probe／venv／cache 檔。

### 4.3 版本裁決與不可豁免的反轉條件

【推論】`.python-version` 固定 **3.14.7**，`pyproject.toml` 固定上述四個 direct tool versions，`uv.lock` 固定 transitive versions。不能只寫 `>=3.14`；patch／tool 任一升版都先跑同一 bootstrap probe。

【推論】day-one gate 必須同時證明：pytest 可 collect／execute、Hypothesis 至少跑一個 generated property、xdist 確實啟動兩個 worker、mutation runner 產生至少一個 mutant且 negative control 能殺掉。四者任一非零、hang、無 mutant、或 forced-fail 自檢失效，就立即把 runtime pin 改為本機已具備的 **CPython 3.13.15** 並重鎖；不以 `xfail`、關掉 xdist、拿掉 property 或跳過 mutation 換 3.14。

【推論】mutmut 的 fork warning 若在後續 macOS／Python patch 變成 error、hang 或不可靠結果，就命中同一反轉條件；先釘 3.13，不在 day one 自製 mutation runner。這四項是其他保證的乘數，版本新穎性沒有優先權。

---

## 5. 對第三、四輪定案與目錄樹的必要 diff

【推論】未列路徑不動；以下不是重新設計整棵樹，而是本輪決定必然要求的最小職責變動。

```text
M .python-version                                  — 由 3.14 minor line 收緊為 3.14.7。
M pyproject.toml                                   — pin pytest/Hypothesis/xdist/mutmut 與 day-one probe entry。
M uv.lock                                          — 固定實測相容組合。

規格/
├── 語言/
M   ├── 狀態機.schema.json                         — Guard v1 封閉 AST、limits、FactDef 與 custom budget。
+   ├── 決策表.schema.json                         — 同一 finite proof domain 的 typed input→enum output。
+   └── 事件段.schema.json                         — SegmentManifest、RecoveryCheckpoint 與 retention pin。
├── 資源/
M   ├── 供應商額度.machine.json                    — per-bucket 五態與 probe transition。
+   ├── 額度拓撲.policy.json                       — ALL_OF windows、metric kinds、80%/95%、optional spend channels、300s/60s/15m。
M   └── 保證/                                      — 第 1.4 節列出的 quota claims。
├── 工作/
M   ├── 工作.machine.json                          — 7 天 absolute deadline；PAUSED 仍接受 timer trigger。
    └── 保證/
M       ├── 崩潰重建.claim.json                    — full SQLite history 改 checkpoint＋segments＋suffix。
+       ├── 七天絕對期限.claim.json                — PAUSED 不停鐘；到點 typed terminal。
+       └── 工作事件上限.claim.json                — 第 8,192 terminal reserve 與第 8,193 筆負控。
└── 介面/
M   ├── 事件流.schema.json                         — warm segment／tail cache 透明 cursor continuity。
+   └── 保證/事件分層連續.claim.json               — 90 天內跨層不得漏／改 bytes。

nova/
├── 狀態機/
M   ├── 模型.py                                    — typed facts 與 Guard AST。
M   ├── 檢查.py                                    — 4,096-cell total/exclusive proof 與 escape budget。
M   ├── 編譯.py                                    — canonical GuardPlan／DecisionTablePlan digest。
M   ├── 執行.py                                    — 無 eval 的 total interpreter。
+   └── 決策表.py                                  — finite declarative table；不含 custom code registry。
├── 權威/資源/
M   ├── 額度觀測.py                                — QuotaBucketEvidence 五態與 topology。
M   ├── 資格閘.py                                  — allowed channel、worst-case、probe single-flight。
M   └── 盲派斷路.py                                — 只留給無 observation capability backend。
├── 基礎設施/
│   ├── 狀態庫/sqlite/
+   │   ├── 事件封存.py                            — blob-first／manifest commit／24h bounded prune。
+   │   ├── 復原檢查點.py                          — checkpoint build、verify 與 suffix replay。
+   │   └── 遷移/0006_事件分層與檢查點.sql         — segment manifests、pins、checkpoint refs。
│   ├── 事件流/sqlite/
M   │   ├── 發布器.py                              — 可由 warm segments＋hot suffix backfill。
M   │   └── 尾隨庫.py                              — 7d／2GiB cache，不擁有 90d retention。
+   └── 事件流/分段讀取.py                         — segment→tail 的純 range stream。
└── 介接/執行者後端/
    ├── claude_agent_sdk/額度.py                   — RateLimitEvent→per-bucket evidence。
    └── codex_cli/額度.py                          — token_count.rate_limits→per-bucket evidence。

前端/src/
M ├── 事件流/歸約.ts                               — fold bucket evidence、eligibility 與 segment cursor。
M └── 畫面/後端額度.ts                             — 五態逐 bucket；rolled 不畫成滿額。

驗收/
├── 狀態機/
+ │ ├── test_guard封閉語言.py                      — operator/type/limit 固定反例。
+ │ ├── test_guard互斥完備.py                      — overlap、hole、4,097 cells witness。
+ │ └── test_custom決策預算.py                     — 1／3／max(1,floor(N/5)) 三道硬線。
├── 儲存/
M │ ├── test_envelope.py                           — steady、events/tx、bytes 與一小時 soak 分開。
+ │ ├── test_事件分層.py                           — 24h／90d／365d pins 與 cap 不早刪。
+ │ ├── test_封存崩潰間隙.py                       — blob／manifest／checkpoint／prune 每一縫 SIGKILL。
+ │ └── test_檢查點重播.py                         — checkpoint＋suffix＝genesis replay。
+├── 資源/test_供應商額度五態.py                   — multi-bucket、cold、stale、rollover、other-client 反例。
M ├── 三層流程/test_一定停止.py                    — PAUSED 跨 7 天與 8,192 terminal reserve 都不能留非終態。
M └── 前端契約/test_額度與政策.py                  — rolled 不冒充 full；per-bucket pure fold。

工具/
+└── 驗工具鏈.py                                  — 四項 3.14.7 bootstrap probe；任一失敗整體非零。
```

【推論】`0006` 延續第四輪已預留的 `0005_約束與額度斷路.sql`；不回頭改已發布 migration。事件 segment bytes 仍走既有內容庫 port，沒有新增第五個 authority 或第二個 mutable catalog。

【推論】中文檔名結論不變：source path 與 Python identifier 可用中文且本機 3.14 實測不構成阻礙；跨程序 semantic id、event／schema field、DB table／column、CLI executable 與外部 protocol 仍用 ASCII。Guard operator 與 failure code 也必須是 ASCII stable identity。

---

## 6. 最終一致性檢查與簽字

| 檢查 | 結果 |
|---|---|
| 還有未決嗎 | 【推論】0。所有 fallback、數值、上限、狀態、retention、escape count 與 Python fallback 都有單一值。 |
| SQLite 還合理嗎 | 【推論】是。50 tx/s 是一小時 selection soak，production steady 0.5 tx/s；歷史離開 hot DB 後，single-owner／rollback 的前提反而更乾淨。 |
| UI 純事件 fold 被破壞嗎 | 【推論】沒有。application event-stream port 透明串 warm segments＋tail cache；UI 不向 domain 查 head／checkpoint。 |
| 「日誌是唯一來源」被 checkpoint 破壞嗎 | 【推論】沒有。checkpoint 是帶 source cursor／fold digest 的可驗衍生物；logical log 是 hot range＋manifested immutable segments，checkpoint 可刪後重建。 |
| 五態會捏造額度嗎 | 【推論】不會。rollover 只取得 probe eligibility，不取得 remaining；per-bucket evidence 與 ResourcePolicy 分開。 |
| Guard 還是純宣告嗎 | 【推論】是。Guard／edge 本身無 callback；custom producer 是圖上另一個 typed node、有獨立 owner／ClaimSpec／硬預算，不能回 edge 或寫 state。 |
| Python 3.14 是未驗選型嗎 | 【實測】不是。四項工具已在 3.14.7 真正執行；反轉到 3.13.15 的非豁免條件已固定。 |

【推論】相依決定只有三組，之後改一個必須連動：`steady event rate × bytes × retention ↔ tier capacity／admission`；`quota evidence state ↔ ResourcePolicy channel ↔ UI wording／probe gate`；`Guard grammar ↔ proof algorithm ↔ custom producer budget`。任何一組只改文件中的一格，都應由 impact checker 轉紅。

【推論】最可能在第一個實作被打臉的順序現在是：SQLite 實際 page amplification 是否高於 4 KiB/event、Claude 是否每次新 session 都能及時送出完整 bucket snapshot、checkpoint seal/prune crash matrix 是否能在 60 秒 recovery SLO 內完成、mutmut 的 macOS fork warning 是否在下一個 patch 變成失敗。它們都已有淘汰／降級路徑，不再是未決：前兩者分別命中容量 maintenance 或 single-flight probe；第三者不啟用 prune；第四者釘 3.13.15。

【推論】設計審查方簽字：**同意上述 v1 baseline，2026-08-26。** 依使用者方在本輪第五節明示的簽字條件，五條已逐一滿足；雙方定案完成，下一步可以直接按 quota evidence、event tiering／recovery、Guard compiler、toolchain bootstrap 四個可獨立測試子系統進 spec 與 writing-plans，不需要再補一輪語義裁決。
