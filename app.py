import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime
import pytz

st.set_page_config(page_title=“GOLD MASTER”, layout=“wide”, initial_sidebar_state=“collapsed”)

st.markdown(”””
<style>
@import url(‘https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Rajdhani:wght@400;600;700&display=swap’);
* { box-sizing: border-box; }
body, .stApp { background-color: #060810; color: #c8d0e0; font-family: ‘Rajdhani’, sans-serif; }
.block-container { padding: 1rem 1rem 2rem 1rem !important; max-width: 100% !important; }
header, footer { display: none !important; }
.stTextInput > div > div > input, .stSelectbox > div > div {
background: #0d1117 !important; border: 1px solid #1e2a3a !important;
color: #c8d0e0 !important; font-family: ‘Share Tech Mono’, monospace !important; border-radius: 4px !important;
}
.stButton > button {
background: #0d1117 !important; border: 1px solid #1e3a5f !important;
color: #4a9eff !important; font-family: ‘Rajdhani’, sans-serif !important;
font-weight: 700 !important; letter-spacing: 2px !important;
border-radius: 4px !important; padding: 0.4rem 1rem !important; transition: all 0.2s !important;
}
.stButton > button:hover { background: #1e3a5f !important; border-color: #4a9eff !important; }
label, .stSelectbox label { color: #4a6080 !important; font-size: 0.65rem !important; letter-spacing: 2px !important; font-weight: 700 !important; }
.terminal-header { display: flex; align-items: center; justify-content: space-between; border-bottom: 1px solid #1e2a3a; padding-bottom: 10px; margin-bottom: 16px; }
.terminal-title { font-family: ‘Share Tech Mono’, monospace; font-size: 0.7rem; color: #4a6080; letter-spacing: 4px; }
.terminal-dot { width: 6px; height: 6px; border-radius: 50%; display: inline-block; margin-right: 5px; }
.dot-green { background: #00ff88; box-shadow: 0 0 6px #00ff88; }
.dot-yellow { background: #ffcc00; box-shadow: 0 0 6px #ffcc00; }
.dot-red { background: #ff3355; box-shadow: 0 0 6px #ff3355; }
.card { background: #0a0e18; border: 1px solid #1a2235; border-radius: 8px; padding: 16px; margin-bottom: 12px; position: relative; overflow: hidden; }
.card::before { content: “”; position: absolute; top: 0; left: 0; right: 0; height: 1px; background: linear-gradient(to right, transparent, #1e3a5f, transparent); }
.card-label { font-size: 0.58rem; letter-spacing: 3px; color: #3a5070; font-weight: 700; margin-bottom: 10px; text-transform: uppercase; }
.price-big { font-family: ‘Share Tech Mono’, monospace; font-size: 3.2rem; font-weight: 400; color: #ffffff; text-align: center; line-height: 1; letter-spacing: -1px; }
.price-big span { color: #2a4060; font-size: 2rem; }
.bias-badge { display: inline-block; padding: 3px 12px; border-radius: 3px; font-size: 0.7rem; font-weight: 700; letter-spacing: 3px; margin-top: 6px; }
.bias-bull { background: rgba(0,255,136,0.1); border: 1px solid #00ff88; color: #00ff88; }
.bias-bear { background: rgba(255,51,85,0.1); border: 1px solid #ff3355; color: #ff3355; }
.bias-neutral { background: rgba(255,204,0,0.1); border: 1px solid #ffcc00; color: #ffcc00; }
.level-row { display: flex; justify-content: space-between; align-items: center; padding: 5px 0; border-bottom: 1px solid #0f1825; font-size: 0.82rem; }
.level-row:last-child { border-bottom: none; }
.level-label { color: #4a6080; font-size: 0.65rem; letter-spacing: 1px; }
.level-val { font-family: ‘Share Tech Mono’, monospace; font-weight: 400; }
.trade-block { display: flex; justify-content: space-between; gap: 8px; margin-top: 4px; }
.trade-cell { flex: 1; background: #060810; border-radius: 6px; padding: 10px 12px; text-align: center; border: 1px solid #1a2235; }
.trade-cell-label { font-size: 0.55rem; letter-spacing: 3px; color: #3a5070; margin-bottom: 4px; }
.trade-cell-val { font-family: ‘Share Tech Mono’, monospace; font-size: 1rem; font-weight: 400; }
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
.timestamp { font-family: ‘Share Tech Mono’, monospace; font-size: 0.65rem; color: #2a4060; }
</style>
<div class="scanline"></div>
“””, unsafe_allow_html=True)

st.markdown(”””
<div class="terminal-header">
<div class="terminal-title">
<span class="terminal-dot dot-green"></span>
<span class="terminal-dot dot-yellow"></span>
<span class="terminal-dot dot-red"></span>
  GOLD MASTER // TRADING TERMINAL v2.1
</div>
</div>
“””, unsafe_allow_html=True)

c1, c2, c3, c4 = st.columns([2, 2, 1, 1])
with c1:
asset = st.text_input(“SYMBOL”, value=“GC=F”).upper()
with c2:
tf = st.selectbox(“TIMEFRAME”, [“1h”, “4h”, “1d”], index=1)
with c3:
risk_pct = st.number_input(“RISK %”, min_value=0.1, max_value=10.0, value=1.0, step=0.1)
with c4:
st.write(””)
st.write(””)
if st.button(“REFRESH”):
st.cache_data.clear()
st.rerun()

PERIOD_MAP = {“1h”: “10d”, “4h”: “30d”, “1d”: “180d”}
LOOKBACK_MAP = {“1h”: 48, “4h”: 30, “1d”: 60}

@st.cache_data(ttl=60)
def fetch_data(ticker, interval, period):
try:
df = yf.download(ticker, period=period, interval=interval, auto_adjust=True)
if isinstance(df.columns, pd.MultiIndex):
df.columns = df.columns.get_level_values(0)
return df
except Exception:
return pd.DataFrame()

period = PERIOD_MAP[tf]
lookback = LOOKBACK_MAP[tf]
data = fetch_data(asset, tf, period)
time_now = datetime.now(pytz.timezone(“Africa/Johannesburg”)).strftime(”%H:%M:%S”)
date_now = datetime.now(pytz.timezone(“Africa/Johannesburg”)).strftime(”%d %b %Y”)

def calc_levels(df, n_candles):
window = df.iloc[-n_candles:]
H = float(window[“High”].max())
L = float(window[“Low”].min())
C = float(df[“Close”].iloc[-1])
P = (H + L + C) / 3
R1 = 2 * P - L
R2 = P + (H - L)
S1 = 2 * P - H
S2 = P - (H - L)
return P, R1, R2, S1, S2

def is_bearish_market(price, pivot, df):
“””
Returns True if market structure and momentum favour shorts.
Uses three confluence filters:
1. Price vs pivot
2. Short-term momentum (last 5 closes)
3. Structure: lower lows over last 10 candles
Bearish confirmed when at least 2 of 3 filters are bearish.
“””
# Filter 1: price below pivot
below_pivot = price < pivot

```
# Filter 2: momentum — last close vs 5 candles ago
if len(df) >= 5:
    momentum_up = float(df["Close"].iloc[-1]) > float(df["Close"].iloc[-5])
else:
    momentum_up = price >= pivot

# Filter 3: lower lows structure
if len(df) >= 10:
    lower_lows = float(df["Low"].iloc[-1]) < float(df["Low"].iloc[-10])
else:
    lower_lows = False

bearish_votes = sum([below_pivot, not momentum_up, lower_lows])
return bearish_votes >= 2
```

def calc_trade(price, pivot, res1, res2, sup1, sup2, df):
full_range = res2 - sup2
buffer = full_range * 0.015

```
bearish = is_bearish_market(price, pivot, df)

if not bearish:
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
```

def get_bias_class(price, pivot, res1, sup1, df):
bearish = is_bearish_market(price, pivot, df)

```
if bearish:
    if price < sup1:
        return "bear", "BEARISH"
    else:
        return "bear", "BEARISH BIAS"
else:
    if price > res1:
        return "bull", "BULLISH"
    elif price > pivot:
        return "bull", "BULLISH BIAS"
    else:
        return "neutral", "NEUTRAL"
```

def price_position_pct(price, s2, r2):
rng = r2 - s2
if rng == 0:
return 50
return max(0, min(100, (price - s2) / rng * 100))

if not data.empty and len(data) >= 10:
cl = float(data[“Close”].iloc[-1])
prev_cl = float(data[“Close”].iloc[-2]) if len(data) > 1 else cl
chg = cl - prev_cl
chg_pct = (chg / prev_cl * 100) if prev_cl != 0 else 0
chg_sign = “+” if chg >= 0 else “”
chg_color = “#00ff88” if chg >= 0 else “#ff3355”

```
pivot, res1, res2, sup1, sup2 = calc_levels(data, min(lookback, len(data)))
bias, entry, tp, sl, rr = calc_trade(cl, pivot, res1, res2, sup1, sup2, data)
pos_pct = price_position_pct(cl, sup2, res2)
bias_type, bias_label = get_bias_class(cl, pivot, res1, sup1, data)

n_used = min(lookback, len(data))
bias_badge_class = "bias-bull" if bias_type == "bull" else "bias-bear" if bias_type == "bear" else "bias-neutral"
alert_class = "alert-bull" if bias_type == "bull" else "alert-bear" if bias_type == "bear" else "alert-neutral"
bar_gradient = "linear-gradient(to right, #00ff88, #ffcc00, #ff3355)"

col_a, col_b = st.columns([1, 1])

with col_a:
    st.markdown(
        "<div class='card'>"
        "<div class='card-label'>LIVE PRICE // " + asset + " // " + date_now + "</div>"
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

# --- Market Context Alert ---
if bias_type == "bull":
    if cl > res2:
        alert_msg = "🚀 <b>BREAKOUT CONFIRMED.</b> " + asset + " trading above R2 at <b>$" + f"{res2:,.2f}" + "</b>. Long bias active. Trail stop above pivot."
    elif cl > res1:
        alert_msg = "📈 <b>APPROACHING R2.</b> Price above R1 — " + asset + " testing upper structure. Long entry near <b>$" + f"{entry:,.2f}" + "</b>, target R2."
    else:
        alert_msg = "📊 <b>BULLISH BIAS.</b> " + asset + " holding above pivot <b>$" + f"{pivot:,.2f}" + "</b>. Look for long entries on pullbacks."
elif bias_type == "bear":
    if cl < sup2:
        alert_msg = "🚨 <b>MAJOR SUPPORT BROKEN.</b> " + asset + " below S2 <b>$" + f"{sup2:,.2f}" + "</b>. Short bias active. Ride the breakdown."
    elif cl < sup1:
        alert_msg = "🔴 <b>APPROACHING S2.</b> Price below S1 — bears in control. Short entry near <b>$" + f"{entry:,.2f}" + "</b>, target S2."
    else:
        alert_msg = "⚠️ <b>BEARISH BIAS.</b> " + asset + " showing bearish momentum. Look for short entries on bounces toward <b>$" + f"{entry:,.2f}" + "</b>."
else:
    alert_msg = "⏸ <b>RANGE BOUND.</b> " + asset + " consolidating between S1 and R1. Wait for break above <b>$" + f"{res1:,.2f}" + "</b> or below <b>$" + f"{sup1:,.2f}" + "</b>."

st.markdown(
    "<div class='card'><div class='card-label'>MARKET CONTEXT</div>"
    "<div class='alert-box " + alert_class + "'>" + alert_msg + "</div></div>",
    unsafe_allow_html=True
)
```

else:
reason = “No data returned. Check the symbol or your connection.” if data.empty else “Only “ + str(len(data)) + “ candles — need at least 10.”
st.error(“OFFLINE // “ + reason)
st.info(“Try refreshing or changing the symbol/timeframe.”)

# ============================================================

# END OF FILE

# ============================================================