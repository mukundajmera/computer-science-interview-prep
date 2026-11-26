/**
 * V2: Time-Series with Windowing
 * 
 * Aggregates metrics over time windows.
 */

import java.util.*;
import java.util.concurrent.*;

public class TimeSeriesMetrics {
    
    private final Map<String, WindowedMetric> metrics = new ConcurrentHashMap<>();
    private final long windowSizeMs;
    
    public TimeSeriesMetrics(long windowSizeMs) {
        this.windowSizeMs = windowSizeMs;
    }
    
    public void record(String name, double value) {
        metrics.computeIfAbsent(name, k -> new WindowedMetric(windowSizeMs))
               .record(value);
    }
    
    public MetricStats getStats(String name) {
        WindowedMetric metric = metrics.get(name);
        return metric != null ? metric.getStats() : new MetricStats(0, 0, 0, 0, 0);
    }
    
    public void printAll() {
        System.out.println("=== Time Series Metrics (last window) ===");
        for (Map.Entry<String, WindowedMetric> entry : metrics.entrySet()) {
            MetricStats stats = entry.getValue().getStats();
            System.out.printf("%s: count=%d, min=%.2f, max=%.2f, avg=%.2f, p99=%.2f%n",
                entry.getKey(), stats.count, stats.min, stats.max, stats.avg, stats.p99);
        }
    }
    
    static class WindowedMetric {
        private final long windowSizeMs;
        private final List<Sample> samples = Collections.synchronizedList(new ArrayList<>());
        
        WindowedMetric(long windowSizeMs) {
            this.windowSizeMs = windowSizeMs;
        }
        
        void record(double value) {
            samples.add(new Sample(System.currentTimeMillis(), value));
            cleanup();
        }
        
        private void cleanup() {
            long cutoff = System.currentTimeMillis() - windowSizeMs;
            samples.removeIf(s -> s.timestamp < cutoff);
        }
        
        MetricStats getStats() {
            cleanup();
            if (samples.isEmpty()) return new MetricStats(0, 0, 0, 0, 0);
            
            double[] values = samples.stream().mapToDouble(s -> s.value).sorted().toArray();
            double min = values[0];
            double max = values[values.length - 1];
            double avg = Arrays.stream(values).average().orElse(0);
            double p99 = values[(int)(values.length * 0.99)];
            
            return new MetricStats(values.length, min, max, avg, p99);
        }
    }
    
    static class Sample {
        final long timestamp;
        final double value;
        Sample(long timestamp, double value) {
            this.timestamp = timestamp;
            this.value = value;
        }
    }
    
    public static class MetricStats {
        public final int count;
        public final double min, max, avg, p99;
        
        MetricStats(int count, double min, double max, double avg, double p99) {
            this.count = count;
            this.min = min;
            this.max = max;
            this.avg = avg;
            this.p99 = p99;
        }
    }
    
    public static void main(String[] args) throws InterruptedException {
        TimeSeriesMetrics metrics = new TimeSeriesMetrics(5000); // 5 second window
        
        Random rand = new Random();
        for (int i = 0; i < 1000; i++) {
            metrics.record("request_latency_ms", rand.nextGaussian() * 20 + 100);
            metrics.record("requests", 1);
        }
        
        metrics.printAll();
    }
}
