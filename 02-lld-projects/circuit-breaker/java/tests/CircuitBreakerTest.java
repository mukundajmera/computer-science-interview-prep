import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.BeforeEach;
import static org.junit.jupiter.api.Assertions.*;

import java.util.concurrent.Callable;

public class CircuitBreakerTest {

    @Test
    public void testInitialStateIsClosed() {
        CircuitBreakerConfig config = new CircuitBreakerConfig(50, 10, 1000, 2, 50, 1000);
        CircuitBreaker cb = new CircuitBreaker(config);
        assertEquals(CircuitBreakerState.CLOSED, cb.getState());
    }

    @Test
    public void testSuccessfulCallsKeepStateClosed() throws Exception {
        CircuitBreakerConfig config = new CircuitBreakerConfig(50, 10, 1000, 2, 50, 1000);
        CircuitBreaker cb = new CircuitBreaker(config);
        
        Callable<String> successCall = () -> "Success";
        for (int i = 0; i < 5; i++) {
            assertEquals("Success", cb.execute(successCall));
        }
        assertEquals(CircuitBreakerState.CLOSED, cb.getState());
    }

    @Test
    public void testTransitionToOpenOnFailureThreshold() {
        CircuitBreakerConfig config = new CircuitBreakerConfig(50, 4, 1000, 2, 50, 1000);
        CircuitBreaker cb = new CircuitBreaker(config);
        
        Callable<String> failCall = () -> { throw new RuntimeException("Fail"); };
        Callable<String> successCall = () -> "Success";

        try { cb.execute(failCall); } catch (Exception e) {}
        try { cb.execute(failCall); } catch (Exception e) {}
        try { cb.execute(successCall); } catch (Exception e) {}
        try { cb.execute(failCall); } catch (Exception e) {}
        
        // 3 failures out of 4 calls = 75% > 50%
        assertEquals(CircuitBreakerState.OPEN, cb.getState());
    }

    @Test
    public void testTransitionToHalfOpenAfterWait() throws Exception {
        CircuitBreakerConfig config = new CircuitBreakerConfig(50, 2, 100, 2, 50, 1000);
        CircuitBreaker cb = new CircuitBreaker(config);
        
        Callable<String> failCall = () -> { throw new RuntimeException("Fail"); };

        try { cb.execute(failCall); } catch (Exception e) {}
        try { cb.execute(failCall); } catch (Exception e) {}
        
        assertEquals(CircuitBreakerState.OPEN, cb.getState());
        
        Thread.sleep(150); // wait duration is 100ms
        
        // Next call should transition to HALF_OPEN
        try { cb.execute(failCall); } catch (Exception e) {}
        assertEquals(CircuitBreakerState.OPEN, cb.getState()); // It failed again, so back to OPEN
    }
    
    @Test
    public void testFallbackExecution() throws Exception {
        CircuitBreakerConfig config = new CircuitBreakerConfig(50, 2, 100, 2, 50, 1000);
        CircuitBreaker cb = new CircuitBreaker(config);
        
        Callable<String> failCall = () -> { throw new RuntimeException("Fail"); };
        Fallback<String> fallback = (e) -> "FallbackResult";
        
        String result = cb.execute(failCall, fallback);
        assertEquals("FallbackResult", result);
    }
}
