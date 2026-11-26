import java.util.Map;

public class RateLimiterTest {
    public static void main(String[] args) throws Exception {
        System.out.println("Running RateLimiterTest...");
        testCapacity(); testRefill(); testBurst();
        testPerUser(); testRemaining();
        testTiers(); testHeaders(); testMetrics();
        System.out.println("All tests passed.");
    }
    // TokenBucketRateLimiter Tests
    private static void testCapacity() {
        TokenBucketRateLimiter limiter = new TokenBucketRateLimiter(5, 1);
        for (int i = 0; i < 5; i++) {
            assertTrue(limiter.tryAcquire(), "testCapacity failed at index " + i);
        }
        assertFalse(limiter.tryAcquire(), "testCapacity failed");
        assertTrue(limiter.getWaitTimeMs() > 0, "testCapacity failed");
    }
    private static void testRefill() throws InterruptedException {
        TokenBucketRateLimiter limiter = new TokenBucketRateLimiter(1, 20);
        assertTrue(limiter.tryAcquire(), "testRefill failed");
        assertFalse(limiter.tryAcquire(), "testRefill failed");
        Thread.sleep(80);
        assertTrue(limiter.tryAcquire(), "testRefill failed after sleep");
    }
    private static void testBurst() {
        TokenBucketRateLimiter limiter = new TokenBucketRateLimiter(100, 1);
        int allowed = 0;
        for (int i = 0; i < 100; i++) {
            if (limiter.tryAcquire()) allowed++;
        }
        assertEquals(100, allowed, "testBurst failed");
        assertFalse(limiter.tryAcquire(), "testBurst failed");
    }
    // SlidingWindowRateLimiter Tests
    private static void testPerUser() {
        SlidingWindowRateLimiter limiter = new SlidingWindowRateLimiter(5, 60);
        for (int i = 0; i < 5; i++) {
            assertTrue(limiter.tryAcquire("user1").isAllowed(), "testPerUser failed");
        }
        assertFalse(limiter.tryAcquire("user1").isAllowed(), "testPerUser failed");
        assertTrue(limiter.tryAcquire("user2").isAllowed(), "testPerUser failed");
    }
    private static void testRemaining() {
        SlidingWindowRateLimiter limiter = new SlidingWindowRateLimiter(5, 60);
        assertEquals(4, limiter.tryAcquire("user").getRemaining(), "testRemaining failed 1");
        assertEquals(3, limiter.tryAcquire("user").getRemaining(), "testRemaining failed 2");
        assertEquals(2, limiter.tryAcquire("user").getRemaining(), "testRemaining failed 3");
    }
    // DistributedRateLimiter Tests
    private static void testTiers() {
        DistributedRateLimiter.InMemoryRateLimitStore store = new DistributedRateLimiter.InMemoryRateLimitStore();
        DistributedRateLimiter limiter = new DistributedRateLimiter(store);
        try {
            limiter.addTier(new DistributedRateLimiter.TierConfig("test", 3, 60, 1));
            for (int i = 0; i < 3; i++) {
                assertTrue(limiter.checkRateLimit("user", "test").isAllowed(), "testTiers failed");
            }
            DistributedRateLimiter.RateLimitDecision rejected = limiter.checkRateLimit("user", "test");
            assertFalse(rejected.isAllowed(), "testTiers failed");
            assertEquals("user", rejected.getLimitedBy(), "testTiers failed");
        } finally { limiter.shutdown(); }
    }
    private static void testHeaders() {
        DistributedRateLimiter.InMemoryRateLimitStore store = new DistributedRateLimiter.InMemoryRateLimitStore();
        DistributedRateLimiter limiter = new DistributedRateLimiter(store);
        try {
            DistributedRateLimiter.RateLimitDecision result = limiter.checkRateLimit("user", "free");
            Map<String, String> headers = result.getHeaders();
            assertTrue(result.isAllowed(), "testHeaders failed");
            assertEquals("100", headers.get("X-RateLimit-Limit"), "testHeaders failed");
            assertEquals("99", headers.get("X-RateLimit-Remaining"), "testHeaders failed");
            assertTrue(headers.containsKey("X-RateLimit-Reset"), "testHeaders failed");
        } finally { limiter.shutdown(); }
    }
    private static void testMetrics() {
        DistributedRateLimiter.InMemoryRateLimitStore store = new DistributedRateLimiter.InMemoryRateLimitStore();
        DistributedRateLimiter limiter = new DistributedRateLimiter(store);
        try {
            limiter.addTier(new DistributedRateLimiter.TierConfig("test", 2, 60, 1));
            limiter.checkRateLimit("user", "test");
            limiter.checkRateLimit("user", "test");
            limiter.checkRateLimit("user", "test");
            DistributedRateLimiter.Metrics metrics = limiter.getMetrics();
            assertEquals(3, metrics.getTotalRequests(), "testMetrics failed");
            assertEquals(2, metrics.getAllowedRequests(), "testMetrics failed");
            assertEquals(1, metrics.getRejectedRequests(), "testMetrics failed");
            assertEquals(1L, metrics.getRejectionsByTier().get("test"), "testMetrics failed");
        } finally { limiter.shutdown(); }
    }
    private static void assertTrue(boolean condition, String message) {
        if (!condition) throw new AssertionError(message);
    }
    private static void assertFalse(boolean condition, String message) {
        if (condition) throw new AssertionError(message);
    }
    private static void assertEquals(Object expected, Object actual, String message) {
        if (expected == null && actual == null) return;
        if (expected != null && expected.toString().equals(actual.toString())) return;
        throw new AssertionError(message + " - Expected: " + expected + ", Actual: " + actual);
    }
}
