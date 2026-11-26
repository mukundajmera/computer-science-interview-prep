package resilience;

import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

import java.time.Clock;
import java.time.Instant;
import java.time.ZoneId;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.concurrent.CountDownLatch;

public class ResilienceOrchestratorTest {

    @Test
    public void testCircuitBreakerTripsToOpen() {
        ResilienceOrchestrator orchestrator = new ResilienceOrchestrator(2, 1000, 10, 0, 10);
        
        AtomicInteger calls = new AtomicInteger(0);
        
        // 1st failure
        assertEquals("fallback", orchestrator.execute(() -> {
            calls.incrementAndGet();
            throw new RuntimeException("fail");
        }, () -> "fallback"));
        
        // 2nd failure - threshold reached, should trip
        assertEquals("fallback", orchestrator.execute(() -> {
            calls.incrementAndGet();
            throw new RuntimeException("fail");
        }, () -> "fallback"));
        
        // 3rd call - Circuit is OPEN, fast fail
        assertEquals("fallback", orchestrator.execute(() -> {
            calls.incrementAndGet();
            return "success";
        }, () -> "fallback"));
        
        assertEquals(2, calls.get(), "Action should only be called twice before opening");
    }

    @Test
    public void testCircuitBreakerHalfOpenRecovery() throws InterruptedException {
        // Need to test inner logic closely, we can instantiate CB
        ResilienceOrchestrator.CircuitBreaker cb = new ResilienceOrchestrator.CircuitBreaker(2, 100);
        
        // Fail twice
        assertThrows(Exception.class, () -> cb.execute(() -> { throw new RuntimeException("fail"); }));
        assertThrows(Exception.class, () -> cb.execute(() -> { throw new RuntimeException("fail"); }));
        
        assertEquals(ResilienceOrchestrator.CircuitBreaker.State.OPEN, cb.getState());
        
        Thread.sleep(150); // wait for reset timeout
        
        // Probe 1
        assertEquals("success", cb.execute(() -> "success"));
        assertEquals(ResilienceOrchestrator.CircuitBreaker.State.HALF_OPEN, cb.getState());
        
        // Probe 2
        assertEquals("success", cb.execute(() -> "success"));
        
        // Probe 3
        assertEquals("success", cb.execute(() -> "success"));
        
        assertEquals(ResilienceOrchestrator.CircuitBreaker.State.CLOSED, cb.getState());
    }

    @Test
    public void testBulkheadRejection() throws InterruptedException {
        ResilienceOrchestrator orchestrator = new ResilienceOrchestrator(5, 1000, 2, 0, 10);
        
        CountDownLatch latch = new CountDownLatch(1);
        CountDownLatch doneLatch = new CountDownLatch(3);
        AtomicInteger successCount = new AtomicInteger(0);
        AtomicInteger fallbackCount = new AtomicInteger(0);
        
        Runnable task = () -> {
            String result = orchestrator.execute(() -> {
                try {
                    latch.await();
                } catch (InterruptedException e) {
                    Thread.currentThread().interrupt();
                }
                return "success";
            }, () -> "fallback");
            
            if ("success".equals(result)) {
                successCount.incrementAndGet();
            } else {
                fallbackCount.incrementAndGet();
            }
            doneLatch.countDown();
        };
        
        new Thread(task).start();
        new Thread(task).start();
        
        Thread.sleep(100); // ensure first two threads are blocking in semaphore
        
        // 3rd thread should be rejected
        new Thread(task).start();
        
        Thread.sleep(100);
        latch.countDown();
        doneLatch.await();
        
        assertEquals(2, successCount.get());
        assertEquals(1, fallbackCount.get(), "One task should have been rejected by bulkhead and used fallback");
    }

    @Test
    public void testJitterDelay() {
        ResilienceOrchestrator.RetryPolicy policy = new ResilienceOrchestrator.RetryPolicy(3, 100);
        AtomicInteger calls = new AtomicInteger(0);
        long start = System.currentTimeMillis();
        
        assertThrows(RuntimeException.class, () -> {
            policy.executeWithRetry(() -> {
                calls.incrementAndGet();
                throw new RuntimeException("fail");
            });
        });
        
        long end = System.currentTimeMillis();
        long duration = end - start;
        
        assertEquals(4, calls.get()); // 1 initial + 3 retries
        // Max possible delay: 100*2^0 + 100*2^1 + 100*2^2 = 100 + 200 + 400 = 700
        // Min possible delay: 0
        assertTrue(duration >= 0 && duration <= 800, "Duration should be within theoretical bounds");
    }
}
