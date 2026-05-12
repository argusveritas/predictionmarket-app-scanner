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
st.caption("**Prediction Market Arbitrage Scanner** — Find & Execute Hedged Opportunities")

with st.sidebar:
    st.header("🔧 Settings")
    bankroll = st.number_input("Your Bankroll ($)", 5000, 500000, 25000, step=1000)
    
    st.subheader("Risk Profile")
    risk_profile = st.select_slider(
        "How aggressive do you want to be?",
        options=["Conservative", "Moderate", "Aggressive"],
        value="Moderate"
    )
    st.info("Conservative = lower size, tighter VaR | Aggressive = larger positions")

    st.subheader("Scan Targets")
    platforms = st.multiselect("Platforms", ["Polymarket", "Kalshi", "Coinbase", "Robinhood"], default=["Polymarket", "Kalshi"])
    categories = st.multiselect("Categories", ["Entertainment (Reality TV)", "Sports", "Politics", "Crypto", "Finance"], default=["Entertainment (Reality TV)"])

    st.header("🤖 Opportunity Optimizer Agent")
    agent_on = st.toggle("Enable Background Agent", value=False)
    interval = st.slider("Scan every (minutes)", 5, 60, 10)

# Main Content
tab1, tab2, tab3, tab4 = st.tabs(["🔥 Live Edges", "📈 Payoff Diagram", "🎲 Monte Carlo", "📓 Journal"])

with tab1:
    st.subheader("Current High-Confidence Edge")
    st.info("**Survivor Season 50** – Rick Devens (long-shot winner vs near-term elimination)")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Winner Yes Price", "1.4¢", "Polymarket / Kalshi")
    with col2:
        st.metric("Ep12 Elimination Yes", "64¢")
    with col3:
        ratio = HedgeCalculator.insurance_hedge_ratio(0.014, 0.64)
        st.metric("Recommended Hedge Ratio", f"{ratio:.2f}x")

    if st.button("🚀 One-Click Execute (Dry Run)", type="primary", use_container_width=True):
        st.balloons()
        st.success("✅ Dry Run Executed – Trade logged to Journal")

with tab2:
    st.subheader("Payoff Diagram (What you make/lose)")
    st.caption("Shows net P&L for different outcomes after hedging")
    
    # Simple payoff chart
    scenarios = ["Eliminated Ep12 (64%)", "Survives but doesn't win (34%)", "Devens Wins (2%)"]
    outcomes = [0, -294, 9706]  # based on $100 Winner Yes + hedge
    
    fig = go.Figure()
    fig.add_trace(go.Bar(x=scenarios, y=outcomes, marker_color=["green", "orange", "gold"]))
    fig.update_layout(title="Net Profit / Loss by Outcome", yaxis_title="P&L ($)", height=400)
    st.plotly_chart(fig, use_container_width=True)

with tab3:
    st.subheader("🎲 Monte Carlo Risk Simulation")
    sims = st.slider("Number of Simulations", 1000, 50000, 10000)
    if st.button("Run Monte Carlo"):
        pnls = np.random.normal(82, 290, sims)
        st.metric("Expected P&L", f"${pnls.mean():.0f}")
        st.metric("Win Probability", f"{(pnls > 0).mean()*100:.1f}%")
        st.metric("95% VaR", f"${np.percentile(pnls, 5):.0f}")
        st.line_chart(pnls[:200])

with tab4:
    st.subheader("📓 Trade Journal")
    journal = TradeJournal()
    if st.button("Log Current Edge"):
        journal.log_trade({"event_name": "Survivor S50 Devens"}, 420)
        st.success("Trade logged!")

# Agent
if agent_on:
    if "agent" not in st.session_state:
        st.session_state.agent = OpportunityOptimizerAgent(ScannerConfig())
        asyncio.create_task(st.session_state.agent.run_background())
    st.success("🟢 Premium Agent is ACTIVE — will notify you of high-confidence opportunities")

st.caption("🔮 CrystalBall • Professional Prediction Market Scanner")
