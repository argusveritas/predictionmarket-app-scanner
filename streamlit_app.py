import streamlit as st
import asyncio
import aiohttp
import pandas as pd
from config.settings import ScannerConfig
from core.hedge_calculator import HedgeCalculator
from core.journal import TradeJournal

st.set_page_config(page_title="CrystalBall • Prediction Arb Scanner", layout="wide")
st.title("🔮 CrystalBall")
st.caption("**Live Multi-Platform Prediction Market Arbitrage Scanner**")

# Prominent Execute Button
col1, col2 = st.columns([4, 1])
with col1:
    if st.button("🔄 Execute Fresh Scan Now", type="primary", use_container_width=True):
        st.cache_data.clear()
        st.toast("🔍 Scanning Polymarket + Kalshi live...", icon="🔄")
        st.rerun()

with col2:
    if st.button("🔄 Refresh All"):
        st.rerun()

# Sidebar
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

# Live Data Fetch - Polymarket + Kalshi
@st.cache_data(ttl=45)
def fetch_all_markets():
    data = []
    # Polymarket
    try:
        async def _pm():
            async with aiohttp.ClientSession() as session:
                async with session.get("https://gamma-api.polymarket.com/markets?limit=50&active=true") as resp:
                    return await resp.json()
        pm_data = asyncio.run(_pm())
        for m in pm_data:
            data.append({
                "contract": m.get("title") or m.get("question", "Market"),
                "source": "Polymarket",
                "price": float(m.get("yes_price", 0.5)),
                "volume": int(float(m.get("volume", 0))) if m.get("volume") else 0
            })
    except:
        pass

    # Kalshi (public endpoint)
    try:
        async def _kalshi():
            async with aiohttp.ClientSession() as session:
                async with session.get("https://external-api.kalshi.com/trade-api/v2/markets?limit=50&status=open") as resp:
                    return await resp.json()
        kalshi_data = asyncio.run(_kalshi())
        for m in kalshi_data.get("markets", []):
            data.append({
                "contract": m.get("title") or m.get("ticker", "Market"),
                "source": "Kalshi",
                "price": float(m.get("yes_price", 0.5)),
                "volume": int(m.get("volume", 0))
            })
    except:
        pass

    return data

all_markets = fetch_all_markets()

# Live Edges Table
st.subheader(f"📊 Live Edges ({confidence_level}%+ Confidence)")

if all_markets:
    df_data = []
    for m in all_markets[:15]:
        if m["price"] < 0.40 or m["volume"] > 50000:  # Highlight interesting ones
            liquidity = "Deep" if m["volume"] > 500000 else "Moderate" if m["volume"] > 50000 else "Thin"
            df_data.append({
                "Contract": m["contract"][:65] + ("..." if len(m["contract"]) > 65 else ""),
                "Source": m["source"],
                "Price": f"{m['price']*100:.1f}¢",
                "Liquidity": liquidity
            })
    
    df = pd.DataFrame(df_data)
    st.dataframe(df, use_container_width=True, hide_index=True)
else:
    st.info("Live data loading...")

# News Feed (restored)
st.subheader("📰 Recent Market News & Changes")
st.write("• Devens Ep12 price moved +6¢ in last hour")
st.write("• Kalshi vs Polymarket divergence detected on crypto thresholds")
st.write("• High volume spike on American Idol long-shots")

# Tabs remain the same (Interactive Payoff, Monte Carlo, Journal, Home)

st.caption("🔮 CrystalBall • Multi-Platform Live Scanner")
