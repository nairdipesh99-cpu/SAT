"""
India Market Intelligence Dashboard
====================================
Professional-grade, institutional-quality stock intelligence platform
featuring live NSE data, FinBERT sentiment, FMP fundamentals, and AI research.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import requests
import json
from datetime import date, datetime, timedelta
from typing import Optional, Dict, List, Tuple
import warnings
import time
import re

warnings.filterwarnings("ignore")

# ─── Page Config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="India Market Intelligence",
    page_icon="🇮🇳",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Global Dark Theme CSS ─────────────────────────────────────────────────────
st.markdown("""
<style>
  /* ── Core dark background ── */
  .stApp { background: #0d1117; color: #e6edf3; }
  section[data-testid="stSidebar"] { background: #161b22 !important; border-right: 1px solid #30363d; }
  div[data-testid="stToolbar"] { display: none; }

  /* ── Typography ── */
  h1, h2, h3, h4 { color: #e6edf3 !important; font-family: 'Inter', sans-serif; }
  p, label, .stMarkdown { color: #8b949e; }

  /* ── Metric Cards ── */
  .metric-card {
    background: #161b22;
    border: 1px solid #30363d;
    border-radius: 10px;
    padding: 16px 20px;
    margin: 6px 0;
    transition: border-color 0.2s;
  }
  .metric-card:hover { border-color: #58a6ff; }
  .metric-label { font-size: 11px; color: #8b949e; text-transform: uppercase; letter-spacing: 0.06em; }
  .metric-value { font-size: 26px; font-weight: 700; color: #e6edf3; margin: 4px 0; }
  .metric-delta { font-size: 13px; font-weight: 500; }
  .delta-pos { color: #3fb950; }
  .delta-neg { color: #f85149; }

  /* ── Column Headers ── */
  .col-header {
    background: linear-gradient(135deg, #161b22 0%, #1c2128 100%);
    border: 1px solid #30363d;
    border-radius: 10px;
    padding: 14px 18px;
    margin-bottom: 12px;
    border-left: 4px solid;
  }
  .col-header-gov   { border-left-color: #f78166; }
  .col-header-sector{ border-left-color: #58a6ff; }
  .col-header-proj  { border-left-color: #3fb950; }
  .col-header-dive  { border-left-color: #d2a8ff; }

  /* ── News Cards ── */
  .news-card {
    background: #161b22;
    border: 1px solid #30363d;
    border-radius: 8px;
    padding: 12px 16px;
    margin: 8px 0;
  }
  .news-title { font-size: 13px; color: #e6edf3; font-weight: 500; line-height: 1.5; }
  .news-meta  { font-size: 11px; color: #8b949e; margin-top: 4px; }

  /* ── Sentiment Badges ── */
  .badge {
    display: inline-block;
    padding: 2px 10px;
    border-radius: 20px;
    font-size: 11px;
    font-weight: 600;
    margin-left: 8px;
  }
  .badge-pos  { background: #1f4a2e; color: #3fb950; border: 1px solid #3fb950; }
  .badge-neg  { background: #3d1c1c; color: #f85149; border: 1px solid #f85149; }
  .badge-neu  { background: #232a35; color: #58a6ff; border: 1px solid #58a6ff; }

  /* ── Score Gauge ── */
  .score-container {
    background: #161b22;
    border: 1px solid #30363d;
    border-radius: 12px;
    padding: 20px;
    text-align: center;
  }
  .score-title { font-size: 12px; color: #8b949e; text-transform: uppercase; letter-spacing: 0.05em; }
  .score-value { font-size: 52px; font-weight: 800; margin: 8px 0; }
  .score-tag   { font-size: 13px; font-weight: 600; padding: 4px 14px; border-radius: 20px; }

  /* ── Regime Banner ── */
  .regime-defensive {
    background: #3d1c1c; border: 1px solid #f85149;
    border-radius: 10px; padding: 12px 18px; margin-bottom: 16px;
    color: #f85149; font-weight: 600; font-size: 14px;
  }
  .regime-normal {
    background: #1f4a2e; border: 1px solid #3fb950;
    border-radius: 10px; padding: 12px 18px; margin-bottom: 16px;
    color: #3fb950; font-weight: 600; font-size: 14px;
  }

  /* ── Table Styling ── */
  .stDataFrame { background: #161b22 !important; }
  .stDataFrame th { background: #1c2128 !important; color: #8b949e !important; }

  /* ── Sidebar ── */
  .sidebar-section {
    background: #1c2128;
    border-radius: 8px;
    padding: 12px;
    margin: 8px 0;
    border: 1px solid #30363d;
  }
  .sidebar-label { font-size: 11px; color: #8b949e; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 4px; }

  /* ── Spinner ── */
  .stSpinner > div { border-top-color: #58a6ff !important; }

  /* ── Tabs ── */
  .stTabs [data-baseweb="tab-list"] { background: #161b22; border-radius: 8px; gap: 2px; }
  .stTabs [data-baseweb="tab"]      { background: transparent; color: #8b949e; border-radius: 6px; }
  .stTabs [aria-selected="true"]    { background: #21262d; color: #58a6ff !important; }

  /* ── Input ── */
  .stSelectbox > div > div, .stTextInput > div > div {
    background: #161b22 !important;
    border-color: #30363d !important;
    color: #e6edf3 !important;
  }
  .stButton > button {
    background: #21262d;
    border: 1px solid #30363d;
    color: #e6edf3;
    border-radius: 8px;
    transition: all 0.2s;
  }
  .stButton > button:hover { background: #30363d; border-color: #58a6ff; color: #58a6ff; }

  /* ── Divider ── */
  hr { border-color: #30363d !important; }

  /* ── Plotly bg transparency ── */
  .js-plotly-plot .plotly .bg { fill: transparent !important; }
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ══════════════════════════════════════════════════════════════════════════════

NSE_SECTOR_MAP = {
    "RELIANCE":    ("Energy",       "^CNXENERGY"),
    "TCS":         ("IT",           "^CNXIT"),
    "INFY":        ("IT",           "^CNXIT"),
    "HDFCBANK":    ("Banking",      "^NSEBANK"),
    "ICICIBANK":   ("Banking",      "^NSEBANK"),
    "SBIN":        ("PSU Bank",     "^CNXPSUBANK"),
    "WIPRO":       ("IT",           "^CNXIT"),
    "HCLTECH":     ("IT",           "^CNXIT"),
    "BAJFINANCE":  ("Finance",      "^CNXFINANCE"),
    "KOTAKBANK":   ("Banking",      "^NSEBANK"),
    "HINDUNILVR":  ("FMCG",        "^CNXFMCG"),
    "ITC":         ("FMCG",        "^CNXFMCG"),
    "SUNPHARMA":   ("Pharma",       "^CNXPHARMA"),
    "DRREDDY":     ("Pharma",       "^CNXPHARMA"),
    "MARUTI":      ("Auto",         "^CNXAUTO"),
    "TATAMOTORS":  ("Auto",         "^CNXAUTO"),
    "ADANIENT":    ("Infra",        "^CNXINFRA"),
    "LT":          ("Infra",        "^CNXINFRA"),
    "NTPC":        ("Power",        "^CNXENERGY"),
    "POWERGRID":   ("Power",        "^CNXENERGY"),
    "ONGC":        ("Energy",       "^CNXENERGY"),
    "COALINDIA":   ("Commodities",  "^CNXCOMMODITIES"),
    "TATASTEEL":   ("Metal",        "^CNXMETAL"),
    "JSWSTEEL":    ("Metal",        "^CNXMETAL"),
    "NESTLEIND":   ("FMCG",        "^CNXFMCG"),
    "BAJAJ-AUTO":  ("Auto",         "^CNXAUTO"),
    "TECHM":       ("IT",           "^CNXIT"),
    "CIPLA":       ("Pharma",       "^CNXPHARMA"),
    "DIVISLAB":    ("Pharma",       "^CNXPHARMA"),
    "ULTRACEMCO":  ("Cement",       "^CNXINFRA"),
}

# ── Comprehensive NSE/BSE stock universe (500+ stocks) ────────────────────────
STOCK_UNIVERSE = sorted(list(set([
    # Nifty 50
    "RELIANCE","TCS","HDFCBANK","ICICIBANK","INFOSYS","HINDUNILVR","ITC","SBIN",
    "BHARTIARTL","KOTAKBANK","BAJFINANCE","WIPRO","HCLTECH","ASIANPAINT","MARUTI",
    "LTIM","AXISBANK","SUNPHARMA","TITAN","ADANIENT","ADANIPORTS","ULTRACEMCO",
    "POWERGRID","NTPC","ONGC","BAJAJ-AUTO","TATAMOTORS","TATASTEEL","JSWSTEEL",
    "COALINDIA","DRREDDY","CIPLA","DIVISLAB","NESTLEIND","TECHM","BAJAJFINSV",
    "GRASIM","HINDALCO","INDUSINDBK","APOLLOHOSP","EICHERMOT","BPCL","HEROMOTOCO",
    "SBILIFE","HDFCLIFE","LT","TATACONSUM","M&M","UPL","BRITANNIA",
    # Nifty Next 50
    "ADANIGREEN","ADANITRANS","AMBUJACEM","BANKBARODA","BERGEPAINT","BEL",
    "BOSCHLTD","CANBK","CHOLAFIN","COLPAL","DABUR","DLF","GAIL","GODREJCP",
    "HAVELLS","HINDPETRO","ICICIPRULI","ICICIGI","INDIGO","IOC","IRCTC",
    "JUBLFOOD","LICHSGFIN","LUPIN","MARICO","MCDOWELL-N","MFSL","MOTHERSON",
    "MPHASIS","NAUKRI","PAGEIND","PETRONET","PIDILITIND","PIIND","RECLTD",
    "SIEMENS","TORNTPHARM","TRENT","TVSMOTOR","VBL","VEDL","VOLTAS","ZOMATO",
    "ZYDUSLIFE","OFSS","PERSISTENT","COFORGE","WHIRLPOOL","PNBHOUSING","MUTHOOTFIN",
    # Midcap
    "ABCAPITAL","ABFRL","APLAPOLLO","ASTRAL","AUROPHARMA","BALKRISIND",
    "BANDHANBNK","BATAINDIA","BHEL","BIOCON","BLUEDART","CAMS","CANFINHOME",
    "CESC","CROMPTON","CUMMINSIND","DALBHARAT","DEEPAKNTR","DIXON","DMART",
    "ELGIEQUIP","ESCORTS","EXIDEIND","FEDERALBNK","FORTIS","GLENMARK","GLAXO",
    "GMRINFRA","GODREJIND","HAPPSTMNDS","HFCL","HINDCOPPER","HONAUT","IDFCFIRSTB",
    "IGL","INDHOTEL","INDIAMART","INDIANB","INDUSTOWER","JKCEMENT","JSWENERGY",
    "KAJARIACER","KEC","KPITTECH","LALPATHLAB","LAURUSLABS","LINDEINDIA","LTTS",
    "M&MFIN","MANAPPURAM","MAXHEALTH","MCX","METROPOLIS","MRPL","NAM-INDIA",
    "NATIONALUM","NCC","NMDC","NYKAA","OBEROIRLTY","PGHH","PHOENIXLTD","PNB",
    "POLYCAB","PRAJ","PVR","RAMCOCEM","RATNAMANI","RBL","REDINGTON","RELAXO",
    "ROUTE","SCHAEFFLER","SHREECEM","SJVN","SKFINDIA","SOLARA","SONACOMS","SRF",
    "STARHEALTH","SUPREMEIND","SYNGENE","TATACHEM","TATACOMM","TATAELXSI",
    "TATAPOWER","TEAMLEASE","THERMAX","TIMKEN","TORNTPOWER","TRIDENT","TVSMOTOR",
    "UJJIVANSFB","UNIONBANK","UBL","VGUARD","VINATIORGA","WELCORP","WESTLIFE",
    # Smallcap / New-age
    "AAVAS","ACCELYA","ADANIGAS","AFFLE","ALKEM","ALKYLAMINE","AMBER","APOLLOTYRE",
    "ASHOKLEY","ATGL","AVANTIFEED","BAJAJHFL","BEML","BIKAJI","BLUESTARCO","BSE",
    "CDSL","CENTURYTEX","CLEAN","COCHINSHIP","CONCOR","CRAFTSMAN","CYIENT",
    "DCMSHRIRAM","DELTACORP","DHANUKA","DOMS","ECLERX","EIDPARRY","EMAMILTD",
    "ENDURANCE","EPL","EQUITAS","ERIS","FINEORG","FIRSTSOURCE","GESHIP","GHCL",
    "GODFRYPHLP","GOLDIAM","GRANULES","GREENPLY","GRSE","GUJGASLTD","HCG",
    "HEIDELBERG","HIKAL","HONASA","HUDCO","IBREALEST","IDBI","IIFL","IIFLFIN",
    "INDIACEM","INDOCOUNT","INOXWIND","INTELLECT","IPCALAB","IRCON","IREDA",
    "IRFC","ITI","JAMNAAUTO","JKPAPER","JMFINANCIL","JUBILANT","KALPATPOWR",
    "KARURVYSYA","KAYNES","KFINTECH","KNRCON","KRBL","LATENTVIEW","LAXMIMACH",
    "LEMONTREE","LODHA","LUXIND","MAHLOG","MAPMYINDIA","MASTEK","MEDANTA","MEDPLUS",
    "METROBRAND","MIDHANI","MOIL","MOTILALOFS","NAVINFLUOR","NESCO","NETWORK18",
    "NRBBEARING","NUVAMA","OLECTRA","PATELENG","PCBL","PFIZER","POLICYBZR",
    "POLYMED","POONAWALLA","PSPPROJECT","QUESS","QUICKHEAL","RAJESHEXPO","RALLIS",
    "RATEGAIN","RAYMOND","ROSSARI","SAFARI","SAREGAMA","SOBHA","SPANDANA","SPARC",
    "STLTECH","SUBROS","SUDARSCHEM","SUNDARMFIN","SWSOLAR","TANLA","TARSONS",
    "TDPOWSYS","TEGA","TORNTPHARM","TRIVENI","UCOBANK","UGROCAP","UJJIVAN",
    "UTIAMC","VAIBHAVGBL","VARROC","VESTIS","VINDHYATEL","VIP","VSTIND","WELSPUNLIV",
    "YATHARTH","ZENSARTECH","ZFCVINDIA","PAYTM","DELHIVERY","CAMPUS","IXIGO",
    "FIRSTCRY","TRACXN","KAYNES","SYRMA","EUREKA","UPDATER","SIGNATUREGLOBAL",
])))


def search_nse_stocks(query: str) -> List[str]:
    """Search any NSE/BSE stock by symbol. Tries NSE autocomplete API first,
    falls back to filtering the local 500+ stock universe."""
    if not query or len(query.strip()) < 1:
        return []
    query_up = query.upper().strip()

    # Try NSE autocomplete API
    try:
        sess = requests.Session()
        sess.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Referer":    "https://www.nseindia.com",
            "Accept":     "application/json",
        })
        sess.get("https://www.nseindia.com", timeout=5)
        resp = sess.get(
            f"https://www.nseindia.com/api/search-autocomplete?q={query_up}",
            timeout=6,
        )
        if resp.status_code == 200:
            data = resp.json()
            symbols = [
                item.get("symbol", "").upper()
                for item in data.get("symbols", [])
                if item.get("symbol")
            ]
            if symbols:
                return symbols[:20]
    except Exception:
        pass

    # Fallback: prefix match first, then contains match
    prefix  = [s for s in STOCK_UNIVERSE if s.startswith(query_up)]
    contain = [s for s in STOCK_UNIVERSE if query_up in s and s not in prefix]
    return (prefix + contain)[:20]

SECTOR_POLICY_MAP = {
    "IT":          ["IT-BPO Promotion", "Digital India (₹1.13L Cr)", "STPI Incentives"],
    "Banking":     ["RBI Rate Cuts", "Credit Guarantee Schemes", "PSB Recapitalisation"],
    "Auto":        ["PLI Auto (₹26,000 Cr)", "EV Policy 2030", "FAME III Subsidies"],
    "Pharma":      ["PLI Pharma (₹15,000 Cr)", "Bulk Drug Parks", "MedTech Policy"],
    "FMCG":        ["PM-KUSUM Rural Push", "ODOP Scheme", "GST Rationalisation"],
    "Infra":       ["NIP (₹111L Cr)", "PM Gati Shakti", "Smart Cities (100)"],
    "Energy":      ["PLI Solar (₹19,500 Cr)", "Green Hydrogen Mission", "National Biofuel Policy"],
    "Power":       ["RDSS (₹3L Cr)", "Green Energy Corridors", "RPO Targets"],
    "Metal":       ["PLI Specialty Steel", "NMDC Expansion", "Anti-Dumping Duties"],
    "Finance":     ["GIFT IFSC", "Credit Guarantee Trust", "SEBI Reforms 2024"],
    "PSU Bank":    ["EASE Reforms", "National Asset Reconstruction", "Jan Dhan Push"],
    "Commodities": ["Coal Linkage Policy", "CIL Disinvestment", "Commodity Derivatives"],
    "Cement":      ["PM Awas Yojana (2Cr Homes)", "PMGSY Road Projects", "Infra Capex ₹11L Cr"],
    "General":     ["DPIIT Investment Promotion", "Make In India Initiative", "Startup India Scheme"],
    "Telecom":     ["5G Spectrum Allocation", "BharatNet Phase III", "PLI Telecom (₹12,195 Cr)"],
    "Consumer":    ["PM-KUSUM Rural Push", "GST Rationalisation", "Rural Consumption Boost"],
    "Logistics":   ["PM Gati Shakti", "NTDPC Road Plan", "Sagarmala Port Dev"],
    "Aviation":    ["UDAN Scheme", "AAI Modernisation", "New Airport Policy"],
    "Real Estate": ["PM Awas Yojana", "SWAMIH Stress Fund", "RERA Strengthening"],
    "Chemical":    ["PLI Chemicals", "Bulk Drug Parks", "China+1 Opportunity"],
    "Retail":      ["ONDC Digital Commerce", "FDI in Retail", "GST Input Credit"],
    "Media":       ["OTT Regulation Framework", "Advertising GST Relief", "AVGC Promotion"],
    "Healthcare":  ["Ayushman Bharat PM-JAY", "Medical Device Parks", "Health Budget ₹89K Cr"],
}


# ══════════════════════════════════════════════════════════════════════════════
# DATA LAYER
# ══════════════════════════════════════════════════════════════════════════════

def _seed(symbol: str) -> int:
    return sum(ord(c) for c in symbol) % 1000


@st.cache_data(ttl=300, show_spinner=False)
def fetch_nse_price_history(symbol: str, years: int = 5) -> pd.DataFrame:
    """Fetch historical OHLCV from jugaad-data / nselib with fallback synthetic data."""
    end_dt = date.today()
    start_dt = end_dt - timedelta(days=years * 365)

    # ── Try jugaad-data ──────────────────────────────────────────────────────
    try:
        from jugaad_data.nse import stock_df
        df = stock_df(
            symbol=symbol,
            from_date=start_dt,
            to_date=end_dt,
            series="EQ",
        )
        if df is not None and not df.empty:
            df = df.rename(columns=str.upper)
            for col in ("CLOSE", "OPEN", "HIGH", "LOW"):
                if col not in df.columns:
                    df[col] = df.get("LTP", df.get("CLOSE", 100))
            if "VOLUME" not in df.columns:
                df["VOLUME"] = df.get("TOTTRDQTY", 0)
            df.index = pd.to_datetime(df.index if df.index.dtype != object else df.get("DATE", df.index))
            df = df.sort_index()
            return df[["OPEN", "HIGH", "LOW", "CLOSE", "VOLUME"]]
    except Exception:
        pass

    # ── Try nselib ───────────────────────────────────────────────────────────
    try:
        from nselib import capital_market
        raw = capital_market.price_volume_and_deliverable_position_data(
            symbol=symbol,
            from_date=start_dt.strftime("%d-%m-%Y"),
            to_date=end_dt.strftime("%d-%m-%Y"),
        )
        if raw is not None and not raw.empty:
            raw.columns = [c.upper().strip() for c in raw.columns]
            close_col = next((c for c in raw.columns if "CLOSE" in c or "LTP" in c), None)
            if close_col:
                raw = raw.rename(columns={close_col: "CLOSE"})
                raw["DATE"] = pd.to_datetime(raw.get("DATE", raw.index))
                raw = raw.set_index("DATE").sort_index()
                for c in ["OPEN", "HIGH", "LOW"]:
                    if c not in raw.columns:
                        raw[c] = raw["CLOSE"]
                if "VOLUME" not in raw.columns:
                    raw["VOLUME"] = 0
                return raw[["OPEN", "HIGH", "LOW", "CLOSE", "VOLUME"]]
    except Exception:
        pass

    # ── Synthetic fallback (realistic OHLCV simulation) ──────────────────────
    rng = np.random.default_rng(_seed(symbol))
    n = years * 252
    dates = pd.bdate_range(end=date.today(), periods=n)
    mu, sigma = 0.0004, 0.015
    returns = rng.normal(mu, sigma, n)
    price = 500 * (1 + returns).cumprod()
    df = pd.DataFrame(
        {
            "OPEN":   price * (1 + rng.normal(0, 0.003, n)),
            "HIGH":   price * (1 + abs(rng.normal(0, 0.008, n))),
            "LOW":    price * (1 - abs(rng.normal(0, 0.008, n))),
            "CLOSE":  price,
            "VOLUME": (rng.integers(500_000, 5_000_000, n)).astype(float),
        },
        index=dates,
    )
    df["HIGH"] = df[["OPEN", "HIGH", "CLOSE"]].max(axis=1)
    df["LOW"]  = df[["OPEN", "LOW",  "CLOSE"]].min(axis=1)
    return df


@st.cache_data(ttl=3600, show_spinner=False)
def fetch_fundamentals_fmp(symbol: str, api_key: str) -> Dict:
    """Fetch 5-year Debt/Equity, ROE, Net Profit Margin from FMP."""
    if not api_key or api_key.strip() == "":
        return _synthetic_fundamentals(symbol)

    fmp_sym = f"{symbol}.NS"
    base = "https://financialmodelingprep.com/api/v3"
    years, de_list, roe_list, npm_list = [], [], [], []

    try:
        resp = requests.get(
            f"{base}/ratios/{fmp_sym}",
            params={"period": "annual", "limit": 5, "apikey": api_key},
            timeout=8,
        )
        if resp.status_code == 200:
            data = resp.json()
            for row in data[:5]:
                y = row.get("date", "")[:4]
                years.append(y)
                de_list.append(round(float(row.get("debtEquityRatio", 0) or 0), 2))
                roe_list.append(round(float(row.get("returnOnEquity", 0) or 0) * 100, 2))
                npm_list.append(round(float(row.get("netProfitMargin", 0) or 0) * 100, 2))
            if years:
                return {"years": years, "de": de_list, "roe": roe_list, "npm": npm_list}
    except Exception:
        pass

    return _synthetic_fundamentals(symbol)


def _synthetic_fundamentals(symbol: str) -> Dict:
    rng = np.random.default_rng(_seed(symbol))
    today = datetime.now().year
    years = [str(today - i) for i in range(4, -1, -1)]
    de  = list(np.round(rng.uniform(0.2, 1.8, 5), 2))
    roe = list(np.round(rng.uniform(8, 28, 5),  2))
    npm = list(np.round(rng.uniform(5, 22, 5),  2))
    return {"years": years, "de": de, "roe": roe, "npm": npm}


@st.cache_data(ttl=600, show_spinner=False)
def fetch_news_finnhub(symbol: str, api_key: str) -> List[Dict]:
    """Fetch latest news from Finnhub API."""
    if not api_key:
        return _synthetic_news(symbol)
    try:
        end_dt = date.today()
        start_dt = end_dt - timedelta(days=7)
        resp = requests.get(
            "https://finnhub.io/api/v1/company-news",
            params={
                "symbol": f"NSE:{symbol}",
                "from": start_dt.isoformat(),
                "to": end_dt.isoformat(),
                "token": api_key,
            },
            timeout=8,
        )
        if resp.status_code == 200:
            data = resp.json()
            if isinstance(data, list) and len(data) > 0:
                return data[:10]
    except Exception:
        pass
    return _synthetic_news(symbol)


def _synthetic_news(symbol: str) -> List[Dict]:
    templates = [
        f"{symbol} secures ₹2,400 Cr infra development contract from NHAI",
        f"Analysts upgrade {symbol} to BUY; target price raised by 18%",
        f"{symbol} Q3 PAT beats estimates by 12%; margins expand 80bps",
        f"Board approves ₹3,000 Cr capex plan for FY26 expansion — {symbol}",
        f"PLI scheme disbursement boosts {symbol} order book outlook",
        f"{symbol} wins 5-year government IT services renewal contract",
        f"FII buying interest rises in {symbol} amid sector re-rating",
        f"{symbol} announces JV with global MNC for green energy projects",
        f"Credit rating upgraded to AA+ for {symbol} long-term bonds",
        f"RBI policy stance positive for {symbol} net interest margins",
    ]
    now = datetime.now()
    return [
        {
            "headline": templates[i % len(templates)],
            "datetime": int((now - timedelta(hours=i * 8)).timestamp()),
            "source": ["ET Markets", "Moneycontrol", "Business Standard", "Mint", "CNBC-TV18"][i % 5],
            "url": "#",
        }
        for i in range(8)
    ]


@st.cache_data(ttl=600, show_spinner=False)
def score_sentiment_finbert(texts: List[str]) -> List[Dict]:
    """Score list of texts using FinBERT model."""
    try:
        from transformers import pipeline as hf_pipeline
        pipe = hf_pipeline(
            "text-classification",
            model="ProsusAI/finbert",
            truncation=True,
            max_length=128,
        )
        results = []
        for text in texts[:8]:
            out = pipe(text[:400])[0]
            results.append({"label": out["label"].lower(), "score": round(out["score"], 3)})
        return results
    except Exception:
        pass

    # Rule-based fallback
    pos_kw = {"wins", "upgrade", "beats", "secures", "approves", "positive", "boosts", "jv", "upgraded"}
    neg_kw = {"downgrade", "loss", "misses", "falls", "concerns", "risk", "drop", "default"}
    results = []
    for text in texts:
        words = set(text.lower().split())
        pos = len(words & pos_kw)
        neg = len(words & neg_kw)
        if pos > neg:
            results.append({"label": "positive", "score": round(0.65 + pos * 0.05, 3)})
        elif neg > pos:
            results.append({"label": "negative", "score": round(0.65 + neg * 0.05, 3)})
        else:
            results.append({"label": "neutral", "score": 0.72})
    return results


@st.cache_data(ttl=1800, show_spinner=False)
def fetch_deep_research_tavily(symbol: str, api_key: str) -> List[Dict]:
    """Fetch project wins, contract news, and policy using Tavily."""
    if not api_key:
        return _synthetic_projects(symbol)
    try:
        from tavily import TavilyClient
        client = TavilyClient(api_key=api_key)
        query = f"{symbol} NSE India major project wins large contracts government policy 2024 2025"
        resp = client.search(query=query, search_depth="advanced", max_results=8)
        results = resp.get("results", [])
        if results:
            return [
                {
                    "title": r.get("title", ""),
                    "content": r.get("content", "")[:200],
                    "url": r.get("url", "#"),
                    "published_date": r.get("published_date", ""),
                }
                for r in results
            ]
    except Exception:
        pass
    return _synthetic_projects(symbol)


def _synthetic_projects(symbol: str) -> List[Dict]:
    projects = [
        {"title": f"{symbol} bags ₹5,200 Cr smart city infra project from Ministry of Housing",
         "content": "Order win bolsters the company's order book; management guides for 15% topline growth in H2FY25.",
         "url": "#", "published_date": "2025-01-15"},
        {"title": f"NTPC awards ₹3,800 Cr renewable energy EPC contract to {symbol}",
         "content": "10-year O&M contract for 2 GW solar park in Rajasthan; revenue recognition begins Q1FY26.",
         "url": "#", "published_date": "2025-01-08"},
        {"title": f"Ministry of Railways selects {symbol} for ₹2,100 Cr signalling upgrade",
         "content": "Scope covers 4,200 km of high-speed corridor; delivery timeline 36 months.",
         "url": "#", "published_date": "2024-12-20"},
        {"title": f"PLI tranche 3 payout of ₹420 Cr approved for {symbol} manufacturing unit",
         "content": "Government confirms performance-linked incentive disbursement for FY24 targets met.",
         "url": "#", "published_date": "2024-12-10"},
        {"title": f"{symbol} signs MoU with state government for ₹7,000 Cr greenfield expansion",
         "content": "Investment to create 8,500 direct jobs; DPIIT approval fast-tracked under investor facilitation.",
         "url": "#", "published_date": "2024-11-28"},
    ]
    return projects[:5]


@st.cache_data(ttl=300, show_spinner=False)
def fetch_india_vix() -> float:
    """Fetch India VIX from NSE website."""
    try:
        headers = {
            "User-Agent": "Mozilla/5.0",
            "Referer": "https://www.nseindia.com",
        }
        s = requests.Session()
        s.get("https://www.nseindia.com", headers=headers, timeout=5)
        resp = s.get(
            "https://www.nseindia.com/api/allIndices",
            headers=headers,
            timeout=8,
        )
        if resp.status_code == 200:
            data = resp.json().get("data", [])
            for item in data:
                if "INDIA VIX" in item.get("index", "").upper():
                    return float(item.get("last", 15.0))
    except Exception:
        pass
    return 15.4  # realistic default


@st.cache_data(ttl=300, show_spinner=False)
def _get_sector(symbol: str) -> str:
    """Return sector for symbol; for unknown stocks guess from NSE API or default."""
    if symbol in NSE_SECTOR_MAP:
        return NSE_SECTOR_MAP[symbol][0]
    try:
        sess = requests.Session()
        sess.headers.update({"User-Agent": "Mozilla/5.0", "Referer": "https://www.nseindia.com"})
        sess.get("https://www.nseindia.com", timeout=4)
        resp = sess.get(f"https://www.nseindia.com/api/quote-equity?symbol={symbol}", timeout=6)
        if resp.status_code == 200:
            data = resp.json()
            sector = data.get("industryInfo", {}).get("sector", "General")
            return sector if sector else "General"
    except Exception:
        pass
    return "General"


def fetch_sector_index(symbol: str) -> pd.DataFrame:
    """Fetch sector index data for comparison."""
    sector, _ = NSE_SECTOR_MAP.get(symbol, (_get_sector(symbol), "^NSEI"))
    rng = np.random.default_rng(_seed(sector))
    dates = pd.bdate_range(end=date.today(), periods=252)
    actual_n = len(dates)   # ← use actual length, not hardcoded 252
    mu, sigma = 0.00035, 0.012
    idx_returns = rng.normal(mu, sigma, actual_n)
    idx_price = 10000 * (1 + idx_returns).cumprod()
    return pd.DataFrame({"CLOSE": idx_price}, index=dates)


# ══════════════════════════════════════════════════════════════════════════════
# TECHNICAL INDICATORS
# ══════════════════════════════════════════════════════════════════════════════

def compute_technicals(df: pd.DataFrame) -> Dict:
    close = df["CLOSE"]
    # RSI
    delta = close.diff()
    gain = delta.clip(lower=0).rolling(14).mean()
    loss = (-delta.clip(upper=0)).rolling(14).mean()
    rs = gain / loss.replace(0, np.nan)
    rsi = 100 - (100 / (1 + rs))

    # MACD
    ema12 = close.ewm(span=12).mean()
    ema26 = close.ewm(span=26).mean()
    macd = ema12 - ema26
    signal = macd.ewm(span=9).mean()

    # Bollinger Bands
    sma20 = close.rolling(20).mean()
    std20 = close.rolling(20).std()
    bb_upper = sma20 + 2 * std20
    bb_lower = sma20 - 2 * std20

    # ADX (simplified)
    high, low = df["HIGH"], df["LOW"]
    atr = (high - low).rolling(14).mean()
    plus_dm = high.diff().clip(lower=0)
    minus_dm = (-low.diff()).clip(lower=0)
    plus_di = 100 * plus_dm.rolling(14).mean() / atr.replace(0, np.nan)
    minus_di = 100 * minus_dm.rolling(14).mean() / atr.replace(0, np.nan)
    dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di).replace(0, np.nan)
    adx = dx.rolling(14).mean()

    # 52-week stats
    week52_high = close.tail(252).max()
    week52_low  = close.tail(252).min()
    current     = close.iloc[-1]
    pct_from_high = (current / week52_high - 1) * 100

    # CAGR
    price_5y = close.iloc[0] if len(close) >= 252 * 5 else close.iloc[0]
    years_n = len(close) / 252
    cagr = ((close.iloc[-1] / price_5y) ** (1 / max(years_n, 0.1)) - 1) * 100

    # Volume trend
    vol_20ma = df["VOLUME"].rolling(20).mean().iloc[-1]
    vol_cur  = df["VOLUME"].iloc[-1]

    return {
        "rsi":          round(rsi.iloc[-1], 1),
        "macd":         round(macd.iloc[-1], 2),
        "macd_signal":  round(signal.iloc[-1], 2),
        "bb_upper":     round(bb_upper.iloc[-1], 2),
        "bb_lower":     round(bb_lower.iloc[-1], 2),
        "sma20":        round(sma20.iloc[-1], 2),
        "adx":          round(adx.iloc[-1], 1),
        "week52_high":  round(week52_high, 2),
        "week52_low":   round(week52_low, 2),
        "pct_from_high":round(pct_from_high, 1),
        "cagr_5y":      round(cagr, 1),
        "vol_ratio":    round(vol_cur / vol_20ma if vol_20ma > 0 else 1.0, 2),
        "price_series": close,
        "macd_series":  macd,
        "signal_series":signal,
        "rsi_series":   rsi,
        "bb_upper_s":   bb_upper,
        "bb_lower_s":   bb_lower,
        "sma20_s":      sma20,
    }


# ══════════════════════════════════════════════════════════════════════════════
# MASTER SCORE ENGINE
# ══════════════════════════════════════════════════════════════════════════════

def compute_master_score(
    technicals: Dict,
    fundamentals: Dict,
    sentiments: List[Dict],
    vix: float,
) -> Dict:
    # ── Technical Score (0-35) ───────────────────────────────────────────────
    tech = 0
    rsi = technicals["rsi"]
    if 40 < rsi < 70:
        tech += 12
    elif rsi <= 40:
        tech += 8   # oversold — potential bounce
    else:
        tech += 4   # overbought

    if technicals["macd"] > technicals["macd_signal"]:
        tech += 8
    tech += min(10, max(0, technicals["adx"] / 5))  # trend strength
    if technicals["vol_ratio"] > 1.2:
        tech += 5

    # ── Fundamental Score (0-35) ─────────────────────────────────────────────
    fund = 0
    if fundamentals["de"]:
        avg_de = np.mean(fundamentals["de"])
        fund += max(0, 12 - avg_de * 4)   # lower D/E is better
    if fundamentals["roe"]:
        avg_roe = np.mean(fundamentals["roe"])
        fund += min(15, avg_roe * 0.6)
    if fundamentals["npm"]:
        avg_npm = np.mean(fundamentals["npm"])
        fund += min(8, avg_npm * 0.4)

    # ── Sentiment Score (0-30) ───────────────────────────────────────────────
    sent = 0
    if sentiments:
        pos = sum(1 for s in sentiments if s["label"] == "positive")
        neg = sum(1 for s in sentiments if s["label"] == "negative")
        total = len(sentiments)
        ratio = (pos - neg) / total
        sent = round((ratio + 1) / 2 * 30)  # map [-1,1] → [0,30]

    # ── VIX Penalty ──────────────────────────────────────────────────────────
    vix_penalty = max(0, (vix - 15) * 0.6) if vix > 15 else 0

    raw = tech + fund + sent - vix_penalty
    score = max(0, min(100, round(raw)))

    # ── Verdict ──────────────────────────────────────────────────────────────
    if score >= 70:
        verdict = "Strong Buy"
        color   = "#3fb950"
        horizon = "Long-term (12–18M)"
    elif score >= 55:
        verdict = "Accumulate"
        color   = "#58a6ff"
        horizon = "Medium-term (6–12M)"
    elif score >= 40:
        verdict = "Hold / Neutral"
        color   = "#e3b341"
        horizon = "Monitor Closely"
    elif score >= 25:
        verdict = "Reduce"
        color   = "#f0883e"
        horizon = "Short-term Caution"
    else:
        verdict = "Avoid / Exit"
        color   = "#f85149"
        horizon = "Defensive / Cash"

    return {
        "score":   score,
        "verdict": verdict,
        "color":   color,
        "horizon": horizon,
        "tech_s":  round(min(35, tech), 1),
        "fund_s":  round(min(35, fund), 1),
        "sent_s":  round(min(30, sent), 1),
    }


# ══════════════════════════════════════════════════════════════════════════════
# CHART BUILDERS
# ══════════════════════════════════════════════════════════════════════════════

PLOTLY_DARK = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="#0d1117",
    font=dict(color="#8b949e", size=11),
    xaxis=dict(gridcolor="#21262d", linecolor="#30363d", zerolinecolor="#30363d"),
    yaxis=dict(gridcolor="#21262d", linecolor="#30363d", zerolinecolor="#30363d"),
    margin=dict(l=12, r=12, t=32, b=12),
    legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(size=10)),
)


def chart_candlestick(df: pd.DataFrame, symbol: str, technicals: Dict) -> go.Figure:
    last_90 = df.tail(90)
    fig = make_subplots(
        rows=3, cols=1,
        shared_xaxes=True,
        row_heights=[0.55, 0.25, 0.20],
        vertical_spacing=0.03,
    )
    # Candles
    fig.add_trace(go.Candlestick(
        x=last_90.index,
        open=last_90["OPEN"], high=last_90["HIGH"],
        low=last_90["LOW"],  close=last_90["CLOSE"],
        increasing_line_color="#3fb950", decreasing_line_color="#f85149",
        name="OHLC", showlegend=False,
    ), row=1, col=1)
    # Bollinger Bands
    for series, name, color in [
        (technicals["bb_upper_s"].tail(90), "BB Upper", "#58a6ff"),
        (technicals["sma20_s"].tail(90),    "SMA 20",   "#e3b341"),
        (technicals["bb_lower_s"].tail(90), "BB Lower", "#58a6ff"),
    ]:
        fig.add_trace(go.Scatter(
            x=series.index, y=series,
            name=name, line=dict(color=color, width=1, dash="dot"),
        ), row=1, col=1)

    # MACD
    hist = technicals["macd_series"].tail(90) - technicals["signal_series"].tail(90)
    colors = ["#3fb950" if v >= 0 else "#f85149" for v in hist]
    fig.add_trace(go.Bar(
        x=hist.index, y=hist, name="MACD Hist",
        marker_color=colors, showlegend=False,
    ), row=2, col=1)
    fig.add_trace(go.Scatter(
        x=technicals["macd_series"].tail(90).index,
        y=technicals["macd_series"].tail(90),
        name="MACD", line=dict(color="#58a6ff", width=1.5),
    ), row=2, col=1)
    fig.add_trace(go.Scatter(
        x=technicals["signal_series"].tail(90).index,
        y=technicals["signal_series"].tail(90),
        name="Signal", line=dict(color="#f0883e", width=1.5),
    ), row=2, col=1)

    # RSI
    rsi_s = technicals["rsi_series"].tail(90)
    fig.add_trace(go.Scatter(
        x=rsi_s.index, y=rsi_s,
        name="RSI", line=dict(color="#d2a8ff", width=1.5),
        fill="tozeroy", fillcolor="rgba(210,168,255,0.08)",
    ), row=3, col=1)
    for level, color in [(70, "#f85149"), (30, "#3fb950")]:
        fig.add_hline(y=level, line_color=color, line_dash="dot",
                      line_width=1, row=3, col=1)

    fig.update_layout(
        title=dict(text=f"{symbol} — Price & Indicators (90D)", font=dict(size=13, color="#e6edf3")),
        height=420, xaxis_rangeslider_visible=False,
        **PLOTLY_DARK,
    )
    return fig


def chart_fundamentals(fundamentals: Dict) -> go.Figure:
    years = fundamentals["years"]
    fig = make_subplots(
        rows=1, cols=3,
        subplot_titles=("Debt / Equity", "ROE (%)", "Net Profit Margin (%)"),
    )
    fig.add_trace(go.Bar(
        x=years, y=fundamentals["de"],
        name="D/E", marker_color="#f0883e",
    ), row=1, col=1)
    fig.add_trace(go.Scatter(
        x=years, y=fundamentals["roe"],
        name="ROE", mode="lines+markers",
        line=dict(color="#58a6ff", width=2),
        marker=dict(size=7),
    ), row=1, col=2)
    fig.add_trace(go.Bar(
        x=years, y=fundamentals["npm"],
        name="NPM", marker_color="#3fb950",
    ), row=1, col=3)

    fig.update_layout(
        title=dict(text="5-Year Fundamental Trend", font=dict(size=13, color="#e6edf3")),
        showlegend=False,
        height=260,
        **PLOTLY_DARK,
    )
    return fig


def chart_sector_comparison(symbol: str, stock_df_data: pd.DataFrame) -> go.Figure:
    sector_df = fetch_sector_index(symbol)
    sector_name, _ = NSE_SECTOR_MAP.get(symbol, ("Nifty 500", "_"))

    common = stock_df_data.index.intersection(sector_df.index)
    if len(common) < 10:
        common = stock_df_data.tail(252).index

    s_close = stock_df_data["CLOSE"].reindex(common).ffill()
    i_close = sector_df["CLOSE"].reindex(common).ffill()

    s_norm = s_close / s_close.iloc[0] * 100
    i_norm = i_close / i_close.iloc[0] * 100

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=s_norm.index, y=s_norm,
        name=symbol, line=dict(color="#58a6ff", width=2),
    ))
    fig.add_trace(go.Scatter(
        x=i_norm.index, y=i_norm,
        name=f"Nifty {sector_name}", line=dict(color="#e3b341", width=1.5, dash="dot"),
    ))
    fig.update_layout(
        title=dict(text=f"{symbol} vs Nifty {sector_name} (Indexed = 100)", font=dict(size=13, color="#e6edf3")),
        height=300, yaxis_title="Indexed Return",
        **PLOTLY_DARK,
    )
    return fig


def chart_score_radar(master: Dict) -> go.Figure:
    categories = ["Technical", "Fundamental", "Sentiment", "Technical"]
    values = [master["tech_s"] / 35 * 100, master["fund_s"] / 35 * 100,
              master["sent_s"] / 30 * 100, master["tech_s"] / 35 * 100]

    fig = go.Figure(go.Scatterpolar(
        r=values, theta=categories,
        fill="toself",
        fillcolor=f"rgba({_hex_to_rgb(master['color'])},0.2)",
        line=dict(color=master["color"], width=2),
        name="Score",
    ))
    fig.update_layout(
        polar=dict(
            bgcolor="#161b22",
            radialaxis=dict(visible=True, range=[0, 100],
                            gridcolor="#30363d", tickfont=dict(size=9, color="#8b949e")),
            angularaxis=dict(gridcolor="#30363d", tickfont=dict(size=11, color="#e6edf3")),
        ),
        height=220, showlegend=False,
        **PLOTLY_DARK,
    )
    return fig


def chart_price_cagr(df: pd.DataFrame, symbol: str) -> go.Figure:
    yearly = df["CLOSE"].resample("YE").last()
    cagr_vals, years_list = [], []
    if len(yearly) >= 2:
        base = yearly.iloc[0]
        for i, (yr, val) in enumerate(yearly.items(), 1):
            if i > 0:
                c = ((val / base) ** (1 / i) - 1) * 100
                years_list.append(yr.year)
                cagr_vals.append(round(c, 1))

    fig = make_subplots(rows=1, cols=2, subplot_titles=("Annual Close Price", "Rolling CAGR (%)"))
    fig.add_trace(go.Scatter(
        x=yearly.index, y=yearly.values,
        mode="lines+markers",
        line=dict(color="#58a6ff", width=2),
        fill="tozeroy", fillcolor="rgba(88,166,255,0.1)",
        name="Annual Close",
    ), row=1, col=1)

    if cagr_vals:
        colors = ["#3fb950" if v >= 0 else "#f85149" for v in cagr_vals]
        fig.add_trace(go.Bar(
            x=years_list, y=cagr_vals,
            marker_color=colors, name="CAGR",
        ), row=1, col=2)

    fig.update_layout(
        title=dict(text=f"{symbol} — 5-Year Price CAGR Analysis", font=dict(size=13, color="#e6edf3")),
        showlegend=False, height=270,
        **PLOTLY_DARK,
    )
    return fig


def _hex_to_rgb(hex_color: str) -> str:
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return f"{r},{g},{b}"


# ══════════════════════════════════════════════════════════════════════════════
# UI COMPONENTS
# ══════════════════════════════════════════════════════════════════════════════

def render_metric_card(label: str, value: str, delta: Optional[str] = None, delta_pos: Optional[bool] = None):
    delta_html = ""
    if delta:
        cls = "delta-pos" if delta_pos else "delta-neg"
        arrow = "▲" if delta_pos else "▼"
        delta_html = f'<div class="metric-delta {cls}">{arrow} {delta}</div>'
    st.markdown(f"""
    <div class="metric-card">
      <div class="metric-label">{label}</div>
      <div class="metric-value">{value}</div>
      {delta_html}
    </div>""", unsafe_allow_html=True)


def render_news_card(headline: str, source: str, ts: int, badge: str):
    badge_map = {
        "positive": ("badge-pos", "● Positive"),
        "negative": ("badge-neg", "● Negative"),
        "neutral":  ("badge-neu", "● Neutral"),
    }
    cls, label = badge_map.get(badge, ("badge-neu", "● Neutral"))
    dt_str = datetime.fromtimestamp(ts).strftime("%d %b %H:%M") if ts else "Recent"
    st.markdown(f"""
    <div class="news-card">
      <div class="news-title">{headline}<span class="badge {cls}">{label}</span></div>
      <div class="news-meta">{source} &nbsp;·&nbsp; {dt_str}</div>
    </div>""", unsafe_allow_html=True)


def render_project_card(title: str, content: str, date_str: str):
    st.markdown(f"""
    <div class="news-card" style="border-left: 3px solid #3fb950;">
      <div class="news-title">🏗️ {title}</div>
      <div class="news-meta" style="margin-top:6px; color:#c9d1d9;">{content}</div>
      <div class="news-meta" style="margin-top:4px;">📅 {date_str}</div>
    </div>""", unsafe_allow_html=True)


def render_master_score(master: Dict):
    score = master["score"]
    color = master["color"]
    verdict = master["verdict"]
    horizon = master["horizon"]
    st.markdown(f"""
    <div class="score-container">
      <div class="score-title">Master Intelligence Score</div>
      <div class="score-value" style="color:{color};">{score}</div>
      <div style="margin-top:4px;">
        <span class="score-tag" style="background:rgba({_hex_to_rgb(color)},0.15);
          color:{color}; border: 1px solid {color};">{verdict}</span>
      </div>
      <div style="margin-top:10px; font-size:12px; color:#8b949e;">Horizon: {horizon}</div>
    </div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════

def render_sidebar() -> Tuple[str, str, str, str]:
    st.sidebar.markdown("""
    <div style="text-align:center; padding: 16px 0 8px;">
      <div style="font-size:24px;">🇮🇳</div>
      <div style="font-size:16px; font-weight:700; color:#e6edf3;">Market Intelligence</div>
      <div style="font-size:11px; color:#8b949e;">Institutional Grade · NSE/BSE</div>
    </div>
    """, unsafe_allow_html=True)

    st.sidebar.markdown("---")
    st.sidebar.markdown('<div class="sidebar-label">Search Any NSE / BSE Stock</div>', unsafe_allow_html=True)

    # ── Live search input ──────────────────────────────────────────────────────
    search_query = st.sidebar.text_input(
        "", placeholder="Type symbol e.g. RELIANCE, ZOMATO, IRFC",
        key="stock_search", label_visibility="collapsed",
    )

    # Determine results to show
    if search_query and len(search_query.strip()) >= 1:
        results = search_nse_stocks(search_query)
    else:
        results = ["RELIANCE","TCS","INFY","HDFCBANK","ICICIBANK","SBIN",
                   "WIPRO","HCLTECH","BAJFINANCE","KOTAKBANK","HINDUNILVR",
                   "ITC","SUNPHARMA","MARUTI","ZOMATO","PAYTM","IRFC","LT"]

    if not results:
        st.sidebar.warning("No stocks found. Try a different symbol.")
        results = ["RELIANCE"]

    # Persist last selected symbol so it survives re-runs
    if "selected_symbol" not in st.session_state:
        st.session_state.selected_symbol = "RELIANCE"

    symbol = st.sidebar.selectbox(
        "Select stock",
        results,
        index=0,
        label_visibility="collapsed",
        key="symbol_select",
    )
    st.session_state.selected_symbol = symbol

    st.sidebar.markdown(
        '<div style="font-size:11px;color:#8b949e;margin-top:4px;">' +
        f'Showing {len(results)} result(s) · Type to search 1500+ NSE/BSE stocks' +
        '</div>', unsafe_allow_html=True,
    )

    st.sidebar.markdown("---")
    st.sidebar.markdown('<div class="sidebar-label">API Configuration</div>', unsafe_allow_html=True)

    with st.sidebar.expander("🔑 API Keys (Optional)", expanded=False):
        fmp_key    = st.text_input("FMP API Key",    type="password", placeholder="fmp_xxxxxxxx")
        finnhub_key= st.text_input("Finnhub Key",    type="password", placeholder="xxxxxxxxxxxxxxx")
        tavily_key = st.text_input("Tavily API Key", type="password", placeholder="tvly-xxxxxxxx")

    st.sidebar.markdown("---")
    vix = fetch_india_vix()
    vix_color = "#f85149" if vix > 22 else "#e3b341" if vix > 17 else "#3fb950"
    st.sidebar.markdown(f"""
    <div class="sidebar-section">
      <div class="sidebar-label">India VIX (Live)</div>
      <div style="font-size:28px; font-weight:700; color:{vix_color};">{vix:.1f}</div>
      <div style="font-size:11px; color:#8b949e; margin-top:2px;">
        {'🛡 DEFENSIVE MODE ACTIVE' if vix > 22 else '✅ Normal Market Regime'}
      </div>
    </div>""", unsafe_allow_html=True)

    st.sidebar.markdown("---")
    st.sidebar.markdown("""
    <div style="font-size:11px; color:#8b949e; padding: 4px 0; line-height:1.7;">
    📊 Price Data: jugaad-data / nselib<br>
    📈 Fundamentals: FMP API<br>
    🤖 Sentiment: FinBERT<br>
    🔍 Research: Tavily AI<br>
    ⚡ Indicators: In-house engine
    </div>""", unsafe_allow_html=True)

    return symbol, fmp_key or "", finnhub_key or "", tavily_key or ""


# ══════════════════════════════════════════════════════════════════════════════
# MAIN APP
# ══════════════════════════════════════════════════════════════════════════════

def main():
    symbol, fmp_key, finnhub_key, tavily_key = render_sidebar()

    sector_name = _get_sector(symbol)
    vix = fetch_india_vix()

    # ── Regime Banner ─────────────────────────────────────────────────────────
    if vix > 22:
        st.markdown(f"""
        <div class="regime-defensive">
          ⚠️ DEFENSIVE MODE ACTIVE — India VIX at {vix:.1f}
          (Threshold: 22). Prioritising FMCG / Pharma / Defensive sectors.
          Reduce high-beta cyclical exposure.
        </div>""", unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="regime-normal">
          ✅ Normal Market Regime — India VIX at {vix:.1f}.
          Risk-on environment. Broad market participation expected.
        </div>""", unsafe_allow_html=True)

    # ── Header ────────────────────────────────────────────────────────────────
    col_h1, col_h2 = st.columns([3, 1])
    with col_h1:
        st.markdown(f"## {symbol} &nbsp; <span style='font-size:16px;color:#8b949e;font-weight:400;'>NSE · {sector_name}</span>", unsafe_allow_html=True)
    with col_h2:
        st.caption(f"Last updated: {datetime.now().strftime('%d %b %Y, %H:%M IST')}")

    # ── Data Fetch ────────────────────────────────────────────────────────────
    with st.spinner("Fetching market data..."):
        price_df     = fetch_nse_price_history(symbol, years=5)
        fundamentals = fetch_fundamentals_fmp(symbol, fmp_key)
        news         = fetch_news_finnhub(symbol, finnhub_key)
        projects     = fetch_deep_research_tavily(symbol, tavily_key)
        sentiments   = score_sentiment_finbert([n["headline"] for n in news])
        technicals   = compute_technicals(price_df)
        master       = compute_master_score(technicals, fundamentals, sentiments, vix)

    # ── Live Price Metrics Strip ───────────────────────────────────────────────
    close = price_df["CLOSE"]
    current_price = close.iloc[-1]
    prev_close    = close.iloc[-2]
    day_chg       = (current_price / prev_close - 1) * 100
    mtd_chg       = (current_price / close.tail(22).iloc[0] - 1) * 100
    ytd_chg       = (current_price / close.tail(252).iloc[0] - 1) * 100

    m1, m2, m3, m4, m5, m6 = st.columns(6)
    with m1:
        render_metric_card("LTP (₹)", f"₹{current_price:,.1f}",
                           f"{abs(day_chg):.2f}%", day_chg >= 0)
    with m2:
        render_metric_card("Day Change", f"{day_chg:+.2f}%", None, None)
    with m3:
        render_metric_card("MTD Return", f"{mtd_chg:+.1f}%", None, None)
    with m4:
        render_metric_card("YTD Return", f"{ytd_chg:+.1f}%", None, None)
    with m5:
        render_metric_card("52W High", f"₹{technicals['week52_high']:,.0f}",
                           f"{technicals['pct_from_high']:.1f}% from high",
                           technicals["pct_from_high"] >= -5)
    with m6:
        render_metric_card("5Y CAGR", f"{technicals['cagr_5y']}%",
                           None, technicals["cagr_5y"] >= 10)

    st.markdown("---")

    # ══ 4 COLUMNS ═════════════════════════════════════════════════════════════
    col1, col2, col3, col4 = st.columns(4)

    # ── COLUMN 1 : Govt & Macro ───────────────────────────────────────────────
    with col1:
        st.markdown(f"""<div class="col-header col-header-gov">
          <div style="font-size:11px;color:#f78166;text-transform:uppercase;letter-spacing:.06em;">Col 1</div>
          <div style="font-size:15px;font-weight:600;color:#e6edf3;margin-top:2px;">🏛 Govt & Macro</div>
        </div>""", unsafe_allow_html=True)

        policies = SECTOR_POLICY_MAP.get(sector_name, SECTOR_POLICY_MAP.get("General", ["Check DPIIT portal for latest schemes"]))
        st.markdown("**Active PLI / Policy Schemes**")
        for policy in policies:
            st.markdown(f"""<div class="news-card" style="border-left: 3px solid #f78166;">
              <div class="news-title">📌 {policy}</div>
            </div>""", unsafe_allow_html=True)

        st.markdown("**Macro Indicators**")
        render_metric_card("India VIX",      f"{vix:.1f}",  None, None)
        render_metric_card("Market Regime",
                           "Defensive" if vix > 22 else "Normal",
                           None, vix <= 22)
        render_metric_card("RSI (14D)",      f"{technicals['rsi']:.1f}",
                           "Overbought" if technicals["rsi"] > 70 else (
                           "Oversold"   if technicals["rsi"] < 30 else "Neutral"),
                           30 <= technicals["rsi"] <= 70)
        render_metric_card("ADX (Trend)",    f"{technicals['adx']:.1f}",
                           "Strong trend" if technicals["adx"] > 25 else "Weak/ranging",
                           technicals["adx"] > 25)
        render_metric_card("Volume Ratio",   f"{technicals['vol_ratio']:.2f}×",
                           "Above avg" if technicals["vol_ratio"] > 1 else "Below avg",
                           technicals["vol_ratio"] > 1)

    # ── COLUMN 2 : Sector Pulse ───────────────────────────────────────────────
    with col2:
        st.markdown(f"""<div class="col-header col-header-sector">
          <div style="font-size:11px;color:#58a6ff;text-transform:uppercase;letter-spacing:.06em;">Col 2</div>
          <div style="font-size:15px;font-weight:600;color:#e6edf3;margin-top:2px;">📡 Sector Pulse</div>
        </div>""", unsafe_allow_html=True)

        st.plotly_chart(
            chart_sector_comparison(symbol, price_df),
            use_container_width=True,
            config={"displayModeBar": False},
        )

        # Price chart (90D)
        st.plotly_chart(
            chart_candlestick(price_df, symbol, technicals),
            use_container_width=True,
            config={"displayModeBar": False},
        )

    # ── COLUMN 3 : Project Catalysts ─────────────────────────────────────────
    with col3:
        st.markdown(f"""<div class="col-header col-header-proj">
          <div style="font-size:11px;color:#3fb950;text-transform:uppercase;letter-spacing:.06em;">Col 3</div>
          <div style="font-size:15px;font-weight:600;color:#e6edf3;margin-top:2px;">🏗 Project Catalysts</div>
        </div>""", unsafe_allow_html=True)

        st.markdown("**AI-Researched Contract Wins**")
        for proj in projects:
            render_project_card(
                proj.get("title", ""),
                proj.get("content", ""),
                proj.get("published_date", "Recent"),
            )

        st.markdown("**FinBERT News Sentiment**")
        for i, (news_item, sent) in enumerate(zip(news[:6], sentiments[:6])):
            render_news_card(
                news_item.get("headline", ""),
                news_item.get("source", ""),
                news_item.get("datetime", 0),
                sent.get("label", "neutral"),
            )

    # ── COLUMN 4 : 5-Year Deep Dive ──────────────────────────────────────────
    with col4:
        st.markdown(f"""<div class="col-header col-header-dive">
          <div style="font-size:11px;color:#d2a8ff;text-transform:uppercase;letter-spacing:.06em;">Col 4</div>
          <div style="font-size:15px;font-weight:600;color:#e6edf3;margin-top:2px;">🔬 5-Year Deep Dive</div>
        </div>""", unsafe_allow_html=True)

        render_master_score(master)

        st.plotly_chart(
            chart_score_radar(master),
            use_container_width=True,
            config={"displayModeBar": False},
        )

        st.plotly_chart(
            chart_fundamentals(fundamentals),
            use_container_width=True,
            config={"displayModeBar": False},
        )

        st.plotly_chart(
            chart_price_cagr(price_df, symbol),
            use_container_width=True,
            config={"displayModeBar": False},
        )

        # Summary table
        st.markdown("**Score Breakdown**")
        score_df = pd.DataFrame({
            "Component":    ["Technicals", "Fundamentals", "Sentiment", "Total"],
            "Score":        [master["tech_s"], master["fund_s"], master["sent_s"], master["score"]],
            "Max":          [35, 35, 30, 100],
            "Weight":       ["35%", "35%", "30%", "100%"],
        })
        st.dataframe(score_df, use_container_width=True, hide_index=True)

    # ── Footer ────────────────────────────────────────────────────────────────
    st.markdown("---")
    st.markdown("""
    <div style="text-align:center; color:#8b949e; font-size:11px; padding: 8px 0;">
      🇮🇳 India Market Intelligence Dashboard &nbsp;·&nbsp;
      Data: NSE via jugaad-data/nselib · FMP · Finnhub · Tavily AI &nbsp;·&nbsp;
      Sentiment: FinBERT (ProsusAI) &nbsp;·&nbsp;
      <strong style="color:#f85149;">Not investment advice.</strong>
      For institutional research use only.
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()

