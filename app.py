import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import pytz

# --- 1. SQUASH UI WITH CSS ---
st.set_page_config(page_title="Gold TLS", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    /* Hide Streamlit Overhead */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Remove padding and force single screen */
    .block-container {
        padding-top: 0rem !important;
        padding-bottom: 0rem !important;
        padding-left: 0.5rem !important;
        padding-right: 0.5rem !important;
    }
    
    /* Shrink Metric Sizes */
    [data-testid="stMetricValue"] { font-size: 1.2rem !important; }
    [data-testid="stMetricLabel"] { font-size: 0.8rem !important; }
    
    /* Hide scrollbars */
    html, body { overflow: hidden; height: 100vh; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. LOGIC ---
jhb_tz = pytz.timezone('Africa/Johannesburg')
now_jhb = datetime.now(jhb_tz)

@st.cache_data(ttl=300)
def load_gold(tf):
    df = yf.download("GC=F", period="5d", interval=tf, auto_adjust=True)
    if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
    return df

# TOP BAR (Very Small)
col_a, col_b = st.columns([3, 1])
with col_a: st.write(f"🥇 **GOLD** | {now_jhb.strftime('%H:%M')}")
with col_b: 
    if st.button("🔄", key="ref"): st.cache_data.clear(); st.rerun()

# TIME SLIDER (Ultra Slim)
tf = st.select_slider("TF", options=["1h", "4h", "1d"], value="4h", label_visibility="collapsed")
data = load_gold(tf)

if not data.empty:
    data['SMA21'] = data['Close'].rolling(window=21).mean()
    c = data.iloc[-1]
    cl, o, h, l = float(c['Close']), float(c['Open']), float(c['High']), float(c['Low'])
    
    # Simple Pattern Math
    body, l_shad, u_shad = abs(o - cl), (min(o, cl) - l), (h - max(o, cl))
    signal = "None"
    if l_shad > (body * 2): signal = "Bull Pin"
    elif u_shad > (body * 2): signal = "Bear Pin"
    elif (cl > o) and (float(data.iloc[-2]['Close']) < float(data.iloc[-2]['Open'])) and (cl >= float(data.iloc[-2]['Open'])): signal = "Bull Eng"
    elif (cl < o) and (float(data.iloc[-2]['Close']) > float(data.iloc[-2]['Open'])) and (cl <= float(data.iloc[-2]['Open'])): signal = "Bear Eng"

    # --- 3. METRIC ROW ---
    m1, m2, m3 = st.columns(3)
    m1.metric("Price", f"${cl:.1f}")
    m2.metric("Trend", "UP" if cl > c['SMA21'] else "DOWN")
    
    if signal != "None":
        m3.success(signal)
        # Only show trade plan if signal exists (saves space)
        st.write("---")
        if "Bull" in signal:
            ent, sl = h + 0.2, l - 0.2
            tp = ent + ((ent - sl) * 2)
        else:
            ent, sl = l - 0.2, h + 0.2
            tp = ent - ((sl - ent) * 2)
        
        t1, t2, t3 = st.columns(3)
        t1.write(f"**E:** {ent:.1f}")
        t2.write(f"**SL:** {sl:.1f}")
        t3.write(f"**TP:** {tp:.1f}")
    else:
        m3.info("No Signal")

    # --- 4. THE CHART (Small Height) ---
    fig = go.Figure(data=[go.Candlestick(
        x=data.index, open=data['Open'], high=data['High'], low=data['Low'], close=data['Close'],
        increasing_line_color='#00ffcc', decreasing_line_color='#f63366'
    )])
    fig.add_trace(go.Scatter(x=data.index, y=data['SMA21'], line=dict(color='yellow', width=1)))
    
    fig.update_layout(
        height=280, margin=dict(l=0, r=0, t=0, b=0),
        xaxis_rangeslider_visible=False, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        showlegend=False, yaxis=dict(gridcolor='#333', side="right"), xaxis=dict(gridcolor='#333', visible=False)
    )
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
