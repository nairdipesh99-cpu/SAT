import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def search_ticker(query):
    """Search for ticker by company name or ticker symbol"""
    try:
        ticker = yf.Ticker(query)
        info = ticker.info
        if info and info.get("regularMarketPrice"):
            return query.upper()
    except:
        pass
    # Common Indian stock mappings
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
    # Try adding .NS for NSE
    for suffix in [".NS", ".BO", ""]:
        try:
            t = yf.Ticker(query.upper() + suffix)
            i = t.info
            if i and i.get("regularMarketPrice"):
                return query.upper() + suffix
        except:
            pass
    return None

def get_stock_info(ticker):
    """Get comprehensive stock information"""
    try:
        t = yf.Ticker(ticker)
        info = t.info
        if not info:
            return None
        price = info.get("regularMarketPrice") or info.get("currentPrice") or info.get("previousClose")
        prev  = info.get("previousClose") or price
        change_pct = ((price - prev) / prev * 100) if prev and price else 0
        return {
            "ticker":          ticker,
            "name":            info.get("longName") or info.get("shortName", ticker),
            "price":           price,
            "prev_close":      prev,
            "change_pct":      round(change_pct, 2),
            "day_high":        info.get("dayHigh"),
            "day_low":         info.get("dayLow"),
            "week_52_high":    info.get("fiftyTwoWeekHigh"),
            "week_52_low":     info.get("fiftyTwoWeekLow"),
            "volume":          info.get("volume"),
            "avg_volume":      info.get("averageVolume"),
            "market_cap":      info.get("marketCap"),
            "pe_ratio":        info.get("trailingPE") or info.get("forwardPE"),
            "pb_ratio":        info.get("priceToBook"),
            "revenue_growth":  round((info.get("revenueGrowth") or 0) * 100, 2),
            "profit_margin":   round((info.get("profitMargins") or 0) * 100, 2),
            "debt_to_equity":  info.get("debtToEquity"),
            "current_ratio":   info.get("currentRatio"),
            "roe":             round((info.get("returnOnEquity") or 0) * 100, 2),
            "eps":             info.get("trailingEps"),
            "dividend_yield":  round((info.get("dividendYield") or 0) * 100, 2),
            "analyst_rating":  info.get("recommendationKey", "").upper(),
            "target_price":    info.get("targetMeanPrice"),
            "sector":          info.get("sector", ""),
            "industry":        info.get("industry", ""),
            "currency":        info.get("currency", "INR"),
            "exchange":        info.get("exchange", ""),
            "beta":            info.get("beta"),
        }
    except Exception as e:
        return None

def get_historical_data(ticker, period="5y", interval="1wk"):
    """Get historical price data for charting"""
    try:
        t = yf.Ticker(ticker)
        df = t.history(period=period, interval=interval)
        if df.empty:
            return None
        df.index = pd.to_datetime(df.index)
        return df[["Open", "High", "Low", "Close", "Volume"]].dropna()
    except:
        return None

def get_intraday_data(ticker):
    """Get intraday data (1-minute, last 1 day)"""
    try:
        t = yf.Ticker(ticker)
        df = t.history(period="1d", interval="5m")
        if df.empty:
            return None
        df.index = pd.to_datetime(df.index)
        return df[["Open", "High", "Low", "Close", "Volume"]].dropna()
    except:
        return None

def calculate_technicals(df):
    """Calculate RSI and Moving Averages from price data"""
    if df is None or len(df) < 20:
        return {}
    close = df["Close"]
    # RSI
    delta = close.diff()
    gain  = delta.clip(lower=0).rolling(14).mean()
    loss  = (-delta.clip(upper=0)).rolling(14).mean()
    rs    = gain / loss
    rsi   = round(float(100 - (100 / (1 + rs.iloc[-1]))), 1)
    # Moving averages (use weekly data approximations)
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
    """Top NIFTY 50 tickers for auto scan"""
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
    """Top S&P 100 tickers for US auto scan"""
    return [
        "AAPL","MSFT","GOOGL","AMZN","NVDA","META","TSLA","BRK-B","UNH","JNJ",
        "JPM","V","PG","XOM","MA","HD","CVX","MRK","ABBV","PFE",
        "AVGO","COST","LLY","BAC","KO","DIS","CSCO","TMO","WMT","PEP",
        "ACN","DHR","ABT","MCD","NKE","ADBE","CRM","TXN","LIN","CMCSA",
        "VZ","NFLX","PM","INTC","UPS","RTX","HON","AMD","QCOM","AMGN",
    ]

def get_ftse100_tickers():
    """Top FTSE 100 tickers for UK auto scan"""
    return [
        "SHEL.L","AZN.L","HSBA.L","ULVR.L","BP.L","RIO.L","GSK.L","DGE.L",
        "BATS.L","LSEG.L","NG.L","NWG.L","LLOY.L","BARC.L","VOD.L","AAL.L",
        "REL.L","EXPN.L","STAN.L","PRU.L","WPP.L","IAG.L","SBRY.L","TSCO.L",
    ]

