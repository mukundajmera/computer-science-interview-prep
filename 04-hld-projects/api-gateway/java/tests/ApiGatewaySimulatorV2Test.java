package tests;

import v2_extended.ApiGatewaySimulator;
import v2_extended.CircuitBreaker;
import v2_extended.DownstreamError;
import v2_extended.Request;
import v2_extended.Response;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Random;

public class ApiGatewaySimulatorV2Test {

    private static class FakeClock implements v2_extended.TimeSource {
        long now = 1_000_000L;
        public long nowMillis() { return now; }
        void advance(long millis) { now += millis; }
    }

    public static void main(String[] args) {
        testNormalTrace();
        testMissingAuthorizationReturns401();
        testOpenBreakerFastFails503();
        testInternalHeadersScrubbedBeforeForwarding();
        testRetryRecoversFromTransientFailure();
        testRetryExhaustedReturns502();
        testBackoffDelaysGrowExponentiallyWithBoundedJitter();
        testDownstream5xxIsRetriedLikeATimeout();
        testBreakerOpensOnRollingFailureRate();
        testOpenBreakerSkipsDownstreamEntirely();
        testHalfOpenProbeSuccessClosesBreaker();
        testHalfOpenProbeFailureReopensBreaker();
        testHalfOpenAdmitsOnlyOneProbe();
        testWindowAgesOutOldFailures();
        testInvalidPolicyValuesRejected();
        System.out.println("All Java API Gateway V2 tests passed!");
    }

    private static ApiGatewaySimulator makeGateway(CircuitBreaker breaker,
                                                   int maxRetries,
                                                   long backoffBaseMillis,
                                                   List<Long> delays) {
        return new ApiGatewaySimulator(
                maxRetries,
                backoffBaseMillis,
                delays::add,
                new Random(7),
                breaker);
    }

    private static ApiGatewaySimulator makeGateway() {
        return makeGateway(new CircuitBreaker(), 2, 500L, new ArrayList<>());
    }

    private static Request authedRequest() {
        Map<String, String> headers = new HashMap<>();
        headers.put("Authorization", "Bearer valid-token");
        return new Request("/api/v1/data", headers);
    }

    private static void check(boolean condition, String message) {
        if (!condition) {
            throw new RuntimeException(message);
        }
    }

    // --- v1 parity -----------------------------------------------------------

    private static void testNormalTrace() {
        ApiGatewaySimulator gateway = makeGateway();
        Response res = gateway.handleRequest(authedRequest());
        check(res.statusCode == 200, "Expected 200 OK, got " + res.statusCode);
        check("OK from downstream".equals(res.body), "Unexpected body: " + res.body);
    }

    private static void testMissingAuthorizationReturns401() {
        ApiGatewaySimulator gateway = makeGateway();
        Response res = gateway.handleRequest(new Request("/api/v1/data", new HashMap<>()));
        check(res.statusCode == 401, "Expected 401, got " + res.statusCode);
    }

    private static void testOpenBreakerFastFails503() {
        ApiGatewaySimulator gateway = makeGateway();
        gateway.getCircuitBreaker().tripOpen();
        Response res = gateway.handleRequest(authedRequest());
        check(res.statusCode == 503, "Expected 503, got " + res.statusCode);
    }

    // --- v2 item 1: header scrubbing -----------------------------------------

    private static void testInternalHeadersScrubbedBeforeForwarding() {
        Map<String, String> captured = new HashMap<>();
        ApiGatewaySimulator gateway = makeGateway();
        Map<String, String> headers = new HashMap<>();
        headers.put("Authorization", "Bearer valid-token");
        headers.put("X-Internal-Auth", "spoofed-admin");
        headers.put("X-INTERNAL-ROUTE", "/admin");
        headers.put("X-Gateway-Internal", "1");
        headers.put("X-Custom", "keep-me");
        Response res = gateway.handleRequest(new Request("/api/v1/data", headers),
                (path, forwarded) -> {
                    captured.putAll(forwarded);
                    return new Response(200, "OK");
                });
        check(res.statusCode == 200, "Expected 200, got " + res.statusCode);
        check(captured.size() == 2, "Expected 2 forwarded headers, got " + captured.size());
        check("Bearer valid-token".equals(captured.get("Authorization")),
                "Authorization header missing after scrubbing");
        check("keep-me".equals(captured.get("X-Custom")), "X-Custom header missing after scrubbing");
    }

    // --- v2 item 2: retries with backoff + jitter ----------------------------

    private static void testRetryRecoversFromTransientFailure() {
        int[] calls = {0};
        List<Long> delays = new ArrayList<>();
        ApiGatewaySimulator gateway = makeGateway(new CircuitBreaker(), 2, 500L, delays);
        Response res = gateway.handleRequest(authedRequest(), (path, headers) -> {
            calls[0]++;
            if (calls[0] == 1) {
                throw new DownstreamError("simulated timeout");
            }
            return new Response(200, "recovered");
        });
        check(res.statusCode == 200, "Expected 200, got " + res.statusCode);
        check(calls[0] == 2, "Expected 2 downstream calls, got " + calls[0]);
        check(delays.size() == 1, "Expected 1 backoff sleep, got " + delays.size());
    }

    private static void testRetryExhaustedReturns502() {
        int[] calls = {0};
        ApiGatewaySimulator gateway = makeGateway();
        Response res = gateway.handleRequest(authedRequest(), (path, headers) -> {
            calls[0]++;
            throw new DownstreamError("simulated timeout");
        });
        check(res.statusCode == 502, "Expected 502, got " + res.statusCode);
        // 1 initial attempt + 2 retries = 3 downstream calls.
        check(calls[0] == 3, "Expected 3 downstream calls, got " + calls[0]);
    }

    private static void testBackoffDelaysGrowExponentiallyWithBoundedJitter() {
        List<Long> delays = new ArrayList<>();
        ApiGatewaySimulator gateway = makeGateway(new CircuitBreaker(), 3, 500L, delays);
        gateway.handleRequest(authedRequest(), (path, headers) -> {
            throw new DownstreamError("simulated timeout");
        });
        // base = 500 ms: attempt a delay in [500*2^a, 500*2^a + 500*2^a).
        check(delays.size() == 3, "Expected 3 backoff sleeps, got " + delays.size());
        for (int attempt = 0; attempt < delays.size(); attempt++) {
            long base = 500L * (1L << attempt);
            long delay = delays.get(attempt);
            check(delay >= base && delay < base + base,
                    "Delay " + delay + " outside [" + base + ", " + (base + base) + ")");
        }
    }

    private static void testDownstream5xxIsRetriedLikeATimeout() {
        int[] calls = {0};
        ApiGatewaySimulator gateway = makeGateway();
        Response res = gateway.handleRequest(authedRequest(), (path, headers) -> {
            calls[0]++;
            if (calls[0] == 1) {
                return new Response(500, "boom");
            }
            return new Response(200, "fine");
        });
        check(res.statusCode == 200, "Expected 200, got " + res.statusCode);
        check(calls[0] == 2, "Expected 2 downstream calls, got " + calls[0]);
    }

    // --- v2 item 3: rolling-rate half-open circuit breaker -------------------

    private static void testBreakerOpensOnRollingFailureRate() {
        CircuitBreaker breaker = new CircuitBreaker(0.5, 4, 4, 30000L, System::currentTimeMillis);
        breaker.recordSuccess();
        breaker.recordSuccess();
        breaker.recordFailure();
        check(breaker.getState() == CircuitBreaker.State.CLOSED,
                "Breaker opened before min_samples");
        breaker.recordFailure();
        // 2 failures / 4 samples = 0.5 >= 0.5 threshold -> OPEN.
        check(breaker.getState() == CircuitBreaker.State.OPEN,
                "Breaker did not open at 50% rolling failure rate");
    }

    private static void testOpenBreakerSkipsDownstreamEntirely() {
        int[] calls = {0};
        ApiGatewaySimulator gateway = makeGateway();
        gateway.getCircuitBreaker().tripOpen();
        Response res = gateway.handleRequest(authedRequest(), (path, headers) -> {
            calls[0]++;
            return new Response(200, "OK");
        });
        check(res.statusCode == 503, "Expected 503, got " + res.statusCode);
        check(calls[0] == 0, "Downstream called while breaker open");
    }

    private static void testHalfOpenProbeSuccessClosesBreaker() {
        FakeClock clock = new FakeClock();
        CircuitBreaker breaker = new CircuitBreaker(0.5, 10, 4, 10000L, clock);
        breaker.tripOpen();
        clock.advance(11000L);
        ApiGatewaySimulator gateway = makeGateway(breaker, 2, 500L, new ArrayList<>());
        Response res = gateway.handleRequest(authedRequest());
        check(res.statusCode == 200, "Expected 200, got " + res.statusCode);
        check(breaker.getState() == CircuitBreaker.State.CLOSED,
                "Probe success did not close breaker");
    }

    private static void testHalfOpenProbeFailureReopensBreaker() {
        FakeClock clock = new FakeClock();
        CircuitBreaker breaker = new CircuitBreaker(0.5, 10, 4, 10000L, clock);
        breaker.tripOpen();
        clock.advance(11000L);
        // No retries during the probe: a single failure must reopen instantly.
        ApiGatewaySimulator gateway = makeGateway(breaker, 0, 500L, new ArrayList<>());
        Response res = gateway.handleRequest(authedRequest(), (path, headers) -> {
            throw new DownstreamError("still down");
        });
        check(res.statusCode == 502, "Expected 502, got " + res.statusCode);
        check(breaker.getState() == CircuitBreaker.State.OPEN,
                "Probe failure did not reopen breaker");
        // The reopened breaker fast-fails the next request.
        res = gateway.handleRequest(authedRequest(), (path, headers) -> {
            throw new DownstreamError("still down");
        });
        check(res.statusCode == 503, "Expected 503 after reopen, got " + res.statusCode);
    }

    private static void testHalfOpenAdmitsOnlyOneProbe() {
        FakeClock clock = new FakeClock();
        CircuitBreaker breaker = new CircuitBreaker(0.5, 10, 4, 10000L, clock);
        breaker.tripOpen();
        clock.advance(11000L);
        check(breaker.allowRequest(), "Probe should be admitted");
        check(!breaker.allowRequest(), "Second request should wait while probe in flight");
    }

    private static void testWindowAgesOutOldFailures() {
        CircuitBreaker breaker = new CircuitBreaker(0.5, 4, 4, 30000L, System::currentTimeMillis);
        breaker.recordFailure();
        breaker.recordFailure();
        for (int i = 0; i < 4; i++) {
            breaker.recordSuccess();
        }
        // The two old failures fell out of the 4-sample window: all successes.
        check(breaker.getState() == CircuitBreaker.State.CLOSED,
                "Breaker opened despite failures aging out of the window");
    }

    private static void testInvalidPolicyValuesRejected() {
        expectIllegalArgument(() -> new CircuitBreaker(0.0, 10, 4, 30000L, System::currentTimeMillis));
        expectIllegalArgument(() -> new CircuitBreaker(0.5, 0, 4, 30000L, System::currentTimeMillis));
        expectIllegalArgument(() -> new CircuitBreaker(0.5, 4, 5, 30000L, System::currentTimeMillis));
        expectIllegalArgument(() -> new ApiGatewaySimulator(-1, 500L, Thread::sleep, new Random(), new CircuitBreaker()));
    }

    private static void expectIllegalArgument(Runnable action) {
        try {
            action.run();
        } catch (IllegalArgumentException expected) {
            return;
        }
        throw new RuntimeException("Expected IllegalArgumentException");
    }
}
