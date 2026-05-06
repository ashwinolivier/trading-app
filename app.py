import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime
import pytz

# --- 1. PRO UI STYLING ---
st.set_page_config(page_title="Gold Master", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    #MainMenu, footer, header {visibility: hidden;}
    .block-container {padding: 1rem !important; background-color: #050505;}
    
    /* Premium Card Styling */
    .trade-card {
        background-color: #121212;
        border: 1px solid #222;
        border-radius: 15px;
        padding: 20px;
        margin-bottom: 10px;
        text-align: center;
    }
    .signal-header { font-size: 0.9rem; color: #888; text-transform: uppercase; letter-spacing: 1px; }
    .price-large { font-size: 2.5rem; font-weight: 700; color: #ffffff; margin: 10px 0; }
    
    /* Status Badges */
    .badge { padding: 4px 12px; border-radius: 20px; font-size: 0.8rem; font-weight: bold; }
    .bull { background-color: #00ffcc22; color: #00ffcc; border: 1px solid #00ffcc; }
    .bear { background-color: #f6336622; color: #f63366; border: 1px solid #f63366; }
    
    /* Trade Ticket */
    .ticket { background-color: #1e1e1e; border-radius: 12px; padding: 15px; margin-top: 15px; border: 1px dashed #444; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. LOGIC & DATA ---
@st.cache_data(ttl=60)
def get_gold_data(tf):
    df = yf.download("GC=F", period="5d", interval=tf, auto_adjust=True)
    if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
    return df

jhb_tz = pytz.timezone('Africa/Johannesburg')
now = datetime.now(jhb_tz)
tf = st.sidebar.selectbox("Timeframe", ["1h", "4h", "1d"], index=1)
data = get_gold_data(tf)

if not data.empty:
    # SMA & Logic
    data['SMA21'] = data['Close'].rolling(window=21).mean()
    c, p = data.iloc[-1], data.iloc[-2]
    cl, o, h, l = float(c['Close']), float(c['Open']), float(c['High']), float(c['Low'])
    
    # Trend & Pattern
    is_uptrend = cl > c['SMA21']
    trend_label = "UPTREND" if is_uptrend else "DOWNTREND"
    trend_class = "bull" if is_uptrend else "bear"
    
    # Bible Pattern Math
    body, l_shad, u_shad = abs(o - cl), (min(o, cl) - l), (h - max(o, cl))
    signal, color_class = "NO SIGNAL", ""
    if l_shad > (body * 2): signal, color_class = "BULLISH PIN BAR", "bull"
    elif u_shad > (body * 2): signal, color_class = "BEARISH PIN BAR", "bear"
    elif (cl > o) and (float(p['Close']) < float(p['Open'])) and (cl >= float(p['Open'])): 
        signal, color_class = "BULLISH ENGULFING", "bull"
    elif (cl < o) and (float(p['Close']) > float(p['Open'])) and (cl <= float(p['Open'])): 
        signal, color_class = "BEARISH ENGULFING", "bear"

    # --- 3. THE UI DISPLAY ---
    
    # Header Info
    st.markdown(f"**GOLD MARKET** | {now.strftime('%H:%M')} JHB | `{tf.upper()}`")
    
    # Main Price Card
    st.markdown(f"""
        <div class="trade-card">
            <div class="signal-header">Live Gold Price (USD)</div>
            <div class="price-large">${cl:,.2f}</div>
            <span class="badge {trend_class}">{trend_label} (21 SMA)</span>
        </div>
    """, unsafe_allow_html=True)

    # Signal Card
    if signal != "NO SIGNAL":
        st.markdown(f"""
            <div class="trade-card" style="border: 2px solid {'#00ffcc' if 'BULL' in signal else '#f63366'}">
                <div class="signal-header">Bible Signal Found</div>
                <div style="font-size: 1.5rem; font-weight: bold; margin: 10px 0;">{signal}</div>
                <div class="ticket">
                    <div style="display: flex; justify-content: space-between;">
                        <span>ENTRY</span><b>{h+0.3 if 'BULL' in signal else l-0.3:.2f}</b>
                    </div>
                    <div style="display: flex; justify-content: space-between;">
                        <span>STOP LOSS</span><b>{l-0.3 if 'BULL' in signal else h+0.3:.2f}</b>
                    </div>
                    <div style="display: flex; justify-content: space-between; color: #00ffcc;">
                        <span>TARGET (1:2)</span><b>{cl+((cl-l)*2) if 'BULL' in signal else cl-((h-cl)*2):.2f}</b>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)
    else:
        st.info("🔎 Scanning for Pin Bars and Engulfing patterns...")

    # Action Buttons
    if st.button("REFRESH DATA", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

else:
    st.error("Connecting to server...")
