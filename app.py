import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime
import pytz

# --- APP CONFIGURATION ---
st.set_page_config(page_title="Gold T.L.S. Scanner", layout="wide")

# --- TIMEZONE & MARKET CLOCK LOGIC ---
def get_market_info():
    jhb_tz = pytz.timezone('Africa/Johannesburg')
    ny_tz = pytz.timezone('America/New_York')
    now_jhb = datetime.now(jhb_tz)
    now_ny = datetime.now(ny_tz)
    
    day_ny = now_ny.weekday() 
    hour_ny = now_ny.hour
    
    status = "OPEN / ACTIVE"
    color = "green"
    
    if day_ny == 5 or (day_ny == 4 and hour_ny >= 17) or (day_ny == 6 and hour_ny < 18):
        status, color = "CLOSED (Weekend)", "red"
    elif hour_ny == 17:
        status, color = "CLOSED (Daily Break)", "orange"
        
    return now_jhb, status, color

now_jhb, status, color = get_market_info()

# --- UI HEADER ---
st.title("🥇 Gold T.L.S. Signal Scanner")
st.write(f"**Johannesburg Time:** {now_jhb.strftime('%H:%M:%S')}")
st.markdown(f"**Market Status:** :{color}[{status}]")

# --- SIDEBAR ---
st.sidebar.header("Settings")
symbol = st.sidebar.text_input("Ticker Symbol", value="GC=F")
timeframe = st.sidebar.selectbox("Timeframe", ("1h", "4h", "1d"), index=0)

# --- DATA ENGINE ---
@st.cache_data(ttl=60)
def load_data(ticker, tf):
    try:
        df = yf.download(ticker, period="60d", interval=tf, auto_adjust=True)
        return df
    except:
        return pd.DataFrame()

data = load_data(symbol, timeframe)

if not data.empty:
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(0)

    # 1. THE TREND (21 SMA)
    data['SMA21'] = data['Close'].rolling(window=21).mean()
    
    def detect_patterns(curr, p):
        o, h, l, c = float(curr['Open']), float(curr['High']), float(curr['Low']), float(curr['Close'])
        po, ph, pl, pc = float(p['Open']), float(p['High']), float(p['Low']), float(p['Close'])
        
        tr = h - l 
        if tr == 0: return None
        
        body_size = abs(o - c)
        lower_shadow = min(o, c) - l
        upper_shadow = h - max(o, c)
        
        # --- Adjusted Pin Bar Logic (The "Bible" Hammer/Shooting Star) ---
        # Tail should be at least 2x the body size (relaxed from 66% total range)
        if lower_shadow > (body_size * 2) and upper_shadow < (body_size * 0.5):
            return "Bullish Pin Bar"
        if upper_shadow > (body_size * 2) and lower_shadow < (body_size * 0.5):
            return "Bearish Pin Bar"
        
        # --- Engulfing Bar Logic ---
        is_bull_engulf = (c > o) and (pc < po) and (c >= po) and (o <= pc)
        is_bear_engulf = (c < o) and (pc > po) and (c <= po) and (o >= pc)
        
        if is_bull_engulf: return "Bullish Engulfing"
        if is_bear_engulf: return "Bearish Engulfing"
        
        return None

    # --- SCANNING RECENT CANDLES ---
    # Instead of just the last candle, we check the last 3 candles to see if a signal JUST happened
    signals_found = []
    for i in range(1, 4):
        sig = detect_patterns(data.iloc[-i], data.iloc[-(i+1)])
        if sig:
            signals_found.append((data.index[-i], sig))

    curr_close = float(data.iloc[-1]['Close'])
    curr_sma = float(data.iloc[-1]['SMA21'])
    is_uptrend = curr_close > curr_sma

    # --- DASHBOARD ---
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric(label=f"{symbol} Price", value=f"{curr_close:.2f}")
        trend_text = "📈 UPTREND" if is_uptrend else "📉 DOWNTREND"
        st.write(f"Trend Direction: **{trend_text}**")
        st.write("*(Price relative to 21 SMA)*")

    with col2:
        if signals_found:
            last_time, last_sig = signals_found[0]
            st.success(f"**SIGNAL FOUND:** {last_sig}")
            st.write(f"Detected at: {last_time.strftime('%H:%M')}")
            
            # T.L.S. Check
            if (is_uptrend and "Bullish" in last_sig) or (not is_uptrend and "Bearish" in last_sig):
                st.markdown("### ✅ **T.L.S. CONFIRMED**")
                st.write("This is a high-probability trade according to the book.")
            else:
                st.warning("⚠️ **COUNTER-TREND**")
        else:
            st.info("🔎 **Scanning...** No perfect Pin Bar or Engulfing patterns on the last 3 candles.")
            st.write("The book teaches that 'no trade' is a trade. Wait for a clear rejection at a level.")

    # --- VISUAL CANDLE CHECK (So you know it's working) ---
    with st.expander("Recent Analysis Logs"):
        st.write("Latest Candle Ratios:")
        c = data.iloc[-1]
        tr = c['High']-c['Low']
        ls = min(c['Open'], c['Close'])-c['Low']
        us = c['High']-max(c['Open'], c['Close'])
        st.write(f"- Lower Shadow: {((ls/tr)*100 if tr>0 else 0):.1f}% of candle")
        st.write(f"- Upper Shadow: {((us/tr)*100 if tr>0 else 0):.1f}% of candle")
        st.dataframe(data.tail(5))

else:
    st.error("No data available.")
