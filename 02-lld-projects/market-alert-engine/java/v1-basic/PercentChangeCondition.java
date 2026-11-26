import java.util.LinkedList;
import java.util.Queue;

public class PercentChangeCondition implements Condition {
    private final double percentThreshold;
    private final long timeWindowMs;
    // To keep track of history per symbol, we would need engine level state
    // But for this Condition to be stateful per symbol, it needs to track it here.
    private final java.util.Map<String, Queue<Tick>> tickHistory = new java.util.concurrent.ConcurrentHashMap<>();

    public PercentChangeCondition(double percentThreshold, long timeWindowMs) {
        this.percentThreshold = percentThreshold;
        this.timeWindowMs = timeWindowMs;
    }

    @Override
    public boolean evaluate(Tick tick) {
        Queue<Tick> window = tickHistory.computeIfAbsent(tick.getSymbol(), k -> new LinkedList<>());
        
        synchronized (window) {
            window.offer(tick);
            
            // Evict old ticks outside the time window
            long cutoffTime = tick.getTimestamp() - timeWindowMs;
            while (!window.isEmpty() && window.peek().getTimestamp() < cutoffTime) {
                window.poll();
            }

            // Find min and max in the window
            if (window.size() < 2) {
                return false;
            }

            double minPrice = Double.MAX_VALUE;
            double maxPrice = Double.MIN_VALUE;

            for (Tick t : window) {
                if (t.getPrice() < minPrice) minPrice = t.getPrice();
                if (t.getPrice() > maxPrice) maxPrice = t.getPrice();
            }
            
            // Assuming threshold is a positive percentage like 5.0 for 5%
            // and we check if the max change in the window exceeds it
            double currentChange = ((maxPrice - minPrice) / minPrice) * 100.0;

            return currentChange > percentThreshold;
        }
    }
}
