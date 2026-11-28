import random
import unittest
import sys
import os

# Add v2-extended to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../v2-extended')))

from api_gateway_simulator_v2 import (
    ApiGatewaySimulator,
    CircuitBreaker,
    DownstreamError,
    Request,
    Response,
)


def make_gateway(breaker=None, max_retries=2, backoff_base=0.5, delays=None, seed=7):
    sleeper = delays.append if delays is not None else (lambda d: None)
    return ApiGatewaySimulator(
        max_retries=max_retries,
        backoff_base=backoff_base,
        sleeper=sleeper,
        rng=random.Random(seed),
        circuit_breaker=breaker,
    )


def authed_request(extra_headers=None):
    headers = {"Authorization": "Bearer valid-token"}
    if extra_headers:
        headers.update(extra_headers)
    return Request("/api/v1/data", headers)


class FakeClock:
    def __init__(self, now=1000.0):
        self.now = now

    def __call__(self):
        return self.now

    def advance(self, seconds):
        self.now += seconds


class TestApiGatewaySimulatorV2(unittest.TestCase):
    # --- v1 parity -----------------------------------------------------------

    def test_normal_trace(self):
        gateway = make_gateway()
        res = gateway.handle_request(authed_request())
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.body, "OK from downstream")

    def test_missing_authorization_returns_401(self):
        gateway = make_gateway()
        res = gateway.handle_request(Request("/api/v1/data", {}))
        self.assertEqual(res.status_code, 401)
        self.assertEqual(res.body, "Unauthorized")

    def test_open_breaker_fast_fails_503(self):
        gateway = make_gateway()
        gateway.circuit_breaker.trip_open()
        res = gateway.handle_request(authed_request())
        self.assertEqual(res.status_code, 503)
        self.assertEqual(res.body, "Service Unavailable")

    # --- v2 item 1: header scrubbing -----------------------------------------

    def test_internal_headers_scrubbed_before_forwarding(self):
        captured = {}

        def downstream(path, headers):
            captured.update(headers)
            return Response(200, "OK")

        gateway = make_gateway()
        req = authed_request(
            {
                "X-Internal-Auth": "spoofed-admin",
                "X-INTERNAL-ROUTE": "/admin",
                "X-Gateway-Internal": "1",
                "X-Custom": "keep-me",
            }
        )
        res = gateway.handle_request(req, downstream)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(
            captured,
            {"Authorization": "Bearer valid-token", "X-Custom": "keep-me"},
        )

    # --- v2 item 2: retries with backoff + jitter ----------------------------

    def test_retry_recovers_from_transient_failure(self):
        calls = []

        def flaky(path, headers):
            calls.append(1)
            if len(calls) == 1:
                raise DownstreamError("simulated timeout")
            return Response(200, "recovered")

        delays = []
        gateway = make_gateway(delays=delays)
        res = gateway.handle_request(authed_request(), flaky)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.body, "recovered")
        self.assertEqual(len(calls), 2)
        # One backoff sleep between the two attempts.
        self.assertEqual(len(delays), 1)

    def test_retry_exhausted_returns_502(self):
        calls = []

        def always_down(path, headers):
            calls.append(1)
            raise DownstreamError("simulated timeout")

        gateway = make_gateway(max_retries=2)
        res = gateway.handle_request(authed_request(), always_down)
        self.assertEqual(res.status_code, 502)
        self.assertEqual(res.body, "Bad Gateway")
        # 1 initial attempt + 2 retries = 3 downstream calls.
        self.assertEqual(len(calls), 3)

    def test_backoff_delays_grow_exponentially_with_bounded_jitter(self):
        calls = []

        def always_down(path, headers):
            calls.append(1)
            raise DownstreamError("simulated timeout")

        delays = []
        # base = 0.5: attempt 0 delay in [0.5, 1.0), attempt 1 in [1.0, 2.0),
        # attempt 2 in [2.0, 4.0): base * 2**attempt plus jitter in [0, base * 2**attempt).
        gateway = make_gateway(max_retries=3, backoff_base=0.5, delays=delays)
        gateway.handle_request(authed_request(), always_down)
        self.assertEqual(len(delays), 3)
        for attempt, delay in enumerate(delays):
            base = 0.5 * (2 ** attempt)
            self.assertGreaterEqual(delay, base)
            self.assertLess(delay, base + base)

    def test_downstream_5xx_is_retried_like_a_timeout(self):
        calls = []

        def error_then_ok(path, headers):
            calls.append(1)
            if len(calls) == 1:
                return Response(500, "boom")
            return Response(200, "fine")

        gateway = make_gateway()
        res = gateway.handle_request(authed_request(), error_then_ok)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(calls), 2)

    # --- v2 item 3: rolling-rate half-open circuit breaker -------------------

    def test_breaker_opens_on_rolling_failure_rate(self):
        breaker = CircuitBreaker(
            failure_rate_threshold=0.5, window_size=4, min_samples=4
        )
        breaker.record_success()
        breaker.record_success()
        breaker.record_failure()
        self.assertEqual(breaker.state, "CLOSED")  # below min_samples
        breaker.record_failure()
        # 2 failures / 4 samples = 0.5 >= 0.5 threshold -> OPEN.
        self.assertEqual(breaker.state, "OPEN")

    def test_open_breaker_skips_downstream_entirely(self):
        calls = []

        def downstream(path, headers):
            calls.append(1)
            return Response(200, "OK")

        gateway = make_gateway()
        gateway.circuit_breaker.trip_open()
        res = gateway.handle_request(authed_request(), downstream)
        self.assertEqual(res.status_code, 503)
        self.assertEqual(calls, [])

    def test_half_open_probe_success_closes_breaker(self):
        clock = FakeClock()
        breaker = CircuitBreaker(reset_timeout=10.0, clock=clock)
        breaker.trip_open()
        clock.advance(11.0)
        gateway = make_gateway(breaker=breaker)
        res = gateway.handle_request(authed_request())
        self.assertEqual(res.status_code, 200)
        self.assertEqual(breaker.state, "CLOSED")

    def test_half_open_probe_failure_reopens_breaker(self):
        clock = FakeClock()
        breaker = CircuitBreaker(reset_timeout=10.0, clock=clock)
        breaker.trip_open()
        clock.advance(11.0)

        def always_down(path, headers):
            raise DownstreamError("still down")

        # No retries during the probe: a single failure must reopen instantly.
        gateway = make_gateway(breaker=breaker, max_retries=0)
        res = gateway.handle_request(authed_request(), always_down)
        self.assertEqual(res.status_code, 502)
        self.assertEqual(breaker.state, "OPEN")
        # The reopened breaker fast-fails the next request.
        res = gateway.handle_request(authed_request(), always_down)
        self.assertEqual(res.status_code, 503)

    def test_half_open_admits_only_one_probe(self):
        clock = FakeClock()
        breaker = CircuitBreaker(reset_timeout=10.0, clock=clock)
        breaker.trip_open()
        clock.advance(11.0)
        self.assertTrue(breaker.allow_request())   # the probe
        self.assertFalse(breaker.allow_request())  # second request waits

    def test_window_ages_out_old_failures(self):
        breaker = CircuitBreaker(
            failure_rate_threshold=0.5, window_size=4, min_samples=4
        )
        breaker.record_failure()
        breaker.record_failure()
        for _ in range(4):
            breaker.record_success()
        # The two old failures fell out of the 4-sample window: all successes.
        self.assertEqual(breaker.state, "CLOSED")

    def test_invalid_policy_values_rejected(self):
        with self.assertRaises(ValueError):
            CircuitBreaker(failure_rate_threshold=0.0)
        with self.assertRaises(ValueError):
            CircuitBreaker(window_size=0)
        with self.assertRaises(ValueError):
            CircuitBreaker(window_size=4, min_samples=5)
        with self.assertRaises(ValueError):
            ApiGatewaySimulator(max_retries=-1)


if __name__ == '__main__':
    unittest.main()
