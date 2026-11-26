"""Simple idempotency key store for retry-safe API handling."""

from typing import Dict, Optional
from threading import Lock


class IdempotencyStore:
    def __init__(self) -> None:
        self._responses: Dict[str, str] = {}
        self._lock = Lock()

    def record(self, key: str, response_id: str) -> None:
        self._validate(key, response_id)
        with self._lock:
            self._responses.setdefault(key, response_id)

    def get(self, key: str) -> Optional[str]:
        if not key or key.isspace():
            raise ValueError("key must not be blank")
        with self._lock:
            return self._responses.get(key)

    def process_create_request(self, key: str, generated_id: str) -> str:
        self._validate(key, generated_id)
        with self._lock:
            return self._responses.setdefault(key, generated_id)

    @staticmethod
    def _validate(key: str, response_id: str) -> None:
        if not key or key.isspace():
            raise ValueError("key must not be blank")
        if response_id is None:
            raise ValueError("response_id must not be None")


def process_create_request(store: IdempotencyStore, idempotency_key: str, generated_id: str) -> str:
    return store.process_create_request(idempotency_key, generated_id)


if __name__ == "__main__":
    store = IdempotencyStore()
    print(process_create_request(store, "k1", "order-1"))
    print(process_create_request(store, "k1", "order-2"))
