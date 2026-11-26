import java.time.Instant;
import java.util.Objects;

public class ProductPriceSummary {
    private final String productId;
    private final double minPrice;
    private final double maxPrice;
    private final double currentPrice;
    private final Instant lastUpdated;

    public ProductPriceSummary(String productId, double minPrice, double maxPrice, double currentPrice, Instant lastUpdated) {
        this.productId = productId;
        this.minPrice = minPrice;
        this.maxPrice = maxPrice;
        this.currentPrice = currentPrice;
        this.lastUpdated = lastUpdated;
    }

    public String getProductId() {
        return productId;
    }

    public double getMinPrice() {
        return minPrice;
    }

    public double getMaxPrice() {
        return maxPrice;
    }

    public double getCurrentPrice() {
        return currentPrice;
    }

    public Instant getLastUpdated() {
        return lastUpdated;
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        ProductPriceSummary that = (ProductPriceSummary) o;
        return Double.compare(that.minPrice, minPrice) == 0 &&
                Double.compare(that.maxPrice, maxPrice) == 0 &&
                Double.compare(that.currentPrice, currentPrice) == 0 &&
                Objects.equals(productId, that.productId) &&
                Objects.equals(lastUpdated, that.lastUpdated);
    }

    @Override
    public int hashCode() {
        return Objects.hash(productId, minPrice, maxPrice, currentPrice, lastUpdated);
    }
}
