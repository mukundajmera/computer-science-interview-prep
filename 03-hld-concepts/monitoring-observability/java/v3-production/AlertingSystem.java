/**
 * V3: Alerting System with Threshold Detection
 * 
 * Monitors metrics and fires alerts when thresholds are breached.
 */

import java.util.*;
import java.util.concurrent.*;
import java.util.function.Consumer;

public class AlertingSystem {
    
    private final TimeSeriesMetrics metrics;
    private final List<AlertRule> rules = new CopyOnWriteArrayList<>();
    private final ScheduledExecutorService scheduler = Executors.newSingleThreadScheduledExecutor();
    private final List<Consumer<Alert>> alertHandlers = new CopyOnWriteArrayList<>();
    
    public AlertingSystem(TimeSeriesMetrics metrics) {
        this.metrics = metrics;
    }
    
    public void addRule(AlertRule rule) {
        rules.add(rule);
    }
    
    public void addAlertHandler(Consumer<Alert> handler) {
        alertHandlers.add(handler);
    }
    
    public void start(long checkIntervalMs) {
        scheduler.scheduleAtFixedRate(this::checkRules, 0, checkIntervalMs, TimeUnit.MILLISECONDS);
    }
    
    public void stop() {
        scheduler.shutdown();
    }
    
    private void checkRules() {
        for (AlertRule rule : rules) {
            TimeSeriesMetrics.MetricStats stats = metrics.getStats(rule.metricName);
            double value = getValueForType(stats, rule.valueType);
            
            boolean triggered = rule.comparator.test(value, rule.threshold);
            
            if (triggered) {
                Alert alert = new Alert(rule.name, rule.severity, 
                    String.format("%s %s: %.2f %s %.2f", 
                        rule.metricName, rule.valueType, value, 
                        rule.comparator.symbol, rule.threshold));
                fireAlert(alert);
            }
        }
    }
    
    private double getValueForType(TimeSeriesMetrics.MetricStats stats, String type) {
        switch (type) {
            case "avg": return stats.avg;
            case "max": return stats.max;
            case "p99": return stats.p99;
            case "count": return stats.count;
            default: return stats.avg;
        }
    }
    
    private void fireAlert(Alert alert) {
        for (Consumer<Alert> handler : alertHandlers) {
            handler.accept(alert);
        }
    }
    
    public static class AlertRule {
        final String name;
        final String metricName;
        final String valueType;
        final Comparator comparator;
        final double threshold;
        final Severity severity;
        
        public AlertRule(String name, String metricName, String valueType,
                        Comparator comparator, double threshold, Severity severity) {
            this.name = name;
            this.metricName = metricName;
            this.valueType = valueType;
            this.comparator = comparator;
            this.threshold = threshold;
            this.severity = severity;
        }
    }
    
    public enum Comparator {
        GREATER_THAN(">", (a, b) -> a > b),
        LESS_THAN("<", (a, b) -> a < b);
        
        final String symbol;
        private final java.util.function.BiPredicate<Double, Double> predicate;
        
        Comparator(String symbol, java.util.function.BiPredicate<Double, Double> predicate) {
            this.symbol = symbol;
            this.predicate = predicate;
        }
        
        boolean test(double a, double b) { return predicate.test(a, b); }
    }
    
    public enum Severity { INFO, WARNING, CRITICAL }
    
    public static class Alert {
        public final String ruleName;
        public final Severity severity;
        public final String message;
        public final long timestamp = System.currentTimeMillis();
        
        Alert(String ruleName, Severity severity, String message) {
            this.ruleName = ruleName;
            this.severity = severity;
            this.message = message;
        }
    }
    
    // Uses TimeSeriesMetrics from v2
    static class TimeSeriesMetrics {
        private final Map<String, List<Double>> metrics = new ConcurrentHashMap<>();
        
        void record(String name, double value) {
            metrics.computeIfAbsent(name, k -> Collections.synchronizedList(new ArrayList<>()))
                   .add(value);
        }
        
        MetricStats getStats(String name) {
            List<Double> values = metrics.get(name);
            if (values == null || values.isEmpty()) return new MetricStats(0, 0, 0, 0, 0);
            
            double[] arr = values.stream().mapToDouble(d -> d).sorted().toArray();
            return new MetricStats(arr.length, arr[0], arr[arr.length-1],
                Arrays.stream(arr).average().orElse(0), arr[(int)(arr.length * 0.99)]);
        }
        
        static class MetricStats {
            final int count;
            final double min, max, avg, p99;
            MetricStats(int count, double min, double max, double avg, double p99) {
                this.count = count; this.min = min; this.max = max; this.avg = avg; this.p99 = p99;
            }
        }
    }
    
    public static void main(String[] args) throws InterruptedException {
        TimeSeriesMetrics metrics = new TimeSeriesMetrics();
        AlertingSystem alerting = new AlertingSystem(metrics);
        
        // Add alert rules
        alerting.addRule(new AlertRule("HighLatency", "latency", "p99",
            Comparator.GREATER_THAN, 200.0, Severity.WARNING));
        alerting.addRule(new AlertRule("HighErrorRate", "errors", "count",
            Comparator.GREATER_THAN, 10, Severity.CRITICAL));
        
        // Add alert handler
        alerting.addAlertHandler(alert -> 
            System.out.printf("[%s] %s: %s%n", alert.severity, alert.ruleName, alert.message));
        
        // Record some metrics
        Random rand = new Random();
        for (int i = 0; i < 100; i++) {
            metrics.record("latency", rand.nextGaussian() * 50 + 150); // Some will exceed 200
            if (rand.nextDouble() < 0.15) metrics.record("errors", 1);
        }
        
        alerting.start(1000);
        Thread.sleep(3000);
        alerting.stop();
    }
}
