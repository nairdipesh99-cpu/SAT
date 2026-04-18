# 🇮🇳 India Market Intelligence Dashboard

**Institutional-grade stock intelligence platform** for NSE/BSE listed equities.
Built with Streamlit · FinBERT · Plotly · jugaad-data · FMP · Tavily AI.

---

## Features

| Module | Description |
|---|---|
| **Col 1 — Govt & Macro** | PLI schemes, RBI/policy impacts, sector subsidies, India VIX regime |
| **Col 2 — Sector Pulse** | Stock vs. Nifty sector index comparison, candlestick + MACD + RSI |
| **Col 3 — Project Catalysts** | AI-researched contract wins, FinBERT news sentiment feed |
| **Col 4 — 5-Year Deep Dive** | Master Score, D/E · ROE · NPM trends, Price CAGR analysis |
| **Market Regime** | India VIX > 22 → Defensive Mode banner; FMCG/Pharma prioritised |
| **Master Score** | 0–100 composite (Technicals 35% + Fundamentals 35% + Sentiment 30%) |

---

## Quick Start

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

> **Note:** `torch` + `transformers` can be large (~2 GB). For faster startup,
> the dashboard includes a lightweight keyword-based fallback if FinBERT
> cannot be loaded.

### 2. Run the dashboard
```bash
streamlit run app.py
```

The app opens at `http://localhost:8501`.

---

## API Keys (All Optional — Graceful Fallbacks Included)

All API keys are entered in the sidebar under **🔑 API Keys**. The app always
runs with synthetic/demo data when keys are absent.

### Financial Modeling Prep (FMP) — Fundamentals
- **Data:** 5-year D/E Ratio, ROE, Net Profit Margin
- **Free tier:** 250 requests/day
- **Get key:** https://financialmodelingprep.com/developer/docs
- **Env var:** `FMP_API_KEY`

### Finnhub — News Feed
- **Data:** Company news articles (7-day window)
- **Free tier:** 60 calls/minute
- **Get key:** https://finnhub.io/register
- **Env var:** `FINNHUB_API_KEY`

### Tavily AI — Deep Research
- **Data:** Contract wins, project announcements, policy news
- **Free tier:** 1,000 searches/month
- **Get key:** https://app.tavily.com
- **Env var:** `TAVILY_API_KEY`

You can also set keys as environment variables and the app will detect them:
```bash
export FMP_API_KEY="your_key_here"
export FINNHUB_API_KEY="your_key_here"
export TAVILY_API_KEY="tvly-your_key_here"
streamlit run app.py
```

---

## NSE Data Sources

The app attempts to fetch live price history in this order:

1. **jugaad-data** (`jugaad_data.nse.stock_df`) — primary source
2. **nselib** (`nselib.capital_market`) — fallback
3. **Synthetic OHLCV** — realistic simulation if both fail

> NSE data sources occasionally require a stable Indian IP or VPN.
> The synthetic fallback provides realistic chart demonstrations.

---

## Supported Stocks (30 included)

```
RELIANCE, TCS, INFY, HDFCBANK, ICICIBANK, SBIN, WIPRO, HCLTECH,
BAJFINANCE, KOTAKBANK, HINDUNILVR, ITC, SUNPHARMA, DRREDDY,
MARUTI, TATAMOTORS, ADANIENT, LT, NTPC, POWERGRID, ONGC,
COALINDIA, TATASTEEL, JSWSTEEL, NESTLEIND, BAJAJ-AUTO, TECHM,
CIPLA, DIVISLAB, ULTRACEMCO
```

To add more stocks, extend `NSE_SECTOR_MAP` in `app.py`.

---

## Master Score Methodology

```
Master Score (0–100)
├── Technical Score   (0–35 pts)
│   ├── RSI position          (12 pts)
│   ├── MACD crossover        ( 8 pts)
│   ├── ADX trend strength    (10 pts)
│   └── Volume confirmation   ( 5 pts)
│
├── Fundamental Score (0–35 pts)
│   ├── Debt/Equity ratio     (12 pts)
│   ├── ROE (5-year avg)      (15 pts)
│   └── Net Profit Margin     ( 8 pts)
│
├── Sentiment Score   (0–30 pts)
│   └── FinBERT positive/negative news ratio
│
└── VIX Penalty
    └── −0.6 pts per VIX point above 15
```

| Score Range | Verdict | Horizon |
|---|---|---|
| 70–100 | 🟢 Strong Buy | Long-term (12–18M) |
| 55–69  | 🔵 Accumulate | Medium-term (6–12M) |
| 40–54  | 🟡 Hold / Neutral | Monitor Closely |
| 25–39  | 🟠 Reduce | Short-term Caution |
| 0–24   | 🔴 Avoid / Exit | Defensive / Cash |

---

## Market Regime Logic

```
India VIX > 22  →  🛡 DEFENSIVE MODE
                    Prioritise: FMCG, Pharma, IT (export), PSU Bonds
                    Reduce: High-beta Auto, Metals, Cyclicals

India VIX ≤ 22  →  ✅ NORMAL REGIME
                    Broad market participation; follow stock-specific signals
```

---

## Disclaimer

> This dashboard is for **institutional research and educational purposes only**.
> It does **not** constitute investment advice. Always conduct your own due
> diligence and consult a SEBI-registered investment advisor before trading.

