# tg_bot.py — reserved for Phase B command bot (e.g., /analyze, /chart)
# Minimal send helper if you want to import it elsewhere.

import os, asyncio
from dotenv import load_dotenv

async def send_telegram(text:str):
    load_dotenv()
    token = os.getenv("TELEGRAM_BOT_TOKEN","").strip()
    chat_id = os.getenv("TELEGRAM_CHAT_ID","").strip()
    if not token or not chat_id:
        print("Telegram not configured. Set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID in .env")
        return
    try:
        from telegram import Bot
        bot = Bot(token)
        await bot.send_message(chat_id=chat_id, text=text)
    except Exception as e:
        print(f"Telegram send failed: {e}")
