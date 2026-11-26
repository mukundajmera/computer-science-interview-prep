import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Collections;
import java.util.Comparator;
import java.util.stream.Collectors;

public class TimeSeriesDownsampler {

    public enum AggregationType {
        AVG, MIN, MAX, SUM
    }

    public static class DataPoint {
        private String metricName;
        private long timestamp;
        private double value;
        private Map<String, String> tags;

        public DataPoint(String metricName, long timestamp, double value, Map<String, String> tags) {
            this.metricName = metricName;
            this.timestamp = timestamp;
            this.value = value;
            this.tags = tags != null ? tags : new HashMap<>();
        }

        public String getMetricName() {
            return metricName;
        }

        public long getTimestamp() {
            return timestamp;
        }

        public double getValue() {
            return value;
        }

        public Map<String, String> getTags() {
            return tags;
        }

        @Override
        public String toString() {
            return "DataPoint{" +
                    "metricName='" + metricName + '\'' +
                    ", timestamp=" + timestamp +
                    ", value=" + value +
                    ", tags=" + tags +
                    '}';
        }
    }

    private Map<String, List<DataPoint>> data;

    public TimeSeriesDownsampler() {
        this.data = new HashMap<>();
    }

    public void insert(DataPoint point) {
        data.putIfAbsent(point.getMetricName(), new ArrayList<>());
        List<DataPoint> points = data.get(point.getMetricName());
        points.add(point);
        // Keep points sorted by timestamp
        points.sort(Comparator.comparingLong(DataPoint::getTimestamp));
    }

    public List<DataPoint> rangeQuery(String metricName, long startTime, long endTime, Map<String, String> tags) {
        if (!data.containsKey(metricName)) {
            return Collections.emptyList();
        }

        return data.get(metricName).stream()
            .filter(p -> p.getTimestamp() >= startTime && p.getTimestamp() <= endTime)
            .filter(p -> {
                if (tags == null || tags.isEmpty()) {
                    return true;
                }
                for (Map.Entry<String, String> entry : tags.entrySet()) {
                    if (!entry.getValue().equals(p.getTags().get(entry.getKey()))) {
                        return false;
                    }
                }
                return true;
            })
            .collect(Collectors.toList());
    }

    public List<DataPoint> downsample(String metricName, long bucketSizeSeconds, AggregationType aggType) {
        if (!data.containsKey(metricName) || data.get(metricName).isEmpty()) {
            return Collections.emptyList();
        }

        Map<Long, List<Double>> buckets = new HashMap<>();
        for (DataPoint p : data.get(metricName)) {
            long bucketTs = (p.getTimestamp() / bucketSizeSeconds) * bucketSizeSeconds;
            buckets.putIfAbsent(bucketTs, new ArrayList<>());
            buckets.get(bucketTs).add(p.getValue());
        }

        List<DataPoint> downsampledPoints = new ArrayList<>();
        List<Long> sortedBucketTimes = new ArrayList<>(buckets.keySet());
        Collections.sort(sortedBucketTimes);

        for (long bucketTs : sortedBucketTimes) {
            List<Double> values = buckets.get(bucketTs);
            double val = 0.0;
            switch (aggType) {
                case AVG:
                    val = values.stream().mapToDouble(Double::doubleValue).average().orElse(0.0);
                    break;
                case MIN:
                    val = values.stream().mapToDouble(Double::doubleValue).min().orElse(0.0);
                    break;
                case MAX:
                    val = values.stream().mapToDouble(Double::doubleValue).max().orElse(0.0);
                    break;
                case SUM:
                    val = values.stream().mapToDouble(Double::doubleValue).sum();
                    break;
            }
            // Tags omitted in downsampled data points
            downsampledPoints.add(new DataPoint(metricName, bucketTs, val, Collections.emptyMap()));
        }

        return downsampledPoints;
    }

    public void applyRetention(long currentTime, long retentionPeriodSeconds) {
        long cutoffTime = currentTime - retentionPeriodSeconds;
        List<String> metricsToRemove = new ArrayList<>();

        for (Map.Entry<String, List<DataPoint>> entry : data.entrySet()) {
            List<DataPoint> retainedPoints = entry.getValue().stream()
                .filter(p -> p.getTimestamp() >= cutoffTime)
                .collect(Collectors.toList());

            if (retainedPoints.isEmpty()) {
                metricsToRemove.add(entry.getKey());
            } else {
                data.put(entry.getKey(), retainedPoints);
            }
        }

        for (String metric : metricsToRemove) {
            data.remove(metric);
        }
    }
}
