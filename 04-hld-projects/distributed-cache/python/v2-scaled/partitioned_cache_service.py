from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class RingSnapshot:
    version: int
    serialized_assignments: str


class PartitionedCacheService(Protocol):
    def resolve_node_for_key(self, key: str) -> str: ...
    def replicate_write(self, key: str, value: str, ttl_seconds: int) -> None: ...
    def rebalance_range(self, token_range: str, target_node_id: str) -> None: ...


class MembershipService(Protocol):
    def current_ring(self) -> RingSnapshot: ...
