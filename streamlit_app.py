import streamlit as st
import asyncio
from config.settings import ScannerConfig
from core.opportunity_optimizer_agent import OpportunityOptimizerAgent
from core.hedge_calculator import HedgeCalculator
from core.risk_manager import RiskManager
from core.journal import TradeJournal
st.set_page_config(page_title="Prediction Arb Scanner", layout="wide")
st.title("🚀 Prediction Market Arb Scanner - MVP v1.0")

# Sidebar
with st.sidebar:
    st.header("💰 Bankroll")
    bankroll = st.number_input("Current Bankroll ($)", 5000, 500000, 25000, step=1000)
    
    st.header("🤖 Opportunity Optimizer Agent")
    agent_on = st.toggle("Enable Background Agent", value=False)
    interval = st.slider("Scan Interval (minutes)", 5, 60, 10)

# Main Dashboard
st.subheader("🔥 Current Edge (Devens Example)")
col1, col2 = st.columns(2)
with col1:
    st.metric("Rick Devens Winner Yes", "1.4¢")
    st.metric("Ep12 Elim Yes", "64¢")
with col2:
    hedge_ratio = HedgeCalculator.insurance_hedge_ratio(0.014, 0.64)
    st.metric("Recommended Hedge Ratio", f"{hedge_ratio:.2f}x")
    st.metric("EV", "+8.2%")

if st.button("🚀 One-Click Execute (Dry Run)", type="primary"):
    st.success("Dry Run Executed! (Check Journal below)")

# Agent Control
if agent_on:
    if "agent" not in st.session_state:
        st.session_state.agent = OpportunityOptimizerAgent(ScannerConfig())
        asyncio.create_task(st.session_state.agent.run_background())
    st.success("🟢 Agent is running — will alert on high-confidence opportunities")

# Journal
st.subheader("📓 Trade Journal")
journal = TradeJournal()
if st.button("Log Sample Trade"):
    journal.log_trade({"event_name": "Survivor S50 Devens"}, 380, notes="Insurance hedge")
    st.success("Trade logged!")

st.info("✅ Core modules loaded. Expand scanner, Monte Carlo, and optimizer next.")

st.caption("Built collaboratively with Grok • Premium Agent feature active")
