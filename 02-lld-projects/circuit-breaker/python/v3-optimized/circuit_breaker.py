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

class StateInfo:
    __slots__ = ['state', 'generation', 'transition_time', 'half_open_calls']
    def __init__(self, state: CircuitBreakerState, generation: int, transition_time: float):
        self.state = state
        self.generation = generation
        self.transition_time = transition_time
        self.half_open_calls = 0

class CircuitBreaker:
    def __init__(self, config: CircuitBreakerConfig, clock: Optional[Callable[[], float]] = None):
        self.config = config
        self.clock = clock if clock else lambda: time.monotonic() * 1000.0
        
        now_ms = self.clock()
        self.state_info = StateInfo(CircuitBreakerState.CLOSED, 0, now_ms)
        
        self.bucket_size_in_ms = 1000
        self.buckets = [Bucket(now_ms - (config.sliding_window_size - i) * self.bucket_size_in_ms) for i in range(config.sliding_window_size)]
        
        self.lock = Lock()
        self.window_lock = Lock()
        
    @property
    def state(self):
        with self.lock:
            return self.state_info.state

    def execute(self, callable_func: Callable, fallback: Optional[Callable] = None) -> Any:
        try:
            call_generation = self._check_state()
        except CircuitBreakerOpenException as e:
            if fallback:
                return fallback(e)
            raise e

        start_time = self.clock()
        try:
            result = callable_func()
            duration_ms = self.clock() - start_time
            self._on_success(duration_ms, call_generation)
            return result
        except Exception as e:
            duration_ms = self.clock() - start_time
            if not isinstance(e, CircuitBreakerOpenException):
                self._on_error(duration_ms, call_generation)
            if fallback:
                return fallback(e)
            raise e

    def _check_state(self) -> int:
        while True:
            with self.lock:
                current = self.state_info
                
                if current.state == CircuitBreakerState.OPEN:
                    now = self.clock()
                    if (now - current.transition_time) >= self.config.wait_duration_in_open_state:
                        self.state_info = StateInfo(CircuitBreakerState.HALF_OPEN, current.generation + 1, now)
                        continue
                    else:
                        raise CircuitBreakerOpenException("Circuit Breaker is OPEN")
                
                if current.state == CircuitBreakerState.HALF_OPEN:
                    current.half_open_calls += 1
                    if current.half_open_calls > self.config.permitted_number_of_calls_in_half_open:
                        raise CircuitBreakerOpenException("Circuit Breaker is HALF_OPEN (No permits left)")
                        
                return current.generation

    def _on_success(self, duration_ms: float, call_generation: int):
        with self.lock:
            current = self.state_info
            if current.generation != call_generation:
                return
                
            if current.state == CircuitBreakerState.HALF_OPEN:
                now = self.clock()
                self.state_info = StateInfo(CircuitBreakerState.CLOSED, current.generation + 1, now)
                self._reset_window(now)
            elif current.state == CircuitBreakerState.CLOSED:
                self._record_result(True, duration_ms)
                self._evaluate_state(current)

    def _on_error(self, duration_ms: float, call_generation: int):
        with self.lock:
            current = self.state_info
            if current.generation != call_generation:
                return
                
            if current.state == CircuitBreakerState.HALF_OPEN:
                now = self.clock()
                self.state_info = StateInfo(CircuitBreakerState.OPEN, current.generation + 1, now)
            elif current.state == CircuitBreakerState.CLOSED:
                self._record_result(False, duration_ms)
                self._evaluate_state(current)
                
    def _evaluate_state(self, current: StateInfo):
        if current.state != CircuitBreakerState.CLOSED:
            return
            
        failure_rate, slow_call_rate = self._calculate_rates()
        if failure_rate >= self.config.failure_rate_threshold or slow_call_rate >= self.config.slow_call_rate_threshold:
            now = self.clock()
            self.state_info = StateInfo(CircuitBreakerState.OPEN, current.generation + 1, now)

    def _record_result(self, success: bool, duration_ms: float):
        now = self.clock()
        current_bucket = self._get_current_bucket(now)
        with self.window_lock:
            if success:
                current_bucket.success_count += 1
            else:
                current_bucket.failure_count += 1
            if duration_ms > self.config.slow_call_duration_threshold_ms:
                current_bucket.slow_call_count += 1

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

    def _calculate_rates(self):
        with self.window_lock:
            total_calls = 0
            total_failures = 0
            total_slow_calls = 0
            
            now = self.clock()
            window_start = now - (len(self.buckets) * self.bucket_size_in_ms)
            
            for b in self.buckets:
                if b.start_time >= window_start:
                    total_calls += b.success_count + b.failure_count
                    total_failures += b.failure_count
                    total_slow_calls += b.slow_call_count
            
            if total_calls == 0:
                return 0, 0
            return (total_failures * 100) // total_calls, (total_slow_calls * 100) // total_calls

    def _reset_window(self, now_ms: float):
        with self.window_lock:
            self.buckets = [Bucket(now_ms - (len(self.buckets) - i) * self.bucket_size_in_ms) for i in range(len(self.buckets))]
