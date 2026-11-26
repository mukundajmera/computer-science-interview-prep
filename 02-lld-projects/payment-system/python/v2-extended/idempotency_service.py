"""IdempotencyService for payment-system (v2-extended)."""
import threading
from typing import Dict, Optional, Any

class IdempotencyService:
    def __init__(self) -> None:
        self.id = "IdempotencyService"
        self._store: Dict[str, Dict[str, Any]] = {}
        self._lock = threading.RLock()

    def check_or_acquire(self, key: str, payload_hash: str) -> Optional[Dict[str, Any]]:
        """
        Check if key exists.
        If it exists and payload matches, return the cached response (or indicator).
        If it exists and payload mismatches, raise ValueError to reject.
        If it does not exist, initialize and return None (lock acquired/ready).
        """
        with self._lock:
            if key in self._store:
                entry = self._store[key]
                if entry['payload_hash'] != payload_hash:
                    raise ValueError("Repeated idempotency key with changed payload")
                return entry['response']
            else:
                self._store[key] = {
                    'payload_hash': payload_hash,
                    'response': None
                }
                return None

    def save_response(self, key: str, response: Any) -> None:
        with self._lock:
            if key in self._store:
                self._store[key]['response'] = response

    def describe(self) -> str:
        return f"IdempotencyService:{self.id}"
