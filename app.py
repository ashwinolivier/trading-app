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
    st.title("🥇 Gold T.L.S. Scanner")
    st.subheader(f"Current View: {symbol} | {tf_choice.upper()} Timeframe")
with col_h2:
    st.write(f"📍 **JHB:** {now_jhb.strftime('%H:%M:%S')}")
    st.markdown(f"**Market Status:** :{m_color}[{m_status}]")

st.divider()

# --- DATA ENGINE ---
@st.cache_data(ttl=60)
def load_data(ticker, tf):
    try:
        df = yf.download(ticker, period="60d", interval=tf, auto_adjust=True)
        return df
    except: return pd.DataFrame()

data = load_data(symbol, tf_choice)

if not data.empty:
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(0)

    # 1. THE TREND (21 SMA)
    data['SMA21'] = data['Close'].rolling(window=21).mean()
    curr = data.iloc[-1]
    prev = data.iloc[-2]
    
    # 2. PATTERN LOGIC
    def detect_signals(c, p):
        o, h, l, cl = float(c['Open']), float(c['High']), float(c['Low']), float(c['Close'])
        po, pc = float(p['Open']), float(p['Close'])
        tr = h - l
        if tr == 0: return None
        body = abs(o - cl)
        l_shadow = min(o, cl) - l
        u_shadow = h - max(o, cl)
        
        # Pin Bar
        if l_shadow > (body * 2) and u_shadow < (body * 0.5): return "Bullish Pin Bar"
        if u_shadow > (body * 2) and l_shadow < (body * 0.5): return "Bearish Pin Bar"
        
        # Engulfing
        if (cl > o) and (pc < po) and (cl >= po): return "Bullish Engulfing"
        if (cl < o) and (pc > po) and (cl <= po): return "Bearish Engulfing"
        
        return None

    signal = detect_signals(curr, prev)
    price = float(curr['Close'])
    sma = float(curr['SMA21'])
    is_uptrend = price > sma

    # --- MAIN DASHBOARD ---
    m_col1, m_col2, m_col3 = st.columns(3)
    m_col1.metric("Live Price", f"${price:,.2f}")
    m_col2.metric("21 SMA Trend", "UP" if is_uptrend else "DOWN", delta="Trending" if is_uptrend else "-Trending")
    m_col3.metric("Selected TF", tf_choice.upper())

    st.write("---")

    if signal:
        # Use HTML for a better looking Signal Card
        confluence = (is_uptrend and "Bullish" in signal) or (not is_uptrend and "Bearish" in signal)
        card_class = "signal-card success-card" if confluence else "signal-card"
        
        st.markdown(f"""
            <div class="{card_class}">
                <h2>🎯 Signal: {signal}</h2>
                <p>Detected on the <b>{tf_choice.upper()}</b> chart.</p>
                <h3>{'✅ T.L.S. MATCHED' if confluence else '⚠️ COUNTER-TREND'}</h3>
            </div>
            """, unsafe_allow_html=True)
        
        if confluence:
            st.balloons()
            st.info("**Instruction:** Look at your MT4/MT5 for a Key Support/Resistance Level. If this signal is sitting ON a level, prepare for entry.")
    else:
        st.info(f"🔎 Scanning the **{tf_choice.upper()}** timeframe for Pin Bars and Engulfing patterns...")

    # --- RECENT PRICE ACTION ---
    with st.expander("Show Recent Price History"):
        st.dataframe(data.tail(10).style.highlight_max(axis=0, subset=['High'], color='#00ffcc22'))

else:
    st.error("Data unreachable. Check your internet or Ticker symbol.")
