#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""計畫集的機械複驗閘。

存在理由：2026-08-27 控制端對 21 份計畫做複驗，先用讀的找不到破綻，改用交叉比對才
確認不變式成立。此後任何人改計畫（含插入 01B、擴充 05/07/13/14/20）都必須讓它們
仍然成立——讀不出來的東西，算得出來。

十一項不變式（下面逐條列出；I6 的說明在負控段）：
  I1 檔案所有權   同一路徑不得被兩份計畫 Create；Modify 的對象必須有人 Create。
  I2 依賴無環     Dependency Gate 構成的圖不得有多節點 SCC。
  I3 編號即拓撲序 沒有計畫依賴編號比自己大的計畫（否則照編號執行會違反依賴閘）。
  I4 任務完整性   每個 task 都要有 ClaimSpec、固定負控、先紅步、commit 步。
  I5 修改方向     Modify 的對象必須由自己或**遞移**前置計畫 Create——否則就是一條沒有
                  宣告的隱含依賴，照宣告的順序執行時那個檔案還不存在。用遞移閉包而不是
                  直接邊：14 沒有直接宣告 01，但它宣告了 01B 而 01B 依賴 01。
  I10 宣告與落點  每個已遷移 task 的 `**ClaimSpec落點:**` 行，id 集合必須與 `**ClaimSpec:**`
                  行逐字相等；每個 id 恰對一條 `規格/**/*.claim.json`，該路徑必須由本 task 或
                  更早（同計畫更前面的 task／遞移前置計畫）Create；全域一對一。
                  未遷移的 task 數必須等於檔裡寫死的 baseline——多了紅，**少了也紅**。
                  它**抓不到配錯人**：把兩個 id 的路徑對調，兩邊都存在也都一對一，I10 全綠。
                  那要靠打開 .claim.json 比對 claim_id 的另一道閘（尚未建立）。
  I11 檔內id相符 每一份**實際存在**的 `規格/**/*.claim.json`，其 `claim_id` 欄位必須等於
                  I10 綁定表指名該路徑的那個 id；沒有任何綁定行指名它的 claim 檔是孤兒；
                  兩份檔用同一個 claim_id 也紅。
                  這是 I10 抓不到的那一半——**I10 只看計畫文字，永遠抓不到配錯人**：
                  把兩個 id 的路徑對調，兩邊都存在也都一對一，I10 全綠。I11 是唯一會打開
                  `.claim.json` 的閘。它今天就非空：七份實存檔都被檢查。
  I8 命名可通過   計畫在 code fence 裡宣告的 def／class 名，必須通過 `架構/檢查工程規範.py`
                  的識別字閘（NFC＋NFKC＋每個 `_` 段單一 script）。計畫宣告一個自家閘會判紅
                  的名字，實作者照著寫就撞紅，最可能的反應是**放寬閘**——那正好毀掉閘。
                  實測一次掃出 30 個（全在 01–04，後面的計畫用散文寫測試名）。
  I9 訊息用中文   每個 task 的 `git commit -m` 訊息必須含漢字。CLAUDE.md 最高原則第 2 條要求
                  commit message 一律繁體中文，而計畫原本 177 條裡有 176 條是英文——
                  Tasks 1-4 的實作者都默默照 CLAUDE.md 走而偏離計畫文字，那正是
                  「規範只活在文件裡」的形狀。conventional-commit 的型別前綴
                  （feat:／test:／build:／perf:）保持 ASCII，它是跨工具的 semantic id。
  I7 引用可解析   `Run:` 指令引用的檔案必須在該 task 或更早被 Create；File Structure
                  宣告的檔案必須有人 Create。I1 只查 Create/Modify 條目的所有權，
                  查不到指令引用——實測一次掃出 22 處。

負控（改壞任一項應轉紅）：
  I1 → 把某個 Create 路徑複製到另一份計畫。
  I2 → 讓兩份計畫互相宣告前置。
  I3 → 讓 05 宣告依賴 09。
  I4 → 刪掉任一 task 的「**固定負控:**」段。
  I5 → 讓 05 去 Modify 一個由 14 Create 的檔案。
  I7 → 把任一 Run: 指令的檔名改掉一個字，或從 File Structure 挑一個檔刪掉它的 Create 條目。
  I8 → 把任一 `def test_x_中文` 的底線刪掉，變成 `def test_x中文`。
  I9 → 把任一 commit 訊息改回英文。
  I11 → 把任一份 claim 檔的 `claim_id` 改掉一個字元；把兩份檔改成同一個 claim_id；
         把某個 id 的落點路徑與另一個 id 的對調（**這條 I10 抓不到，I11 才抓得到**）。
  I10 → ①刪掉某已遷移 task 的落點行而不動 baseline；②把某 id 的路徑改一個字指到沒人 Create 的檔；
        ③把兩個 id 指到同一條路徑；④落點行少寫一個 id；⑤把某 id 指到更晚的 task 才 Create 的檔。
  I6 → 把兩個 task 併成一個（commit 步會變成兩個）；把任一 task 標題序號改成
       與位置不符（撞號或跳號）。
       **回歸負控要長期存在**：真實撞號（08 曾同時出現兩個「Task 9」）的最小壞檔應固定在
       執法器自己的 fixture 裡，不能只靠某次跑在暫存目錄的複本——否則這項檢查
       套用後就只剩程式碼、沒有長期牙齒。
       註：ClaimSpec 上限 2 抓不到 1+1 合併（併完剛好是 2，仍在上限內），
       所以偵測合併靠的是 commit 步那條——每個 task 都恰好一次 commit。

exit 0 全過；非零＝有不變式不成立，逐條明講。
"""
import re, sys, glob, os, json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from 架構.檢查工程規範 import 字的_script, 載入規則  # noqa: E402

根 = (sys.argv[1] if len(sys.argv) > 1
     else os.path.join(os.path.dirname(os.path.abspath(__file__)), '計畫'))
失敗 = []


def 重置():
    失敗.clear()


def 計畫檔():
    檔 = sorted(f for f in glob.glob(os.path.join(根, '*.md'))
                if re.match(r'^\d\d[A-Z]?-', os.path.basename(f)))
    return [f for f in 檔 if not os.path.basename(f).startswith('00-')]


def 編號(路徑):
    return re.match(r'^(\d\d[A-Z]?)-', os.path.basename(路徑)).group(1)


def 閉包(邊):
    """遞移閉包。依賴是可遞移的，只比對直接邊會誤報。"""
    c = {n: set(ws) for n, ws in 邊.items()}
    變 = True
    while 變:
        變 = False
        for n in c:
            新 = set(c[n])
            for w in c[n]:
                新 |= c.get(w, set())
            if 新 != c[n]:
                c[n] = 新; 變 = True
    return c


def i1_i5_檔案所有權(檔, 邊=None):
    全 = 閉包(邊) if 邊 is not None else None
    建, 改 = {}, {}
    for f in 檔:
        n = 編號(f)
        for 動作, 路徑 in re.findall(r'^\s*-\s*(Create|Modify):\s*`([^`]+)`',
                                     open(f, encoding='utf-8').read(), re.M):
            (建 if 動作 == 'Create' else 改).setdefault(路徑, set()).add(n)
    for 路徑, ns in sorted(建.items()):
        if len(ns) > 1:
            失敗.append(f'I1 雙重 Create：{路徑} ← {sorted(ns)}')
    for 路徑 in sorted(改):
        if 路徑 not in 建:
            失敗.append(f'I1 懸空 Modify：{路徑} ← {sorted(改[路徑])}')
        elif 全 is not None:
            擁有 = next(iter(建[路徑]))
            for 改者 in sorted(改[路徑]):
                if 改者 != 擁有 and 擁有 not in 全.get(改者, set()):
                    失敗.append(
                        f'I5 未宣告的隱含依賴：{改者} 修改 {路徑}，'
                        f'但該檔由 {擁有} 建立而 {改者} 的前置沒有 {擁有}')
    return len(建)


def 前置(f):
    """只讀機器可讀的『前置計畫：』宣告，不解析散文。

    為什麼：第一版解析 Dependency Gate 的散文，兩個方向都錯——「必須完成plan 05–07、
    11–13」不匹配動詞清單而少報，計畫 14 散文裡「plan 11 提供…但本 adapter v1 不提供
    它」被誤當前置而多報。少報會讓 I3 空過，多報會誤判順序違反。散文給人讀，宣告給機器讀。
    """
    s = open(f, encoding='utf-8').read()
    m = re.search(r'^前置計畫：(.+)$', s, re.M)
    if not m:
        失敗.append(f'I2 缺「前置計畫：」宣告：{os.path.basename(f)}')
        return set()
    值 = m.group(1).strip()
    if 值 == '無':
        return set()
    項 = re.findall(r'\d\d[A-Z]?', 值)
    if not 項 or ''.join(項) != re.sub(r'\s+', '', 值):
        失敗.append(f'I2 「前置計畫：」格式不合：{os.path.basename(f)} → {值!r}')
        return set()
    return set(項) - {編號(f)}


def i2_i3_依賴(檔):
    邊 = {編號(f): sorted(前置(f)) for f in 檔}
    有效 = set(邊)
    for n, ws in 邊.items():
        for w in ws:
            if w not in 有效:
                失敗.append(f'I2 {n} 宣告的前置 {w} 不存在')
    # Tarjan SCC：找環要跑 SCC，不是列已知的邊
    idx, low, on, st, c, = {}, {}, {}, [], [0]
    def 走(v):
        idx[v] = low[v] = c[0]; c[0] += 1; st.append(v); on[v] = True
        for w in 邊.get(v, []):
            if w not in 有效: continue
            if w not in idx:
                走(w); low[v] = min(low[v], low[w])
            elif on.get(w):
                low[v] = min(low[v], idx[w])
        if low[v] == idx[v]:
            comp = []
            while True:
                w = st.pop(); on[w] = False; comp.append(w)
                if w == v: break
            if len(comp) > 1:
                失敗.append(f'I2 依賴環：{sorted(comp)}')
    for v in 邊:
        if v not in idx: 走(v)
    for n, ws in 邊.items():
        for w in ws:
            if w in 有效 and 序位(w) >= 序位(n):
                失敗.append(f'I3 順序違反：{n} 依賴編號較大的 {w}')
    return 邊


def 序位(n):
    """01B 夾在 01 與 02 之間；字典序剛好正確，但寫明比依賴巧合安全。"""
    return (int(n[:2]), n[2:] or '')


def i6_任務口徑(檔, 上限條=2, 上限檔=10):
    """一個 task 至多 2 條 ClaimSpec、至多 10 個檔。

    第一版只讀每個 task 的**第一個** `**ClaimSpec:**` 區塊，於是「把兩個 task
    併成一個」完全抓不到——負控用差異法才驗出來（直接看 exit code 會誤判成通過，
    因為基線本來就有 14 條別的違規）。現在數的是 task 內**所有** ClaimSpec 區塊。
    """
    for f in 檔:
        s = open(f, encoding='utf-8').read()
        for i, b in enumerate(re.split(r'^### Task ', s, flags=re.M)[1:], 1):
            名 = f'{編號(f)}-Task{i}'
            # 標題序號必須等於出現位置：R11 實測 08 出現兩個「Task 9」（R8 套用改號後，
            # R9 的 diff 仍寫舊號、逐字套用），本檢查之前完全不看標題數字，撞號不紅。
            標題號 = re.match(r'(\d+)\s*:', b)
            if not 標題號 or int(標題號.group(1)) != i:
                失敗.append(f'I6 task 標題序號與位置不符：{名} 的標題寫 Task '
                            f'{標題號.group(1) if 標題號 else "?"}（撞號或跳號）')
            區 = re.findall(r'\*\*ClaimSpec:\*\*(.+?)(?:\n\n|\*\*固定負控)', b, re.S)
            條 = set()
            for x in 區:
                條 |= set(re.findall(r'`([a-z][a-z0-9]*(?:[.\-][a-z0-9\-]+){2,6})`', x))
            # 沒有具名 id 時退回用區塊數計，否則「一個 task 兩段 ClaimSpec」會漏
            量 = max(len(條), len(區))
            if 量 > 上限條:
                失敗.append(f'I6 一個 task 宣稱 {量} 條 ClaimSpec（上限 {上限條}）：{名}')
            c = len(re.findall(r'git commit', b))
            if c != 1:
                失敗.append(f'I6 一個 task 有 {c} 個 commit 步（應恰好 1）：{名}')
            檔數 = len(re.findall(r'^\s*-\s*(?:Create|Modify):', b, re.M))
            if 檔數 > 上限檔:
                失敗.append(f'I6 一個 task 動 {檔數} 個檔（上限 {上限檔}）：{名}')


def i7_引用可解析(檔):
    """Run: 引用的檔案必須在該 task 或更早被 Create；File Structure 宣告的必須有人 Create。

    為什麼：I1 只查 Create/Modify 條目彼此的所有權，不查**指令引用**。2026-08-27 手掃
    一次抓到 22 處：4 處引用尚未建立的檔（真順序問題）、10 處引用整份計畫從未 Create 過
    的檔（改名沒跟上）、8 處 File Structure 宣告了卻沒有任何 task 建立。

    第二類最貴：實作者跑到 `pytest 某個不存在的檔` 會得到 file not found，最可能的反應是
    「大概改名了」自己挑一個看起來對的檔跑——那道檢查就**靜默消失，而且不會有任何紅**。
    這正是本 repo 最痛恨的形狀：宣稱有把關而沒有。
    """
    路徑樣式 = re.compile(r'(?:nova|規格|驗收|前端|工具|架構)/[^\s`\'"()、，。：]+')
    樹字 = set("│├└─ ")
    全建 = set()
    for f in 檔:
        全建 |= set(re.findall(r'^- Create: `([^`]+)`', open(f, encoding='utf-8').read(), re.M))

    已存在 = set()
    for f in sorted(檔, key=lambda x: 序位(編號(x))):
        s = open(f, encoding='utf-8').read()
        for i, b in enumerate(re.split(r'^### Task \d+:', s, flags=re.M)[1:], 1):
            名 = f'{編號(f)}-Task{i}'
            本 = set(re.findall(r'^- (?:Create|Modify): `([^`]+)`', b, re.M))
            引用 = set()
            for 行 in re.findall(r'^Run:\s*`([^`]+)`', b, re.M):
                引用 |= {p.split('::')[0].rstrip('/') for p in 路徑樣式.findall(行)}
            for p in sorted(引用):
                if p in 已存在 or p in 本: continue
                if any(x.startswith(p + '/') for x in 已存在 | 本): continue
                因 = '該檔在後面的 task 才 Create' if (p in 全建 or any(
                    x.startswith(p + '/') for x in 全建)) else '整份計畫從未 Create 過這個檔'
                失敗.append(f'I7 {名} 的 Run 引用了不存在的 {p}（{因}）')
            已存在 |= set(re.findall(r'^- Create: `([^`]+)`', b, re.M))

        m = re.search(r'## File Structure\s*```text\n(.*?)```', s, re.S)
        if not m: continue
        堆 = []
        for 行 in m.group(1).splitlines():
            j = 0
            while j < len(行) and 行[j] in 樹字: j += 1
            if j >= len(行): continue
            深, 名2 = j // 4, 行[j:].split('—')[0].strip()
            if not 名2: continue
            if 名2.endswith('/'):
                堆 = 堆[:深] + [名2]; continue
            路徑 = ''.join(堆[:深]) + 名2
            if '*' in 路徑 or not re.match(
                    r'^(nova|規格|驗收|前端|工具|架構)/.+\.\w+$', 路徑): continue
            if 路徑 not in 全建:
                失敗.append(f'I7 {編號(f)} 的 File Structure 宣告了 {路徑} 但沒有任何 task Create')


def i9_訊息用中文(檔):
    """commit 訊息必須含漢字。判準是「有沒有漢字」而不是「有沒有非 ASCII」——

    後者會把 emoji、法文重音符號都算成通過。漢字判定與命名閘共用 字的_script。
    """
    訊息 = re.compile(r'git commit -m "([^"]+)"')
    for f in 檔:
        for i, m in enumerate(訊息.findall(open(f, encoding='utf-8').read()), 1):
            if not any(字的_script(c) == 'HAN' for c in m):
                失敗.append(f'I9 {編號(f)} 第 {i} 條 commit 訊息沒有中文：{m}')


BINDING_ID白名單 = frozenset({'execution-envelope.reference', 'execution-envelope.production'})
未遷移基線 = 130  # R12-01 給 12 Task 9 補落點行後自 131 減一  # R4-01 給 09 Task 4、R4-02 給 05 Task 7 各補落點行後自 133 減二；新開 task 全帶落點行不計入
ID樣式 = re.compile(r'^[a-z][a-z0-9]*(?:[.-][a-z0-9]+)+$')


def 宣告的_id(區):
    """從 `**ClaimSpec:**` 行取 claim id。反引號裡也會出現 binding id、failure code
    與萬用字元，全部不是 claim id——實測 210 個 token 裡有 6 個不是。"""
    m = re.search(r'\*\*ClaimSpec:\*\*(.*)', 區)
    if not m:
        return set()
    return {t for t in re.findall(r'`([^`]+)`', m.group(1))
            if ID樣式.match(t) and t not in BINDING_ID白名單}


def i10_宣告與落點一對一(檔, 邊):
    """claim id 與 .claim.json 路徑的綁定，在計畫層第一次變成可機械查核的東西。

    存在理由：2026-08-27 量到 204 個宣告的 claim id 只有 139 份 Create 的 .claim.json，
    至少 65 個 id 沒有檔可以住。但當時**寫不出誠實的閘**——實測全 21 份計畫裡，
    同一行同時出現 claim 檔路徑與已宣告 claim id 的行數是 **0**：檔名是中文語意名，
    id 是 ASCII，綁定只存在於檔案內部的 claim_id 欄位，而 139 份裡只有 3 份真的存在。
    於是任何「claim 有落點」的閘都只能退化成「這個 task 有沒有 Create 至少一份 claim 檔」，
    而那對 20 個建 ≥2 份檔的 task 刪掉一份仍然全綠——一道抓不到自己成立理由的閘就是恆真格。

    所以先讓計畫把綁定寫出來（新增一行，舊的宣告行一個字不改），再談補哪 65 份檔。
    新增而不改舊行還買到一件事：兩行的 id 集合必須逐字相等，抄錯一個 id 閘自己會抓到。
    """
    建於 = {}
    for f in 檔:
        n = 編號(f)
        for i, b in enumerate(re.split(r'^### Task ', open(f, encoding='utf-8').read(), flags=re.M)[1:], 1):
            for 路徑 in re.findall(r'^\s*-\s*Create:\s*`([^`]+)`', b, re.M):
                建於.setdefault(路徑, (n, i))
    全 = 閉包(邊)
    id對路徑, 路徑對id, 未遷移 = {}, {}, []
    for f in sorted(檔, key=lambda x: 序位(編號(x))):
        n = 編號(f)
        for i, b in enumerate(re.split(r'^### Task ', open(f, encoding='utf-8').read(), flags=re.M)[1:], 1):
            名 = f'{n}-Task{i}'
            m = re.search(r'^\*\*ClaimSpec落點:\*\*(.*?)(?=\n\s*\n)', b, re.S | re.M)
            if not m:
                未遷移.append(名)
                continue
            對 = re.findall(r'`([^`]+)`\s*→\s*`([^`]+)`', m.group(1))
            落 = {}
            for i2, (鍵, 路徑) in enumerate(對):
                if 鍵 in 落:
                    失敗.append(f'I10 {名} 的落點行把 {鍵} 指了兩條路徑')
                落[鍵] = 路徑
            if 落.keys() != 宣告的_id(b):
                失敗.append(f'I10 {名} 落點行的 id 集合與宣告行不符：'
                            f'落點 {sorted(落)} vs 宣告 {sorted(宣告的_id(b))}')
            for 鍵, 路徑 in 落.items():
                if not re.match(r'^規格/.+\.claim\.json$', 路徑):
                    失敗.append(f'I10 {名} 的 {鍵} 指到不是 claim 檔的路徑：{路徑}')
                    continue
                if 路徑 not in 建於:
                    失敗.append(f'I10 {名} 的 {鍵} 指到沒有任何 task Create 的 {路徑}')
                    continue
                擁計畫, 擁task = 建於[路徑]
                太晚 = (擁計畫 == n and 擁task > i) or (
                    擁計畫 != n and 擁計畫 not in 全.get(n, set()))
                if 太晚:
                    失敗.append(f'I10 {名} 的 {鍵} 指到 {擁計畫}-Task{擁task} 才 Create 的 {路徑}')
                if 鍵 in id對路徑 and id對路徑[鍵] != 路徑:
                    失敗.append(f'I10 {鍵} 被指到兩條路徑：{id對路徑[鍵]} 與 {路徑}')
                if 路徑 in 路徑對id and 路徑對id[路徑] != 鍵:
                    失敗.append(f'I10 {路徑} 被兩個 id 指名：{路徑對id[路徑]} 與 {鍵}')
                id對路徑[鍵] = 路徑
                路徑對id[路徑] = 鍵
    if len(未遷移) != 未遷移基線:
        失敗.append(f'I10 未遷移 {len(未遷移)} 個 task，baseline 寫的是 {未遷移基線}'
                    f'——多了要補落點行，少了要把 baseline 改小')
    return len(未遷移), 路徑對id


def i11_檔內id相符(綁定):
    """打開每一份實存的 claim 檔，比對它的 claim_id 與計畫綁定表。

    存在理由：I10 只讀計畫文字。把兩個 id 的落點路徑對調，兩份檔都存在、都一對一，
    I10 全綠——它結構上抓不到「配錯人」。只做 I10 就是把「宣稱有把關」從 id 層搬到路徑層。

    這支是唯一會打開 `.claim.json` 的閘，也是唯一能抓到配錯人的東西。
    """
    根目錄 = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    見過 = {}
    for 路徑 in sorted(glob.glob(os.path.join(根目錄, '規格', '**', '*.claim.json'), recursive=True)):
        相對 = os.path.relpath(路徑, 根目錄)
        try:
            內 = json.loads(open(路徑, encoding='utf-8').read())
        except json.JSONDecodeError as 誤:
            失敗.append(f'I11 {相對} 不是合法 JSON：{誤}')
            continue
        實 = 內.get('claim_id')
        期 = 綁定.get(相對)
        if 期 is None:
            失敗.append(f'I11 {相對} 是孤兒：沒有任何 task 的落點行指名它'
                        f'（它自稱 {實}）')
        elif 實 != 期:
            失敗.append(f'I11 {相對} 檔內 claim_id 是 {實}，但計畫綁定表說它該裝 {期}')
        if 實 in 見過:
            失敗.append(f'I11 claim_id {實} 出現在兩份檔：{見過[實]} 與 {相對}')
        見過[實] = 相對
    return len(見過)


def i8_命名可通過(檔):
    """計畫自己宣告的識別字必須通過命名閘——規則與 checker 共用同一支，不重寫一份。

    存在理由：Task 4 建好識別字閘後，01–04 的 code fence 裡有 30 個 `def` 名
    （`test_相同bytes同ref` 這種）在同一個 `_` 段裡黏 Latin 與 Han，正是閘要擋的形狀。
    計畫要求實作者寫出自家閘會判紅的名字，實作者最省事的出路是把閘改鬆。
    """
    分隔 = 載入規則().段分隔
    宣告 = re.compile(r'^\s*(?:def|class)\s+([^\s(:]+)', re.M)
    for f in 檔:
        for 名 in 宣告.findall(open(f, encoding='utf-8').read()):
            for 段 in 名.split(分隔):
                if len({字的_script(c) for c in 段} - {'NEUTRAL'}) > 1:
                    失敗.append(f'I8 {編號(f)} 宣告了黏寫的識別字 {名}（段 {段}）')
                    break


def i13_task引用可解析(檔):
    """跨計畫與計畫內的 `Task N` 引用必須指得到真的存在的 task。

    **只驗 resolvable，不驗 semantically correct。** 改號之後「指錯但仍在範圍內」
    的引用（resolvable-but-wrong）這條抓不到——那種只能靠人工逐處判歸屬。
    I13 綠**不等於**引用都對，別這樣讀。

    存在理由：T12 拆分要整體改號 12→13…19→20，而**沒有任何不變式管 task 之間的
    文字引用**（I6 只管標題序號與位置，I7 只管 `Run:` 與 File Structure）。
    改錯不會紅。實測當時的規模：跨計畫引用 4 處、01 內部 `Task 1[2-9]` 26 處。

    **認得的引用形式全集**（其餘形式一律漏報，明講）：

        跨計畫   `01 Task 15`、`plan 01 Task 1`、`計畫 08 Task 4`、`15 的 Task 8`
        計畫內   裸 `Task 12`、`Tasks 3`

    **這份全集是逐條列舉語料得來的，不是猜的。** 我第一版只測了以 `01` 開頭的樣式，
    報「跨計畫引用只有 4 處」——實際是 **16 處、四種寫法**。
    那是「全集來源太窄」在本檔的第一次發作，而且它**不只漏報**：
    未認得的跨計畫形式會被下面裸 `Task N` 那條當成「本計畫的引用」再誤判一次，
    **變成誤報**（`16:313` 的 `15 的 Task 8` 就是這樣被報成「16 只有 7 個 task」）。

    不支援的形式（實測零命中）：`01 T15`、`01-可執行保證語言.md ... Task 15`。
    哪天有人這樣寫，I13 看不見——**漏報比誤報糟**，新增形式要連同 fixture 一起加。

    計畫識別沿用正式文法 `NN` 加選用大寫後綴（正則 ``\\d\\d[A-Z]?``），涵蓋 `01B`、`06B`；否則後綴計畫是系統性盲區。
    先辨識並排除跨計畫引用的 span，再檢查裸 `Task N`——不然 `01 Task 15` 會被
    當成「本計畫的 Task 15」再誤判一次。
    """
    任務數 = {}
    for f in 檔:
        任務數[編號(f)] = len(re.split(r'^### Task ', open(f, encoding='utf-8').read(), flags=re.M)[1:])

    跨 = re.compile(r'(?:(?:計畫|plan)\s*)?(\d\d[A-Z]?)\s*(?:的)?\s*Tasks?\s*(\d+)')
    內 = re.compile(r'Tasks?\s+(\d+)')

    for f in 檔:
        我 = 編號(f)
        s = open(f, encoding='utf-8').read()
        遮蔽 = []
        for m in 跨.finditer(s):
            他, n = m.group(1), int(m.group(2))
            遮蔽.append(m.span())
            if 他 not in 任務數:
                失敗.append(f'I13 {我} 引用了不存在的計畫 {他}（`{m.group(0)}`）')
            elif not 1 <= n <= 任務數[他]:
                失敗.append(f'I13 {我} 的 `{m.group(0)}` 指到計畫 {他} 的 Task {n}，'
                            f'但該計畫只有 {任務數[他]} 個 task')
        for m in 內.finditer(s):
            if any(a <= m.start() < b for a, b in 遮蔽):
                continue
            n = int(m.group(1))
            if not 1 <= n <= 任務數[我]:
                失敗.append(f'I13 {我} 的裸 `{m.group(0)}` 超出範圍：'
                            f'本計畫只有 {任務數[我]} 個 task')


def i4_任務完整(檔):
    總 = 0
    for f in 檔:
        for b in re.split(r'^### Task ', open(f, encoding='utf-8').read(), flags=re.M)[1:]:
            總 += 1
            名 = f'{編號(f)}-Task{b.split(":")[0].strip()}'
            if not re.search(r'\*\*ClaimSpec:\*\*', b):
                失敗.append(f'I4 缺 ClaimSpec：{名}')
            if not re.search(r'\*\*固定負控:\*\*', b):
                失敗.append(f'I4 缺固定負控：{名}')
            if not re.search(r'Expected:[^\n]*(FAIL|紅|red|non-zero|錯誤接受)', b, re.I):
                失敗.append(f'I4 缺先紅步：{名}')
            if not re.search(r'git commit', b):
                失敗.append(f'I4 缺 commit 步：{名}')
    return 總


def 自測():
    """對 docs/計畫複驗自測/<情境>/ 逐一跑本執法器，斷言非零且輸出含 預期.txt 的字串。

    存在理由（R11 實測）：真撞號修好之後，「執法器抓得到撞號」就只剩程式碼、沒有長期
    牙齒——負控 fixture 不能只活在暫存目錄。fixture 只保證目標訊息出現；
    其他不變式在最小 fixture 上本來就會紅（如 I10 基線），不計。"""
    import subprocess
    根目錄 = os.path.dirname(os.path.abspath(__file__))
    自測根 = os.path.join(根目錄, '計畫複驗自測')
    情境們 = sorted(d for d in glob.glob(os.path.join(自測根, '*')) if os.path.isdir(d))
    if not 情境們:
        print('自測：找不到任何情境目錄', file=sys.stderr); return 2
    壞 = 0
    for 情境 in 情境們:
        預期 = open(os.path.join(情境, '預期.txt'), encoding='utf-8').read().strip()
        跑 = subprocess.run([sys.executable, os.path.abspath(__file__), 情境],
                            capture_output=True, text=True)
        中 = 預期 in (跑.stdout + 跑.stderr)
        if 跑.returncode == 0 or not 中:
            壞 += 1
            print(f'自測 ✗ {os.path.basename(情境)}：exit={跑.returncode}，'
                  f'預期字串{"有" if 中 else "沒"}出現')
        else:
            print(f'自測 ✓ {os.path.basename(情境)}：非零且含「{預期}」')
    return 1 if 壞 else 0


def main():
    if sys.argv[1:] == ['--自測']:
        return 自測()
    檔 = 計畫檔()
    if not 檔:
        print('找不到計畫檔', file=sys.stderr); return 2
    邊 = i2_i3_依賴(檔)
    建數 = i1_i5_檔案所有權(檔, 邊)
    任務數 = i4_任務完整(檔)
    i6_任務口徑(檔)
    i7_引用可解析(檔)
    i8_命名可通過(檔)
    i9_訊息用中文(檔)
    i13_task引用可解析(檔)
    未遷移, 綁定 = i10_宣告與落點一對一(檔, 邊)
    實存claim = i11_檔內id相符(綁定)
    print(f'計畫 {len(檔)} 份 · Create 路徑 {建數} 個 · task {任務數} 個 · ClaimSpec 落點未遷移 {未遷移} 個 · 實存 claim 檔 {實存claim} 份')
    for n in sorted(邊):
        print(f'  {n} ← {邊[n] or "（無前置）"}')
    if 失敗:
        print(f'\n不變式不成立（{len(失敗)}）：')
        for x in 失敗: print(f'  ✗ {x}')
        return 1
    print('\nI1 檔案所有權 · I2 依賴無環 · I3 編號即拓撲序 · I4 任務完整 · I5 修改方向 · I6 任務口徑 · I7 引用可解析 · I8 命名可通過 · I9 訊息用中文 · I10 宣告與落點一對一 · I11 檔內id相符 · I13 task引用可解析　全部成立')
    return 0


if __name__ == '__main__':
    sys.exit(main())
