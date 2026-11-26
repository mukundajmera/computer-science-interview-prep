import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.atomic.AtomicBoolean;

public class FoodDeliveryPlatform {
    private DriverManager driverManager;

    public FoodDeliveryPlatform() {
        this.driverManager = null;
    }
    
    public FoodDeliveryPlatform(DriverManager driverManager) {
        this.driverManager = driverManager;
    }

    public boolean processOrder(Order order, Restaurant restaurant, boolean restaurantAccepts, boolean stockAvailable) {
        if (!stockAvailable) {
            return false;
        }

        try {
            order.transitionState(OrderState.CREATED, OrderState.RESERVATION);
        } catch (IllegalStateException e) {
            return false;
        }

        if (!restaurantAccepts) {
            return false;
        }

        try {
            order.transitionState(OrderState.RESERVATION, OrderState.ACCEPTED);
        } catch (IllegalStateException e) {
            return false;
        }

        Driver assigned = null;
        if (driverManager != null) {
            assigned = driverManager.assignDriver(restaurant);
            if (assigned == null) {
                return false;
            }
        }

        try {
            order.transitionState(OrderState.ACCEPTED, OrderState.COURIER_DISPATCH);
            return true;
        } catch (IllegalStateException e) {
            if (assigned != null) {
                assigned.release();
            }
            return false;
        }
    }
}
