
import os
import json

def get_api_key():
    try:
        import streamlit as st
        return st.secrets.get("ANTHROPIC_API_KEY", "")
    except:
        return os.environ.get("ANTHROPIC_API_KEY", "")

def analyse_stock(stock_info, technicals, news, gc_status, gc_reason):
    """Call Claude API to get AI analysis"""
    api_key = get_api_key()
    if not api_key:
        return get_fallback_analysis(stock_info, technicals, gc_status)
    try:
        import anthropic
        client = anthropic.Anthropic(api_key=api_key)
        news_text = "\n".join([f"- [{n['tier']}] {n['title']}" for n in (news or [])[:6]])
        prompt = f"""You are a professional stock market analyst. Analyse this stock and give a clear investment verdict.

STOCK: {stock_info.get('name')} ({stock_info.get('ticker')})
SECTOR: {stock_info.get('sector', 'Unknown')}
CURRENT PRICE: {stock_info.get('price')} {stock_info.get('currency', 'INR')}

FINANCIAL METRICS:
- P/E Ratio: {stock_info.get('pe_ratio', 'N/A')}
- Revenue Growth: {stock_info.get('revenue_growth', 'N/A')}%
- Profit Margin: {stock_info.get('profit_margin', 'N/A')}%
- Debt to Equity: {stock_info.get('debt_to_equity', 'N/A')}
- ROE: {stock_info.get('roe', 'N/A')}%
- Dividend Yield: {stock_info.get('dividend_yield', 'N/A')}%
- Analyst Rating: {stock_info.get('analyst_rating', 'N/A')}

TECHNICAL SIGNALS:
- RSI: {technicals.get('rsi', 'N/A')}
- 50-day MA: {technicals.get('ma50', 'N/A')}
- 200-day MA: {technicals.get('ma200', 'N/A')}
- Golden Cross: {technicals.get('golden_cross', 'N/A')}
- 52-week position: {technicals.get('position_52w', 'N/A')}%

GLOBAL CRISIS STATUS: {gc_status} — {gc_reason}

RECENT NEWS:
{news_text if news_text else 'No significant news found'}

Respond ONLY in this exact JSON format with no other text:
{{
  "short_term_verdict": "STRONG BUY|BUY|BUY ON DIP|HOLD|CAUTION|AVOID",
  "long_term_verdict": "STRONG BUY|BUY|BUY ON DIP|HOLD|CAUTION|AVOID",
  "short_term_target": <number or null>,
  "long_term_target": <number or null>,
  "stop_loss": <number or null>,
  "short_term_reasons": ["reason1", "reason2", "reason3"],
  "long_term_reasons": ["reason1", "reason2", "reason3"],
  "key_risks": ["risk1", "risk2"],
  "signal_strength": "STRONG|MODERATE|WEAK",
  "summary": "2-3 sentence plain English summary"
}}"""
        resp = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1000,
            messages=[{"role": "user", "content": prompt}]
        )
        text = resp.content[0].text.strip()
        # Strip markdown fences
        if text.startswith("```"):
            text = "\n".join(text.split("\n")[1:])
        if text.endswith("```"):
            text = "\n".join(text.split("\n")[:-1])
        return json.loads(text)
    except Exception as e:
        return get_fallback_analysis(stock_info, technicals, gc_status)

def get_fallback_analysis(stock_info, technicals, gc_status):
    """Rule-based fallback when no API key"""
    from utils.helpers import calculate_score, score_to_decision
    metrics = {
        "revenue_growth":  stock_info.get("revenue_growth"),
        "profit_margin":   stock_info.get("profit_margin"),
        "debt_to_equity":  stock_info.get("debt_to_equity"),
        "rsi":             technicals.get("rsi"),
        "pe_ratio":        stock_info.get("pe_ratio"),
    }
    score = calculate_score(metrics)
    st_decision = score_to_decision(score, gc_status)
    lt_decision = score_to_decision(min(score + 5, 100), "GREEN")
    price = stock_info.get("price") or 100
    target_price = stock_info.get("target_price")
    st_target = round(target_price * 0.85, 2) if target_price else round(price * 1.12, 2)
    lt_target = round(target_price, 2) if target_price else round(price * 1.40, 2)
    stop_loss = round(price * 0.88, 2)
    rsi = technicals.get("rsi", 50)
    gc = technicals.get("golden_cross", False)
    st_reasons = []
    lt_reasons = []
    if rsi and rsi < 40:   st_reasons.append("RSI oversold — potential bounce opportunity")
    elif rsi and rsi > 70: st_reasons.append("RSI overbought — wait for pullback")
    else:                  st_reasons.append(f"RSI at {rsi} — neutral momentum zone")
    if gc:  st_reasons.append("Golden cross confirmed — bullish trend signal")
    else:   st_reasons.append("No golden cross — trend not confirmed yet")
    if stock_info.get("revenue_growth", 0) > 10:
        lt_reasons.append(f"Strong revenue growth of {stock_info.get('revenue_growth')}%")
    if stock_info.get("profit_margin", 0) > 8:
        lt_reasons.append(f"Healthy profit margin of {stock_info.get('profit_margin')}%")
    if stock_info.get("debt_to_equity") and stock_info["debt_to_equity"] < 1:
        lt_reasons.append("Manageable debt levels — financially stable")
    if not lt_reasons:
        lt_reasons.append("Fundamental data requires further review")
    return {
        "short_term_verdict":  st_decision,
        "long_term_verdict":   lt_decision,
        "short_term_target":   st_target,
        "long_term_target":    lt_target,
        "stop_loss":           stop_loss,
        "short_term_reasons":  st_reasons[:3],
        "long_term_reasons":   lt_reasons[:3],
        "key_risks":           ["Market volatility risk", "Sector specific risks apply"],
        "signal_strength":     "STRONG" if score >= 75 else "MODERATE" if score >= 50 else "WEAK",
        "summary":             f"Based on available data, {stock_info.get('name')} scores {score}/100. "
                               f"Add your Anthropic API key in Settings for full AI-powered analysis.",
        "api_key_missing":     True,
    }

