package v2_scaled;

import java.util.*;
import java.util.concurrent.ConcurrentHashMap;
import java.util.stream.Collectors;

public class ScaledMetricsMonitoringService {

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

    public enum Resolution {
        RAW, ONE_MIN, ONE_HOUR
    }

    public static class RollupPoint {
        private final String name;
        private final Map<String, String> tags;
        private final Resolution resolution;
        private final long windowStartMs;
        private int count;
        private double sumValue;
        private double minValue;
        private double maxValue;

        public RollupPoint(String name, Map<String, String> tags, Resolution resolution, long windowStartMs,
                           int count, double sumValue, double minValue, double maxValue) {
            this.name = name;
            this.tags = tags != null ? new HashMap<>(tags) : new HashMap<>();
            this.resolution = resolution;
            this.windowStartMs = windowStartMs;
            this.count = count;
            this.sumValue = sumValue;
            this.minValue = minValue;
            this.maxValue = maxValue;
        }

        public String getName() { return name; }
        public Map<String, String> getTags() { return tags; }
        public Resolution getResolution() { return resolution; }
        public long getWindowStartMs() { return windowStartMs; }
        public int getCount() { return count; }
        public double getSumValue() { return sumValue; }
        public double getMinValue() { return minValue; }
        public double getMaxValue() { return maxValue; }

        public void update(double value) {
            this.count++;
            this.sumValue += value;
            this.minValue = Math.min(this.minValue, value);
            this.maxValue = Math.max(this.maxValue, value);
        }
    }

    public static class AlertRule {
        private final String ruleId;
        private final String metricName;
        private final double threshold;
        private final boolean greaterThan;
        private final double hysteresis;
        private final long cooldownMs;

        public AlertRule(String ruleId, String metricName, double threshold, boolean greaterThan, double hysteresis, long cooldownMs) {
            this.ruleId = ruleId;
            this.metricName = metricName;
            this.threshold = threshold;
            this.greaterThan = greaterThan;
            this.hysteresis = hysteresis;
            this.cooldownMs = cooldownMs;
        }

        public String getRuleId() { return ruleId; }
        public String getMetricName() { return metricName; }
        public double getThreshold() { return threshold; }
        public boolean isGreaterThan() { return greaterThan; }
        public double getHysteresis() { return hysteresis; }
        public long getCooldownMs() { return cooldownMs; }
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

    private final int batchSize;
    private final List<MetricPoint> ingestionBuffer = new ArrayList<>();

    private final List<MetricPoint> rawData = new ArrayList<>();
    private final List<RollupPoint> rollups1m = new ArrayList<>();
    private final List<RollupPoint> rollups1h = new ArrayList<>();

    private final Map<String, AlertRule> alertRules = new ConcurrentHashMap<>();
    private final Map<String, AlertStatus> currentAlertStates = new ConcurrentHashMap<>();
    private final Map<String, Long> lastAlertTime = new ConcurrentHashMap<>();
    private final List<AlertEvent> alertHistory = new ArrayList<>();

    public ScaledMetricsMonitoringService(int batchSize) {
        this.batchSize = batchSize;
    }

    public synchronized void ingest(MetricPoint point) {
        ingestionBuffer.add(point);
        if (ingestionBuffer.size() >= batchSize) {
            flush();
        }
    }

    public synchronized void flush() {
        if (ingestionBuffer.isEmpty()) {
            return;
        }

        rawData.addAll(ingestionBuffer);
        buildRollups(ingestionBuffer);
        ingestionBuffer.clear();
    }

    private void buildRollups(List<MetricPoint> points) {
        for (MetricPoint point : points) {
            long window1m = (point.getTimestampMs() / 60000) * 60000;
            updateRollup(rollups1m, Resolution.ONE_MIN, point, window1m);

            long window1h = (point.getTimestampMs() / 3600000) * 3600000;
            updateRollup(rollups1h, Resolution.ONE_HOUR, point, window1h);
        }
    }

    private void updateRollup(List<RollupPoint> rollupsList, Resolution resolution, MetricPoint point, long windowStart) {
        for (int i = rollupsList.size() - 1; i >= 0; i--) {
            RollupPoint rollup = rollupsList.get(i);
            if (rollup.getName().equals(point.getName()) && rollup.getWindowStartMs() == windowStart && matchesTags(rollup.getTags(), point.getTags())) {
                rollup.update(point.getValue());
                return;
            }
        }

        rollupsList.add(new RollupPoint(
            point.getName(),
            point.getTags(),
            resolution,
            windowStart,
            1,
            point.getValue(),
            point.getValue(),
            point.getValue()
        ));
    }

    public synchronized List<?> queryRange(String metricName, Map<String, String> tags, long startMs, long endMs, Resolution resolution) {
        flush();

        if (resolution == Resolution.RAW) {
            return rawData.stream()
                .filter(p -> p.getName().equals(metricName))
                .filter(p -> p.getTimestampMs() >= startMs && p.getTimestampMs() <= endMs)
                .filter(p -> matchesTags(p.getTags(), tags))
                .collect(Collectors.toList());
        } else if (resolution == Resolution.ONE_MIN) {
            return rollups1m.stream()
                .filter(p -> p.getName().equals(metricName))
                .filter(p -> p.getWindowStartMs() >= startMs && p.getWindowStartMs() <= endMs)
                .filter(p -> matchesTags(p.getTags(), tags))
                .collect(Collectors.toList());
        } else {
            return rollups1h.stream()
                .filter(p -> p.getName().equals(metricName))
                .filter(p -> p.getWindowStartMs() >= startMs && p.getWindowStartMs() <= endMs)
                .filter(p -> matchesTags(p.getTags(), tags))
                .collect(Collectors.toList());
        }
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
        flush();
        List<AlertEvent> newEvents = new ArrayList<>();

        for (AlertRule rule : alertRules.values()) {
            MetricPoint latest = null;
            for (int i = rawData.size() - 1; i >= 0; i--) {
                if (rawData.get(i).getName().equals(rule.getMetricName())) {
                    latest = rawData.get(i);
                    break;
                }
            }

            if (latest != null) {
                AlertStatus currentState = currentAlertStates.getOrDefault(rule.getRuleId(), AlertStatus.RESOLVED);
                long lastTime = lastAlertTime.getOrDefault(rule.getRuleId(), 0L);

                if (lastTime != 0 && currentTimestampMs - lastTime < rule.getCooldownMs()) {
                    continue;
                }

                boolean isFiring;
                boolean isResolving;

                if (rule.isGreaterThan()) {
                    isFiring = latest.getValue() > rule.getThreshold();
                    isResolving = latest.getValue() < (rule.getThreshold() - rule.getHysteresis());
                } else {
                    isFiring = latest.getValue() < rule.getThreshold();
                    isResolving = latest.getValue() > (rule.getThreshold() + rule.getHysteresis());
                }

                if (isFiring && currentState == AlertStatus.RESOLVED) {
                    currentAlertStates.put(rule.getRuleId(), AlertStatus.FIRING);
                    lastAlertTime.put(rule.getRuleId(), currentTimestampMs);
                    AlertEvent event = new AlertEvent(rule.getRuleId(), AlertStatus.FIRING, currentTimestampMs);
                    alertHistory.add(event);
                    newEvents.add(event);
                } else if (isResolving && currentState == AlertStatus.FIRING) {
                    currentAlertStates.put(rule.getRuleId(), AlertStatus.RESOLVED);
                    lastAlertTime.put(rule.getRuleId(), currentTimestampMs);
                    AlertEvent event = new AlertEvent(rule.getRuleId(), AlertStatus.RESOLVED, currentTimestampMs);
                    alertHistory.add(event);
                    newEvents.add(event);
                }
            }
        }

        return newEvents;
    }

    public synchronized double getSlidingWindowPercentile(String metricName, Map<String, String> tags, long startMs, long endMs, double percentile) {
        flush();
        List<MetricPoint> points = rawData.stream()
            .filter(p -> p.getName().equals(metricName))
            .filter(p -> p.getType() == MetricType.HISTOGRAM)
            .filter(p -> p.getTimestampMs() >= startMs && p.getTimestampMs() <= endMs)
            .filter(p -> matchesTags(p.getTags(), tags))
            .collect(Collectors.toList());

        if (points.isEmpty()) return 0.0;

        List<Double> values = points.stream().map(MetricPoint::getValue).sorted().collect(Collectors.toList());
        int index = (int) Math.ceil((percentile / 100.0) * values.size()) - 1;
        if (index < 0) index = 0;
        if (index >= values.size()) index = values.size() - 1;
        return values.get(index);
    }

    // Package-private getters for testing
    List<MetricPoint> getRawData() { return rawData; }
    List<MetricPoint> getIngestionBuffer() { return ingestionBuffer; }
    AlertStatus getAlertStatus(String ruleId) { return currentAlertStates.get(ruleId); }
}
