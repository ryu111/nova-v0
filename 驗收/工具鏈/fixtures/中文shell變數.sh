#!/usr/bin/env bash
# 事前固定的錯誤 subject：shell 變數名用中文。
#
# 宣稱落點: 工具/清理產物.sh
#
# CLAUDE.md 把 shell 變數／函式名列在 ASCII 例外清單裡：Bash 的 name 只接受
# 字母、數字、底線且不能以數字開頭，中文名在不同 bash 版本與 locale 下行為不一致。
# checker 必須回 NON_ASCII_SHELL_NAME。
#
# 同檔的 target_dir 是合法 ASCII name，必須不被誤殺。
set -euo pipefail

target_dir="/tmp/nova-probe"
本次路徑=/tmp/x
rm -rf "${target_dir}" "${本次路徑}"
