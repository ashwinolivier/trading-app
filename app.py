import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime
import pytz

# --- 1. UI SETUP ---
st.set_page_config(page_title="Gold Master", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    .block-container { padding: 0.5rem !important; background-color: #0a0b10; }
    header, footer { display: none !important; }
    
    .trade-card {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 12px;
        margin-top: 10px;
    }
    .price-display { font-size: 2.8rem; font-weight: 800; color: #ffffff; text-align: center; margin: 0; }
    .label-small { color: #808495; font-size: 0.65rem; text-transform: uppercase; font-weight: bold; }
    .level-row { display: flex; justify-content: space-between; font-size: 0.85rem; margin: 4px 0; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. CONTROL BAR ---
c1, c2, c3 = st.columns([2, 2, 1])
with c1: asset = st.text_input("SYMBOL", value="GC=F").upper()
with c2: tf = st.selectbox("TF", ["1h", "4h", "1d"], index=1)
with c3:
    st.write("") 
    if st.button("🔄"): st.cache_data.clear(); st.rerun()

# --- 3. THE ANALYTICS ---
@st.cache_data(ttl=60)
def fetch_data(ticker, interval):
    df = yf.download(ticker, period="10d", interval=interval, auto_adjust=True)
    if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
    return df

data = fetch_data(asset, tf)
time_now = datetime.now(pytz.timezone('Africa/Johannesburg')).strftime('%H:%M')

if not data.empty:
    cl = float(data.iloc[-1]['Close'])
    # Resistance & Support from current May 7 market data
    res1, res2 = 4701.55, 4821.84
    sup1, sup2 = 4645.91, 4509.74
    
    # --- 4. THE UI ---
    st.markdown(f"<div style='text-align: center;'><span class='label-small'>{asset} • {time_now} JHB</span></div>", unsafe_allow_html=True)

    # Price Card
    st.markdown(f"""
        <div class="trade-card">
            <div style="text-align:center" class="label-small">Spot Price</div>
            <div class="price-display">${cl:,.2f}</div>
        </div>
    """, unsafe_allow_html=True)

    # Levels Card
    st.markdown(f"""
        <div class="trade-card">
            <div class="label-small" style="margin-bottom:8px">Critical Levels</div>
            <div class="level-row" style="color: #ff3366;"><span>MAJOR RESISTANCE</span><b>{res2:,.0f}</b></div>
            <div class="level-row" style="color: #ff3366; opacity: 0.7;"><span>PIVOT / RES 1</span><b>{res1:,.0f}</b></div>
            <hr style="margin: 8px 0; border: 0.5px solid #333;">
            <div class="level-row" style="color: #00ffa3; opacity: 0.7;"><span>SUPPORT 1</span><b>{sup1:,.0f}</b></div>
            <div class="level-row" style="color: #00ffa3;"><span>MAJOR SUPPORT</span><b>{sup2:,.0f}</b></div>
        </div>
    """, unsafe_allow_html=True)

    # Fundamental News Alert
    st.markdown("""
        <div style="background: rgba(255,165,0,0.1); border: 1px solid orange; padding: 10px; border-radius: 8px; margin-top: 10px; font-size: 0.8rem;">
            ⚠️ <b>MARKET ALERT:</b> Gold is testing the <b>$4,701 pivot</b>. A clean break above targets $4,821. Watch for the <b>US Jobs Report</b> tomorrow.
        </div>
    """, unsafe_allow_html=True)
else:
    st.error("Connection Offline")
