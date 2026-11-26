package v1_basic.strategies;

import v1_basic.models.Order;

public class DeliveryFeeStrategy {
    private static final double BASE_FEE = 5.0;
    private static final double PER_KM_FEE = 2.0;

    public double calculateFee(Order order) {
        double distance = calculateDistance(
            order.getRestaurantLatitude(), order.getRestaurantLongitude(),
            order.getCustomer().getLatitude(), order.getCustomer().getLongitude()
        );
        return BASE_FEE + (distance * PER_KM_FEE);
    }

    private double calculateDistance(double lat1, double lon1, double lat2, double lon2) {
        // Simplified Euclidean distance for demo purposes
        return Math.sqrt(Math.pow(lat1 - lat2, 2) + Math.pow(lon1 - lon2, 2));
    }
}
