import os, pandas as pd, numpy as np, requests, yfinance as yf
from datetime import datetime, timezone

def _to_yahoo(sym: str) -> str:
    s = sym.upper()
    s = s.replace("/","")  # EUR/USD -> EURUSD
    return s + ("=X" if not s.endswith("=X") else "")

def _to_td(sym: str) -> str:
    s = sym.upper().replace("=X","")
    return s if "/" in s else (s[:3]+"/"+s[3:] if len(s)==6 and s.isalpha() else s)

def _pretty_tf(tf_minutes: int) -> str:
    return f"H{tf_minutes//60}" if tf_minutes>=60 else f"M{tf_minutes}"

def _yf_interval(tf_minutes: int):
    return f"{tf_minutes}m", ("60d" if tf_minutes<=240 else "730d")

def _td_interval(tf_minutes: int):
    return {1:"1min",5:"5min",15:"15min",30:"30min",60:"1h",240:"4h",1440:"1day"}.get(tf_minutes,"1h")

def _fetch_yahoo(y_sym: str, tf_minutes: int):
    interval, period = _yf_interval(tf_minutes)
    try:
        df = yf.download(tickers=y_sym, period=period, interval=interval, progress=False)
        if df is None or df.empty: return None
        df = df.rename(columns=str.title).dropna()
        return df.astype(float)
    except Exception:
        return None

def _fetch_td(td_sym: str, tf_minutes: int):
    key = os.getenv("TWELVE_DATA_API_KEY")
    if not key: return None
    url = "https://api.twelvedata.com/time_series"
    params = dict(symbol=td_sym, interval=_td_interval(tf_minutes), outputsize=400,
                  timezone="UTC", order="ASC", apikey=key)
    try:
        r = requests.get(url, params=params, timeout=12)
        j = r.json()
        if isinstance(j, dict) and j.get("status")=="error":  # invalid symbol, etc.
            return None
        vals = j.get("values", [])
        if not vals: return None
        df = pd.DataFrame(vals)
        cols = {"open":"Open","high":"High","low":"Low","close":"Close","volume":"Volume"}
        df = df.rename(columns=cols)
        df["datetime"] = pd.to_datetime(df["datetime"], utc=True)
        df = df.set_index("datetime").sort_index()
        for c in ("Open","High","Low","Close","Volume"):
            if c in df: df[c] = pd.to_numeric(df[c], errors="coerce")
        return df.dropna(subset=["Open","High","Low","Close"])
    except Exception:
        return None

def get_candles(symbol: str, tf_minutes: int):
    """Return (df, source, y_sym, td_sym, pretty_tf, interval_str) and NEVER None."""
    y_sym = _to_yahoo(symbol)
    td_sym = _to_td(symbol)
    pretty = _pretty_tf(tf_minutes)
    y_df = _fetch_yahoo(y_sym, tf_minutes)
    if y_df is not None and not y_df.empty:
        return y_df, "yahoo", y_sym, td_sym, pretty, f"{tf_minutes}m"
    t_df = _fetch_td(td_sym, tf_minutes)
    if t_df is not None and not t_df.empty:
        return t_df, "twelvedata", y_sym, td_sym, pretty, _td_interval(tf_minutes)
    # final guaranteed tuple even on total failure
    return None, "none", y_sym, td_sym, pretty, _td_interval(tf_minutes)
