import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime
import pytz

# --- 1. PRO UI RESET (FIXED SIDE-BY-SIDE) ---
st.set_page_config(page_title="Gold Master", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    .block-container { padding: 0.5rem !important; background-color: #0a0b10; }
    header, footer { display: none !important; }
    
    /* Force SYMBOL and TF to stay on ONE LINE */
    .control-row {
        display: flex;
        gap: 10px;
        align-items: flex-end;
        margin-bottom: 15px;
    }
    .control-item { flex: 1; }
    
    /* Glass Card Style */
    .trade-card {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 15px;
        margin-top: 10px;
        text-align: center;
    }
    .price-display { font-size: 2.8rem; font-weight: 800; color: #ffffff; margin: 0; line-height: 1.1; }
    .label-small { color: #808495; font-size: 0.65rem; text-transform: uppercase; font-weight: bold; }
    .ticket-line { display: flex; justify-content: space-between; margin: 6px 0; font-size: 1rem; border-bottom: 1px solid rgba(255, 255, 255, 0.03); padding-bottom: 2px; }
    
    /* Custom Refresh Button Style */
    .stButton>button { width: 100%; border-radius: 10px; background: #1e1e2e; color: white; border: 1px solid #333; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. CONTROL CENTER ---
c1, c2, c3 = st.columns([2, 2, 1])
with c1:
    asset = st.text_input("SYMBOL", value="GC=F").upper()
with c2:
    tf = st.selectbox("TF", ["1h", "4h", "1d"], index=1)
with c3:
    st.write("") # Spacer
    if st.button("🔄"):
        st.cache_data.clear()
        st.rerun()

# --- 3. DATA & NEWS ENGINE ---
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
    
    is_up = cl > curr['SMA21']
    body, l_s, u_s = abs(o - cl), (min(o, cl) - l), (h - max(o, cl))
    
    sig = None
    if l_s > (body * 2): sig = "BULLISH PIN BAR"
    elif u_s > (body * 2): sig = "BEARISH PIN BAR"
    elif (cl > o) and (float(prev['Close']) < float(prev['Open'])) and (cl >= float(prev['Open'])): sig = "BULLISH ENGULFING"
    elif (cl < o) and (float(prev['Close']) > float(prev['Open'])) and (cl <= float(prev['Open'])): sig = "BEARISH ENGULFING"

    # --- 4. THE UI ---
    st.markdown(f"<div style='text-align: center;'><span class='label-small'>{asset} • {time_now} JHB</span></div>", unsafe_allow_html=True)

    # Price Card
    trend_color = "#00ffa3" if is_up else "#ff3366"
    st.markdown(f"""
        <div class="trade-card">
            <div class="label-small">Spot Price</div>
            <div class="price-display">${cl:,.2f}</div>
            <div style="color: {trend_color}; font-size: 0.8rem; font-weight: bold;">TREND: {'UP' if is_up else 'DOWN'}</div>
        </div>
    """, unsafe_allow_html=True)

    # Signal & Strategy
    if sig:
        is_bull = "BULLISH" in sig
        ent = h + 0.3 if is_bull else l - 0.3
        sl = l - 0.3 if is_bull else h + 0.3
        tp = ent + (abs(ent-sl)*2) if is_bull else ent - (abs(ent-sl)*2)
        accent = "#00ffa3" if is_bull else "#ff3366"
        st.markdown(f"""
            <div class="trade-card" style="border-top: 3px solid {accent}">
                <div style="color: {accent}; font-weight: bold; font-size: 1.1rem; margin-bottom: 5px;">{sig}</div>
                <div class="ticket-line"><span>ENTRY</span><b>{ent:.2f}</b></div>
                <div class="ticket-line"><span>STOP LOSS</span><b>{sl:.2f}</b></div>
                <div class="ticket-line" style="color: #00ffa3;"><span>TARGET (1:2)</span><b>{tp:.2f}</b></div>
            </div>
        """, unsafe_allow_html=True)
    
    # Fundamental Alert
    st.markdown("""
        <div style="background: rgba(255,165,0,0.1); border: 1px solid orange; padding: 10px; border-radius: 8px; margin-top: 10px; font-size: 0.8rem;">
            ⚠️ <b>NEWS:</b> Gold rebounding on Iran peace talks progress. Focus on Friday's US Jobs Report.
        </div>
    """, unsafe_allow_html=True)

else:
    st.error("Check Connection")
