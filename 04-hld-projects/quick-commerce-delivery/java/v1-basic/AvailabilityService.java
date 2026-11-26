/**
 * Quick Commerce Delivery - V1 Basic
 * Skeleton for location availability lookup and order placement.
 */

import java.time.Instant;
import java.util.List;
import java.util.Optional;

public class AvailabilityService {

    public static class AvailabilityItem {
        private final String itemId;
        private final String centerId;
        private final int availableQty;
        private final int etaMinutes;

        public AvailabilityItem(String itemId, String centerId, int availableQty, int etaMinutes) {
            this.itemId = itemId;
            this.centerId = centerId;
            this.availableQty = availableQty;
            this.etaMinutes = etaMinutes;
        }

        public String getItemId() { return itemId; }
        public String getCenterId() { return centerId; }
        public int getAvailableQty() { return availableQty; }
        public int getEtaMinutes() { return etaMinutes; }
    }

    public static class OrderLine {
        private final String itemId;
        private final int qty;

        public OrderLine(String itemId, int qty) {
            this.itemId = itemId;
            this.qty = qty;
        }

        public String getItemId() { return itemId; }
        public int getQty() { return qty; }
    }

    public interface NearbyCenterResolver {
        List<String> resolve(double lat, double lng, int limit);
    }

    public interface InventoryRepository {
        List<AvailabilityItem> query(String centerId, String query, int page, int pageSize);
        boolean reserve(String centerId, List<OrderLine> lines);
    }

    public interface OrderRepository {
        String create(String userId, String centerId, List<OrderLine> lines, String idempotencyKey, Instant createdAt);
        Optional<String> findByIdempotencyKey(String idempotencyKey);
    }


    private NearbyCenterResolver resolver;
    private InventoryRepository inventoryRepository;
    private OrderRepository orderRepository;

    public AvailabilityService() {}
    
    public AvailabilityService(NearbyCenterResolver resolver, InventoryRepository inventoryRepository, OrderRepository orderRepository) {
        this.resolver = resolver;
        this.inventoryRepository = inventoryRepository;
        this.orderRepository = orderRepository;
    }

    public List<AvailabilityItem> lookup(double lat, double lng, String query, int page, int pageSize) {
        List<String> centers = resolver.resolve(lat, lng, 10);
        List<AvailabilityItem> results = new java.util.ArrayList<>();
        for (String centerId : centers) {
            List<AvailabilityItem> centerItems = inventoryRepository.query(centerId, query, page, pageSize);
            for (AvailabilityItem item : centerItems) {
                if (results.size() < pageSize) {
                    results.add(item);
                }
            }
            if (results.size() >= pageSize) break;
        }
        return results;
    }

    public String placeOrder(String userId, double lat, double lng, List<OrderLine> lines, String idempotencyKey) {

        Optional<String> existingOrder = orderRepository.findByIdempotencyKey(idempotencyKey);
        if (existingOrder.isPresent()) {
            return existingOrder.get();
        }

        List<String> centers = resolver.resolve(lat, lng, 10);
        for (String centerId : centers) {
            if (inventoryRepository.reserve(centerId, lines)) {
                return orderRepository.create(userId, centerId, lines, idempotencyKey, Instant.now());
            }
        }
        throw new IllegalStateException("Insufficient inventory in nearby centers");
    }
}

