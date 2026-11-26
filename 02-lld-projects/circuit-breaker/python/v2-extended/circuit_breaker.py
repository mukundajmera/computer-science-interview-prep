import time
from typing import Callable, Any, Optional
from threading import Lock

try:
    from .circuit_breaker_state import CircuitBreakerState
    from .exceptions import CircuitBreakerOpenException
    from .config import CircuitBreakerConfig
    from .bucket import Bucket
except ImportError:
    from circuit_breaker_state import CircuitBreakerState
    from exceptions import CircuitBreakerOpenException
    from config import CircuitBreakerConfig
    from bucket import Bucket

class CircuitBreaker:
    def __init__(self, config: CircuitBreakerConfig, clock: Optional[Callable[[], float]] = None):
        self.config = config
        self.clock = clock if clock else lambda: time.time() * 1000
        self.state = CircuitBreakerState.CLOSED
        self.last_state_transition_time = 0.0
        
        self.bucket_size_in_ms = 1000
        now_ms = self.clock()
        # window size in config is treated as seconds, so buckets = sliding_window_size
        self.buckets = [Bucket(now_ms - (config.sliding_window_size - i) * self.bucket_size_in_ms) for i in range(config.sliding_window_size)]
        
        self.half_open_calls = 0
        self.generation = 0
        self.lock = Lock()
        self.window_lock = Lock()

    def execute(self, callable_func: Callable, fallback: Optional[Callable] = None) -> Any:
        try:
            current_gen = self._check_state()
        except CircuitBreakerOpenException as e:
            if fallback:
                return fallback(e)
            raise e

        try:
            result = callable_func()
            self._on_success(current_gen)
            return result
        except Exception as e:
            if not isinstance(e, CircuitBreakerOpenException):
                self._on_error(current_gen)
            if fallback:
                return fallback(e)
            raise e

    def _check_state(self):
        with self.lock:
            if self.state == CircuitBreakerState.OPEN:
                now = self.clock()
                if (now - self.last_state_transition_time) >= self.config.wait_duration_in_open_state:
                    self.state = CircuitBreakerState.HALF_OPEN
                    self.half_open_calls = 0
                    self.generation += 1
                else:
                    raise CircuitBreakerOpenException("Circuit Breaker is OPEN")
            
            if self.state == CircuitBreakerState.HALF_OPEN:
                self.half_open_calls += 1
                if self.half_open_calls > self.config.permitted_number_of_calls_in_half_open:
                    raise CircuitBreakerOpenException("Circuit Breaker is HALF_OPEN (No permits left)")
            return self.generation

    def _on_success(self, gen: int):
        with self.lock:
            if gen != self.generation:
                return
            if self.state == CircuitBreakerState.HALF_OPEN:
                self.state = CircuitBreakerState.CLOSED
                self._reset_window()
                self.last_state_transition_time = self.clock()
                self.generation += 1
            elif self.state == CircuitBreakerState.CLOSED:
                self._record_result(True)

    def _on_error(self, gen: int):
        with self.lock:
            if gen != self.generation:
                return
            if self.state == CircuitBreakerState.HALF_OPEN:
                self.state = CircuitBreakerState.OPEN
                self.last_state_transition_time = self.clock()
                self.generation += 1
            elif self.state == CircuitBreakerState.CLOSED:
                self._record_result(False)
                if self._calculate_failure_rate() >= self.config.failure_rate_threshold:
                    self.state = CircuitBreakerState.OPEN
                    self.last_state_transition_time = self.clock()
                    self.generation += 1

    def _record_result(self, success: bool):
        now = self.clock()
        current_bucket = self._get_current_bucket(now)
        with self.window_lock:
            if success:
                current_bucket.success_count += 1
            else:
                current_bucket.failure_count += 1

    def _get_current_bucket(self, now: float) -> Bucket:
        with self.window_lock:
            latest_bucket = max(self.buckets, key=lambda b: b.start_time)
            current_bucket_start_time = now - (now % self.bucket_size_in_ms)
            
            if latest_bucket.start_time != current_bucket_start_time:
                time_diff = current_bucket_start_time - latest_bucket.start_time
                shift_count = min(int(time_diff // self.bucket_size_in_ms), len(self.buckets))
                
                for i in range(shift_count):
                    self.buckets.pop(0)
                    self.buckets.append(Bucket(current_bucket_start_time - (shift_count - 1 - i) * self.bucket_size_in_ms))
            
            return self.buckets[-1]

    def _calculate_failure_rate(self) -> int:
        with self.window_lock:
            total_calls = 0
            total_failures = 0
            
            now = self.clock()
            window_start = now - (len(self.buckets) * self.bucket_size_in_ms)
            
            for b in self.buckets:
                if b.start_time >= window_start:
                    total_calls += b.success_count + b.failure_count
                    total_failures += b.failure_count
            
            if total_calls == 0:
                return 0
            return (total_failures * 100) // total_calls

    def _reset_window(self):
        with self.window_lock:
            now_ms = self.clock()
            self.buckets = [Bucket(now_ms - (len(self.buckets) - i) * self.bucket_size_in_ms) for i in range(len(self.buckets))]
