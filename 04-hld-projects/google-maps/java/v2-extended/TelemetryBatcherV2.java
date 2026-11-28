import java.util.ArrayList;
import java.util.List;
import java.util.function.DoubleSupplier;

/**
 * v2 telemetry batching (v2 improvement #3).
 *
 * Implements PITFALLS.md #5: mobile clients collect GPS pings continuously
 * but only send a batched payload every flushIntervalSeconds (the pitfall
 * suggests 15-30s), saving battery and cellular radio overhead. The clock
 * is injectable so tests can drive the flush window deterministically.
 * See GoogleMapsServiceV2 for the full v2 improvement list.
 */
public class TelemetryBatcherV2 {

    public static class Ping {
        public final double lat;
        public final double lng;
        public final double timestampSeconds;

        public Ping(double lat, double lng, double timestampSeconds) {
            this.lat = lat;
            this.lng = lng;
            this.timestampSeconds = timestampSeconds;
        }
    }

    private final double flushIntervalSeconds;
    private final DoubleSupplier clock;
    private final List<Ping> buffer = new ArrayList<>();
    private double lastFlush;

    public TelemetryBatcherV2(double flushIntervalSeconds, DoubleSupplier clock) {
        if (flushIntervalSeconds <= 0) {
            throw new IllegalArgumentException("flush interval must be positive");
        }
        this.flushIntervalSeconds = flushIntervalSeconds;
        this.clock = clock;
        this.lastFlush = clock.getAsDouble();
    }

    /**
     * Buffers one ping. Returns the flushed batch when the flush interval
     * has elapsed since the last send, else null.
     */
    public List<Ping> recordPing(double lat, double lng, double timestampSeconds) {
        buffer.add(new Ping(lat, lng, timestampSeconds));
        if (timestampSeconds - lastFlush >= flushIntervalSeconds) {
            return flush(timestampSeconds);
        }
        return null;
    }

    /** Sends everything buffered so far and restarts the window. */
    public List<Ping> flush(double nowSeconds) {
        List<Ping> batch = new ArrayList<>(buffer);
        buffer.clear();
        lastFlush = nowSeconds;
        return batch;
    }

    public int pendingCount() {
        return buffer.size();
    }
}
