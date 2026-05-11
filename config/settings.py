from dataclasses import dataclass
from typing import List

@dataclass
class ScannerConfig:
    platforms: List[str] = None
    fee_rate: float = 0.015
    ev_threshold_percent: float = 5.0
    scan_interval_sec: int = 300
    hedge_breakeven_target: float = 0.65
    min_volume_usd: int = 50000
    auto_execute: bool = False
    dry_run: bool = True