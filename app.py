import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime
import pytz

# --- APP CONFIGURATION ---
st.set_page_config(page_title="Gold T.L.S. Scanner", layout="wide")

# --- TIMEZONE & MARKET CLOCK LOGIC ---
def get_market_info():
    # Setup Timezones
    jhb_tz = pytz.timezone('Africa/Johannesburg')
    ny_tz = pytz.timezone('America/New_York')
    
    now_jhb = datetime.now(jhb_tz)
    now_ny = datetime.now(ny_tz)
    
    # Gold (GC=F) Hours in NY Time: 
    # Opens Sunday 18:00, Closes Friday 17:00. Break daily 17:00-18:00.
    day_ny = now_ny.weekday() 
    hour_ny = now_ny.hour
    
    status = "OPEN / ACTIVE"
    color = "green"
    
    # Weekend Check
    if day_ny == 5: # Saturday
        status, color = "CLOSED (Weekend)", "red"
    elif day_ny == 4 and hour_ny >= 17: # Friday post-close
        status, color = "CLOSED (Weekend)", "red"
    elif day_ny == 6 and hour_ny < 18: # Sunday pre-open
        status, color = "CLOSED (Weekend)", "red"
    # Daily Break Check
    elif hour_ny == 17:
        status, color = "CLOSED (Daily Break)", "orange"
        
    return now_jhb, status, color

now_jhb, status, color = get_market_info()

# --- UI HEADER ---
st.title("🥇 Gold T.L.S. Signal Scanner")
st.write(f"**Johannesburg Time:** {now_jhb.strftime('%Y-%m-%d %H:%M:%S')}")
st.markdown(f"**Market Status:** :{color}[{status}]")

# --- SIDEBAR SETTINGS ---
st.sidebar.header("Strategy Settings")
symbol = st.sidebar.text_input("Ticker Symbol", value="GC=F")
timeframe = st.sidebar.selectbox("Timeframe", ("1h", "4h", "1d"), index=0)

st.sidebar.markdown("""
---
**The Candlestick Trading Bible Rules:**
1. **Trend:** Price vs 21 SMA.
2. **Level:** Signal must be at Support/Resistance.
3. **Signal:** Pin Bar or Engulfing Bar.
""")

# --- DATA ENGINE ---
@st.cache_data(ttl=60)
def load_data(ticker, tf):
    try:
        # auto_adjust=True ensures we get OHLC data for candle patterns
        df = yf.download(ticker, period="60d", interval=tf, auto_adjust=True)
        return df
    except Exception as e:
        return pd.DataFrame()

data = load_data(symbol, timeframe)

if not data.empty:
    # Clean up column names if they are MultiIndex
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(0)

    # 1. THE TREND (21 SMA)
    data['SMA21'] = data['Close'].rolling(window=21).mean()
    
    # Extract the last two candles for analysis
    current_candle = data.iloc[-1]
    prev_candle = data.iloc[-2]
    
    # 2. THE SIGNAL LOGIC (Function to detect patterns)
    def detect_patterns(curr, p):
        # Convert to float to avoid pandas Series errors
        o, h, l, c = float(curr['Open']), float(curr['High']), float(curr['Low']), float(curr['Close'])
        po, pc = float(p['Open']), float(p['Close'])
        
        tr = h - l # Total Range
        if tr == 0: return None
        
        body_size = abs(o - c)
        lower_shadow = min(o, c) - l
        upper_shadow = h - max(o, c)
        
        # --- Pin Bar Logic ---
        # Rule: Tail is at least 2/3 (66%) of the total candle range
        if lower_shadow > (tr * 0.66): return "Bullish Pin Bar"
        if upper_shadow > (tr * 0.66): return "Bearish Pin Bar"
        
        # --- Engulfing Bar Logic ---
        # Rule: Current body fully covers previous body
        is_bull_engulf = (c > o) and (pc < po) and (c >= po) and (o <= pc)
        is_bear_engulf = (c < o) and (pc > po) and (c <= po) and (o >= pc)
        
        if is_bull_engulf: return "Bullish Engulfing"
        if is_bear_engulf: return "Bearish Engulfing"
        
        return None

    # --- EXECUTE STRATEGY ---
    signal = detect_patterns(current_candle, prev_candle)
    curr_close = float(current_candle['Close'])
    curr_sma = float(current_candle['SMA21'])
    is_uptrend = curr_close > curr_sma

    # --- DASHBOARD ---
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric(label=f"{symbol} Price", value=f"{curr_close:.2f}")
        trend_label = "📈 UPTREND" if is_uptrend else "📉 DOWNTREND"
        st.write(f"Trend (21 SMA): **{trend_label}**")

    with col2:
        if signal:
            st.subheader(f"Signal: {signal}")
            # Check for T.L.S. Confluence
            if (is_uptrend and "Bullish" in signal) or (not is_uptrend and "Bearish" in signal):
                st.success("✅ **HIGH PROBABILITY SETUP (T.L.S.)**")
                st.write("Confluence: Signal matches the 21 SMA Trend. Check for Key Levels.")
            else:
                st.warning("⚠️ **COUNTER-TREND SIGNAL**")
                st.write("Warning: This signal is against the dominant trend.")
        else:
            st.info("Searching for Candlestick Patterns...")

    # Chart Data Table
    with st.expander("Recent Candle Data"):
        st.dataframe(data.tail(10))

else:
    st.error("Unable to fetch data. If the market is closed, some symbols may not provide data.")
