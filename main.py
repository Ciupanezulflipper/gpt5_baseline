# main.py — FULL canonical build
# Version: 1.0.1 (2025-08-19)

from __future__ import annotations
import os, argparse
from datetime import datetime, timezone
import requests

from core import (
    get_candles, build_bias, atr, pip_size, risk_plan,
    last_bar_time, tf_label, round_px
)

# Optional Telegram
def tg_send(text: str) -> bool:
    tok = os.getenv("TELEGRAM_BOT_TOKEN")
    chat = os.getenv("TELEGRAM_CHAT_ID")
    if not tok or not chat:
        return False
    try:
        url = f"https://api.telegram.org/bot{tok}/sendMessage"
        r = requests.post(url, json={"chat_id": chat, "text": text, "parse_mode": "Markdown"}, timeout=8)
        return r.status_code == 200
    except Exception:
        return False

def utc_now_iso():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()

def fmt_msg(sym: str, src: str, df, bias_info: dict, stop_pips: float, plan: dict, tfm: int):
    if df is None or df.empty:
        return f"📉 *{sym}*\nNo data. Wait."
    last = float(df['close'].iloc[-1])
    lastt = last_bar_time(df)
    why = ", ".join(bias_info.get("why", []))
    bias = bias_info.get("bias", "MIXED")
    score = bias_info.get("score", 0.0)
    lines = []
    lines.append(f"📊 *{sym}* — *{bias}* (score `{score}`)")
    lines.append(f"Source: `{src}`  TF:`{tf_label(tfm)}`  Rows:`{len(df)}`")
    lines.append(f"Price: `{round_px(sym, last)}`  Time:`{lastt}`")
    if stop_pips and plan:
        lines.append(f"ATR stop ~ `{round(stop_pips,1)} pips`  | Risk ${plan['risk_amount']}  | Lot `{plan['lot_size']}`")
    if why:
        lines.append(f"Why: {why}")
    lines.append(f"Built: `{utc_now_iso()}`")
    return "\n".join(lines)

def parse_args():
    ap = argparse.ArgumentParser()
    ap.add_argument("--symbol", required=True, help='e.g. "USD/JPY" or "EURUSD"')
    ap.add_argument("--tf", type=int, default=60, help="timeframe in minutes (e.g. 60=H1)")
    ap.add_argument("--no-telegram", action="store_true", help="do not send to Telegram")
    return ap.parse_args()

if __name__ == "__main__":
    args = parse_args()

    df, src = get_candles(args.symbol, args.tf, rows=400)

    if df is None or df.empty:
        msg = f"📉 *{args.symbol}*\nNo data. Wait."
        print(msg)
        if not args.no_telegram:
            tg_send(msg)
        raise SystemExit(0)

    bias_info = build_bias(df)
    atr_pts = atr(df, period=14)
    pipsz = pip_size(args.symbol)
    stop_pips = atr_pts / pipsz if atr_pts == atr_pts and pipsz > 0 else 0.0
    plan = risk_plan(balance=1000.0, risk_pct=2.0, stop_pips=stop_pips, pip_value=1.0)

    msg = fmt_msg(args.symbol, src, df, bias_info, stop_pips, plan, args.tf)
    print("\n" + msg + "\n")

    if not args.no_telegram:
        tg_send(msg)
