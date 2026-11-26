import java.time.Instant;
import java.time.ZoneOffset;
import java.time.format.DateTimeFormatter;
import java.util.Map;
import java.util.Set;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.atomic.AtomicLong;

public class AdClickAggregator {
    // Stores aggregated counts. Key structure: "dimension:dimensionValue:granularity:windowStr"
    private final Map<String, AtomicLong> aggregationCounters = new ConcurrentHashMap<>();

    // Deduplication set
    private final Set<String> processedEventIds = ConcurrentHashMap.newKeySet();

    private static final DateTimeFormatter MINUTE_FORMATTER = DateTimeFormatter.ofPattern("yyyy-MM-dd'T'HH:mm").withZone(ZoneOffset.UTC);
    private static final DateTimeFormatter HOUR_FORMATTER = DateTimeFormatter.ofPattern("yyyy-MM-dd'T'HH").withZone(ZoneOffset.UTC);
    private static final DateTimeFormatter DAY_FORMATTER = DateTimeFormatter.ofPattern("yyyy-MM-dd").withZone(ZoneOffset.UTC);

    public static class ClickEvent {
        public final String eventId;
        public final Instant eventTime;
        public final String campaignId;
        public final String adGroupId;
        public final String publisherId;

        public ClickEvent(String eventId, Instant eventTime, String campaignId, String adGroupId, String publisherId) {
            if (eventId == null || eventId.trim().isEmpty()) {
                throw new IllegalArgumentException("eventId is required");
            }
            if (eventTime == null) {
                throw new IllegalArgumentException("eventTime is required");
            }
            if (campaignId == null || campaignId.trim().isEmpty()) {
                throw new IllegalArgumentException("campaignId is required");
            }
            if (adGroupId == null || adGroupId.trim().isEmpty()) {
                throw new IllegalArgumentException("adGroupId is required");
            }
            if (publisherId == null || publisherId.trim().isEmpty()) {
                throw new IllegalArgumentException("publisherId is required");
            }
            this.eventId = eventId;
            this.eventTime = eventTime;
            this.campaignId = campaignId;
            this.adGroupId = adGroupId;
            this.publisherId = publisherId;
        }
    }

    public void processEvent(ClickEvent event) {
        if (event == null) {
            throw new IllegalArgumentException("Event cannot be null");
        }

        // Deduplicate using eventId
        if (!processedEventIds.add(event.eventId)) {
            return;
        }

        String minWindow = MINUTE_FORMATTER.format(event.eventTime);
        String hourWindow = HOUR_FORMATTER.format(event.eventTime);
        String dayWindow = DAY_FORMATTER.format(event.eventTime);

        incrementCounter("campaign", event.campaignId, "1m", minWindow);
        incrementCounter("campaign", event.campaignId, "1h", hourWindow);
        incrementCounter("campaign", event.campaignId, "1d", dayWindow);

        incrementCounter("adGroup", event.adGroupId, "1m", minWindow);
        incrementCounter("adGroup", event.adGroupId, "1h", hourWindow);
        incrementCounter("adGroup", event.adGroupId, "1d", dayWindow);

        incrementCounter("publisher", event.publisherId, "1m", minWindow);
        incrementCounter("publisher", event.publisherId, "1h", hourWindow);
        incrementCounter("publisher", event.publisherId, "1d", dayWindow);
    }

    private void incrementCounter(String dimension, String dimensionValue, String granularity, String windowStr) {
        String key = String.format("%s:%s:%s:%s", dimension, dimensionValue, granularity, windowStr);
        aggregationCounters.computeIfAbsent(key, k -> new AtomicLong(0)).incrementAndGet();
    }

    public long getCount(String dimension, String dimensionValue, String granularity, String windowStr) {
        String key = String.format("%s:%s:%s:%s", dimension, dimensionValue, granularity, windowStr);
        AtomicLong count = aggregationCounters.get(key);
        return count != null ? count.get() : 0L;
    }
}
