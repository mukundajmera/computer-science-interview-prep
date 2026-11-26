package v2_extended;

public class PriceRecord {
    public final long timestamp;
    public final int priceCents;
    public final boolean inStock;

    public PriceRecord(long timestamp, int priceCents, boolean inStock) {
        this.timestamp = timestamp;
        this.priceCents = priceCents;
        this.inStock = inStock;
    }
}
