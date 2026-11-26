"""
Quick Commerce Delivery - V2 Scaled
Cache-oriented availability skeleton with invalidation hooks.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional, Protocol


class AvailabilityCache(Protocol):
    def get(self, key: str) -> Optional[List[str]]:
        ...

    def put(self, key: str, item_ids: List[str], ttl_seconds: int) -> None:
        ...

    def invalidate_center(self, center_id: str) -> None:
        ...


class AvailabilitySource(Protocol):
    def query_center(self, center_id: str, keyword: str, page: int, page_size: int) -> List[str]:
        ...

    def resolve_nearby_centers(self, lat: float, lng: float, limit: int) -> List[str]:
        ...


@dataclass
class InventoryDelta:
    center_id: str
    item_id: str
    available_qty: int
    observed_at: datetime


class CachedAvailabilityService:
    def search(self, lat: float, lng: float, keyword: str, page: int, page_size: int) -> List[str]:
        raise NotImplementedError("V2 skeleton")

    def on_inventory_delta(self, delta: InventoryDelta) -> None:
        raise NotImplementedError("V2 skeleton")
