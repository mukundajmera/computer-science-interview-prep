from enum import Enum, auto
from typing import Optional, Dict, Tuple
import threading
import time
from payment_response import PaymentResponse

class IdempotencyState(Enum):
    IN_PROGRESS = auto()
    COMPLETED = auto()
    FAILED = auto()

class IdempotencyRecord:
    def __init__(self, state: IdempotencyState, response: Optional[PaymentResponse]):
        self.state = state
        self.response = response
        self.timestamp = time.time()
        self.lock = threading.Lock()

class IdempotencyStore:
    def __init__(self, ttl_seconds: int = 3600):
        self.store: Dict[str, IdempotencyRecord] = {}
        self.store_lock = threading.Lock()
        self.ttl_seconds = ttl_seconds

    def _cleanup_expired(self, current_time: float):
        keys_to_delete = []
        for key, record in self.store.items():
            if current_time - record.timestamp > self.ttl_seconds:
                keys_to_delete.append(key)
        for key in keys_to_delete:
            del self.store[key]

    def lock_or_check(self, key: str) -> bool:
        current_time = time.time()
        with self.store_lock:
            self._cleanup_expired(current_time)
            if key not in self.store:
                self.store[key] = IdempotencyRecord(IdempotencyState.IN_PROGRESS, None)
                return True
            
            record = self.store[key]
            
        with record.lock:
            if record.state == IdempotencyState.IN_PROGRESS:
                return False
            # if not in progress we assume it's completed/failed
            return False

    def get_state(self, key: str) -> Optional[IdempotencyState]:
        with self.store_lock:
            record = self.store.get(key)
            if not record:
                return None
            if time.time() - record.timestamp > self.ttl_seconds:
                return None
        with record.lock:
            return record.state

    def get_response(self, key: str) -> Optional[PaymentResponse]:
        with self.store_lock:
            record = self.store.get(key)
            if not record:
                return None
            if time.time() - record.timestamp > self.ttl_seconds:
                return None
        with record.lock:
            return record.response

    def update(self, key: str, state: IdempotencyState, response: Optional[PaymentResponse]):
        with self.store_lock:
            record = self.store.get(key)
        
        if record:
            with record.lock:
                record.state = state
                record.response = response
                record.timestamp = time.time()
        else:
            with self.store_lock:
                self.store[key] = IdempotencyRecord(state, response)
