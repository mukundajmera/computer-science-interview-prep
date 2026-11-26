import time
from typing import Callable, Any, Optional
from threading import Lock

try:
    from .circuit_breaker_state import CircuitBreakerState
    from .exceptions import CircuitBreakerOpenException
    from .config import CircuitBreakerConfig
except ImportError:
    from circuit_breaker_state import CircuitBreakerState
    from exceptions import CircuitBreakerOpenException
    from config import CircuitBreakerConfig

class CircuitBreaker:
    def __init__(self, config: CircuitBreakerConfig, clock: Optional[Callable[[], float]] = None):
        self.config = config
        self.state = CircuitBreakerState.CLOSED
        self.last_state_transition_time = 0.0
        self.generation = 0
        self.clock = clock if clock else time.time
        
        self.window = [False] * config.sliding_window_size
        self.window_index = 0
        self.current_calls = 0
        
        self.half_open_calls = 0
        self.lock = Lock()

    def execute(self, callable_func: Callable, fallback: Optional[Callable] = None) -> Any:
        try:
            call_generation = self._check_state()
        except CircuitBreakerOpenException as e:
            if fallback:
                return fallback(e)
            raise e

        try:
            result = callable_func()
            self._on_success(call_generation)
            return result
        except Exception as e:
            if not isinstance(e, CircuitBreakerOpenException):
                self._on_error(call_generation)
            if fallback:
                return fallback(e)
            raise e

    def _check_state(self):
        with self.lock:
            if self.state == CircuitBreakerState.OPEN:
                now = self.clock()
                if (now - self.last_state_transition_time) * 1000 >= self.config.wait_duration_in_open_state:
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

    def _on_success(self, call_generation: int):
        with self.lock:
            if self.generation != call_generation:
                return
            if self.state == CircuitBreakerState.HALF_OPEN:
                self._transition_to_closed()
            elif self.state == CircuitBreakerState.CLOSED:
                self._record_result(True)

    def _on_error(self, call_generation: int):
        with self.lock:
            if self.generation != call_generation:
                return
            if self.state == CircuitBreakerState.HALF_OPEN:
                self._transition_to_open()
            elif self.state == CircuitBreakerState.CLOSED:
                self._record_result(False)
                if self.current_calls >= self.config.sliding_window_size and self._calculate_failure_rate() >= self.config.failure_rate_threshold:
                    self._transition_to_open()

    def _record_result(self, success: bool):
        idx = self.window_index % len(self.window)
        self.window[idx] = success
        self.window_index += 1
        if self.current_calls < len(self.window):
            self.current_calls += 1

    def _calculate_failure_rate(self) -> int:
        failures = sum(1 for i in range(self.current_calls) if not self.window[i])
        if self.current_calls == 0:
            return 0
        return (failures * 100) // self.current_calls

    def _transition_to_closed(self):
        self.state = CircuitBreakerState.CLOSED
        self.current_calls = 0
        self.window_index = 0
        self.last_state_transition_time = self.clock()
        self.generation += 1

    def _transition_to_open(self):
        self.state = CircuitBreakerState.OPEN
        self.last_state_transition_time = self.clock()
        self.generation += 1
