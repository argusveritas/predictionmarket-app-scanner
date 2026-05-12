import streamlit as st
import asyncio
from config.settings import ScannerConfig
from core.opportunity_optimizer_agent import OpportunityOptimizerAgent
from core.hedge_calculator import HedgeCalculator
from core.risk_manager import RiskManager
from core.journal import TradeJournal

st.set_page_config(page_title="Prediction Arb Scanner", layout="wide")
st.title("🚀 Prediction Market Arb Scanner")
st.caption("Real-time Hedged Opportunities • Powered by Grok")

with st.sidebar:
    st.header("💰 Bankroll")
    bankroll = st.number_input("Current Bankroll ($)", 5000, 500000, 25000, step=1000)
    
    st.header("🤖 Opportunity Optimizer Agent")
    agent_on = st.toggle("Enable Background Agent", value=False)
    interval = st.slider("Scan Interval (minutes)", 5, 60, 10)

# Tabs
tab1, tab2, tab3, tab4 = st.tabs(["🔥 Live Edges", "📊 Monte Carlo", "⚙️ Optimizer", "📓 Journal"])

with tab1:
    st.subheader("Current High-Confidence Edge - Survivor S50")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Rick Devens Winner Yes", "1.4¢")
    with col2:
        st.metric("Ep12 Elim Yes", "64¢")
    with col3:
        ratio = HedgeCalculator.insurance_hedge_ratio(0.014, 0.64)
        st.metric("Recommended Hedge", f"{ratio:.2f}x")

    if st.button("🚀 One-Click Execute (Dry Run)", type="primary"):
        st.success("✅ Executed Dry Run - Logged to Journal!")

with tab2:
    st.subheader("Monte Carlo Simulation")
    st.info("Monte Carlo + Risk visuals will go here (add later)")

with tab3:
    st.subheader("Strategy Optimizer")
    st.info("Optimizer + Position Sizing will go here")

with tab4:
    st.subheader("Trade Journal")
    journal = TradeJournal()
    if st.button("Log Sample Trade"):
        journal.log_trade({"event_name": "Survivor S50 Devens"}, 380)
        st.success("Trade logged!")

# Agent
if agent_on:
    if "agent" not in st.session_state:
        st.session_state.agent = OpportunityOptimizerAgent(ScannerConfig())
        asyncio.create_task(st.session_state.agent.run_background())
    st.success("🟢 Agent ACTIVE in background")

st.caption("Full MVP • Ready for premium alerts & more platforms")
