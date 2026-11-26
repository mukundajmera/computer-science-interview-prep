/**
 * Quick Commerce Delivery - V3 Distributed
 * Skeleton for regional routing, order orchestration, and reconciliation.
 */

import java.util.Map;

public class RegionalOrderOrchestrator {

    public interface RegionRouter {
        String readRegion(double lat, double lng);
        String writeRegion(double lat, double lng);
    }

    public interface ReservationEngine {
        boolean reserve(String region, String orderId);
        void release(String region, String orderId);
    }

    public interface EventBus {
        void publish(String topic, Map<String, String> payload);
    }


    private RegionRouter router;
    private ReservationEngine reservationEngine;
    private EventBus eventBus;
    private Map<String, String> orderRegions = new java.util.concurrent.ConcurrentHashMap<>();

    public RegionalOrderOrchestrator() {}

    public RegionalOrderOrchestrator(RegionRouter router, ReservationEngine reservationEngine, EventBus eventBus) {
        this.router = router;
        this.reservationEngine = reservationEngine;
        this.eventBus = eventBus;
    }

    public String createRegionalOrder(String userId, double lat, double lng, String requestId) {

        String region = router.writeRegion(lat, lng);
        if ("unknown".equals(region)) {
            throw new IllegalStateException("Unknown region for location");
        }

        String orderId = requestId != null ? requestId : java.util.UUID.randomUUID().toString();
        if (!reservationEngine.reserve(region, orderId)) {
            throw new IllegalStateException("Reservation failed in region: " + region);
        }

        orderRegions.put(orderId, region);
        return orderId;
    }

    public void reconcileFailedOrder(String orderId, String reason) {
        String region = orderRegions.get(orderId);
        if (region != null) {
            reservationEngine.release(region, orderId);
            Map<String, String> payload = new java.util.HashMap<>();
            payload.put("orderId", orderId);
            payload.put("reason", reason);
            payload.put("region", region);
            eventBus.publish("order_failed", payload);
            orderRegions.remove(orderId);
        }
    }
}

