import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np

COLORS = {
    "bg":      "#0A0E1A",
    "card":    "#111827",
    "border":  "#1F2937",
    "text":    "#F9FAFB",
    "muted":   "#6B7280",
    "green":   "#10B981",
    "red":     "#EF4444",
    "blue":    "#3B82F6",
    "amber":   "#F59E0B",
    "ma50":    "#F59E0B",
    "ma200":   "#A78BFA",
}

def plot_candlestick(df, ticker, show_ma=True):
    """5-year weekly candlestick chart with MAs"""
    if df is None or df.empty:
        return None
    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.03,
        row_heights=[0.75, 0.25]
    )
    # Candlestick
    fig.add_trace(go.Candlestick(
        x=df.index, open=df["Open"], high=df["High"],
        low=df["Low"],  close=df["Close"],
        increasing_line_color=COLORS["green"],
        decreasing_line_color=COLORS["red"],
        increasing_fillcolor=COLORS["green"],
        decreasing_fillcolor=COLORS["red"],
        name="Price",
        showlegend=False,
    ), row=1, col=1)
    # Moving averages
    if show_ma and len(df) >= 20:
        close = df["Close"]
        ma50_data  = close.rolling(min(50,  len(close))).mean()
        ma200_data = close.rolling(min(200, len(close))).mean()
        fig.add_trace(go.Scatter(
            x=df.index, y=ma50_data,
            line=dict(color=COLORS["ma50"], width=1.5, dash="solid"),
            name="50 MA", opacity=0.8,
        ), row=1, col=1)
        fig.add_trace(go.Scatter(
            x=df.index, y=ma200_data,
            line=dict(color=COLORS["ma200"], width=1.5, dash="solid"),
            name="200 MA", opacity=0.8,
        ), row=1, col=1)
    # Volume bars
    colors = [COLORS["green"] if c >= o else COLORS["red"]
              for c, o in zip(df["Close"], df["Open"])]
    fig.add_trace(go.Bar(
        x=df.index, y=df["Volume"],
        marker_color=colors, marker_opacity=0.6,
        name="Volume", showlegend=False,
    ), row=2, col=1)
    fig.update_layout(
        plot_bgcolor=COLORS["card"],
        paper_bgcolor=COLORS["card"],
        font=dict(family="Inter", color=COLORS["text"], size=11),
        margin=dict(l=0, r=0, t=10, b=0),
        legend=dict(
            orientation="h", yanchor="bottom", y=1.02,
            xanchor="left", x=0,
            bgcolor="rgba(0,0,0,0)",
            font=dict(size=11, color=COLORS["muted"]),
        ),
        xaxis_rangeslider_visible=False,
        height=420,
    )
    for row in [1, 2]:
        fig.update_xaxes(
            gridcolor=COLORS["border"], zeroline=False,
            showline=False, row=row, col=1,
        )
        fig.update_yaxes(
            gridcolor=COLORS["border"], zeroline=False,
            showline=False, row=row, col=1,
            tickfont=dict(size=10, color=COLORS["muted"]),
        )
    return fig

def plot_intraday(df, ticker):
    """Intraday 5-minute candlestick chart"""
    if df is None or df.empty:
        return None
    fig = go.Figure()
    fig.add_trace(go.Candlestick(
        x=df.index, open=df["Open"], high=df["High"],
        low=df["Low"],  close=df["Close"],
        increasing_line_color=COLORS["green"],
        decreasing_line_color=COLORS["red"],
        increasing_fillcolor=COLORS["green"],
        decreasing_fillcolor=COLORS["red"],
        name="", showlegend=False,
    ))
    # VWAP
    if "Volume" in df.columns and len(df) > 1:
        typical = (df["High"] + df["Low"] + df["Close"]) / 3
        vwap = (typical * df["Volume"]).cumsum() / df["Volume"].cumsum()
        fig.add_trace(go.Scatter(
            x=df.index, y=vwap,
            line=dict(color=COLORS["blue"], width=1.5, dash="dot"),
            name="VWAP", opacity=0.9,
        ))
    fig.update_layout(
        plot_bgcolor=COLORS["card"],
        paper_bgcolor=COLORS["card"],
        font=dict(family="Inter", color=COLORS["text"], size=11),
        margin=dict(l=0, r=0, t=10, b=0),
        xaxis_rangeslider_visible=False,
        height=280,
        legend=dict(
            orientation="h", yanchor="bottom", y=1.02,
            xanchor="left", x=0,
            bgcolor="rgba(0,0,0,0)",
            font=dict(size=11, color=COLORS["muted"]),
        ),
    )
    fig.update_xaxes(gridcolor=COLORS["border"], zeroline=False, showline=False)
    fig.update_yaxes(gridcolor=COLORS["border"], zeroline=False, showline=False,
                     tickfont=dict(size=10, color=COLORS["muted"]))
    return fig

def plot_health_radar(metrics):
    """Radar chart for financial health"""
    categories = ["Revenue Growth", "Profit Margin", "Low Debt", "Valuation", "Momentum"]
    rg = metrics.get("revenue_growth", 0) or 0
    pm = metrics.get("profit_margin", 0) or 0
    de = metrics.get("debt_to_equity", 2) or 2
    pe = metrics.get("pe_ratio", 30) or 30
    rs = metrics.get("rsi", 50) or 50
    values = [
        min(100, max(0, rg * 4)),
        min(100, max(0, pm * 4)),
        min(100, max(0, (2 - min(de, 2)) * 50)),
        min(100, max(0, (40 - min(pe, 40)) * 2.5)),
        min(100, max(0, 100 - abs(rs - 50) * 2)),
    ]
    values_closed = values + [values[0]]
    cats_closed   = categories + [categories[0]]
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=values_closed, theta=cats_closed,
        fill="toself",
        fillcolor="rgba(59, 130, 246, 0.15)",
        line=dict(color=COLORS["blue"], width=2),
        name="Health Score",
    ))
    fig.update_layout(
        polar=dict(
            bgcolor=COLORS["card"],
            radialaxis=dict(visible=True, range=[0, 100], gridcolor=COLORS["border"],
                            tickfont=dict(color=COLORS["muted"], size=9), showticklabels=False),
            angularaxis=dict(gridcolor=COLORS["border"],
                             tickfont=dict(color=COLORS["text"], size=11)),
        ),
        plot_bgcolor=COLORS["card"],
        paper_bgcolor=COLORS["card"],
        font=dict(family="Inter", color=COLORS["text"]),
        margin=dict(l=40, r=40, t=20, b=20),
        height=260,
        showlegend=False,
    )
    return fig

def plot_score_gauge(score):
    """Gauge chart for overall score"""
    color = COLORS["green"] if score >= 70 else COLORS["amber"] if score >= 45 else COLORS["red"]
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        domain={"x": [0, 1], "y": [0, 1]},
        gauge={
            "axis": {"range": [0, 100], "tickcolor": COLORS["muted"],
                     "tickfont": {"color": COLORS["muted"], "size": 10}},
            "bar":  {"color": color, "thickness": 0.25},
            "bgcolor": COLORS["card"],
            "bordercolor": COLORS["border"],
            "steps": [
                {"range": [0,  30], "color": "#1A0A0A"},
                {"range": [30, 55], "color": "#1C1209"},
                {"range": [55, 75], "color": "#0C1A20"},
                {"range": [75, 100],"color": "#071A12"},
            ],
            "threshold": {"line": {"color": color, "width": 3}, "thickness": 0.75, "value": score},
        },
        number={"font": {"size": 28, "color": COLORS["text"], "family": "Inter"}, "suffix": ""},
    ))
    fig.update_layout(
        paper_bgcolor=COLORS["card"],
        font=dict(family="Inter", color=COLORS["text"]),
        margin=dict(l=20, r=20, t=20, b=10),
        height=180,
    )
    return fig

