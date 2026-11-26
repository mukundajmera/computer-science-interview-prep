

import java.util.*;
import java.util.concurrent.*;
import java.util.stream.*;

public abstract class AbstractPaymentGateway implements PaymentGateway {
    private final String name;
    private final LinkedList<Boolean> window = new LinkedList<>();
    private final LinkedList<Double> latencyWindow = new LinkedList<>();
    private final int windowSize = 10;
    protected CircuitBreaker circuitBreaker;

    public AbstractPaymentGateway(String name) {
        this.name = name;
        this.circuitBreaker = new CircuitBreaker(3, 5000); // 3 failures, 5 seconds reset
    }

    @Override
    public String getName() {
        return name;
    }

    @Override
    public synchronized void recordMetrics(boolean success, double latency) {
        if (window.size() >= windowSize) {
            window.removeFirst();
            latencyWindow.removeFirst();
        }
        window.addLast(success);
        latencyWindow.addLast(latency);
        
        if (success) {
            circuitBreaker.recordSuccess();
        } else {
            circuitBreaker.recordFailure();
        }
    }

    @Override
    public synchronized double getSuccessRate() {
        if (window.isEmpty()) return 1.0; // Default to 100%
        long successes = window.stream().filter(b -> b).count();
        return (double) successes / window.size();
    }

    @Override
    public synchronized double getAverageLatency() {
        if (latencyWindow.isEmpty()) return 0.0;
        return latencyWindow.stream().mapToDouble(Double::doubleValue).average().orElse(0.0);
    }
    
    public CircuitBreaker getCircuitBreaker() {
        return circuitBreaker;
    }
}
