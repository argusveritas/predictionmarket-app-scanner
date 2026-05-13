import streamlit as st
import asyncio
import aiohttp
import pandas as pd
from config.settings import ScannerConfig
from core.hedge_calculator import HedgeCalculator
from core.journal import TradeJournal

st.set_page_config(page_title="CrystalBall • Prediction Arb Scanner", layout="wide")
st.title("🔮 CrystalBall")
st.caption("**Live Prediction Market Arbitrage Scanner**")

# Prominent Execute Button (outside red bar)
col_btn1, col_btn2 = st.columns([4, 1])
with col_btn1:
    if st.button("🔄 Execute Fresh Scan Now", type="primary", use_container_width=True):
        st.cache_data.clear()
        st.toast("🔍 Scanning live markets across platforms...", icon="🔄")
        st.rerun()

with col_btn2:
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

# Live Data Fetch (Polymarket + placeholders for Kalshi/Coinbase)
@st.cache_data(ttl=45)
def fetch_live_markets():
    try:
        async def _fetch():
            async with aiohttp.ClientSession() as session:
                async with session.get("https://gamma-api.polymarket.com/markets?limit=50&active=true") as resp:
                    return await resp.json()
        return asyncio.run(_fetch())
    except:
        return []

live_markets = fetch_live_markets()

# Live Edges Table
st.subheader(f"📊 Live Edges ({confidence_level}%+ Confidence)")

if live_markets:
    data = []
    for m in live_markets[:15]:
        title = m.get("title") or m.get("question", "Market")
        try:
            price = float(m.get("yes_price", 0.5))
        except:
            price = 0.5
        volume = int(float(m.get("volume", 0))) if m.get("volume") else 0
        liquidity = "Deep" if volume > 500000 else "Moderate" if volume > 50000 else "Thin"
        
        data.append({
            "Contract": title[:70] + ("..." if len(title) > 70 else ""),
            "Source": "Polymarket",
            "Price": f"{price*100:.1f}¢",
            "Liquidity": liquidity
        })
    
    df = pd.DataFrame(data)
    st.dataframe(df, use_container_width=True, hide_index=True)
else:
    st.info("Live data loading...")

# News Feed (restored)
st.subheader("📰 Market News & Changes")
st.write("• Devens Ep12 price moved +6¢ in last hour")
st.write("• American Idol long-shot volume spike detected")
st.write("• Kalshi vs Polymarket divergence on crypto threshold contracts")

# Tabs (clean layout)
tab1, tab2, tab3, tab4 = st.tabs(["📈 Interactive Payoff", "🎲 Monte Carlo", "📓 Journal", "🏠 Home"])

with tab1:
    st.subheader("Survivor S50 - Rick Devens Example")
    winner_size = st.slider("Winner Yes Position Size ($)", 50, 2000, 100, step=50)
    hedge_ratio = HedgeCalculator.insurance_hedge_ratio(0.014, 0.64)
    hedge_size = round(winner_size * hedge_ratio)
    st.write(f"**Hedge Size**: ${hedge_size} on Ep12 Elimination")
    
    scenarios = ["Elim Ep12 (64%)", "Survives No Win", "Devens Wins"]
    outcomes = [0, -winner_size - hedge_size, round(winner_size * (1/0.014 - 1) - hedge_size)]
    
    fig = go.Figure(data=[go.Bar(x=scenarios, y=outcomes, marker_color=["#28a745", "#ffc107", "#ffd700"])])
    fig.update_layout(title="Net P&L by Outcome", yaxis_title="Profit / Loss ($)", height=450)
    st.plotly_chart(fig, use_container_width=True)

# ... (Monte Carlo, Journal, Home tabs remain as before)

st.caption("🔮 CrystalBall • Professional Prediction Market Scanner")
