import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

import java.util.concurrent.Callable;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.concurrent.atomic.AtomicLong;

public class CircuitBreakerAll_versionsTest {

    @Test
    public void testMonotonicStateTransitionsAndHalfOpenProbes() throws Exception {
        AtomicLong virtualTime = new AtomicLong(1000000L);
        CircuitBreakerConfig config = new CircuitBreakerConfig(50, 4, 1000, 2, 50, 1000);
        CircuitBreaker cb = new CircuitBreaker(config, virtualTime::get);
        
        Callable<String> failCall = () -> { throw new RuntimeException("Fail"); };
        
        try { cb.execute(failCall); } catch (Exception e) {}
        try { cb.execute(failCall); } catch (Exception e) {}
        try { cb.execute(failCall); } catch (Exception e) {}
        try { cb.execute(failCall); } catch (Exception e) {}
        
        assertEquals(CircuitBreakerState.OPEN, cb.getState());
        
        // Elapse enough time for OPEN -> HALF_OPEN
        virtualTime.addAndGet(1100);
        
        AtomicInteger executedInHalfOpen = new AtomicInteger(0);
        AtomicInteger rejectedByHalfOpen = new AtomicInteger(0);
        
        Callable<String> slowFailCall = () -> { 
            executedInHalfOpen.incrementAndGet();
            Thread.sleep(500); 
            throw new RuntimeException("Fail"); 
        };
        
        ExecutorService executor = Executors.newFixedThreadPool(8);
        CountDownLatch latch = new CountDownLatch(8);
        
        for (int i = 0; i < 8; i++) {
            executor.submit(() -> {
                try {
                    cb.execute(slowFailCall);
                } catch (CircuitBreakerOpenException e) {
                    rejectedByHalfOpen.incrementAndGet();
                } catch (Exception e) {
                    // Ignore expected exception from the call itself
                } finally {
                    latch.countDown();
                }
            });
        }
        
        latch.await();
        executor.shutdown();
        
        // Exact half_open calls enforcement
        assertEquals(2, executedInHalfOpen.get());
        assertEquals(6, rejectedByHalfOpen.get());
        assertEquals(CircuitBreakerState.OPEN, cb.getState());
    }

    @Test
    public void testStaleClosedCallbackDoesNotAffectOpenState() throws Exception {
        AtomicLong virtualTime = new AtomicLong(1000000L);
        CircuitBreakerConfig config = new CircuitBreakerConfig(50, 4, 1000, 2, 50, 1000);
        CircuitBreaker cb = new CircuitBreaker(config, virtualTime::get);
        
        CountDownLatch slowCallStarted = new CountDownLatch(1);
        CountDownLatch slowCallFinished = new CountDownLatch(1);
        CountDownLatch fastFailuresFinished = new CountDownLatch(1);
        
        Thread slowThread = new Thread(() -> {
            try {
                cb.execute(() -> {
                    slowCallStarted.countDown();
                    fastFailuresFinished.await(); // wait for state to turn OPEN
                    return "Slow Success";
                });
            } catch (Exception e) { }
            slowCallFinished.countDown();
        });
        
        slowThread.start();
        slowCallStarted.await(); // Call has read gen 0 and is executing
        
        Callable<String> failCall = () -> { throw new RuntimeException("Fail"); };
        // Breach threshold to OPEN state
        try { cb.execute(failCall); } catch (Exception e) {}
        try { cb.execute(failCall); } catch (Exception e) {}
        try { cb.execute(failCall); } catch (Exception e) {}
        try { cb.execute(failCall); } catch (Exception e) {}
        
        assertEquals(CircuitBreakerState.OPEN, cb.getState());
        
        fastFailuresFinished.countDown(); // Let the slow success finish
        slowCallFinished.await();
        
        // The slow success shouldn't transition us to CLOSED or evaluate state for Gen 1,
        // because its call generation was 0.
        assertEquals(CircuitBreakerState.OPEN, cb.getState());
    }
}
