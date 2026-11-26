"""
Quick Commerce Delivery - V3 Distributed
Regional orchestration skeleton.
"""

from __future__ import annotations

from typing import Dict, Protocol


class RegionRouter(Protocol):
    def read_region(self, lat: float, lng: float) -> str:
        ...

    def write_region(self, lat: float, lng: float) -> str:
        ...


class RegionalOrderOrchestrator:
    def create_regional_order(self, user_id: str, lat: float, lng: float, request_id: str) -> str:
        raise NotImplementedError("V3 skeleton")

    def reconcile_failed_order(self, order_id: str, reason: str) -> Dict[str, str]:
        raise NotImplementedError("V3 skeleton")
