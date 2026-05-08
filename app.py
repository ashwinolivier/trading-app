# ============================================================
# GOLD MASTER - Trading Terminal v2.2
# Added:
# - 20 EMA trend filter
# - 4-factor confluence system
#
# Bearish conditions:
# 1. Price below pivot
# 2. Momentum weak
# 3. Lower lows structure
# 4. Price below EMA20
#
# Requires 3/4 bearish votes for SHORT bias
#
# Install:
# pip install streamlit yfinance pandas pytz
#
# Run:
# streamlit run app.py
# ============================================================

import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime
import pytz

# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="GOLD MASTER",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ============================================================
# STYLING
# ============================================================

st.markdown("""
<style>

@import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Rajdhani:wght@400;600;700&display=swap');

* {
    box-sizing: border-box;
}

body, .stApp {
    background-color: #060810;
    color: #c8d0e0;
    font-family: 'Rajdhani', sans-serif;
}

.block-container {
    padding: 1rem 1rem 2rem 1rem !important;
    max-width: 100% !important;
}

header, footer {
    display: none !important;
}

.stTextInput > div > div > input,
.stSelectbox > div > div {
    background: #0d1117 !important;
    border: 1px solid #1e2a3a !important;
    color: #c8d0e0 !important;
    font-family: 'Share Tech Mono', monospace !important;
    border-radius: 4px !important;
}

.stButton > button {
    background: #0d1117 !important;
    border: 1px solid #1e3a5f !important;
    color: #4a9eff !important;
    font-family: 'Rajdhani', sans-serif !important;
    font-weight: 700 !important;
    letter-spacing: 2px !important;
    border-radius: 4px !important;
    padding: 0.4rem 1rem !important;
}

.stButton > button:hover {
    background: #1e3a5f !important;
    border-color: #4a9eff !important;
}

label {
    color: #4a6080 !important;
    font-size: 0.65rem !important;
    letter-spacing: 2px !important;
    font-weight: 700 !important;
}

.terminal-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    border-bottom: 1px solid #1e2a3a;
    padding-bottom: 10px;
    margin-bottom: 16px;
}

.terminal-title {
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.7rem;
    color: #4a6080;
    letter-spacing: 4px;
}

.terminal-dot {
    width: 6px;
    height: 6px;
    border-radius: 50%;
    display: inline-block;
    margin-right: 5px;
}

.dot-green {
    background: #00ff88;
}

.dot-yellow {
    background: #ffcc00;
}

.dot-red {
    background: #ff3355;
}

.card {
    background: #0a0e18;
    border: 1px solid #1a2235;
    border-radius: 8px;
    padding: 16px;
    margin-bottom: 12px;
}

.card-label {
    font-size: 0.58rem;
    letter-spacing: 3px;
    color: #3a5070;
    font-weight: 700;
    margin-bottom: 10px;
    text-transform: uppercase;
}

.price-big {
    font-family: 'Share Tech Mono', monospace;
    font-size: 3rem;
    text-align: center;
    color: white;
}

.bias-badge {
    display: inline-block;
    padding: 4px 12px;
    border-radius: 3px;
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 2px;
}

.bias-bull {
    background: rgba(0,255,136,0.1);
    border: 1px solid #00ff88;
    color: #00ff88;
}

.bias-bear {
    background: rgba(255,51,85,0.1);
    border: 1px solid #ff3355;
    color: #ff3355;
}

.bias-neutral {
    background: rgba(255,204,0,0.1);
    border: 1px solid #ffcc00;
    color: #ffcc00;
}

.level-row {
    display: flex;
    justify-content: space-between;
    padding: 6px 0;
    border-bottom: 1px solid #101826;
}

.trade-block {
    display: flex;
    gap: 10px;
    flex-wrap: wrap;
}

.trade-cell {
    flex: 1;
    min-width: 150px;
    background: #060810;
    border: 1px solid #1a2235;
    border-radius: 6px;
    padding: 12px;
    text-align: center;
}

.trade-cell-label {
    font-size: 0.55rem;
    letter-spacing: 2px;
    color: #3a5070;
}

.trade-cell-val {
    font-family: 'Share Tech Mono', monospace;
    font-size: 1rem;
    margin-top: 4px;
}

.alert-box {
    border-radius: 6px;
    padding: 12px;
    margin-top: 8px;
}

.alert-bull {
    background: rgba(0,255,136,0.08);
    border-left: 3px solid #00ff88;
}

.alert-bear {
    background: rgba(255,51,85,0.08);
    border-left: 3px solid #ff3355;
}

.alert-neutral {
    background: rgba(255,204,0,0.08);
    border-left: 3px solid #ffcc00;
}

</style>
""", unsafe_allow_html=True)

# ============================================================
# HEADER
# ============================================================

st.markdown("""
<div class="terminal-header">
<div class="terminal-title">
<span class="terminal-dot dot-green"></span>
<span class="terminal-dot dot-yellow"></span>
<span class="terminal-dot dot-red"></span>
GOLD MASTER // TRADING TERMINAL v2.2
</div>
</div>
""", unsafe_allow_html=True)

# ============================================================
# INPUTS
# ============================================================

c1, c2, c3, c4 = st.columns([2, 2, 1, 1])

with c1:
    asset = st.text_input("SYMBOL", value="GC=F").upper()

with c2:
    tf = st.selectbox("TIMEFRAME", ["1h", "4h", "1d"], index=1)

with c3:
    risk_pct = st.number_input(
        "RISK %",
        min_value=0.1,
        max_value=10.0,
        value=1.0,
        step=0.1
    )

with c4:
    st.write("")
    st.write("")

    if st.button("REFRESH"):
        st.cache_data.clear()
        st.rerun()

# ============================================================
# MAPS
# ============================================================

PERIOD_MAP = {
    "1h": "10d",
    "4h": "30d",
    "1d": "180d"
}

LOOKBACK_MAP = {
    "1h": 48,
    "4h": 30,
    "1d": 60
}

YF_INTERVAL_MAP = {
    "1h": "1h",
    "4h": "1h",
    "1d": "1d"
}

# ============================================================
# FETCH DATA
# ============================================================

@st.cache_data(ttl=60)
def fetch_data(ticker, interval, period):

    try:

        df = yf.download(
            ticker,
            period=period,
            interval=interval,
            auto_adjust=True,
            progress=False
        )

        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        return df

    except Exception:
        return pd.DataFrame()

period = PERIOD_MAP[tf]
lookback = LOOKBACK_MAP[tf]

data = fetch_data(
    asset,
    YF_INTERVAL_MAP[tf],
    period
)

# ============================================================
# TIME
# ============================================================

jhb = pytz.timezone("Africa/Johannesburg")

time_now = datetime.now(jhb).strftime("%H:%M:%S")
date_now = datetime.now(jhb).strftime("%d %b %Y")

# ============================================================
# FUNCTIONS
# ============================================================

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


def is_bearish_market(price, pivot, df):

    # ========================================================
    # FILTER 1 - BELOW PIVOT
    # ========================================================

    below_pivot = price < pivot

    # ========================================================
    # FILTER 2 - MOMENTUM
    # ========================================================

    if len(df) >= 5:
        momentum_up = (
            float(df["Close"].iloc[-1]) >
            float(df["Close"].iloc[-5])
        )
    else:
        momentum_up = False

    # ========================================================
    # FILTER 3 - LOWER LOWS
    # ========================================================

    if len(df) >= 10:
        lower_lows = (
            float(df["Low"].iloc[-1]) <
            float(df["Low"].iloc[-10])
        )
    else:
        lower_lows = False

    # ========================================================
    # FILTER 4 - EMA20 TREND
    # ========================================================

    ema20 = (
        df["Close"]
        .ewm(span=20)
        .mean()
        .iloc[-1]
    )

    below_ema = price < ema20

    # ========================================================
    # CONFLUENCE
    # ========================================================

    bearish_votes = sum([
        below_pivot,
        not momentum_up,
        lower_lows,
        below_ema
    ])

    return bearish_votes >= 3


def calc_trade(price, pivot, res1, res2, sup1, sup2, df):

    full_range = res2 - sup2

    buffer = full_range * 0.015

    bearish = is_bearish_market(
        price,
        pivot,
        df
    )

    if bearish:

        bias = "SHORT"

        entry = round(
            min(pivot, sup1 + buffer),
            2
        )

        sl = round(
            entry + (res1 - entry) * 0.5,
            2
        )

        tp = round(
            sup2 + buffer,
            2
        )

    else:

        bias = "LONG"

        entry = round(
            max(pivot, res1 - buffer),
            2
        )

        sl = round(
            entry - (entry - sup1) * 0.5,
            2
        )

        tp = round(
            res2 - buffer,
            2
        )

    risk = abs(entry - sl)
    reward = abs(tp - entry)

    rr = (
        round(reward / risk, 2)
        if risk > 0 else 0
    )

    return bias, entry, tp, sl, rr


def get_bias_class(price, pivot, res1, sup1, df):

    bearish = is_bearish_market(
        price,
        pivot,
        df
    )

    if bearish:

        if price < sup1:
            return "bear", "BEARISH"

        return "bear", "BEARISH BIAS"

    else:

        if price > res1:
            return "bull", "BULLISH"

        elif price > pivot:
            return "bull", "BULLISH BIAS"

        return "neutral", "NEUTRAL"

# ============================================================
# MAIN
# ============================================================

if not data.empty and len(data) >= 20:

    cl = float(data["Close"].iloc[-1])

    prev_cl = float(data["Close"].iloc[-2])

    chg = cl - prev_cl

    chg_pct = (
        (chg / prev_cl) * 100
        if prev_cl != 0 else 0
    )

    chg_sign = "+" if chg >= 0 else ""

    chg_color = (
        "#00ff88"
        if chg >= 0 else "#ff3355"
    )

    pivot, res1, res2, sup1, sup2 = calc_levels(
        data,
        min(lookback, len(data))
    )

    bias, entry, tp, sl, rr = calc_trade(
        cl,
        pivot,
        res1,
        res2,
        sup1,
        sup2,
        data
    )

    bias_type, bias_label = get_bias_class(
        cl,
        pivot,
        res1,
        sup1,
        data
    )

    ema20 = (
        data["Close"]
        .ewm(span=20)
        .mean()
        .iloc[-1]
    )

    # ========================================================
    # COLORS
    # ========================================================

    bias_badge_class = (
        "bias-bull"
        if bias_type == "bull"
        else "bias-bear"
        if bias_type == "bear"
        else "bias-neutral"
    )

    alert_class = (
        "alert-bull"
        if bias_type == "bull"
        else "alert-bear"
        if bias_type == "bear"
        else "alert-neutral"
    )

    # ========================================================
    # LAYOUT
    # ========================================================

    col1, col2 = st.columns([1, 1])

    with col1:

        st.markdown(f"""
        <div class='card'>

        <div class='card-label'>
        LIVE PRICE // {asset}
        </div>

        <div class='price-big'>
        ${cl:,.2f}
        </div>

        <div style='text-align:center;
                    color:{chg_color};
                    margin-top:8px;'>

        {chg_sign}{chg:,.2f}
        ({chg_sign}{chg_pct:.2f}%)

        </div>

        <div style='text-align:center;
                    margin-top:10px;'>

        <span class='bias-badge {bias_badge_class}'>
        {bias_label}
        </span>

        </div>

        <div style='text-align:center;
                    margin-top:16px;
                    color:#4a9eff;'>

        EMA20: {ema20:,.2f}

        </div>

        <div style='text-align:center;
                    margin-top:12px;
                    font-size:0.75rem;
                    color:#4a6080;'>

        {date_now} | {time_now} JHB

        </div>

        </div>
        """, unsafe_allow_html=True)

    with col2:

        st.markdown(f"""
        <div class='card'>

        <div class='card-label'>
        KEY LEVELS
        </div>

        <div class='level-row'>
        <span>R2</span>
        <span>{res2:,.2f}</span>
        </div>

        <div class='level-row'>
        <span>R1</span>
        <span>{res1:,.2f}</span>
        </div>

        <div class='level-row'>
        <span>PIVOT</span>
        <span>{pivot:,.2f}</span>
        </div>

        <div class='level-row'>
        <span>S1</span>
        <span>{sup1:,.2f}</span>
        </div>

        <div class='level-row'>
        <span>S2</span>
        <span>{sup2:,.2f}</span>
        </div>

        </div>
        """, unsafe_allow_html=True)

    # ========================================================
    # TRADE CARD
    # ========================================================

    direction_color = (
        "#00ff88"
        if bias == "LONG"
        else "#ff3355"
    )

    st.markdown(f"""
    <div class='card'>

    <div class='card-label'>
    TRADE SETUP
    </div>

    <div class='trade-block'>

    <div class='trade-cell'>
    <div class='trade-cell-label'>BIAS</div>
    <div class='trade-cell-val'
         style='color:{direction_color};'>
    {bias}
    </div>
    </div>

    <div class='trade-cell'>
    <div class='trade-cell-label'>ENTRY</div>
    <div class='trade-cell-val'>
    {entry:,.2f}
    </div>
    </div>

    <div class='trade-cell'>
    <div class='trade-cell-label'>TP</div>
    <div class='trade-cell-val'
         style='color:#00ff88;'>
    {tp:,.2f}
    </div>
    </div>

    <div class='trade-cell'>
    <div class='trade-cell-label'>SL</div>
    <div class='trade-cell-val'
         style='color:#ff3355;'>
    {sl:,.2f}
    </div>
    </div>

    <div class='trade-cell'>
    <div class='trade-cell-label'>RR</div>
    <div class='trade-cell-val'
         style='color:#ffcc00;'>
    1 : {rr}
    </div>
    </div>

    </div>

    </div>
    """, unsafe_allow_html=True)

    # ========================================================
    # MARKET CONTEXT
    # ========================================================

    if bias_type == "bull":

        alert_msg = (
            f"📈 Bullish structure above EMA20 "
            f"and pivot support."
        )

    elif bias_type == "bear":

        alert_msg = (
            f"🔴 Bearish structure confirmed "
            f"below EMA20 and pivot."
        )

    else:

        alert_msg = (
            "⏸ Market consolidating. "
            "Wait for confirmation."
        )

    st.markdown(f"""
    <div class='card'>

    <div class='card-label'>
    MARKET CONTEXT
    </div>

    <div class='alert-box {alert_class}'>
    {alert_msg}
    </div>

    </div>
    """, unsafe_allow_html=True)

# ============================================================
# ERROR
# ============================================================

else:

    st.error(
        "OFFLINE // Not enough data returned."
    )

    st.info(
        "Try another symbol or timeframe."
    )

# ============================================================
# END
# ============================================================