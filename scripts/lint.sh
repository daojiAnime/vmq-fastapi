#!/usr/bin/env bash

# 当任何命令返回非零状态时立即退出脚本
set -e
# 打印执行的每个命令及其参数（带展开变量）
set -x
# 防止变量错误
set -u

mypy app
ruff check app
ruff format app --check
