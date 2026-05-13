# 🔮 CrystalBall - Prediction Market Arbitrage Scanner

Professional tool for finding and executing hedged opportunities across Polymarket, Kalshi, DraftKings Predictions, FanDuel Predicts, and more.

## App Architecture & Decision Flow

```mermaid
flowchart LR
    A[User Opens CrystalBall] --> B[Load Sidebar\nBankroll + Risk + Scan Targets]
    B --> C{Execute Fresh Scan Now?}
    C -->|Yes| D[Clear Cache + Fetch Live Markets\nPolymarket + Kalshi + DraftKings/FanDuel]
    C -->|No| E[Background Agent Running?]
    E -->|Yes| D
    E -->|No| F[Show Cached Edges]
    D --> G[Build Live Edges Table\nContract + Source + Price + Liquidity + Counter + Est. P&L]
    G --> H{User clicks row?}
    H -->|Yes| I[Show Detailed Arbitrage Panel\nHedge Ratio + P&L + Risk Summary]
    H -->|No| J[Navigate Tabs]
    J --> K[Interactive Payoff Table]
    J --> L[Monte Carlo Simulation]
    J --> M[Trade Journal]
    J --> N[Home Tab + FAQ]
    I --> O{Agent Enabled?}
    O -->|Yes| P[Run Background Scanning Loop]
    O -->|No| Q[End Session]
    P --> D# predictionmarket-app-scanner
# Prediction Market Arb Scanner

Professional tool for finding Devens-style hedged opportunities across Polymarket, Kalshi, Coinbase, etc.

## Features
- Real-time edge detection
- Monte Carlo + Optimizer
- One-Click Execute (dry-run / live)
- Opportunity Optimizer Agent with screaming alerts
- Full risk management & journal

## Run Locally
```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
