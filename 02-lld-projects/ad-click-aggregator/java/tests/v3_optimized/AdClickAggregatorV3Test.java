package v3_optimized;

import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

import v1_basic.AggregationKey;
import v1_basic.ClickEvent;
import v2_extended.WindowStrategy;

public class AdClickAggregatorV3Test {
    @Test
    void testV3Sanity() {
        ShardedStateStore store = new ShardedStateStore(4);
        WatermarkManager watermarkManager = new WatermarkManager();
        LateEventHandler lateHandler = new LateEventHandler(5000);
        WindowStrategy windowStrategy = new WindowStrategy(60000, 10000);
        
        AdClickAggregator aggregator = new AdClickAggregator(store, watermarkManager, lateHandler, windowStrategy);
        
        aggregator.ingest(new ClickEvent("e1", "ad1", "u1", 10000));
        // Watermark is now 10000
        
        // Late event (older than watermark - 5000) -> should be dropped
        aggregator.ingest(new ClickEvent("e2", "ad1", "u2", 4000)); 
        
        // In-time event -> should be processed
        aggregator.ingest(new ClickEvent("e3", "ad1", "u3", 8000));
        
        AggregationKey key = new AggregationKey("ad1", 0);
        assertEquals(2, store.getCount(key)); // e1 and e3 processed
    }

    @Test
    void testV3DeduplicationAndValidation() {
        ShardedStateStore store = new ShardedStateStore(4);
        WatermarkManager watermarkManager = new WatermarkManager();
        LateEventHandler lateHandler = new LateEventHandler(5000);
        WindowStrategy windowStrategy = new WindowStrategy(60000, 10000);
        v2_extended.EventDeduplicator deduplicator = new v2_extended.EventDeduplicator();
     
        AdClickAggregator aggregator = new AdClickAggregator(store, watermarkManager, lateHandler, windowStrategy, deduplicator);
        
        assertThrows(IllegalArgumentException.class, () -> {
            aggregator.ingest(new ClickEvent("", "ad1", "u1", 10000));
        });

        aggregator.ingest(new ClickEvent("e1", "ad1", "u1", 10000));
        aggregator.ingest(new ClickEvent("e1", "ad1", "u1", 10000)); // Duplicate
        
        AggregationKey key = new AggregationKey("ad1", 0);
        assertEquals(1, store.getCount(key));
    }

    @Test
    void testV3ProcessingTimePolicy() {
        ShardedStateStore store = new ShardedStateStore(4);
        WatermarkManager watermarkManager = new WatermarkManager();
        LateEventHandler lateHandler = new LateEventHandler(5000);
        WindowStrategy windowStrategy = new WindowStrategy(60000, 10000);
        
        AdClickAggregator aggregator = new AdClickAggregator(store, watermarkManager, lateHandler, windowStrategy, null);
        
        aggregator.ingest(new ClickEvent("e1", "ad1", "u1", 1000), 400000);
        
        AggregationKey key = new AggregationKey("ad1", 0);
        assertEquals(0, store.getCount(key));
    }
}
