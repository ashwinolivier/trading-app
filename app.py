import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime
import pytz

# --- 1. APP CONFIG ---
st.set_page_config(page_title="Gold T.L.S. Pro", layout="wide")

# --- 2. THE REFRESH LOGIC ---
# This line makes the app automatically rerun every 5 minutes (300,000 milliseconds)
# If you haven't installed 'streamlit-autorefresh', you can just use a manual button.
# To keep it simple and avoid extra installs, we use the st.button + cache TTL.

# --- 3. MARKET CLOCK ---
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
        status, color = "DAILY BREAK", "orange"
        
    return now_jhb, status, color

now_jhb, m_status, m_color = get_market_info()

# --- 4. HEADER & REFRESH BUTTON ---
st.title("🥇 Gold T.L.S. Scanner")

col_header, col_btn = st.columns([3, 1])
with col_header:
    st.write(f"**Status:** :{m_color}[{m_status}] | 📍 **JHB:** {now_jhb.strftime('%H:%M:%S')}")

with col_btn:
    # Manual Refresh Button
    if st.button("🔄 Refresh Data"):
        st.cache_data.clear() # Clears old data so it pulls fresh from Yahoo
        st.rerun()

st.divider()

# --- 5. SIDEBAR ---
symbol = st.sidebar.text_input("Ticker", value="GC=F")
tf = st.sidebar.selectbox("Timeframe", ("1h", "4h", "1d"), index=1)

# --- 6. DATA ENGINE ---
@st.cache_data(ttl=300) # Data "expires" every 5 minutes
def load_data(ticker, timeframe):
    df = yf.download(ticker, period="60d", interval=timeframe, auto_adjust=True)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    return df

data = load_data(symbol, tf)

if not data.empty:
    data['SMA21'] = data['Close'].rolling(window=21).mean()
    c = data.iloc[-1]
    p = data.iloc[-2]
    
    # Values
    cl, sma = float(c['Close']), float(c['SMA21'])
    o, h, l = float(c['Open']), float(c['High']), float(c['Low'])
    po, pc = float(p['Open']), float(p['Close'])
    
    # Patterns
    body, tr = abs(o - cl), (h - l)
    l_shad, u_shad = (min(o, cl) - l), (h - max(o, cl))
    
    signal = None
    if l_shad > (body * 2): signal = "Bullish Pin Bar"
    elif u_shad > (body * 2): signal = "Bearish Pin Bar"
    elif (cl > o) and (pc < po) and (cl >= po): signal = "Bullish Engulfing"
    elif (cl < o) and (pc > po) and (cl <= po): signal = "Bearish Engulfing"

    is_uptrend = cl > sma
    confluence = (is_uptrend and "Bullish" in str(signal)) or (not is_uptrend and "Bearish" in str(signal))

    # --- 7. DISPLAY ---
    m1, m2, m3 = st.columns(3)
    m1.metric("Live Price", f"${cl:.2f}")
    m2.metric("Trend", "UP" if is_uptrend else "DOWN")
    m3.metric("Timeframe", tf.upper())

    if signal:
        if "Bullish" in signal:
            entry, sl = h + 0.25, l - 0.25
            tp = entry + ((entry - sl) * 2)
        else:
            entry, sl = l - 0.25, h + 0.25
            tp = entry - ((sl - entry) * 2)

        st.markdown(f"### 🎯 {signal}")
        if confluence:
            st.success("✅ **T.L.S. CONFIRMED**")
        
        st.subheader("📋 Trade Plan")
        i1, i2, i3 = st.columns(3)
        i1.metric("ENTRY", f"{entry:.2f}")
        i2.metric("STOP LOSS", f"{sl:.2f}")
        i3.metric("TAKE PROFIT", f"{tp:.2f}")
    else:
        st.info(f"🔎 Monitoring {tf} for patterns...")

else:
    st.error("Market data currently unavailable.")
