import os
from datetime import datetime, timezone

def check_api_expiry():
    expiry_str = os.getenv("FINAGE_KEY_EXPIRY")
    warn_days = int(os.getenv("FINAGE_KEY_WARN_DAYS", "7"))
    if not expiry_str:
        return "⚠️  FINAGE_KEY_EXPIRY is not set"

    try:
        # Accept YYYY-MM-DD (date only)
        expiry = datetime.fromisoformat(expiry_str.strip())
        if expiry.tzinfo is None:
            expiry = expiry.replace(tzinfo=timezone.utc)
    except Exception as e:
        return f"⚠️  FINAGE_KEY_EXPIRY parse error: {e}"

    today = datetime.now(timezone.utc)
    days_left = (expiry - today).days

    if days_left < 0:
        return f"❌ Finage API key expired {abs(days_left)} day(s) ago ({expiry.date()})."
    if days_left <= warn_days:
        return f"⚠️  Finage API key will expire in {days_left} day(s) on {expiry.date()}. Regenerate soon."
    return f"✅ Finage API key valid: {days_left} day(s) left (expires {expiry.date()})."

if __name__ == "__main__":
    print(check_api_expiry())
