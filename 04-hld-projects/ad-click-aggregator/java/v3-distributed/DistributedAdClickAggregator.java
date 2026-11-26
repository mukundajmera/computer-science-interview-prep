package v3;

import java.time.Instant;
import java.util.*;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.atomic.AtomicLong;
import java.util.stream.Collectors;

public class DistributedAdClickAggregator {

    public static class ClickEvent {
        public final String eventId;
        public final String campaignId;
        public final String adGroupId;
        public final String publisherId;
        public final Instant eventTime;
        public final Map<String, String> attributes;

        public ClickEvent(String eventId, String campaignId, String adGroupId, String publisherId, Instant eventTime, Map<String, String> attributes) {
            this.eventId = eventId;
            this.campaignId = campaignId;
            this.adGroupId = adGroupId;
            this.publisherId = publisherId;
            this.eventTime = eventTime;
            this.attributes = attributes;
        }

        public String dimsHash() {
            // A simplified hash for dimensions
            return String.format("%s:%s:%s", campaignId, adGroupId, publisherId);
        }
    }

    public static class AggregateBucket {
        public final String campaignId;
        public final Instant windowStart;
        public final long count;

        public AggregateBucket(String campaignId, Instant windowStart, long count) {
            this.campaignId = campaignId;
            this.windowStart = windowStart;
            this.count = count;
        }
    }

    public static class CorrectionEntry {
        public final String campaignId;
        public final Instant windowStart;
        public final long delta;
        public final String reason;
        public final Instant appliedAt;

        public CorrectionEntry(String campaignId, Instant windowStart, long delta, String reason, Instant appliedAt) {
            this.campaignId = campaignId;
            this.windowStart = windowStart;
            this.delta = delta;
            this.reason = reason;
            this.appliedAt = appliedAt;
        }
    }

    // State definitions
    private final long watermarkBoundSeconds;
    private final int numPartitions;
    private final int maxSalt; // Number of partial buckets to use for hot keys

    // Ingest Log: PartitionId -> List<ClickEvent>
    private final Map<Integer, List<ClickEvent>> ingestLogs = new ConcurrentHashMap<>();

    // Processed Events (Idempotence): PartitionId -> Set<String(eventId)>
    private final Map<Integer, Set<String>> processedEvents = new ConcurrentHashMap<>();

    // Aggregates: SaltedKey (CampaignId#Salt) -> WindowStart -> Count
    private final Map<String, Map<Instant, AtomicLong>> saltedAggregates = new ConcurrentHashMap<>();

    // Correction Log
    private final List<CorrectionEntry> correctionLog = Collections.synchronizedList(new ArrayList<>());

    private final AtomicLong droppedEvents = new AtomicLong(0);

    public DistributedAdClickAggregator(long watermarkBoundSeconds, int numPartitions, int maxSalt) {
        this.watermarkBoundSeconds = watermarkBoundSeconds;
        this.numPartitions = numPartitions;
        this.maxSalt = maxSalt;
    }

    public int getPartition(String key) {
        return Math.abs(key.hashCode()) % numPartitions;
    }

    private int getSalt(String eventId) {
        return Math.abs(eventId.hashCode()) % maxSalt;
    }

    private String getSaltedKey(String campaignId, int salt) {
        return campaignId + "#" + salt;
    }

    public void processEvent(ClickEvent event, Instant processingTime) {
        int partitionId = getPartition(event.campaignId);
        ingestLogs.computeIfAbsent(partitionId, k -> Collections.synchronizedList(new ArrayList<>()))
                  .add(event);

        applyEvent(event, processingTime, partitionId);
    }

    // Simulated log processing step that handles retries natively
    public void applyEvent(ClickEvent event, Instant processingTime, int partitionId) {
        if (processingTime.getEpochSecond() - event.eventTime.getEpochSecond() > watermarkBoundSeconds) {
            droppedEvents.incrementAndGet();
            return;
        }

        Set<String> processed = processedEvents.computeIfAbsent(partitionId, k -> ConcurrentHashMap.newKeySet());
        if (processed.contains(event.eventId)) {
            // Idempotent retry: skip already applied
            return;
        }

        Instant windowStart = getWindowStart(event.eventTime);
        int salt = getSalt(event.eventId);
        String saltedKey = getSaltedKey(event.dimsHash(), salt);

        // Update Aggregate
        saltedAggregates.computeIfAbsent(saltedKey, k -> new ConcurrentHashMap<>())
                        .computeIfAbsent(windowStart, k -> new AtomicLong(0))
                        .incrementAndGet();

        // Correction Logic
        Instant processingWindowStart = getWindowStart(processingTime);
        if (windowStart.isBefore(processingWindowStart)) {
            correctionLog.add(new CorrectionEntry(event.campaignId, windowStart, 1, "Late arrival", processingTime));
        }

        // Mark as processed
        processed.add(event.eventId);
    }

    public void processBatchWithSimulatedFailure(List<ClickEvent> batch, Instant processingTime, int failAfter) {
        int count = 0;
        for (ClickEvent event : batch) {
            if (count == failAfter) {
                throw new RuntimeException("Simulated partial application failure");
            }
            int partitionId = getPartition(event.campaignId);
            applyEvent(event, processingTime, partitionId);
            count++;
        }
    }

    public Instant getWindowStart(Instant time) {
        return Instant.ofEpochSecond((time.getEpochSecond() / 60) * 60);
    }

    public List<AggregateBucket> getMetrics(String dimsHash, Instant from, Instant to) {
        Map<Instant, Long> mergedCounts = new HashMap<>();

        for (int i = 0; i < maxSalt; i++) {
            String saltedKey = getSaltedKey(dimsHash, i);
            Map<Instant, AtomicLong> windows = saltedAggregates.get(saltedKey);
            if (windows != null) {
                for (Map.Entry<Instant, AtomicLong> entry : windows.entrySet()) {
                    Instant w = entry.getKey();
                    if (!w.isBefore(from) && w.isBefore(to)) {
                        mergedCounts.put(w, mergedCounts.getOrDefault(w, 0L) + entry.getValue().get());
                    }
                }
            }
        }

        return mergedCounts.entrySet().stream()
                .map(e -> new AggregateBucket(dimsHash, e.getKey(), e.getValue()))
                .collect(Collectors.toList());
    }

    public List<CorrectionEntry> getCorrections(String campaignId, Instant from, Instant to) {
        return correctionLog.stream()
                .filter(c -> c.campaignId.equals(campaignId) && !c.windowStart.isBefore(from) && c.windowStart.isBefore(to))
                .collect(Collectors.toList());
    }

    public long getDroppedEvents() {
        return droppedEvents.get();
    }
}
