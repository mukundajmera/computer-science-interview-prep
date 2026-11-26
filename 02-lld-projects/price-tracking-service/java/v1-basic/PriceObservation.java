import java.time.Instant;
import java.util.Objects;

public class PriceObservation {
    private final String productId;
    private final Instant timestamp;
    private final double price;
    private final String retailer;

    public PriceObservation(String productId, Instant timestamp, double price, String retailer) {
        this.productId = productId;
        this.timestamp = timestamp;
        this.price = price;
        this.retailer = retailer;
    }

    public String getProductId() {
        return productId;
    }

    public Instant getTimestamp() {
        return timestamp;
    }

    public double getPrice() {
        return price;
    }

    public String getRetailer() {
        return retailer;
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        PriceObservation that = (PriceObservation) o;
        return Double.compare(that.price, price) == 0 &&
                Objects.equals(productId, that.productId) &&
                Objects.equals(timestamp, that.timestamp) &&
                Objects.equals(retailer, that.retailer);
    }

    @Override
    public int hashCode() {
        return Objects.hash(productId, timestamp, price, retailer);
    }
}
