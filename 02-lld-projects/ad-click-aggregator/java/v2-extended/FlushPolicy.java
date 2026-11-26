package v2_extended;

public class FlushPolicy {
    private final long flushIntervalMs;
    private long lastFlush;

    public FlushPolicy(long flushIntervalMs) {
        this.flushIntervalMs = flushIntervalMs;
        this.lastFlush = 0;
    }

    public boolean shouldFlush(long currentTime) {
        if (currentTime - lastFlush >= flushIntervalMs) {
            lastFlush = currentTime;
            return true;
        }
        return false;
    }
}
