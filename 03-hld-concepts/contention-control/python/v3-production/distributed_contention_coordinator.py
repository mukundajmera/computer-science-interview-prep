"""v3-production: execute once with idempotency."""

from typing import Callable, Dict, Generic, Optional, TypeVar


T = TypeVar("T")


class IdempotencyStore(Generic[T]):
    def __init__(self) -> None:
        self._store: Dict[str, T] = {}

    def get(self, key: str) -> Optional[T]:
        return self._store.get(key)

    def put_if_absent(self, key: str, value: T) -> bool:
        if key in self._store:
            return False
        self._store[key] = value
        return True


class DistributedContentionCoordinator:
    def execute_once(self, idempotency_key: str, action: Callable[[], T], store: IdempotencyStore[T]) -> T:
        existing = store.get(idempotency_key)
        if existing is not None:
            return existing
        result = action()
        store.put_if_absent(idempotency_key, result)
        return store.get(idempotency_key)  # type: ignore[return-value]
