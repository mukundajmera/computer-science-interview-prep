
public class SurgePricingStrategy implements PricingStrategy {
    @Override
    public double calculatePrice(double baseTotal, int activeOrders, int availableDrivers) {
        if (availableDrivers == 0) return baseTotal * 2.0;
        double ratio = (double) activeOrders / availableDrivers;
        if (ratio > 2.0) {
            return baseTotal * 1.5;
        } else if (ratio > 1.0) {
            return baseTotal * 1.2;
        }
        return baseTotal;
    }
}
