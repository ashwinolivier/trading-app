import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="Candlestick Bible Signals", layout="wide")
st.title("🥇 Gold & Forex Signal Scanner")

# --- SIDEBAR SETTINGS ---
st.sidebar.header("Settings")
symbol = st.sidebar.text_input("Ticker Symbol", value="GC=F")
timeframe = st.sidebar.selectbox("Timeframe", ("1h", "4h", "1d"), index=0)

st.sidebar.info("Strategy: T.L.S. (Trend, Level, Signal) as taught in the Candlestick Trading Bible.")

# --- DATA FETCHING ---
@st.cache_data(ttl=300)
def load_data(ticker, tf):
    # we use auto_adjust=True to ensure we have clean Open/High/Low/Close columns
    df = yf.download(ticker, period="60d", interval=tf, auto_adjust=True)
    return df

data = load_data(symbol, timeframe)

if not data.empty:
    # Handle potential multi-index columns from yfinance
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(0)

    # 1. THE TREND (21 SMA)
    data['SMA21'] = data['Close'].rolling(window=21).mean()
    
    # Get the two most recent candles
    current = data.iloc[-1]
    prev = data.iloc[-2]
    
    # 2. THE SIGNAL LOGIC (Pin Bar & Engulfing)
    def detect_signals(curr, p):
        # Extract values as floats to prevent the ValueError
        c_open, c_high, c_low, c_close = float(curr['Open']), float(curr['High']), float(curr['Low']), float(curr['Close'])
        p_open, p_close = float(p['Open']), float(p['Close'])
        
        total_range = c_high - c_low
        if total_range == 0: return None
        
        body_size = abs(c_open - c_close)
        lower_shadow = min(c_open, c_close) - c_low
        upper_shadow = c_high - max(c_open, c_close)
        
        # --- Pin Bar (The 'Hammer' or 'Shooting Star' in the book) ---
        # Rule: Shadow is at least 2/3 (66%) of the candle
        is_bull_pin = lower_shadow > (total_range * 0.66)
        is_bear_pin = upper_shadow > (total_range * 0.66)
        
        # --- Engulfing Bar ---
        # Rule: Current body fully consumes the previous body
        is_bull_engulf = (c_close > c_open) and (p_close < p_open) and (c_close >= p_open) and (c_open <= p_close)
        is_bear_engulf = (c_close < c_open) and (p_close > p_open) and (c_close <= p_open) and (c_open >= p_close)
        
        if is_bull_pin: return "Bullish Pin Bar"
        if is_bear_pin: return "Bearish Pin Bar"
        if is_bull_engulf: return "Bullish Engulfing"
        if is_bear_engulf: return "Bearish Engulfing"
        return None

    signal = detect_signals(current, prev)
    
    # 3. THE TREND CHECK (T.L.S. Rule)
    curr_close = float(current['Close'])
    curr_sma = float(current['SMA21'])
    is_uptrend = curr_close > curr_sma
    trend_text = "UPTREND" if is_uptrend else "DOWNTREND"
    
    # --- DASHBOARD DISPLAY ---
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric(label=f"Current {symbol} Price", value=f"{curr_close:.2f}")
        st.write(f"**Market Trend (21 SMA):** {trend_text}")

    with col2:
        if signal:
            st.header(f"Signal: {signal}")
            # Check for Confluence
            if (is_uptrend and "Bullish" in signal) or (not is_uptrend and "Bearish" in signal):
                st.success("✅ **HIGH PROBABILITY SETUP (T.L.S.)**")
                st.write("The signal aligns with the trend. Check for Support/Resistance levels.")
            else:
                st.warning("⚠️ **COUNTER-TREND SIGNAL**")
                st.write("The book advises caution. This signal is against the 21 SMA trend.")
        else:
            st.info("No primary candlestick patterns detected on the latest candle.")

    # Show chart-like view of data
    with st.expander("View Recent Data"):
        st.dataframe(data.tail(5))
else:
    st.error("No data found. Please check your Ticker Symbol.")
