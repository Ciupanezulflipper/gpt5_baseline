#!/data/data/com.termux/files/usr/bin/bash
set -e
set -a && . ./.env 2>/dev/null || true && set +a

echo "[*] Running smoke tests..."
python - <<'PY'
from core import get_candles
syms = ("USD/JPY","EUR/USD","XAU/USD")
for s in syms:
    df, src = get_candles(s, 60, 50)
    print(f"{s} -> {src} | rows:", 0 if df is None else len(df))
    if df is not None:
        print(df.tail(2))
PY
