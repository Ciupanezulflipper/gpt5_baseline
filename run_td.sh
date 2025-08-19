#!/usr/bin/env bash
set -euo pipefail

# Defaults (override by exporting before calling if you want)
export PREFER_SOURCE="${PREFER_SOURCE:-TD}"
export LOG_FILE="${LOG_FILE:-errors.log}"
export LOG_LEVEL="${LOG_LEVEL:-INFO}"

# Show what we’re about to do
echo "[$(date -u +%FT%TZ)] START symbol=${1:-USD/JPY} tf=${2:-60} src=$PREFER_SOURCE" | tee -a "$LOG_FILE"

python run.py --symbol "${1:-USD/JPY}" --tf "${2:-60}" --no-telegram 2>&1 | tee -a "$LOG_FILE"

echo "[$(date -u +%FT%TZ)] END status=$?" | tee -a "$LOG_FILE"
