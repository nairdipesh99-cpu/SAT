import streamlit as st
from utils.helpers import (format_currency, get_change_color,
                            get_change_arrow, decision_to_color, decision_to_bg,
                            gc_to_emoji, calculate_score, score_to_decision)
from data.yahoo_fetcher import get_historical_data, get_intraday_data, calculate_technicals
from data.news_fetcher import fetch_news, calculate_gc_status, tier_color
from data.ai_analyst import analyse_stock
from components.charts import plot_candlestick, plot_intraday

def render_stock_row(info, gc_status, short_verdict, long_verdict, on_click_key):
    price = info.get("price") or 0
    chg   = info.get("change_pct") or 0
    clr   = get_change_color(chg)
    arr   = get_change_arrow(chg)
    sv_clr = decision_to_color(short_verdict)
    lv_clr = decision_to_color(long_verdict)
    gc_em  = gc_to_emoji(gc_status)
    ticker = info.get("ticker", "")
    curr   = "₹" if ".NS" in ticker or ".BO" in ticker else ("£" if ".L" in ticker else "$")
    st.markdown(f"""
    <div class="stock-row">
        <div style="flex:2;">
            <div class="stock-name">{info.get('name','')[:22]}</div>
            <div class="stock-ticker">{ticker}</div>
        </div>
        <div style="flex:1;text-align:right;">
            <div class="stock-price">{curr}{price:,.2f}</div>
            <div style="font-size:0.75rem;color:{clr};font-weight:500;">{arr} {abs(chg):.2f}%</div>
        </div>
        <div style="flex:1;text-align:center;">
            <div style="font-size:0.68rem;color:#6B7280;margin-bottom:3px;">SHORT</div>
            <span style="font-size:0.72rem;font-weight:700;color:{sv_clr};">{short_verdict}</span>
        </div>
        <div style="flex:1;text-align:center;">
            <div style="font-size:0.68rem;color:#6B7280;margin-bottom:3px;">LONG</div>
            <span style="font-size:0.72rem;font-weight:700;color:{lv_clr};">{long_verdict}</span>
        </div>
        <div style="flex:0.6;text-align:center;">
            <span style="font-size:1rem;">{gc_em}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_full_analysis(ticker, market="india"):
    with st.spinner(f"Fetching data for {ticker}..."):
        from data.yahoo_fetcher import get_stock_info
        info = get_stock_info(ticker)
        if not info:
            st.error(f"Could not fetch data for {ticker}.")
            return
        hist  = get_historical_data(ticker)
        intra = get_intraday_data(ticker)
        tech  = calculate_technicals(hist) if hist is not None else {}
        news  = fetch_news(info.get("name", ""), ticker)
        gc_status, gc_reason = calculate_gc_status(ticker, info.get("sector", ""))
        analysis = analyse_stock(info, tech, news, gc_status, gc_reason)

    curr  = "₹" if ".NS" in ticker or ".BO" in ticker else ("£" if ".L" in ticker else "$")
    price = info.get("price") or 0
    chg   = info.get("change_pct") or 0
    clr   = get_change_color(chg)
    arr   = get_change_arrow(chg)

    st.markdown(f"""
    <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:1rem;">
        <div>
            <div style="font-size:1.3rem;font-weight:700;color:#F9FAFB;">{info.get('name','')}</div>
            <div style="font-size:0.8rem;color:#6B7280;">{ticker} · {info.get('sector','')}</div>
        </div>
        <div style="text-align:right;">
            <div style="font-size:1.8rem;font-weight:700;color:#F9FAFB;">{curr}{price:,.2f}</div>
            <div style="font-size:0.9rem;color:{clr};font-weight:500;">{arr} {abs(chg):.2f}% today</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st_v  = analysis.get("short_term_verdict", "HOLD")
    lt_v  = analysis.get("long_term_verdict",  "HOLD")
    st_c  = decision_to_color(st_v)
    lt_c  = decision_to_color(lt_v)
    st_t  = analysis.get("short_term_target")
    lt_t  = analysis.get("long_term_target")
    sl    = analysis.get("stop_loss")
    sig   = analysis.get("signal_strength", "MODERATE")
    sig_color = {"STRONG": "#10B981", "MODERATE": "#F59E0B", "WEAK": "#EF4444"}.get(sig, "#F59E0B")

    if analysis.get("api_key_missing"):
        st.info("🔑 Add your Anthropic API key in Settings for full AI analysis.")

    st.markdown(f"""
    <div style="background:#111827;border:1px solid #1F2937;border-radius:16px;padding:1.5rem;margin-bottom:1rem;">
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:1rem;margin-bottom:1rem;">
            <div style="text-align:center;background:#0F172A;border-radius:12px;padding:1rem;">
                <div style="font-size:0.68rem;color:#6B7280;text-transform:uppercase;margin-bottom:0.4rem;">Short Term · 1-6 months</div>
                <div style="font-size:1.4rem;font-weight:700;color:{st_c};">{st_v}</div>
                {f'<div style="font-size:0.78rem;color:#9CA3AF;margin-top:0.3rem;">Target {curr}{st_t:,.0f}</div>' if st_t else ''}
            </div>
            <div style="text-align:center;background:#0F172A;border-radius:12px;padding:1rem;">
                <div style="font-size:0.68rem;color:#6B7280;text-transform:uppercase;margin-bottom:0.4rem;">Long Term · 1-3 years</div>
                <div style="font-size:1.4rem;font-weight:700;color:{lt_c};">{lt_v}</div>
                {f'<div style="font-size:0.78rem;color:#9CA3AF;margin-top:0.3rem;">Target {curr}{lt_t:,.0f}</div>' if lt_t else ''}
            </div>
        </div>
        <div style="display:flex;justify-content:space-between;padding-top:0.75rem;border-top:1px solid #1F2937;font-size:0.78rem;">
            <span style="color:#9CA3AF;">Signal: <span style="color:{sig_color};font-weight:600;">{sig}</span></span>
            {f'<span style="color:#9CA3AF;">Stop Loss: <span style="color:#EF4444;font-weight:600;">{curr}{sl:,.0f}</span></span>' if sl else ''}
            <span>GC: {gc_to_emoji(gc_status)}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["📈 5-Year Chart", "⚡ Intraday"])
    with tab1:
        if hist is not None:
            fig = plot_candlestick(hist, ticker)
            if fig:
                st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
        else:
            st.info("Historical data unavailable.")
    with tab2:
        if intra is not None:
            fig2 = plot_intraday(intra, ticker)
            if fig2:
                st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar": False})
        else:
            st.info("Intraday data unavailable. Market may be closed.")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="section-header">FINANCIAL HEALTH</div>', unsafe_allow_html=True)
        metrics = [
            ("Revenue Growth",  f"{info.get('revenue_growth', 'N/A')}%"),
            ("Profit Margin",   f"{info.get('profit_margin', 'N/A')}%"),
            ("Debt / Equity",   f"{info.get('debt_to_equity', 'N/A')}"),
            ("P/E Ratio",       f"{info.get('pe_ratio', 'N/A')}"),
            ("ROE",             f"{info.get('roe', 'N/A')}%"),
            ("Dividend Yield",  f"{info.get('dividend_yield', 'N/A')}%"),
        ]
        for label, val in metrics:
            st.markdown(f"""
            <div style="display:flex;justify-content:space-between;padding:0.4rem 0;
                        border-bottom:1px solid #1F2937;font-size:0.82rem;">
                <span style="color:#9CA3AF;">{label}</span>
                <span style="color:#F9FAFB;font-weight:600;">{val}</span>
            </div>""", unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="section-header">TECHNICAL SIGNALS</div>', unsafe_allow_html=True)
        rsi  = tech.get("rsi")
        gc   = tech.get("golden_cross")
        pos52 = tech.get("position_52w")
        technicals = [
            ("RSI",          f"{rsi}" if rsi else "N/A"),
            ("MA Signal",    "Golden Cross 🟢" if gc else "Death Cross 🔴"),
            ("52W Position", f"{pos52}%" if pos52 else "N/A"),
            ("50-day MA",    f"{curr}{tech.get('ma50', 'N/A')}"),
            ("200-day MA",   f"{curr}{tech.get('ma200', 'N/A')}"),
            ("Analyst",      info.get("analyst_rating", "N/A")),
        ]
        for label, val in technicals:
            st.markdown(f"""
            <div style="display:flex;justify-content:space-between;padding:0.4rem 0;
                        border-bottom:1px solid #1F2937;font-size:0.82rem;">
                <span style="color:#9CA3AF;">{label}</span>
                <span style="color:#F9FAFB;font-weight:600;">{val}</span>
            </div>""", unsafe_allow_html=True)

    if analysis.get("summary"):
        st.markdown(f"""
        <div style="background:#0F172A;border:1px solid #1F2937;border-radius:10px;
                    padding:0.85rem;margin-top:0.75rem;font-size:0.82rem;
                    color:#D1D5DB;line-height:1.6;">
            {analysis['summary']}
        </div>""", unsafe_allow_html=True)

    if news:
        st.markdown('<div class="section-header">NEWS</div>', unsafe_allow_html=True)
        for item in news[:5]:
            tc = tier_color(item["tier"])
            st.markdown(f"""
            <div style="border-left:3px solid {tc};padding:0.4rem 0.75rem;
                        margin-bottom:0.4rem;background:#0F172A;border-radius:0 8px 8px 0;">
                <div style="font-size:0.65rem;font-weight:600;color:{tc};text-transform:uppercase;">
                    {item['tier']} · {item.get('source','')}
                </div>
                <div style="font-size:0.8rem;color:#D1D5DB;margin-top:2px;">{item['title']}</div>
                <div style="font-size:0.68rem;color:#4B5563;margin-top:2px;">{item.get('time','')}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown('<div style="margin-top:1rem;"></div>', unsafe_allow_html=True)
    from components.portfolio_panel import render_add_to_portfolio
    render_add_to_portfolio(ticker, info.get("name", ""), price, market)
