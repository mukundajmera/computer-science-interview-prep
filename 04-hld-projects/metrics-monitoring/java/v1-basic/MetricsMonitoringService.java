package v1;

import java.util.*;
import java.util.concurrent.ConcurrentHashMap;
import java.util.stream.Collectors;

public class MetricsMonitoringService {

    public enum MetricType {
        COUNTER, GAUGE, HISTOGRAM
    }

    public static class MetricPoint {
        private final String name;
        private final MetricType type;
        private final Map<String, String> tags;
        private final long timestampMs;
        private final double value;

        public MetricPoint(String name, MetricType type, Map<String, String> tags, long timestampMs, double value) {
            this.name = name;
            this.type = type;
            this.tags = tags != null ? new HashMap<>(tags) : new HashMap<>();
            this.timestampMs = timestampMs;
            this.value = value;
        }

        public String getName() { return name; }
        public MetricType getType() { return type; }
        public Map<String, String> getTags() { return tags; }
        public long getTimestampMs() { return timestampMs; }
        public double getValue() { return value; }
    }

    public static class AlertRule {
        private final String ruleId;
        private final String metricName;
        private final double threshold;
        private final boolean greaterThan;

        public AlertRule(String ruleId, String metricName, double threshold, boolean greaterThan) {
            this.ruleId = ruleId;
            this.metricName = metricName;
            this.threshold = threshold;
            this.greaterThan = greaterThan;
        }

        public String getRuleId() { return ruleId; }
        public String getMetricName() { return metricName; }
        public double getThreshold() { return threshold; }
        public boolean isGreaterThan() { return greaterThan; }
    }

    public enum AlertStatus {
        FIRING, RESOLVED
    }

    public static class AlertEvent {
        private final String ruleId;
        private final AlertStatus status;
        private final long timestampMs;

        public AlertEvent(String ruleId, AlertStatus status, long timestampMs) {
            this.ruleId = ruleId;
            this.status = status;
            this.timestampMs = timestampMs;
        }

        public String getRuleId() { return ruleId; }
        public AlertStatus getStatus() { return status; }
        public long getTimestampMs() { return timestampMs; }
    }

    private final List<MetricPoint> dataStore = new ArrayList<>();
    private final Map<String, AlertRule> alertRules = new ConcurrentHashMap<>();
    private final Map<String, AlertStatus> currentAlertStates = new ConcurrentHashMap<>();
    private final List<AlertEvent> alertHistory = new ArrayList<>();

    public synchronized void ingest(MetricPoint point) {
        dataStore.add(point);
    }

    public synchronized List<MetricPoint> queryRange(String metricName, Map<String, String> tags, long startMs, long endMs) {
        return dataStore.stream()
                .filter(p -> p.getName().equals(metricName))
                .filter(p -> p.getTimestampMs() >= startMs && p.getTimestampMs() <= endMs)
                .filter(p -> matchesTags(p.getTags(), tags))
                .collect(Collectors.toList());
    }

    private boolean matchesTags(Map<String, String> pointTags, Map<String, String> queryTags) {
        if (queryTags == null || queryTags.isEmpty()) return true;
        for (Map.Entry<String, String> entry : queryTags.entrySet()) {
            if (!entry.getValue().equals(pointTags.get(entry.getKey()))) {
                return false;
            }
        }
        return true;
    }

    public void registerAlertRule(AlertRule rule) {
        alertRules.put(rule.getRuleId(), rule);
        currentAlertStates.put(rule.getRuleId(), AlertStatus.RESOLVED);
    }

    public synchronized List<AlertEvent> evaluateAlerts(long currentTimestampMs) {
        List<AlertEvent> newEvents = new ArrayList<>();

        for (AlertRule rule : alertRules.values()) {
            // Very simple evaluation: get latest point for metric
            MetricPoint latest = null;
            for (int i = dataStore.size() - 1; i >= 0; i--) {
                if (dataStore.get(i).getName().equals(rule.getMetricName())) {
                    latest = dataStore.get(i);
                    break;
                }
            }

            if (latest != null) {
                boolean isFiring = rule.isGreaterThan() ?
                    latest.getValue() > rule.getThreshold() :
                    latest.getValue() < rule.getThreshold();

                AlertStatus currentState = currentAlertStates.getOrDefault(rule.getRuleId(), AlertStatus.RESOLVED);

                if (isFiring && currentState == AlertStatus.RESOLVED) {
                    currentAlertStates.put(rule.getRuleId(), AlertStatus.FIRING);
                    AlertEvent event = new AlertEvent(rule.getRuleId(), AlertStatus.FIRING, currentTimestampMs);
                    alertHistory.add(event);
                    newEvents.add(event);
                } else if (!isFiring && currentState == AlertStatus.FIRING) {
                    currentAlertStates.put(rule.getRuleId(), AlertStatus.RESOLVED);
                    AlertEvent event = new AlertEvent(rule.getRuleId(), AlertStatus.RESOLVED, currentTimestampMs);
                    alertHistory.add(event);
                    newEvents.add(event);
                }
            }
        }
        return newEvents;
    }

    public synchronized double getHistogramPercentile(String metricName, Map<String, String> tags, long startMs, long endMs, double percentile) {
        List<MetricPoint> points = queryRange(metricName, tags, startMs, endMs).stream()
            .filter(p -> p.getType() == MetricType.HISTOGRAM)
            .collect(Collectors.toList());

        if (points.isEmpty()) return 0.0;

        List<Double> values = points.stream().map(MetricPoint::getValue).sorted().collect(Collectors.toList());
        int index = (int) Math.ceil((percentile / 100.0) * values.size()) - 1;
        if (index < 0) index = 0;
        if (index >= values.size()) index = values.size() - 1;
        return values.get(index);
    }

    public synchronized double getCounterTotal(String metricName, Map<String, String> tags, long startMs, long endMs) {
        return queryRange(metricName, tags, startMs, endMs).stream()
            .filter(p -> p.getType() == MetricType.COUNTER)
            .mapToDouble(MetricPoint::getValue)
            .sum();
    }

    public synchronized double getGaugeLatest(String metricName, Map<String, String> tags, long startMs, long endMs) {
        return queryRange(metricName, tags, startMs, endMs).stream()
            .filter(p -> p.getType() == MetricType.GAUGE)
            .max(Comparator.comparing(MetricPoint::getTimestampMs))
            .map(MetricPoint::getValue)
            .orElse(0.0);
    }
}
