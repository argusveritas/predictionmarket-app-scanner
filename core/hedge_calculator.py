class HedgeCalculator:
    @staticmethod
    def insurance_hedge_ratio(winner_yes: float, granular_yes: float) -> float:
        if not (0 < granular_yes < 1):
            return 0.0
        return winner_yes / ((1 / granular_yes) - 1)
