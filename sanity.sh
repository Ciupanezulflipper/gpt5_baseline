#!/data/data/com.termux/files/usr/bin/bash
set -u

pass=0; fail=0
ok(){ echo -e "✅ $1"; pass=$((pass+1)); }
bad(){ echo -e "❌ $1"; fail=$((fail+1)); }

echo "[*] Reloading .env..."
set -a && . ./.env 2>/dev/null || true && set +a

# workdir for temp
tmpdir="./_sanity_tmp"
mkdir -p "$tmpdir"

# 1) env check
[[ "${PREFER_SOURCE:-}" == "TD" ]] && ok "PREFER_SOURCE=TD" || bad "PREFER_SOURCE not TD"
[[ "${YF_DISABLE:-}" == "1" ]] && ok "YF_DISABLE=1" || bad "YF_DISABLE not 1"
[[ -n "${TWELVE_DATA_API_KEY:-}" ]] && ok "TD key present" || bad "TD key missing"

# 2) TwelveData curl check
resp="$(curl -s "https://api.twelvedata.com/time_series?symbol=USD/JPY&interval=1h&outputsize=3&apikey=${TWELVE_DATA_API_KEY:-}")"
echo "$resp" | grep -q '"status":"ok"' && ok "TwelveData HTTP OK" || bad "TwelveData HTTP not OK"

# 3) Python import + get_candles rows
python - <<'PY' >"$tmpdir/rows.txt" 2>"$tmpdir/pyerr.txt" || true
from core import get_candles
df, src = get_candles("USD/JPY", 60, 50)
print(src, len(df) if df is not None else 0)
PY
if [[ -s "$tmpdir/rows.txt" ]]; then
  rows=$(awk '{print $2}' "$tmpdir/rows.txt")
  [[ ${rows:-0} -ge 10 ]] && ok "Python get_candles rows=${rows}" || bad "Low/zero rows from get_candles (${rows})"
else
  bad "Python get_candles error"; sed -n '1,80p' "$tmpdir/pyerr.txt"
fi

# 4) main.py dry run (no telegram)
python main.py --symbol "USD/JPY" --tf 60 --no-telegram >"$tmpdir/main.txt" 2>&1
grep -q "Price:" "$tmpdir/main.txt" && ok "main.py printed signal" || bad "main.py did not print a signal"

echo
echo "==== Sanity Summary ===="
echo "Pass: $pass  Fail: $fail"
[[ $fail -eq 0 ]] && exit 0 || exit 1

# --- Key expiry check ---
echo "[*] Checking Finage API key expiry..."
python helpers/check_api_expiry.py
