package v3;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

import java.time.Instant;
import java.util.Arrays;
import java.util.Collections;
import java.util.List;
import java.util.stream.Collectors;

import static org.junit.jupiter.api.Assertions.*;

public class DistributedAdClickAggregatorV3Test {

    private DistributedAdClickAggregator aggregator;

    @BeforeEach
    void setUp() {
        // watermark 15 min (900s), 16 partitions, 4 salts
        aggregator = new DistributedAdClickAggregator(900, 16, 4);
    }

    @Test
    void testStableRoutingAndBasicMerge() {
        Instant now = Instant.parse("2023-10-01T10:00:00Z");

        // Use different event IDs to ensure they hash to different salts but same campaign
        DistributedAdClickAggregator.ClickEvent e1 = new DistributedAdClickAggregator.ClickEvent("e1", "camp1", "ad1", "pub1", now, Collections.emptyMap());
        DistributedAdClickAggregator.ClickEvent e2 = new DistributedAdClickAggregator.ClickEvent("e2", "camp1", "ad1", "pub1", now, Collections.emptyMap());
        DistributedAdClickAggregator.ClickEvent e3 = new DistributedAdClickAggregator.ClickEvent("e3", "camp1", "ad1", "pub1", now, Collections.emptyMap());

        aggregator.processEvent(e1, now);
        aggregator.processEvent(e2, now);
        aggregator.processEvent(e3, now);

        List<DistributedAdClickAggregator.AggregateBucket> metrics = aggregator.getMetrics(e1.dimsHash(), now.minusSeconds(60), now.plusSeconds(60));
        assertEquals(1, metrics.size());
        assertEquals(3, metrics.get(0).count);
    }

    @Test
    void testPartialApplicationAndIdempotentRetry() {
        Instant now = Instant.parse("2023-10-01T10:00:00Z");

        DistributedAdClickAggregator.ClickEvent e1 = new DistributedAdClickAggregator.ClickEvent("e1", "camp1", "ad1", "pub1", now, Collections.emptyMap());
        DistributedAdClickAggregator.ClickEvent e2 = new DistributedAdClickAggregator.ClickEvent("e2", "camp1", "ad1", "pub1", now, Collections.emptyMap());
        DistributedAdClickAggregator.ClickEvent e3 = new DistributedAdClickAggregator.ClickEvent("e3", "camp1", "ad1", "pub1", now, Collections.emptyMap());

        List<DistributedAdClickAggregator.ClickEvent> batch = Arrays.asList(e1, e2, e3);

        // Simulate failure after processing 2 events (e1, e2 applied)
        assertThrows(RuntimeException.class, () -> {
            aggregator.processBatchWithSimulatedFailure(batch, now, 2);
        });

        // The first 2 events should be in the system
        List<DistributedAdClickAggregator.AggregateBucket> metrics1 = aggregator.getMetrics(e1.dimsHash(), now.minusSeconds(60), now.plusSeconds(60));
        assertEquals(1, metrics1.size());
        assertEquals(2, metrics1.get(0).count);

        // Now retry the entire batch without simulating failure
        // e1 and e2 should be skipped, e3 should be applied
        batch.forEach(e -> aggregator.applyEvent(e, now, aggregator.getPartition(e.campaignId)));

        List<DistributedAdClickAggregator.AggregateBucket> metrics2 = aggregator.getMetrics(e1.dimsHash(), now.minusSeconds(60), now.plusSeconds(60));
        assertEquals(1, metrics2.size());
        assertEquals(3, metrics2.get(0).count);
    }

    @Test
    void testLateArrivalCorrectionVisibility() {
        Instant now = Instant.parse("2023-10-01T10:05:00Z");
        Instant lateTime = Instant.parse("2023-10-01T10:00:00Z"); // 5 mins late

        DistributedAdClickAggregator.ClickEvent lateEvent = new DistributedAdClickAggregator.ClickEvent("e1", "camp1", "ad1", "pub1", lateTime, Collections.emptyMap());

        aggregator.processEvent(lateEvent, now);

        List<DistributedAdClickAggregator.CorrectionEntry> corrections = aggregator.getCorrections("camp1", lateTime.minusSeconds(60), lateTime.plusSeconds(60));
        assertEquals(1, corrections.size());
        assertEquals(1, corrections.get(0).delta);
        assertEquals("Late arrival", corrections.get(0).reason);

        List<DistributedAdClickAggregator.AggregateBucket> metrics = aggregator.getMetrics(lateEvent.dimsHash(), lateTime.minusSeconds(60), lateTime.plusSeconds(60));
        assertEquals(1, metrics.size());
        assertEquals(1, metrics.get(0).count);
    }
}
