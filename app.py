import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import pytz

# --- 1. SET COMPACT LAYOUT ---
st.set_page_config(page_title="Gold Master", layout="wide", initial_sidebar_state="collapsed")

# Inject CSS to remove extra padding and make it fit mobile screens better
st.markdown("""
    <style>
    .block-container { padding-top: 1rem; padding-bottom: 0rem; }
    .stMetric { background-color: #1e2130; padding: 10px; border-radius: 8px; }
    div[data-testid="stExpander"] { border: none; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. TIME & MARKET LOGIC ---
jhb_tz = pytz.timezone('Africa/Johannesburg')
ny_tz = pytz.timezone('America/New_York')
now_jhb = datetime.now(jhb_tz)
now_ny = datetime.now(ny_tz)

def get_status():
    d, h = now_ny.weekday(), now_ny.hour
    if d == 5 or (d == 4 and h >= 17) or (d == 6 and h < 18): return "CLOSED", "red"
    if h == 17: return "BREAK", "orange"
    return "OPEN", "green"

m_status, m_color = get_status()

# --- 3. DATA FETCHING ---
@st.cache_data(ttl=300)
def load_gold(tf):
    df = yf.download("GC=F", period="5d", interval=tf, auto_adjust=True)
    if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
    return df

# Header Row
col_a, col_b, col_c = st.columns([2, 1, 1])
with col_a: st.title("🥇 Gold T.L.S.")
with col_b: st.write(f"📍 {now_jhb.strftime('%H:%M')}")
with col_c: 
    if st.button("🔄"): st.cache_data.clear(); st.rerun()

# Settings Row
tf = st.select_slider("Select Timeframe", options=["1h", "4h", "1d"], value="4h")
data = load_gold(tf)

if not data.empty:
    # SMA & Calculations
    data['SMA21'] = data['Close'].rolling(window=21).mean()
    c, p = data.iloc[-1], data.iloc[-2]
    cl, o, h, l = float(c['Close']), float(c['Open']), float(c['High']), float(c['Low'])
    po, pc = float(p['Open']), float(p['Close'])
    
    # Pattern Logic
    body, l_shad, u_shad = abs(o - cl), (min(o, cl) - l), (h - max(o, cl))
    signal = None
    if l_shad > (body * 2): signal = "Bullish Pin Bar"
    elif u_shad > (body * 2): signal = "Bearish Pin Bar"
    elif (cl > o) and (pc < po) and (cl >= po): signal = "Bullish Engulfing"
    elif (cl < o) and (pc > po) and (cl <= po): signal = "Bearish Engulfing"

    # --- 4. TOP ROW: METRICS & SIGNAL ---
    m1, m2, m3 = st.columns(3)
    m1.metric("Price", f"${cl:.1f}")
    m2.metric("Trend", "UP" if cl > c['SMA21'] else "DOWN")
    
    with m3:
        if signal: st.success(f"**{signal}**")
        else: st.info("Scanning...")

    # --- 5. MIDDLE ROW: TRADE PLAN (Only shows if signal exists) ---
    if signal:
        st.write("---")
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

    # --- 6. BOTTOM ROW: THE GRAPH ---
    # We keep the height short (300px) to fit on one screen
    fig = go.Figure(data=[go.Candlestick(
        x=data.index, open=data['Open'], high=data['High'], low=data['Low'], close=data['Close'],
        increasing_line_color='#00ffcc', decreasing_line_color='#f63366'
    )])
    fig.add_trace(go.Scatter(x=data.index, y=data['SMA21'], line=dict(color='yellow', width=1), name='21 SMA'))
    
    fig.update_layout(
        height=350, margin=dict(l=10, r=10, t=10, b=10),
        xaxis_rangeslider_visible=False, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        showlegend=False, yaxis=dict(gridcolor='#333'), xaxis=dict(gridcolor='#333')
    )
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

else:
    st.error("Market data unavailable.")
