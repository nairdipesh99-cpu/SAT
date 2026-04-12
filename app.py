
import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

st.set_page_config(
    page_title="StockSense — AI Investment Intelligence",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed",
)

from utils.styles  import MAIN_CSS
from utils.helpers import get_market_status, gc_to_emoji, decision_to_color, score_to_decision, calculate_score
from data.yahoo_fetcher import get_stock_info, get_nifty50_tickers, get_sp100_tickers, get_ftse100_tickers, search_ticker, get_historical_data, calculate_technicals
from data.news_fetcher  import calculate_gc_status, get_gc_news
from components.portfolio_panel import render_portfolio
from components.stock_card import render_stock_row, render_full_analysis
from components.alerts_tab import render_alerts_tab

st.markdown(MAIN_CSS, unsafe_allow_html=True)

# ── Session State ──
if "watchlist_india" not in st.session_state: st.session_state.watchlist_india = []
if "watchlist_us"    not in st.session_state: st.session_state.watchlist_us    = []
if "watchlist_uk"    not in st.session_state: st.session_state.watchlist_uk    = []
if "selected_stock"  not in st.session_state: st.session_state.selected_stock  = None
if "selected_market" not in st.session_state: st.session_state.selected_market = "india"
if "api_key_set"     not in st.session_state: st.session_state.api_key_set     = False

# ── Header ──
market_status = get_market_status()
india_dot = "🟢" if market_status["india"] else "🔴"
us_dot    = "🟢" if market_status["us"]    else "🔴"
uk_dot    = "🟢" if market_status["uk"]    else "🔴"

st.markdown(f"""
<div class="app-header">
    <div style="display:flex;align-items:center;gap:1rem;">
        <div class="app-logo">Stock<span>Sense</span></div>
        <div style="font-size:0.72rem;color:#4B5563;">AI Investment Intelligence</div>
    </div>
    <div style="display:flex;gap:1.5rem;align-items:center;">
        <div class="market-time">{india_dot} NSE {market_status['time_ist']}</div>
        <div class="market-time">{us_dot} NYSE {market_status['time_est']}</div>
        <div class="market-time">{uk_dot} LSE {market_status['time_gmt']}</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Main Tabs ──
tab_india, tab_us, tab_uk, tab_gc, tab_alerts, tab_settings = st.tabs([
    "🇮🇳  Indian Stocks",
    "🇺🇸  US Stocks",
    "🇬🇧  UK Stocks",
    "🌍  GC Monitor",
    "🛡️  Position Alerts",
    "⚙️  Settings",
])

def render_market_tab(market, watchlist_key, tickers_fn, currency, index_tickers):
    watchlist = st.session_state[watchlist_key]

    # ── If a stock is selected show full analysis ──
    if st.session_state.selected_stock and st.session_state.selected_market == market:
        if st.button("← Back to Market", key=f"back_{market}"):
            st.session_state.selected_stock = None
            st.rerun()
        render_full_analysis(st.session_state.selected_stock, market)
        return

    main_col, port_col = st.columns([7, 3])

    with main_col:
        # ── Market Indices ──
        st.markdown('<div class="section-header">MARKET OVERVIEW</div>', unsafe_allow_html=True)
        idx_cols = st.columns(len(index_tickers))
        for i, (idx_ticker, idx_name) in enumerate(index_tickers):
            with idx_cols[i]:
                info = get_stock_info(idx_ticker)
                if info and info.get("price"):
                    p   = info["price"]
                    chg = info.get("change_pct", 0) or 0
                    clr = "#10B981" if chg >= 0 else "#EF4444"
                    arr = "▲" if chg >= 0 else "▼"
                    st.markdown(f"""
                    <div class="index-pill">
                        <div class="index-name">{idx_name}</div>
                        <div class="index-value">{currency}{p:,.0f}</div>
                        <div style="font-size:0.72rem;color:{clr};font-weight:500;">{arr} {abs(chg):.2f}%</div>
                    </div>""", unsafe_allow_html=True)

        # ── GC Winners Banner ──
        st.markdown('<div style="margin-top:1rem;"></div>', unsafe_allow_html=True)

        # ── Search & Add ──
        st.markdown('<div class="section-header">ADD STOCKS TO WATCHLIST</div>', unsafe_allow_html=True)
        s1, s2 = st.columns([4, 1])
        with s1:
            query = st.text_input("", placeholder="Type company name or ticker (e.g. Tata Steel or TATASTEEL.NS)", key=f"search_{market}", label_visibility="collapsed")
        with s2:
            if st.button("Add Stock", type="primary", key=f"add_btn_{market}"):
                if query:
                    with st.spinner("Searching..."):
                        found = search_ticker(query)
                    if found and found not in watchlist:
                        st.session_state[watchlist_key].append(found)
                        st.success(f"✓ {found} added")
                        st.rerun()
                    elif found in watchlist:
                        st.warning("Already in watchlist")
                    else:
                        st.error("Stock not found. Try the exact ticker symbol.")

        # ── Quick Add Popular ──
        if not watchlist:
            st.markdown('<div style="font-size:0.72rem;color:#6B7280;margin-bottom:0.5rem;">Quick add popular stocks:</div>', unsafe_allow_html=True)
            popular = tickers_fn()[:8]
            p_cols  = st.columns(4)
            for i, t in enumerate(popular):
                with p_cols[i % 4]:
                    label = t.replace(".NS","").replace(".BO","").replace(".L","")
                    if st.button(label, key=f"quick_{t}_{market}"):
                        if t not in st.session_state[watchlist_key]:
                            st.session_state[watchlist_key].append(t)
                            st.rerun()

        # ── Watchlist ──
        if watchlist:
            st.markdown('<div class="section-header">YOUR WATCHLIST</div>', unsafe_allow_html=True)
            gc_winners = []
            for ticker in watchlist:
                info = get_stock_info(ticker)
                if not info:
                    st.markdown(f'<div style="font-size:0.8rem;color:#6B7280;padding:0.5rem;">⚠ Could not load {ticker}</div>', unsafe_allow_html=True)
                    continue
                hist     = get_historical_data(ticker, period="1y")
                tech     = calculate_technicals(hist) if hist is not None else {}
                gc_st, _ = calculate_gc_status(ticker, info.get("sector",""))
                metrics  = {
                    "revenue_growth": info.get("revenue_growth"),
                    "profit_margin":  info.get("profit_margin"),
                    "debt_to_equity": info.get("debt_to_equity"),
                    "rsi":            tech.get("rsi"),
                    "pe_ratio":       info.get("pe_ratio"),
                }
                score    = calculate_score(metrics)
                short_v  = score_to_decision(score, gc_st)
                long_v   = score_to_decision(min(score + 8, 100), "GREEN")
                if gc_st == "WINNER":
                    gc_winners.append(info.get("name",""))
                c1, c2 = st.columns([9, 1])
                with c1:
                    render_stock_row(info, gc_st, short_v, long_v, ticker)
                with c2:
                    if st.button("View", key=f"view_{ticker}_{market}"):
                        st.session_state.selected_stock  = ticker
                        st.session_state.selected_market = market
                        st.rerun()
                    if st.button("✕", key=f"del_{ticker}_{market}"):
                        st.session_state[watchlist_key].remove(ticker)
                        st.rerun()
            # GC Winners banner
            if gc_winners:
                st.markdown(f"""
                <div class="gc-winners-banner">
                    <div class="gc-winners-title">⭐ GC WINNERS — RISING DUE TO GLOBAL EVENTS</div>
                    <div style="font-size:0.82rem;color:#FCD34D;">{' · '.join(gc_winners)}</div>
                </div>""", unsafe_allow_html=True)

        # ── Top Auto Picks ──
        st.markdown('<div class="section-header">TODAY\'S TOP AUTO PICKS — FROM MARKET SCAN</div>', unsafe_allow_html=True)
        with st.spinner("Scanning market for top picks..."):
            scan_tickers = tickers_fn()[:20]
            scored = []
            for t in scan_tickers:
                if t in watchlist: continue
                info = get_stock_info(t)
                if not info: continue
                hist = get_historical_data(t, period="6mo")
                tech = calculate_technicals(hist) if hist is not None else {}
                gc_s, _ = calculate_gc_status(t, info.get("sector",""))
                metrics = {
                    "revenue_growth": info.get("revenue_growth"),
                    "profit_margin":  info.get("profit_margin"),
                    "debt_to_equity": info.get("debt_to_equity"),
                    "rsi":            tech.get("rsi"),
                    "pe_ratio":       info.get("pe_ratio"),
                }
                score   = calculate_score(metrics)
                short_v = score_to_decision(score, gc_s)
                long_v  = score_to_decision(min(score + 8, 100), "GREEN")
                scored.append((score, t, info, gc_s, short_v, long_v))
            scored.sort(reverse=True, key=lambda x: x[0])
            top_picks = scored[:5]
        if top_picks:
            for score, ticker, info, gc_s, sv, lv in top_picks:
                c1, c2 = st.columns([9, 1])
                with c1:
                    render_stock_row(info, gc_s, sv, lv, f"auto_{ticker}")
                with c2:
                    if st.button("View", key=f"view_auto_{ticker}_{market}"):
                        st.session_state.selected_stock  = ticker
                        st.session_state.selected_market = market
                        st.rerun()

    with port_col:
        st.markdown('<div class="portfolio-card">', unsafe_allow_html=True)
        render_portfolio(market_filter=market)
        st.markdown('</div>', unsafe_allow_html=True)

# ── Indian Tab ──
with tab_india:
    render_market_tab(
        market="india",
        watchlist_key="watchlist_india",
        tickers_fn=get_nifty50_tickers,
        currency="₹",
        index_tickers=[
            ("^NSEI",  "NIFTY 50"),
            ("^BSESN", "SENSEX"),
            ("^CNXMETAL","NIFTY METAL"),
            ("^CNXPHARMA","NIFTY PHARMA"),
        ]
    )

# ── US Tab ──
with tab_us:
    render_market_tab(
        market="us",
        watchlist_key="watchlist_us",
        tickers_fn=get_sp100_tickers,
        currency="$",
        index_tickers=[
            ("^GSPC", "S&P 500"),
            ("^DJI",  "DOW JONES"),
            ("^IXIC", "NASDAQ"),
            ("^VIX",  "VIX"),
        ]
    )

# ── UK Tab ──
with tab_uk:
    render_market_tab(
        market="uk",
        watchlist_key="watchlist_uk",
        tickers_fn=get_ftse100_tickers,
        currency="£",
        index_tickers=[
            ("^FTSE",  "FTSE 100"),
            ("^FTMC",  "FTSE 250"),
            ("GBPUSD=X","GBP/USD"),
        ]
    )

# ── GC Monitor Tab ──
with tab_gc:
    st.markdown('<div class="section-header">🌍 GLOBAL CRISIS MONITOR</div>', unsafe_allow_html=True)
    st.markdown("""
    <div style="font-size:0.8rem;color:#6B7280;margin-bottom:1rem;">
        Monitoring geopolitical events, commodity prices, interest rates and macroeconomic conditions.
        The GC dot on each stock reflects how global events specifically impact that company.
    </div>""", unsafe_allow_html=True)

    categories = [
        ("Geopolitical Risk",   "🔴", "↑", "Ongoing conflicts affecting global supply chains and energy prices"),
        ("Recession Risk",      "🟡", "→", "Mixed signals — GDP growth slowing in major economies"),
        ("Interest Rate Risk",  "🟡", "↓", "Central banks signalling pause in rate hikes"),
        ("Commodity Prices",    "🔴", "↑", "Oil and coal prices elevated — pressure on manufacturers"),
        ("Policy & Regulation", "🟢", "→", "No major regulatory changes expected near term"),
        ("Currency Risk",       "🟡", "→", "INR stable vs USD, slight GBP weakness"),
    ]
    for cat, status, trend, desc in categories:
        t_color = "#EF4444" if trend == "↑" else "#10B981" if trend == "↓" else "#6B7280"
        st.markdown(f"""
        <div class="gc-category-row">
            <div>
                <div style="font-size:0.85rem;color:#D1D5DB;font-weight:500;">{cat}</div>
                <div style="font-size:0.72rem;color:#6B7280;margin-top:2px;">{desc}</div>
            </div>
            <div style="display:flex;align-items:center;gap:0.75rem;">
                <span style="font-size:1rem;">{status}</span>
                <span style="font-size:0.85rem;color:{t_color};font-weight:600;">{trend} {"Worsening" if trend=="↑" else "Improving" if trend=="↓" else "Stable"}</span>
            </div>
        </div>""", unsafe_allow_html=True)

    st.markdown('<div class="section-header" style="margin-top:1.5rem;">LATEST MACRO NEWS</div>', unsafe_allow_html=True)
    with st.spinner("Fetching global news..."):
        gc_news = get_gc_news()
    if gc_news:
        for item in gc_news[:8]:
            imp_color = "#EF4444" if item["impact"] == "NEGATIVE" else "#10B981" if item["impact"] == "POSITIVE" else "#6B7280"
            st.markdown(f"""
            <div style="border-left:3px solid {imp_color};padding:0.4rem 0.75rem;margin-bottom:0.4rem;background:#111827;border-radius:0 8px 8px 0;">
                <div style="font-size:0.65rem;font-weight:600;color:{imp_color};text-transform:uppercase;">{item['impact']} · {item.get('source','')}</div>
                <div style="font-size:0.8rem;color:#D1D5DB;margin-top:2px;">{item['title']}</div>
                <div style="font-size:0.68rem;color:#4B5563;margin-top:2px;">{item.get('time','')}</div>
            </div>""", unsafe_allow_html=True)
    else:
        st.info("Could not fetch global news. Check your internet connection.")

# ── Alerts Tab ──
with tab_alerts:
    render_alerts_tab()

# ── Settings Tab ──
with tab_settings:
    st.markdown('<div class="section-header">⚙️ SETTINGS</div>', unsafe_allow_html=True)
    st.markdown("""
    <div style="background:#111827;border:1px solid #1F2937;border-radius:12px;padding:1.25rem;margin-bottom:1rem;">
        <div style="font-size:0.85rem;font-weight:600;color:#F9FAFB;margin-bottom:0.5rem;">🔑 Anthropic API Key</div>
        <div style="font-size:0.78rem;color:#6B7280;margin-bottom:0.75rem;">
            Add your API key to unlock full AI-powered analysis, expert consensus, and intelligent verdicts.
            Get your free key at console.anthropic.com
        </div>
    </div>""", unsafe_allow_html=True)
    api_key_input = st.text_input("Anthropic API Key", type="password", placeholder="sk-ant-api03-...", key="api_key_input")
    if st.button("Save API Key", type="primary"):
        if api_key_input.startswith("sk-ant"):
            st.session_state.api_key_set = True
            st.success("✓ API key saved. Full AI analysis is now enabled.")
        else:
            st.error("Invalid API key format. Should start with sk-ant-")

    st.markdown('<div class="section-header" style="margin-top:1.5rem;">ABOUT</div>', unsafe_allow_html=True)
    st.markdown("""
    <div style="background:#111827;border:1px solid #1F2937;border-radius:12px;padding:1.25rem;font-size:0.82rem;color:#9CA3AF;line-height:1.7;">
        <strong style="color:#F9FAFB;">StockSense</strong> — AI Investment Intelligence<br><br>
        Data sources: Yahoo Finance · NSE India · BSE India · Google News · Reuters RSS<br>
        AI Analysis: Claude by Anthropic<br>
        Charts: Plotly<br><br>
        <span style="color:#EF4444;">⚠ Disclaimer:</span> This tool is for informational purposes only. 
        Always consult a qualified financial advisor before making investment decisions. 
        Past performance does not guarantee future results.
    </div>""", unsafe_allow_html=True)

