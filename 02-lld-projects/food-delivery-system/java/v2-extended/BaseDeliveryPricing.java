package v2_extended;

/**
 * v1 parity: the same distance-based delivery fee as v1's
 * DeliveryFeeStrategy (base $5 plus $2 per unit of distance).
 */
public class BaseDeliveryPricing implements PricingStrategyV2 {
    private static final double BASE_FEE = 5.0;
    private static final double PER_KM_FEE = 2.0;

    @Override
    public double calculatePrice(OrderV2 order) {
        double distance = calculateDistance(
            order.getRestaurantLatitude(), order.getRestaurantLongitude(),
            order.getCustomer().getLatitude(), order.getCustomer().getLongitude()
        );
        return BASE_FEE + (distance * PER_KM_FEE);
    }

    private double calculateDistance(double lat1, double lon1, double lat2, double lon2) {
        return Math.sqrt(Math.pow(lat1 - lat2, 2) + Math.pow(lon1 - lon2, 2));
    }
}
