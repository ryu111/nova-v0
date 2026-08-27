"""事前固定的錯誤 subject：一個識別字裡混用 Latin 與 Han。

宣稱落點: nova/核心/狀態旗標.py

`claim狀態` 把 ASCII 的 claim 與漢字的 狀態 黏在同一個 lexical segment 裡。
Python 解析時做 NFKC 正規化，同形異碼與規約漂移會讓「看起來同名」的兩個識別字
在 import graph 上是兩個東西。checker 必須回 MIXED_SCRIPT_IDENTIFIER。

同檔的 `狀態` 與 `claim_ref` 各自單一 script，必須不被誤殺。
"""

狀態 = "ACTIVE"
claim_ref = "engineering.rules.day-one-enforced"
claim狀態 = (claim_ref, 狀態)
