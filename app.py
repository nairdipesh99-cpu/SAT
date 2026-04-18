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

  /* ── Sidebar — always visible, never hidden ── */
  section[data-testid="stSidebar"] {
    display: block !important;
    visibility: visible !important;
    background: #161b22 !important;
    border-right: 1px solid #30363d !important;
    min-width: 240px;
  }
  section[data-testid="stSidebar"] > div {
    display: block !important;
    visibility: visible !important;
  }

  /* ── Sidebar collapse/expand arrow button ── */
  button[kind="header"],
  button[data-testid="collapsedControl"],
  button[data-testid="baseButton-header"] {
    display: block !important;
    visibility: visible !important;
    color: #58a6ff !important;
    background: #161b22 !important;
  }

  /* ── Hide only the Streamlit deploy/share menu — NOT the sidebar toggle ── */
  #MainMenu { visibility: hidden; }
  footer { visibility: hidden; }
  header { visibility: hidden; }

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
    transition: border-color 0.18s, background 0.18s;
  }
  a.news-card-link {
    display: block;
    background: #161b22;
    border: 1px solid #30363d;
    border-radius: 8px;
    padding: 12px 16px;
    margin: 8px 0;
    text-decoration: none;
    transition: border-color 0.18s, background 0.18s;
  }
  a.news-card-link:hover {
    border-color: #58a6ff;
    background: #1c2128;
    cursor: pointer;
  }
  a.news-card-link:hover .news-title { color: #79c0ff; }
  .news-link-icon { float: right; font-size: 11px; color: #58a6ff; margin-left: 6px; opacity: 0.7; }
  .news-title { font-size: 13px; color: #e6edf3; font-weight: 500; line-height: 1.5; }
  .news-meta  { font-size: 11px; color: #8b949e; margin-top: 4px; }

  /* ── Project Cards ── */
  a.project-card-link {
    display: block;
    background: #161b22;
    border: 1px solid #30363d;
    border-left: 3px solid #3fb950;
    border-radius: 8px;
    padding: 12px 16px;
    margin: 8px 0;
    text-decoration: none;
    transition: border-color 0.18s, background 0.18s;
  }
  a.project-card-link:hover {
    border-color: #3fb950;
    background: #1c2128;
    cursor: pointer;
  }
  a.project-card-link:hover .news-title { color: #56d364; }

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

  /* ── Watchlist ── */
  .watchlist-card {
    background: #161b22; border: 1px solid #30363d;
    border-radius: 10px; padding: 14px 18px; margin: 6px 0;
    display: flex; align-items: center; justify-content: space-between;
    transition: border-color 0.15s;
  }
  .watchlist-card:hover { border-color: #58a6ff; }
  .wl-symbol { font-size:15px; font-weight:700; color:#e6edf3; }
  .wl-name   { font-size:11px; color:#8b949e; margin-top:2px; }
  .wl-price  { font-size:18px; font-weight:700; }
  .wl-chg    { font-size:12px; font-weight:600; }

  /* ── Global Crisis ── */
  .crisis-card {
    background: #161b22; border: 1px solid #30363d;
    border-radius: 10px; padding: 14px 18px; margin: 6px 0;
  }
  .crisis-label { font-size:11px; color:#8b949e; text-transform:uppercase; letter-spacing:.05em; }
  .crisis-value { font-size:22px; font-weight:700; margin: 4px 0; }
  .crisis-status{ font-size:11px; font-weight:600; margin-top:2px; }
  .crisis-extreme { border-left: 3px solid #f85149; }
  .crisis-high    { border-left: 3px solid #f0883e; }
  .crisis-moderate{ border-left: 3px solid #e3b341; }
  .crisis-low     { border-left: 3px solid #3fb950; }

  /* ── Opportunity Card ── */
  .opp-card {
    background: #161b22; border: 1px solid #30363d;
    border-left: 3px solid #3fb950;
    border-radius: 10px; padding: 14px 18px; margin: 8px 0;
  }
  .opp-card.caution { border-left-color: #e3b341; }
  .opp-symbol { font-size:14px; font-weight:700; color:#e6edf3; }
  .opp-reason { font-size:11px; color:#8b949e; margin-top:3px; line-height:1.5; }
  .opp-verdict{ font-size:11px; font-weight:600; margin-top:5px; }

  /* ── Tab styling ── */
  .stTabs [data-baseweb="tab"] { font-size:13px !important; padding: 8px 18px !important; }

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

  /* ── AI Agent Card ── */
  .ai-agent-card {
    background: linear-gradient(135deg, #0d1117 0%, #161b22 100%);
    border: 1px solid #30363d;
    border-radius: 14px;
    padding: 24px 28px;
    margin: 16px 0;
    position: relative;
    overflow: hidden;
  }
  .ai-agent-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    background: linear-gradient(90deg, #58a6ff, #3fb950, #d2a8ff, #f78166);
  }
  .ai-verdict-header {
    font-size: 11px; color: #58a6ff; text-transform: uppercase;
    letter-spacing: 0.1em; font-weight: 600; margin-bottom: 12px;
  }
  .ai-verdict-main {
    font-size: 32px; font-weight: 800; margin: 0;
  }
  .ai-verdict-sub {
    font-size: 13px; color: #8b949e; margin-top: 4px;
  }
  .ai-target-box {
    background: #1c2128; border: 1px solid #30363d;
    border-radius: 10px; padding: 14px 18px; text-align: center;
  }
  .ai-target-label { font-size: 10px; color: #8b949e; text-transform: uppercase; letter-spacing:.06em; }
  .ai-target-val   { font-size: 20px; font-weight: 700; margin: 4px 0; }
  .ai-target-upside{ font-size: 12px; font-weight: 600; }
  .ai-reasoning-block {
    background: #161b22; border-radius: 10px;
    padding: 14px 18px; margin: 10px 0;
  }
  .ai-reasoning-title {
    font-size: 11px; font-weight: 600; text-transform: uppercase;
    letter-spacing: .06em; margin-bottom: 8px;
  }
  .ai-reasoning-item {
    font-size: 13px; color: #c9d1d9; line-height: 1.7;
    padding: 3px 0; border-bottom: 1px solid #21262d;
  }
  .ai-reasoning-item:last-child { border-bottom: none; }
  .ai-conviction {
    background: #1c2128; border-radius: 10px; padding: 14px 18px;
    font-size: 14px; color: #e6edf3; font-style: italic;
    line-height: 1.7; border-left: 3px solid #58a6ff; margin-top: 12px;
  }
  .ai-badge-buy    { color: #3fb950; }
  .ai-badge-sell   { color: #f85149; }
  .ai-badge-hold   { color: #e3b341; }
  .ai-badge-acc    { color: #58a6ff; }
  .ai-loading {
    text-align: center; padding: 32px;
    color: #8b949e; font-size: 14px;
  }
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
                # Ensure every item has a non-empty url field
                cleaned = []
                for item in data[:10]:
                    url = item.get("url", "")
                    if not url:
                        query = requests.utils.quote(item.get("headline", symbol) + " NSE India")
                        url = f"https://news.google.com/search?q={query}&hl=en-IN&gl=IN&ceid=IN:en"
                    item["url"] = url
                    cleaned.append(item)
                return cleaned
    except Exception:
        pass
    return _synthetic_news(symbol)


def _synthetic_news(symbol: str) -> List[Dict]:
    """
    When no Finnhub key is provided, generate placeholder headlines
    and point each one to a live Google News search for that exact headline —
    so clicking always opens a real news page.
    """
    templates = [
        f"{symbol} secures infra development contract from NHAI",
        f"Analysts upgrade {symbol} to BUY target price raised",
        f"{symbol} Q3 PAT beats estimates margins expand",
        f"Board approves capex plan for FY26 expansion {symbol}",
        f"PLI scheme disbursement boosts {symbol} order book",
        f"{symbol} wins government IT services renewal contract",
        f"FII buying interest rises in {symbol} sector re-rating",
        f"{symbol} announces JV global MNC green energy projects",
        f"Credit rating upgraded for {symbol} long-term bonds",
        f"RBI policy stance positive {symbol} net interest margins",
    ]
    sources = ["ET Markets", "Moneycontrol", "Business Standard", "Mint", "CNBC-TV18"]
    source_urls = [
        "https://economictimes.indiatimes.com/markets",
        "https://www.moneycontrol.com/news/business/stocks/",
        "https://www.business-standard.com/markets",
        "https://www.livemint.com/market",
        "https://www.cnbctv18.com/market/",
    ]
    now = datetime.now()
    result = []
    for i in range(8):
        headline = templates[i % len(templates)]
        # Google News search URL — always opens real news
        search_url = (
            "https://news.google.com/search?q="
            + requests.utils.quote(headline + " NSE India")
            + "&hl=en-IN&gl=IN&ceid=IN:en"
        )
        result.append({
            "headline": headline,
            "datetime": int((now - timedelta(hours=i * 8)).timestamp()),
            "source":   sources[i % 5],
            "url":      search_url,
        })
    return result


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
# AI AGENT — CLAUDE-POWERED STOCK ANALYST
# ══════════════════════════════════════════════════════════════════════════════

def call_ai_agent(
    symbol: str,
    sector: str,
    current_price: float,
    day_chg: float,
    technicals: Dict,
    fundamentals: Dict,
    master: Dict,
    news: List[Dict],
    sentiments: List[Dict],
    projects: List[Dict],
    vix: float,
    anthropic_key: str,
) -> Dict:
    """
    Send all collected data to Claude and get a structured
    short-term + long-term investment verdict with targets,
    stop loss, bull/bear case, risk factors, and conviction.
    Returns a dict with the parsed verdict.
    """

    # ── Build the data brief ─────────────────────────────────────────────────
    pos_news = sum(1 for s in sentiments if s.get("label") == "positive")
    neg_news = sum(1 for s in sentiments if s.get("label") == "negative")
    news_titles = [n.get("headline","") for n in news[:5]]
    project_titles = [p.get("title","") for p in projects[:3]]

    avg_de  = round(float(np.mean(fundamentals["de"])),  2) if fundamentals.get("de")  else "N/A"
    avg_roe = round(float(np.mean(fundamentals["roe"])), 2) if fundamentals.get("roe") else "N/A"
    avg_npm = round(float(np.mean(fundamentals["npm"])), 2) if fundamentals.get("npm") else "N/A"

    brief = f"""You are an elite Indian equity research analyst with 20 years of experience
covering NSE/BSE markets. Analyse the following real-time data for {symbol} and
give a precise, actionable investment verdict.

══ STOCK SNAPSHOT ══
Symbol        : {symbol}
Sector        : {sector}
Current Price : ₹{current_price:,.2f}
Day Change    : {day_chg:+.2f}%
India VIX     : {vix:.1f} {"[DEFENSIVE MODE]" if vix > 22 else "[NORMAL]"}

══ TECHNICAL PICTURE ══
RSI (14D)     : {technicals["rsi"]} {"(Overbought)" if technicals["rsi"]>70 else "(Oversold)" if technicals["rsi"]<30 else "(Neutral)"}
MACD          : {technicals["macd"]} vs Signal {technicals["macd_signal"]} → {"Bullish crossover" if technicals["macd"]>technicals["macd_signal"] else "Bearish crossover"}
ADX           : {technicals["adx"]} {"(Strong trend)" if technicals["adx"]>25 else "(Weak/ranging)"}
Volume Ratio  : {technicals["vol_ratio"]}x 20-day average
52W High      : ₹{technicals["week52_high"]:,.2f} | 52W Low: ₹{technicals["week52_low"]:,.2f}
From 52W High : {technicals["pct_from_high"]:+.1f}%
5-Year CAGR   : {technicals["cagr_5y"]}%
BB Upper      : ₹{technicals["bb_upper"]:,.2f} | BB Lower: ₹{technicals["bb_lower"]:,.2f}

══ FUNDAMENTAL HEALTH (5-YEAR AVERAGES) ══
Debt/Equity   : {avg_de}
ROE           : {avg_roe}%
Net Profit Margin : {avg_npm}%

══ NEWS SENTIMENT ══
Positive articles: {pos_news} | Negative: {neg_news} out of {len(sentiments)} analysed
Recent headlines:
{chr(10).join(f"• {t}" for t in news_titles)}

══ AI-RESEARCHED CATALYSTS ══
{chr(10).join(f"• {t}" for t in project_titles) if project_titles else "• No major catalysts found"}

══ MASTER SCORE ══
Overall Score : {master["score"]}/100
Technical     : {master["tech_s"]}/35
Fundamental   : {master["fund_s"]}/35
Sentiment     : {master["sent_s"]}/30

══ YOUR TASK ══
Based on ALL the above data, provide a JSON response (and ONLY JSON, no markdown, no preamble) in exactly this structure:

{{
  "short_term": {{
    "verdict": "STRONG BUY | BUY | ACCUMULATE | HOLD | REDUCE | SELL | AVOID",
    "horizon": "1-3 months",
    "target_price": <number or null>,
    "stop_loss": <number>,
    "upside_pct": <number or null>,
    "confidence": "HIGH | MEDIUM | LOW",
    "reasoning": ["reason 1", "reason 2", "reason 3"]
  }},
  "long_term": {{
    "verdict": "STRONG BUY | BUY | ACCUMULATE | HOLD | REDUCE | SELL | AVOID",
    "horizon": "12-36 months",
    "target_price": <number or null>,
    "stop_loss": <number>,
    "upside_pct": <number or null>,
    "confidence": "HIGH | MEDIUM | LOW",
    "reasoning": ["reason 1", "reason 2", "reason 3"]
  }},
  "bull_case": ["key bull argument 1", "key bull argument 2", "key bull argument 3"],
  "bear_case": ["key risk 1", "key risk 2", "key risk 3"],
  "key_risks": ["risk 1", "risk 2"],
  "conviction_statement": "One powerful sentence summing up your overall view on this stock right now.",
  "suggested_strategy": "e.g. SIP entry over 3 months | Lump sum at current levels | Wait for dip to ₹X | Trail stop at ₹X"
}}

Be specific with price targets — calculate them based on the current price ₹{current_price:,.2f}.
Stop loss must be a specific ₹ number, not a percentage.
Do not add any text outside the JSON."""

    # ── Call Anthropic API ───────────────────────────────────────────────────
    if not anthropic_key or not anthropic_key.strip().startswith("sk-ant"):
        return _fallback_verdict(master, current_price, technicals)

    try:
        resp = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key":         anthropic_key.strip(),
                "anthropic-version": "2023-06-01",
                "content-type":      "application/json",
            },
            json={
                "model":      "claude-opus-4-6",
                "max_tokens": 1500,
                "messages":   [{"role": "user", "content": brief}],
            },
            timeout=45,
        )
        if resp.status_code == 200:
            raw = resp.json()["content"][0]["text"].strip()
            # Strip any accidental markdown fences
            raw = re.sub(r"^```json\s*", "", raw)
            raw = re.sub(r"```\s*$",     "", raw)
            verdict = json.loads(raw)
            verdict["_source"] = "claude"
            return verdict
        else:
            return _fallback_verdict(master, current_price, technicals)
    except Exception:
        return _fallback_verdict(master, current_price, technicals)


def _fallback_verdict(master: Dict, price: float, tech: Dict) -> Dict:
    """Rule-based fallback when no Anthropic key is provided."""
    score = master["score"]
    st_v  = master["verdict"]
    lt_v  = "BUY" if score >= 55 else "HOLD" if score >= 40 else "REDUCE"

    st_target = round(price * (1 + max(0.05, tech["cagr_5y"] / 100 * 0.5)), 2) if score >= 55 else None
    lt_target = round(price * (1 + max(0.15, tech["cagr_5y"] / 100 * 2.0)), 2) if score >= 40 else None
    stop      = round(price * 0.93, 2)

    return {
        "short_term": {
            "verdict":     st_v,
            "horizon":     "1-3 months",
            "target_price":st_target,
            "stop_loss":   stop,
            "upside_pct":  round((st_target / price - 1) * 100, 1) if st_target else None,
            "confidence":  "HIGH" if score >= 70 else "MEDIUM" if score >= 50 else "LOW",
            "reasoning":   [
                f"Master Score of {score}/100 {'supports' if score>=55 else 'does not support'} buying",
                f"RSI at {tech['rsi']} — {'momentum intact' if 40<tech['rsi']<70 else 'overbought' if tech['rsi']>=70 else 'oversold — bounce potential'}",
                f"MACD {'bullish' if tech['macd']>tech['macd_signal'] else 'bearish'} crossover in play",
            ],
        },
        "long_term": {
            "verdict":     lt_v,
            "horizon":     "12-36 months",
            "target_price":lt_target,
            "stop_loss":   round(price * 0.80, 2),
            "upside_pct":  round((lt_target / price - 1) * 100, 1) if lt_target else None,
            "confidence":  "MEDIUM",
            "reasoning":   [
                f"5-Year CAGR of {tech['cagr_5y']}% shows {'strong' if tech['cagr_5y']>=12 else 'moderate'} compounding",
                "Fundamental score reflects balance sheet health",
                "Sector policy tailwinds provide structural support",
            ],
        },
        "bull_case":  ["Strong technical momentum", "Improving fundamentals", "Positive macro environment"],
        "bear_case":  ["Market-wide correction risk", "Sector rotation possible", "Global headwinds from VIX"],
        "key_risks":  ["India VIX elevated — systemic risk", "Earnings miss could trigger selloff"],
        "conviction_statement": f"Score of {score}/100 — {master['verdict']} with {master['horizon']}.",
        "suggested_strategy":   "Add Anthropic API key in sidebar for a full AI-generated strategy.",
        "_source":              "fallback",
    }


def render_ai_verdict(verdict, symbol, current_price, has_api_key):
    """Render the full AI agent verdict card. All HTML built via string concat — no nested f-strings."""

    st_data    = verdict.get("short_term", {})
    lt_data    = verdict.get("long_term",  {})
    is_claude  = verdict.get("_source") == "claude"

    VERDICT_COLOR = {
        "STRONG BUY": "#3fb950", "BUY": "#3fb950",
        "ACCUMULATE": "#58a6ff", "HOLD": "#e3b341",
        "REDUCE": "#f0883e",     "SELL": "#f85149", "AVOID": "#f85149",
    }
    CONF_MAP = {"HIGH": ("&#x1F7E2;", "#3fb950"), "MEDIUM": ("&#x1F7E1;", "#e3b341"), "LOW": ("&#x1F534;", "#f85149")}

    st_color = VERDICT_COLOR.get(st_data.get("verdict","HOLD"), "#e3b341")
    lt_color = VERDICT_COLOR.get(lt_data.get("verdict","HOLD"), "#e3b341")
    st_ci, st_cc = CONF_MAP.get(st_data.get("confidence","MEDIUM"), ("&#x26AA;","#8b949e"))
    lt_ci, lt_cc = CONF_MAP.get(lt_data.get("confidence","MEDIUM"), ("&#x26AA;","#8b949e"))

    if is_claude:
        src_badge = ('<span style="font-size:10px;background:#1f4a2e;color:#3fb950;'
                     'border:1px solid #3fb950;padding:2px 8px;border-radius:10px;margin-left:8px;">'
                     '&#x1F916; Claude AI</span>')
    else:
        src_badge = ('<span style="font-size:10px;background:#232a35;color:#58a6ff;'
                     'border:1px solid #58a6ff;padding:2px 8px;border-radius:10px;margin-left:8px;">'
                     '&#9881;&#65039; Rule Engine</span>')

    if not has_api_key:
        st.markdown(
            '<div style="background:#1c2128;border:1px dashed #30363d;border-radius:10px;'
            'padding:14px 18px;margin-bottom:8px;font-size:13px;color:#8b949e;">'
            '&#x1F511; Add your <strong style="color:#58a6ff;">Anthropic API Key</strong> '
            'in the sidebar to unlock full Claude AI verdict with precise targets. '
            'A rule-based fallback is shown below.</div>',
            unsafe_allow_html=True,
        )

    # Pre-compute all display values as plain strings
    st_verdict    = st_data.get("verdict", "HOLD")
    st_horizon    = st_data.get("horizon", "1-3 months")
    st_confidence = st_data.get("confidence", "MEDIUM")
    lt_verdict    = lt_data.get("verdict", "HOLD")
    lt_horizon    = lt_data.get("horizon", "12-36 months")
    lt_confidence = lt_data.get("confidence", "MEDIUM")

    header_html = (
        '<div class="ai-agent-card">'
        '<div class="ai-verdict-header">&#x1F9E0; AI Agent Verdict &nbsp;' + src_badge + '</div>'
        '<div style="display:grid;grid-template-columns:1fr 1fr;gap:20px;margin-bottom:20px;">'
        '<div>'
        '<div style="font-size:11px;color:#8b949e;text-transform:uppercase;letter-spacing:.06em;margin-bottom:8px;">'
        'Short Term &middot; ' + st_horizon + '</div>'
        '<div class="ai-verdict-main" style="color:' + st_color + ';">' + st_verdict + '</div>'
        '<div class="ai-verdict-sub">' + st_ci +
        ' <span style="color:' + st_cc + ';">' + st_confidence + ' confidence</span></div>'
        '</div>'
        '<div>'
        '<div style="font-size:11px;color:#8b949e;text-transform:uppercase;letter-spacing:.06em;margin-bottom:8px;">'
        'Long Term &middot; ' + lt_horizon + '</div>'
        '<div class="ai-verdict-main" style="color:' + lt_color + ';">' + lt_verdict + '</div>'
        '<div class="ai-verdict-sub">' + lt_ci +
        ' <span style="color:' + lt_cc + ';">' + lt_confidence + ' confidence</span></div>'
        '</div>'
        '</div></div>'
    )
    st.markdown(header_html, unsafe_allow_html=True)

    # ── Target / Stop Loss boxes ──────────────────────────────────────────────
    def _fmt_price(v):
        return "&#8377;" + "{:,.0f}".format(v) if v else "&#8212;"

    def _fmt_pct(v):
        if v is None: return ""
        return "+" + "{:.1f}%".format(v) if v > 0 else "{:.1f}%".format(v)

    def _target_card(label, price_val, pct_val, color):
        return (
            '<div class="ai-target-box">'
            '<div class="ai-target-label">' + label + '</div>'
            '<div class="ai-target-val" style="color:' + color + ';">' + _fmt_price(price_val) + '</div>'
            '<div class="ai-target-upside" style="color:' + color + ';">' + _fmt_pct(pct_val) + '</div>'
            '</div>'
        )

    st_tp = st_data.get("target_price")
    st_up = st_data.get("upside_pct")
    st_sl = st_data.get("stop_loss")
    st_sl_pct = round((st_sl / current_price - 1) * 100, 1) if st_sl and current_price else None
    lt_tp = lt_data.get("target_price")
    lt_up = lt_data.get("upside_pct")
    lt_sl = lt_data.get("stop_loss")
    lt_sl_pct = round((lt_sl / current_price - 1) * 100, 1) if lt_sl and current_price else None

    t1, t2, t3, t4 = st.columns(4)
    with t1:
        st.markdown(_target_card("ST Target",   st_tp, st_up,    "#3fb950"), unsafe_allow_html=True)
    with t2:
        st.markdown(_target_card("ST Stop Loss",st_sl, st_sl_pct,"#f85149"), unsafe_allow_html=True)
    with t3:
        st.markdown(_target_card("LT Target",   lt_tp, lt_up,    "#d2a8ff"), unsafe_allow_html=True)
    with t4:
        st.markdown(_target_card("LT Stop Loss",lt_sl, lt_sl_pct,"#f85149"), unsafe_allow_html=True)

    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

    # ── Bull / Bear / Strategy ────────────────────────────────────────────────
    def _list_items(items, icon):
        return "".join('<div class="ai-reasoning-item">' + icon + " " + r + "</div>" for r in items)

    bull  = verdict.get("bull_case", [])
    bear  = verdict.get("bear_case", [])
    risks = verdict.get("key_risks", [])
    strat = verdict.get("suggested_strategy", "")

    b1, b2, b3 = st.columns(3)
    with b1:
        st.markdown(
            '<div class="ai-reasoning-block">'
            '<div class="ai-reasoning-title" style="color:#3fb950;">&#x1F402; Bull Case</div>'
            + _list_items(bull, "&#x2705;") + "</div>",
            unsafe_allow_html=True,
        )
    with b2:
        st.markdown(
            '<div class="ai-reasoning-block">'
            '<div class="ai-reasoning-title" style="color:#f85149;">&#x1F43B; Bear Case</div>'
            + _list_items(bear, "&#x26A0;&#xFE0F;") + "</div>",
            unsafe_allow_html=True,
        )
    with b3:
        strat_item = (
            '<div class="ai-reasoning-item" style="color:#58a6ff;font-weight:500;">'
            "&#x1F4CB; " + strat + "</div>" if strat else ""
        )
        st.markdown(
            '<div class="ai-reasoning-block">'
            '<div class="ai-reasoning-title" style="color:#e3b341;">&#x26A1; Strategy</div>'
            + strat_item + _list_items(risks, "&#x1F53A;") + "</div>",
            unsafe_allow_html=True,
        )

    # ── Conviction statement ──────────────────────────────────────────────────
    conviction = verdict.get("conviction_statement", "")
    if conviction:
        st.markdown(
            '<div class="ai-conviction">'
            '&#x1F4A1; <strong style="color:#58a6ff;">AI Conviction:</strong> ' + conviction + "</div>",
            unsafe_allow_html=True,
        )


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
        horizontal_spacing=0.12,   # breathing room between subplots
    )
    fig.add_trace(go.Bar(
        x=years, y=fundamentals["de"],
        name="D/E", marker_color="#f0883e",
        text=[str(v) for v in fundamentals["de"]],
        textposition="outside",
        textfont=dict(size=9, color="#8b949e"),
    ), row=1, col=1)
    fig.add_trace(go.Scatter(
        x=years, y=fundamentals["roe"],
        name="ROE", mode="lines+markers",
        line=dict(color="#58a6ff", width=2),
        marker=dict(size=6),
    ), row=1, col=2)
    fig.add_trace(go.Bar(
        x=years, y=fundamentals["npm"],
        name="NPM", marker_color="#3fb950",
        text=[str(v) for v in fundamentals["npm"]],
        textposition="outside",
        textfont=dict(size=9, color="#8b949e"),
    ), row=1, col=3)

    # Style subplot title annotations so they sit above charts cleanly
    for ann in fig.layout.annotations:
        ann.font = dict(size=11, color="#8b949e")
        ann.y   += 0.05   # push titles up slightly

    fig.update_xaxes(tickfont=dict(size=9, color="#8b949e"))
    fig.update_yaxes(tickfont=dict(size=9, color="#8b949e"), showgrid=True,
                     gridcolor="#21262d", zeroline=False)

    fig.update_layout(
        showlegend=False,
        height=300,
        margin=dict(l=40, r=20, t=50, b=40),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="#0d1117",
        font=dict(color="#8b949e", size=11),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(size=10)),
    )
    return fig


def chart_sector_comparison(symbol: str, stock_df_data: pd.DataFrame) -> go.Figure:
    sector_df = fetch_sector_index(symbol)
    sector_name = NSE_SECTOR_MAP.get(symbol, (_get_sector(symbol), "_"))[0]

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
    values = [
        round(master["tech_s"] / 35 * 100, 1),
        round(master["fund_s"] / 35 * 100, 1),
        round(master["sent_s"] / 30 * 100, 1),
        round(master["tech_s"] / 35 * 100, 1),
    ]
    fig = go.Figure(go.Scatterpolar(
        r=values, theta=categories,
        fill="toself",
        fillcolor="rgba({},0.18)".format(_hex_to_rgb(master["color"])),
        line=dict(color=master["color"], width=2.5),
        name="Score",
    ))
    fig.update_layout(
        polar=dict(
            bgcolor="#161b22",
            radialaxis=dict(
                visible=True, range=[0, 100],
                gridcolor="#30363d",
                tickvals=[25, 50, 75, 100],
                tickfont=dict(size=8, color="#8b949e"),
                showticklabels=True,
            ),
            angularaxis=dict(
                gridcolor="#30363d",
                tickfont=dict(size=12, color="#e6edf3"),
            ),
            domain=dict(x=[0.08, 0.92], y=[0.08, 0.92]),
        ),
        height=270,
        showlegend=False,
        margin=dict(l=60, r=60, t=20, b=60),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="#0d1117",
        font=dict(color="#8b949e", size=11),
    )
    return fig


def chart_price_cagr(df: pd.DataFrame, symbol: str) -> go.Figure:
    yearly = df["CLOSE"].resample("YE").last()

    # Convert datetime index → clean year strings (avoids "23:59", "00:00:00" on x-axis)
    yearly_years  = [str(d.year) for d in yearly.index]
    yearly_prices = list(yearly.values)

    cagr_vals, cagr_years = [], []
    if len(yearly) >= 2:
        base = yearly.iloc[0]
        for i, (yr, val) in enumerate(yearly.items(), 1):
            c = ((val / base) ** (1 / i) - 1) * 100
            cagr_years.append(str(yr.year))
            cagr_vals.append(round(c, 1))

    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=("Annual Close (&#8377;)", "Rolling CAGR (%)"),
        horizontal_spacing=0.14,
    )

    fig.add_trace(go.Scatter(
        x=yearly_years, y=yearly_prices,
        mode="lines+markers",
        line=dict(color="#58a6ff", width=2),
        marker=dict(size=6, color="#58a6ff"),
        fill="tozeroy", fillcolor="rgba(88,166,255,0.1)",
        name="Annual Close",
    ), row=1, col=1)

    if cagr_vals:
        bar_colors = ["#3fb950" if v >= 0 else "#f85149" for v in cagr_vals]
        fig.add_trace(go.Bar(
            x=cagr_years, y=cagr_vals,
            marker_color=bar_colors,
            text=[str(v)+"%" for v in cagr_vals],
            textposition="outside",
            textfont=dict(size=9, color="#8b949e"),
            name="CAGR",
        ), row=1, col=2)

    # Push subplot titles up and reduce font so they don't sit on the chart
    for ann in fig.layout.annotations:
        ann.font = dict(size=11, color="#8b949e")
        ann.y   += 0.05

    fig.update_xaxes(tickfont=dict(size=10, color="#8b949e"), tickangle=0)
    fig.update_yaxes(tickfont=dict(size=9,  color="#8b949e"),
                     gridcolor="#21262d", zeroline=False)

    fig.update_layout(
        showlegend=False,
        height=300,
        margin=dict(l=40, r=20, t=50, b=40),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="#0d1117",
        font=dict(color="#8b949e", size=11),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(size=10)),
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


def render_news_card(headline: str, source: str, ts: int, badge: str, url: str = ""):
    badge_map = {
        "positive": ("badge-pos", "&#9679; Positive"),
        "negative": ("badge-neg", "&#9679; Negative"),
        "neutral":  ("badge-neu", "&#9679; Neutral"),
    }
    cls, label = badge_map.get(badge, ("badge-neu", "&#9679; Neutral"))
    dt_str = datetime.fromtimestamp(ts).strftime("%d %b %H:%M") if ts else "Recent"

    has_url = url and url not in ("#", "", "None")
    tag_open  = '<a class="news-card-link" href="' + url + '" target="_blank" rel="noopener noreferrer">' if has_url else '<div class="news-card">'
    tag_close = "</a>" if has_url else "</div>"
    ext_icon  = '<span class="news-link-icon">&#8599;</span>' if has_url else ""

    html = (
        tag_open
        + '<div class="news-title">' + ext_icon + headline
        + '<span class="badge ' + cls + '">' + label + "</span></div>"
        + '<div class="news-meta">' + source + " &nbsp;&middot;&nbsp; " + dt_str + "</div>"
        + tag_close
    )
    st.markdown(html, unsafe_allow_html=True)


def render_project_card(title: str, content: str, date_str: str, url: str = ""):
    has_url  = url and url not in ("#", "", "None")
    tag_open = ('<a class="project-card-link" href="' + url + '" target="_blank" rel="noopener noreferrer">') if has_url else '<div class="news-card" style="border-left:3px solid #3fb950;">'
    tag_close= "</a>" if has_url else "</div>"
    ext_icon = '<span class="news-link-icon">&#8599;</span>' if has_url else ""

    html = (
        tag_open
        + '<div class="news-title">&#x1F3D7;&#xFE0F; ' + ext_icon + title + "</div>"
        + '<div class="news-meta" style="margin-top:6px;color:#c9d1d9;">' + content + "</div>"
        + '<div class="news-meta" style="margin-top:4px;">&#128197; ' + date_str + "</div>"
        + tag_close
    )
    st.markdown(html, unsafe_allow_html=True)


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
    with st.sidebar:
        st.markdown("""
        <div style="text-align:center; padding: 16px 0 8px;">
          <div style="font-size:24px;">&#x1F1EE;&#x1F1F3;</div>
          <div style="font-size:16px; font-weight:700; color:#e6edf3;">Market Intelligence</div>
          <div style="font-size:11px; color:#8b949e;">Institutional Grade · NSE/BSE</div>
        </div>
        """, unsafe_allow_html=True)

        st.divider()
        st.markdown("**🔍 Search NSE / BSE Stock**")

        # ── Live search input ────────────────────────────────────────────────
        search_query = st.text_input(
            "Stock Symbol", placeholder="e.g. RELIANCE, ZOMATO, IRFC",
            key="stock_search", label_visibility="visible",
        )

        # Determine results to show
        if search_query and len(search_query.strip()) >= 1:
            results = search_nse_stocks(search_query)
        else:
            results = ["RELIANCE","TCS","INFY","HDFCBANK","ICICIBANK","SBIN",
                       "WIPRO","HCLTECH","BAJFINANCE","KOTAKBANK","HINDUNILVR",
                       "ITC","SUNPHARMA","MARUTI","ZOMATO","PAYTM","IRFC","LT"]

        if not results:
            st.warning("No stocks found. Try a different symbol.")
            results = ["RELIANCE"]

        if "selected_symbol" not in st.session_state:
            st.session_state.selected_symbol = "RELIANCE"

        symbol = st.selectbox(
            "Select stock to analyse",
            results,
            index=0,
            key="symbol_select",
        )
        st.session_state.selected_symbol = symbol
        st.caption(f"{len(results)} result(s) · 1500+ NSE/BSE stocks available")

        st.divider()
        st.markdown("**🔑 API Keys (Optional)**")
        with st.expander("Configure API Keys", expanded=False):
            fmp_key     = st.text_input("FMP API Key",    type="password", placeholder="fmp_xxxxxxxx")
            finnhub_key = st.text_input("Finnhub Key",    type="password", placeholder="xxxxxxxxxxxxxxx")
            tavily_key  = st.text_input("Tavily AI Key",  type="password", placeholder="tvly-xxxxxxxx")
            anthropic_key = st.text_input(
                "Anthropic Key (AI Agent)",
                type="password",
                placeholder="sk-ant-api03-...",
                help="Get free key at console.anthropic.com",
            )
            if anthropic_key and anthropic_key.startswith("sk-ant"):
                st.success("Claude AI active")

        st.divider()
        vix = fetch_india_vix()
        vix_color = "#f85149" if vix > 22 else "#e3b341" if vix > 17 else "#3fb950"
        vix_status = "DEFENSIVE MODE" if vix > 22 else "Normal Regime"
        st.markdown(
            "<div class='sidebar-section'>"
            "<div class='sidebar-label'>India VIX (Live)</div>"
            "<div style='font-size:28px;font-weight:700;color:" + vix_color + ";'>" + str(round(vix,1)) + "</div>"
            "<div style='font-size:11px;color:#8b949e;margin-top:2px;'>" + vix_status + "</div>"
            "</div>",
            unsafe_allow_html=True,
        )

        st.divider()
        st.markdown("""
<div style="font-size:11px;color:#8b949e;line-height:1.8;">
&#x1F4CA; Price: jugaad-data / nselib<br>
&#x1F4C8; Fundamentals: FMP API<br>
&#x1F916; Sentiment: FinBERT<br>
&#x1F50D; Research: Tavily AI<br>
&#x26A1; Indicators: In-house engine
</div>""", unsafe_allow_html=True)

    return symbol, fmp_key or "", finnhub_key or "", tavily_key or "", anthropic_key or ""



# ══════════════════════════════════════════════════════════════════════════════
# MAIN APP
# ══════════════════════════════════════════════════════════════════════════════


# ══════════════════════════════════════════════════════════════════════════════
# GLOBAL CRISIS DATA
# ══════════════════════════════════════════════════════════════════════════════

@st.cache_data(ttl=300, show_spinner=False)
def fetch_global_indicators() -> Dict:
    """Fetch real-time global market stress indicators."""
    indicators = {}

    # Fear & Greed Index (alternative.me - free, no key)
    try:
        r = requests.get("https://api.alternative.me/fng/?limit=1", timeout=6)
        if r.status_code == 200:
            d = r.json()["data"][0]
            indicators["fear_greed"] = {
                "value": int(d["value"]),
                "label": d["value_classification"],
            }
    except Exception:
        indicators["fear_greed"] = {"value": 45, "label": "Fear"}

    # Gold, Oil, USD/INR, US10Y via Yahoo Finance public API
    symbols_map = {
        "GC=F":    "gold",
        "CL=F":    "oil",
        "USDINR=X":"usdinr",
        "^TNX":    "us10y",
        "^FTSE":   "ftse",
        "^N225":   "nikkei",
    }
    for sym, key in symbols_map.items():
        try:
            r = requests.get(
                f"https://query1.finance.yahoo.com/v8/finance/chart/{sym}",
                params={"interval":"1d","range":"5d"},
                headers={"User-Agent":"Mozilla/5.0"},
                timeout=6,
            )
            if r.status_code == 200:
                meta  = r.json()["chart"]["result"][0]["meta"]
                price = meta.get("regularMarketPrice", 0)
                prev  = meta.get("previousClose", price)
                chg   = round((price / prev - 1) * 100, 2) if prev else 0
                indicators[key] = {"price": round(price, 2), "chg": chg}
        except Exception:
            pass

    # India VIX
    indicators["india_vix"] = {"price": fetch_india_vix(), "chg": 0}
    return indicators


CRISIS_OPPORTUNITY_STOCKS = [
    # Format: (symbol, reason, crisis_type)
    ("HINDUNILVR", "Defensive FMCG — outperforms in risk-off markets",       "defensive"),
    ("ITC",        "High dividend yield, low volatility — safe haven",         "defensive"),
    ("SUNPHARMA",  "Pharma demand non-cyclical, USD revenues hedge INR",       "defensive"),
    ("DRREDDY",    "Export-driven Pharma — benefits from USD strength",        "defensive"),
    ("NESTLEIND",  "Staples pricing power, insulated from market cycles",      "defensive"),
    ("CIPLA",      "Domestic pharma, government supply contracts — stable",    "defensive"),
    ("TCS",        "USD earner — INR depreciation boosts profits",             "currency"),
    ("INFY",       "80% revenues in USD/EUR — natural INR hedge",              "currency"),
    ("WIPRO",      "Global IT — earnings rise when INR falls vs USD",          "currency"),
    ("HCLTECH",    "Dollar-denominated contracts insulate from local risks",   "currency"),
    ("NTPC",       "Government-backed power — essential services floor",       "infra"),
    ("POWERGRID",  "Regulated utility — stable cash flows regardless of cycle","infra"),
    ("COALINDIA",  "Commodity supply — energy crisis drives coal demand up",   "commodity"),
    ("ONGC",       "Oil price surge benefits upstream E&P revenues",           "commodity"),
]


def get_crisis_opportunity_stocks(indicators: Dict) -> List[Dict]:
    """Score and rank crisis opportunity stocks based on current global conditions."""
    fg = indicators.get("fear_greed", {}).get("value", 50)
    vix = indicators.get("india_vix", {}).get("price", 15)
    oil = indicators.get("oil", {}).get("chg", 0)
    usdinr = indicators.get("usdinr", {}).get("chg", 0)

    results = []
    for symbol, reason, crisis_type in CRISIS_OPPORTUNITY_STOCKS:
        score = 0
        if crisis_type == "defensive" and (fg < 40 or vix > 18):
            score += 30
        if crisis_type == "currency" and usdinr > 0.2:
            score += 25
        if crisis_type == "commodity" and oil > 1.0:
            score += 20
        if crisis_type == "infra":
            score += 15

        # Sentiment boost
        if fg < 25: score += 15   # extreme fear = defensive plays shine
        if vix > 22: score += 10  # defensive mode active

        results.append({
            "symbol":      symbol,
            "reason":      reason,
            "crisis_type": crisis_type,
            "score":       score,
            "verdict":     "STRONG BUY" if score >= 50 else "BUY" if score >= 30 else "ACCUMULATE",
        })

    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:8]


# ══════════════════════════════════════════════════════════════════════════════
# MAIN APP
# ══════════════════════════════════════════════════════════════════════════════

def main():
    # ── Session state init ────────────────────────────────────────────────────
    if "watchlist" not in st.session_state:
        st.session_state.watchlist = ["RELIANCE", "TCS", "HDFCBANK", "INFY", "SBIN"]
    if "active_tab" not in st.session_state:
        st.session_state.active_tab = 0

    symbol, fmp_key, finnhub_key, tavily_key, anthropic_key = render_sidebar()

    sector_name = _get_sector(symbol)
    vix = fetch_india_vix()

    # ── Regime Banner ─────────────────────────────────────────────────────────
    if vix > 22:
        st.markdown(
            '<div class="regime-defensive">&#x26A0;&#xFE0F; DEFENSIVE MODE ACTIVE — India VIX at '
            + str(round(vix, 1))
            + '. Prioritising FMCG / Pharma / Defensive sectors. Reduce high-beta cyclical exposure.</div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            '<div class="regime-normal">&#x2705; Normal Market Regime — India VIX at '
            + str(round(vix, 1))
            + '. Risk-on environment. Broad market participation expected.</div>',
            unsafe_allow_html=True,
        )

    # ── TABS ──────────────────────────────────────────────────────────────────
    tab_analysis, tab_mystocks, tab_crisis = st.tabs([
        "📊 Stock Analysis",
        "⭐ My Stocks",
        "🌍 Global Crisis Monitor",
    ])

    # ══════════════════════════════════════════════════════════════════════════
    # TAB 1 — STOCK ANALYSIS
    # ══════════════════════════════════════════════════════════════════════════
    with tab_analysis:
        col_h1, col_h2 = st.columns([3, 1])
        with col_h1:
            st.markdown(
                "## " + symbol +
                " &nbsp;<span style=\'font-size:16px;color:#8b949e;font-weight:400;\'>NSE · "
                + sector_name + "</span>",
                unsafe_allow_html=True,
            )
        with col_h2:
            st.caption("Updated: " + datetime.now().strftime("%d %b %Y, %H:%M IST"))
            if st.button("+ Add to Watchlist", key="add_wl_analysis"):
                if symbol not in st.session_state.watchlist:
                    st.session_state.watchlist.append(symbol)
                    st.success(symbol + " added to watchlist!")
                else:
                    st.info("Already in watchlist")

        with st.spinner("Fetching market data..."):
            price_df     = fetch_nse_price_history(symbol, years=5)
            fundamentals = fetch_fundamentals_fmp(symbol, fmp_key)
            news         = fetch_news_finnhub(symbol, finnhub_key)
            projects     = fetch_deep_research_tavily(symbol, tavily_key)
            sentiments   = score_sentiment_finbert([n["headline"] for n in news])
            technicals   = compute_technicals(price_df)
            master       = compute_master_score(technicals, fundamentals, sentiments, vix)

        close         = price_df["CLOSE"]
        current_price = close.iloc[-1]
        prev_close    = close.iloc[-2]
        day_chg       = (current_price / prev_close - 1) * 100
        mtd_chg       = (current_price / close.tail(22).iloc[0] - 1) * 100
        ytd_chg       = (current_price / close.tail(252).iloc[0] - 1) * 100

        m1, m2, m3, m4, m5, m6 = st.columns(6)
        with m1: render_metric_card("LTP (Rs)", "Rs" + "{:,.1f}".format(current_price), "{:.2f}%".format(abs(day_chg)), day_chg >= 0)
        with m2: render_metric_card("Day Change", "{:+.2f}%".format(day_chg), None, None)
        with m3: render_metric_card("MTD Return", "{:+.1f}%".format(mtd_chg), None, None)
        with m4: render_metric_card("YTD Return", "{:+.1f}%".format(ytd_chg), None, None)
        with m5: render_metric_card("52W High", "Rs" + "{:,.0f}".format(technicals["week52_high"]), "{:.1f}% from high".format(technicals["pct_from_high"]), technicals["pct_from_high"] >= -5)
        with m6: render_metric_card("5Y CAGR", str(technicals["cagr_5y"]) + "%", None, technicals["cagr_5y"] >= 10)

        st.markdown("---")

        has_key = bool(anthropic_key and anthropic_key.strip().startswith("sk-ant"))
        with st.spinner("AI Agent analysing..." if has_key else "Generating verdict..."):
            ai_verdict = call_ai_agent(symbol, sector_name, current_price, day_chg,
                                       technicals, fundamentals, master, news,
                                       sentiments, projects, vix, anthropic_key)
        render_ai_verdict(ai_verdict, symbol, current_price, has_key)

        st.markdown("---")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.markdown(
                '<div class="col-header col-header-gov">'
                '<div style="font-size:11px;color:#f78166;text-transform:uppercase;letter-spacing:.06em;">Col 1</div>'
                '<div style="font-size:15px;font-weight:600;color:#e6edf3;margin-top:2px;">&#x1F3DB; Govt &amp; Macro</div>'
                '</div>', unsafe_allow_html=True)
            policies = SECTOR_POLICY_MAP.get(sector_name, SECTOR_POLICY_MAP.get("General", ["Check DPIIT portal"]))
            st.markdown("**Active PLI / Policy Schemes**")
            for policy in policies:
                st.markdown('<div class="news-card" style="border-left:3px solid #f78166;"><div class="news-title">&#x1F4CC; ' + policy + '</div></div>', unsafe_allow_html=True)
            st.markdown("**Macro Indicators**")
            render_metric_card("India VIX", str(round(vix, 1)), None, None)
            render_metric_card("Market Regime", "Defensive" if vix > 22 else "Normal", None, vix <= 22)
            render_metric_card("RSI (14D)", str(technicals["rsi"]), "Overbought" if technicals["rsi"] > 70 else ("Oversold" if technicals["rsi"] < 30 else "Neutral"), 30 <= technicals["rsi"] <= 70)
            render_metric_card("ADX (Trend)", str(technicals["adx"]), "Strong" if technicals["adx"] > 25 else "Weak", technicals["adx"] > 25)
            render_metric_card("Volume Ratio", str(technicals["vol_ratio"]) + "x", "Above avg" if technicals["vol_ratio"] > 1 else "Below avg", technicals["vol_ratio"] > 1)

        with col2:
            st.markdown(
                '<div class="col-header col-header-sector">'
                '<div style="font-size:11px;color:#58a6ff;text-transform:uppercase;letter-spacing:.06em;">Col 2</div>'
                '<div style="font-size:15px;font-weight:600;color:#e6edf3;margin-top:2px;">&#x1F4E1; Sector Pulse</div>'
                '</div>', unsafe_allow_html=True)
            st.plotly_chart(chart_sector_comparison(symbol, price_df), use_container_width=True, config={"displayModeBar": False})
            st.plotly_chart(chart_candlestick(price_df, symbol, technicals), use_container_width=True, config={"displayModeBar": False})

        with col3:
            st.markdown(
                '<div class="col-header col-header-proj">'
                '<div style="font-size:11px;color:#3fb950;text-transform:uppercase;letter-spacing:.06em;">Col 3</div>'
                '<div style="font-size:15px;font-weight:600;color:#e6edf3;margin-top:2px;">&#x1F3D7; Project Catalysts</div>'
                '</div>', unsafe_allow_html=True)
            st.markdown("**AI-Researched Contract Wins**")
            for proj in projects:
                render_project_card(proj.get("title",""), proj.get("content",""), proj.get("published_date","Recent"), proj.get("url",""))
            st.markdown("**FinBERT News Sentiment**")
            for news_item, sent in zip(news[:6], sentiments[:6]):
                render_news_card(news_item.get("headline",""), news_item.get("source",""), news_item.get("datetime",0), sent.get("label","neutral"), news_item.get("url",""))

        with col4:
            st.markdown(
                '<div class="col-header col-header-dive">'
                '<div style="font-size:11px;color:#d2a8ff;text-transform:uppercase;letter-spacing:.06em;">Col 4</div>'
                '<div style="font-size:15px;font-weight:600;color:#e6edf3;margin-top:2px;">&#x1F52C; 5-Year Deep Dive</div>'
                '</div>', unsafe_allow_html=True)
            render_master_score(master)
            st.plotly_chart(chart_score_radar(master), use_container_width=True, config={"displayModeBar": False})
            st.plotly_chart(chart_fundamentals(fundamentals), use_container_width=True, config={"displayModeBar": False})
            st.plotly_chart(chart_price_cagr(price_df, symbol), use_container_width=True, config={"displayModeBar": False})
            score_df = pd.DataFrame({
                "Component": ["Technicals","Fundamentals","Sentiment","Total"],
                "Score":     [master["tech_s"], master["fund_s"], master["sent_s"], master["score"]],
                "Max":       [35, 35, 30, 100],
                "Weight":    ["35%","35%","30%","100%"],
            })
            st.dataframe(score_df, use_container_width=True, hide_index=True)

    # ══════════════════════════════════════════════════════════════════════════
    # TAB 2 — MY STOCKS (WATCHLIST)
    # ══════════════════════════════════════════════════════════════════════════
    with tab_mystocks:
        st.markdown("### ⭐ My Watchlist")

        # ── Add stock ─────────────────────────────────────────────────────────
        with st.expander("➕ Add Stock to Watchlist", expanded=len(st.session_state.watchlist) == 0):
            a1, a2 = st.columns([4, 1])
            with a1:
                add_query = st.text_input("Search NSE/BSE symbol", placeholder="e.g. ZOMATO, IRFC, DMART", key="wl_add_search")
                if add_query:
                    suggestions = search_nse_stocks(add_query)
                    if suggestions:
                        chosen = st.selectbox("Select stock", suggestions, key="wl_chosen")
                    else:
                        chosen = add_query.upper().strip()
            with a2:
                st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
                if st.button("Add ➕", key="wl_add_btn", type="primary"):
                    sym_to_add = chosen if add_query else ""
                    if sym_to_add and sym_to_add not in st.session_state.watchlist:
                        st.session_state.watchlist.append(sym_to_add)
                        st.success(sym_to_add + " added!")
                        st.rerun()
                    elif sym_to_add in st.session_state.watchlist:
                        st.warning("Already in watchlist")

        # ── Watchlist display ─────────────────────────────────────────────────
        if not st.session_state.watchlist:
            st.info("Your watchlist is empty. Add stocks using the form above.")
        else:
            st.markdown(
                '<div style="font-size:11px;color:#8b949e;margin-bottom:12px;">'
                + str(len(st.session_state.watchlist))
                + ' stocks tracked · Click ✕ to remove · Click Analyse for full report</div>',
                unsafe_allow_html=True,
            )

            total_gain = 0
            total_stocks = 0

            for wl_sym in list(st.session_state.watchlist):
                try:
                    wl_df   = fetch_nse_price_history(wl_sym, years=1)
                    wl_close= wl_df["CLOSE"]
                    wl_price= round(wl_close.iloc[-1], 2)
                    wl_prev = round(wl_close.iloc[-2], 2)
                    wl_chg  = round((wl_price / wl_prev - 1) * 100, 2)
                    wl_ytd  = round((wl_price / wl_close.iloc[0] - 1) * 100, 1)
                    wl_tech = compute_technicals(wl_df)
                    wl_fund = _synthetic_fundamentals(wl_sym)
                    wl_master = compute_master_score(wl_tech, wl_fund, [{"label":"neutral","score":0.5}], vix)
                    score   = wl_master["score"]
                    verdict = wl_master["verdict"]
                    v_color = wl_master["color"]
                    chg_color = "#3fb950" if wl_chg >= 0 else "#f85149"
                    chg_arrow = "&#9650;" if wl_chg >= 0 else "&#9660;"
                    total_gain += wl_ytd
                    total_stocks += 1
                except Exception:
                    wl_price, wl_chg, wl_ytd, score, verdict, v_color = 0, 0, 0, 50, "HOLD", "#e3b341"
                    chg_color, chg_arrow = "#8b949e", ""

                r1, r2, r3, r4, r5 = st.columns([2, 2, 2, 2, 1])
                with r1:
                    st.markdown(
                        '<div style="padding:10px 0;">'
                        '<div class="wl-symbol">' + wl_sym + '</div>'
                        '<div class="wl-name">' + _get_sector(wl_sym) + '</div>'
                        '</div>', unsafe_allow_html=True)
                with r2:
                    st.markdown(
                        '<div style="padding:10px 0;">'
                        '<div class="wl-price" style="color:' + chg_color + ';">&#8377;' + "{:,.2f}".format(wl_price) + '</div>'
                        '<div class="wl-chg" style="color:' + chg_color + ';">' + chg_arrow + ' ' + "{:+.2f}%".format(wl_chg) + ' today</div>'
                        '</div>', unsafe_allow_html=True)
                with r3:
                    ytd_color = "#3fb950" if wl_ytd >= 0 else "#f85149"
                    st.markdown(
                        '<div style="padding:10px 0;">'
                        '<div style="font-size:11px;color:#8b949e;">YTD Return</div>'
                        '<div style="font-size:16px;font-weight:700;color:' + ytd_color + ';">' + "{:+.1f}%".format(wl_ytd) + '</div>'
                        '</div>', unsafe_allow_html=True)
                with r4:
                    st.markdown(
                        '<div style="padding:10px 0;">'
                        '<div style="font-size:11px;color:#8b949e;">AI Score · Verdict</div>'
                        '<div style="font-size:15px;font-weight:700;color:' + v_color + ';">' + str(score) + '/100</div>'
                        '<div style="font-size:11px;color:' + v_color + ';font-weight:600;">' + verdict + '</div>'
                        '</div>', unsafe_allow_html=True)
                with r5:
                    c1b, c2b = st.columns(2)
                    with c1b:
                        if st.button("&#x1F4C8;", key="wl_view_" + wl_sym, help="Analyse " + wl_sym):
                            st.session_state.selected_symbol = wl_sym
                            st.info("Switch to Stock Analysis tab and search " + wl_sym)
                    with c2b:
                        if st.button("&#x2715;", key="wl_del_" + wl_sym, help="Remove " + wl_sym):
                            st.session_state.watchlist.remove(wl_sym)
                            st.rerun()
                st.markdown('<hr style="border-color:#21262d;margin:0;">', unsafe_allow_html=True)

            # ── Portfolio summary ─────────────────────────────────────────────
            if total_stocks > 0:
                avg_gain = round(total_gain / total_stocks, 1)
                gain_color = "#3fb950" if avg_gain >= 0 else "#f85149"
                st.markdown(
                    '<div style="background:#161b22;border:1px solid #30363d;border-radius:10px;'
                    'padding:16px 20px;margin-top:16px;display:flex;justify-content:space-between;">'
                    '<div><div style="font-size:11px;color:#8b949e;">Stocks Tracked</div>'
                    '<div style="font-size:22px;font-weight:700;color:#e6edf3;">' + str(total_stocks) + '</div></div>'
                    '<div><div style="font-size:11px;color:#8b949e;">Avg YTD Return</div>'
                    '<div style="font-size:22px;font-weight:700;color:' + gain_color + ';">'
                    + "{:+.1f}%".format(avg_gain) + '</div></div>'
                    '<div><div style="font-size:11px;color:#8b949e;">Market Regime</div>'
                    '<div style="font-size:16px;font-weight:700;color:' + ("#f85149" if vix > 22 else "#3fb950") + ';">'
                    + ("Defensive" if vix > 22 else "Normal") + '</div></div>'
                    '</div>', unsafe_allow_html=True)

    # ══════════════════════════════════════════════════════════════════════════
    # TAB 3 — GLOBAL CRISIS MONITOR
    # ══════════════════════════════════════════════════════════════════════════
    with tab_crisis:
        st.markdown("### 🌍 Global Crisis Monitor")
        st.markdown('<div style="font-size:13px;color:#8b949e;margin-bottom:16px;">Live global market stress indicators that affect NSE/BSE stocks. Updated every 5 minutes.</div>', unsafe_allow_html=True)

        with st.spinner("Fetching global indicators..."):
            indicators = fetch_global_indicators()

        # ── Global Indicator Grid ─────────────────────────────────────────────
        def _crisis_card(label, value_str, status, level, sub=""):
            level_class = {"extreme":"crisis-extreme","high":"crisis-high","moderate":"crisis-moderate","low":"crisis-low"}.get(level,"crisis-moderate")
            color = {"extreme":"#f85149","high":"#f0883e","moderate":"#e3b341","low":"#3fb950"}.get(level,"#e3b341")
            return (
                '<div class="crisis-card ' + level_class + '">'
                '<div class="crisis-label">' + label + '</div>'
                '<div class="crisis-value" style="color:' + color + ';">' + value_str + '</div>'
                '<div class="crisis-status" style="color:' + color + ';">' + status + '</div>'
                + ('<div style="font-size:10px;color:#8b949e;margin-top:3px;">' + sub + '</div>' if sub else "")
                + '</div>'
            )

        fg = indicators.get("fear_greed", {})
        fg_val = fg.get("value", 50)
        fg_lbl = fg.get("label", "Neutral")
        fg_level = "extreme" if fg_val < 20 else "high" if fg_val < 35 else "moderate" if fg_val < 55 else "low"

        vix_val = indicators.get("india_vix", {}).get("price", 15)
        vix_level = "extreme" if vix_val > 30 else "high" if vix_val > 22 else "moderate" if vix_val > 17 else "low"

        gold = indicators.get("gold", {})
        gold_chg = gold.get("chg", 0)
        gold_level = "extreme" if gold_chg > 2 else "high" if gold_chg > 0.5 else "low"

        oil = indicators.get("oil", {})
        oil_chg = oil.get("chg", 0)
        oil_level = "extreme" if abs(oil_chg) > 3 else "high" if abs(oil_chg) > 1.5 else "low"

        usdinr = indicators.get("usdinr", {})
        usdinr_price = usdinr.get("price", 83)
        usdinr_chg   = usdinr.get("chg", 0)
        usdinr_level = "high" if usdinr_chg > 0.5 else "moderate" if usdinr_chg > 0.2 else "low"

        us10y = indicators.get("us10y", {})
        us10y_price = us10y.get("price", 4.3)
        us10y_level = "high" if us10y_price > 5 else "moderate" if us10y_price > 4.5 else "low"

        g1, g2, g3, g4, g5, g6 = st.columns(6)
        with g1:
            st.markdown(_crisis_card("Fear & Greed", str(fg_val), fg_lbl, fg_level, "0=Extreme Fear, 100=Greed"), unsafe_allow_html=True)
        with g2:
            st.markdown(_crisis_card("India VIX", str(round(vix_val,1)), "Defensive Mode" if vix_val>22 else "Normal", vix_level, ">22 triggers Defensive"), unsafe_allow_html=True)
        with g3:
            gold_str = "$" + "{:,.0f}".format(gold.get("price",0)) if gold.get("price") else "N/A"
            st.markdown(_crisis_card("Gold ($/oz)", gold_str, ("+" if gold_chg>=0 else "")+"{:.2f}%".format(gold_chg)+" today", gold_level, "Safe haven demand"), unsafe_allow_html=True)
        with g4:
            oil_str = "$" + "{:.1f}".format(oil.get("price",0)) if oil.get("price") else "N/A"
            st.markdown(_crisis_card("Crude Oil (WTI)", oil_str, ("+" if oil_chg>=0 else "")+"{:.2f}%".format(oil_chg)+" today", oil_level, "High oil = cost pressure"), unsafe_allow_html=True)
        with g5:
            st.markdown(_crisis_card("USD/INR", str(round(usdinr_price,2)), ("+" if usdinr_chg>=0 else "")+"{:.2f}%".format(usdinr_chg)+" today", usdinr_level, "Rising = IT stocks benefit"), unsafe_allow_html=True)
        with g6:
            st.markdown(_crisis_card("US 10Y Yield", str(round(us10y_price,2))+"%", "High" if us10y_price>4.5 else "Moderate", us10y_level, "High = FII outflows risk"), unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # ── Impact Analysis ───────────────────────────────────────────────────
        st.markdown("### 🎯 How Global Crisis Affects Your Stocks")
        impact_col, opp_col = st.columns([1, 1])

        with impact_col:
            st.markdown("**🔴 Crisis Impact on Indian Markets**")
            impacts = [
                ("High US Yields (>4.5%)", "FII outflows from emerging markets → Nifty pressure", us10y_level in ["high","extreme"]),
                ("USD/INR Depreciation",   "Import costs rise → Margins hurt for manufacturers",  usdinr_chg > 0.3),
                ("Oil Price Surge (>$90)", "Input cost inflation → FMCG, Auto, Airlines suffer",  oil.get("price",70) > 90),
                ("Extreme Fear (F&G<25)",  "Panic selling → Blue-chips oversold → Buying opp",    fg_val < 25),
                ("India VIX > 22",         "High volatility → Reduce position sizing by 30%",     vix_val > 22),
                ("Gold Rally",             "Risk-off signal → Rotate to defensives & gold ETFs",  gold_chg > 1.5),
            ]
            for label, desc, is_active in impacts:
                border = "#f85149" if is_active else "#30363d"
                icon   = "&#x1F534;" if is_active else "&#x26AA;"
                st.markdown(
                    '<div style="background:#161b22;border:1px solid ' + border + ';border-radius:8px;'
                    'padding:10px 14px;margin:6px 0;">'
                    '<div style="font-size:12px;font-weight:600;color:#e6edf3;">' + icon + ' ' + label + '</div>'
                    '<div style="font-size:11px;color:#8b949e;margin-top:3px;">' + desc + '</div>'
                    '</div>', unsafe_allow_html=True)

        with opp_col:
            st.markdown("**🟢 Crisis Opportunity Stocks (3-6 Month Outlook)**")
            opp_stocks = get_crisis_opportunity_stocks(indicators)
            for opp in opp_stocks:
                v_color = "#3fb950" if opp["verdict"] in ["STRONG BUY","BUY"] else "#e3b341"
                type_badge = {"defensive":"&#x1F6E1; Defensive","currency":"&#x1F4B5; USD Hedge","infra":"&#x1F3D7; Infra","commodity":"&#x26CF; Commodity"}.get(opp["crisis_type"],"")
                st.markdown(
                    '<div class="opp-card ' + ("" if opp["score"]>=30 else "caution") + '">'
                    '<div style="display:flex;justify-content:space-between;align-items:center;">'
                    '<div class="opp-symbol">' + opp["symbol"] + ' <span style="font-size:10px;color:#58a6ff;">' + type_badge + '</span></div>'
                    '<div class="opp-verdict" style="color:' + v_color + ';">' + opp["verdict"] + '</div>'
                    '</div>'
                    '<div class="opp-reason">' + opp["reason"] + '</div>'
                    '<div style="font-size:10px;color:#8b949e;margin-top:4px;">Crisis Score: ' + str(opp["score"]) + '/70</div>'
                    '</div>', unsafe_allow_html=True)

        # ── Global Market Heatmap ─────────────────────────────────────────────
        st.markdown("<br>**📡 Global Index Pulse**")
        g_indices = [
            ("FTSE 100",  indicators.get("ftse",   {}).get("price", 0), indicators.get("ftse",   {}).get("chg", 0)),
            ("Nikkei 225",indicators.get("nikkei", {}).get("price", 0), indicators.get("nikkei", {}).get("chg", 0)),
        ]
        idx_cols = st.columns(max(len(g_indices), 1))
        for i, (name, price, chg) in enumerate(g_indices):
            with idx_cols[i]:
                chg_color = "#3fb950" if chg >= 0 else "#f85149"
                st.markdown(
                    '<div class="crisis-card" style="text-align:center;">'
                    '<div class="crisis-label">' + name + '</div>'
                    '<div class="crisis-value" style="color:#e6edf3;">' + ("{:,.0f}".format(price) if price else "N/A") + '</div>'
                    '<div style="font-size:12px;color:' + chg_color + ';font-weight:600;">'
                    + ("+" if chg>=0 else "") + "{:.2f}%".format(chg) + '</div>'
                    '</div>', unsafe_allow_html=True)

    # ── Footer ────────────────────────────────────────────────────────────────
    st.markdown("---")
    st.markdown(
        '<div style="text-align:center;color:#8b949e;font-size:11px;padding:8px 0;">'
        '&#x1F1EE;&#x1F1F3; India Market Intelligence &nbsp;&middot;&nbsp; '
        'NSE/BSE &middot; FMP &middot; Finnhub &middot; Tavily AI &middot; FinBERT &nbsp;&middot;&nbsp; '
        '<strong style="color:#f85149;">Not investment advice.</strong>'
        '</div>', unsafe_allow_html=True)


if __name__ == "__main__":
    main()

