    async def execute_hedge(self, edge: Dict, size_usd: float = 100.0) -> Dict:
        result = { ... }  # previous logic
        
        # Auto-log to journal
        journal = TradeJournal()
        journal.log_trade(edge, size_usd, outcome="pending", pnl=None,
                         notes=f"Executed via optimizer | Hedge ratio {result['hedge_ratio']}")
        
        return result
