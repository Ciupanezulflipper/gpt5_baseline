#!/data/data/com.termux/files/usr/bin/bash
set -e
set -a && . ./.env 2>/dev/null || true && set +a
: > "${LOG_FILE:-errors.log}"
echo "[`date -u +%FT%TZ`] START symbol=$1 tf=$2 src=${PREFER_SOURCE:-TD}" | tee -a "${LOG_FILE:-errors.log}"
python main.py --symbol "$1" --tf "$2" --no-telegram | tee -a "${LOG_FILE:-errors.log}"
echo "[`date -u +%FT%TZ`] END status=$?" | tee -a "${LOG_FILE:-errors.log}"

echo "[*] Finage key status:"
python helpers/check_api_expiry.py | tee -a "${LOG_FILE:-errors.log}"
