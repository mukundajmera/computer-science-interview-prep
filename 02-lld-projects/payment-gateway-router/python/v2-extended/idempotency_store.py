from enum import Enum, auto
from typing import Optional, Dict
import threading
from payment_response import PaymentResponse

class IdempotencyState(Enum):
    IN_PROGRESS = auto()
    COMPLETED = auto()
    FAILED = auto()

class IdempotencyRecord:
    def __init__(self, state: IdempotencyState, response: Optional[PaymentResponse]):
        self.state = state
        self.response = response

class IdempotencyStore:
    def __init__(self):
        self.store: Dict[str, IdempotencyRecord] = {}
        self.lock = threading.RLock()

    def lock_or_check(self, key: str) -> bool:
        with self.lock:
            if key not in self.store:
                self.store[key] = IdempotencyRecord(IdempotencyState.IN_PROGRESS, None)
                return True
            return False

    def get_state(self, key: str) -> Optional[IdempotencyState]:
        with self.lock:
            record = self.store.get(key)
            return record.state if record else None

    def get_response(self, key: str) -> Optional[PaymentResponse]:
        with self.lock:
            record = self.store.get(key)
            return record.response if record else None

    def update(self, key: str, state: IdempotencyState, response: Optional[PaymentResponse]):
        with self.lock:
            self.store[key] = IdempotencyRecord(state, response)
