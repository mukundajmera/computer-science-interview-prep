
public interface PricingStrategy {
    double calculatePrice(double baseTotal, int activeOrders, int availableDrivers);
}
