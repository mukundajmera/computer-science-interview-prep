package v2_extended;

import v1_basic.models.Courier;
import v1_basic.strategies.NearestCourierStrategy;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * v2 service over v1's with two doc-named fixes:
 *
 * 1. Idempotency keys (FOLLOW-UPS): placeOrder keys each placement, so
 *    a client retry after a timeout gets the original order back instead
 *    of a duplicate order and a second charge.
 * 2. Atomic courier assignment (PITFALLS): assignment is synchronized and
 *    re-checks that the order still has no courier, so two racing
 *    assignments cannot both succeed for one order.
 */
public class FoodDeliveryServiceV2 {
    private final List<Courier> couriers = new ArrayList<>();
    private final Map<String, OrderV2> ordersByKey = new HashMap<>();
    private final NearestCourierStrategy nearestCourierStrategy = new NearestCourierStrategy();

    public void addCourier(Courier courier) {
        couriers.add(courier);
    }

    /**
     * Returns the stored order for this key: the existing one on a retry,
     * or the newly placed one otherwise. Use wasNewlyPlaced() to tell.
     */
    public synchronized OrderV2 placeOrder(String idempotencyKey, OrderV2 order) {
        OrderV2 existing = ordersByKey.get(idempotencyKey);
        if (existing != null) {
            return existing;
        }
        ordersByKey.put(idempotencyKey, order);
        return order;
    }

    public boolean wasNewlyPlaced(String idempotencyKey, OrderV2 order) {
        return ordersByKey.get(idempotencyKey) == order;
    }

    public int orderCount() {
        return ordersByKey.size();
    }

    public OrderV2 getOrder(String idempotencyKey) {
        return ordersByKey.get(idempotencyKey);
    }

    /** Assigns the nearest available courier; at most one caller wins. */
    public synchronized boolean assignCourier(OrderV2 order) {
        if (order.getCourier() != null) {
            return false;
        }
        Courier nearest = nearestCourierStrategy.findNearestCourier(
            toV1OrderView(order), couriers);
        if (nearest != null) {
            order.setCourier(nearest);
            nearest.setAvailable(false);
            order.advance(); // PLACED -> ASSIGNED
            return true;
        }
        return false;
    }

    /** v1's NearestCourierStrategy reads a v1 Order; adapt v2's fields. */
    private v1_basic.models.Order toV1OrderView(OrderV2 order) {
        return new v1_basic.models.Order(order.getId(), order.getCustomer(),
            order.getRestaurantLatitude(), order.getRestaurantLongitude());
    }
}
