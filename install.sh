#!/data/data/com.termux/files/usr/bin/bash
set -e

echo "[*] Installing Termux packages..."
pkg update -y
pkg install -y python git curl jq

echo "[*] Upgrading pip & installing Python deps..."
python -m pip install --upgrade pip
python -m pip install pandas requests python-telegram-bot --upgrade

if [ ! -f ".env" ]; then
  echo "[*] Creating .env skeleton..."
  cat > .env <<'ENV'
PREFER_SOURCE=TD
YF_DISABLE=1
LOG_FILE=errors.log
LOG_LEVEL=INFO
# put your real key below
TWELVE_DATA_API_KEY=
NO_PROXY=api.twelvedata.com,.twelvedata.com
ENV
fi

echo "[*] Reloading .env into this shell..."
set -a && . ./.env 2>/dev/null || true && set +a

echo "[*] Ensuring wrappers are executable..."
chmod +x start.sh 2>/dev/null || true

echo "[*] Done. Run './smoke.sh' next."
