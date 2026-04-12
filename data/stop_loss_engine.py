
import numpy as np
import pandas as pd
from data.yahoo_fetcher import get_historical_data, get_stock_info, calculate_technicals
from data.news_fetcher import calculate_gc_status, get_gc_news
import json

def calculate_atr(df, period=14):
    """Average True Range — how much stock moves daily"""
    if df is None or len(df) < period:
        return None
    high  = df["High"]
    low   = df["Low"]
    close = df["Close"]
    tr = pd.concat([
        high - low,
        (high - close.shift()).abs(),
        (low  - close.shift()).abs()
    ], axis=1).max(axis=1)
    return float(tr.rolling(period).mean().iloc[-1])

def find_support_levels(df, lookback=52):
    """Find key price support levels from historical data"""
    if df is None or len(df) < 10:
        return []
    close  = df["Close"].tail(lookback)
    lows   = df["Low"].tail(lookback)
    levels = []
    # Find local minima (price bounced from these levels)
    for i in range(2, len(lows) - 2):
        if lows.iloc[i] < lows.iloc[i-1] and lows.iloc[i] < lows.iloc[i+1] and \
           lows.iloc[i] < lows.iloc[i-2] and lows.iloc[i] < lows.iloc[i+2]:
            levels.append(float(lows.iloc[i]))
    # Cluster nearby levels
    if not levels:
        return [float(lows.min()), float(lows.quantile(0.25))]
    levels.sort()
    clustered = []
    cluster   = [levels[0]]
    for l in levels[1:]:
        if l - cluster[-1] < cluster[-1] * 0.03:  # within 3%
            cluster.append(l)
        else:
            clustered.append(np.mean(cluster))
            cluster = [l]
    clustered.append(np.mean(cluster))
    return sorted(clustered, reverse=True)[:5]

def get_vix_level():
    """Get current VIX or India VIX as market fear gauge"""
    try:
        import yfinance as yf
        vix = yf.Ticker("^VIX")
        info = vix.info
        v = info.get("regularMarketPrice") or info.get("previousClose")
        if v:
            return float(v), "HIGH" if v > 25 else "MODERATE" if v > 15 else "LOW"
    except:
        pass
    return 18.0, "MODERATE"

def get_market_trend():
    """Get broad market trend"""
    try:
        import yfinance as yf
        nifty = yf.Ticker("^NSEI")
        df    = nifty.history(period="3mo", interval="1wk")
        if not df.empty:
            start = float(df["Close"].iloc[0])
            end   = float(df["Close"].iloc[-1])
            pct   = (end - start) / start * 100
            return "BULLISH" if pct > 3 else "BEARISH" if pct < -3 else "SIDEWAYS"
    except:
        pass
    return "SIDEWAYS"

def get_earnings_days(ticker):
    """Check if earnings are coming up soon"""
    try:
        import yfinance as yf
        t    = yf.Ticker(ticker)
        cal  = t.calendar
        if cal is not None and not cal.empty:
            from datetime import datetime
            ed = cal.iloc[0, 0] if hasattr(cal, 'iloc') else None
            if ed:
                days = (pd.Timestamp(ed) - pd.Timestamp.now()).days
                if 0 <= days <= 30:
                    return days
    except:
        pass
    return None

def calculate_ai_stop_loss(ticker, buy_price, shares, risk_preference="MODERATE"):
    """
    Full AI-powered stop loss calculation.
    Returns a dict with all 3 levels + reasoning.
    """
    # ── Fetch all data ──
    hist  = get_historical_data(ticker, period="2y", interval="1d")
    info  = get_stock_info(ticker)
    tech  = calculate_technicals(get_historical_data(ticker, period="1y")) if hist is not None else {}
    gc_status, gc_reason = calculate_gc_status(ticker, info.get("sector","") if info else "")

    current_price = (info.get("price") if info else None) or buy_price
    atr           = calculate_atr(hist)
    supports      = find_support_levels(hist)
    vix_val, vix_level = get_vix_level()
    mkt_trend     = get_market_trend()
    earnings_days = get_earnings_days(ticker)
    rsi           = tech.get("rsi", 50) or 50
    beta          = (info.get("beta") if info else None) or 1.0
    pnl_pct       = (current_price - buy_price) / buy_price * 100

    # ── ATR multiplier based on risk preference ──
    atr_mult = {"CONSERVATIVE": 1.2, "MODERATE": 1.8, "AGGRESSIVE": 2.5}.get(risk_preference, 1.8)

    # ── Market condition adjustments ──
    mkt_adj = 1.0
    if vix_level  == "HIGH":     mkt_adj *= 1.4
    if mkt_trend  == "BEARISH":  mkt_adj *= 1.2
    if gc_status  == "RED":      mkt_adj *= 1.2
    if gc_status  == "WINNER":   mkt_adj *= 0.9
    if beta and beta > 1.5:      mkt_adj *= 1.2
    if earnings_days and earnings_days <= 14: mkt_adj *= 1.3

    # ── Calculate base stop distance ──
    atr_buffer = (atr or current_price * 0.02) * atr_mult * mkt_adj

    # ── Find best support level for hard stop ──
    hard_stop = current_price - atr_buffer
    if supports:
        # Find nearest support below current price
        below = [s for s in supports if s < current_price - atr_buffer * 0.3]
        if below:
            nearest = max(below)
            # Place stop just below support
            hard_stop = nearest - (atr or current_price * 0.01) * 0.5

    # ── 3 levels ──
    warning_level = current_price - atr_buffer * 0.4
    reduce_level  = current_price - atr_buffer * 0.7
    hard_stop     = min(hard_stop, current_price - atr_buffer)

    # Never let stop be above buy price if in loss
    if pnl_pct < 0:
        hard_stop = min(hard_stop, buy_price * 0.92)

    # Trailing: if in profit, raise floor
    trailing_floor = None
    if pnl_pct > 8:
        trailing_floor = buy_price + (current_price - buy_price) * 0.3
        hard_stop  = max(hard_stop, trailing_floor)
        reduce_level  = max(reduce_level,  buy_price)
        warning_level = max(warning_level, buy_price * 1.02)

    # ── Max loss calculations ──
    max_loss_per_share = buy_price - hard_stop
    max_loss_total     = max_loss_per_share * shares
    loss_pct           = (max_loss_per_share / buy_price) * 100

    # ── Entry quality ──
    if   rsi < 40:   entry_quality = "EXCELLENT"
    elif rsi < 55:   entry_quality = "GOOD"
    elif rsi < 65:   entry_quality = "AVERAGE"
    else:            entry_quality = "RISKY"

    # ── Risk/Reward ──
    target = info.get("target_price") if info else None
    if target and target > current_price:
        potential_gain = target - current_price
        rr_ratio       = round(potential_gain / max_loss_per_share, 2) if max_loss_per_share > 0 else 0
    else:
        rr_ratio = None

    # ── Build reasoning ──
    reasons = []
    if supports:
        reasons.append(f"Key support identified at {round(max(s for s in supports if s < current_price), 2) if any(s < current_price for s in supports) else 'N/A'} from price history")
    if atr:
        reasons.append(f"ATR buffer of {round(atr, 2)} × {atr_mult} applied for {risk_preference.lower()} risk profile")
    if vix_level != "LOW":
        reasons.append(f"VIX at {round(vix_val, 1)} ({vix_level}) — stop widened for market volatility")
    if mkt_trend == "BEARISH":
        reasons.append("Bearish market trend — wider stop to handle deeper dips")
    if gc_status == "RED":
        reasons.append(f"GC Status RED — global risks require wider protection")
    if earnings_days and earnings_days <= 14:
        reasons.append(f"Earnings in {earnings_days} days — stop widened to avoid earnings volatility trigger")
    if trailing_floor:
        reasons.append(f"Trailing stop active — floor raised to protect {round(pnl_pct, 1)}% gain")
    if beta and beta > 1.2:
        reasons.append(f"High beta ({round(beta, 2)}) stock — naturally wider stop needed")

    curr_sym = "₹" if ".NS" in ticker or ".BO" in ticker else ("£" if ".L" in ticker else "$")

    return {
        "ticker":           ticker,
        "buy_price":        round(buy_price, 2),
        "current_price":    round(current_price, 2),
        "shares":           shares,
        "pnl_pct":          round(pnl_pct, 2),
        "warning_level":    round(warning_level, 2),
        "reduce_level":     round(reduce_level, 2),
        "hard_stop":        round(hard_stop, 2),
        "max_loss_per_share": round(max_loss_per_share, 2),
        "max_loss_total":   round(max_loss_total, 2),
        "loss_pct":         round(loss_pct, 2),
        "atr":              round(atr, 2) if atr else None,
        "vix":              round(vix_val, 1),
        "vix_level":        vix_level,
        "market_trend":     mkt_trend,
        "gc_status":        gc_status,
        "gc_reason":        gc_reason,
        "earnings_days":    earnings_days,
        "entry_quality":    entry_quality,
        "rsi_at_check":     round(rsi, 1),
        "beta":             round(beta, 2) if beta else None,
        "trailing_floor":   round(trailing_floor, 2) if trailing_floor else None,
        "support_levels":   [round(s, 2) for s in supports[:4]] if supports else [],
        "rr_ratio":         rr_ratio,
        "reasons":          reasons,
        "risk_preference":  risk_preference,
        "currency":         curr_sym,
    }

def check_alert_status(stop_loss_data):
    """Check current price against stop loss levels"""
    cp  = stop_loss_data["current_price"]
    w   = stop_loss_data["warning_level"]
    r   = stop_loss_data["reduce_level"]
    h   = stop_loss_data["hard_stop"]
    pnl = stop_loss_data["pnl_pct"]

    if   cp <= h: return "HARD_STOP",  "🔴", "EXIT NOW — Hard stop triggered"
    elif cp <= r: return "REDUCE",      "🟠", "REDUCE POSITION — Sell 50%"
    elif cp <= w: return "WARNING",     "🟡", "WARNING — Monitor closely"
    elif pnl < -15: return "DEEP_LOSS", "🔴", "DEEP LOSS — Reassess position"
    else:           return "SAFE",      "🟢", "Position healthy"

def get_ai_stop_loss_explanation(stop_data, analysis_reversed=False):
    """Get Claude AI explanation for stop loss recommendation"""
    try:
        from data.ai_analyst import get_api_key
        import anthropic
        api_key = get_api_key()
        if not api_key:
            return get_fallback_explanation(stop_data, analysis_reversed)
        client = anthropic.Anthropic(api_key=api_key)
        curr = stop_data["currency"]
        prompt = f"""You are a risk management expert. Explain this stop loss recommendation in simple, clear language for a retail investor.

STOCK: {stop_data['ticker']}
Buy Price: {curr}{stop_data['buy_price']}
Current Price: {curr}{stop_data['current_price']} ({stop_data['pnl_pct']:+.1f}%)
Shares: {stop_data['shares']}

STOP LOSS LEVELS:
Warning Level: {curr}{stop_data['warning_level']}
Reduce Level: {curr}{stop_data['reduce_level']} (sell 50% here)
Hard Stop: {curr}{stop_data['hard_stop']} (exit all here)
Max Loss if Hard Stop Hit: {curr}{stop_data['max_loss_total']:.0f}

MARKET CONDITIONS:
VIX: {stop_data['vix']} ({stop_data['vix_level']})
Market Trend: {stop_data['market_trend']}
GC Status: {stop_data['gc_status']}
Earnings in: {stop_data['earnings_days']} days if applicable
Entry Quality: {stop_data['entry_quality']}
Risk/Reward Ratio: {stop_data['rr_ratio']}

Analysis Reversed Today: {analysis_reversed}

Write a clear 3-4 sentence explanation in simple English covering:
1. Why these specific levels were chosen
2. What the investor should do if each level is hit
3. One key thing to watch for
4. Whether current position looks safe or concerning

Keep it conversational — like a trusted advisor talking to a friend."""

        resp = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=400,
            messages=[{"role": "user", "content": prompt}]
        )
        return resp.content[0].text.strip()
    except:
        return get_fallback_explanation(stop_data, analysis_reversed)

def get_fallback_explanation(stop_data, analysis_reversed=False):
    curr  = stop_data["currency"]
    pnl   = stop_data["pnl_pct"]
    trend = stop_data["market_trend"]
    vix   = stop_data["vix_level"]
    base  = f"Stop loss levels are set based on the stock's average daily movement (ATR: {curr}{stop_data['atr'] or 'N/A'}) and key support levels from price history. "
    if pnl > 5:
        base += f"Your position is currently profitable at +{pnl:.1f}% — the stop loss has been trailed up to protect your gains. "
    elif pnl < -5:
        base += f"Your position is currently at {pnl:.1f}% — monitor closely and be ready to act if reduce level is hit. "
    if vix == "HIGH":
        base += "Market volatility is elevated — stops are wider than normal to avoid being triggered by noise. "
    if analysis_reversed:
        base += "⚠️ Today's analysis has reversed from your original buy signal — consider reviewing your position carefully."
    return base

