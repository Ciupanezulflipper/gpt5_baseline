# core.py — FULL canonical build
# Version: 1.0.1 (2025-08-19)  — TD symbol fix (ensure "USD/JPY" not "USDJPY")

from __future__ import annotations
import os
import math
import requests
import pandas as pd

# -----------------------------
# Environment / switches
# -----------------------------
PREFER_SOURCE = os.getenv("PREFER_SOURCE", "TD").upper()  # TD or YF
TD_API_KEY = os.getenv("TWELVE_DATA_API_KEY", "")
YF_DISABLE = os.getenv("YF_DISABLE", "0") == "1"

# -----------------------------
# Timeframe helpers
# -----------------------------
def tf_label(minutes: int) -> str:
    m = int(minutes)
    return {
        1: "1m", 5: "5m", 15: "15m", 30: "30m",
        60: "1h", 120: "2h", 240: "4h", 1440: "1day"
    }.get(m, "1h")

# -----------------------------
# Symbol helpers
# -----------------------------
def map_symbol_for_yahoo(symbol: str) -> str:
    s = symbol.upper().replace(" ", "")
    if "/" in s:
        b, q = s.split("/", 1)
        return f"{b}{q}=X"
    if not s.endswith("=X"):
        return f"{s}=X"
    return s

def map_symbol_for_td(symbol: str) -> str:
    """
    Normalize to TD preferred format (with slash for FX: 'USD/JPY').
    Accepts 'USD/JPY', 'USDJPY', or 'USDJPY=X'.
    """
    s = symbol.upper().replace(" ", "")
    if s.endswith("=X"):
        s = s[:-2]  # 'USDJPY=X' -> 'USDJPY'
    if "/" in s:
        return s
    if len(s) == 6 and s.isalpha():
        return f"{s[:3]}/{s[3:]}"
    return s

def pip_size(symbol: str) -> float:
    s = symbol.upper()
    if "JPY" in s: return 0.01
    if "XAU" in s: return 0.10
    if "XAG" in s: return 0.001
    return 0.0001

# -----------------------------
# Fetchers
# -----------------------------
def _fetch_twelvedata(symbol: str, tf_minutes: int, rows: int = 400) -> pd.DataFrame | None:
    if not TD_API_KEY:
        return None
    intr = tf_label(tf_minutes)
    td_sym = map_symbol_for_td(symbol)
    url = "https://api.twelvedata.com/time_series"
    params = {
        "symbol": td_sym,
        "interval": intr,
        "outputsize": min(rows, 5000),
        "format": "JSON",
        "apikey": TD_API_KEY,
    }
    try:
        r = requests.get(url, params=params, timeout=10)
        r.raise_for_status()
        data = r.json()
        if "values" not in data:
            return None
        vals = data["values"]
        if not vals:
            return None
        df = pd.DataFrame(vals)
        df.rename(columns={
            "datetime": "datetime",
            "open": "open", "high": "high",
            "low": "low", "close": "close",
            "volume": "volume"
        }, inplace=True)
        df["datetime"] = pd.to_datetime(df["datetime"], utc=True)
        for c in ("open", "high", "low", "close"):
            df[c] = pd.to_numeric(df[c], errors="coerce")
        df = df.dropna(subset=["open", "high", "low", "close"]).sort_values("datetime")
        if len(df) > rows:
            df = df.tail(rows)
        return df
    except Exception:
        return None

def _fetch_yahoo(symbol: str, tf_minutes: int, rows: int = 400) -> pd.DataFrame | None:
    if YF_DISABLE:
        return None
    try:
        import yfinance as yf
    except Exception:
        return None
    intr = tf_label(tf_minutes)
    yf_interval = {
        "1m":"1m","5m":"5m","15m":"15m","30m":"30m",
        "1h":"60m","2h":"60m","4h":"60m","1day":"1d"
    }.get(intr, "60m")
    period = "60d" if tf_minutes >= 60 else "10d"
    try:
        ysym = map_symbol_for_yahoo(symbol)
        df = yf.download(ysym, interval=yf_interval, period=period, progress=False, threads=False)
        if df is None or df.empty:
            return None
        df = df.rename(columns=str.lower).reset_index()
        if "datetime" not in df.columns:
            dtcol = "Datetime" if "Datetime" in df.columns else "Date"
            df.rename(columns={dtcol: "datetime"}, inplace=True)
        df.rename(columns={"open":"open","high":"high","low":"low","close":"close","Open":"open","High":"high","Low":"low","Close":"close"}, inplace=True)
        df["datetime"] = pd.to_datetime(df["datetime"], utc=True)
        df = df[["datetime","open","high","low","close"]].dropna()
        if len(df) > rows:
            df = df.tail(rows)
        return df
    except Exception:
        return None

def get_candles(symbol: str, tf_minutes: int, rows: int = 400) -> tuple[pd.DataFrame | None, str]:
    """
    Unified fetch: tries the preferred source, then fallback.
    Returns (df, source) where source in {"TD","YF","None"}.
    """
    order = ["TD","YF"] if PREFER_SOURCE == "TD" else ["YF","TD"]
    df = None; src = "None"
    for s in order:
        df = _fetch_twelvedata(symbol, tf_minutes, rows) if s == "TD" else _fetch_yahoo(symbol, tf_minutes, rows)
        if df is not None and not df.empty:
            src = s
            break
    return df, src

# -----------------------------
# Indicators
# -----------------------------
def sma(series: pd.Series, period: int = 14) -> pd.Series:
    return series.rolling(period).mean()

def ema(series: pd.Series, period: int = 14) -> pd.Series:
    return series.ewm(span=period, adjust=False).mean()

def rsi(series: pd.Series, period: int = 14) -> pd.Series:
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(period).mean()
    rs = gain / (loss.replace(0, pd.NA))
    return 100 - (100 / (1 + rs))

def atr(df: pd.DataFrame, period: int = 14) -> float:
    if df is None or df.empty or len(df) < 2:
        return float("nan")
    h = df["high"].to_numpy()
    l = df["low"].to_numpy()
    c = df["close"].to_numpy()
    tr = []
    for i in range(1, len(df)):
        tr_i = max(h[i] - l[i], abs(h[i] - c[i-1]), abs(l[i] - c[i-1]))
        tr.append(tr_i)
    if not tr:
        return float("nan")
    s = pd.Series(tr).tail(period).mean()
    return float(s)

# -----------------------------
# Bias
# -----------------------------
def build_bias(df: pd.DataFrame) -> dict:
    """
    Simple bias based on SMA cross + RSI.
    Returns dict: {"bias": str, "score": float, "why": list[str]}
    """
    out = {"bias":"NEUTRAL","score":0.0,"why":[]}
    if df is None or df.empty:
        out["why"].append("no_data")
        return out
    c = df["close"]
    f = sma(c, 10).iloc[-1]
    s = sma(c, 30).iloc[-1]
    rv = rsi(c, 14).iloc[-1]
    why = []
    score = 0
    if pd.notna(f) and pd.notna(s):
        if f > s: score += 1; why.append("sma_fast>slow")
        if f < s: score += 1; why.append("sma_fast<slow")
    if pd.notna(rv):
        if rv > 60: score += 1; why.append("rsi>60")
        elif rv < 40: score += 1; why.append("rsi<40")
    if "sma_fast>slow" in why and "rsi>60" in why:
        bias = "BULLISH"
    elif "sma_fast<slow" in why and "rsi<40" in why:
        bias = "BEARISH"
    else:
        bias = "MIXED"
    out["bias"] = bias
    out["score"] = float(score)
    out["why"] = why
    return out

# -----------------------------
# Risk management
# -----------------------------
def risk_plan(balance: float, risk_pct: float, stop_pips: float, pip_value: float = 1.0) -> dict:
    """
    Position size based on balance & stop in pips.
    """
    risk_amount = max(0.0, balance) * (risk_pct / 100.0)
    lot_size = (risk_amount / (stop_pips * pip_value)) if stop_pips and stop_pips > 0 else 0.0
    return {"risk_amount": round(risk_amount, 2), "lot_size": round(lot_size, 2)}

# -----------------------------
# Utilities
# -----------------------------
def last_bar_time(df: pd.DataFrame):
    if df is None or df.empty:
        return None
    return pd.to_datetime(df["datetime"].iloc[-1]).to_pydatetime()

def round_px(symbol: str, price: float) -> float:
    step = pip_size(symbol)
    prec = 3 if math.isclose(step, 0.01) else (2 if math.isclose(step,0.1) else 5)
    return round(price, prec)
