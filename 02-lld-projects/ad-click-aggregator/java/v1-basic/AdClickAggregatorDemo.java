package v1_basic;

public class AdClickAggregatorDemo {
    public static void main(String[] args) {
        InMemoryAggregationStore store = new InMemoryAggregationStore();
        AdClickAggregator aggregator = new AdClickAggregator(store, 60000);
        QueryService queryService = new QueryService(store);
        
        ClickEvent event = new ClickEvent("e1", "ad1", "u1", 1000);
        aggregator.ingest(event);
        
        System.out.println("Clicks for ad1: " + queryService.getClicksForAd("ad1", 0));
    }
}
