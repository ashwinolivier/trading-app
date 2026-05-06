import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime
import pytz

# --- APP CONFIG ---
st.set_page_config(page_title="Gold T.L.S. Pro", layout="wide")

# --- CUSTOM STYLING ---
st.markdown("""
    <style>
    .stMetric { background-color: #1e2130; padding: 15px; border-radius: 10px; border: 1px solid #3e4255; }
    .signal-card { padding: 20px; border-radius: 15px; border-left: 10px solid #f63366; background-color: #262730; margin-bottom: 20px; }
    .success-card { border-left: 10px solid #00ffcc; }
    </style>
    """, unsafe_allow_html=True)

# --- MARKET CLOCK (JHB TIME) ---
def get_market_info():
    jhb_tz = pytz.timezone('Africa/Johannesburg')
    ny_tz = pytz.timezone('America/New_York')
    now_jhb = datetime.now(jhb_tz)
    now_ny = datetime.now(ny_tz)
    
    day_ny = now_ny.weekday() 
    hour_ny = now_ny.hour
    
    # Gold Market (GC=F) Logic
    status, color = "OPEN", "green"
    if day_ny == 5 or (day_ny == 4 and hour_ny >= 17) or (day_ny == 6 and hour_ny < 18):
        status, color = "CLOSED", "red"
    elif hour_ny == 17:
        status, color = "DAILY BREAK", "orange"
        
    return now_jhb, status, color

now_jhb, m_status, m_color = get_market_info()

# --- HEADER ---
st.title("🥇 Simple Gold Scanner")
col_h1, col_h2 = st.columns([2, 1])
with col_h1:
    st.write(f"**Market Status:** :{m_color}[{m_status}]")
with col_h2:
    st.write(f"📍 **JHB:** {now_jhb.strftime('%H:%M:%S')}")

# --- SIDEBAR SETTINGS ---
symbol = st.sidebar.text_input("Ticker", value="GC=F")
tf = st.sidebar.selectbox("Timeframe", ("1h", "4h", "1d"), index=1)

# --- DATA ENGINE ---
@st.cache_data(ttl=60)
def load_data(ticker, timeframe):
    df = yf.download(ticker, period="60d", interval=timeframe, auto_adjust=True)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    return df

data = load_data(symbol, tf)

if not data.empty:
    # 21 SMA Trend
    data['SMA21'] = data['Close'].rolling(window=21).mean()
    c, p = data.iloc[-1], data.iloc[-2]
    
    # Prices & Logic
    o, h, l, cl = float(c['Open']), float(c['High']), float(c['Low']), float(c['Close'])
    po, pc = float(p['Open']), float(p['Close'])
    sma = float(c['SMA21'])
    
    # Pattern Logic
    body, tr = abs(o - cl), (h - l)
    l_shadow, u_shadow = (min(o, cl) - l), (h - max(o, cl))
    
    signal = None
    if l_shadow > (body * 2): signal = "Bullish Pin Bar"
    elif u_shadow > (body * 2): signal = "Bearish Pin Bar"
    elif (cl > o) and (pc < po) and (cl >= po): signal = "Bullish Engulfing"
    elif (cl < o) and (pc > po) and (cl <= po): signal = "Bearish Engulfing"

    is_uptrend = cl > sma
    confluence = (is_uptrend and "Bullish" in str(signal)) or (not is_uptrend and "Bearish" in str(signal))

    # --- DISPLAY ---
    m1, m2, m3 = st.columns(3)
    m1.metric("Live Price", f"${cl:.2f}")
    m2.metric("Trend", "UP" if is_uptrend else "DOWN")
    m3.metric("Timeframe", tf.upper())

    if signal:
        # Calculate SL and TP (1:2 Risk/Reward)
        if "Bullish" in signal:
            entry = h + 0.25 # Buffer for spread
            sl = l - 0.25
            tp = entry + ((entry - sl) * 2)
        else:
            entry = l - 0.25
            sl = h + 0.25
            tp = entry - ((sl - entry) * 2)

        card_class = "signal-card success-card" if confluence else "signal-card"
        st.markdown(f"""
            <div class="{card_class}">
                <h2>🎯 {signal} Found</h2>
                <p>Status: {'<b>T.L.S. MATCHED</b>' if confluence else 'Counter-Trend'}</p>
            </div>
            """, unsafe_allow_html=True)
        
        st.subheader("📋 Trade Instructions")
        i1, i2, i3 = st.columns(3)
        i1.metric("BUY/SELL STOP", f"{entry:.2f}")
        i2.metric("STOP LOSS", f"{sl:.2f}")
        i3.metric("TAKE PROFIT", f"{tp:.2f}")
    else:
        st.info(f"🔎 Scanning the **{tf}** chart for Bible patterns...")

    with st.expander("Recent Data History"):
        st.dataframe(data.tail(5))
else:
    st.error("No data found. If it's the weekend, the price will not update.")
