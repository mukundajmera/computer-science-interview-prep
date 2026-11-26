/**
 * V1: Simple Metric Collection
 * 
 * Basic metric collection and storage.
 */

import java.util.*;
import java.util.concurrent.ConcurrentHashMap;

public class SimpleMetrics {
    
    private final Map<String, List<DataPoint>> metrics = new ConcurrentHashMap<>();
    
    public void record(String name, double value) {
        metrics.computeIfAbsent(name, k -> Collections.synchronizedList(new ArrayList<>()))
               .add(new DataPoint(System.currentTimeMillis(), value));
    }
    
    public void increment(String name) {
        record(name, 1.0);
    }
    
    public double getSum(String name) {
        List<DataPoint> points = metrics.get(name);
        if (points == null) return 0;
        return points.stream().mapToDouble(p -> p.value).sum();
    }
    
    public double getAverage(String name) {
        List<DataPoint> points = metrics.get(name);
        if (points == null || points.isEmpty()) return 0;
        return points.stream().mapToDouble(p -> p.value).average().orElse(0);
    }
    
    public void printAll() {
        System.out.println("=== Metrics ===");
        for (String name : metrics.keySet()) {
            System.out.printf("%s: count=%d, sum=%.2f, avg=%.2f%n",
                name, metrics.get(name).size(), getSum(name), getAverage(name));
        }
    }
    
    static class DataPoint {
        final long timestamp;
        final double value;
        
        DataPoint(long timestamp, double value) {
            this.timestamp = timestamp;
            this.value = value;
        }
    }
    
    public static void main(String[] args) {
        SimpleMetrics metrics = new SimpleMetrics();
        
        // Record some metrics
        for (int i = 0; i < 100; i++) {
            metrics.increment("http_requests_total");
            metrics.record("http_request_duration_ms", Math.random() * 100);
        }
        
        metrics.printAll();
    }
}
