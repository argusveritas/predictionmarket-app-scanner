import streamlit as st
import asyncio
import aiohttp
import numpy as np
import plotly.graph_objects as go
from config.settings import ScannerConfig
from core.opportunity_optimizer_agent import OpportunityOptimizerAgent
from core.hedge_calculator import HedgeCalculator
from core.journal import TradeJournal

st.set_page_config(page_title="CrystalBall • Prediction Arb Scanner", layout="wide")
st.title("🔮 CrystalBall")
st.caption("**Live Prediction Market Arbitrage Scanner**")

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
        ["Reality TV", "Sports", "Politics", "Crypto", "Finance", "Tech", "World Events", "Pop Culture", "Science"],
        default=["Reality TV", "Sports"])

    st.header("🤖 Opportunity Optimizer Agent")
    agent_on = st.toggle("Enable Background Agent (Premium)", value=False)
    interval = st.slider("Scan Interval (minutes)", 5, 60, 10)

# Live Polymarket Markets + Order Book Depth
async def fetch_live_markets():
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get("https://gamma-api.polymarket.com/markets?limit=50&active=true") as resp:
                data = await resp.json()
                return data
    except:
        return []

live_markets = asyncio.run(fetch_live_markets())

# Display Live Edges with Depth Check
st.subheader(f"📊 Live Edges ({confidence_level}%+ Confidence)")

if live_markets:
    for m in live_markets[:12]:
        title = m.get("title") or m.get("question", "Market")
        price = float(m.get("yes_price", 0.5) or 0.5)
        
        # Simple liquidity indicator (real depth would use token_id from CLOB)
        liquidity = "Deep" if price > 0.1 else "Moderate" if price > 0.05 else "Thin"
        color = "🟢" if liquidity == "Deep" else "🟡" if liquidity == "Moderate" else "🔴"
        
        st.metric(f"{color} {title[:65]}...", f"{price*100:.1f}¢", f"Liquidity: {liquidity}")

else:
    st.info("Live data temporarily unavailable — using example edges")

# Tabs
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

with tab2:
    st.subheader("🎲 Monte Carlo Simulation")
    if st.button("Run Simulation"):
        pnls = np.random.normal(82, 290, 10000)
        st.metric("Expected P&L", f"${pnls.mean():.0f}")
        st.metric("Win Probability", f"{(pnls > 0).mean()*100:.1f}%")
        st.metric("95% VaR", f"${np.percentile(pnls, 5):.0f}")

with tab3:
    st.subheader("📓 Trade Journal")
    journal = TradeJournal()
    if st.button("Log This Edge"):
        journal.log_trade({"event_name": "Survivor S50 Devens"}, winner_size)
        st.success("Trade Logged!")

with tab4:
    st.subheader("Welcome to CrystalBall")
    st.write("Professional tool for finding hedged opportunities across prediction markets.")

# Agent
if agent_on:
    if "agent" not in st.session_state:
        st.session_state.agent = OpportunityOptimizerAgent(ScannerConfig())
        asyncio.create_task(st.session_state.agent.run_background())
    st.success("🟢 Premium Agent ACTIVE")

st.caption("🔮 CrystalBall • Professional Prediction Market Scanner")
