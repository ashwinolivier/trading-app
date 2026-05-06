import streamlit as st
import yfinance as yf
import pandas as pd

st.title("Candlestick Bible Signals")

# 1. Inputs
symbol = st.sidebar.text_input("Ticker (e.g., EURUSD=X, AAPL)", "EURUSD=X")
timeframe = st.sidebar.selectbox("Timeframe", ("1h", "4h", "1d"))

# 2. Fetch Data
data = yf.download(symbol, period="60d", interval=timeframe)

if not data.empty:
    # Calculate 21 SMA (The Trend - as per the book)
    data['SMA21'] = data['Close'].rolling(window=21).mean()
    
    current = data.iloc[-1]
    prev = data.iloc[-2]
    
    # 3. The Signal Logic (Pin Bar & Engulfing)
    def get_signal(curr, p):
        # Pin Bar logic
        total_range = curr['High'] - curr['Low']
        lower_shadow = min(curr['Open'], curr['Close']) - curr['Low']
        upper_shadow = curr['High'] - max(curr['Open'], curr['Close'])
        
        # Engulfing logic
        is_bullish_engulfing = (curr['Close'] > curr['Open']) and (p['Close'] < p['Open']) and (curr['Close'] > p['Open']) and (curr['Open'] < p['Close'])
        
        if lower_shadow > (total_range * 0.66): return "Bullish Pin Bar"
        if upper_shadow > (total_range * 0.66): return "Bearish Pin Bar"
        if is_bullish_engulfing: return "Bullish Engulfing"
        return None

    signal = get_signal(current, prev)
    
    # 4. The Trend Check (T.L.S. Rule)
    trend = "UP" if current['Close'] > current['SMA21'] else "DOWN"
    
    # 5. Output
    st.metric("Price", f"{current['Close']:.4f}")
    st.write(f"**Current Trend:** {trend}")
    
    if signal:
        st.success(f"**SIGNAL DETECTED:** {signal}")
        if (trend == "UP" and "Bullish" in signal) or (trend == "DOWN" and "Bearish" in signal):
            st.write("✅ **T.L.S. Confirmed:** Signal aligns with Trend.")
        else:
            st.warning("⚠️ **Caution:** Signal against Trend.")
    else:
        st.info("Searching for patterns at key levels...")