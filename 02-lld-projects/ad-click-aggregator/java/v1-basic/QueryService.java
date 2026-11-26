package v1_basic;

public class QueryService {
    private final AggregationStore store;

    public QueryService(AggregationStore store) {
        this.store = store;
    }

    public QueryService() {
        this.store = new InMemoryAggregationStore();
    }

    public int getClicksForAd(String adId, long windowStartMs) {
        AggregationKey key = new AggregationKey(adId, windowStartMs);
        return store.getCount(key);
    }
}
