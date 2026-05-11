from platforms.base import PlatformFetcher
from typing import List, Dict

class PolymarketFetcher(PlatformFetcher):
    async def fetch_markets(self, category_filter: str = None) -> List[Dict]:
        # Mock data - replace with real gamma-api later
        return [
            {"id": "surv-devens", "slug": "survivor-50-devens-winner", "yes_price": 0.014, "volume": 60700, "title": "Survivor S50 - Rick Devens Winner"},
        ]
