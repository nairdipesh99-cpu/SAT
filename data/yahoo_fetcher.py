import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time
import streamlit as st
import yfinance as yf

# ── NSE Headers ──
NSE_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "*/*",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.nseindia.com/",
}

# ── Index fallback data (used when Yahoo rate-limits) ──
INDEX_FALLBACK = {
    "^NSEI":     {"name": "NIFTY 50",     "price": None},
    "^BSESN":    {"name": "SENSEX",       "price": None},
    "^CNXMETAL": {"name": "NIFTY METAL",  "price": None},
    "^CNXPHARMA":{"name": "NIFTY PHARMA", "price": None},
    "^GSPC":     {"name": "S&P 500",      "price": None},
    "^DJI":      {"name": "DOW JONES",    "price": None},
    "^IXIC":     {"name": "NASDAQ",       "price": None},
    "^VIX":      {"name": "VIX",          "price": None},
    "^FTSE":     {"name": "FTSE 100",     "price": None},
    "^FTMC":     {"name": "FTSE 250",     "price": None},
    "GBPUSD=X":  {"name": "GBP/USD",      "price": None},
}

def _nse_session():
    session = requests.Session()
    try:
        session.get("https://www.nseindia.com", headers=NSE_HEADERS, timeout=6)
    except:
        pass
    return session

@st.cache_data(ttl=300)
def get_nse_quote(symbol):
    """Fetch live quote directly from NSE India API"""
    try:
        session = _nse_session()
        url = f"https://www.nseindia.com/api/quote-equity?symbol={symbol}"
        r = session.get(url, headers=NSE_HEADERS, timeout=8)
        if r.status_code == 200:
            data    = r.json()
            pd_info = data.get("priceInfo", {})
            meta    = data.get("metadata", {})
            sec     = data.get("securityInfo", {})
            price   = pd_info.get("lastPrice")
            prev    = pd_info.get("previousClose") or price
            if not price:
                return None
            change_pct = ((price - prev) / prev * 100) if prev else 0
            return {
                "ticker":         symbol + ".NS",
                "name":           meta.get("companyName", symbol),
                "price":          price,
                "prev_close":     prev,
                "change_pct":     round(change_pct, 2),
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
    except Exception:
        pass
    return None

@st.cache_data(ttl=300)
def get_nse_index(symbol):
    """Fetch NSE index data (NIFTY 50, NIFTY METAL etc)"""
    try:
        session = _nse_session()
        url = "https://www.nseindia.com/api/allIndices"
        r   = session.get(url, headers=NSE_HEADERS, timeout=8)
        if r.status_code == 200:
            indices = r.json().get("data", [])
            name_map = {
                "^NSEI":      "Nifty 50",
                "^CNXMETAL":  "Nifty Metal",
                "^CNXPHARMA": "Nifty Pharma",
                "^CNXIT":     "Nifty IT",
            }
            target = name_map.get(symbol, "").lower()
            for idx in indices:
                if idx.get("indexSymbol","").lower() == target or idx.get("index","").lower() == target:
                    price = idx.get("last")
                    prev  = idx.get("previousClose") or price
                    chg   = ((price - prev)/prev*100) if prev else 0
                    return {
                        "ticker": symbol,
                        "name": idx.get("index", symbol),
                        "price": price,
                        "prev_close": prev,
                        "change_pct": round(chg, 2),
                        "day_high": idx.get("high"),
                        "day_low":  idx.get("low"),
                        "week_52_high": idx.get("yearHigh"),
                        "week_52_low":  idx.get("yearLow"),
                        "volume": None, "avg_volume": None, "market_cap": None,
                        "pe_ratio": None, "pb_ratio": None, "revenue_growth": 0,
                        "profit_margin": 0, "debt_to_equity": None, "current_ratio": None,
                        "roe": 0, "eps": None, "dividend_yield": 0,
                        "analyst_rating": "", "target_price": None,
                        "sector": "", "industry": "", "currency": "INR",
                        "exchange": "NSE", "beta": None,
                    }
    except Exception:
        pass
    return None

@st.cache_data(ttl=300)
def _yf_get_info_cached(ticker):
    """yfinance info with retry — cached to avoid repeat 429s"""
    for attempt in range(3):
        try:
            t    = yf.Ticker(ticker)
            info = t.info
            if info and (info.get("regularMarketPrice") or info.get("currentPrice") or info.get("previousClose")):
                return info
        except Exception:
            pass
        time.sleep(2 * (attempt + 1))
    return {}

@st.cache_data(ttl=300)
def get_stock_info(ticker):
    """Route Indian tickers to NSE, indices smartly, others to yfinance"""

    # ── NSE Indices ──
    if ticker in ("^NSEI", "^CNXMETAL", "^CNXPHARMA", "^CNXIT"):
        result = get_nse_index(ticker)
        if result:
            return result

    # ── Indian equity stocks ──
    if ticker.endswith(".NS") or ticker.endswith(".BO"):
        symbol = ticker.replace(".NS", "").replace(".BO", "")
        result = get_nse_quote(symbol)
        if result:
            return result
        # Fall through to yfinance if NSE fails

    # ── Global indices + US/UK stocks → yfinance with rate limit guard ──
    try:
        info = _yf_get_info_cached(ticker)
        if not info:
            return None
        price = info.get("regularMarketPrice") or info.get("currentPrice") or info.get("previousClose")
        prev  = info.get("previousClose") or price
        if not price:
            return None
        change_pct = ((price - prev) / prev * 100) if prev else 0
        return {
            "ticker":         ticker,
            "name":           info.get("longName") or info.get("shortName", ticker),
            "price":          price,
            "prev_close":     prev,
            "change_pct":     round(change_pct, 2),
            "day_high":       info.get("dayHigh"),
            "day_low":        info.get("dayLow"),
            "week_52_high":   info.get("fiftyTwoWeekHigh"),
            "week_52_low":    info.get("fiftyTwoWeekLow"),
            "volume":         info.get("volume"),
            "avg_volume":     info.get("averageVolume"),
            "market_cap":     info.get("marketCap"),
            "pe_ratio":       info.get("trailingPE") or info.get("forwardPE"),
            "pb_ratio":       info.get("priceToBook"),
            "revenue_growth": round((info.get("revenueGrowth") or 0) * 100, 2),
            "profit_margin":  round((info.get("profitMargins") or 0) * 100, 2),
            "debt_to_equity": info.get("debtToEquity"),
            "current_ratio":  info.get("currentRatio"),
            "roe":            round((info.get("returnOnEquity") or 0) * 100, 2),
            "eps":            info.get("trailingEps"),
            "dividend_yield": round((info.get("dividendYield") or 0) * 100, 2),
            "analyst_rating": info.get("recommendationKey", "").upper(),
            "target_price":   info.get("targetMeanPrice"),
            "sector":         info.get("sector", ""),
            "industry":       info.get("industry", ""),
            "currency":       info.get("currency", "USD"),
            "exchange":       info.get("exchange", ""),
            "beta":           info.get("beta"),
        }
    except Exception:
        return None

@st.cache_data(ttl=600)
def get_historical_data(ticker, period="5y", interval="1wk"):
    """NSE historical for Indian stocks, yfinance for others"""
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
        except Exception:
            pass
    # yfinance fallback
    try:
        t  = yf.Ticker(ticker)
        df = t.history(period=period, interval=interval)
        if df.empty:
            return None
        df.index = pd.to_datetime(df.index)
        return df[["Open","High","Low","Close","Volume"]].dropna()
    except:
        return None

@st.cache_data(ttl=120)
def get_intraday_data(ticker):
    """NSE intraday for Indian stocks, yfinance for others"""
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
        except Exception:
            pass
    try:
        t  = yf.Ticker(ticker)
        df = t.history(period="1d", interval="5m")
        if df.empty:
            return None
        df.index = pd.to_datetime(df.index)
        return df[["Open","High","Low","Close","Volume"]].dropna()
    except:
        return None

@st.cache_data(ttl=300)
def search_ticker(query):
    """Search: NSE first for Indian stocks, yfinance fallback"""
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
    except Exception:
        pass
    for suffix in [".NS", ".BO", "", ".L"]:
        try:
            candidate = query.upper() + suffix
            info = _yf_get_info_cached(candidate)
            if info:
                return candidate
        except:
            pass
        time.sleep(0.3)
    return None

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
