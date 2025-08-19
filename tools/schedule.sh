#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail
cd "$(dirname "$0")/.."
termux-wake-lock || true
while :; do
  date -u +"[H1] %F %T UTC"
  python main.py --symbol EURUSD=X --tf 60 --htf 240 || true
  sleep 3600
done
