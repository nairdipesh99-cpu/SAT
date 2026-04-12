
import streamlit as st
from utils.helpers import load_portfolio, save_portfolio, format_currency, decision_to_color, gc_to_emoji
from data.yahoo_fetcher import get_stock_info, get_historical_data, calculate_technicals
from data.news_fetcher import calculate_gc_status
from data.stop_loss_engine import (calculate_ai_stop_loss, check_alert_status,
                                    get_ai_stop_loss_explanation)
from data.ai_analyst import get_fallback_analysis
from utils.helpers import calculate_score, score_to_decision
import json, os

SL_FILE = "stop_losses.json"

def load_stop_losses():
    if os.path.exists(SL_FILE):
        try:
            with open(SL_FILE) as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_stop_losses(data):
    with open(SL_FILE, "w") as f:
        json.dump(data, f, indent=2)

def render_alerts_tab():
    portfolio  = load_portfolio()
    stop_losses = load_stop_losses()

    st.markdown("""
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:1rem;">
        <div>
            <div style="font-size:1.1rem;font-weight:700;color:#F9FAFB;">🛡️ Position Alerts & AI Stop Loss</div>
            <div style="font-size:0.75rem;color:#6B7280;margin-top:3px;">
                AI monitors every position daily and alerts you before losses grow
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if not portfolio:
        st.markdown("""
        <div style="text-align:center;padding:3rem;background:#111827;border:1px solid #1F2937;border-radius:12px;">
            <div style="font-size:2rem;margin-bottom:0.75rem;">🛡️</div>
            <div style="color:#F9FAFB;font-weight:600;margin-bottom:0.4rem;">No positions to monitor</div>
            <div style="color:#6B7280;font-size:0.82rem;">Add stocks to your portfolio to enable AI stop loss protection.</div>
        </div>""", unsafe_allow_html=True)
        return

    # ── Scan all positions ──
    alerts      = []
    safe        = []
    all_results = []

    for ticker, pdata in portfolio.items():
        info = get_stock_info(ticker)
        if not info:
            continue
        current_price = info.get("price") or pdata["buy_price"]
        buy_price     = pdata["buy_price"]
        shares        = pdata["shares"]
        name          = pdata["name"]

        # Get today's analysis
        hist  = get_historical_data(ticker, period="1y")
        tech  = calculate_technicals(hist) if hist is not None else {}
        gc_s, gc_r = calculate_gc_status(ticker, info.get("sector",""))
        metrics = {
            "revenue_growth": info.get("revenue_growth"),
            "profit_margin":  info.get("profit_margin"),
            "debt_to_equity": info.get("debt_to_equity"),
            "rsi":            tech.get("rsi"),
            "pe_ratio":       info.get("pe_ratio"),
        }
        score         = calculate_score(metrics)
        today_verdict = score_to_decision(score, gc_s)

        # Original verdict stored
        orig_verdict  = pdata.get("original_verdict", "BUY")
        analysis_reversed = _is_reversed(orig_verdict, today_verdict)

        # Get or calculate stop loss
        sl_key = ticker
        pref   = stop_losses.get(sl_key, {}).get("preference", "MODERATE")
        sl_data = calculate_ai_stop_loss(ticker, buy_price, shares, pref)
        sl_data["today_verdict"]      = today_verdict
        sl_data["original_verdict"]   = orig_verdict
        sl_data["analysis_reversed"]  = analysis_reversed
        sl_data["name"]               = name

        alert_status, alert_emoji, alert_msg = check_alert_status(sl_data)
        sl_data["alert_status"] = alert_status
        sl_data["alert_emoji"]  = alert_emoji
        sl_data["alert_msg"]    = alert_msg

        if alert_status in ("HARD_STOP", "REDUCE", "DEEP_LOSS") or analysis_reversed:
            alerts.append(sl_data)
        else:
            safe.append(sl_data)
        all_results.append(sl_data)

    # ── Alert Banner ──
    if alerts:
        st.markdown(f"""
        <div style="background:#450A0A;border:1px solid #7F1D1D;border-radius:12px;
                    padding:1rem 1.25rem;margin-bottom:1.25rem;">
            <div style="font-size:0.75rem;font-weight:700;color:#EF4444;
                        text-transform:uppercase;letter-spacing:0.8px;margin-bottom:0.5rem;">
                🚨 {len(alerts)} POSITION{'S' if len(alerts)>1 else ''} NEED YOUR ATTENTION
            </div>
            <div style="font-size:0.82rem;color:#FCA5A5;">
                Review the alerts below and take action to protect your capital.
            </div>
        </div>""", unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="background:#064E3B;border:1px solid #065F46;border-radius:12px;
                    padding:0.85rem 1.25rem;margin-bottom:1.25rem;">
            <div style="font-size:0.82rem;color:#10B981;font-weight:500;">
                ✓ All positions are within safe parameters — no action needed today
            </div>
        </div>""", unsafe_allow_html=True)

    # ── Render Alert Positions First ──
    for sl in alerts:
        _render_position_card(sl, stop_losses, is_alert=True)

    # ── Render Safe Positions ──
    if safe:
        st.markdown('<div class="section-header" style="margin-top:1rem;">SAFE POSITIONS</div>', unsafe_allow_html=True)
        for sl in safe:
            _render_position_card(sl, stop_losses, is_alert=False)

    # ── Summary Stats ──
    if all_results:
        st.markdown('<div class="section-header" style="margin-top:1.5rem;">PORTFOLIO RISK SUMMARY</div>', unsafe_allow_html=True)
        c1, c2, c3, c4 = st.columns(4)
        total_at_risk = sum(r["max_loss_total"] for r in all_results)
        profitable    = sum(1 for r in all_results if r["pnl_pct"] > 0)
        avg_loss_pct  = sum(r["loss_pct"] for r in all_results) / len(all_results)
        with c1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Positions</div>
                <div class="metric-value">{len(all_results)}</div>
            </div>""", unsafe_allow_html=True)
        with c2:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">In Profit</div>
                <div class="metric-value" style="color:#10B981;">{profitable}</div>
            </div>""", unsafe_allow_html=True)
        with c3:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Alerts Active</div>
                <div class="metric-value" style="color:{'#EF4444' if alerts else '#10B981'};">{len(alerts)}</div>
            </div>""", unsafe_allow_html=True)
        with c4:
            curr = all_results[0]["currency"] if all_results else "₹"
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Max Capital at Risk</div>
                <div class="metric-value" style="color:#F59E0B;">{curr}{total_at_risk:,.0f}</div>
            </div>""", unsafe_allow_html=True)

def _render_position_card(sl, stop_losses, is_alert):
    ticker  = sl["ticker"]
    name    = sl["name"]
    curr    = sl["currency"]
    pnl     = sl["pnl_pct"]
    pnl_clr = "#10B981" if pnl >= 0 else "#EF4444"
    pnl_arr = "▲" if pnl >= 0 else "▼"
    border  = "#7F1D1D" if is_alert else "#1F2937"
    bg      = "#1A0505" if is_alert else "#111827"

    with st.expander(
        f"{sl['alert_emoji']} {name} ({ticker}) — {curr}{sl['current_price']:,.2f} "
        f"({pnl_arr}{abs(pnl):.1f}%) — {sl['alert_msg']}",
        expanded=is_alert
    ):
        # ── Top row ──
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Bought At</div>
                <div class="metric-value">{curr}{sl['buy_price']:,.2f}</div>
            </div>""", unsafe_allow_html=True)
        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Current Price</div>
                <div class="metric-value" style="color:{pnl_clr};">{curr}{sl['current_price']:,.2f}</div>
            </div>""", unsafe_allow_html=True)
        with col3:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">P&L ({sl['shares']} shares)</div>
                <div class="metric-value" style="color:{pnl_clr};">
                    {pnl_arr}{abs((sl['current_price']-sl['buy_price'])*sl['shares']):,.0f}
                </div>
            </div>""", unsafe_allow_html=True)

        # ── Analysis Reversal Warning ──
        if sl.get("analysis_reversed"):
            ov_clr = decision_to_color(sl["original_verdict"])
            tv_clr = decision_to_color(sl["today_verdict"])
            st.markdown(f"""
            <div style="background:#451A03;border:1px solid #92400E;border-radius:10px;
                        padding:0.85rem 1rem;margin:0.75rem 0;">
                <div style="font-size:0.72rem;font-weight:700;color:#F59E0B;
                            text-transform:uppercase;letter-spacing:0.5px;margin-bottom:0.4rem;">
                    ⚠️ ANALYSIS REVERSED
                </div>
                <div style="display:flex;gap:1rem;align-items:center;font-size:0.82rem;">
                    <span>When you bought: <strong style="color:{ov_clr};">{sl['original_verdict']}</strong></span>
                    <span style="color:#6B7280;">→</span>
                    <span>Today's verdict: <strong style="color:{tv_clr};">{sl['today_verdict']}</strong></span>
                </div>
                <div style="font-size:0.78rem;color:#FCD34D;margin-top:0.4rem;">
                    Market conditions have shifted since your purchase. Review this position carefully.
                </div>
            </div>""", unsafe_allow_html=True)

        # ── 3-Level Stop Loss Visual ──
        st.markdown('<div style="margin:0.75rem 0 0.4rem;font-size:0.72rem;font-weight:600;color:#6B7280;text-transform:uppercase;letter-spacing:0.8px;">AI STOP LOSS LEVELS</div>', unsafe_allow_html=True)

        cp = sl["current_price"]
        w  = sl["warning_level"]
        r  = sl["reduce_level"]
        h  = sl["hard_stop"]

        def _pct(level): return round((cp - level) / cp * 100, 1)

        levels = [
            ("🟡", "WARNING LEVEL",   w, "Do not exit — monitor closely",        "#451A03", "#F59E0B"),
            ("🟠", "REDUCE POSITION", r, "Sell 50% — limit further loss",          "#431407", "#FB923C"),
            ("🔴", "HARD STOP EXIT",  h, "Exit all — capital preservation mode",   "#450A0A", "#EF4444"),
        ]
        for emoji, label, level, action, bg_c, txt_c in levels:
            hit = cp <= level
            st.markdown(f"""
            <div style="background:{bg_c};border:1px solid {txt_c}40;border-radius:8px;
                        padding:0.6rem 0.85rem;margin-bottom:0.35rem;
                        display:flex;justify-content:space-between;align-items:center;
                        {'border-color:'+txt_c+';' if hit else ''}">
                <div>
                    <span style="font-size:0.85rem;">{emoji}</span>
                    <span style="font-size:0.75rem;font-weight:600;color:{txt_c};margin-left:6px;">
                        {label} {'← TRIGGERED' if hit else ''}
                    </span>
                    <div style="font-size:0.72rem;color:#9CA3AF;margin-top:2px;">{action}</div>
                </div>
                <div style="text-align:right;">
                    <div style="font-size:0.95rem;font-weight:700;color:{txt_c};">{curr}{level:,.2f}</div>
                    <div style="font-size:0.7rem;color:#6B7280;">-{_pct(level):.1f}% from now</div>
                </div>
            </div>""", unsafe_allow_html=True)

        # ── Max Loss Box ──
        st.markdown(f"""
        <div style="background:#0F172A;border:1px solid #1F2937;border-radius:8px;
                    padding:0.65rem 1rem;margin:0.5rem 0;display:flex;justify-content:space-between;">
            <div style="font-size:0.78rem;color:#6B7280;">
                Max loss if hard stop triggered
            </div>
            <div style="font-size:0.85rem;font-weight:600;color:#EF4444;">
                -{curr}{sl['max_loss_total']:,.0f} ({sl['loss_pct']:.1f}%)
            </div>
        </div>""", unsafe_allow_html=True)

        # ── Trailing Stop Note ──
        if sl.get("trailing_floor"):
            st.markdown(f"""
            <div style="background:#064E3B;border:1px solid #065F46;border-radius:8px;
                        padding:0.55rem 0.85rem;margin-bottom:0.5rem;font-size:0.78rem;color:#10B981;">
                ✓ Trailing stop active — floor raised to {curr}{sl['trailing_floor']:,.2f} to protect your gains
            </div>""", unsafe_allow_html=True)

        # ── Key Conditions ──
        st.markdown('<div style="margin-top:0.75rem;font-size:0.72rem;font-weight:600;color:#6B7280;text-transform:uppercase;letter-spacing:0.8px;">MARKET CONDITIONS FACTORED IN</div>', unsafe_allow_html=True)
        conds = [
            ("Market Trend", sl["market_trend"],   {"BULLISH":"#10B981","BEARISH":"#EF4444","SIDEWAYS":"#F59E0B"}),
            ("VIX Level",    sl["vix_level"],       {"LOW":"#10B981","MODERATE":"#F59E0B","HIGH":"#EF4444"}),
            ("GC Status",    f"{gc_to_emoji(sl['gc_status'])} {sl['gc_status']}", {"GREEN":"#10B981","AMBER":"#F59E0B","RED":"#EF4444","WINNER":"#F59E0B"}),
            ("Entry Quality",sl["entry_quality"],   {"EXCELLENT":"#10B981","GOOD":"#34D399","AVERAGE":"#F59E0B","RISKY":"#EF4444"}),
        ]
        if sl.get("earnings_days") and sl["earnings_days"] <= 30:
            conds.append((f"Earnings", f"In {sl['earnings_days']} days ⚠️", {}))
        if sl.get("rr_ratio"):
            conds.append(("Risk/Reward", f"1:{sl['rr_ratio']}", {}))

        cc = st.columns(3)
        for i, (label, val, cmap) in enumerate(conds):
            color = cmap.get(val, "#9CA3AF") if cmap else "#9CA3AF"
            with cc[i % 3]:
                st.markdown(f"""
                <div style="padding:0.4rem 0;border-bottom:1px solid #1F2937;font-size:0.78rem;">
                    <div style="color:#6B7280;">{label}</div>
                    <div style="color:{color};font-weight:600;">{val}</div>
                </div>""", unsafe_allow_html=True)

        # ── Why These Levels ──
        if sl.get("reasons"):
            st.markdown('<div style="margin-top:0.75rem;font-size:0.72rem;font-weight:600;color:#6B7280;text-transform:uppercase;letter-spacing:0.8px;">WHY THESE LEVELS</div>', unsafe_allow_html=True)
            for reason in sl["reasons"]:
                st.markdown(f'<div style="font-size:0.78rem;color:#D1D5DB;padding:0.2rem 0;">• {reason}</div>', unsafe_allow_html=True)

        # ── AI Explanation ──
        if st.button(f"🤖 Get AI Explanation", key=f"ai_exp_{ticker}"):
            with st.spinner("Claude AI is analysing your position..."):
                explanation = get_ai_stop_loss_explanation(sl, sl.get("analysis_reversed", False))
            st.markdown(f"""
            <div style="background:#1E3A5F;border:1px solid #1D4ED8;border-radius:10px;
                        padding:0.85rem 1rem;margin-top:0.5rem;font-size:0.82rem;
                        color:#93C5FD;line-height:1.7;">
                🤖 <strong>Claude AI says:</strong><br><br>{explanation}
            </div>""", unsafe_allow_html=True)

        # ── Support Levels ──
        if sl.get("support_levels"):
            st.markdown(f"""
            <div style="font-size:0.72rem;color:#6B7280;margin-top:0.5rem;">
                Key support levels identified: {' → '.join([f'{curr}{s:,.0f}' for s in sl['support_levels']])}
            </div>""", unsafe_allow_html=True)

        # ── Risk Preference Control ──
        st.markdown('<div style="margin-top:0.75rem;"></div>', unsafe_allow_html=True)
        pref_key  = f"pref_{ticker}"
        cur_pref  = stop_losses.get(ticker, {}).get("preference", "MODERATE")
        new_pref  = st.select_slider(
            "Adjust stop loss width",
            options=["CONSERVATIVE", "MODERATE", "AGGRESSIVE"],
            value=cur_pref,
            key=pref_key,
            help="Conservative = tighter stops, Aggressive = wider stops for volatile stocks"
        )
        if new_pref != cur_pref:
            if ticker not in stop_losses:
                stop_losses[ticker] = {}
            stop_losses[ticker]["preference"] = new_pref
            save_stop_losses(stop_losses)
            st.rerun()

        # ── Action Buttons ──
        st.markdown('<div style="margin-top:0.5rem;"></div>', unsafe_allow_html=True)
        ab1, ab2, ab3 = st.columns(3)
        with ab1:
            if st.button("📊 Full Analysis", key=f"full_{ticker}"):
                st.session_state.selected_stock  = ticker
                st.session_state.selected_market = portfolio.get(ticker, {}).get("market", "india")
                st.rerun()
        with ab2:
            if is_alert and st.button("⚠️ Mark Reviewed", key=f"rev_{ticker}"):
                st.success("Marked as reviewed — will re-alert if conditions worsen")
        with ab3:
            if st.button("🗑️ Remove Position", key=f"rmp_{ticker}"):
                from utils.helpers import remove_from_portfolio
                remove_from_portfolio(ticker)
                st.rerun()

def _is_reversed(original, today):
    """Check if verdict has materially reversed"""
    order = {"STRONG BUY": 0, "BUY": 1, "BUY ON DIP": 2, "HOLD": 3, "CAUTION": 4, "AVOID": 5}
    o = order.get(original, 2)
    t = order.get(today, 2)
    return t - o >= 2  # 2+ steps down = reversal

