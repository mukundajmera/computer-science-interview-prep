/**
 * V2: Circuit Breaker Pattern
 * 
 * Prevents cascading failures by stopping calls to failing services.
 */

import java.util.concurrent.atomic.AtomicInteger;
import java.util.concurrent.atomic.AtomicLong;
import java.util.function.Supplier;

public class CircuitBreaker {
    
    public enum State { CLOSED, OPEN, HALF_OPEN }
    
    private final String name;
    private final int failureThreshold;
    private final long openDurationMs;
    
    private volatile State state = State.CLOSED;
    private final AtomicInteger failureCount = new AtomicInteger(0);
    private final AtomicLong lastFailureTime = new AtomicLong(0);
    
    public CircuitBreaker(String name, int failureThreshold, long openDurationMs) {
        this.name = name;
        this.failureThreshold = failureThreshold;
        this.openDurationMs = openDurationMs;
    }
    
    public <T> T call(Supplier<T> action, Supplier<T> fallback) {
        if (!allowRequest()) {
            System.out.println("[" + name + "] Circuit OPEN - using fallback");
            return fallback.get();
        }
        
        try {
            T result = action.get();
            onSuccess();
            return result;
        } catch (Exception e) {
            onFailure();
            System.out.println("[" + name + "] Call failed: " + e.getMessage());
            return fallback.get();
        }
    }
    
    private boolean allowRequest() {
        if (state == State.CLOSED) {
            return true;
        }
        
        if (state == State.OPEN) {
            if (System.currentTimeMillis() - lastFailureTime.get() > openDurationMs) {
                state = State.HALF_OPEN;
                System.out.println("[" + name + "] Circuit HALF_OPEN - testing");
                return true;
            }
            return false;
        }
        
        return true; // HALF_OPEN allows one request
    }
    
    private void onSuccess() {
        if (state == State.HALF_OPEN) {
            state = State.CLOSED;
            failureCount.set(0);
            System.out.println("[" + name + "] Circuit CLOSED - recovered");
        }
    }
    
    private void onFailure() {
        lastFailureTime.set(System.currentTimeMillis());
        int failures = failureCount.incrementAndGet();
        
        if (failures >= failureThreshold) {
            state = State.OPEN;
            System.out.println("[" + name + "] Circuit OPEN - threshold reached");
        }
    }
    
    public State getState() { return state; }
    
    public static void main(String[] args) throws InterruptedException {
        CircuitBreaker cb = new CircuitBreaker("user-service", 3, 2000);
        
        // Simulate failing service
        Supplier<String> failingCall = () -> { throw new RuntimeException("Service down"); };
        Supplier<String> fallback = () -> "Cached user data";
        
        for (int i = 0; i < 5; i++) {
            String result = cb.call(failingCall, fallback);
            System.out.println("Result: " + result + ", State: " + cb.getState());
        }
        
        System.out.println("\nWaiting for circuit to half-open...");
        Thread.sleep(2500);
        
        // Now service recovers
        Supplier<String> workingCall = () -> "Live user data";
        String result = cb.call(workingCall, fallback);
        System.out.println("Result: " + result + ", State: " + cb.getState());
    }
}
