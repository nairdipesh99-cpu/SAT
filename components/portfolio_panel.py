import streamlit as st
import json
import os
from datetime import datetime

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

def render_portfolio(market_filter=None):
    portfolio = load_portfolio()
    st.markdown('<div class="portfolio-header">MY PORTFOLIO</div>', unsafe_allow_html=True)
    if not portfolio:
        st.markdown("""
        <div style="text-align:center;padding:1.5rem 0;color:#4B5563;font-size:0.82rem;">
            No stocks added yet.<br>Search and add stocks below.
        </div>""", unsafe_allow_html=True)
        return
    st.markdown('<hr style="border-color:#1F2937;margin:0.75rem 0;">', unsafe_allow_html=True)

def render_add_to_portfolio(ticker, name, price, market, current_verdict="BUY"):
    with st.expander("➕ Add to Portfolio"):
        c1, c2 = st.columns(2)
        with c1:
            shares = st.number_input("Shares", min_value=1, value=10, key=f"shares_{ticker}")
        with c2:
            buy_price = st.number_input("Buy Price", min_value=0.01,
                                        value=float(price or 100), key=f"bp_{ticker}")
        sl_pref = st.select_slider(
            "Stop loss width",
            options=["CONSERVATIVE", "MODERATE", "AGGRESSIVE"],
            value="MODERATE",
            key=f"sl_pref_{ticker}",
        )
        if st.button("Add to Portfolio", type="primary", key=f"add_{ticker}"):
            portfolio = load_portfolio()
            portfolio[ticker] = {
                "name": name,
                "shares": shares,
                "buy_price": buy_price,
                "market": market,
                "added": datetime.now().strftime("%Y-%m-%d"),
                "original_verdict": current_verdict,
                "sl_preference": sl_pref,
            }
            save_portfolio(portfolio)
            st.success(f"✓ {name} added to portfolio")
            st.rerun()
