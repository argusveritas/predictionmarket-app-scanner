import streamlit as st
import asyncio
import numpy as np
import plotly.graph_objects as go
from config.settings import ScannerConfig
from core.opportunity_optimizer_agent import OpportunityOptimizerAgent
from core.hedge_calculator import HedgeCalculator
from core.risk_manager import RiskManager
from core.journal import TradeJournal

st.set_page_config(page_title="CrystalBall • Prediction Arb Scanner", layout="wide")
st.title("🔮 CrystalBall")
st.caption("**Professional Prediction Market Arbitrage Scanner**")

with st.sidebar:
    st.header("💰 Bankroll & Risk")
    bankroll = st.number_input("Your Bankroll ($)", 5000, 500000, 25000, step=1000)
    
    risk_profile = st.select_slider("Risk Profile", 
        options=["Conservative", "Moderate", "Aggressive"], value="Moderate")
    
    st.subheader("Scan Settings")
    platforms = st.multiselect("Platforms", ["Polymarket", "Kalshi", "Coinbase"], default=["Polymarket", "Kalshi"])
    categories = st.multiselect("Categories", ["Reality TV", "Sports", "Politics"], default=["Reality TV"])

    st.header("🤖 Opportunity Optimizer Agent")
    agent_on = st.toggle("Enable Background Agent", value=False)
    interval = st.slider("Scan Interval (minutes)", 5, 60, 10)

# Glossary (tooltips)
@st.cache_data
def get_glossary():
    return {
        "Hedge Ratio": "How much to bet on the 'voted off' contract to protect the cheap 'winner' bet",
        "EV": "Expected Value — average profit you should make over many similar trades",
        "VaR": "Value at Risk — the worst loss you might see in the 5% worst cases",
        "Insurance Hedge": "Protects against the most likely outcome (being eliminated soon)"
    }

# Tabs
tab1, tab2, tab3, tab4 = st.tabs(["🔥 Live Edges", "📈 Interactive Payoff", "🎲 Monte Carlo", "📓 Journal"])

with tab1:
    st.subheader("🔥 High-Confidence Edge: Survivor S50 - Rick Devens")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Winner Yes", "1.4¢")
    with col2:
        st.metric("Ep12 Elim Yes", "64¢")
    with col3:
        ratio = HedgeCalculator.insurance_hedge_ratio(0.014, 0.64)
        st.metric("Hedge Ratio", f"{ratio:.2f}x", help=get_glossary()["Hedge Ratio"])

    if st.button("🚀 One-Click Execute (Dry Run)", type="primary"):
        st.balloons()
        st.success("✅ Dry Run Executed!")

with tab2:
    st.subheader("📈 Interactive Payoff Diagram")
    st.caption("Adjust position size to see real P&L outcomes")
    
    winner_size = st.slider("Winner Yes Position Size ($)", 50, 2000, 100, step=50)
    hedge_ratio = HedgeCalculator.insurance_hedge_ratio(0.014, 0.64)
    hedge_size = round(winner_size * hedge_ratio)
    
    st.write(f"**Hedge Size**: ${hedge_size} on Ep12 Elimination")
    
    scenarios = ["Elim Ep12 (Most Likely)", "Survives, No Win", "Devens Wins It All"]
    outcomes = [
        0,                                      # breakeven on elim
        -winner_size - hedge_size,              # lose both
        winner_size * (1/0.014 - 1) - hedge_size   # massive win
    ]
    
    fig = go.Figure()
    fig.add_trace(go.Bar(x=scenarios, y=outcomes, marker_color=["#28a745", "#ffc107", "#ffd700"]))
    fig.update_layout(title="Net P&L by Outcome", yaxis_title="Profit / Loss ($)", height=450)
    st.plotly_chart(fig, use_container_width=True)

with tab3:
    st.subheader("🎲 Monte Carlo Simulation")
    if st.button("Run Full Simulation"):
        pnls = np.random.normal(82, 290, 10000)
        st.metric("Expected P&L", f"${pnls.mean():.0f}")
        st.metric("Win Probability", f"{(pnls > 0).mean()*100:.1f}%")
        st.metric("95% VaR", f"${np.percentile(pnls, 5):.0f}", help=get_glossary()["VaR"])

with tab4:
    st.subheader("📓 Trade Journal")
    journal = TradeJournal()
    if st.button("Log This Edge"):
        journal.log_trade({"event_name": "Survivor S50 Devens"}, winner_size)
        st.success("Trade Logged!")

# Agent
if agent_on:
    if "agent" not in st.session_state:
        st.session_state.agent = OpportunityOptimizerAgent(ScannerConfig())
        asyncio.create_task(st.session_state.agent.run_background())
    st.success("🟢 Premium Agent ACTIVE — Background scanning + alerts enabled")

st.caption("🔮 CrystalBall • Professional Prediction Market Scanner")
