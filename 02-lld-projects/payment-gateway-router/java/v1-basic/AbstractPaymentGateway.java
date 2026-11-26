import java.util.LinkedList;

public abstract class AbstractPaymentGateway implements PaymentGateway {
    private final String name;
    private final LinkedList<Boolean> window = new LinkedList<>();
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
    public synchronized void recordMetrics(boolean success) {
        if (window.size() >= windowSize) {
            window.removeFirst();
        }
        window.addLast(success);
        
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
    
    public CircuitBreaker getCircuitBreaker() {
        return circuitBreaker;
    }
}
