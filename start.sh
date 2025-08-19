#!/data/data/com.termux/files/usr/bin/bash
set -e

# Load env (LOG_FILE, LOG_LEVEL, PREFER_SOURCE, TELEGRAM_* etc.)
set -a && . ./.env 2>/dev/null || true && set +a

# Fresh log per run
: > "${LOG_FILE:-errors.log}"

echo "[`date -u +%FT%TZ`] START symbol=$1 tf=$2 src=${PREFER_SOURCE:-TD}" | tee -a "${LOG_FILE:-errors.log}"

# Optional Finage key expiry notice (safe if vars are missing)
python helpers/check_api_expiry.py 2>/dev/null | tee -a "${LOG_FILE:-errors.log}" || true

# Run the bot WITH Telegram (flag removed)
python main.py --symbol "$1" --tf "$2" | tee -a "${LOG_FILE:-errors.log}"

# Preserve python exit status when piped through 'tee'
status=${PIPESTATUS[0]}
echo "[`date -u +%FT%TZ`] END status=$status" | tee -a "${LOG_FILE:-errors.log}"
exit $status
