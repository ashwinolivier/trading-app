import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime
import pytz

# --- 1. PREMIUM UI STYLING ---
st.set_page_config(page_title="Gold Master", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    /* Hide all default Streamlit menus */
    #MainMenu, footer, header {visibility: hidden;}
    .block-container {padding: 0.5rem !important; background-color: #050505;}
    
    /* Custom Card Styling */
    .trade-card {
        background-color: #121212;
        border: 1px solid #222;
        border-radius: 15px;
        padding: 15px;
        margin-bottom: 10px;
        text-align: center;
    }
    .price-large { font-size: 2.2rem; font-weight: 700; color: #ffffff; margin: 5px 0; }
    
    /* Trade Ticket for Entry/SL/TP */
    .ticket { background-color: #1e1e1e; border-radius: 10px; padding: 12px; margin-top: 10px; border: 1px dashed #444; }
    .ticket-row { display: flex; justify-content: space-between; margin-bottom: 4px; font-size: 0.9rem; }
    
    /* Make input widgets smaller for the top bar */
    .stSelectbox, .stTextInput { margin-top: -15px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. THE TOP CONTROL BAR ---
# We use columns to put Ticker, TF, and Rerun all in one line at the top
c1, c2, c3 = st.columns([1.5, 1.2, 0.5])

with c1:
    asset = st.text_input("Asset", value="GC=F", label_visibility="collapsed")
with c2:
    tf = st.selectbox("TF", ["1h", "4h", "1d"], index=1, label_visibility="collapsed")
with c3:
    if st.button("🔄"):
        st.cache_data.clear()
        st.rerun()

# --- 3. DATA & LOGIC ---
@st.cache_data(ttl=60)
def get_market_data(ticker, timeframe):
    try:
        df = yf.download(ticker, period="5d", interval=timeframe, auto_adjust=True)
        if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
        return df
    except: return pd.DataFrame()

data = get_market_data(asset, tf)
jhb_tz = pytz.timezone('Africa/Johannesburg')
now = datetime.now(jhb_tz)

if not data.empty:
    # SMA & Candle Logic
    data['SMA21'] = data['Close'].rolling(window=21).mean()
    c, p = data.iloc[-1], data.iloc[-2]
    cl, o, h, l = float(c['Close']), float(c['Open']), float(c['High']), float(c['Low'])
    
    # Trend Detection
    is_uptrend = cl > c['SMA21']
    
    # Pattern Detection (The Bible Rules)
    body, l_shad, u_shad = abs(o - cl), (min(o, cl) - l), (h - max(o, cl))
    signal = "NO SIGNAL"
    if l_shad > (body * 2): signal = "BULLISH PIN BAR"
    elif u_shad > (body * 2): signal = "BEARISH PIN BAR"
    elif (cl > o) and (float(p['Close']) < float(p['Open'])) and (cl >= float(p['Open'])): signal = "BULLISH ENGULFING"
    elif (cl < o) and (float(p['Close']) > float(p['Open'])) and (cl <= float(p['Open'])): signal = "BEARISH ENGULFING"

    # --- 4. THE DASHBOARD ---
    
    # Live Status Row
    st.write(f"🕒 {now.strftime('%H:%M')} | Trend: {'🟢 UP' if is_uptrend else '🔴 DOWN'}")

    # Main Price Display
    st.markdown(f"""
        <div class="trade-card">
            <div style="color: #888; font-size: 0.8rem;">{asset.upper()} LIVE PRICE</div>
            <div class="price-large">${cl:,.2f}</div>
        </div>
    """, unsafe_allow_html=True)

    # Signal & Trade Plan
    if signal != "NO SIGNAL":
        # Calculate Levels
        is_bull = "BULLISH" in signal
        entry = h + 0.3 if is_bull else l - 0.3
        sl = l - 0.3 if is_bull else h + 0.3
        risk = abs(entry - sl)
        tp = entry + (risk * 2) if is_bull else entry - (risk * 2)

        st.markdown(f"""
            <div class="trade-card" style="border-color: {'#00ffcc' if is_bull else '#f63366'}">
                <div style="font-weight: bold; color: {'#00ffcc' if is_bull else '#f63366'};">{signal}</div>
                <div class="ticket">
                    <div class="ticket-row"><span>ENTRY</span> <b>{entry:.2f}</b></div>
                    <div class="ticket-row"><span>STOP LOSS</span> <b>{sl:.2f}</b></div>
                    <div class="ticket-row" style="color: #00ffcc;"><span>TARGET (1:2)</span> <b>{tp:.2f}</b></div>
                </div>
            </div>
        """, unsafe_allow_html=True)
    else:
        st.info(f"Scanning {tf} for patterns...")

else:
    st.warning("Data offline. Check Ticker or Market Hours.")
