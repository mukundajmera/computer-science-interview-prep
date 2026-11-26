
from typing import List, Protocol


class DistributedIdempotencyStore(Protocol):
    def claim(self, key: str, ttl_ms: int) -> bool: ...


class DistributedSocialPostSearchService(Protocol):
    """Social Post Search System - v3 distributed contract."""

    def create(self, owner_id: str, payload: str, region: str) -> str: ...
    def mutate_with_replay_token(self, object_id: str, mutation_payload: str, idempotency_key: str, replay_token: str) -> None: ...
    def read_region_view(self, region: str, limit: int) -> List[str]: ...
