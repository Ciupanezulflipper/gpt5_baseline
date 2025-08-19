# health_main.py — quick smoke test for env, profile, and data reachability

import os
from datetime import datetime, timezone
from dotenv import load_dotenv
from core import get_candles

def main():
    load_dotenv()
    print(f"🩺 Health Check @ {datetime.now(timezone.utc).isoformat(timespec='seconds')}")
    # Env
    print("\n🔑 Env:")
    for k in ["TELEGRAM_BOT_TOKEN","TELEGRAM_CHAT_ID","TWELVE_DATA_API_KEY"]:
        val = os.getenv(k)
        print(f"  {k:>20}: {'SET' if val else 'MISSING'}")
    bypass = os.getenv("NO_PROXY","") + " " + os.getenv("no_proxy","")
    ok_bypass = ("twelvedata.com" in bypass)
    print(f"  NO_PROXY/no_proxy includes TwelveData {'✅' if ok_bypass else '❌'}")

    # Reachability + core.get_candles smoke
    pairs = ["EUR/USD","EURUSD","EURUSD=X","XAUUSD","XAU/USD"]
    print("\n🧪 core.get_candles() smoke test:")
    ok=0
    for s in pairs:
        try:
            r = get_candles(s, 60)
            df = r[0]
            if df is not None and not df.empty:
                ok += 1
                print(f"  ✅ {s}: rows={len(df)}")
            else:
                print(f"  ❌ {s}: empty")
        except Exception as e:
            print(f"  ❌ {s}: {e}")

    print(f"\n📦 OK {ok}/{len(pairs)} symbols")

if __name__ == "__main__":
    main()
