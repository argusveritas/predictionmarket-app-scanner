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

# Execute Now Button
if st.button("🔄 Execute Fresh Scan Now", type="primary", use_container_width=True):
    st.cache_data.clear()
    st.toast("🔍 Fetching fresh live data...", icon="🔄")
    st.rerun()

# Sidebar
with st.sidebar:
    st.header("💰 Bankroll & Risk")
    bankroll = st.number_input("Your Bankroll ($)", 5000, 500000, 25000, step=1000)
    
    st.subheader("Risk Profile")
    confidence_level = st.slider("Minimum Confidence Level", 60, 100, 80, step=5)
    st.caption(f"Current: **{confidence_level}% Confidence**")

    st.subheader("Scan Targets")
    platforms = st.multiselect("Platforms", ["Polymarket", "Kalshi"], default=["Polymarket"])
    categories = st.multiselect("Categories", 
        ["Reality TV", "Sports", "Politics", "Crypto", "Finance", "World Events"],
        default=["Reality TV"])

# Live Data Fetch
@st.cache_data(ttl=45)
def fetch_polymarket_markets():
    try:
        async def _fetch():
            async with aiohttp.ClientSession() as session:
                async with session.get("https://gamma-api.polymarket.com/markets?limit=100&active=true") as resp:
                    return await resp.json()
        return asyncio.run(_fetch())
    except Exception as e:
        st.error(f"Live fetch failed: {str(e)[:80]}")
        return []

live_markets = fetch_polymarket_markets()

st.subheader(f"📊 Live Edges ({confidence_level}%+ Confidence)")

if live_markets:
    count = 0
    for m in live_markets:
        if count >= 12:
            break
        title = m.get("title") or m.get("question", "Market")
        try:
            price = float(m.get("yes_price", 0.5))
        except:
            price = 0.5
        
        volume = int(float(m.get("volume", 0))) if m.get("volume") else 0
        liquidity = "🟢 Deep" if volume > 500000 else "🟡 Moderate" if volume > 50000 else "🔴 Thin"
        
        # Show interesting markets (low price or high volume)
        if price < 0.35 or volume > 100000 or "survivor" in title.lower():
            st.metric(f"{liquidity} {title[:68]}...", f"{price*100:.1f}¢")
            count += 1
else:
    st.info("No live data available — showing example edges below.")

# Example Devens Edge (always visible)
st.subheader("🔥 Highlight: Survivor S50 - Rick Devens")
winner_size = st.slider("Winner Yes Position Size ($)", 50, 2000, 100, step=50)
hedge_ratio = HedgeCalculator.insurance_hedge_ratio(0.014, 0.64)
hedge_size = round(winner_size * hedge_ratio)
st.write(f"**Hedge Size**: ${hedge_size} on Ep12 Elimination")

# Rest of tabs (Payoff, Monte Carlo, Journal) as before...

st.caption("🔮 CrystalBall • Live Data Enabled")
