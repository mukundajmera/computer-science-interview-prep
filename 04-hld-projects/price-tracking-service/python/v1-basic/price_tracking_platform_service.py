
from typing import Optional, Protocol


class PriceTrackingPlatformService(Protocol):
    """Price Tracking Service - v1 service boundary."""

    def create(self, owner_id: str, payload: str) -> str: ...
    def get_by_id(self, object_id: str) -> Optional[str]: ...
    def mutate(self, object_id: str, mutation_payload: str, idempotency_key: str) -> None: ...
