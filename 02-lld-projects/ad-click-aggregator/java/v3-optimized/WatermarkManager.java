package v3_optimized;

public class WatermarkManager {
    private long currentWatermark = 0;

    public synchronized void updateWatermark(long timestamp) {
        if (timestamp > currentWatermark) {
            currentWatermark = timestamp;
        }
    }

    public synchronized long getWatermark() {
        return currentWatermark;
    }
}
