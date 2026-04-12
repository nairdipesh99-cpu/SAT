import json
import os
from datetime import datetime
import pytz

PORTFOLIO_FILE = "portfolio.json"

def load_portfolio():
    if os.path.exists(PORTFOLIO_FILE):
        try:
            with open(PORTFOLIO_FILE, "r") as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_portfolio(portfolio):
    with open(PORTFOLIO_FILE, "w") as f:
        json.dump(portfolio, f, indent=2)

def add_to_portfolio(ticker, name, shares, buy_price, market):
    portfolio = load_portfolio()
    portfolio[ticker] = {
        "name": name, "shares": shares, "buy_price": buy_price,
        "market": market, "added": datetime.now().strftime("%Y-%m-%d")
    }
    save_portfolio(portfolio)

def remove_from_portfolio(ticker):
    portfolio = load_portfolio()
    if ticker in portfolio:
        del portfolio[ticker]
        save_portfolio(portfolio)

def get_market_status():
    now_ist = datetime.now(pytz.timezone("Asia/Kolkata"))
    now_est = datetime.now(pytz.timezone("US/Eastern"))
    now_gmt = datetime.now(pytz.timezone("Europe/London"))
    wd = now_ist.weekday()
    return {
        "india": wd < 5 and (9 < now_ist.hour < 15 or (now_ist.hour == 9 and now_ist.minute >= 15) or (now_ist.hour == 15 and now_ist.minute <= 30)),
        "us":    wd < 5 and (9 < now_est.hour < 16 or (now_est.hour == 9 and now_est.minute >= 30)),
        "uk":    wd < 5 and 8 <= now_gmt.hour < 16,
        "time_ist": now_ist.strftime("%H:%M IST"),
        "time_est": now_est.strftime("%H:%M EST"),
        "time_gmt": now_gmt.strftime("%H:%M GMT"),
    }

def format_currency(value, currency="₹"):
    if value is None: return "N/A"
    if abs(value) >= 1e7:  return f"{currency}{value/1e7:.2f}Cr"
    if abs(value) >= 1e5:  return f"{currency}{value/1e5:.2f}L"
    if abs(value) >= 1000: return f"{currency}{value:,.0f}"
    return f"{currency}{value:.2f}"

def format_number(value):
    if value is None: return "N/A"
    if abs(value) >= 1e9: return f"{value/1e9:.2f}B"
    if abs(value) >= 1e6: return f"{value/1e6:.2f}M"
    if abs(value) >= 1e3: return f"{value/1e3:.1f}K"
    return f"{value:.2f}"

def get_change_color(value):
    if value is None: return "#6B7280"
    return "#10B981" if value >= 0 else "#EF4444"

def get_change_arrow(value):
    if value is None: return ""
    return "▲" if value >= 0 else "▼"

def decision_to_color(decision):
    return {
        "STRONG BUY": "#10B981", "BUY": "#34D399",
        "BUY ON DIP": "#60A5FA", "HOLD": "#F59E0B",
        "CAUTION": "#FB923C",   "AVOID": "#EF4444",
    }.get(decision, "#F59E0B")

def decision_to_bg(decision):
    return {
        "STRONG BUY": "#064E3B", "BUY": "#052E16",
        "BUY ON DIP": "#1E3A5F", "HOLD": "#451A03",
        "CAUTION": "#431407",   "AVOID": "#450A0A",
    }.get(decision, "#451A03")

def gc_to_emoji(gc_status):
    return {"GREEN": "🟢", "AMBER": "🟡", "RED": "🔴", "WINNER": "⭐"}.get(gc_status, "🟡")

def calculate_score(metrics):
    score, total = 0, 0
    rg = metrics.get("revenue_growth")
    if rg is not None:
        score += 20 if rg > 15 else 15 if rg > 8 else 10 if rg > 0 else 3; total += 20
    pm = metrics.get("profit_margin")
    if pm is not None:
        score += 20 if pm > 15 else 15 if pm > 8 else 10 if pm > 0 else 3; total += 20
    de = metrics.get("debt_to_equity")
    if de is not None:
        score += 20 if de < 0.5 else 15 if de < 1 else 10 if de < 2 else 3; total += 20
    rsi = metrics.get("rsi")
    if rsi is not None:
        score += 20 if 40 < rsi < 60 else 15 if (30 < rsi <= 40 or 60 <= rsi < 70) else 8; total += 20
    pe = metrics.get("pe_ratio")
    if pe is not None:
        score += 20 if 0 < pe < 15 else 15 if pe < 25 else 10 if pe < 40 else 5; total += 20
    return round((score / total) * 100) if total else 50

def score_to_decision(score, gc_status="GREEN"):
    penalty = {"GREEN": 0, "AMBER": 1, "RED": 2, "WINNER": -1}.get(gc_status, 0)
    decisions = ["STRONG BUY", "BUY", "BUY ON DIP", "HOLD", "CAUTION", "AVOID"]
    idx = 0 if score >= 85 else 1 if score >= 70 else 2 if score >= 55 else 3 if score >= 40 else 4 if score >= 25 else 5
    return decisions[min(5, idx + penalty)]

