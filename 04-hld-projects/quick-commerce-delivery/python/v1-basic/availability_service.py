"""
Quick Commerce Delivery - V1 Basic
Availability and order placement skeleton.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional, Protocol


@dataclass
class AvailabilityItem:
    item_id: str
    center_id: str
    available_qty: int
    eta_minutes: int


@dataclass
class OrderLine:
    item_id: str
    qty: int


class NearbyCenterResolver(Protocol):
    def resolve(self, lat: float, lng: float, limit: int) -> List[str]:
        ...


class InventoryRepository(Protocol):
    def query(self, center_id: str, query: str, page: int, page_size: int) -> List[AvailabilityItem]:
        ...

    def reserve(self, center_id: str, lines: List[OrderLine]) -> bool:
        ...


class OrderRepository(Protocol):
    def create(self, user_id: str, center_id: str, lines: List[OrderLine], idempotency_key: str, created_at: datetime) -> str:
        ...

    def find_by_idempotency_key(self, idempotency_key: str) -> Optional[str]:
        ...


class AvailabilityService:
    def lookup(self, lat: float, lng: float, query: str, page: int, page_size: int) -> List[AvailabilityItem]:
        raise NotImplementedError("V1 skeleton")

    def place_order(self, user_id: str, lat: float, lng: float, lines: List[OrderLine], idempotency_key: str) -> str:
        raise NotImplementedError("V1 skeleton")
