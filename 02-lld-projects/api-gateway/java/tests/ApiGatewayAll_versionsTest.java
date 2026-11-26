package tests;

import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

import java.util.HashMap;
import java.util.Map;

public class ApiGatewayAll_versionsTest {

    // --- v1 tests ---
    @Test
    public void testV1BasicRouting() {
        v1_basic.ApiGateway gw = new v1_basic.ApiGateway();
        gw.registerBackend("users", req -> new v1_basic.ApiGateway.Response(200, null, "Users Data"));
        gw.addRoute("/api/users", "users");

        v1_basic.ApiGateway.Request req = new v1_basic.ApiGateway.Request("/api/users/1", "GET", null, null);
        v1_basic.ApiGateway.Response res = gw.handle(req);
        assertEquals(200, res.statusCode);
        assertEquals("Users Data", res.body);
    }

    @Test
    public void testV1NotFound() {
        v1_basic.ApiGateway gw = new v1_basic.ApiGateway();
        v1_basic.ApiGateway.Request req = new v1_basic.ApiGateway.Request("/api/unknown", "GET", null, null);
        v1_basic.ApiGateway.Response res = gw.handle(req);
        assertEquals(404, res.statusCode);
    }

    @Test
    public void testV1AuthFilterUnauthorized() {
        v1_basic.ApiGateway gw = new v1_basic.ApiGateway();
        gw.addPreFilter(new v1_basic.ApiGateway.AuthFilter());
        gw.registerBackend("users", req -> new v1_basic.ApiGateway.Response(200, null, "Users Data"));
        gw.addRoute("/api/users", "users");

        v1_basic.ApiGateway.Request req = new v1_basic.ApiGateway.Request("/api/users/1", "GET", null, null);
        v1_basic.ApiGateway.Response res = gw.handle(req);
        assertEquals(401, res.statusCode);
    }

    @Test
    public void testV1AuthFilterAuthorized() {
        v1_basic.ApiGateway gw = new v1_basic.ApiGateway();
        gw.addPreFilter(new v1_basic.ApiGateway.AuthFilter());
        gw.registerBackend("users", req -> new v1_basic.ApiGateway.Response(200, null, "Users Data"));
        gw.addRoute("/api/users", "users");

        Map<String, String> headers = new HashMap<>();
        headers.put("Authorization", "Bearer token");
        v1_basic.ApiGateway.Request req = new v1_basic.ApiGateway.Request("/api/users/1", "GET", headers, null);
        v1_basic.ApiGateway.Response res = gw.handle(req);
        assertEquals(200, res.statusCode);
    }
    
    @Test
    public void testV1BackendError() {
        v1_basic.ApiGateway gw = new v1_basic.ApiGateway();
        gw.registerBackend("users", req -> {
            throw new RuntimeException("DB Error");
        });
        gw.addRoute("/api/users", "users");
        
        v1_basic.ApiGateway.Request req = new v1_basic.ApiGateway.Request("/api/users/1", "POST", null, null);
        v1_basic.ApiGateway.Response res = gw.handle(req);
        assertEquals(500, res.statusCode);
    }
    
    @Test
    public void testV1BoundedRequestBody() {
        v1_basic.ApiGateway gw = new v1_basic.ApiGateway();
        gw.registerBackend("users", req -> new v1_basic.ApiGateway.Response(200, null, "OK"));
        gw.addRoute("/api/users", "users");
        
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < 1024 * 1024 + 1; i++) {
            sb.append("a");
        }
        v1_basic.ApiGateway.Request req = new v1_basic.ApiGateway.Request("/api/users/1", "POST", null, sb.toString());
        v1_basic.ApiGateway.Response res = gw.handle(req);
        assertEquals(413, res.statusCode);
    }

    @Test
    public void testV1DownstreamCancellation() {
        v1_basic.ApiGateway gw = new v1_basic.ApiGateway();
        gw.registerBackend("users", req -> new v1_basic.ApiGateway.Response(200, null, "OK"));
        gw.addRoute("/api/users", "users");
        
        v1_basic.ApiGateway.Request req = new v1_basic.ApiGateway.Request("/api/users/1", "GET", null, null);
        req.isCancelled = true;
        v1_basic.ApiGateway.Response res = gw.handle(req);
        assertEquals(499, res.statusCode);
    }

    @Test
    public void testV1DeadlinePropagation() {
        v1_basic.ApiGateway gw = new v1_basic.ApiGateway();
        gw.registerBackend("users", req -> new v1_basic.ApiGateway.Response(200, null, "OK"));
        gw.addRoute("/api/users", "users");
        
        v1_basic.ApiGateway.Request req = new v1_basic.ApiGateway.Request("/api/users/1", "GET", null, null);
        req.deadlineMs = System.currentTimeMillis() - 1000; // Past
        v1_basic.ApiGateway.Response res = gw.handle(req);
        assertEquals(504, res.statusCode);
    }

    @Test
    public void testV1DuplicateRetryEligibility() {
        v1_basic.ApiGateway gw = new v1_basic.ApiGateway();
        int[] calls = {0};
        gw.registerBackend("users", req -> {
            calls[0]++;
            if (calls[0] == 1) throw new RuntimeException("DB Error");
            return new v1_basic.ApiGateway.Response(200, null, "OK");
        });
        gw.addRoute("/api/users", "users");
        
        v1_basic.ApiGateway.Request req = new v1_basic.ApiGateway.Request("/api/users/1", "GET", null, null);
        v1_basic.ApiGateway.Response res = gw.handle(req);
        assertEquals(200, res.statusCode);
        assertEquals(2, calls[0]);
    }

    // --- v2 tests ---
    @Test
    public void testV2RateLimiting() {
        v2_extended.ApiGateway gw = new v2_extended.ApiGateway();
        gw.addFilter(new v2_extended.ApiGateway.RateLimitFilter(2, 1));
        gw.registerBackend("users", req -> new v2_extended.ApiGateway.Response(200, null, "Users Data"));
        gw.addRoute("/api/users", "users");

        Map<String, String> headers = new HashMap<>();
        headers.put("Client-ID", "test_client");
        v2_extended.ApiGateway.Request req = new v2_extended.ApiGateway.Request("/api/users/1", "GET", headers, null);

        assertEquals(200, gw.handle(req).statusCode);
        assertEquals(200, gw.handle(req).statusCode);
        assertEquals(429, gw.handle(req).statusCode);
    }

    @Test
    public void testV2LoggingFilter() {
        v2_extended.ApiGateway gw = new v2_extended.ApiGateway();
        v2_extended.ApiGateway.LoggingFilter logger = new v2_extended.ApiGateway.LoggingFilter();
        gw.addFilter(logger);
        gw.registerBackend("users", req -> new v2_extended.ApiGateway.Response(200, null, "Users Data"));
        gw.addRoute("/api/users", "users");

        v2_extended.ApiGateway.Request req = new v2_extended.ApiGateway.Request("/api/users/1", "GET", null, null);
        gw.handle(req);
        
        assertEquals(1, logger.logs.size());
        assertTrue(logger.logs.get(0).contains("200"));
    }
    
    @Test
    public void testV2MultipleFilters() {
        v2_extended.ApiGateway gw = new v2_extended.ApiGateway();
        gw.addFilter(new v2_extended.ApiGateway.AuthFilter());
        gw.addFilter(new v2_extended.ApiGateway.RateLimitFilter(2, 1));
        gw.registerBackend("users", req -> new v2_extended.ApiGateway.Response(200, null, "Users Data"));
        gw.addRoute("/api/users", "users");
        
        Map<String, String> headers1 = new HashMap<>();
        headers1.put("Client-ID", "test");
        v2_extended.ApiGateway.Request req1 = new v2_extended.ApiGateway.Request("/api/users/1", "GET", headers1, null);
        assertEquals(401, gw.handle(req1).statusCode);
        
        Map<String, String> headers2 = new HashMap<>();
        headers2.put("Authorization", "token");
        headers2.put("Client-ID", "test");
        v2_extended.ApiGateway.Request req2 = new v2_extended.ApiGateway.Request("/api/users/1", "GET", headers2, null);
        assertEquals(200, gw.handle(req2).statusCode);
    }

    // --- v3 tests ---
    @Test
    public void testV3CircuitBreaker() {
        v3_optimized.ApiGateway gw = new v3_optimized.ApiGateway();
        gw.registerBackend("flaky", req -> new v3_optimized.ApiGateway.Response(500, null, "Error"));
        gw.addRoute("/api", "flaky");

        v3_optimized.ApiGateway.Request req = new v3_optimized.ApiGateway.Request("/api/test", "GET", null, null);

        // 3 failures
        assertEquals(500, gw.handle(req).statusCode);
        assertEquals(500, gw.handle(req).statusCode);
        assertEquals(500, gw.handle(req).statusCode);

        // 4th fails fast
        v3_optimized.ApiGateway.Response res = gw.handle(req);
        assertEquals(503, res.statusCode);
        assertTrue(res.body.toString().contains("Circuit Open"));
    }

    @Test
    public void testV3CircuitBreakerRecovery() throws InterruptedException {
        v3_optimized.ApiGateway gw = new v3_optimized.ApiGateway();
        
        // Custom backend that responds 500 then 200
        int[] status = {500};
        gw.registerBackend("dynamic", req -> new v3_optimized.ApiGateway.Response(status[0], null, "Dynamic"));
        
        // Custom short-timeout CB
        v3_optimized.ApiGateway.CircuitBreaker cb = new v3_optimized.ApiGateway.CircuitBreaker(3, 1);
        gw.addRoute("/api", "dynamic", cb);

        v3_optimized.ApiGateway.Request req = new v3_optimized.ApiGateway.Request("/api/test", "GET", null, null);

        gw.handle(req);
        gw.handle(req);
        gw.handle(req);
        assertEquals(503, gw.handle(req).statusCode);

        Thread.sleep(1100);
        
        status[0] = 200;
        assertEquals(200, gw.handle(req).statusCode);
        assertEquals(v3_optimized.ApiGateway.CircuitBreaker.State.CLOSED, gw.getCircuitBreakers().get("dynamic").getState());
    }

    @Test
    public void testV3ConcurrentRateLimiting() throws InterruptedException {
        v3_optimized.ApiGateway gw = new v3_optimized.ApiGateway();
        gw.addFilter(new v3_optimized.ApiGateway.RateLimitFilter(5, 1));
        gw.registerBackend("users", req -> new v3_optimized.ApiGateway.Response(200, null, "Users Data"));
        gw.addRoute("/api/users", "users");

        Map<String, String> headers = new HashMap<>();
        headers.put("Client-ID", "concurrent_test");
        v3_optimized.ApiGateway.Request req = new v3_optimized.ApiGateway.Request("/api/users/1", "GET", headers, null);

        int[] results = new int[10];
        Thread[] threads = new Thread[10];

        for (int i = 0; i < 10; i++) {
            final int index = i;
            threads[i] = new Thread(() -> {
                results[index] = gw.handle(req).statusCode;
            });
            threads[i].start();
        }

        for (Thread t : threads) {
            t.join();
        }

        int successes = 0;
        int tooMany = 0;
        for (int status : results) {
            if (status == 200) successes++;
            else if (status == 429) tooMany++;
        }

        assertEquals(5, successes);
        assertEquals(5, tooMany);
    }
    
    @Test
    public void testV3LoggingWithDuration() throws InterruptedException {
        v3_optimized.ApiGateway gw = new v3_optimized.ApiGateway();
        v3_optimized.ApiGateway.LoggingFilter logger = new v3_optimized.ApiGateway.LoggingFilter();
        gw.addFilter(logger);
        
        gw.registerBackend("slow", req -> {
            try { Thread.sleep(50); } catch (Exception e) {}
            return new v3_optimized.ApiGateway.Response(200, null, "OK");
        });
        gw.addRoute("/api/slow", "slow");
        
        v3_optimized.ApiGateway.Request req = new v3_optimized.ApiGateway.Request("/api/slow/test", "GET", null, null);
        gw.handle(req);
        
        assertEquals(1, logger.logs.size());
        assertTrue(logger.logs.get(0).contains("GET /api/slow/test 200"));
        assertTrue(logger.logs.get(0).contains("ms"));
    }
    
    @Test
    public void testV3CircuitBreakerExcludeOwnRejections() {
        v3_optimized.ApiGateway gw = new v3_optimized.ApiGateway();
        
        // CB threshold is 3 by default
        gw.addFilter(new v3_optimized.ApiGateway.RateLimitFilter(1, 10)); // Fail after 1st req
        gw.registerBackend("users", req -> new v3_optimized.ApiGateway.Response(200, null, "OK"));
        gw.addRoute("/api", "users");
        
        Map<String, String> headers = new HashMap<>();
        headers.put("Client-ID", "test");
        v3_optimized.ApiGateway.Request req = new v3_optimized.ApiGateway.Request("/api/test", "GET", headers, null);
        
        assertEquals(200, gw.handle(req).statusCode); // Success
        assertEquals(429, gw.handle(req).statusCode); // Fail fast (rate limit)
        assertEquals(429, gw.handle(req).statusCode);
        assertEquals(429, gw.handle(req).statusCode);
        assertEquals(429, gw.handle(req).statusCode);
        
        // Circuit should still be CLOSED and failures = 0
        v3_optimized.ApiGateway.CircuitBreaker cb = gw.getCircuitBreakers().get("users");
        assertEquals(v3_optimized.ApiGateway.CircuitBreaker.State.CLOSED, cb.getState());
        assertEquals(0, cb.getFailures());
    }
}
