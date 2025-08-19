import os, asyncio
from pathlib import Path
from dotenv import load_dotenv
from telegram import Bot

load_dotenv()
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN","").strip()
CHAT_ID   = os.getenv("TELEGRAM_CHAT_ID","").strip()
LOGDIR    = Path("logs"); LOGDIR.mkdir(exist_ok=True)
PENDING   = LOGDIR / "pending.txt"

async def _flush_pending(bot: Bot):
    if not PENDING.exists():
        return
    try:
        lines = PENDING.read_text().splitlines()
        if not lines: return
        # send in one chunk if small, else line by line
        chunk = []
        for ln in lines:
            if ln.strip() == "---":
                if chunk:
                    await bot.send_message(chat_id=CHAT_ID, text="\n".join(chunk)[:4000])
                    chunk = []
            else:
                chunk.append(ln)
        if chunk:
            await bot.send_message(chat_id=CHAT_ID, text="\n".join(chunk)[:4000])
        PENDING.unlink(missing_ok=True)
    except Exception:
        # keep file if not flushed
        pass

async def send_telegram(text: str):
    if not BOT_TOKEN or not CHAT_ID:
        print("Telegram not configured (.env TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID).")
        return
    bot = Bot(BOT_TOKEN)
    try:
        await _flush_pending(bot)
        await bot.send_message(chat_id=CHAT_ID, text=text)
    except Exception as e:
        print(f"Telegram send failed: {e} -> queued")
        try:
            with PENDING.open("a") as f:
                f.write(text + "\n---\n")
        except Exception:
            pass
