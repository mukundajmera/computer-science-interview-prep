package v3_optimized;

import v1_basic.ClickEvent;

public class LateEventHandler {
    private final long maxLatenessMs;
    private long lateEventsDropped;

    public LateEventHandler(long maxLatenessMs) {
        this.maxLatenessMs = maxLatenessMs;
        this.lateEventsDropped = 0;
    }

    public boolean isLate(ClickEvent event, long currentWatermark) {
        if (event.getTimestamp() < currentWatermark - maxLatenessMs) {
            lateEventsDropped++;
            return true;
        }
        return false;
    }
}
