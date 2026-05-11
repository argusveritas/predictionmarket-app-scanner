# core/journal.py
import pandas as pd
import json
from datetime import datetime
from typing import Dict, List, Optional

class TradeJournal:
    def __init__(self, journal_file: str = "data/journal/trades.csv"):
        self.journal_file = journal_file
        self.trades = self._load_journal()

    def _load_journal(self) -> pd.DataFrame:
        try:
            return pd.read_csv(self.journal_file)
        except FileNotFoundError:
            return pd.DataFrame(columns=[
                "timestamp", "event", "winner_size", "hedge_size", "total_cost",
                "strategy", "outcome", "pnl", "return_pct", "notes"
            ])

    def log_trade(self, edge: Dict, size: float, outcome: str = "pending",
                  pnl: float = None, notes: str = "") -> None:
        new_trade = {
            "timestamp": datetime.now().isoformat(),
            "event": edge.get("event_name", "Unknown"),
            "winner_size": size,
            "hedge_size": round(size * edge.get("optimal_ratio", 1.9), 0),
            "total_cost": round(size * (1 + edge.get("optimal_ratio", 1.9)), 0),
            "strategy": edge.get("sizing_strategy", "kelly_fractional"),
            "outcome": outcome,
            "pnl": pnl,
            "return_pct": round((pnl / edge.get("total_cost", 1)) * 100, 2) if pnl else None,
            "notes": notes
        }
        self.trades = pd.concat([self.trades, pd.DataFrame([new_trade])], ignore_index=True)
        self.trades.to_csv(self.journal_file, index=False)

    def get_performance_summary(self) -> Dict:
        if self.trades.empty:
            return {"total_trades": 0, "total_pnl": 0}
        
        closed = self.trades[self.trades["pnl"].notna()]
        return {
            "total_trades": len(self.trades),
            "closed_trades": len(closed),
            "total_pnl": round(closed["pnl"].sum(), 2),
            "win_rate": round((closed["pnl"] > 0).mean() * 100, 1) if not closed.empty else 0,
            "total_return_pct": round((closed["pnl"].sum() / closed["total_cost"].sum()) * 100, 2),
            "avg_pnl": round(closed["pnl"].mean(), 2),
            "best_trade": round(closed["pnl"].max(), 2),
            "worst_trade": round(closed["pnl"].min(), 2),
            "equity_curve": self.trades["pnl"].cumsum().tolist()
        }

    def mark_trade_resolved(self, index: int, outcome: str, actual_pnl: float):
        self.trades.loc[index, "outcome"] = outcome
        self.trades.loc[index, "pnl"] = actual_pnl
        self.trades.to_csv(self.journal_file, index=False)
