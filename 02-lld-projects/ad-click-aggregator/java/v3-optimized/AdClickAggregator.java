package v3_optimized;

import v1_basic.ClickEvent;
import v1_basic.AggregationKey;
import v2_extended.WindowStrategy;
import v2_extended.EventDeduplicator;
import java.util.List;

public class AdClickAggregator {
    private final ShardedStateStore store;
    private final WatermarkManager watermarkManager;
    private final LateEventHandler lateHandler;
    private final WindowStrategy windowStrategy;
    private final EventDeduplicator deduplicator;

    public AdClickAggregator(ShardedStateStore store, WatermarkManager watermarkManager, LateEventHandler lateHandler, WindowStrategy windowStrategy, EventDeduplicator deduplicator) {
        this.store = store;
        this.watermarkManager = watermarkManager;
        this.lateHandler = lateHandler;
        this.windowStrategy = windowStrategy;
        this.deduplicator = deduplicator;
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

        if (deduplicator != null && deduplicator.isDuplicate(event.getEventId())) {
            return;
        }

        watermarkManager.updateWatermark(event.getTimestamp());
        
        if (lateHandler.isLate(event, watermarkManager.getWatermark())) {
            return;
        }

        List<Long> windows = windowStrategy.getOverlappingWindows(event.getTimestamp());
        for (long windowStart : windows) {
            AggregationKey key = new AggregationKey(event.getAdId(), windowStart);
            store.increment(key, 1);
        }
    }
}
