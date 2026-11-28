package v2_extended;

import java.util.ArrayDeque;
import java.util.Deque;

/**
 * Half-open circuit breaker driven by a rolling failure-rate window.
 *
 * CLOSED: requests flow; outcomes are recorded in a bounded window and the
 * breaker opens once the failure rate over the window reaches the threshold
 * (with at least minSamples observations, so a single early failure cannot
 * trip it). OPEN: requests fast-fail until resetTimeoutMillis have passed,
 * then one half-open probe is admitted. Probe success closes the breaker and
 * clears the window; probe failure reopens it immediately.
 */
public class CircuitBreaker {
    public enum State { CLOSED, OPEN, HALF_OPEN }

    private final double failureRateThreshold;
    private final int windowSize;
    private final int minSamples;
    private final long resetTimeoutMillis;
    private final TimeSource clock;

    private final Deque<Boolean> outcomes = new ArrayDeque<>(); // TRUE = success
    private State state = State.CLOSED;
    private long openedAt = 0L;
    private boolean probeInFlight = false;

    public CircuitBreaker(double failureRateThreshold, int windowSize,
                          int minSamples, long resetTimeoutMillis, TimeSource clock) {
        if (!(failureRateThreshold > 0.0) || failureRateThreshold > 1.0) {
            throw new IllegalArgumentException("failureRateThreshold must be in (0, 1]");
        }
        if (windowSize < 1) {
            throw new IllegalArgumentException("windowSize must be >= 1");
        }
        if (minSamples < 1 || minSamples > windowSize) {
            throw new IllegalArgumentException("minSamples must be in [1, windowSize]");
        }
        if (resetTimeoutMillis < 0) {
            throw new IllegalArgumentException("resetTimeoutMillis must be >= 0");
        }
        this.failureRateThreshold = failureRateThreshold;
        this.windowSize = windowSize;
        this.minSamples = minSamples;
        this.resetTimeoutMillis = resetTimeoutMillis;
        this.clock = clock;
    }

    public CircuitBreaker() {
        this(0.5, 10, 4, 30000L, System::currentTimeMillis);
    }

    public synchronized State getState() {
        return state;
    }

    public synchronized boolean allowRequest() {
        if (state == State.OPEN) {
            if (clock.nowMillis() - openedAt < resetTimeoutMillis) {
                return false;
            }
            state = State.HALF_OPEN;
            probeInFlight = false;
        }
        if (state == State.HALF_OPEN) {
            if (probeInFlight) {
                return false;
            }
            probeInFlight = true;
            return true;
        }
        return true;
    }

    public synchronized void recordSuccess() {
        if (state == State.HALF_OPEN) {
            state = State.CLOSED;
            outcomes.clear();
            probeInFlight = false;
            return;
        }
        push(true);
    }

    public synchronized void recordFailure() {
        if (state == State.HALF_OPEN) {
            state = State.OPEN;
            openedAt = clock.nowMillis();
            probeInFlight = false;
            return;
        }
        push(false);
        maybeOpen();
    }

    private void push(boolean success) {
        if (outcomes.size() == windowSize) {
            outcomes.pollFirst();
        }
        outcomes.addLast(success);
    }

    private void maybeOpen() {
        if (outcomes.size() < minSamples) {
            return;
        }
        int failures = 0;
        for (Boolean ok : outcomes) {
            if (!ok) {
                failures++;
            }
        }
        if ((double) failures / outcomes.size() >= failureRateThreshold) {
            state = State.OPEN;
            openedAt = clock.nowMillis();
        }
    }

    // Test-simulation helpers kept from v1 for API parity.
    public synchronized void tripOpen() {
        state = State.OPEN;
        openedAt = clock.nowMillis();
        probeInFlight = false;
    }

    public synchronized void reset() {
        state = State.CLOSED;
        outcomes.clear();
        openedAt = 0L;
        probeInFlight = false;
    }
}
