import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="Candlestick Bible Signals", layout="wide")
st.title("🥇 Gold & Forex Signal Scanner")

# --- SIDEBAR SETTINGS ---
st.sidebar.header("Settings")

# Set GC=F (Gold) as the default text input
symbol = st.sidebar.text_input("Ticker Symbol", value="GC=F")

# Set 1h as the default index for the select box
# index=0 corresponds to the first item in the list ["1h", "4h", "1d"]
timeframe = st.sidebar.selectbox("Timeframe", ("1h", "4h", "1d"), index=0)

st.sidebar.info("As per the book: Focus on 1H, 4H, and Daily for reliable T.L.S. signals.")

# --- DATA FETCHING ---
@st.cache_data(ttl=300) # Caches data for 5 minutes to keep the app fast
def load_data(ticker, tf):
    return yf.download(ticker, period="60d", interval=tf)

data = load_data(symbol, timeframe)

if not data.empty:
    # 1. THE TREND (21 SMA)
    # The book uses the 21-period SMA to determine the dominant market direction
    data['SMA21'] = data['Close'].rolling(window=21).mean()
    
    current = data.iloc[-1]
    prev = data.iloc[-2]
    
    # 2. THE SIGNAL LOGIC (Pin Bar & Engulfing)
    def detect_signals(curr, p):
        total_range = curr['High'] - curr['Low']
        body_size = abs(curr['Open'] - curr['Close'])
        lower_shadow = min(curr['Open'], curr['Close']) - curr['Low']
        upper_shadow = curr['High'] - max(curr['Open'], curr['Close'])
        
        # Pin Bar: Shadow is at least 2/3 (66%) of the candle
        is_bull_pin = lower_shadow > (total_range * 0.66)
        is_bear_pin = upper_shadow > (total_range * 0.66)
        
        # Engulfing: Current body consumes previous body
        is_bull_engulf = (curr['Close'] > curr['Open']) and (p['Close'] < p['Open']) and (curr['Close'] >= p['Open']) and (curr['Open'] <= p['Close'])
        is_bear_engulf = (curr['Close'] < curr['Open']) and (p['Close'] > p['Open']) and (curr['Close'] <= p['Open']) and (curr['Open'] >= p['Close'])
        
        if is_bull_pin: return "Bullish Pin Bar"
        if is_bear_pin: return "Bearish Pin Bar"
        if is_bull_engulf: return "Bullish Engulfing"
        if is_bear_engulf: return "Bearish Engulfing"
        return None

    signal = detect_signals(current, prev)
    
    # 3. THE TREND CHECK (T.L.S. Rule)
    # Is the price above or below the 21 SMA?
    is_uptrend = current['Close'] > current['SMA21']
    trend_text = "UPTREND" if is_uptrend else "DOWNTREND"
    
    # --- DASHBOARD DISPLAY ---
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric(label=f"Current {symbol} Price", value=f"{current['Close']:.2f}")
        st.write(f"**Market Trend:** {trend_text}")

    with col2:
        if signal:
            st.header(f"Signal: {signal}")
            # Logic for Confluence (Signal + Trend)
            if (is_uptrend and "Bullish" in signal) or (not is_uptrend and "Bearish" in signal):
                st.success("✅ **HIGH PROBABILITY SETUP**")
                st.write("The Signal matches the Trend (T.L.S. Confirmed). Look for Support/Resistance levels to enter.")
            else:
                st.warning("⚠️ **COUNTER-TREND SIGNAL**")
                st.write("The book advises caution. This signal is against the dominant trend.")
        else:
            st.info("No primary candlestick patterns detected on the current candle.")

    # Show the chart data for reference
    with st.expander("View Raw Data"):
        st.dataframe(data.tail(10))

else:
    st.error("No data found. Please check the Ticker Symbol (e.g., GC=F for Gold).")
