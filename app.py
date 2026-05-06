import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import pytz

st.set_page_config(page_title="GOLD MASTER", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Rajdhani:wght@400;600;700&display=swap');
    * { box-sizing: border-box; }
    body, .stApp { background-color: #060810; color: #c8d0e0; font-family: 'Rajdhani', sans-serif; }
    .block-container { padding: 1rem 1rem 2rem 1rem !important; max-width: 100% !important; }
    header, footer { display: none !important; }
    .stTextInput > div > div > input, .stSelectbox > div > div {
        background: #0d1117 !important; border: 1px solid #1e2a3a !important;
        color: #c8d0e0 !important; font-family: 'Share Tech Mono', monospace !important; border-radius: 4px !important;
    }
    .stButton > button {
        background: #0d1117 !important; border: 1px solid #1e3a5f !important;
        color: #4a9eff !important; font-family: 'Rajdhani', sans-serif !important;
        font-weight: 700 !important; letter-spacing: 2px !important;
        border-radius: 4px !important; padding: 0.4rem 1rem !important; transition: all 0.2s !important;
    }
    .stButton > button:hover { background: #1e3a5f !important; border-color: #4a9eff !important; }
    label, .stSelectbox label { color: #4a6080 !important; font-size: 0.65rem !important; letter-spacing: 2px !important; font-weight: 700 !important; }
    .terminal-header { display: flex; align-items: center; justify-content: space-between; border-bottom: 1px solid #1e2a3a; padding-bottom: 10px; margin-bottom: 16px; }
    .terminal-title { font-family: 'Share Tech Mono', monospace; font-size: 0.7rem; color: #4a6080; letter-spacing: 4px; }
    .terminal-dot { width: 6px; height: 6px; border-radius: 50%; display: inline-block; margin-right: 5px; }
    .dot-green { background: #00ff88; box-shadow: 0 0 6px #00ff88; }
    .dot-yellow { background: #ffcc00; box-shadow: 0 0 6px #ffcc00; }
    .dot-red { background: #ff3355; box-shadow: 0 0 6px #ff3355; }
    .card { background: #0a0e18; border: 1px solid #1a2235; border-radius: 8px; padding: 16px; margin-bottom: 12px; position: relative; overflow: hidden; }
    .card::before { content: ""; position: absolute; top: 0; left: 0; right: 0; height: 1px; background: linear-gradient(to right, transparent, #1e3a5f, transparent); }
    .card-label { font-size: 0.58rem; letter-spacing: 3px; color: #3a5070; font-weight: 700; margin-bottom: 10px; text-transform: uppercase; }
    .price-big { font-family: 'Share Tech Mono', monospace; font-size: 3.2rem; font-weight: 400; color: #ffffff; text-align: center; line-height: 1; letter-spacing: -1px; }
    .price-big span { color: #2a4060; font-size: 2rem; }
    .bias-badge { display: inline-block; padding: 3px 12px; border-radius: 3px; font-size: 0.7rem; font-weight: 700; letter-spacing: 3px; margin-top: 6px; }
    .bias-bull { background: rgba(0,255,136,0.1); border: 1px solid #00ff88; color: #00ff88; }
    .bias-bear { background: rgba(255,51,85,0.1); border: 1px solid #ff3355; color: #ff3355; }
    .bias-neutral { background: rgba(255,204,0,0.1); border: 1px solid #ffcc00; color: #ffcc00; }
    .level-row { display: flex; justify-content: space-between; align-items: center; padding: 5px 0; border-bottom: 1px solid #0f1825; font-size: 0.82rem; }
    .level-row:last-child { border-bottom: none; }
    .level-label { color: #4a6080; font-size: 0.65rem; letter-spacing: 1px; }
    .level-val { font-family: 'Share Tech Mono', monospace; font-weight: 400; }
    .trade-block { display: flex; justify-content: space-between; gap: 8px; margin-top: 4px; }
    .trade-cell { flex: 1; background: #060810; border-radius: 6px; padding: 10px 12px; text-align: center; border: 1px solid #1a2235; }
    .trade-cell-label { font-size: 0.55rem; letter-spacing: 3px; color: #3a5070; margin-bottom: 4px; }
    .trade-cell-val { font-family: 'Share Tech Mono', monospace; font-size: 1rem; font-weight: 400; }
    .entry-color { color: #4a9eff; }
    .tp-color { color: #00ff88; }
    .sl-color { color: #ff3355; }
    .rr-color { color: #ffcc00; }
    .range-bar-wrap { margin: 12px 0 4px 0; position: relative; }
    .range-track { height: 4px; background: #1a2235; border-radius: 2px; position: relative; }
    .range-fill { position: absolute; top: 0; left: 0; height: 100%; border-radius: 2px; }
    .range-needle { position: absolute; top: -4px; width: 2px; height: 12px; background: #ffffff; border-radius: 1px; transform: translateX(-50%); }
    .range-labels { display: flex; justify-content: space-between; font-size: 0.55rem; color: #3a5070; margin-top: 4px; letter-spacing: 1px; }
    .alert-box { border-radius: 6px; padding: 10px 14px; font-size: 0.78rem; line-height: 1.5; border-left: 3px solid; margin-top: 4px; }
    .alert-bull { background: rgba(0,255,136,0.05); border-color: #00ff88; }
    .alert-bear { background: rgba(255,51,85,0.05); border-color: #ff3355; }
    .alert-neutral { background: rgba(255,204,0,0.05); border-color: #ffcc00; }
    .scanline { position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: repeating-linear-gradient(0deg, transparent, transparent 2px, rgba(0,0,0,0.03) 2px, rgba(0,0,0,0.03) 4px); pointer-events: none; z-index: 9999; }
    .timestamp { font-family: 'Share Tech Mono', monospace; font-size: 0.65rem; color: #2a4060; }
    .req-counter { font-family: 'Share Tech Mono', monospace; font-size: 0.6rem; color: #3a5070; text-align: right; margin-top: 4px; }
    </style>
    <div class="scanline"></div>
""", unsafe_allow_html=True)

st.markdown("""
    <div class="terminal-header">
        <div class="terminal-title">
            <span class="terminal-dot dot-green"></span>
            <span class="terminal-dot dot-yellow"></span>
            <span class="terminal-dot dot-red"></span>
            &nbsp; GOLD MASTER // XAU/USD // ALPHA VANTAGE
        </div>
    </div>
""", unsafe_allow_html=True)

# --- API KEY INPUT ---
with st.sidebar:
    st.markdown("### CONFIG")
    api_key = st.text_input("Alpha Vantage API Key", type="password", placeholder="Enter your key...")
    st.caption("Get a free key at alphavantage.co")

c1, c2, c3 = st.columns([2, 2, 1])
with c1:
    tf = st.selectbox("TIMEFRAME", ["60min", "daily"], index=0,
                      format_func=lambda x: "1H" if x == "60min" else "1D")
with c2:
    risk_pct = st.number_input("RISK %", min_value=0.1, max_value=10.0, value=1.0, step=0.1)
with c3:
    st.write("")
    st.write("")
    if st.button("REFRESH"):
        st.cache_data.clear()
        st.rerun()

# --- DATA FETCH ---
# Cache for 15min on intraday, 1hr on daily to protect free tier
TTL_MAP = {"60min": 900, "daily": 3600}

@st.cache_data(ttl=TTL_MAP.get("60min", 900), show_spinner=False)
def fetch_intraday(key, interval):
    url = (
        "https://www.alphavantage.co/query"
        "?function=FX_INTRADAY"
        "&from_symbol=XAU"
        "&to_symbol=USD"
        "&interval=" + interval +
        "&outputsize=compact"
        "&apikey=" + key
    )
    r = requests.get(url, timeout=10)
    data = r.json()
    key_name = "Time Series FX (" + interval + ")"
    if key_name not in data:
        return pd.DataFrame(), data.get("Note", data.get("Information", "Unknown error"))
    ts = data[key_name]
    df = pd.DataFrame(ts).T
    df.index = pd.to_datetime(df.index)
    df = df.sort_index()
    df.columns = ["Open", "High", "Low", "Close"]
    df = df.astype(float)
    return df, None

@st.cache_data(ttl=3600, show_spinner=False)
def fetch_daily(key):
    url = (
        "https://www.alphavantage.co/query"
        "?function=FX_DAILY"
        "&from_symbol=XAU"
        "&to_symbol=USD"
        "&outputsize=compact"
        "&apikey=" + key
    )
    r = requests.get(url, timeout=10)
    data = r.json()
    if "Time Series FX (Daily)" not in data:
        return pd.DataFrame(), data.get("Note", data.get("Information", "Unknown error"))
    ts = data["Time Series FX (Daily)"]
    df = pd.DataFrame(ts).T
    df.index = pd.to_datetime(df.index)
    df = df.sort_index()
    df.columns = ["Open", "High", "Low", "Close"]
    df = df.astype(float)
    return df, None

# --- LEVELS & TRADE LOGIC ---
def calc_levels(df, n_candles):
    window = df.iloc[-n_candles:]
    H = float(window["High"].max())
    L = float(window["Low"].min())
    C = float(df["Close"].iloc[-1])
    P = (H + L + C) / 3
    R1 = 2 * P - L
    R2 = P + (H - L)
    S1 = 2 * P - H
    S2 = P - (H - L)
    return P, R1, R2, S1, S2

def calc_trade(price, pivot, res1, res2, sup1, sup2):
    full_range = res2 - sup2
    buffer = full_range * 0.015
    if price > pivot:
        bias = "LONG"
        entry = round(max(pivot, res1 - buffer), 2)
        sl = round(entry - (entry - sup1) * 0.5, 2)
        tp = round(res2 - buffer, 2)
    else:
        bias = "SHORT"
        entry = round(min(pivot, sup1 + buffer), 2)
        sl = round(entry + (res1 - entry) * 0.5, 2)
        tp = round(sup2 + buffer, 2)
    risk = abs(entry - sl)
    reward = abs(tp - entry)
    rr = round(reward / risk, 2) if risk > 0 else 0
    return bias, entry, tp, sl, rr

def price_position_pct(price, s2, r2):
    rng = r2 - s2
    if rng == 0:
        return 50
    return max(0, min(100, (price - s2) / rng * 100))

def get_bias_class(price, pivot, res1, sup1):
    if price > res1:
        return "bull", "BULLISH"
    elif price > pivot:
        return "bull", "BULLISH BIAS"
    elif price < sup1:
        return "bear", "BEARISH"
    else:
        return "neutral", "NEUTRAL"

# --- MAIN ---
if not api_key:
    st.markdown(
        "<div class='card' style='text-align:center;padding:40px;'>"
        "<div class='card-label' style='font-size:0.8rem;margin-bottom:12px'>API KEY REQUIRED</div>"
        "<div style='color:#4a6080;font-size:0.85rem'>Enter your Alpha Vantage API key in the sidebar to begin.</div>"
        "<div style='margin-top:12px;font-size:0.75rem;color:#3a5070'>Free key at <b style='color:#4a9eff'>alphavantage.co</b></div>"
        "</div>",
        unsafe_allow_html=True
    )
    st.stop()

with st.spinner("Fetching XAU/USD..."):
    if tf == "daily":
        data, err = fetch_daily(api_key)
        lookback = 60
    else:
        data, err = fetch_intraday(api_key, tf)
        lookback = 48

time_now = datetime.now(pytz.timezone("Africa/Johannesburg")).strftime("%H:%M:%S")
date_now = datetime.now(pytz.timezone("Africa/Johannesburg")).strftime("%d %b %Y")

if err:
    st.markdown(
        "<div class='card' style='border-color:#ff3355'>"
        "<div class='card-label'>API ERROR</div>"
        "<div style='color:#ff3355;font-size:0.85rem'>" + str(err) + "</div>"
        "<div style='color:#4a6080;font-size:0.75rem;margin-top:8px'>Free tier: 25 requests/day. If you hit the limit, try again tomorrow or upgrade at alphavantage.co</div>"
        "</div>",
        unsafe_allow_html=True
    )
    st.stop()

if data.empty or len(data) < 5:
    st.error("Not enough data. Try a different timeframe or check your API key.")
    st.stop()

cl = float(data["Close"].iloc[-1])
prev_cl = float(data["Close"].iloc[-2]) if len(data) > 1 else cl
chg = cl - prev_cl
chg_pct = (chg / prev_cl * 100) if prev_cl != 0 else 0
chg_sign = "+" if chg >= 0 else ""
chg_color = "#00ff88" if chg >= 0 else "#ff3355"
pivot, res1, res2, sup1, sup2 = calc_levels(data, min(lookback, len(data)))
bias, entry, tp, sl, rr = calc_trade(cl, pivot, res1, res2, sup1, sup2)
pos_pct = price_position_pct(cl, sup2, res2)
bias_type, bias_label = get_bias_class(cl, pivot, res1, sup1)
n_used = min(lookback, len(data))
bias_badge_class = "bias-bull" if bias_type == "bull" else "bias-bear" if bias_type == "bear" else "bias-neutral"
alert_class = "alert-bull" if bias_type == "bull" else "alert-bear" if bias_type == "bear" else "alert-neutral"
bar_gradient = "linear-gradient(to right, #00ff88, #ffcc00, #ff3355)"

col_a, col_b = st.columns([1, 1])

with col_a:
    st.markdown(
        "<div class='card'>"
        "<div class='card-label'>LIVE PRICE // XAU/USD // " + date_now + "</div>"
        "<div style='text-align:center'>"
        "<div class='price-big'><span>$</span>" + f"{cl:,.2f}" + "</div>"
        "<div style='margin-top:6px;font-family:Share Tech Mono,monospace;font-size:0.75rem;color:" + chg_color + ";'>"
        + chg_sign + f"{chg:,.2f}" + " (" + chg_sign + f"{chg_pct:.2f}" + "%)</div>"
        "<div style='margin-top:8px'><span class='bias-badge " + bias_badge_class + "'>" + bias_label + "</span></div>"
        "</div>"
        "<div class='range-bar-wrap'><div class='range-track'>"
        "<div class='range-fill' style='width:" + f"{pos_pct:.1f}" + "%;background:" + bar_gradient + ";'></div>"
        "<div class='range-needle' style='left:" + f"{pos_pct:.1f}" + "%'></div>"
        "</div>"
        "<div class='range-labels'><span>S2 " + f"{sup2:,.0f}" + "</span><span>PIVOT " + f"{pivot:,.0f}" + "</span><span>" + f"{res2:,.0f}" + " R2</span></div>"
        "</div>"
        "<div style='text-align:center' class='timestamp'>" + time_now + " JHB | " + str(n_used) + " CANDLES | " + tf.upper() + "</div>"
        "<div class='req-counter'>FREE TIER: 25 REQ/DAY -- CACHE: " + ("15MIN" if tf != "daily" else "1HR") + "</div>"
        "</div>",
        unsafe_allow_html=True
    )

with col_b:
    st.markdown(
        "<div class='card'>"
        "<div class='card-label'>KEY LEVELS // PIVOT ANALYSIS</div>"
        "<div class='level-row'><span class='level-label'>MAJOR RESISTANCE R2</span><span class='level-val' style='color:#ff3355'>" + f"{res2:,.2f}" + "</span></div>"
        "<div class='level-row'><span class='level-label'>RESISTANCE R1</span><span class='level-val' style='color:#ff8080'>" + f"{res1:,.2f}" + "</span></div>"
        "<div class='level-row' style='background:rgba(74,158,255,0.04);border-radius:3px;padding:6px 4px;'><span class='level-label' style='color:#4a9eff'>PIVOT POINT</span><span class='level-val' style='color:#4a9eff'>" + f"{pivot:,.2f}" + "</span></div>"
        "<div class='level-row'><span class='level-label'>SUPPORT S1</span><span class='level-val' style='color:#80ffb0'>" + f"{sup1:,.2f}" + "</span></div>"
        "<div class='level-row'><span class='level-label'>MAJOR SUPPORT S2</span><span class='level-val' style='color:#00ff88'>" + f"{sup2:,.2f}" + "</span></div>"
        "</div>",
        unsafe_allow_html=True
    )

st.markdown(
    "<div class='card'>"
    "<div class='card-label'>TRADE SETUP // " + bias + " SCENARIO</div>"
    "<div class='trade-block'>"
    "<div class='trade-cell'><div class='trade-cell-label'>DIRECTION</div><div class='trade-cell-val' style='color:" + ("#00ff88" if bias == "LONG" else "#ff3355") + ";font-size:1.4rem;font-weight:700;letter-spacing:3px'>" + bias + "</div></div>"
    "<div class='trade-cell'><div class='trade-cell-label'>ENTRY ZONE</div><div class='trade-cell-val entry-color'>" + f"{entry:,.2f}" + "</div></div>"
    "<div class='trade-cell'><div class='trade-cell-label'>TAKE PROFIT</div><div class='trade-cell-val tp-color'>" + f"{tp:,.2f}" + "</div></div>"
    "<div class='trade-cell'><div class='trade-cell-label'>STOP LOSS</div><div class='trade-cell-val sl-color'>" + f"{sl:,.2f}" + "</div></div>"
    "<div class='trade-cell'><div class='trade-cell-label'>RISK : REWARD</div><div class='trade-cell-val rr-color'>1 : " + f"{rr}" + "</div></div>"
    "<div class='trade-cell'><div class='trade-cell-label'>RISK (" + f"{risk_pct:.1f}" + "%)</div><div class='trade-cell-val' style='color:#c8d0e0;font-size:0.85rem'>$" + f"{abs(entry - sl):,.2f}" + "/unit</div></div>"
    "</div></div>",
    unsafe_allow_html=True
)

if bias_type == "bull":
    if cl > res2:
        alert_msg = "🚀 <b>BREAKOUT CONFIRMED.</b> XAU/USD trading above R2 at <b>$" + f"{res2:,.2f}" + "</b>. Long bias active. Trail stop above pivot."
    elif cl > res1:
        alert_msg = "📈 <b>APPROACHING R2.</b> Price above R1 -- XAU/USD testing upper structure. Long entry near <b>$" + f"{entry:,.2f}" + "</b>, target R2."
    else:
        alert_msg = "📊 <b>BULLISH BIAS.</b> XAU/USD holding above pivot <b>$" + f"{pivot:,.2f}" + "</b>. Look for long entries on pullbacks."
elif bias_type == "bear":
    if cl < sup2:
        alert_msg = "🚨 <b>MAJOR SUPPORT BROKEN.</b> XAU/USD below S2 <b>$" + f"{sup2:,.2f}" + "</b>. Short bias active."
    elif cl < sup1:
        alert_msg = "🔴 <b>APPROACHING S2.</b> Price below S1 -- bears in control. Short entry near <b>$" + f"{entry:,.2f}" + "</b>, target S2."
    else:
        alert_msg = "⚠️ <b>BEARISH BIAS.</b> XAU/USD below pivot <b>$" + f"{pivot:,.2f}" + "</b>. Look for short entries on bounces."
else:
    alert_msg = "⏸ <b>RANGE BOUND.</b> XAU/USD consolidating between S1 and R1. Wait for break above <b>$" + f"{res1:,.2f}" + "</b> or below <b>$" + f"{sup1:,.2f}" + "</b>."

st.markdown(
    "<div class='card'><div class='card-label'>MARKET CONTEXT</div>"
    "<div class='alert-box " + alert_class + "'>" + alert_msg + "</div></div>",
    unsafe_allow_html=True
)