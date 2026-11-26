"""v1-simple: optimistic reservation with version checks."""

from dataclasses import dataclass
from typing import Dict


@dataclass
class Resource:
    available: int
    version: int


class OptimisticReservationService:
    def __init__(self) -> None:
        self._resources: Dict[str, Resource] = {}

    def upsert(self, resource_key: str, available: int) -> None:
        self._resources[resource_key] = Resource(available=available, version=0)

    def reserve(self, resource_key: str, quantity: int, expected_version: int) -> bool:
        current = self._resources.get(resource_key)
        if current is None:
            return False
        if current.available < quantity or current.version != expected_version:
            return False
        current.available -= quantity
        current.version += 1
        return True
