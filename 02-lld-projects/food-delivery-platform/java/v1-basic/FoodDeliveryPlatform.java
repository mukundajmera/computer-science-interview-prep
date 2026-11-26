import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.atomic.AtomicBoolean;

public class FoodDeliveryPlatform {
    private final ConcurrentHashMap<String, AtomicBoolean> driverLocks = new ConcurrentHashMap<>();

    private boolean assignDriverThreadSafe(String driverId) {
        AtomicBoolean lock = driverLocks.computeIfAbsent(driverId, k -> new AtomicBoolean(true));
        return lock.compareAndSet(true, false);
    }

    private void releaseDriverThreadSafe(String driverId) {
        AtomicBoolean lock = driverLocks.get(driverId);
        if (lock != null) {
            lock.set(true);
        }
    }

    public boolean processOrder(Order order, String driverId, boolean restaurantAccepts, boolean stockAvailable) {
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

        if (!assignDriverThreadSafe(driverId)) {
            return false;
        }

        try {
            order.transitionState(OrderState.ACCEPTED, OrderState.COURIER_DISPATCH);
            return true;
        } catch (IllegalStateException e) {
            releaseDriverThreadSafe(driverId);
            return false;
        }
    }
}
