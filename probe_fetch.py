import os, sys, requests
API_KEY = os.getenv("TWELVE_DATA_API_KEY")
if not API_KEY:
    print("NO_TD_KEY in env. Put TWELVE_DATA_API_KEY in .env here."); raise SystemExit(2)

sym_in = (sys.argv[1] if len(sys.argv)>1 else "EUR/USD").upper()
tf     = int(sys.argv[2]) if len(sys.argv)>2 else 60

def to_td(s):
    s = s.upper().replace("=X","")
    if len(s)==6 and s.isalpha(): return s[:3]+"/"+s[3:]
    return s

interval = {1:"1min",5:"5min",15:"15min",30:"30min",60:"1h",240:"4h",1440:"1day"}.get(tf,"1h")
td_sym   = to_td(sym_in)

params = dict(symbol=td_sym, interval=interval, outputsize=2, timezone="UTC",
              order="ASC", apikey=API_KEY)
try:
    r = requests.get("https://api.twelvedata.com/time_series", params=params, timeout=10)
    j = r.json()
    if isinstance(j, dict) and j.get("status")=="error":
        print("TD_ERROR:", j); raise SystemExit(3)
    vals = j.get("values", [])
    print(f"OK TD → {td_sym} ({interval}) rows={len(vals)}")
    for row in vals[-2:]:
        print(row.get("datetime"), row.get("open"), row.get("high"), row.get("low"), row.get("close"))
except Exception as e:
    print("TD_EXCEPTION:", repr(e)); raise SystemExit(4)
