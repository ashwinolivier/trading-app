import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime
import pytz

# --- APP CONFIGURATION ---
st.set_page_config(page_title="Gold T.L.S. Pro", layout="wide", initial_sidebar_state="collapsed")

# --- CUSTOM STYLING ---
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stMetric { background-color: #1e2130; padding: 15px; border-radius: 10px; border: 1px solid #3e4255; }
    .signal-card { padding: 20px; border-radius: 15px; border-left: 10px solid #f63366; background-color: #262730; margin-bottom: 20px; }
    .success-card { border-left: 10px solid #00ffcc; }
    .news-card { padding: 10px; border-bottom: 1px solid #3e4255; margin-bottom: 5px; }
    </style>
    """, unsafe_allow_html=True)

# --- TIMEZONE & MARKET CLOCK ---
def get_market_info():
    jhb_tz = pytz.timezone('Africa/Johannesburg')
    ny_tz = pytz.timezone('America/New_York')
    now_jhb = datetime.now(jhb_tz)
    now_ny = datetime.now(ny_tz)
    day_ny = now_ny.weekday() 
    hour_ny = now_ny.hour
    status, color = "OPEN", "green"
    if day_ny == 5 or (day_ny == 4 and hour_ny >= 17) or (day_ny == 6 and hour_ny < 18):
        status, color = "CLOSED", "red"
    elif hour_ny == 17:
        status, color = "BREAK", "orange"
    return now_jhb, status, color

now_jhb, m_status, m_color = get_market_info()

# --- SIDEBAR ---
st.sidebar.header("Configuration")
symbol = st.sidebar.text_input("Asset", value="GC=F")
tf_choice = st.sidebar.selectbox("Select Timeframe", ("1h", "4h", "1d"), index=0)

# --- HEADER SECTION ---
col_h1, col_h2 = st.columns([2, 1])
with col_h1:
    st.title("🥇 Gold T.L.S. & News Scanner")
    st.subheader(f"{symbol} | {tf_choice.upper()} View")
with col_h2:
    st.write(f"📍 **JHB:** {now_jhb.strftime('%H:%M:%S')}")
    st.markdown(f"**Market Status:** :{m_color}[{m_status}]")

st.divider()

# --- DATA & NEWS ENGINE ---
ticker_obj = yf.Ticker(symbol)

@st.cache_data(ttl=60)
def load_data(ticker_str, tf):
    try:
        df = yf.download(ticker_str, period="60d", interval=tf, auto_adjust=True)
        return df
    except: return pd.DataFrame()

data = load_data(symbol, tf_choice)

# --- MAIN LAYOUT (Signals on Left, News on Right) ---
col_main, col_news = st.columns([2, 1])

with col_main:
    if not data.empty:
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.get_level_values(0)

        data['SMA21'] = data['Close'].rolling(window=21).mean()
        curr, prev = data.iloc[-1], data.iloc[-2]
        
        # Pattern Logic
        def detect_signals(c, p):
            o, h, l, cl = float(c['Open']), float(c['High']), float(c['Low']), float(c['Close'])
            po, pc = float(p['Open']), float(p['Close'])
            tr = h - l
            if tr == 0: return None
            body, l_shadow, u_shadow = abs(o - cl), min(o, cl) - l, h - max(o, cl)
            # Pin Bar
            if l_shadow > (body * 2) and u_shadow < (body * 0.5): return "Bullish Pin Bar"
            if u_shadow > (body * 2) and l_shadow < (body * 0.5): return "Bearish Pin Bar"
            # Engulfing
            if (cl > o) and (pc < po) and (cl >= po): return "Bullish Engulfing"
            if (cl < o) and (pc > po) and (cl <= po): return "Bearish Engulfing"
            return None

        signal = detect_signals(curr, prev)
        is_uptrend = float(curr['Close']) > float(curr['SMA21'])

        # Metrics
        m1, m2 = st.columns(2)
        m1.metric("Live Price", f"${float(curr['Close']):,.2f}")
        m2.metric("Trend", "UP" if is_uptrend else "DOWN")

        if signal:
            confluence = (is_uptrend and "Bullish" in signal) or (not is_uptrend and "Bearish" in signal)
            st.markdown(f"""<div class="signal-card {'success-card' if confluence else ''}">
                <h2>🎯 Signal: {signal}</h2>
                <h3>{'✅ T.L.S. MATCHED' if confluence else '⚠️ COUNTER-TREND'}</h3>
            </div>""", unsafe_allow_html=True)
        else:
            st.info(f"🔎 Scanning {tf_choice.upper()} for high-probability setups...")
    else:
        st.error("Data error.")

with col_news:
    st.subheader("📰 Market News Watch")
    try:
        news_items = ticker_obj.news
        if news_items:
            for item in news_items[:8]: # Show top 8 news items
                with st.container():
                    # Format timestamp
                    pub_time = datetime.fromtimestamp(item['providerPublishTime']).strftime('%H:%M')
                    st.markdown(f"""
                    <div class="news-card">
                        <small>{pub_time} | {item['publisher']}</small><br>
                        <b><a href="{item['link']}" target="_blank" style="color: #00ffcc; text-decoration: none;">{item['title']}</a></b>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.write("No recent news for this asset.")
    except:
        st.write("News feed temporarily unavailable.")
