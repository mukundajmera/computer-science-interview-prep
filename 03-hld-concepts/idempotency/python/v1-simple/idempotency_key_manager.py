import hashlib
import time
import threading
from enum import Enum
from typing import Dict, Any, Optional

class Status(Enum):
    IN_PROGRESS = 1
    COMPLETED = 2
    FAILED = 3

class ConflictException(Exception):
    pass

class InProgressException(Exception):
    pass

class Record:
    def __init__(self, key: str, payload_hash: str, expires_at: float):
        self.key = key
        self.payload_hash = payload_hash
        self.status = Status.IN_PROGRESS
        self.response: Optional[Any] = None
        self.expires_at = expires_at

class IdempotencyKeyManager:
    def __init__(self, ttl_seconds: float):
        self.ttl_seconds = ttl_seconds
        self.store: Dict[str, Record] = {}
        self.lock = threading.Lock()

    def _hash_payload(self, payload: str) -> str:
        if payload is None:
            return ""
        return hashlib.sha256(payload.encode('utf-8')).hexdigest()

    def begin_request(self, key: str, payload: str) -> Record:
        payload_hash = self._hash_payload(payload)
        now = time.time()

        with self.lock:
            if key in self.store:
                existing = self.store[key]
                if existing.expires_at < now:
                    record = Record(key, payload_hash, now + self.ttl_seconds)
                    self.store[key] = record
                    return record
                if existing.payload_hash != payload_hash:
                    raise ConflictException("Payload mismatch for idempotency key")
                if existing.status == Status.IN_PROGRESS:
                    raise InProgressException("Request is already in progress")
                return existing

            record = Record(key, payload_hash, now + self.ttl_seconds)
            self.store[key] = record
            return record

    def complete_request(self, key: str, response: Any) -> None:
        with self.lock:
            if key in self.store:
                record = self.store[key]
                record.status = Status.COMPLETED
                record.response = response

    def fail_request(self, key: str) -> None:
        with self.lock:
            if key in self.store:
                record = self.store[key]
                record.status = Status.FAILED

    def cleanup(self) -> None:
        now = time.time()
        with self.lock:
            expired_keys = [k for k, v in self.store.items() if v.expires_at < now]
            for k in expired_keys:
                del self.store[k]
