class CircuitBreakerConfig:
    def __init__(self, failure_rate_threshold: int, sliding_window_size: int, wait_duration_in_open_state: int, permitted_number_of_calls_in_half_open: int, slow_call_rate_threshold: int = 50, slow_call_duration_threshold_ms: int = 1000):
        self.failure_rate_threshold = failure_rate_threshold
        self.sliding_window_size = sliding_window_size
        self.wait_duration_in_open_state = wait_duration_in_open_state
        self.permitted_number_of_calls_in_half_open = permitted_number_of_calls_in_half_open
        self.slow_call_rate_threshold = slow_call_rate_threshold
        self.slow_call_duration_threshold_ms = slow_call_duration_threshold_ms
