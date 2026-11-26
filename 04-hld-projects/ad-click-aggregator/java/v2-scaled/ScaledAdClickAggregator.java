package v2;

import java.time.Instant;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.atomic.AtomicLong;
import java.util.stream.Collectors;

public class ScaledAdClickAggregator {

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

    private final long watermarkBoundSeconds;
    private final long dedupExpirySeconds;

    // Simulate Partitions (Immutable Ingest Log)
    // Map of Partition ID -> List of Events
    private final Map<Integer, List<ClickEvent>> ingestLogs = new ConcurrentHashMap<>();

    // Dedup Index: EventId -> Ingestion Timestamp
    private final Map<String, Instant> dedupIndex = new ConcurrentHashMap<>();

    // Aggregate Store: CampaignId -> WindowStart -> Count
    private final Map<String, Map<Instant, AtomicLong>> aggregates = new ConcurrentHashMap<>();

    // Correction Log
    private final List<CorrectionEntry> correctionLog = Collections.synchronizedList(new ArrayList<>());

    // Operator Metrics
    private final AtomicLong droppedEvents = new AtomicLong(0);

    public ScaledAdClickAggregator(long watermarkBoundSeconds, long dedupExpirySeconds) {
        this.watermarkBoundSeconds = watermarkBoundSeconds;
        this.dedupExpirySeconds = dedupExpirySeconds;
    }

    public int getPartition(String key) {
        return Math.abs(key.hashCode() % 16);
    }

    public void processEvent(ClickEvent event, Instant processingTime) {
        // 1. Check watermark bound (late events)
        if (processingTime.getEpochSecond() - event.eventTime.getEpochSecond() > watermarkBoundSeconds) {
            // Drop events beyond bound
            droppedEvents.incrementAndGet();
            return;
        }

        // 2. Dedup
        cleanupDedupIndex(processingTime);
        if (dedupIndex.containsKey(event.eventId)) {
            // Already processed
            return;
        }

        // Append to ingest log
        int partitionId = getPartition(event.campaignId);
        ingestLogs.computeIfAbsent(partitionId, k -> Collections.synchronizedList(new ArrayList<>()))
                  .add(event);

        dedupIndex.put(event.eventId, processingTime);

        // 3. Aggregate
        Instant windowStart = getWindowStart(event.eventTime);
        aggregates.computeIfAbsent(event.campaignId, k -> new ConcurrentHashMap<>())
                  .computeIfAbsent(windowStart, k -> new AtomicLong(0))
                  .incrementAndGet();

        // 4. Correction tracking
        Instant processingWindowStart = getWindowStart(processingTime);
        if (windowStart.isBefore(processingWindowStart)) {
            correctionLog.add(new CorrectionEntry(event.campaignId, windowStart, 1, "Late arrival", processingTime));
        }
    }

    public void replayPartition(int partitionId, Instant processingTime) {
        // Replaying a partition essentially re-runs its events through aggregation logic.
        // Since we are idempotent, if the events are already deduped and their dedup hasn't expired,
        // they are ignored. To truly "replay" as an operator without double counting, we could clear
        // the aggregates and rebuild them, but doing so for all campaigns is complex.
        // Real systems emit replacement events or rebuild views.
        // For our v1 contract preservation and idempotency requirement, we simulate
        // a replay by resetting the aggregates for campaigns found in this partition
        // and re-applying the log.
        List<ClickEvent> events = ingestLogs.getOrDefault(partitionId, Collections.emptyList());
        if (events.isEmpty()) return;

        // Clear aggregates that belong to this partition.
        // We only clear campaigns whose partition matches.
        for (String campaignId : aggregates.keySet()) {
            if (getPartition(campaignId) == partitionId) {
                aggregates.put(campaignId, new ConcurrentHashMap<>());
            }
        }

        // Remove those from dedup index so we can re-process
        for (ClickEvent e : events) {
            dedupIndex.remove(e.eventId);
        }

        // Also remove corrections matching these campaigns (for simplicity)
        correctionLog.removeIf(c -> getPartition(c.campaignId) == partitionId);

        // Temporarily store old log and clear it so processEvent appends fresh
        List<ClickEvent> oldLog = new ArrayList<>(events);
        ingestLogs.put(partitionId, Collections.synchronizedList(new ArrayList<>()));

        for (ClickEvent event : oldLog) {
            processEvent(event, processingTime);
        }
    }

    private void cleanupDedupIndex(Instant currentTime) {
        dedupIndex.entrySet().removeIf(entry ->
            currentTime.getEpochSecond() - entry.getValue().getEpochSecond() > dedupExpirySeconds
        );
    }

    private Instant getWindowStart(Instant time) {
        // 1-minute windows
        return Instant.ofEpochSecond((time.getEpochSecond() / 60) * 60);
    }

    public List<AggregateBucket> getMetrics(String campaignId, Instant from, Instant to) {
        Map<Instant, AtomicLong> campaignAggs = aggregates.getOrDefault(campaignId, Collections.emptyMap());
        return campaignAggs.entrySet().stream()
                .filter(e -> !e.getKey().isBefore(from) && e.getKey().isBefore(to))
                .map(e -> new AggregateBucket(campaignId, e.getKey(), e.getValue().get()))
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
