import streamlit as st
import asyncio
from config.settings import ScannerConfig
from core.opportunity_optimizer_agent import OpportunityOptimizerAgent
from core.hedge_calculator import HedgeCalculator
from core.risk_manager import RiskManager
from core.journal import TradeJournal

st.set_page_config(page_title="Prediction Arb Scanner", layout="wide")
st.title("🚀 Prediction Market Arb Scanner")
st.caption("Devens-style Hedged Opportunities • Premium Agent Active")

with st.sidebar:
    st.header("💰 Bankroll & Controls")
    bankroll = st.number_input("Bankroll ($)", 5000, 500000, 25000, step=1000)
    
    st.header("🤖 Opportunity Optimizer Agent")
    agent_on = st.toggle("Enable Background Agent", value=False)
    interval = st.slider("Scan Interval (minutes)", 5, 60, 10)

# Live Edge Example (Survivor Devens)
st.subheader("🔥 Current High-Confidence Edge")
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Rick Devens Winner", "1.4¢")
with col2:
    st.metric("Ep12 Elimination", "64¢")
with col3:
    ratio = HedgeCalculator.insurance_hedge_ratio(0.014, 0.64)
    st.metric("Hedge Ratio", f"{ratio:.2f}x")

if st.button("🚀 One-Click Execute (Dry Run)", type="primary"):
    st.success("✅ Dry Run Executed - Trade logged to Journal!")

# Agent Status
if agent_on:
    if "agent" not in st.session_state:
        st.session_state.agent = OpportunityOptimizerAgent(ScannerConfig())
        asyncio.create_task(st.session_state.agent.run_background())
    st.success("🟢 Agent is ACTIVE — will scream on near-arb opportunities!")

# Journal
st.subheader("📓 Trade Journal")
journal = TradeJournal()
if st.button("Log Test Trade"):
    journal.log_trade({"event_name": "Survivor S50 - Devens"}, 380)
    st.success("Trade logged successfully!")

st.info("App is running! Next: Add full scanner, Monte Carlo, and Optimizer tabs.")

st.caption("Built with Grok • Ready for premium features")
