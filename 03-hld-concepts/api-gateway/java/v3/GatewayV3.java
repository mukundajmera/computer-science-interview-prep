import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.concurrent.TimeoutException;

class CircuitBreaker {
    private final int failureThreshold;
    private final long resetTimeoutMs;
    
    private String state = "CLOSED";
    private int failures = 0;
    private long lastFailureTime = 0;

    public CircuitBreaker(int failureThreshold, long resetTimeoutMs) {
        this.failureThreshold = failureThreshold;
        this.resetTimeoutMs = resetTimeoutMs;
    }

    public synchronized boolean canRequest() {
        if ("CLOSED".equals(state)) return true;
        if ("OPEN".equals(state)) {
            if (System.currentTimeMillis() - lastFailureTime > resetTimeoutMs) {
                state = "HALF_OPEN";
                return true;
            }
            return false;
        }
        if ("HALF_OPEN".equals(state)) return true;
        return false;
    }

    public synchronized void recordSuccess() {
        state = "CLOSED";
        failures = 0;
    }

    public synchronized void recordFailure() {
        failures++;
        if ("HALF_OPEN".equals(state) || failures >= failureThreshold) {
            state = "OPEN";
            lastFailureTime = System.currentTimeMillis();
        }
    }
}

abstract class BackendService {
    protected final String name;
    
    public BackendService(String name) {
        this.name = name;
    }
    
    public String getName() {
        return name;
    }

    public abstract String call(long timeoutMs) throws TimeoutException, Exception;
}

public class GatewayV3 {
    private final double retryBudget;
    private final AtomicInteger totalRequests = new AtomicInteger(0);
    private final AtomicInteger totalRetries = new AtomicInteger(0);
    private final Map<String, CircuitBreaker> circuitBreakers = new ConcurrentHashMap<>();

    public GatewayV3(double retryBudget) {
        this.retryBudget = retryBudget;
    }

    private CircuitBreaker getCircuitBreaker(String serviceName) {
        return circuitBreakers.computeIfAbsent(serviceName, k -> new CircuitBreaker(3, 2000));
    }

    private boolean canRetry() {
        int reqs = totalRequests.get();
        if (reqs == 0) return true;
        return ((double) totalRetries.get() / reqs) < retryBudget;
    }

    public String handle(BackendService backend, long timeoutMs) {
        totalRequests.incrementAndGet();
        CircuitBreaker cb = getCircuitBreaker(backend.getName());

        if (!cb.canRequest()) {
            return "503 Service Unavailable (Circuit Breaker OPEN)";
        }

        try {
            String res = backend.call(timeoutMs);
            cb.recordSuccess();
            return res;
        } catch (TimeoutException e) {
            cb.recordFailure();
            if (canRetry()) {
                totalRetries.incrementAndGet();
                try {
                    String res = backend.call(timeoutMs);
                    cb.recordSuccess();
                    return res;
                } catch (Exception ex) {
                    cb.recordFailure();
                    return "504 Gateway Timeout";
                }
            } else {
                return "504 Gateway Timeout";
            }
        } catch (Exception e) {
            cb.recordFailure();
            return "500 Internal Server Error";
        }
    }

    public Map<String, String> aggregate(List<BackendService> backends, long timeoutMs) {
        totalRequests.incrementAndGet();
        Map<String, String> results = new HashMap<>();
        
        // Simulating concurrent aggregation synchronously for parity
        for (BackendService backend : backends) {
            CircuitBreaker cb = getCircuitBreaker(backend.getName());
            if (!cb.canRequest()) {
                results.put(backend.getName(), "503 Service Unavailable");
                continue;
            }

            try {
                String res = backend.call(timeoutMs);
                cb.recordSuccess();
                results.put(backend.getName(), res);
            } catch (TimeoutException e) {
                cb.recordFailure();
                results.put(backend.getName(), "504 Gateway Timeout");
            } catch (Exception e) {
                cb.recordFailure();
                results.put(backend.getName(), "500 Internal Server Error");
            }
        }
        return results;
    }
}
