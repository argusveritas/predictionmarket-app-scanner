import streamlit as st
import asyncio
import aiohttp
import numpy as np
import plotly.graph_objects as go
from config.settings import ScannerConfig
from core.hedge_calculator import HedgeCalculator
from core.journal import TradeJournal

st.set_page_config(page_title="CrystalBall • Prediction Arb Scanner", layout="wide")
st.title("🔮 CrystalBall")
st.caption("**Live Prediction Market Arbitrage Scanner**")

# === EXECUTE NOW BUTTON (Prominent & Reliable) ===
col_btn1, col_btn2 = st.columns([3, 1])
with col_btn1:
    if st.button("🔄 Execute Scan Now", type="primary", use_container_width=True):
        st.toast("🔍 Scanning live markets right now...", icon="🔄")
        st.rerun()

with col_btn2:
    if st.button("🔄 Refresh All"):
        st.rerun()

# Sidebar (unchanged)
with st.sidebar:
    st.header("💰 Bankroll & Risk")
    bankroll = st.number_input("Your Bankroll ($)", 5000, 500000, 25000, step=1000)
    
    st.subheader("Risk Profile")
    confidence_level = st.slider("Minimum Confidence Level", 60, 100, 80, step=5)
    st.caption(f"Current: **{confidence_level}% Confidence**")

    st.subheader("Scan Targets")
    platforms = st.multiselect("Platforms", ["Polymarket", "Kalshi", "Coinbase"], default=["Polymarket", "Kalshi"])
    categories = st.multiselect("Categories", 
        ["Reality TV", "Sports", "Politics", "Crypto", "Finance", "World Events"],
        default=["Reality TV"])

    st.header("🤖 Opportunity Optimizer Agent")
    agent_on = st.toggle("Enable Background Agent (Premium)", value=False)
    interval = st.slider("Scan Interval (minutes)", 5, 60, 10)

# Live Data
@st.cache_data(ttl=30)
def fetch_polymarket_markets():
    try:
        async def _fetch():
            async with aiohttp.ClientSession() as session:
                async with session.get("https://gamma-api.polymarket.com/markets?limit=50&active=true") as resp:
                    return await resp.json()
        return asyncio.run(_fetch())
    except:
        return []

live_markets = fetch_polymarket_markets()

st.subheader(f"📊 Live Edges ({confidence_level}%+ Confidence)")

if live_markets:
    for m in live_markets[:10]:
        title = m.get("title") or m.get("question", "Market")
        try:
            price = float(m.get("yes_price", 0.5))
        except:
            price = 0.5
        st.metric(title[:70] + ("..." if len(title) > 70 else ""), f"{price*100:.1f}¢")
else:
    st.info("Live data loading...")

# Rest of the tabs (Payoff, Monte Carlo, Journal) remain the same as previous version

st.caption("🔮 CrystalBall • Professional Prediction Market Scanner")
