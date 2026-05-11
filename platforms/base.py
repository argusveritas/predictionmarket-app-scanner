from abc import ABC, abstractmethod
from typing import List, Dict

class PlatformFetcher(ABC):
    @abstractmethod
    async def fetch_markets(self, category_filter: str = None) -> List[Dict]:
        pass

    def normalize_contract(self, raw: Dict) -> Dict:
        return {
            "platform": self.get_platform_name(),
            "id": raw.get("id"),
            "slug": raw.get("slug"),
            "yes_price": float(raw.get("yes_price", 0.01)),
            "no_price": float(raw.get("no_price", 0.99)),
            "volume": int(raw.get("volume", 0)),
            "event_name": raw.get("title") or raw.get("event", ""),
        }

    @abstractmethod
    def get_platform_name(self) -> str:
        pass