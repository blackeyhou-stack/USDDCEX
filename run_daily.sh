#!/bin/bash
# USDD CEX Balance Tracker — 每日自动抓取脚本
# 每天 00:00 UTC+8 由 cron 调用

set -e

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
LOG_FILE="$PROJECT_DIR/cron.log"

echo "========================================" >> "$LOG_FILE"
echo "[$(date '+%Y-%m-%d %H:%M:%S')] 开始抓取" >> "$LOG_FILE"

cd "$PROJECT_DIR"
source "$PROJECT_DIR/venv/bin/activate"

# 抓取数据
python3 "$PROJECT_DIR/fetch_data.py" >> "$LOG_FILE" 2>&1

# 自动 commit + push 到 GitHub
git add data/history.json data/data.js >> "$LOG_FILE" 2>&1
git commit -m "Auto update: $(date '+%Y-%m-%d') USDD balances" >> "$LOG_FILE" 2>&1 || echo "[$(date '+%Y-%m-%d %H:%M:%S')] 无变化，跳过 commit" >> "$LOG_FILE"
git push >> "$LOG_FILE" 2>&1

echo "[$(date '+%Y-%m-%d %H:%M:%S')] 完成" >> "$LOG_FILE"
