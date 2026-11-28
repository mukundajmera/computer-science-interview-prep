"""v2-extended API gateway simulator.

Improvements over v1-basic (named per the repo rule v1-basic -> v2-extended):
1. Header scrubbing in the security filter: internal routing/identity headers
   are stripped before forwarding so clients cannot spoof gateway-trusted
   metadata downstream (see PITFALLS.md).
2. Bounded retries with exponential backoff and jitter around an injectable
   downstream callable, so transient failures are absorbed without the
   synchronized retry storms PITFALLS.md and FOLLOW-UPS.md warn about.
3. A half-open circuit breaker driven by a rolling failure-rate window with
   configurable policies (threshold, window size, reset timeout), replacing
   v1's breaker that opened on consecutive failures and never recovered.
"""

import random
import time
from collections import deque

# Headers the gateway owns. Any client-supplied copy is stripped before
# forwarding; matched case-insensitively.
SCRUBBED_HEADERS = frozenset(
    {"x-internal-auth", "x-internal-route", "x-gateway-internal"}
)


class DownstreamError(Exception):
    """A simulated downstream failure (timeout or 5xx), injectable in tests."""


class Request:
    def __init__(self, path, headers):
        self.path = path
        self.headers = headers


class Response:
    def __init__(self, status_code, body):
        self.status_code = status_code
        self.body = body


class CircuitBreaker:
    """Half-open breaker driven by a rolling failure-rate window.

    CLOSED: requests flow; outcomes are recorded in a bounded window and the
    breaker opens once the failure rate over the window reaches the threshold
    (with at least min_samples observations, so a single early failure cannot
    trip it). OPEN: requests fast-fail until reset_timeout seconds have
    passed, then one half-open probe is admitted. Probe success closes the
    breaker and clears the window; probe failure reopens it immediately.
    """

    def __init__(
        self,
        failure_rate_threshold=0.5,
        window_size=10,
        min_samples=4,
        reset_timeout=30.0,
        clock=None,
    ):
        if not 0.0 < failure_rate_threshold <= 1.0:
            raise ValueError("failure_rate_threshold must be in (0, 1]")
        if window_size < 1:
            raise ValueError("window_size must be >= 1")
        if min_samples < 1 or min_samples > window_size:
            raise ValueError("min_samples must be in [1, window_size]")
        if reset_timeout < 0:
            raise ValueError("reset_timeout must be >= 0")
        self._failure_rate_threshold = failure_rate_threshold
        self._window_size = window_size
        self._min_samples = min_samples
        self._reset_timeout = reset_timeout
        self._clock = clock if clock is not None else time.time
        self._outcomes = deque(maxlen=window_size)  # True = success
        self._state = "CLOSED"
        self._opened_at = None
        self._probe_in_flight = False

    @property
    def state(self):
        return self._state

    def allow_request(self):
        if self._state == "OPEN":
            if self._clock() - self._opened_at < self._reset_timeout:
                return False
            self._state = "HALF_OPEN"
            self._probe_in_flight = False
        if self._state == "HALF_OPEN":
            if self._probe_in_flight:
                return False
            self._probe_in_flight = True
            return True
        return True

    def record_success(self):
        if self._state == "HALF_OPEN":
            self._state = "CLOSED"
            self._outcomes.clear()
            self._probe_in_flight = False
            return
        self._outcomes.append(True)

    def record_failure(self):
        if self._state == "HALF_OPEN":
            self._state = "OPEN"
            self._opened_at = self._clock()
            self._probe_in_flight = False
            return
        self._outcomes.append(False)
        self._maybe_open()

    def _maybe_open(self):
        if len(self._outcomes) < self._min_samples:
            return
        failures = sum(1 for ok in self._outcomes if not ok)
        if failures / len(self._outcomes) >= self._failure_rate_threshold:
            self._state = "OPEN"
            self._opened_at = self._clock()

    # Test-simulation helpers kept from v1 for API parity.
    def trip_open(self):
        self._state = "OPEN"
        self._opened_at = self._clock()
        self._probe_in_flight = False

    def reset(self):
        self._state = "CLOSED"
        self._outcomes.clear()
        self._opened_at = None
        self._probe_in_flight = False


class ApiGatewaySimulator:
    def __init__(
        self,
        max_retries=2,
        backoff_base=0.1,
        sleeper=None,
        rng=None,
        circuit_breaker=None,
    ):
        if max_retries < 0:
            raise ValueError("max_retries must be >= 0")
        if backoff_base < 0:
            raise ValueError("backoff_base must be >= 0")
        self.circuit_breaker = (
            circuit_breaker if circuit_breaker is not None else CircuitBreaker()
        )
        self._max_retries = max_retries
        self._backoff_base = backoff_base
        self._sleeper = sleeper if sleeper is not None else time.sleep
        self._rng = rng if rng is not None else random.Random()

    @staticmethod
    def scrub_headers(headers):
        """Drop gateway-owned internal headers before forwarding (v2 item 1)."""
        return {
            name: value
            for name, value in headers.items()
            if name.lower() not in SCRUBBED_HEADERS
        }

    def _default_downstream(self, path, headers):
        return Response(200, "OK from downstream")

    def handle_request(self, request, downstream=None):
        # 1. Security/Auth filter (unchanged from v1).
        if not request.headers or "Authorization" not in request.headers:
            return Response(401, "Unauthorized")

        # 2. Circuit breaker filter (now rolling-rate with half-open probes).
        if not self.circuit_breaker.allow_request():
            return Response(503, "Service Unavailable")

        downstream = downstream if downstream is not None else self._default_downstream
        scrubbed = self.scrub_headers(request.headers)

        # 3. Bounded retries with exponential backoff + jitter (v2 item 2).
        attempt = 0
        while True:
            try:
                response = downstream(request.path, scrubbed)
                if response.status_code >= 500:
                    raise DownstreamError(
                        "downstream returned %d" % response.status_code
                    )
                self.circuit_breaker.record_success()
                return response
            except DownstreamError:
                if attempt >= self._max_retries:
                    self.circuit_breaker.record_failure()
                    return Response(502, "Bad Gateway")
                base_delay = self._backoff_base * (2 ** attempt)
                self._sleeper(base_delay + self._rng.uniform(0, base_delay))
                attempt += 1
