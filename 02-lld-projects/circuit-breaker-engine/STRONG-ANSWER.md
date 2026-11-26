# Strong Answer: Circuit Breaker Engine

A strong answer demonstrates a deep understanding of concurrency, clean architecture, and the State pattern. Below is a conceptual overview of what a highly rated implementation looks like in Java, focusing on the critical concurrency aspects.

## The Configuration

A simple immutable object holds the settings.

```java
public class CircuitBreakerConfig {
    private final int failureThreshold;
    private final long resetTimeoutMs;

    public CircuitBreakerConfig(int failureThreshold, long resetTimeoutMs) {
        this.failureThreshold = failureThreshold;
        this.resetTimeoutMs = resetTimeoutMs;
    }
    // Getters...
}
```

## The State Interface

The interface clearly defines the actions that states must handle without leaking implementation details.

```java
public interface CircuitBreakerState {
    boolean acquirePermission();
    void onSuccess(CircuitBreaker cb);
    void onError(Throwable t, CircuitBreaker cb);
    String getStateName();
}
```

## The Engine Context

The Context uses `AtomicReference` for lock-free state transitions.

```java
import java.util.concurrent.atomic.AtomicReference;
import java.util.function.Supplier;

public class CircuitBreaker {
    private final CircuitBreakerConfig config;
    private final AtomicReference<CircuitBreakerState> state;

    public CircuitBreaker(CircuitBreakerConfig config) {
        this.config = config;
        this.state = new AtomicReference<>(new ClosedState(config));
    }

    // Execute wrapped in Proxy pattern
    public <T> T execute(Supplier<T> action) {
        if (!state.get().acquirePermission()) {
            throw new CircuitBreakerOpenException("Circuit breaker is OPEN");
        }
        
        try {
            T result = action.get();
            state.get().onSuccess(this);
            return result;
        } catch (Exception e) {
            state.get().onError(e, this);
            throw e;
        }
    }

    // Thread-safe state transition
    public void transitionTo(CircuitBreakerState expectedCurrentState, CircuitBreakerState newState) {
        // Only transition if the state hasn't been changed by another thread
        state.compareAndSet(expectedCurrentState, newState);
    }
}
```

## The States

### Closed State
Uses `AtomicInteger` to prevent lost updates on failure counts.

```java
import java.util.concurrent.atomic.AtomicInteger;

public class ClosedState implements CircuitBreakerState {
    private final AtomicInteger failures = new AtomicInteger(0);
    private final CircuitBreakerConfig config;

    public ClosedState(CircuitBreakerConfig config) {
        this.config = config;
    }

    @Override
    public boolean acquirePermission() {
        return true;
    }

    @Override
    public void onSuccess(CircuitBreaker cb) {
        failures.set(0); // Reset on success
    }

    @Override
    public void onError(Throwable t, CircuitBreaker cb) {
        int currentFailures = failures.incrementAndGet();
        if (currentFailures >= config.getFailureThreshold()) {
            cb.transitionTo(this, new OpenState(config));
        }
    }
    
    @Override
    public String getStateName() { return "CLOSED"; }
}
```

### Open State
Crucially, this is non-blocking. It checks the time instead of sleeping.

```java
public class OpenState implements CircuitBreakerState {
    private final long openTime;
    private final CircuitBreakerConfig config;

    public OpenState(CircuitBreakerConfig config) {
        this.config = config;
        this.openTime = System.currentTimeMillis();
    }

    @Override
    public boolean acquirePermission() {
        if (System.currentTimeMillis() - openTime >= config.getResetTimeoutMs()) {
            // Time expired, try to transition to Half-Open. 
            // We return false here because we want the *next* state to handle permission.
            // In a highly optimized version, you might transition and then immediately evaluate the new state.
            return false; // Will be handled by transition logic in a more complete implementation
        }
        return false;
    }
    // ... onSuccess, onError do nothing.
}
```

*Note on OpenState `acquirePermission`: A robust implementation handles the transition check atomically. If the timeout has expired, it attempts a `compareAndSet` to Half-Open. If successful, that single thread gets permission. If it fails, another thread won the race, and this thread should re-evaluate against the new state.*

### Half-Open State
Handles the tricky "thundering herd" problem by using an atomic flag to ensure only one test request goes through.

```java
import java.util.concurrent.atomic.AtomicBoolean;

public class HalfOpenState implements CircuitBreakerState {
    private final CircuitBreakerConfig config;
    private final AtomicBoolean testRequestAllowed = new AtomicBoolean(true);

    public HalfOpenState(CircuitBreakerConfig config) {
        this.config = config;
    }

    @Override
    public boolean acquirePermission() {
        // compareAndSet ensures only the FIRST thread to hit this gets true.
        // All subsequent threads get false and are rejected.
        return testRequestAllowed.compareAndSet(true, false);
    }

    @Override
    public void onSuccess(CircuitBreaker cb) {
        cb.transitionTo(this, new ClosedState(config));
    }

    @Override
    public void onError(Throwable t, CircuitBreaker cb) {
        cb.transitionTo(this, new OpenState(config));
    }
}
```

## Adding Resilience Strategies (Fallback Strategy)

A strong candidate will separate fallback logic from the core breaker:

```java
public class ResilienceWrapper<T> {
    private final CircuitBreaker circuitBreaker;
    private final Supplier<T> fallback;

    public ResilienceWrapper(CircuitBreaker circuitBreaker, Supplier<T> fallback) {
        this.circuitBreaker = circuitBreaker;
        this.fallback = fallback;
    }

    public T execute(Supplier<T> action) {
        try {
            return circuitBreaker.execute(action);
        } catch (CircuitBreakerOpenException e) {
            // Circuit is open, use fallback immediately
            return fallback.get();
        } catch (Exception e) {
            // Underlying service failed, use fallback
            return fallback.get();
        }
    }
}
```

## Why this is a Strong Answer
1.  **Thread Safety without Bottlenecks:** Uses lock-free constructs (`AtomicInteger`, `AtomicReference`, `AtomicBoolean`) instead of heavy `synchronized` blocks.
2.  **Solves the Half-Open Race:** The `compareAndSet` in Half-Open guarantees exactly one request is used to test the waters, regardless of how many threads are waiting.
3.  **Clean Separation of Concerns:** State logic is decoupled from execution logic, and fallback logic is injected via strategy.