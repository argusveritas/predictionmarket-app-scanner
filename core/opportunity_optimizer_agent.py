# core/opportunity_optimizer_agent.py
import asyncio
import time
from typing import Dict, Optional
import streamlit as st
from config.settings import ScannerConfig
from scanner import PredictionScanner
from core.risk_manager import RiskManager
from core.optimizer import StrategyOptimizer
from core.journal import TradeJournal

class OpportunityOptimizerAgent:
    def __init__(self, config: ScannerConfig):
        self.config = config
        self.scanner = PredictionScanner(config)
        self.optimizer = StrategyOptimizer(config)
        self.risk_manager = RiskManager(config)
        self.journal = TradeJournal()
        self.is_running = False
        self.interval_minutes = 10
        self.screaming_buy_threshold = 0.92  # 92% composite confidence (tunable)

    async def run_background(self):
        """Background loop — called via asyncio task"""
        self.is_running = True
        st.toast("🚀 Opportunity Optimizer Agent STARTED", icon="🔥")
        
        while self.is_running:
            try:
                # Full scan
                await self.scanner.scan_once()
                
                for edge in self.scanner.latest_edges:  # assume scanner stores latest_edges
                    # Optimize + risk check
                    opt = self.optimizer.optimize_hedge_ratio_scipy(
                        edge["winner"]["yes_price"], edge["granular"]["yes_price"]
                    )
                    safety = self.risk_manager.check_trade_safety(edge, st.session_state.get("bankroll", 25000))
                    
                    confidence = self._calculate_confidence(edge, opt)
                    
                    if safety["safe_to_trade"] and confidence >= self.screaming_buy_threshold:
                        self._trigger_screaming_buy_alert(edge, confidence)
                    
                    elif safety["safe_to_trade"] and edge.get("is_new", False):
                        self._send_new_opportunity_alert(edge)
                    
                    # Check for close-out (profit target or optimal exit)
                    if self._should_close_position(edge):
                        self._send_close_out_alert(edge)
            
            except Exception as e:
                st.error(f"Agent error: {e}")
            
            await asyncio.sleep(self.interval_minutes * 60)

    def _calculate_confidence(self, edge: Dict, opt: Dict) -> float:
        """Composite near-arb confidence (0–1)"""
        mc = edge.get("monte_carlo", {})
        score = (
            (mc.get("win_probability", 0) / 100) * 0.4 +
            (edge.get("ev_percent", 0) / 20) * 0.3 +           # EV normalized
            (1 if edge.get("optimal_ratio", 0) > 0.8 else 0) * 0.2 +
            (opt.get("success", False) * 0.1)
        )
        return min(1.0, max(0.0, score))

    def _trigger_screaming_buy_alert(self, edge: Dict, confidence: float):
        """Cramer-style red flash + sound"""
        st.error(f"🔥 SCREAMING BUY — {edge['event']} @ {confidence:.0%} CONFIDENCE 🔥")
        st.balloons()  # fun visual
        # Browser sound (custom JS)
        st.components.v1.html(
            f"""
            <script>
                const audio = new Audio('https://www.soundjay.com/buttons/beep-07.mp3');
                audio.play();
                document.body.style.backgroundColor = '#ff0000';
                setTimeout(() => {{ document.body.style.backgroundColor = ''; }}, 800);
            </script>
            """,
            height=0
        )
        # Optional: Push/Twilio in production
        st.toast("📱 PUSH/TEXT ALERT SENT: Near-Arb Opportunity!", icon="🚨")

    def _send_new_opportunity_alert(self, edge: Dict):
        st.success(f"🔔 New Opportunity: {edge['event']} — EV {edge.get('ev_percent')}%")
        # In production: integrate Pushover, Twilio SMS, or Firebase

    def _should_close_position(self, edge: Dict) -> bool:
        # Example logic: profit target hit or conditional probability shifted favorably
        return edge.get("current_pnl", 0) > edge.get("total_cost", 0) * 0.8  # 80% profit lock

    def stop(self):
        self.is_running = False
