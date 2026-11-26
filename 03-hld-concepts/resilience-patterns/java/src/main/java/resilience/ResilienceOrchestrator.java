package resilience;

import java.time.Clock;
import java.time.Instant;
import java.util.LinkedList;
import java.util.Queue;
import java.util.Random;
import java.util.concurrent.*;
import java.util.function.Supplier;

public class ResilienceOrchestrator {
    private final CircuitBreaker circuitBreaker;
    private final Bulkhead bulkhead;
    private final RetryPolicy retryPolicy;

    public ResilienceOrchestrator(int cbThreshold, long cbTimeoutMs, int bulkheadCapacity, int maxRetries, long baseDelayMs) {
        this.circuitBreaker = new CircuitBreaker(cbThreshold, cbTimeoutMs);
        this.bulkhead = new Bulkhead(bulkheadCapacity);
        this.retryPolicy = new RetryPolicy(maxRetries, baseDelayMs);
    }

    public <T> T execute(Supplier<T> action, Supplier<T> fallback) {
        try {
            return retryPolicy.executeWithRetry(() -> {
                try {
                    return bulkhead.execute(() -> circuitBreaker.execute(action));
                } catch (Exception e) {
                    throw new RuntimeException(e);
                }
            });
        } catch (Exception e) {
            return fallback.get();
        }
    }

    static class CircuitBreaker {
        enum State { CLOSED, OPEN, HALF_OPEN }
        
        private State state = State.CLOSED;
        private final int threshold;
        private final long timeoutMs;
        private int failureCount = 0;
        private long openTime = 0;
        private int probeCount = 0;
        private final int PROBE_LIMIT = 3;
        private final Clock clock;

        public CircuitBreaker(int threshold, long timeoutMs) {
            this(threshold, timeoutMs, Clock.systemUTC());
        }

        CircuitBreaker(int threshold, long timeoutMs, Clock clock) {
            this.threshold = threshold;
            this.timeoutMs = timeoutMs;
            this.clock = clock;
        }

        public <T> T execute(Supplier<T> action) {
            synchronized (this) {
                if (state == State.OPEN) {
                    if (clock.millis() - openTime > timeoutMs) {
                        state = State.HALF_OPEN;
                        probeCount = 0;
                    } else {
                        throw new RuntimeException("Circuit Breaker is OPEN");
                    }
                }

                if (state == State.HALF_OPEN) {
                    if (probeCount >= PROBE_LIMIT) {
                        throw new RuntimeException("Probe limit reached, waiting for next cycle");
                    }
                    probeCount++;
                }
            }

            try {
                T result = action.get();
                onSuccess();
                return result;
            } catch (Exception e) {
                onFailure();
                throw e;
            }
        }

        private synchronized void onSuccess() {
            if (state == State.HALF_OPEN) {
                if (probeCount == PROBE_LIMIT) {
                    state = State.CLOSED;
                    failureCount = 0;
                }
            } else if (state == State.CLOSED) {
                failureCount = 0;
            }
        }

        private synchronized void onFailure() {
            if (state == State.HALF_OPEN) {
                state = State.OPEN;
                openTime = clock.millis();
            } else if (state == State.CLOSED) {
                failureCount++;
                if (failureCount >= threshold) {
                    state = State.OPEN;
                    openTime = clock.millis();
                }
            }
        }
        
        public State getState() { return state; }
    }

    static class Bulkhead {
        private final Semaphore semaphore;

        public Bulkhead(int capacity) {
            this.semaphore = new Semaphore(capacity);
        }

        public <T> T execute(Supplier<T> action) {
            if (semaphore.tryAcquire()) {
                try {
                    return action.get();
                } finally {
                    semaphore.release();
                }
            } else {
                throw new RuntimeException("Bulkhead capacity reached");
            }
        }
    }

    static class RetryPolicy {
        private final int maxRetries;
        private final long baseDelayMs;
        private final Random random = new Random();

        public RetryPolicy(int maxRetries, long baseDelayMs) {
            this.maxRetries = maxRetries;
            this.baseDelayMs = baseDelayMs;
        }

        public <T> T executeWithRetry(Supplier<T> action) {
            int attempt = 0;
            while (true) {
                try {
                    return action.get();
                } catch (Exception e) {
                    if (attempt >= maxRetries) {
                        throw e;
                    }
                    long delay = calculateFullJitterDelay(attempt);
                    try {
                        Thread.sleep(delay);
                    } catch (InterruptedException ie) {
                        Thread.currentThread().interrupt();
                        throw new RuntimeException(ie);
                    }
                    attempt++;
                }
            }
        }

        private long calculateFullJitterDelay(int attempt) {
            long maxDelay = baseDelayMs * (1L << attempt);
            return (long) (random.nextDouble() * maxDelay);
        }
    }
}
