import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime
import pytz

# --- 1. THEME & UI SETUP ---
st.set_page_config(page_title="Gold Master", layout="wide", initial_sidebar_state="collapsed")

# Professional Dark Mode Styling
st.markdown("""
    <style>
    /* Reset padding but leave the header alone */
    .block-container { padding: 1rem !important; background-color: #0a0b10; }
    
    /* Modern Glass Card */
    .st-emotion-cache-1r6slb0, .trade-card {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 16px;
        text-align: center;
        backdrop-filter: blur(10px);
    }
    
    .price-display { font-size: 3rem; font-weight: 800; color: #ffffff; letter-spacing: -1px; margin: 10px 0; }
    .label-small { color: #808495; font-size: 0.8rem; font-weight: 600; text-transform: uppercase; letter-spacing: 1.5px; }
    
    /* Custom Badge Colors */
    .trend-up { color: #00ffa3; background: rgba(0, 255, 163, 0.1); padding: 4px 12px; border-radius: 20px; font-size: 0.8rem; }
    .trend-down { color: #ff3366; background: rgba(255, 51, 102, 0.1); padding: 4px 12px; border-radius: 20px; font-size: 0.8rem; }
    
    /* Trade Ticket Section */
    .ticket-box { background: rgba(0, 0, 0, 0.2); border-radius: 12px; padding: 16px; border: 1px solid rgba(255, 255, 255, 0.05); margin-top: 15px; }
    .ticket-line { display: flex; justify-content: space-between; margin: 8px 0; font-size: 1rem; border-bottom: 1px solid rgba(255, 255, 255, 0.03); padding-bottom: 4px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. TOP CONTROLS (Always Visible) ---
# Ticker and Timeframe sit side-by-side
top1, top2 = st.columns([1, 1])
with top1:
    asset = st.text_input("Asset", value="GC=F", label_visibility="collapsed")
with top2:
    tf = st.selectbox("TF", ["1h", "4h", "1d"], index=1, label_visibility="collapsed")

# --- 3. DATA & ANALYTICS ---
@st.cache_data(ttl=60)
def fetch_market_data(ticker, interval):
    try:
        df = yf.download(ticker, period="5d", interval=interval, auto_adjust=True)
        if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
        return df
    except: return pd.DataFrame()

data = fetch_market_data(asset, tf)
jhb_tz = pytz.timezone('Africa/Johannesburg')
time_str = datetime.now(jhb_tz).strftime('%H:%M')

if not data.empty:
    data['SMA21'] = data['Close'].rolling(window=21).mean()
    curr, prev = data.iloc[-1], data.iloc[-2]
    cl, o, h, l = float(curr['Close']), float(curr['Open']), float(curr['High']), float(curr['Low'])
    
    # Strategy Logic
    is_up = cl > curr['SMA21']
    
    # Pattern Logic
    body, l_s, u_s = abs(o - cl), (min(o, cl) - l), (h - max(o, cl))
    sig = None
    if l_s > (body * 2): sig = "BULLISH PIN BAR"
    elif u_s > (body * 2): sig = "BEARISH PIN BAR"
    elif (cl > o) and (float(prev['Close']) < float(prev['Open'])) and (cl >= float(prev['Open'])): sig = "BULLISH ENGULFING"
    elif (cl < o) and (float(prev['Close']) > float(prev['Open'])) and (cl <= float(prev['Open'])): sig = "BEARISH ENGULFING"

    # --- 4. THE DASHBOARD UI ---
    
    # Main Header
    st.markdown(f"<div style='text-align: center; margin-bottom: 20px;'><span class='label-small'>{asset.upper()} LIVE</span> • {time_str}</div>", unsafe_allow_html=True)

    # Price Card
    trend_tag = f"<span class='trend-up'>TREND: UP</span>" if is_up else f"<span class='trend-down'>TREND: DOWN</span>"
    st.markdown(f"""
        <div class="trade-card">
            <div class="label-small">Spot Price</div>
            <div class="price-display">${cl:,.2f}</div>
            {trend_tag}
        </div>
    """, unsafe_allow_html=True)

    # Signal Display
    if sig:
        is_bull = "BULLISH" in sig
        ent = h + 0.2 if is_bull else l - 0.2
        sl = l - 0.2 if is_bull else h + 0.2
        tp = ent + (abs(ent-sl)*2) if is_bull else ent - (abs(ent-sl)*2)
        
        sig_color = "#00ffa3" if is_bull else "#ff3366"
        st.markdown(f"""
            <div class="trade-card" style="border: 1px solid {sig_color}">
                <div style="color: {sig_color}; font-weight: bold; font-size: 1.2rem;">{sig}</div>
                <div class="ticket-box">
                    <div class="ticket-line"><span>ENTRY</span><b>{ent:.2f}</b></div>
                    <div class="ticket-line"><span>STOP LOSS</span><b>{sl:.2f}</b></div>
                    <div class="ticket-line" style="color: #00ffa3;"><span>TARGET (1:2)</span><b>{tp:.2f}</b></div>
                </div>
            </div>
        """, unsafe_allow_html=True)
    else:
        st.info("🔎 Monitoring for high-probability setups...")

else:
    st.error("Connection Error. Check Ticker or Market Status.")
