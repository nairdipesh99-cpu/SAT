MAIN_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

/* â”€â”€ Base â”€â”€ */
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.main { background-color: #0A0E1A; }
.block-container { padding: 1.5rem 2rem 2rem 2rem; max-width: 100%; }

/* â”€â”€ Hide Streamlit default elements â”€â”€ */
#MainMenu, footer, header { visibility: hidden; }
.stDeployButton { display: none; }

/* â”€â”€ Custom Header â”€â”€ */
.app-header {
    background: linear-gradient(135deg, #0F172A 0%, #1E293B 100%);
    border-bottom: 1px solid #1F2937;
    padding: 1rem 2rem;
    margin: -1.5rem -2rem 1.5rem -2rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
}

.app-logo {
    font-size: 1.4rem;
    font-weight: 700;
    color: #F9FAFB;
    letter-spacing: -0.5px;
}

.app-logo span { color: #3B82F6; }

.market-time {
    font-size: 0.75rem;
    color: #6B7280;
    font-weight: 400;
}

/* â”€â”€ Metric Cards â”€â”€ */
.metric-card {
    background: #111827;
    border: 1px solid #1F2937;
    border-radius: 12px;
    padding: 1rem 1.25rem;
    margin-bottom: 0.75rem;
}

.metric-label {
    font-size: 0.7rem;
    color: #6B7280;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    font-weight: 500;
    margin-bottom: 0.25rem;
}

.metric-value {
    font-size: 1.5rem;
    font-weight: 600;
    color: #F9FAFB;
    font-variant-numeric: tabular-nums;
}

.metric-change-up { color: #10B981; font-size: 0.85rem; font-weight: 500; }
.metric-change-down { color: #EF4444; font-size: 0.85rem; font-weight: 500; }

/* â”€â”€ Section Headers â”€â”€ */
.section-header {
    font-size: 0.7rem;
    font-weight: 600;
    color: #6B7280;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin: 1.5rem 0 0.75rem 0;
    padding-bottom: 0.5rem;
    border-bottom: 1px solid #1F2937;
}

/* â”€â”€ Stock Row â”€â”€ */
.stock-row {
    background: #111827;
    border: 1px solid #1F2937;
    border-radius: 10px;
    padding: 0.85rem 1.1rem;
    margin-bottom: 0.5rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
    cursor: pointer;
    transition: border-color 0.15s ease;
}

.stock-row:hover { border-color: #3B82F6; }

.stock-name {
    font-size: 0.95rem;
    font-weight: 600;
    color: #F9FAFB;
}

.stock-ticker {
    font-size: 0.72rem;
    color: #6B7280;
    margin-top: 2px;
}

.stock-price {
    font-size: 1rem;
    font-weight: 600;
    color: #F9FAFB;
    font-variant-numeric: tabular-nums;
    text-align: right;
}

/* â”€â”€ Decision Badges â”€â”€ */
.badge {
    display: inline-block;
    padding: 3px 10px;
    border-radius: 20px;
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.3px;
}

.badge-strong-buy  { background: #064E3B; color: #10B981; border: 1px solid #10B981; }
.badge-buy         { background: #052E16; color: #34D399; border: 1px solid #34D399; }
.badge-buy-dip     { background: #1E3A5F; color: #60A5FA; border: 1px solid #60A5FA; }
.badge-hold        { background: #451A03; color: #F59E0B; border: 1px solid #F59E0B; }
.badge-caution     { background: #431407; color: #FB923C; border: 1px solid #FB923C; }
.badge-avoid       { background: #450A0A; color: #EF4444; border: 1px solid #EF4444; }

/* â”€â”€ GC Indicators â”€â”€ */
.gc-pill {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    padding: 3px 8px;
    border-radius: 20px;
    font-size: 0.7rem;
    font-weight: 600;
}

.gc-green  { background: #064E3B; color: #10B981; border: 1px solid #065F46; }
.gc-amber  { background: #451A03; color: #F59E0B; border: 1px solid #78350F; }
.gc-red    { background: #450A0A; color: #EF4444; border: 1px solid #7F1D1D; }
.gc-winner { background: #1C1917; color: #F59E0B; border: 1px solid #92400E; }

/* â”€â”€ GC Winners Banner â”€â”€ */
.gc-winners-banner {
    background: linear-gradient(135deg, #1C1917 0%, #111827 100%);
    border: 1px solid #92400E;
    border-radius: 12px;
    padding: 1rem 1.25rem;
    margin-bottom: 1rem;
}

.gc-winners-title {
    font-size: 0.7rem;
    font-weight: 600;
    color: #F59E0B;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-bottom: 0.5rem;
}

/* â”€â”€ Index Pills â”€â”€ */
.index-pill {
    background: #111827;
    border: 1px solid #1F2937;
    border-radius: 8px;
    padding: 0.6rem 1rem;
    text-align: center;
}

.index-name { font-size: 0.68rem; color: #6B7280; font-weight: 500; }
.index-value { font-size: 1rem; font-weight: 600; color: #F9FAFB; font-variant-numeric: tabular-nums; }

/* â”€â”€ Portfolio Panel â”€â”€ */
.portfolio-card {
    background: #0F172A;
    border: 1px solid #1F2937;
    border-radius: 12px;
    padding: 1rem;
    height: 100%;
}

.portfolio-header {
    font-size: 0.7rem;
    font-weight: 600;
    color: #6B7280;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-bottom: 1rem;
    padding-bottom: 0.5rem;
    border-bottom: 1px solid #1F2937;
}

.portfolio-total {
    font-size: 1.6rem;
    font-weight: 700;
    color: #F9FAFB;
    font-variant-numeric: tabular-nums;
}

.portfolio-stock-item {
    background: #111827;
    border: 1px solid #1F2937;
    border-radius: 8px;
    padding: 0.65rem 0.85rem;
    margin-bottom: 0.4rem;
}

/* â”€â”€ Analysis Cards â”€â”€ */
.analysis-card {
    background: #111827;
    border: 1px solid #1F2937;
    border-radius: 12px;
    padding: 1.25rem;
    margin-bottom: 1rem;
}

.analysis-card-title {
    font-size: 0.7rem;
    font-weight: 600;
    color: #6B7280;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-bottom: 1rem;
}

/* â”€â”€ Decision Card (Top of analysis) â”€â”€ */
.decision-card {
    background: linear-gradient(135deg, #0F172A 0%, #111827 100%);
    border: 1px solid #1F2937;
    border-radius: 16px;
    padding: 1.5rem;
    margin-bottom: 1.25rem;
    text-align: center;
}

.decision-main {
    font-size: 2rem;
    font-weight: 700;
    margin-bottom: 0.25rem;
}

.decision-strong-buy { color: #10B981; }
.decision-buy        { color: #34D399; }
.decision-buy-dip    { color: #60A5FA; }
.decision-hold       { color: #F59E0B; }
.decision-caution    { color: #FB923C; }
.decision-avoid      { color: #EF4444; }

/* â”€â”€ Signal Bars â”€â”€ */
.signal-bar-container {
    background: #1F2937;
    border-radius: 4px;
    height: 6px;
    width: 100%;
    overflow: hidden;
}

.signal-bar-fill {
    height: 100%;
    border-radius: 4px;
    transition: width 0.5s ease;
}

/* â”€â”€ News Items â”€â”€ */
.news-item {
    border-left: 3px solid #1F2937;
    padding: 0.5rem 0.75rem;
    margin-bottom: 0.5rem;
    background: #0F172A;
    border-radius: 0 8px 8px 0;
}

.news-item-official { border-left-color: #10B981; }
.news-item-wire     { border-left-color: #3B82F6; }
.news-item-media    { border-left-color: #6B7280; }
.news-item-caution  { border-left-color: #EF4444; }

.news-source-tag {
    font-size: 0.65rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-bottom: 3px;
}

.news-headline { font-size: 0.82rem; color: #D1D5DB; line-height: 1.4; }
.news-time     { font-size: 0.68rem; color: #4B5563; margin-top: 3px; }

/* â”€â”€ Target Price Box â”€â”€ */
.target-box {
    background: #0F172A;
    border: 1px solid #1F2937;
    border-radius: 10px;
    padding: 0.85rem 1rem;
    text-align: center;
}

.target-label { font-size: 0.68rem; color: #6B7280; text-transform: uppercase; letter-spacing: 0.5px; }
.target-value { font-size: 1.1rem; font-weight: 600; color: #F9FAFB; font-variant-numeric: tabular-nums; }
.target-upside { font-size: 0.78rem; color: #10B981; font-weight: 500; }

/* â”€â”€ Tabs â”€â”€ */
.stTabs [data-baseweb="tab-list"] {
    background: #111827;
    border-radius: 10px;
    padding: 4px;
    gap: 4px;
    border: 1px solid #1F2937;
}

.stTabs [data-baseweb="tab"] {
    background: transparent;
    border-radius: 8px;
    color: #6B7280;
    font-weight: 500;
    font-size: 0.85rem;
    padding: 0.5rem 1.25rem;
    border: none;
}

.stTabs [aria-selected="true"] {
    background: #1F2937 !important;
    color: #F9FAFB !important;
}

/* â”€â”€ Buttons â”€â”€ */
.stButton > button {
    background: transparent;
    border: 1px solid #374151;
    color: #D1D5DB;
    border-radius: 8px;
    font-weight: 500;
    font-size: 0.85rem;
    padding: 0.4rem 1.2rem;
    transition: all 0.15s ease;
}

.stButton > button:hover {
    background: #1F2937;
    border-color: #4B5563;
    color: #F9FAFB;
}

.stButton > button[kind="primary"] {
    background: #2563EB;
    border-color: #2563EB;
    color: white;
}

.stButton > button[kind="primary"]:hover {
    background: #1D4ED8;
    border-color: #1D4ED8;
}

/* â”€â”€ Inputs â”€â”€ */
.stTextInput > div > div > input {
    background: #111827;
    border: 1px solid #374151;
    border-radius: 8px;
    color: #F9FAFB;
    font-size: 0.9rem;
}

.stTextInput > div > div > input:focus {
    border-color: #3B82F6;
    box-shadow: 0 0 0 1px #3B82F6;
}

.stSelectbox > div > div {
    background: #111827;
    border: 1px solid #374151;
    border-radius: 8px;
}

/* â”€â”€ Dividers â”€â”€ */
hr { border-color: #1F2937; margin: 1rem 0; }

/* â”€â”€ Scrollbar â”€â”€ */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: #0A0E1A; }
::-webkit-scrollbar-thumb { background: #374151; border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: #4B5563; }

/* â”€â”€ Loading â”€â”€ */
.loading-text {
    color: #6B7280;
    font-size: 0.85rem;
    text-align: center;
    padding: 2rem;
}

/* â”€â”€ Expert Rating Row â”€â”€ */
.expert-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.45rem 0;
    border-bottom: 1px solid #1F2937;
    font-size: 0.82rem;
}

.expert-name { color: #9CA3AF; }
.expert-buy  { color: #10B981; font-weight: 600; }
.expert-hold { color: #F59E0B; font-weight: 600; }
.expert-sell { color: #EF4444; font-weight: 600; }

/* â”€â”€ GC Monitor â”€â”€ */
.gc-category-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.65rem 0;
    border-bottom: 1px solid #1F2937;
}

.gc-category-name { font-size: 0.85rem; color: #D1D5DB; font-weight: 500; }
.gc-trend-up   { color: #EF4444; font-size: 0.75rem; }
.gc-trend-down { color: #10B981; font-size: 0.75rem; }
.gc-trend-flat { color: #6B7280; font-size: 0.75rem; }

/* â”€â”€ Tooltips / Info boxes â”€â”€ */
.info-box {
    background: #1E3A5F;
    border: 1px solid #1D4ED8;
    border-radius: 8px;
    padding: 0.65rem 0.85rem;
    font-size: 0.8rem;
    color: #93C5FD;
    margin: 0.5rem 0;
}

.warning-box {
    background: #451A03;
    border: 1px solid #92400E;
    border-radius: 8px;
    padding: 0.65rem 0.85rem;
    font-size: 0.8rem;
    color: #FCD34D;
    margin: 0.5rem 0;
}

/* â”€â”€ Leaderboard Table â”€â”€ */
.leaderboard-row {
    display: grid;
    grid-template-columns: 30px 1fr 80px 90px 90px 70px 70px;
    gap: 0.5rem;
    align-items: center;
    padding: 0.65rem 0.85rem;
    border-radius: 8px;
    margin-bottom: 0.3rem;
    font-size: 0.82rem;
    background: #111827;
    border: 1px solid #1F2937;
}

.rank-1 { border-left: 3px solid #F59E0B; }
.rank-2 { border-left: 3px solid #9CA3AF; }
.rank-3 { border-left: 3px solid #B45309; }
</style>
"""

