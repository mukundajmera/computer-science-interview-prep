from typing import Any
from v1_basic.multi_region.hybrid_logical_clock import HybridLogicalClock

class Record:
    def __init__(self, id: str, data: Any, hlc: HybridLogicalClock, origin_region: str, tombstone: bool = False):
        self.id = id
        self.data = data
        self.hlc = hlc
        self.origin_region = origin_region
        self.tombstone = tombstone
