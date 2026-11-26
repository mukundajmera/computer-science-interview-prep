package v3_optimized;

import v1_basic.ClickEvent;
import v2_extended.WindowStrategy;
import v2_extended.EventDeduplicator;

public class AdClickAggregatorDemo {
    public static void main(String[] args) {
        ShardedStateStore store = new ShardedStateStore(4);
        WatermarkManager watermarkManager = new WatermarkManager();
        LateEventHandler lateHandler = new LateEventHandler(5000);
        WindowStrategy windowStrategy = new WindowStrategy(60000, 10000);
        EventDeduplicator deduplicator = new EventDeduplicator();

        AdClickAggregator aggregator = new AdClickAggregator(store, watermarkManager, lateHandler, windowStrategy, deduplicator);

        aggregator.ingest(new ClickEvent("e1", "ad1", "u1", 1000));
    }
}
