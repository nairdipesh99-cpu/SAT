
import feedparser
import requests
from datetime import datetime, timedelta
import re

KEYWORDS = [
    "earnings","results","revenue","profit","loss","debt","contract",
    "acquisition","merger","ceo","expansion","quarterly","annual",
    "dividend","lawsuit","penalty","upgrade","downgrade","target",
    "guidance","forecast","buyback","fundraise","ipo","delisting",
    "default","bankruptcy","rating","interest rate","rbi","fed","sebi",
]

def fetch_news(company_name, ticker="", max_items=8):
    """Fetch and filter news for a company"""
    query = f"{company_name} stock"
    feeds = [
        f"https://news.google.com/rss/search?q={query.replace(' ', '+')}&hl=en-IN&gl=IN&ceid=IN:en",
        f"https://feeds.finance.yahoo.com/rss/2.0/headline?s={ticker}&region=US&lang=en-US",
    ]
    articles = []
    for feed_url in feeds:
        try:
            feed = feedparser.parse(feed_url)
            for entry in feed.entries[:15]:
                title   = entry.get("title", "")
                source  = entry.get("source", {}).get("title", "News") if hasattr(entry.get("source",""), "get") else "News"
                pub     = entry.get("published", "")
                link    = entry.get("link", "")
                if any(kw in title.lower() for kw in KEYWORDS):
                    tier  = classify_source(source)
                    articles.append({
                        "title":   title,
                        "source":  source,
                        "time":    format_pub_time(pub),
                        "link":    link,
                        "tier":    tier,
                    })
        except:
            pass
    # Deduplicate by title similarity
    seen, unique = set(), []
    for a in articles:
        key = a["title"][:40].lower()
        if key not in seen:
            seen.add(key)
            unique.append(a)
    unique.sort(key=lambda x: tier_order(x["tier"]))
    return unique[:max_items]

def classify_source(source):
    source_lower = source.lower()
    official = ["bse","nse","sebi","sec.gov","rbi","fed","lse","fca"]
    wire     = ["reuters","associated press","ap news","bloomberg","ft","financial times"]
    caution  = ["reddit","twitter","telegram","whatsapp","quora"]
    if any(s in source_lower for s in official): return "OFFICIAL"
    if any(s in source_lower for s in wire):     return "WIRE"
    if any(s in source_lower for s in caution):  return "CAUTION"
    return "MEDIA"

def tier_order(tier):
    return {"OFFICIAL": 0, "WIRE": 1, "MEDIA": 2, "CAUTION": 3}.get(tier, 2)

def tier_color(tier):
    return {"OFFICIAL": "#10B981", "WIRE": "#3B82F6", "MEDIA": "#6B7280", "CAUTION": "#EF4444"}.get(tier, "#6B7280")

def format_pub_time(pub_str):
    try:
        from email.utils import parsedate_to_datetime
        dt = parsedate_to_datetime(pub_str)
        diff = datetime.now(dt.tzinfo) - dt
        if diff.days > 0:   return f"{diff.days}d ago"
        hours = diff.seconds // 3600
        if hours > 0:        return f"{hours}h ago"
        mins = diff.seconds // 60
        return f"{mins}m ago"
    except:
        return pub_str[:10] if pub_str else ""

def get_gc_news():
    """Fetch global crisis / macro news"""
    feeds = [
        "https://feeds.reuters.com/reuters/businessNews",
        "https://feeds.bbci.co.uk/news/business/rss.xml",
        "https://feeds.a.dj.com/rss/RSSWorldNews.xml",
    ]
    gc_keywords = [
        "war","conflict","recession","inflation","interest rate","fed rate",
        "rbi rate","oil price","commodity","sanctions","trade war","gdp",
        "unemployment","crisis","default","central bank","geopolitical",
        "opec","dollar","crude","supply chain","covid","pandemic",
    ]
    articles = []
    for feed_url in feeds:
        try:
            feed = feedparser.parse(feed_url)
            for entry in feed.entries[:20]:
                title  = entry.get("title", "")
                source = entry.get("source", {}).get("title", "Reuters") if hasattr(entry.get("source",""), "get") else "Reuters"
                pub    = entry.get("published", "")
                if any(kw in title.lower() for kw in gc_keywords):
                    articles.append({
                        "title":  title,
                        "source": source,
                        "time":   format_pub_time(pub),
                        "impact": classify_gc_impact(title),
                    })
        except:
            pass
    seen, unique = set(), []
    for a in articles:
        key = a["title"][:40].lower()
        if key not in seen:
            seen.add(key)
            unique.append(a)
    return unique[:12]

def classify_gc_impact(title):
    title_lower = title.lower()
    negative = ["war","conflict","recession","crisis","default","sanction","crash","collapse","surge","spike"]
    positive = ["rate cut","recovery","growth","deal","peace","stimulus","easing"]
    if any(w in title_lower for w in negative): return "NEGATIVE"
    if any(w in title_lower for w in positive): return "POSITIVE"
    return "NEUTRAL"

def calculate_gc_status(ticker, sector=""):
    """Calculate GC status for a stock based on global events"""
    # Sectors that benefit from common crises
    gc_winners = {
        "Energy": ["oil","energy","gas","crude"],
        "Technology": ["inr weak","dollar strong","rupee"],
        "Healthcare": ["health","pandemic","covid","disease"],
        "Materials": ["war","conflict","infrastructure","steel","defence"],
        "Utilities": ["recession","defensive","stability"],
    }
    gc_losers = {
        "Airlines": ["oil","fuel","crude"],
        "Consumer Discretionary": ["recession","inflation"],
        "Real Estate": ["interest rate","rate hike"],
        "Automobiles": ["recession","chip shortage"],
    }
    news = get_gc_news()
    if not news:
        return "GREEN", "No significant global events detected"
    negative_count = sum(1 for n in news if n["impact"] == "NEGATIVE")
    positive_count = sum(1 for n in news if n["impact"] == "POSITIVE")
    # Check if sector benefits
    sector_upper = sector.upper()
    for s, keywords in gc_winners.items():
        if s.upper() in sector_upper:
            if any(any(kw in n["title"].lower() for kw in keywords) for n in news):
                return "WINNER", f"{sector} benefits from current global events"
    for s, keywords in gc_losers.items():
        if s.upper() in sector_upper:
            if any(any(kw in n["title"].lower() for kw in keywords) for n in news):
                return "RED", f"Global events creating headwinds for {sector}"
    if negative_count >= 4:   return "RED",   "High global risk environment"
    if negative_count >= 2:   return "AMBER", "Moderate global risks present"
    return "GREEN", "Global conditions broadly stable"

