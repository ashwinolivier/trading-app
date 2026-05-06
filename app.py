import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import pytz

st.set_page_config(page_title="Gold TLS", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    #MainMenu, footer, header {visibility: hidden;}
    .block-container {padding: 0.5rem !important;}
    [data-testid="stMetricValue"] { font-size: 1.1rem !important; }
    html, body { overflow: hidden; }
    </style>
    """, unsafe_allow_html=True)

jhb_tz = pytz.timezone('Africa/Johannesburg')
now_jhb = datetime.now(jhb_tz)

@st.cache_data(ttl=300)
def load_gold(tf):
    df = yf.download("GC=F", period="10d", interval=tf, auto_adjust=True)
    if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
    return df

# Header
c1, c2 = st.columns([4, 1])
with c1: st.write(f"🥇 **GOLD** | {now_jhb.strftime('%H:%M')}")
with c2: 
    if st.button("🔄"): st.cache_data.clear(); st.rerun()

tf = st.select_slider("TF", options=["1h", "4h", "1d"], value="4h", label_visibility="collapsed")
data = load_gold(tf)

if not data.empty:
    data['SMA21'] = data['Close'].rolling(window=21).mean()
    c = data.iloc[-1]
    cl, o, h, l = float(c['Close']), float(c['Open']), float(c['High']), float(c['Low'])
    
    # Pattern Logic
    body, l_shad, u_shad = abs(o - cl), (min(o, cl) - l), (h - max(o, cl))
    signal = "None"
    if l_shad > (body * 2): signal = "Bull Pin"
    elif u_shad > (body * 2): signal = "Bear Pin"
    elif (cl > o) and (float(data.iloc[-2]['Close']) < float(data.iloc[-2]['Open'])) and (cl >= float(data.iloc[-2]['Open'])): signal = "Bull Eng"
    elif (cl < o) and (float(data.iloc[-2]['Close']) > float(data.iloc[-2]['Open'])) and (cl <= float(data.iloc[-2]['Open'])): signal = "Bear Eng"

    # Metrics
    m1, m2, m3 = st.columns(3)
    m1.metric("Price", f"${cl:.1f}")
    m2.metric("Trend", "UP" if cl > c['SMA21'] else "DOWN")
    if signal != "None": m3.success(signal)
    else: m3.info("No Signal")

    if signal != "None":
        ent, sl = (h+0.2, l-0.2) if "Bull" in signal else (l-0.2, h+0.2)
        tp = ent + ((ent - sl) * 2) if "Bull" in signal else ent - ((sl - ent) * 2)
        st.write(f"**E:** {ent:.1f} | **SL:** {sl:.1f} | **TP:** {tp:.1f}")

    # --- CHART WITH FIXED ZOOM ---
    fig = go.Figure(data=[go.Candlestick(
        x=data.index, open=data['Open'], high=data['High'], low=data['Low'], close=data['Close'],
        increasing_line_color='#00ffcc', decreasing_line_color='#f63366'
    )])
    fig.add_trace(go.Scatter(x=data.index, y=data['SMA21'], line=dict(color='yellow', width=1.5)))
    
    # Range Settings (Show last 25 candles)
    last_date = data.index[-1]
    start_date = data.index[-25] if len(data) > 25 else data.index[0]

    fig.update_xaxes(range=[start_date, last_date], rangeslider_visible=False, gridcolor='#333', visible=False)
    
    # Remove Weekend Gaps
    fig.update_xaxes(rangebreaks=[
        dict(bounds=["sat", "mon"]), # hide weekends
        dict(bounds=[17, 18], pattern="hour"), # hide daily break
    ])

    fig.update_layout(
        height=320, margin=dict(l=0, r=0, t=0, b=0),
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        showlegend=False, yaxis=dict(gridcolor='#333', side="right", fixedrange=False)
    )
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
