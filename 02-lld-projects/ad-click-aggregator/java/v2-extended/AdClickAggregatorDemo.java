package v2_extended;

import v1_basic.ClickEvent;
import v1_basic.InMemoryAggregationStore;
import v1_basic.QueryService;

public class AdClickAggregatorDemo {
    public static void main(String[] args) {
        InMemoryAggregationStore store = new InMemoryAggregationStore();
        EventDeduplicator deduplicator = new EventDeduplicator();
        WindowStrategy windowStrategy = new WindowStrategy(60000, 10000);
        FraudRule fraudRule = new FraudRule();

        AdClickAggregator aggregator = new AdClickAggregator(store, deduplicator, windowStrategy, fraudRule);
        QueryService queryService = new QueryService(store);

        ClickEvent event = new ClickEvent("e1", "ad1", "u1", 1000);
        aggregator.ingest(event);

        System.out.println("Clicks for ad1: " + queryService.getClicksForAd("ad1", 0));
    }
}
