package v3_blocks;
import java.util.*;

public class TsdbEngine {
    public static class Point {
        public long ts;
        public double value;
        public Point(long ts, double value) { this.ts = ts; this.value = value; }
    }
    
    public static class SeriesBlock {
        public List<Point> points = new ArrayList<>();
        public void add(long ts, double value) {
            if (!points.isEmpty() && ts < points.get(points.size()-1).ts) {
                throw new IllegalArgumentException("Out of order");
            }
            points.add(new Point(ts, value));
        }
        public List<Point> rangeQuery(long start, long end) {
            List<Point> res = new ArrayList<>();
            for (Point p : points) {
                if (p.ts >= start && p.ts <= end) res.add(p);
            }
            return res;
        }
    }
    
    private Map<String, SeriesBlock> series = new HashMap<>();
    private int maxSeries;
    
    public TsdbEngine(int maxSeries) {
        this.maxSeries = maxSeries;
    }
    
    public void insert(String metric, long ts, double value) {
        if (!series.containsKey(metric) && series.size() >= maxSeries) {
            throw new IllegalStateException("Cardinality limit");
        }
        series.putIfAbsent(metric, new SeriesBlock());
        series.get(metric).add(ts, value);
    }
    
    public List<Point> rangeQuery(String metric, long start, long end) {
        if (!series.containsKey(metric)) return Collections.emptyList();
        return series.get(metric).rangeQuery(start, end);
    }
    
    public List<Point> downsample(String metric, long bucketSize) {
        if (!series.containsKey(metric)) return Collections.emptyList();
        
        Map<Long, List<Double>> buckets = new TreeMap<>();
        for (Point p : series.get(metric).points) {
            long bTs = (p.ts / bucketSize) * bucketSize;
            buckets.putIfAbsent(bTs, new ArrayList<>());
            buckets.get(bTs).add(p.value);
        }
        
        List<Point> res = new ArrayList<>();
        for (Map.Entry<Long, List<Double>> e : buckets.entrySet()) {
            double sum = 0;
            for (Double v : e.getValue()) sum += v;
            res.add(new Point(e.getKey(), sum / e.getValue().size()));
        }
        return res;
    }
    
    public void applyRetention(long cutoff) {
        List<String> toRemove = new ArrayList<>();
        for (Map.Entry<String, SeriesBlock> e : series.entrySet()) {
            List<Point> kept = new ArrayList<>();
            for (Point p : e.getValue().points) {
                if (p.ts >= cutoff) kept.add(p);
            }
            e.getValue().points = kept;
            if (kept.isEmpty()) toRemove.add(e.getKey());
        }
        for (String k : toRemove) series.remove(k);
    }
}
