import time
import random
import threading
from typing import Callable, Any, TypeVar

T = TypeVar('T')

class CircuitBreaker:
    class State:
        CLOSED = "CLOSED"
        OPEN = "OPEN"
        HALF_OPEN = "HALF_OPEN"

    def __init__(self, threshold: int, timeout_ms: int):
        self.state = self.State.CLOSED
        self.threshold = threshold
        self.timeout_ms = timeout_ms
        self.failure_count = 0
        self.open_time = 0.0
        self.probe_count = 0
        self.probe_limit = 3
        self.lock = threading.Lock()

    def execute(self, action: Callable[[], T]) -> T:
        with self.lock:
            if self.state == self.State.OPEN:
                if (time.time() * 1000) - self.open_time > self.timeout_ms:
                    self.state = self.State.HALF_OPEN
                    self.probe_count = 0
                else:
                    raise RuntimeError("Circuit Breaker is OPEN")

            if self.state == self.State.HALF_OPEN:
                if self.probe_count >= self.probe_limit:
                    raise RuntimeError("Probe limit reached, waiting for next cycle")
                self.probe_count += 1

        try:
            result = action()
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise e

    def _on_success(self) -> None:
        with self.lock:
            if self.state == self.State.HALF_OPEN:
                if self.probe_count == self.probe_limit:
                    self.state = self.State.CLOSED
                    self.failure_count = 0
            elif self.state == self.State.CLOSED:
                self.failure_count = 0

    def _on_failure(self) -> None:
        with self.lock:
            if self.state == self.State.HALF_OPEN:
                self.state = self.State.OPEN
                self.open_time = time.time() * 1000
            elif self.state == self.State.CLOSED:
                self.failure_count += 1
                if self.failure_count >= self.threshold:
                    self.state = self.State.OPEN
                    self.open_time = time.time() * 1000

class Bulkhead:
    def __init__(self, capacity: int):
        self.semaphore = threading.Semaphore(capacity)

    def execute(self, action: Callable[[], T]) -> T:
        if self.semaphore.acquire(blocking=False):
            try:
                return action()
            finally:
                self.semaphore.release()
        else:
            raise RuntimeError("Bulkhead capacity reached")

class RetryPolicy:
    def __init__(self, max_retries: int, base_delay_ms: int):
        self.max_retries = max_retries
        self.base_delay_ms = base_delay_ms

    def execute_with_retry(self, action: Callable[[], T]) -> T:
        attempt = 0
        while True:
            try:
                return action()
            except Exception as e:
                if attempt >= self.max_retries:
                    raise e
                delay = self._calculate_full_jitter_delay(attempt)
                time.sleep(delay / 1000.0)
                attempt += 1

    def _calculate_full_jitter_delay(self, attempt: int) -> float:
        max_delay = self.base_delay_ms * (1 << attempt)
        return random.uniform(0, max_delay)

class ResilienceOrchestrator:
    def __init__(self, cb_threshold: int, cb_timeout_ms: int, bulkhead_capacity: int, max_retries: int, base_delay_ms: int):
        self.circuit_breaker = CircuitBreaker(cb_threshold, cb_timeout_ms)
        self.bulkhead = Bulkhead(bulkhead_capacity)
        self.retry_policy = RetryPolicy(max_retries, base_delay_ms)

    def execute(self, action: Callable[[], T], fallback: Callable[[], T]) -> T:
        try:
            return self.retry_policy.execute_with_retry(
                lambda: self.bulkhead.execute(
                    lambda: self.circuit_breaker.execute(action)
                )
            )
        except Exception:
            return fallback()
