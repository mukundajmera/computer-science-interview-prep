package v2_extended;

import v1_basic.AggregationKey;
import v1_basic.AggregationStore;
import v1_basic.ClickEvent;
import java.util.List;

public class AdClickAggregator {
    private final AggregationStore store;
    private final EventDeduplicator deduplicator;
    private final WindowStrategy windowStrategy;
    private final FraudRule fraudRule;

    public AdClickAggregator(AggregationStore store, EventDeduplicator deduplicator, WindowStrategy windowStrategy, FraudRule fraudRule) {
        this.store = store;
        this.deduplicator = deduplicator;
        this.windowStrategy = windowStrategy;
        this.fraudRule = fraudRule;
    }

    public void ingest(ClickEvent event) {
        ingest(event, System.currentTimeMillis());
    }

    public void ingest(ClickEvent event, long processingTime) {
        if (event == null ||
            event.getEventId() == null || event.getEventId().isEmpty() ||
            event.getAdId() == null || event.getAdId().isEmpty() ||
            event.getUserId() == null || event.getUserId().isEmpty()) {
            throw new IllegalArgumentException("Empty input and invalid event payloads fail predictably");
        }

        if (processingTime - event.getTimestamp() > 300000) {
            return;
        }

        if (fraudRule.isFraud(event.getUserId())) {
            return;
        }

        if (deduplicator.isDuplicate(event.getEventId())) {
            return;
        }

        List<Long> windows = windowStrategy.getOverlappingWindows(event.getTimestamp());
        for (long windowStart : windows) {
            AggregationKey key = new AggregationKey(event.getAdId(), windowStart);
            store.increment(key, 1);
        }
    }
}
