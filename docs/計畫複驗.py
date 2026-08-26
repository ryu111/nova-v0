#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""計畫集的機械複驗閘。

存在理由：2026-08-27 控制端對 21 份計畫做複驗，先用讀的找不到破綻，改用交叉比對才
確認四項不變式成立。此後任何人改計畫（含插入 01B、擴充 05/07/13/14/20）都必須讓這
四項仍然成立——讀不出來的東西，算得出來。

四項不變式：
  I1 檔案所有權   同一路徑不得被兩份計畫 Create；Modify 的對象必須有人 Create。
  I2 依賴無環     Dependency Gate 構成的圖不得有多節點 SCC。
  I3 編號即拓撲序 沒有計畫依賴編號比自己大的計畫（否則照編號執行會違反依賴閘）。
  I4 任務完整性   每個 task 都要有 ClaimSpec、固定負控、先紅步、commit 步。
  I5 修改方向     Modify 的對象必須由自己或**遞移**前置計畫 Create——否則就是一條沒有
                  宣告的隱含依賴，照宣告的順序執行時那個檔案還不存在。用遞移閉包而不是
                  直接邊：14 沒有直接宣告 01，但它宣告了 01B 而 01B 依賴 01。

負控（改壞任一項應轉紅）：
  I1 → 把某個 Create 路徑複製到另一份計畫。
  I2 → 讓兩份計畫互相宣告前置。
  I3 → 讓 05 宣告依賴 09。
  I4 → 刪掉任一 task 的「**固定負控:**」段。
  I5 → 讓 05 去 Modify 一個由 14 Create 的檔案。
  I6 → 把兩個 task 併成一個（commit 步會變成兩個）。
       註：ClaimSpec 上限 2 抓不到 1+1 合併（併完剛好是 2，仍在上限內），
       所以偵測合併靠的是 commit 步那條——164/164 個 task 都恰好一次 commit。

exit 0 全過；非零＝有不變式不成立，逐條明講。
"""
import re, sys, glob, os

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


def main():
    檔 = 計畫檔()
    if not 檔:
        print('找不到計畫檔', file=sys.stderr); return 2
    邊 = i2_i3_依賴(檔)
    建數 = i1_i5_檔案所有權(檔, 邊)
    任務數 = i4_任務完整(檔)
    i6_任務口徑(檔)
    print(f'計畫 {len(檔)} 份 · Create 路徑 {建數} 個 · task {任務數} 個')
    for n in sorted(邊):
        print(f'  {n} ← {邊[n] or "（無前置）"}')
    if 失敗:
        print(f'\n不變式不成立（{len(失敗)}）：')
        for x in 失敗: print(f'  ✗ {x}')
        return 1
    print('\nI1 檔案所有權 · I2 依賴無環 · I3 編號即拓撲序 · I4 任務完整 · I5 修改方向 · I6 任務口徑　全部成立')
    return 0


if __name__ == '__main__':
    sys.exit(main())
