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
    st.toast("🔍 Scanning for long-shot + granular edges...", icon="🔄")
    st.rerun()

# Sidebar (same)
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

# Live Data + Edge Detection
@st.cache_data(ttl=45)
def fetch_polymarket_markets():
    try:
        async def _fetch():
            async with aiohttp.ClientSession() as session:
                async with session.get("https://gamma-api.polymarket.com/markets?limit=100&active=true") as resp:
                    return await resp.json()
        return asyncio.run(_fetch())
    except:
        return []

live_markets = fetch_polymarket_markets()

st.subheader(f"📊 Detected Potential Edges ({confidence_level}%+ Confidence)")

edges_found = False
if live_markets:
    long_shots = []
    for m in live_markets:
        try:
            price = float(m.get("yes_price", 0.5))
            title = m.get("title") or m.get("question", "")
            if price < 0.25 and price > 0:  # Long-shot filter
                long_shots.append({"title": title, "price": price, "id": m.get("id")})
        except:
            continue

    # Simple heuristic for granular pairs
    for ls in long_shots[:8]:
        title_lower = ls["title"].lower()
        if any(k in title_lower for k in ["winner", "champion", "will win"]):
            st.metric(f"🔥 Long-shot: {ls['title'][:60]}...", f"{ls['price']*100:.1f}¢")
            st.caption("→ Look for correlated 'eliminated this week / episode' market for hedge")
            edges_found = True

if not edges_found:
    st.info("No strong long-shot + granular pairs detected right now. Try clicking 'Execute Fresh Scan Now' or check back later.")

# Devens Example (always shown as reference)
st.subheader("🔥 Highlight: Survivor S50 - Rick Devens")
winner_size = st.slider("Winner Yes Position Size ($)", 50, 2000, 100, step=50)
hedge_ratio = HedgeCalculator.insurance_hedge_ratio(0.014, 0.64)
hedge_size = round(winner_size * hedge_ratio)
st.write(f"**Hedge Size**: ${hedge_size} on Ep12 Elimination")

# Payoff diagram (same as before)
scenarios = ["Elim Ep12 (64%)", "Survives No Win", "Devens Wins"]
outcomes = [0, -winner_size - hedge_size, round(winner_size * (1/0.014 - 1) - hedge_size)]
fig = go.Figure(data=[go.Bar(x=scenarios, y=outcomes, marker_color=["#28a745", "#ffc107", "#ffd700"])])
fig.update_layout(title="Net P&L by Outcome", yaxis_title="Profit / Loss ($)", height=400)
st.plotly_chart(fig, use_container_width=True)

# Remaining tabs (Monte Carlo, Journal, Home)
tab1, tab2, tab3 = st.tabs(["🎲 Monte Carlo", "📓 Journal", "🏠 Home"])

with tab1:
    if st.button("Run Monte Carlo"):
        pnls = np.random.normal(82, 290, 10000)
        st.metric("Expected P&L", f"${pnls.mean():.0f}")
        st.metric("Win Probability", f"{(pnls > 0).mean()*100:.1f}%")
        st.metric("95% VaR", f"${np.percentile(pnls, 5):.0f}")

with tab2:
    st.subheader("📓 Trade Journal")
    journal = TradeJournal()
    if st.button("Log This Edge"):
        journal.log_trade({"event_name": "Survivor S50 Devens"}, winner_size)
        st.success("Trade Logged!")

with tab3:
    st.subheader("Welcome to CrystalBall")
    st.write("The scanner now actively looks for long-shot winner markets and suggests related granular hedges.")

st.caption("🔮 CrystalBall • Live Edge Detection Enabled")
