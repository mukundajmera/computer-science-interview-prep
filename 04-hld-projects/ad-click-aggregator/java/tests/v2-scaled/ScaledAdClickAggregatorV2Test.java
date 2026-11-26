package v2;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

import java.time.Instant;
import java.util.Collections;
import java.util.List;

import static org.junit.jupiter.api.Assertions.*;

public class ScaledAdClickAggregatorV2Test {

    private ScaledAdClickAggregator aggregator;

    @BeforeEach
    void setUp() {
        // watermark bound 15 mins (900s), dedup expiry 1 hour (3600s)
        aggregator = new ScaledAdClickAggregator(900, 3600);
    }

    @Test
    void testBasicAggregationAndDedup() {
        Instant now = Instant.parse("2023-10-01T10:00:00Z");
        ScaledAdClickAggregator.ClickEvent e1 = new ScaledAdClickAggregator.ClickEvent("e1", "camp1", "ad1", "pub1", now, Collections.emptyMap());
        ScaledAdClickAggregator.ClickEvent e2 = new ScaledAdClickAggregator.ClickEvent("e1", "camp1", "ad1", "pub1", now, Collections.emptyMap()); // dup
        ScaledAdClickAggregator.ClickEvent e3 = new ScaledAdClickAggregator.ClickEvent("e3", "camp1", "ad1", "pub1", now, Collections.emptyMap());

        aggregator.processEvent(e1, now);
        aggregator.processEvent(e2, now); // Should be deduped
        aggregator.processEvent(e3, now);

        List<ScaledAdClickAggregator.AggregateBucket> metrics = aggregator.getMetrics("camp1", now.minusSeconds(60), now.plusSeconds(60));
        assertEquals(1, metrics.size());
        assertEquals(2, metrics.get(0).count);
    }

    @Test
    void testLateEventWithinBound() {
        Instant now = Instant.parse("2023-10-01T10:05:00Z");
        Instant lateTime = Instant.parse("2023-10-01T10:00:00Z"); // 5 mins late

        ScaledAdClickAggregator.ClickEvent lateEvent = new ScaledAdClickAggregator.ClickEvent("e1", "camp1", "ad1", "pub1", lateTime, Collections.emptyMap());

        aggregator.processEvent(lateEvent, now);

        List<ScaledAdClickAggregator.CorrectionEntry> corrections = aggregator.getCorrections("camp1", lateTime.minusSeconds(60), lateTime.plusSeconds(60));
        assertEquals(1, corrections.size());
        assertEquals(1, corrections.get(0).delta);

        List<ScaledAdClickAggregator.AggregateBucket> metrics = aggregator.getMetrics("camp1", lateTime.minusSeconds(60), lateTime.plusSeconds(60));
        assertEquals(1, metrics.size());
        assertEquals(1, metrics.get(0).count);
    }

    @Test
    void testOutOfBoundEventDropped() {
        Instant now = Instant.parse("2023-10-01T10:20:00Z");
        Instant veryLateTime = Instant.parse("2023-10-01T10:00:00Z"); // 20 mins late, bound is 15 mins

        ScaledAdClickAggregator.ClickEvent veryLateEvent = new ScaledAdClickAggregator.ClickEvent("e1", "camp1", "ad1", "pub1", veryLateTime, Collections.emptyMap());

        aggregator.processEvent(veryLateEvent, now);

        assertEquals(1, aggregator.getDroppedEvents());
        List<ScaledAdClickAggregator.AggregateBucket> metrics = aggregator.getMetrics("camp1", veryLateTime.minusSeconds(60), veryLateTime.plusSeconds(60));
        assertEquals(0, metrics.size());
    }

    @Test
    void testDedupExpiry() {
        Instant now = Instant.parse("2023-10-01T10:00:00Z");
        ScaledAdClickAggregator.ClickEvent e1 = new ScaledAdClickAggregator.ClickEvent("e1", "camp1", "ad1", "pub1", now, Collections.emptyMap());

        aggregator.processEvent(e1, now);

        // Fast forward 2 hours
        Instant later = now.plusSeconds(7200);
        ScaledAdClickAggregator.ClickEvent e2 = new ScaledAdClickAggregator.ClickEvent("e1", "camp1", "ad1", "pub1", later, Collections.emptyMap()); // Same event id, but much later processing

        aggregator.processEvent(e2, later);

        // Because dedup expired (1 hour), the new event should be processed.
        List<ScaledAdClickAggregator.AggregateBucket> metricsLater = aggregator.getMetrics("camp1", later.minusSeconds(60), later.plusSeconds(60));
        assertEquals(1, metricsLater.size());
        assertEquals(1, metricsLater.get(0).count);
    }

    @Test
    void testReplayIdempotenceAndPartitionRouting() {
        Instant now = Instant.parse("2023-10-01T10:00:00Z");
        ScaledAdClickAggregator.ClickEvent e1 = new ScaledAdClickAggregator.ClickEvent("e1", "camp1", "ad1", "pub1", now, Collections.emptyMap());

        aggregator.processEvent(e1, now);
        List<ScaledAdClickAggregator.AggregateBucket> metrics1 = aggregator.getMetrics("camp1", now.minusSeconds(60), now.plusSeconds(60));
        assertEquals(1, metrics1.get(0).count);

        // Replay partition
        int partition = aggregator.getPartition("camp1");
        aggregator.replayPartition(partition, now.plusSeconds(10));

        // The aggregate should be rebuilt, but count should remain 1 because it's re-aggregated
        // without duplicates.
        List<ScaledAdClickAggregator.AggregateBucket> metrics2 = aggregator.getMetrics("camp1", now.minusSeconds(60), now.plusSeconds(60));
        assertEquals(1, metrics2.get(0).count);
    }
}
