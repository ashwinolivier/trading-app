import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="Candlestick Bible Signals", layout="wide")
st.title("📖 Candlestick Bible Signal App")

# 1. Sidebar Setup
symbol = st.sidebar.text_input("Ticker (e.g., EURUSD=X, BTC-USD, AAPL)", "EURUSD=X")
timeframe = st.sidebar.selectbox("Timeframe", ("1h", "4h", "1d"), index=2)

# 2. Fetch and Clean Data
@st.cache_data(ttl=300)
def load_data(ticker, tf):
    df = yf.download(ticker, period="60d", interval=tf)
    # Fix for Multi-Index Columns
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    return df

data = load_data(symbol, timeframe)

if not data.empty:
    # Calculate 21 SMA (The Trend filter from the book)
    data['SMA21'] = data['Close'].rolling(window=21).mean()
    
    # Get the two most recent complete candles
    current = data.iloc[-1]
    prev = data.iloc[-2]
    
    # 3. Pattern Detection (The Signal)
    def detect_signals(curr, p):
        signals = []
        
        # Anatomy of the candle
        range_tot = curr['High'] - curr['Low']
        body = abs(curr['Open'] - curr['Close'])
        lower_shadow = min(curr['Open'], curr['Close']) - curr['Low']
        upper_shadow = curr['High'] - max(curr['Open'], curr['Close'])
        
        # PIN BAR (Rejection of price)
        if lower_shadow > (range_tot * 0.66):
            signals.append("Bullish Pin Bar")
        elif upper_shadow > (range_tot * 0.66):
            signals.append("Bearish Pin Bar")
            
        # ENGULFING BAR
        if curr['Close'] > curr['Open'] and p['Close'] < p['Open']:
            if curr['Close'] > p['Open'] and curr['Open'] < p['Close']:
                signals.append("Bullish Engulfing")
        elif curr['Close'] < curr['Open'] and p['Close'] > p['Open']:
            if curr['Close'] < p['Open'] and curr['Open'] > p['Close']:
                signals.append("Bearish Engulfing")
                
        return signals

    found_signals = detect_signals(current, prev)
    
    # 4. Trend Determination (The Trend)
    trend = "UPTREND" if current['Close'] > current['SMA21'] else "DOWNTREND"
    
    # 5. Display Interface
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Current Price", f"{current['Close']:.4f}")
        st.write(f"**Market Structure:** {trend} (Price vs 21 SMA)")

    with col2:
        if found_signals:
            for s in found_signals:
                st.success(f"🎯 SIGNAL: {s}")
                # TLS Check: Trend - Level - Signal
                if ("Bullish" in s and trend == "UPTREND") or ("Bearish" in s and trend == "DOWNTREND"):
                    st.info("✅ **T.L.S. Confluence:** This signal aligns with the trend.")
                else:
                    st.warning("⚠️ **Counter-Trend:** Trade with caution.")
        else:
            st.info("No clear candlestick signals detected. Wait for a setup at a Key Level.")

    # Show raw data for transparency
    with st.expander("View Recent Price Action"):
        st.dataframe(data.tail(5))
else:
    st.error("Could not fetch data. Please check the ticker symbol.")
