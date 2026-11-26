import time
import queue
import threading

class CircuitBreaker:
    def __init__(self, failure_threshold=3, reset_timeout=2.0):
        self.failure_threshold = failure_threshold
        self.reset_timeout = reset_timeout
        
        self.state = "CLOSED"
        self.failures = 0
        self.last_failure_time = None
        self.lock = threading.Lock()

    def can_request(self):
        with self.lock:
            if self.state == "CLOSED":
                return True
            if self.state == "OPEN":
                if time.time() - self.last_failure_time > self.reset_timeout:
                    self.state = "HALF_OPEN"
                    return True
                return False
            if self.state == "HALF_OPEN":
                return True
        return False

    def record_success(self):
        with self.lock:
            self.state = "CLOSED"
            self.failures = 0

    def record_failure(self):
        with self.lock:
            self.failures += 1
            if self.state == "HALF_OPEN" or self.failures >= self.failure_threshold:
                self.state = "OPEN"
                self.last_failure_time = time.time()

class BackendService:
    def __init__(self, name):
        self.name = name

    def call(self, timeout=None):
        pass

class GatewayV3:
    def __init__(self, retry_budget=0.1): # allow retries for 10% of requests
        self.retry_budget = retry_budget
        self.total_requests = 0
        self.total_retries = 0
        self.lock = threading.Lock()
        self.circuit_breakers = {}

    def get_circuit_breaker(self, service_name):
        with self.lock:
            if service_name not in self.circuit_breakers:
                self.circuit_breakers[service_name] = CircuitBreaker()
            return self.circuit_breakers[service_name]

    def _can_retry(self):
        with self.lock:
            if self.total_requests == 0:
                return True
            return (self.total_retries / self.total_requests) < self.retry_budget

    def _record_request(self):
        with self.lock:
            self.total_requests += 1

    def _record_retry(self):
        with self.lock:
            self.total_retries += 1

    def handle(self, backend: BackendService, timeout_sec: float):
        self._record_request()
        cb = self.get_circuit_breaker(backend.name)

        if not cb.can_request():
            return "503 Service Unavailable (Circuit Breaker OPEN)"

        try:
            res = backend.call(timeout=timeout_sec)
            cb.record_success()
            return res
        except TimeoutError:
            cb.record_failure()
            if self._can_retry():
                self._record_retry()
                try:
                    res = backend.call(timeout=timeout_sec)
                    cb.record_success()
                    return res
                except Exception:
                    cb.record_failure()
                    return "504 Gateway Timeout"
            else:
                return "504 Gateway Timeout"
        except Exception:
            cb.record_failure()
            return "500 Internal Server Error"

    def aggregate(self, backends, timeout_sec: float):
        self._record_request()
        results = {}
        
        # In a real system, this would be concurrent. Using simple loop for simulation parity.
        for backend in backends:
            cb = self.get_circuit_breaker(backend.name)
            if not cb.can_request():
                results[backend.name] = "503 Service Unavailable"
                continue

            try:
                res = backend.call(timeout=timeout_sec)
                cb.record_success()
                results[backend.name] = res
            except TimeoutError:
                cb.record_failure()
                results[backend.name] = "504 Gateway Timeout"
            except Exception:
                cb.record_failure()
                results[backend.name] = "500 Internal Server Error"
                
        return results
