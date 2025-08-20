import os, sys
from helpers.check_api_expiry import check_api_expiry

def main():
    msg = check_api_expiry()  # prints ✅/⚠️/❌ status with dates
    print(msg)                # always show in stdout
    warn = msg.startswith("⚠️") or msg.startswith("❌")

    # Telegram notify only on warn/expired
    if warn and os.getenv("TELEGRAM_BOT_TOKEN") and os.getenv("TELEGRAM_CHAT_ID"):
        try:
            from tg_bot import tg_send
            tg_send(msg)
        except Exception as e:
            print(f"⚠️ Telegram notify failed: {e}", file=sys.stderr)

if __name__ == "__main__":
    main()
