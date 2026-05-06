import streamlit as st
import yfinance as yf
import pandas as pd
import feedparser
from datetime import datetime
import pytz

# --- 1. APP CONFIGURATION ---
st.set_page_config(page_title="Gold T.L.S. Pro", layout="wide", initial_sidebar_state="collapsed")

# Custom CSS for a professional look on mobile/desktop
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stMetric { background-color: #1e2130; padding: 15px; border-radius: 10px; border: 1px solid #3e4255; }
    .signal-card { padding: 20px; border-radius: 15px; border-left: 10px solid #f63366; background-color: #262730; margin-bottom: 20px; }
    .success-card { border-left: 10px solid #00ffcc; }
    .news-card { padding: 12px; border-bottom: 1px solid #3e4255; margin-bottom: 8px; font-size: 14px; }
    a { text-decoration: none; color: #00ffcc; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. TIMEZONE & MARKET CLOCK (Johannesburg vs New York) ---
def get_market_info():
    jhb_tz = pytz.timezone('Africa/Johannesburg')
    ny_tz = pytz.timezone('America/New_York')
    now_jhb = datetime.now(jhb_tz)
    now_ny = datetime.now(ny_tz)
    
    day_ny = now_ny.weekday() 
    hour_ny = now_ny.hour
    
    status, color = "OPEN / ACTIVE", "green"
    
    # Gold (GC=F) Market Hours
    if day_ny == 5 or (day_ny == 4 and hour_ny >= 17) or (day_ny == 6 and hour_ny < 18):
        status, color = "CLOSED (Weekend)", "red"
    elif hour_ny == 17:
        status, color = "DAILY BREAK", "orange"
        
    return now_jhb, status, color

now_jhb, m_status, m_color = get_market_info()

# --- 3. SIDEBAR CONFIG ---
st.sidebar.header("Configuration")
symbol = st.sidebar.text_input("Asset (Gold = GC=F)", value="GC=F")
tf_choice = st.sidebar.selectbox("Select Timeframe", ("1h", "4h", "1d"), index=0)

# --- 4. HEADER ---
col_h1, col_h2 = st.columns([2, 1])
with col_h1:
    st.title("🥇 Gold T.L.S. Master")
    st.subheader(f"{symbol} | {tf_choice.upper()} Timeframe")
with col_h2:
    st.write(f"📍 **JHB Time:** {now_jhb.strftime('%H:%M:%S')}")
    st.markdown(f"**Market Status:** :{m_color}[{m_status}]")

st.divider()

# --- 5. DATA ENGINE ---
@st.cache_data(ttl=60)
def load_data(ticker_str, tf):
    try:
        df = yf.download(ticker_str, period="60d", interval=tf, auto_adjust=True)
        return df
    except: return pd.DataFrame()

data = load_data(symbol, tf_choice)

# --- 6. MAIN LAYOUT (Signals & News) ---
col_main, col_news = st.columns([2, 1])

with col_main:
    if not data.empty:
        # Clean column names
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.get_level_values(0)

        # 21 SMA (Trend Rule from the Book)
        data['SMA21'] = data['Close'].rolling(window=21).mean()
        curr, prev = data.iloc[-1], data.iloc[-2]
        
        # Strategy Logic (The Signal)
        def detect_signals(c, p):
            o, h, l, cl = float(c['Open']), float(c['High']), float(c['Low']), float(c['Close'])
            po, pc = float(p['Open']), float(p['Close'])
            tr = h - l
            if tr == 0: return None
            body = abs(o - cl)
            l_shadow, u_shadow = (min(o, cl) - l), (h - max(o, cl))
            
            # Pattern rules from the Candlestick Bible
            if l_shadow > (body * 2) and u_shadow < (body * 0.5): return "Bullish Pin Bar"
            if u_shadow > (body * 2) and l_shadow < (body * 0.5): return "Bearish Pin Bar"
            if (cl > o) and (pc < po) and (cl >= po): return "Bullish Engulfing"
            if (cl < o) and (pc > po) and (cl <= po): return "Bearish Engulfing"
            return None

        signal = detect_signals(curr, prev)
        price, sma = float(curr['Close']), float(curr['SMA21'])
        is_uptrend = price > sma

        # Main Metrics
        m1, m2, m3 = st.columns(3)
        m1.metric("Live Price", f"${price:,.2f}")
        m2.metric("Trend (21 SMA)", "UP" if is_uptrend else "DOWN")
        m3.metric("Chart", tf_choice.upper())

        if signal:
            confluence = (is_uptrend and "Bullish" in signal) or (not is_uptrend and "Bearish" in signal)
            card_style = "signal-card success-card" if confluence else "signal-card"
            st.markdown(f"""
                <div class="{card_style}">
                    <h2>🎯 SIGNAL: {signal}</h2>
                    <h3>{'✅ T.L.S. MATCHED (HIGH PROBABILITY)' if confluence else '⚠️ COUNTER-TREND'}</h3>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info(f"🔎 Scanning {tf_choice.upper()} chart for Bible patterns...")
            
        with st.expander("Show Technical Table"):
            st.dataframe(data.tail(5))
    else:
        st.error("Waiting for market data connection...")

# --- 7. NEWS ENGINE (CNBC Investing RSS) ---
with col_news:
    st.subheader("📰 Global Market News")
    try:
        # Using a direct RSS feed for better reliability on mobile
        feed = feedparser.parse("https://search.cnbc.com/rs/search/combined/rss/rss.html?query=gold%20market")
        if feed.entries:
            for entry in feed.entries[:10]:
                st.markdown(f"""
                <div class="news-card">
                    <b><a href="{entry.link}" target="_blank">{entry.title}</a></b><br>
                    <small>Source: CNBC Business</small>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.write("Checking alternative news sources...")
    except:
        st.write("News currently unavailable due to network timeout.")
