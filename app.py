import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime
import pytz

# --- 1. HARDCORE CSS RESET ---
st.set_page_config(page_title="Gold Master", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    /* 1. Kill all outer margins and the header/footer */
    .block-container { padding: 0.5rem !important; background-color: #0a0b10; }
    header, footer { display: none !important; }
    
    /* 2. Force the inputs to be tiny and horizontal */
    [data-testid="stHorizontalBlock"] { gap: 0rem !important; }
    
    /* 3. Modern Glass Card */
    .trade-card {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 15px;
        margin-top: 10px;
        text-align: center;
    }
    
    .price-display { font-size: 2.8rem; font-weight: 800; color: #ffffff; margin: 0; line-height: 1.1; }
    .label-small { color: #808495; font-size: 0.65rem; text-transform: uppercase; letter-spacing: 1px; }
    
    /* 4. Ticket Rows */
    .ticket-line { display: flex; justify-content: space-between; margin: 6px 0; font-size: 1rem; border-bottom: 1px solid rgba(255, 255, 255, 0.03); padding-bottom: 2px; }
    
    /* 5. Force specific input width to prevent stacking */
    div[data-testid="column"] { min-width: 45% !important; flex: 1 !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. THE CONTROL ROW (STAYS HORIZONTAL) ---
# We use a compact column layout with specific widths
c1, c2 = st.columns([1, 1])
with c1:
    asset = st.text_input("SYMBOL", value="GC=F", label_visibility="visible").upper()
with c2:
    tf = st.selectbox("TF", ["1h", "4h", "1d"], index=1, label_visibility="visible")

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
    
    # Trend & Signal
    is_up = cl > curr['SMA21']
    body, l_s, u_s = abs(o - cl), (min(o, cl) - l), (h - max(o, cl))
    
    sig = None
    if l_s > (body * 2): sig = "PIN BAR (BULL)"
    elif u_s > (body * 2): sig = "PIN BAR (BEAR)"
    elif (cl > o) and (float(prev['Close']) < float(prev['Open'])) and (cl >= float(prev['Open'])): sig = "ENGULFING (BULL)"
    elif (cl < o) and (float(prev['Close']) > float(prev['Open'])) and (cl <= float(prev['Open'])): sig = "ENGULFING (BEAR)"

    # --- 4. THE UI ---
    st.markdown(f"<div style='text-align: center; margin-top: 10px;'><span class='label-small'>{asset} LIVE • {time_now}</span></div>", unsafe_allow_html=True)

    # Price Card
    trend_color = "#00ffa3" if is_up else "#ff3366"
    st.markdown(f"""
        <div class="trade-card">
            <div class="label-small">Spot Price</div>
            <div class="price-display">${cl:,.2f}</div>
            <div style="color: {trend_color}; font-size: 0.8rem; font-weight: bold; margin-top:5px;">TREND: {'UP' if is_up else 'DOWN'}</div>
        </div>
    """, unsafe_allow_html=True)

    # Signal Card
    if sig:
        is_bull = "BULL" in sig
        ent = h + 0.2 if is_bull else l - 0.2
        sl = l - 0.2 if is_bull else h + 0.2
        tp = ent + (abs(ent-sl)*2) if is_bull else ent - (abs(ent-sl)*2)
        accent = "#00ffa3" if is_bull else "#ff3366"
        st.markdown(f"""
            <div class="trade-card" style="border-top: 3px solid {accent}">
                <div style="color: {accent}; font-weight: bold; font-size: 1.1rem; margin-bottom: 10px;">{sig}</div>
                <div class="ticket-line"><span>ENTRY</span><b>{ent:.2f}</b></div>
                <div class="ticket-line"><span>STOP LOSS</span><b>{sl:.2f}</b></div>
                <div class="ticket-line" style="color: #00ffa3;"><span>TARGET (1:2)</span><b>{tp:.2f}</b></div>
            </div>
        """, unsafe_allow_html=True)
    else:
        st.info("🔎 Monitoring Market...")
else:
    st.error("Check Symbol")
