package v2_extended;

import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

import v1_basic.InMemoryAggregationStore;
import v1_basic.QueryService;
import v1_basic.ClickEvent;

public class AdClickAggregatorV2Test {
    @Test
    void testV2Sanity() {
        InMemoryAggregationStore store = new InMemoryAggregationStore();
        EventDeduplicator deduplicator = new EventDeduplicator();
        WindowStrategy windowStrategy = new WindowStrategy(60000, 10000);
        FraudRule fraudRule = new FraudRule();

        AdClickAggregator aggregator = new AdClickAggregator(store, deduplicator, windowStrategy, fraudRule);
        QueryService queryService = new QueryService(store);

        aggregator.ingest(new ClickEvent("e1", "ad1", "u1", 1000), 1000);
        aggregator.ingest(new ClickEvent("e1", "ad1", "u1", 2000), 2000); // duplicate
        aggregator.ingest(new ClickEvent("e3", "ad1", "fraud_user", 3000), 3000); // fraud
        aggregator.ingest(new ClickEvent("e4", "ad1", "u2", 4000), 4000);

        assertEquals(2, queryService.getClicksForAd("ad1", 0));
    }
    
    @Test
    void testEmptyAndInvalidPayloads() {
        InMemoryAggregationStore store = new InMemoryAggregationStore();
        EventDeduplicator deduplicator = new EventDeduplicator();
        WindowStrategy windowStrategy = new WindowStrategy(60000, 10000);
        FraudRule fraudRule = new FraudRule();

        AdClickAggregator aggregator = new AdClickAggregator(store, deduplicator, windowStrategy, fraudRule);
        
        assertThrows(IllegalArgumentException.class, () -> {
            aggregator.ingest(new ClickEvent("", "ad1", "u1", 1000));
        });
        
        assertThrows(IllegalArgumentException.class, () -> {
            aggregator.ingest(new ClickEvent("e1", "", "u1", 1000));
        });
        
        assertThrows(IllegalArgumentException.class, () -> {
            aggregator.ingest(new ClickEvent("e1", "ad1", "", 1000));
        });
    }

    @Test
    void testWindowBoundaryAndLateEvents() {
        InMemoryAggregationStore store = new InMemoryAggregationStore();
        EventDeduplicator deduplicator = new EventDeduplicator();
        WindowStrategy windowStrategy = new WindowStrategy(60000, 60000);
        FraudRule fraudRule = new FraudRule();

        AdClickAggregator aggregator = new AdClickAggregator(store, deduplicator, windowStrategy, fraudRule);
        QueryService queryService = new QueryService(store);

        // Boundary inclusion
        aggregator.ingest(new ClickEvent("e1", "ad1", "u1", 60000), 60000);
        
        // Out-of-order acceptance
        aggregator.ingest(new ClickEvent("e2", "ad1", "u2", 30000), 120000);
        
        // Late-event rejection
        aggregator.ingest(new ClickEvent("e3", "ad1", "u3", 30000), 330001);
        
        assertEquals(1, queryService.getClicksForAd("ad1", 0));
        assertEquals(1, queryService.getClicksForAd("ad1", 60000));
    }
}
