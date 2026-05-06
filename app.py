import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime
import pytz

# --- 1. SQUASH THE UI ---
st.set_page_config(page_title="Gold Master", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    /* Force top padding to zero */
    .block-container { padding-top: 0rem !important; padding-bottom: 0rem !important; background-color: #0a0b10; }
    
    /* Shrink the input boxes for mobile */
    div[data-baseweb="select"] > div { min-height: 30px !important; font-size: 0.8rem !important; }
    .stTextInput input { height: 30px !important; font-size: 0.8rem !important; }
    
    /* Premium Card Styling */
    .trade-card {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 15px;
        margin-bottom: 10px;
        text-align: center;
    }
    
    .price-display { font-size: 2.8rem; font-weight: 800; color: #ffffff; margin: 5px 0; line-height: 1; }
    .label-small { color: #808495; font-size: 0.7rem; font-weight: 600; text-transform: uppercase; letter-spacing: 1px; }
    
    .trend-up { color: #00ffa3; background: rgba(0, 255, 163, 0.1); padding: 2px 10px; border-radius: 10px; font-size: 0.7rem; }
    .trend-down { color: #ff3366; background: rgba(255, 51, 102, 0.1); padding: 2px 10px; border-radius: 10px; font-size: 0.7rem; }
    
    .ticket-line { display: flex; justify-content: space-between; margin: 6px 0; font-size: 0.95rem; border-bottom: 1px solid rgba(255, 255, 255, 0.03); padding-bottom: 2px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. THE NEW CONTROL BAR ---
# Using 2 columns that are guaranteed to stay side-by-side
col1, col2 = st.columns(2)

with col1:
    # This is where you change GC=F to BTC-USD or EURUSD=X
    asset = st.text_input("SYMBOL", value="GC=F").upper()
with col2:
    tf = st.selectbox("TIMEFRAME", ["1h", "4h", "1d"], index=1)

# --- 3. DATA ENGINE ---
@st.cache_data(ttl=60)
def fetch_data(ticker, interval):
    try:
        df = yf.download(ticker, period="5d", interval=interval, auto_adjust=True)
        if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
        return df
    except: return pd.DataFrame()

data = fetch_data(asset, tf)
jhb_tz = pytz.timezone('Africa/Johannesburg')
time_now = datetime.now(jhb_tz).strftime('%H:%M')

if not data.empty:
    data['SMA21'] = data['Close'].rolling(window=21).mean()
    curr, prev = data.iloc[-1], data.iloc[-2]
    cl, o, h, l = float(curr['Close']), float(curr['Open']), float(curr['High']), float(curr['Low'])
    
    # Logic
    is_up = cl > curr['SMA21']
    body, l_s, u_s = abs(o - cl), (min(o, cl) - l), (h - max(o, cl))
    
    sig = None
    if l_s > (body * 2): sig = "BULLISH PIN BAR"
    elif u_s > (body * 2): sig = "BEARISH PIN BAR"
    elif (cl > o) and (float(prev['Close']) < float(prev['Open'])) and (cl >= float(prev['Open'])): sig = "BULLISH ENGULFING"
    elif (cl < o) and (float(prev['Close']) > float(prev['Open'])) and (cl <= float(prev['Open'])): sig = "BEARISH ENGULFING"

    # --- 4. THE UI ---
    st.markdown(f"<div style='text-align: center; margin-bottom: 5px;'><span class='label-small'>{asset} LIVE • {time_now}</span></div>", unsafe_allow_html=True)

    # Price Card
    trend_tag = f"<span class='trend-up'>TREND: UP</span>" if is_up else f"<span class='trend-down'>TREND: DOWN</span>"
    st.markdown(f"""
        <div class="trade-card">
            <div class="label-small">Spot Price</div>
            <div class="price-display">${cl:,.2f}</div>
            {trend_tag}
        </div>
    """, unsafe_allow_html=True)

    # Signal Card
    if sig:
        is_bull = "BULLISH" in sig
        ent = h + 0.2 if is_bull else l - 0.2
        sl = l - 0.2 if is_bull else h + 0.2
        tp = ent + (abs(ent-sl)*2) if is_bull else ent - (abs(ent-sl)*2)
        accent = "#00ffa3" if is_bull else "#ff3366"
        st.markdown(f"""
            <div class="trade-card" style="border: 1px solid {accent}">
                <div style="color: {accent}; font-weight: bold; font-size: 1rem; margin-bottom: 10px;">{sig}</div>
                <div class="ticket-line"><span>ENTRY</span><b>{ent:.2f}</b></div>
                <div class="ticket-line"><span>STOP LOSS</span><b>{sl:.2f}</b></div>
                <div class="ticket-line" style="color: #00ffa3;"><span>TARGET (1:2)</span><b>{tp:.2f}</b></div>
            </div>
        """, unsafe_allow_html=True)
    else:
        st.info("🔎 Scanning...")

else:
    st.error("Invalid Ticker or Connection Error.")
