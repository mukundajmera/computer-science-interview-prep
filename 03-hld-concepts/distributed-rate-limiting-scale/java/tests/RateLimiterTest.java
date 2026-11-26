package implementation;

import org.junit.jupiter.api.Test;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicInteger;

import static org.junit.jupiter.api.Assertions.*;

public class RateLimiterTest {

    @Test
    public void testSlidingWindowCounterAccuracy() {
        RedisSimulator redis = new RedisSimulator();
        String userId = "user1";
        String limit = "100";
        String windowSec = "60";

        // Previous window 80 requests
        for (int i = 0; i < 80; i++) {
            long res = redis.evalLua("sliding_window_increment", new String[]{userId}, new String[]{limit, windowSec, "30"});
            assertEquals(1, res);
        }

        long currentTime = 75;
        int allowedCount = 0;
        for (int i = 0; i < 50; i++) {
            if (redis.evalLua("sliding_window_increment", new String[]{userId}, new String[]{limit, windowSec, String.valueOf(currentTime)}) == 1) {
                allowedCount++;
            }
        }

        assertEquals(40, allowedCount);
    }

    @Test
    public void testLuaScriptAtomicitySimulation() throws InterruptedException {
        RedisSimulator redis = new RedisSimulator();
        String userId = "user2";
        String limit = "1000";
        String windowSec = "60";
        String currentTime = "100";

        ExecutorService executor = Executors.newFixedThreadPool(10);
        AtomicInteger totalAllowed = new AtomicInteger(0);

        for (int i = 0; i < 10; i++) {
            executor.submit(() -> {
                int allowed = 0;
                for (int j = 0; j < 200; j++) {
                    if (redis.evalLua("sliding_window_increment", new String[]{userId}, new String[]{limit, windowSec, currentTime}) == 1) {
                        allowed++;
                    }
                }
                totalAllowed.addAndGet(allowed);
            });
        }

        executor.shutdown();
        executor.awaitTermination(10, TimeUnit.SECONDS);

        assertEquals(1000, totalAllowed.get());
    }

    @Test
    public void testLocalBatchingSpeedAndExhaustion() {
        RedisSimulator redis = new RedisSimulator();
        long globalLimit = 50;
        long batchSize = 20;
        long windowSec = 60;
        long currentTime = 100;

        Tier1DistributedRateLimiter limiter = new Tier1DistributedRateLimiter(redis, globalLimit, windowSec, batchSize);

        assertTrue(limiter.allowRequest("user3", currentTime));
        assertTrue(limiter.allowRequest("user3", currentTime));

        assertEquals(18, limiter.getLocalTokens("user3"));

        for (int i = 0; i < 18; i++) {
            assertTrue(limiter.allowRequest("user3", currentTime));
        }

        for (int i = 0; i < 20; i++) {
            assertTrue(limiter.allowRequest("user3", currentTime));
        }

        for (int i = 0; i < 10; i++) {
            assertTrue(limiter.allowRequest("user3", currentTime));
        }

        assertFalse(limiter.allowRequest("user3", currentTime));
    }

    @Test
    public void testDistributedGatewayWorkers() {
        RedisSimulator redis = new RedisSimulator();
        long globalLimit = 100;
        long batchSize = 30;
        long windowSec = 60;
        long currentTime = 200;

        Tier1DistributedRateLimiter gateway1 = new Tier1DistributedRateLimiter(redis, globalLimit, windowSec, batchSize);
        Tier1DistributedRateLimiter gateway2 = new Tier1DistributedRateLimiter(redis, globalLimit, windowSec, batchSize);

        assertTrue(gateway1.allowRequest("user4", currentTime));
        assertTrue(gateway2.allowRequest("user4", currentTime));

        for (int i = 0; i < 50; i++) {
            gateway1.allowRequest("user4", currentTime);
        }

        int allowedGw2 = 0;
        for (int i = 0; i < 50; i++) {
            if (gateway2.allowRequest("user4", currentTime)) {
                allowedGw2++;
            }
        }

        assertEquals(39, allowedGw2);
    }
}
