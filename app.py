import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import pytz

# --- 1. SET COMPACT LAYOUT ---
st.set_page_config(page_title="Gold T.L.S.", layout="wide", initial_sidebar_state="collapsed")

# Custom CSS to force everything to fit one screen
st.markdown("""
    <style>
    .block-container { padding-top: 0.5rem; padding-bottom: 0rem; }
    .stMetric { background-color: #1e2130; padding: 5px; border-radius: 5px; }
    h1 { font-size: 1.5rem !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. TIME & MARKET LOGIC ---
jhb_tz = pytz.timezone('Africa/Johannesburg')
ny_tz = pytz.timezone('America/New_York')
now_jhb = datetime.now(jhb_tz)
now_ny = datetime.now(ny_tz)

# --- 3. DATA FETCHING ---
@st.cache_data(ttl=300)
def load_gold(tf):
    try:
        df = yf.download("GC=F", period="5d", interval=tf, auto_adjust=True)
        if isinstance(df.columns, pd.MultiIndex): 
            df.columns = df.columns.get_level_values(0)
        return df
    except: return pd.DataFrame()

# HEADER
col_head, col_ref = st.columns([4, 1])
with col_head:
    st.write(f"🥇 **GOLD T.L.S.** | 📍 {now_jhb.strftime('%H:%M')}")
with col_ref:
    if st.button("🔄"): 
        st.cache_data.clear()
        st.rerun()

# TIMEFRAME SELECTOR (Compact)
tf = st.select_slider("TF", options=["1h", "4h", "1d"], value="4h", label_visibility="collapsed")
data = load_gold(tf)

if not data.empty:
    data['SMA21'] = data['Close'].rolling(window=21).mean()
    c, p = data.iloc[-1], data.iloc[-2]
    cl, o, h, l = float(c['Close']), float(c['Open']), float(c['High']), float(c['Low'])
    po, pc = float(p['Open']), float(p['Close'])
    
    # Pattern Logic (Bible Rules)
    body, l_shad, u_shad = abs(o - cl), (min(o, cl) - l), (h - max(o, cl))
    signal = None
    if l_shad > (body * 2): signal = "Bullish Pin Bar"
    elif u_shad > (body * 2): signal = "Bearish Pin Bar"
    elif (cl > o) and (pc < po) and (cl >= po): signal = "Bullish Engulfing"
    elif (cl < o) and (pc > po) and (cl <= po): signal = "Bearish Engulfing"

    # --- 4. TOP METRICS ---
    m1, m2, m3 = st.columns(3)
    m1.metric("Price", f"${cl:.1f}")
    m2.metric("Trend", "UP" if cl > c['SMA21'] else "DOWN")
    
    if signal:
        confluence = (cl > c['SMA21'] and "Bullish" in signal) or (cl < c['SMA21'] and "Bearish" in signal)
        m3.success(f"**{signal}**" if confluence else f"**{signal}** (Counter)")
    else:
        m3.info("No Signal")

    # --- 5. TRADE PLAN (Appears only on Signal) ---
    if signal:
        if "Bullish" in signal:
            ent, sl = h + 0.3, l - 0.3
            tp = ent + ((ent - sl) * 2)
        else:
            ent, sl = l - 0.3, h + 0.3
            tp = ent - ((sl - ent) * 2)
        
        t1, t2, t3 = st.columns(3)
        t1.metric("ENTRY", f"{ent:.1f}")
        t2.metric("SL", f"{sl:.1f}")
        t3.metric("TP", f"{tp:.1f}")

    # --- 6. CHART (Optimized for Height) ---
    fig = go.Figure(data=[go.Candlestick(
        x=data.index, open=data['Open'], high=data['High'], low=data['Low'], close=data['Close'],
        increasing_line_color='#00ffcc', decreasing_line_color='#f63366', name="Price"
    )])
    fig.add_trace(go.Scatter(x=data.index, y=data['SMA21'], line=dict(color='yellow', width=1.5), name='21 SMA'))
    
    fig.update_layout(
        height=320, margin=dict(l=0, r=0, t=0, b=0),
        xaxis_rangeslider_visible=False, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        showlegend=False, yaxis=dict(gridcolor='#333', side="right"), xaxis=dict(gridcolor='#333')
    )
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
else:
    st.error("Connecting to Market Data...")
