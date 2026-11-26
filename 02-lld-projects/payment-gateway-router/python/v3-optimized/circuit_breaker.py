from enum import Enum, auto
import time
import threading

class CircuitState(Enum):
    CLOSED = auto()
    OPEN = auto()
    HALF_OPEN = auto()

class CircuitBreaker:
    def __init__(self, failure_threshold: int = 3, reset_timeout_ms: int = 5000):
        self.state = CircuitState.CLOSED
        self.failure_threshold = failure_threshold
        self.reset_timeout_ms = reset_timeout_ms
        self.failure_count = 0
        self.last_failure_time = 0.0
        self.lock = threading.Lock()

    def allow_request(self) -> bool:
        with self.lock:
            if self.state == CircuitState.OPEN:
                if (time.time() * 1000 - self.last_failure_time) >= self.reset_timeout_ms:
                    self.state = CircuitState.HALF_OPEN
                    return True
                return False
            return True

    def record_success(self):
        with self.lock:
            if self.state == CircuitState.HALF_OPEN:
                self.state = CircuitState.CLOSED
            self.failure_count = 0

    def record_failure(self):
        with self.lock:
            self.failure_count += 1
            if self.failure_count >= self.failure_threshold or self.state == CircuitState.HALF_OPEN:
                self.state = CircuitState.OPEN
                self.last_failure_time = time.time() * 1000
                
    def get_state(self) -> CircuitState:
        with self.lock:
            return self.state
