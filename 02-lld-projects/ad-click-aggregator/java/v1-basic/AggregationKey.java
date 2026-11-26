package v1_basic;

import java.util.Objects;

public class AggregationKey {
    private final String adId;
    private final long windowStartMs;

    public AggregationKey(String adId, long windowStartMs) {
        this.adId = adId;
        this.windowStartMs = windowStartMs;
    }

    public String getAdId() { return adId; }
    public long getWindowStartMs() { return windowStartMs; }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        AggregationKey that = (AggregationKey) o;
        return windowStartMs == that.windowStartMs && Objects.equals(adId, that.adId);
    }

    @Override
    public int hashCode() {
        return Objects.hash(adId, windowStartMs);
    }
}
