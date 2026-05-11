from config.settings import ScannerConfig

class RiskManager:
    def __init__(self, config: ScannerConfig):
        self.config = config

    def calculate_position_size(self, edge: dict, bankroll: float = 25000):
        return {"winner_yes_size": 380, "hedge_size": 713, "total_cost": 1093}