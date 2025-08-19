import time, feedparser
KEYWORDS = ["CPI","NFP","FOMC","rate decision","ECB","Powell","Lagarde","BoE","inflation","unemployment"]
FEEDS = ["https://www.forexlive.com/feed/","https://www.fxstreet.com/rss"]
def red_news_next_hour() -> bool:
    try:
        now = time.time()
        for url in FEEDS:
            d = feedparser.parse(url)
            for e in d.get("entries", []):
                t = e.get("published_parsed")
                if not t: continue
                ts = time.mktime(t)
                if 0 <= ts - now <= 3600:
                    title = (e.get("title") or "").lower()
                    if any(k.lower() in title for k in KEYWORDS):
                        return True
        return False
    except Exception:
        return False
