import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time
import streamlit as st

# ──────────────────────────────────────────────
# NSE INDIA — Primary source for all Indian data
# ──────────────────────────────────────────────
NSE_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.nseindia.com/",
    "X-Requested-With": "XMLHttpRequest",
}

BSE_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Referer": "https://www.bseindia.com/",
}

NSE_INDEX_MAP = {
    "^NSEI":      "NIFTY 50",
    "^BSESN":     "SENSEX",
    "^CNXMETAL":  "NIFTY METAL",
    "^CNXPHARMA": "NIFTY PHARMA",
    "^CNXIT":     "NIFTY IT",
    "^CNXBANK":   "NIFTY BANK",
}

def _nse_session():
    s = requests.Session()
    try:
        s.get("https://www.nseindia.com", headers=NSE_HEADERS, timeout=6)
    except:
        pass
    return s

# ──────────────────────────────────────────────
# NSE — All Indices
# ──────────────────────────────────────────────
@st.cache_data(ttl=120)
def _get_all_nse_indices():
    try:
        session = _nse_session()
        r = session.get("https://www.nseindia.com/api/allIndices", headers=NSE_HEADERS, timeout=8)
        if r.status_code == 200:
            return r.json().get("data", [])
    except:
        pass
    return []

@st.cache_data(ttl=120)
def _get_bse_sensex():
    try:
        indices = _get_all_nse_indices()
        for idx in indices:
            if "SENSEX" in (idx.get("index") or "").upper():
                price = idx.get("last") or idx.get("lastPrice")
                prev  = idx.get("previousClose") or price
                chg   = ((price - prev) / prev * 100) if prev and price else 0
                return {
                    "ticker": "^BSESN", "name": "SENSEX",
                    "price": price, "prev_close": prev, "change_pct": round(chg, 2),
                    "day_high": idx.get("high"), "day_low": idx.get("low"),
                    "week_52_high": idx.get("yearHigh"), "week_52_low": idx.get("yearLow"),
                    "volume": None, "avg_volume": None, "market_cap": None,
                    "pe_ratio": None, "pb_ratio": None, "revenue_growth": 0,
                    "profit_margin": 0, "debt_to_equity": None, "current_ratio": None,
                    "roe": 0, "eps": None, "dividend_yield": 0,
                    "analyst_rating": "", "target_price": None,
                    "sector": "Index", "industry": "Index",
                    "currency": "INR", "exchange": "BSE", "beta": None,
                }
    except:
        pass
    return None

def _get_nse_index_quote(symbol):
    if symbol == "^BSESN":
        return _get_bse_sensex()
    target_name = NSE_INDEX_MAP.get(symbol, "").upper()
    indices = _get_all_nse_indices()
    for idx in indices:
        name = (idx.get("index") or idx.get("indexSymbol") or "").upper()
        if target_name and target_name in name:
            price = idx.get("last") or idx.get("lastPrice")
            prev  = idx.get("previousClose") or price
            chg   = ((price - prev) / prev * 100) if prev and price else 0
            return {
                "ticker": symbol,
                "name":   idx.get("index", target_name),
                "price":  price,
                "prev_close":   prev,
                "change_pct":   round(chg, 2),
                "day_high":     idx.get("high"),
                "day_low":      idx.get("low"),
                "week_52_high": idx.get("yearHigh"),
                "week_52_low":  idx.get("yearLow"),
                "volume": None, "avg_volume": None, "market_cap": None,
                "pe_ratio": None, "pb_ratio": None, "revenue_growth": 0,
                "profit_margin": 0, "debt_to_equity": None, "current_ratio": None,
                "roe": 0, "eps": None, "dividend_yield": 0,
                "analyst_rating": "", "target_price": None,
                "sector": "Index", "industry": "Index",
                "currency": "INR", "exchange": "NSE", "beta": None,
            }
    return None

# ──────────────────────────────────────────────
# NSE — Individual Equity Stocks
# ──────────────────────────────────────────────
@st.cache_data(ttl=180)
def _get_nse_equity(symbol):
    try:
        session = _nse_session()
        url = f"https://www.nseindia.com/api/quote-equity?symbol={symbol}"
        r   = session.get(url, headers=NSE_HEADERS, timeout=8)
        if r.status_code == 200:
            data    = r.json()
            pd_info = data.get("priceInfo", {})
            meta    = data.get("metadata", {})
            sec     = data.get("securityInfo", {})
            price   = pd_info.get("lastPrice")
            prev    = pd_info.get("previousClose") or price
            if not price:
                return None
            chg = ((price - prev) / prev * 100) if prev else 0
            return {
                "ticker":         symbol + ".NS",
                "name":           meta.get("companyName", symbol),
                "price":          price,
                "prev_close":     prev,
                "change_pct":     round(chg, 2),
                "day_high":       pd_info.get("intraDayHighLow", {}).get("max"),
                "day_low":        pd_info.get("intraDayHighLow", {}).get("min"),
                "week_52_high":   pd_info.get("weekHighLow", {}).get("max"),
                "week_52_low":    pd_info.get("weekHighLow", {}).get("min"),
                "volume":         data.get("marketDeptOrderBook", {}).get("tradeInfo", {}).get("totalTradedVolume"),
                "avg_volume":     None,
                "market_cap":     None,
                "pe_ratio":       sec.get("pdSymbolPe"),
                "pb_ratio":       None,
                "revenue_growth": 0,
                "profit_margin":  0,
                "debt_to_equity": None,
                "current_ratio":  None,
                "roe":            0,
                "eps":            None,
                "dividend_yield": 0,
                "analyst_rating": "",
                "target_price":   None,
                "sector":         meta.get("industry", ""),
                "industry":       meta.get("industry", ""),
                "currency":       "INR",
                "exchange":       "NSE",
                "beta":           None,
            }
    except:
        pass
    return None

# ──────────────────────────────────────────────
# US / UK — yfinance via history only (avoids 429)
# ──────────────────────────────────────────────
@st.cache_data(ttl=300)
def _get_us_uk_quote(ticker):
    try:
        import yfinance as yf
        time.sleep(0.5)
        t    = yf.Ticker(ticker)
        hist = t.history(period="5d", interval="1d")
        if hist is not None and not hist.empty:
            price = float(hist["Close"].dropna().iloc[-1])
            prev  = float(hist["Close"].dropna().iloc[-2]) if len(hist["Close"].dropna()) > 1 else price
            chg   = ((price - prev) / prev * 100) if prev else 0
            name  = ticker
            try:
                fi = t.fast_info
                name = getattr(fi, "long_name", None) or getattr(fi, "short_name", None) or ticker
            except:
                pass
            curr = "GBP" if ticker.endswith(".L") else "USD"
            exch = "LSE"  if ticker.endswith(".L") else "NYSE"
            return {
                "ticker":         ticker,
                "name":           name,
                "price":          price,
                "prev_close":     prev,
                "change_pct":     round(chg, 2),
                "day_high":       float(hist["High"].iloc[-1]),
                "day_low":        float(hist["Low"].iloc[-1]),
                "week_52_high":   None,
                "week_52_low":    None,
                "volume":         int(hist["Volume"].iloc[-1]),
                "avg_volume":     None,
                "market_cap":     None,
                "pe_ratio":       None,
                "pb_ratio":       None,
                "revenue_growth": 0,
                "profit_margin":  0,
                "debt_to_equity": None,
                "current_ratio":  None,
                "roe":            0,
                "eps":            None,
                "dividend_yield": 0,
                "analyst_rating": "",
                "target_price":   None,
                "sector":         "",
                "industry":       "",
                "currency":       curr,
                "exchange":       exch,
                "beta":           None,
            }
    except:
        pass
    return None

@st.cache_data(ttl=300)
def _get_global_index_quote(symbol):
    index_names = {
        "^GSPC":    "S&P 500",
        "^DJI":     "DOW JONES",
        "^IXIC":    "NASDAQ",
        "^VIX":     "VIX",
        "^FTSE":    "FTSE 100",
        "^FTMC":    "FTSE 250",
        "GBPUSD=X": "GBP/USD",
    }
    try:
        import yfinance as yf
        time.sleep(0.5)
        t    = yf.Ticker(symbol)
        hist = t.history(period="5d", interval="1d")
        if hist is not None and not hist.empty:
            closes = hist["Close"].dropna()
            price  = float(closes.iloc[-1])
            prev   = float(closes.iloc[-2]) if len(closes) > 1 else price
            chg    = ((price - prev) / prev * 100) if prev else 0
            curr   = "GBP" if any(x in symbol for x in ["FTSE","FTMC"]) else "USD"
            return {
                "ticker":         symbol,
                "name":           index_names.get(symbol, symbol),
                "price":          price,
                "prev_close":     prev,
                "change_pct":     round(chg, 2),
                "day_high":       float(hist["High"].iloc[-1]),
                "day_low":        float(hist["Low"].iloc[-1]),
                "week_52_high":   None,
                "week_52_low":    None,
                "volume":         None,
                "avg_volume":     None,
                "market_cap":     None,
                "pe_ratio":       None,
                "pb_ratio":       None,
                "revenue_growth": 0,
                "profit_margin":  0,
                "debt_to_equity": None,
                "current_ratio":  None,
                "roe":            0,
                "eps":            None,
                "dividend_yield": 0,
                "analyst_rating": "",
                "target_price":   None,
                "sector":         "Index",
                "industry":       "Index",
                "currency":       curr,
                "exchange":       "INDEX",
                "beta":           None,
            }
    except:
        pass
    return None

# ──────────────────────────────────────────────
# Main Router
# ──────────────────────────────────────────────
@st.cache_data(ttl=180)
def get_stock_info(ticker):
    if ticker in NSE_INDEX_MAP:
        return _get_nse_index_quote(ticker)
    if ticker.endswith(".NS") or ticker.endswith(".BO"):
        symbol = ticker.replace(".NS", "").replace(".BO", "")
        return _get_nse_equity(symbol)
    if ticker.startswith("^") or ticker in ("GBPUSD=X",):
        return _get_global_index_quote(ticker)
    return _get_us_uk_quote(ticker)

# ──────────────────────────────────────────────
# Historical Data
# ──────────────────────────────────────────────
@st.cache_data(ttl=600)
def get_historical_data(ticker, period="5y", interval="1wk"):
    if ticker.endswith(".NS") or ticker.endswith(".BO"):
        symbol   = ticker.replace(".NS","").replace(".BO","")
        days_map = {"1mo":30,"3mo":90,"6mo":180,"1y":365,"2y":730,"5y":1825}
        days     = days_map.get(period, 365)
        try:
            session = _nse_session()
            end   = datetime.now()
            start = end - timedelta(days=days)
            url = (
                f"https://www.nseindia.com/api/historical/cm/equity"
                f"?symbol={symbol}&series=[%22EQ%22]"
                f"&from={start.strftime('%d-%m-%Y')}&to={end.strftime('%d-%m-%Y')}"
            )
            r = session.get(url, headers=NSE_HEADERS, timeout=10)
            if r.status_code == 200:
                rows = r.json().get("data", [])
                if rows:
                    df = pd.DataFrame(rows)
                    df["Date"]   = pd.to_datetime(df["CH_TIMESTAMP"])
                    df["Open"]   = df["CH_OPENING_PRICE"].astype(float)
                    df["High"]   = df["CH_TRADE_HIGH_PRICE"].astype(float)
                    df["Low"]    = df["CH_TRADE_LOW_PRICE"].astype(float)
                    df["Close"]  = df["CH_CLOSING_PRICE"].astype(float)
                    df["Volume"] = df["CH_TOT_TRADED_QTY"].astype(float)
                    df.set_index("Date", inplace=True)
                    df.sort_index(inplace=True)
                    return df[["Open","High","Low","Close","Volume"]].dropna()
        except:
            pass
    try:
        import yfinance as yf
        time.sleep(0.5)
        t  = yf.Ticker(ticker)
        df = t.history(period=period, interval=interval)
        if df is None or df.empty:
            return None
        df.index = pd.to_datetime(df.index)
        return df[["Open","High","Low","Close","Volume"]].dropna()
    except:
        return None

# ──────────────────────────────────────────────
# Intraday Data
# ──────────────────────────────────────────────
@st.cache_data(ttl=120)
def get_intraday_data(ticker):
    if ticker.endswith(".NS") or ticker.endswith(".BO"):
        symbol = ticker.replace(".NS","").replace(".BO","")
        try:
            session = _nse_session()
            url = f"https://www.nseindia.com/api/chart-databyindex?index={symbol}EQN"
            r   = session.get(url, headers=NSE_HEADERS, timeout=8)
            if r.status_code == 200:
                raw = r.json().get("grapthData", [])
                if raw:
                    df = pd.DataFrame(raw, columns=["Timestamp","Close"])
                    df["Timestamp"] = pd.to_datetime(df["Timestamp"], unit="ms")
                    df.set_index("Timestamp", inplace=True)
                    df["Open"]   = df["Close"]
                    df["High"]   = df["Close"]
                    df["Low"]    = df["Close"]
                    df["Volume"] = 0
                    return df[["Open","High","Low","Close","Volume"]]
        except:
            pass
    try:
        import yfinance as yf
        time.sleep(0.5)
        t  = yf.Ticker(ticker)
        df = t.history(period="1d", interval="5m")
        if df is None or df.empty:
            return None
        df.index = pd.to_datetime(df.index)
        return df[["Open","High","Low","Close","Volume"]].dropna()
    except:
        return None

# ──────────────────────────────────────────────
# Search
# ──────────────────────────────────────────────
@st.cache_data(ttl=300)
def search_ticker(query):
    indian_map = {
        "tata steel": "TATASTEEL.NS", "jswsteel": "JSWSTEEL.NS", "jsw steel": "JSWSTEEL.NS",
        "sail": "SAIL.NS", "reliance": "RELIANCE.NS", "infosys": "INFY.NS",
        "tcs": "TCS.NS", "hdfc bank": "HDFCBANK.NS", "icici bank": "ICICIBANK.NS",
        "wipro": "WIPRO.NS", "ongc": "ONGC.NS", "coal india": "COALINDIA.NS",
        "sun pharma": "SUNPHARMA.NS", "bajaj finance": "BAJFINANCE.NS",
        "asian paints": "ASIANPAINT.NS", "maruti": "MARUTI.NS",
        "jindal steel": "JINDALSTEL.NS", "apl apollo": "APLAPOLLO.NS",
        "hindalco": "HINDALCO.NS", "vedanta": "VEDL.NS",
    }
    q = query.lower().strip()
    if q in indian_map:
        return indian_map[q]
    try:
        session = _nse_session()
        url = f"https://www.nseindia.com/api/search-autocomplete?q={query}"
        r   = session.get(url, headers=NSE_HEADERS, timeout=5)
        if r.status_code == 200:
            results = r.json().get("symbols", [])
            if results:
                sym = results[0].get("symbol")
                if sym:
                    return sym + ".NS"
    except:
        pass
    try:
        import yfinance as yf
        for suffix in [".NS", ".BO", "", ".L"]:
            try:
                candidate = query.upper() + suffix
                t    = yf.Ticker(candidate)
                hist = t.history(period="2d", interval="1d")
                if hist is not None and not hist.empty:
                    return candidate
            except:
                pass
            time.sleep(0.3)
    except:
        pass
    return None

# ──────────────────────────────────────────────
# Technicals
# ──────────────────────────────────────────────
def calculate_technicals(df):
    if df is None or len(df) < 20:
        return {}
    close = df["Close"]
    delta = close.diff()
    gain  = delta.clip(lower=0).rolling(14).mean()
    loss  = (-delta.clip(upper=0)).rolling(14).mean()
    rs    = gain / loss
    rsi   = round(float(100 - (100 / (1 + rs.iloc[-1]))), 1)
    ma50  = round(float(close.rolling(min(50,  len(close))).mean().iloc[-1]), 2)
    ma200 = round(float(close.rolling(min(200, len(close))).mean().iloc[-1]), 2)
    current = round(float(close.iloc[-1]), 2)
    high52  = round(float(close.tail(52).max()), 2)
    low52   = round(float(close.tail(52).min()), 2)
    pos52   = round((current - low52) / (high52 - low52) * 100, 1) if high52 != low52 else 50
    golden_cross = ma50 > ma200
    signal = "BULLISH" if golden_cross and rsi < 70 else "BEARISH" if not golden_cross and rsi > 50 else "NEUTRAL"
    return {
        "rsi":          rsi,
        "ma50":         ma50,
        "ma200":        ma200,
        "current":      current,
        "high_52w":     high52,
        "low_52w":      low52,
        "position_52w": pos52,
        "golden_cross": golden_cross,
        "signal":       signal,
    }

# ──────────────────────────────────────────────
# Ticker Lists
# ──────────────────────────────────────────────
def get_nifty50_tickers():
    return [
        "RELIANCE.NS","TCS.NS","HDFCBANK.NS","INFY.NS","ICICIBANK.NS",
        "HINDUNILVR.NS","ITC.NS","SBIN.NS","BHARTIARTL.NS","KOTAKBANK.NS",
        "LT.NS","AXISBANK.NS","ASIANPAINT.NS","MARUTI.NS","SUNPHARMA.NS",
        "TITAN.NS","ULTRACEMCO.NS","BAJFINANCE.NS","WIPRO.NS","HCLTECH.NS",
        "ONGC.NS","NTPC.NS","POWERGRID.NS","COALINDIA.NS","JSWSTEEL.NS",
        "TATASTEEL.NS","HINDALCO.NS","VEDL.NS","GRASIM.NS","TECHM.NS",
        "NESTLEIND.NS","DIVISLAB.NS","DRREDDY.NS","CIPLA.NS","EICHERMOT.NS",
        "BAJAJFINSV.NS","TATAMOTORS.NS","ADANIPORTS.NS","BPCL.NS","INDUSINDBK.NS",
    ]

def get_sp100_tickers():
    return [
        "AAPL","MSFT","GOOGL","AMZN","NVDA","META","TSLA","BRK-B","UNH","JNJ",
        "JPM","V","PG","XOM","MA","HD","CVX","MRK","ABBV","PFE",
        "AVGO","COST","LLY","BAC","KO","DIS","CSCO","TMO","WMT","PEP",
        "ACN","DHR","ABT","MCD","NKE","ADBE","CRM","TXN","LIN","CMCSA",
        "VZ","NFLX","PM","INTC","UPS","RTX","HON","AMD","QCOM","AMGN",
    ]

def get_ftse100_tickers():
    return [
        "SHEL.L","AZN.L","HSBA.L","ULVR.L","BP.L","RIO.L","GSK.L","DGE.L",
        "BATS.L","LSEG.L","NG.L","NWG.L","LLOY.L","BARC.L","VOD.L","AAL.L",
        "REL.L","EXPN.L","STAN.L","PRU.L","WPP.L","IAG.L","SBRY.L","TSCO.L",
    ]
