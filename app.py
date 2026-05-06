import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime
import pytz

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

c1, c2, c3 = st.columns([2, 2, 1])
with c1:
    asset = st.text_input("SYMBOL", value="GC=F").upper()
with c2:
    tf = st.selectbox("TF", ["1h", "4h", "1d"], index=1)
with c3:
    st.write("")
    if st.button("Refresh"):
        st.cache_data.clear()
        st.rerun()

PERIOD_MAP = {"1h": "10d", "4h": "30d", "1d": "180d"}
LOOKBACK_MAP = {"1h": 48, "4h": 30, "1d": 60}

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
time_now = datetime.now(pytz.timezone("Africa/Johannesburg")).strftime("%H:%M")

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

def build_alert(price, pivot, res1, res2, sup1, sup2, symbol):
    if price > res2:
        return "🚀 <b>BREAKOUT:</b> " + symbol + " is above major resistance <b>$" + f"{res2:,.0f}" + "</b>. Momentum is bullish."
    elif price > res1:
        return "⚠️ <b>RESISTANCE TEST:</b> " + symbol + " approaching <b>$" + f"{res2:,.0f}" + "</b>. A clean break targets higher highs."
    elif price > pivot:
        return "📈 <b>BULLISH BIAS:</b> " + symbol + " holding above pivot <b>$" + f"{pivot:,.0f}" + "</b>. Bulls in control."
    elif price > sup1:
        return "⚠️ <b>PIVOT LOST:</b> Bears testing Support 1 at <b>$" + f"{sup1:,.0f}" + "</b>. Hold here is key."
    elif price > sup2:
        return "🔴 <b>SUPPORT TEST:</b> Break of <b>$" + f"{sup2:,.0f}" + "</b> would be structurally bearish."
    else:
        return "🚨 <b>MAJOR SUPPORT BROKEN:</b> Below <b>$" + f"{sup2:,.0f}" + "</b>. Significant downside risk."

def price_position_pct(price, s2, r2):
    rng = r2 - s2
    if rng == 0:
        return 50
    return max(0, min(100, (price - s2) / rng * 100))

if not data.empty and len(data) >= 5:
    cl = float(data["Close"].iloc[-1])
    pivot, res1, res2, sup1, sup2 = calc_levels(data, min(lookback, len(data)))
    alert_html = build_alert(cl, pivot, res1, res2, sup1, sup2, asset)
    pos_pct = price_position_pct(cl, sup2, res2)
    bar_color = "#ff3366" if pos_pct > 66 else "#ffcc00" if pos_pct > 33 else "#00ffa3"
    n_used = min(lookback, len(data))

    st.markdown("<div style='text-align:center'><span class='label-small'>" + asset + " | " + tf + " | " + time_now + " JHB</span></div>", unsafe_allow_html=True)

    st.markdown("<div class='trade-card'><div style='text-align:center' class='label-small'>Spot Price</div><div class='price-display'>$" + f"{cl:,.2f}" + "</div></div>", unsafe_allow_html=True)

    st.markdown(
        "<div class='trade-card'>"
        "<div class='label-small' style='margin-bottom:8px'>Dynamic Levels (last " + str(n_used) + " candles)</div>"
        "<div class='level-row' style='color:#ff3366'><span>MAJOR RESISTANCE (R2)</span><b>" + f"{res2:,.0f}" + "</b></div>"
        "<div class='level-row' style='color:#ff3366;opacity:0.7'><span>RESISTANCE 1 (R1)</span><b>" + f"{res1:,.0f}" + "</b></div>"
        "<div class='level-row' style='color:#aaa;font-size:0.8rem'><span>PIVOT</span><b>" + f"{pivot:,.0f}" + "</b></div>"
        "<hr style='margin:8px 0;border:0.5px solid #333'>"
        "<div class='level-row' style='color:#00ffa3;opacity:0.7'><span>SUPPORT 1 (S1)</span><b>" + f"{sup1:,.0f}" + "</b></div>"
        "<div class='level-row' style='color:#00ffa3'><span>MAJOR SUPPORT (S2)</span><b>" + f"{sup2:,.0f}" + "</b></div>"
        "<div style='margin-top:12px'>"
        "<div class='label-small' style='margin-bottom:4px'>Price Position in Range</div>"
        "<div style='background:#1a1b22;border-radius:4px;height:8px;overflow:hidden'>"
        "<div style='width:" + f"{pos_pct:.1f}" + "%;height:100%;background:" + bar_color + ";border-radius:4px'></div>"
        "</div>"
        "<div style='display:flex;justify-content:space-between;font-size:0.6rem;color:#555;margin-top:2px'>"
        "<span>S2</span><span>PIVOT</span><span>R2</span>"
        "</div></div></div>",
        unsafe_allow_html=True,
    )

    st.markdown("<div style='background:rgba(255,165,0,0.1);border:1px solid orange;padding:10px;border-radius:8px;margin-top:10px;font-size:0.8rem;'>" + alert_html + "</div>", unsafe_allow_html=True)

else:
    reason = "No data returned. Check the symbol or your connection." if data.empty else "Only " + str(len(data)) + " candles available; need at least 5."
    st.error("⚠️ " + reason)
    st.info("Try refreshing or changing the symbol/timeframe.")
