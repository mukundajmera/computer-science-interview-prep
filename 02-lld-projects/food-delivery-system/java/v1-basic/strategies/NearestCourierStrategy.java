package v1_basic.strategies;

import v1_basic.models.Courier;
import v1_basic.models.Order;

import java.util.List;

public class NearestCourierStrategy {

    public Courier findNearestCourier(Order order, List<Courier> couriers) {
        Courier nearest = null;
        double minDistance = Double.MAX_VALUE;

        for (Courier courier : couriers) {
            if (courier.isAvailable()) {
                double distance = calculateDistance(
                    order.getRestaurantLatitude(), order.getRestaurantLongitude(),
                    courier.getLatitude(), courier.getLongitude()
                );
                if (distance < minDistance) {
                    minDistance = distance;
                    nearest = courier;
                }
            }
        }
        return nearest;
    }

    private double calculateDistance(double lat1, double lon1, double lat2, double lon2) {
        // Simplified Euclidean distance for demo purposes
        return Math.sqrt(Math.pow(lat1 - lat2, 2) + Math.pow(lon1 - lon2, 2));
    }
}
