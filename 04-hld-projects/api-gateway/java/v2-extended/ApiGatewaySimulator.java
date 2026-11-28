package v2_extended;

import java.util.Arrays;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Map;
import java.util.Random;
import java.util.Set;

/**
 * v2-extended API gateway simulator.
 *
 * Improvements over v1-basic (named per the repo rule v1-basic -> v2-extended):
 * 1. Header scrubbing in the security filter: internal routing/identity
 *    headers are stripped before forwarding so clients cannot spoof
 *    gateway-trusted metadata downstream (see PITFALLS.md).
 * 2. Bounded retries with exponential backoff and jitter around an injectable
 *    downstream callable, so transient failures are absorbed without the
 *    synchronized retry storms PITFALLS.md and FOLLOW-UPS.md warn about.
 * 3. A half-open circuit breaker driven by a rolling failure-rate window with
 *    configurable policies, replacing v1's breaker that opened on consecutive
 *    failures and never recovered.
 */
public class ApiGatewaySimulator {

    /** Headers the gateway owns; client-supplied copies are stripped. */
    static final Set<String> SCRUBBED_HEADERS = new HashSet<>(Arrays.asList(
            "x-internal-auth", "x-internal-route", "x-gateway-internal"));

    private final CircuitBreaker circuitBreaker;
    private final int maxRetries;
    private final long backoffBaseMillis;
    private final Sleeper sleeper;
    private final Random rng;

    public ApiGatewaySimulator(int maxRetries, long backoffBaseMillis,
                               Sleeper sleeper, Random rng,
                               CircuitBreaker circuitBreaker) {
        if (maxRetries < 0) {
            throw new IllegalArgumentException("maxRetries must be >= 0");
        }
        if (backoffBaseMillis < 0) {
            throw new IllegalArgumentException("backoffBaseMillis must be >= 0");
        }
        this.circuitBreaker = circuitBreaker;
        this.maxRetries = maxRetries;
        this.backoffBaseMillis = backoffBaseMillis;
        this.sleeper = sleeper;
        this.rng = rng;
    }

    public ApiGatewaySimulator() {
        this(2, 100L, Thread::sleep, new Random(), new CircuitBreaker());
    }

    public CircuitBreaker getCircuitBreaker() {
        return circuitBreaker;
    }

    /** Drop gateway-owned internal headers before forwarding (v2 item 1). */
    public static Map<String, String> scrubHeaders(Map<String, String> headers) {
        Map<String, String> scrubbed = new HashMap<>();
        for (Map.Entry<String, String> entry : headers.entrySet()) {
            if (!SCRUBBED_HEADERS.contains(entry.getKey().toLowerCase())) {
                scrubbed.put(entry.getKey(), entry.getValue());
            }
        }
        return scrubbed;
    }

    public Response handleRequest(Request request) {
        return handleRequest(request,
                (path, headers) -> new Response(200, "OK from downstream"));
    }

    public Response handleRequest(Request request, Downstream downstream) {
        // 1. Security/Auth filter (unchanged from v1).
        if (request.headers == null || !request.headers.containsKey("Authorization")) {
            return new Response(401, "Unauthorized");
        }

        // 2. Circuit breaker filter (now rolling-rate with half-open probes).
        if (!circuitBreaker.allowRequest()) {
            return new Response(503, "Service Unavailable");
        }

        Map<String, String> scrubbed = scrubHeaders(request.headers);

        // 3. Bounded retries with exponential backoff + jitter (v2 item 2).
        int attempt = 0;
        while (true) {
            try {
                Response response = downstream.call(request.path, scrubbed);
                if (response.statusCode >= 500) {
                    throw new DownstreamError("downstream returned " + response.statusCode);
                }
                circuitBreaker.recordSuccess();
                return response;
            } catch (DownstreamError error) {
                if (attempt >= maxRetries) {
                    circuitBreaker.recordFailure();
                    return new Response(502, "Bad Gateway");
                }
                long baseDelay = backoffBaseMillis * (1L << attempt);
                try {
                    sleeper.sleep(baseDelay + (long) (rng.nextDouble() * baseDelay));
                } catch (InterruptedException interrupted) {
                    Thread.currentThread().interrupt();
                    circuitBreaker.recordFailure();
                    return new Response(502, "Bad Gateway");
                }
                attempt++;
            }
        }
    }
}
