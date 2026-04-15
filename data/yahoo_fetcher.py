import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time
import streamlit as st

# ── Ticker name map for display ──
TICKER_NAMES = {
    "^NSEI":      "NIFTY 50",
    "^BSESN":     "SENSEX",
    "^CNXMETAL":  "NIFTY METAL",
    "^CNXPHARMA": "NIFTY PHARMA",
    "^GSPC":      "S&P 500",
    "^DJI":       "DOW JONES",
    "^IXIC":      "NASDAQ",
    "^VIX":       "VIX",
    "^FTSE":      "FTSE 100",
    "^FTMC":      "FTSE 250",
    "GBPUSD=X":   "GBP/USD",
}

def _get_currency(ticker):
    if ticker.endswith(".NS") or ticker.endswith(".BO") or ticker in ("^NSEI","^BSESN","^CNXMETAL","^CNXPHARMA"):
        return "INR"
    if ticker.endswith(".L") or ticker in ("^FTSE","^FTMC"):
        return "GBP"
    return "USD"

def _get_exchange(ticker):
    if ticker.endswith(".NS") or ticker in ("^NSEI","^BSESN","^CNXMETAL","^CNXPHARMA"):
        return "NSE"
    if ticker.endswith(".BO"):
        return "BSE"
    if ticker.endswith(".L") or ticker in ("^FTSE","^FTMC"):
        return "LSE"
    return "NYSE"

@st.cache_data(ttl=300)
def get_stock_info(ticker):
    """Fetch stock info using yfinance history only — avoids 429 from .info"""
    try:
        import yfinance as yf
        t    = yf.Ticker(ticker)
        hist = t.history(period="5d", interval="1d")
        if hist is None or hist.empty:
            return None
        closes = hist["Close"].dropna()
        if closes.empty:
            return None
        price = float(closes.iloc[-1])
        prev  = float(closes.iloc[-2]) if len(closes) > 1 else price
        chg   = round(((price - prev) / prev * 100), 2) if prev else 0

        # Try fast_info for name — much less likely to 429 than .info
        name = TICKER_NAMES.get(ticker, ticker)
        sector = ""
        try:
            fi     = t.fast_info
            fname  = getattr(fi, "long_name", None) or getattr(fi, "short_name", None)
            if fname:
                name = fname
        except:
            pass

        return {
            "ticker":         ticker,
            "name":           name,
            "price":          price,
            "prev_close":     prev,
            "change_pct":     chg,
            "day_high":       float(hist["High"].iloc[-1]),
            "day_low":        float(hist["Low"].iloc[-1]),
            "week_52_high":   float(closes.max()),
            "week_52_low":    float(closes.min()),
            "volume":         int(hist["Volume"].iloc[-1]) if "Volume" in hist.columns else None,
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
            "sector":         sector,
            "industry":       "",
            "currency":       _get_currency(ticker),
            "exchange":       _get_exchange(ticker),
            "beta":           None,
        }
    except Exception:
        return None

@st.cache_data(ttl=600)
def get_historical_data(ticker, period="5y", interval="1wk"):
    """Fetch historical OHLCV data"""
    try:
        import yfinance as yf
        t  = yf.Ticker(ticker)
        df = t.history(period=period, interval=interval)
        if df is None or df.empty:
            return None
        df.index = pd.to_datetime(df.index)
        return df[["Open","High","Low","Close","Volume"]].dropna()
    except:
        return None

@st.cache_data(ttl=120)
def get_intraday_data(ticker):
    """Fetch intraday 5-minute data"""
    try:
        import yfinance as yf
        t  = yf.Ticker(ticker)
        df = t.history(period="1d", interval="5m")
        if df is None or df.empty:
            return None
        df.index = pd.to_datetime(df.index)
        return df[["Open","High","Low","Close","Volume"]].dropna()
    except:
        return None

@st.cache_data(ttl=300)
def search_ticker(query):
    """Search for ticker symbol"""
    indian_map = {
        "tata steel":   "TATASTEEL.NS",
        "jswsteel":     "JSWSTEEL.NS",
        "jsw steel":    "JSWSTEEL.NS",
        "sail":         "SAIL.NS",
        "reliance":     "RELIANCE.NS",
        "infosys":      "INFY.NS",
        "tcs":          "TCS.NS",
        "hdfc bank":    "HDFCBANK.NS",
        "icici bank":   "ICICIBANK.NS",
        "wipro":        "WIPRO.NS",
        "ongc":         "ONGC.NS",
        "coal india":   "COALINDIA.NS",
        "sun pharma":   "SUNPHARMA.NS",
        "bajaj finance":"BAJFINANCE.NS",
        "asian paints": "ASIANPAINT.NS",
        "maruti":       "MARUTI.NS",
        "jindal steel": "JINDALSTEL.NS",
        "apl apollo":   "APLAPOLLO.NS",
        "hindalco":     "HINDALCO.NS",
        "vedanta":      "VEDL.NS",
        "sbi":          "SBIN.NS",
        "hdfc":         "HDFCBANK.NS",
        "icici":        "ICICIBANK.NS",
        "axis bank":    "AXISBANK.NS",
        "kotak":        "KOTAKBANK.NS",
        "ltim":         "LTIM.NS",
        "hcl tech":     "HCLTECH.NS",
        "tech mahindra":"TECHM.NS",
        "titan":        "TITAN.NS",
        "nestle":       "NESTLEIND.NS",
        "bajaj auto":   "BAJAJ-AUTO.NS",
        "dr reddy":     "DRREDDY.NS",
        "cipla":        "CIPLA.NS",
        "ntpc":         "NTPC.NS",
        "power grid":   "POWERGRID.NS",
        "adani ports":  "ADANIPORTS.NS",
        "bpcl":         "BPCL.NS",
    }
    q = query.lower().strip()
    if q in indian_map:
        return indian_map[q]

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
    return None

def calculate_technicals(df):
    """Calculate RSI, MAs from historical data"""
    if df is None or len(df) < 20:
        return {}
    try:
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
    except:
        return {}

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
