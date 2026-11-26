package v1_basic;

import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

// Tests deliberately select this version in both languages, compile independently and include normal/edge/rollback fixtures without external network or uncontrolled wall-clock waits.
public class AdClickAggregatorV1Test {
    @Test
    void testV1Sanity() {
        InMemoryAggregationStore store = new InMemoryAggregationStore();
        AdClickAggregator adClickAggregator = new AdClickAggregator(store, 60000);
        QueryService queryService = new QueryService(store);

        adClickAggregator.ingest(new ClickEvent("e1", "ad1", "u1", 1000));
        adClickAggregator.ingest(new ClickEvent("e2", "ad1", "u2", 2000));
        adClickAggregator.ingest(new ClickEvent("e3", "ad1", "u3", 65000));

        assertEquals(2, queryService.getClicksForAd("ad1", 0));
        assertEquals(1, queryService.getClicksForAd("ad1", 60000));
        assertEquals(0, queryService.getClicksForAd("ad2", 0));
    }

    @Test
    void testV1Deduplication() {
        InMemoryAggregationStore store = new InMemoryAggregationStore();
        AdClickAggregator adClickAggregator = new AdClickAggregator(store, 60000);
        QueryService queryService = new QueryService(store);

        adClickAggregator.ingest(new ClickEvent("e1", "ad1", "u1", 1000));
        adClickAggregator.ingest(new ClickEvent("e1", "ad1", "u1", 1000));
        adClickAggregator.ingest(new ClickEvent("e1", "ad1", "u1", 1000));

        assertEquals(1, queryService.getClicksForAd("ad1", 0));
    }

    @Test
    void testV1WindowBoundaries() {
        InMemoryAggregationStore store = new InMemoryAggregationStore();
        AdClickAggregator adClickAggregator = new AdClickAggregator(store, 60000);
        QueryService queryService = new QueryService(store);

        adClickAggregator.ingest(new ClickEvent("e1", "ad1", "u1", 0));
        adClickAggregator.ingest(new ClickEvent("e2", "ad1", "u1", 59999));
        adClickAggregator.ingest(new ClickEvent("e3", "ad1", "u1", 60000));

        assertEquals(2, queryService.getClicksForAd("ad1", 0));
        assertEquals(1, queryService.getClicksForAd("ad1", 60000));
    }

    @Test
    void testV1RollbackOnStoreFailure() {
        AggregationStore failingStore = new AggregationStore() {
            @Override
            public void increment(AggregationKey key, int count) {
                throw new RuntimeException("Store failure");
            }
            @Override
            public int getCount(AggregationKey key) {
                return 0;
            }
            @Override
            public java.util.Map<AggregationKey, Integer> getAll() {
                return new java.util.HashMap<>();
            }
        };
        AdClickAggregator adClickAggregator = new AdClickAggregator(failingStore, 60000);
        ClickEvent event = new ClickEvent("e1", "ad1", "u1", 1000);

        assertThrows(RuntimeException.class, () -> adClickAggregator.ingest(event));

        // Attempt exact duplicate ingestion, should fail again because first attempt failed and did not commit exactSeenEvents
        assertThrows(RuntimeException.class, () -> adClickAggregator.ingest(event));
    }

    @Test
    void testV1OutOfOrderAndLateEvents() {
        InMemoryAggregationStore store = new InMemoryAggregationStore();
        AdClickAggregator adClickAggregator = new AdClickAggregator(store, 60000);
        QueryService queryService = new QueryService(store);

        adClickAggregator.ingest(new ClickEvent("e3", "ad1", "u1", 65000));
        adClickAggregator.ingest(new ClickEvent("e1", "ad1", "u1", 1000));
        adClickAggregator.ingest(new ClickEvent("e4", "ad1", "u1", 125000));
        adClickAggregator.ingest(new ClickEvent("e2", "ad1", "u1", 2000));

        assertEquals(2, queryService.getClicksForAd("ad1", 0));
        assertEquals(1, queryService.getClicksForAd("ad1", 60000));
        assertEquals(1, queryService.getClicksForAd("ad1", 120000)); // Out of order events processed correctly
    }

    @Test
    void testV1InvalidPayloads() {
        InMemoryAggregationStore store = new InMemoryAggregationStore();
        AdClickAggregator adClickAggregator = new AdClickAggregator(store, 60000);

        assertThrows(IllegalArgumentException.class, () -> {
            adClickAggregator.ingest(new ClickEvent("", "ad1", "u1", 1000)); // Invalid event payload
        });

        assertThrows(IllegalArgumentException.class, () -> {
            adClickAggregator.ingest(new ClickEvent("e1", "", "u1", 1000));
        });

        assertThrows(IllegalArgumentException.class, () -> {
            adClickAggregator.ingest(null); // Empty input fails predictably
        });
    }
}
