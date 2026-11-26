/**
 * E-commerce Backend - V3 Distributed Implementation
 * 
 * Multi-region deployment with global inventory coordination,
 * cross-region order routing, and partition tolerance.
 */

import java.util.*;
import java.util.concurrent.*;
import java.math.BigDecimal;
import java.time.Instant;
import java.time.Duration;

// ============================================================================
// Global E-commerce Platform
// ============================================================================

public class GlobalEcommercePlatform {
    
    private final Map<String, RegionService> regions;
    private final GeoRouter geoRouter;
    private final GlobalInventoryCoordinator inventoryCoordinator;
    private final CrossRegionMessaging messaging;
    private final String localRegion;
    
    public GlobalEcommercePlatform(String localRegion, List<String> allRegions,
                                    GeoRouter geoRouter,
                                    GlobalInventoryCoordinator inventoryCoordinator,
                                    CrossRegionMessaging messaging) {
        this.localRegion = localRegion;
        this.geoRouter = geoRouter;
        this.inventoryCoordinator = inventoryCoordinator;
        this.messaging = messaging;
        this.regions = new ConcurrentHashMap<>();
        
        for (String region : allRegions) {
            regions.put(region, new RegionService(region));
        }
    }
    
    /**
     * Route order to appropriate region.
     */
    public CompletableFuture<Order> createOrder(String userId, CreateOrderRequest request,
                                                 double userLat, double userLng) {
        String targetRegion = geoRouter.getOptimalRegion(userLat, userLng);
        
        if (targetRegion.equals(localRegion)) {
            return processOrderLocally(userId, request);
        } else {
            return forwardOrderToRegion(userId, request, targetRegion);
        }
    }
    
    private CompletableFuture<Order> processOrderLocally(String userId, 
                                                          CreateOrderRequest request) {
        RegionService service = regions.get(localRegion);
        return service.createOrder(userId, request);
    }
    
    private CompletableFuture<Order> forwardOrderToRegion(String userId,
                                                           CreateOrderRequest request,
                                                           String targetRegion) {
        return messaging.forwardOrder(targetRegion, userId, request);
    }
    
    /**
     * Get product with regional inventory.
     */
    public Product getProduct(String productId, String region) {
        RegionService service = regions.get(region);
        Product product = service.getProduct(productId);
        
        // Enrich with regional inventory
        int regionalStock = inventoryCoordinator.getRegionalStock(productId, region);
        product.setRegionalStock(regionalStock);
        
        return product;
    }
}

// ============================================================================
// Global Inventory Coordinator
// ============================================================================

class GlobalInventoryCoordinator {
    
    private final Map<String, RegionalInventory> regionalInventories;
    private final InventoryReplicationService replicationService;
    private final ConflictResolver conflictResolver;
    
    public GlobalInventoryCoordinator(Map<String, RegionalInventory> regionalInventories,
                                       InventoryReplicationService replicationService) {
        this.regionalInventories = regionalInventories;
        this.replicationService = replicationService;
        this.conflictResolver = new ConflictResolver();
    }
    
    /**
     * Get stock available in a specific region.
     */
    public int getRegionalStock(String productId, String region) {
        RegionalInventory inventory = regionalInventories.get(region);
        if (inventory != null) {
            return inventory.getAvailableQuantity(productId);
        }
        return 0;
    }
    
    /**
     * Get total global stock across all regions.
     */
    public int getGlobalStock(String productId) {
        return regionalInventories.values().stream()
            .mapToInt(inv -> inv.getAvailableQuantity(productId))
            .sum();
    }
    
    /**
     * Reserve inventory with cross-region coordination.
     */
    public InventoryReservation reserveGlobal(String reservationId,
                                               List<OrderItem> items,
                                               String preferredRegion) {
        // Try preferred region first
        RegionalInventory preferred = regionalInventories.get(preferredRegion);
        if (preferred != null && canFulfill(preferred, items)) {
            return preferred.reserve(reservationId, items);
        }
        
        // Try other regions
        for (Map.Entry<String, RegionalInventory> entry : regionalInventories.entrySet()) {
            if (!entry.getKey().equals(preferredRegion)) {
                RegionalInventory inv = entry.getValue();
                if (canFulfill(inv, items)) {
                    return inv.reserve(reservationId, items);
                }
            }
        }
        
        // Try split fulfillment across regions
        return attemptSplitFulfillment(reservationId, items);
    }
    
    private boolean canFulfill(RegionalInventory inventory, List<OrderItem> items) {
        for (OrderItem item : items) {
            if (inventory.getAvailableQuantity(item.getProductId()) < item.getQuantity()) {
                return false;
            }
        }
        return true;
    }
    
    private InventoryReservation attemptSplitFulfillment(String reservationId,
                                                          List<OrderItem> items) {
        // Complex split fulfillment logic
        // For now, throw exception
        throw new InsufficientGlobalInventoryException("Cannot fulfill order globally");
    }
    
    /**
     * Rebalance inventory across regions based on demand.
     */
    public void rebalanceInventory(String productId) {
        Map<String, Integer> currentStock = new HashMap<>();
        Map<String, Double> demandScore = new HashMap<>();
        
        for (String region : regionalInventories.keySet()) {
            currentStock.put(region, getRegionalStock(productId, region));
            demandScore.put(region, calculateDemandScore(productId, region));
        }
        
        // Calculate optimal distribution
        Map<String, Integer> optimalStock = calculateOptimalDistribution(
            getGlobalStock(productId), demandScore
        );
        
        // Execute transfers
        for (String region : optimalStock.keySet()) {
            int current = currentStock.get(region);
            int optimal = optimalStock.get(region);
            
            if (current < optimal) {
                // Need to transfer inventory TO this region
                int needed = optimal - current;
                transferInventory(productId, region, needed);
            }
        }
    }
    
    private double calculateDemandScore(String productId, String region) {
        // Based on recent orders, views, and seasonal patterns
        return 1.0; // Simplified
    }
    
    private Map<String, Integer> calculateOptimalDistribution(int totalStock,
                                                                Map<String, Double> demandScore) {
        double totalDemand = demandScore.values().stream().mapToDouble(d -> d).sum();
        Map<String, Integer> distribution = new HashMap<>();
        
        for (Map.Entry<String, Double> entry : demandScore.entrySet()) {
            double proportion = entry.getValue() / totalDemand;
            distribution.put(entry.getKey(), (int) (totalStock * proportion));
        }
        
        return distribution;
    }
    
    private void transferInventory(String productId, String toRegion, int quantity) {
        replicationService.scheduleTransfer(productId, toRegion, quantity);
    }
}

// ============================================================================
// Regional Inventory
// ============================================================================

class RegionalInventory {
    
    private final String region;
    private final ConcurrentMap<String, InventoryRecord> inventory;
    private final ConcurrentMap<String, InventoryReservation> reservations;
    
    public RegionalInventory(String region) {
        this.region = region;
        this.inventory = new ConcurrentHashMap<>();
        this.reservations = new ConcurrentHashMap<>();
    }
    
    public int getAvailableQuantity(String productId) {
        InventoryRecord record = inventory.get(productId);
        return record != null ? record.getAvailable() : 0;
    }
    
    public InventoryReservation reserve(String reservationId, List<OrderItem> items) {
        // Use optimistic locking
        for (OrderItem item : items) {
            InventoryRecord record = inventory.get(item.getProductId());
            if (record == null || !record.tryReserve(item.getQuantity())) {
                // Rollback previous reservations
                throw new InsufficientInventoryException(item.getProductId());
            }
        }
        
        InventoryReservation reservation = new InventoryReservation(
            reservationId, items, region, Instant.now().plusSeconds(600)
        );
        reservations.put(reservationId, reservation);
        return reservation;
    }
    
    public void commit(String reservationId) {
        InventoryReservation reservation = reservations.get(reservationId);
        if (reservation != null) {
            for (OrderItem item : reservation.getItems()) {
                InventoryRecord record = inventory.get(item.getProductId());
                if (record != null) {
                    record.commit(item.getQuantity());
                }
            }
            reservations.remove(reservationId);
        }
    }
    
    public void release(String reservationId) {
        InventoryReservation reservation = reservations.get(reservationId);
        if (reservation != null) {
            for (OrderItem item : reservation.getItems()) {
                InventoryRecord record = inventory.get(item.getProductId());
                if (record != null) {
                    record.release(item.getQuantity());
                }
            }
            reservations.remove(reservationId);
        }
    }
}

class InventoryRecord {
    private final String productId;
    private volatile int available;
    private volatile int reserved;
    private final Object lock = new Object();
    
    public InventoryRecord(String productId, int available) {
        this.productId = productId;
        this.available = available;
        this.reserved = 0;
    }
    
    public int getAvailable() { return available; }
    
    public boolean tryReserve(int quantity) {
        synchronized (lock) {
            if (available >= quantity) {
                available -= quantity;
                reserved += quantity;
                return true;
            }
            return false;
        }
    }
    
    public void commit(int quantity) {
        synchronized (lock) {
            reserved -= quantity;
        }
    }
    
    public void release(int quantity) {
        synchronized (lock) {
            reserved -= quantity;
            available += quantity;
        }
    }
}

// ============================================================================
// Cross-Region Order Routing
// ============================================================================

class CrossRegionOrderRouter {
    
    private final Map<String, RegionService> regions;
    private final CircuitBreaker circuitBreaker;
    private final FallbackStrategy fallbackStrategy;
    
    public CrossRegionOrderRouter(Map<String, RegionService> regions) {
        this.regions = regions;
        this.circuitBreaker = new CircuitBreaker(5, 30000);
        this.fallbackStrategy = new FallbackStrategy();
    }
    
    /**
     * Route order with circuit breaker and fallback.
     */
    public CompletableFuture<Order> routeOrder(String targetRegion, String userId,
                                                CreateOrderRequest request) {
        if (circuitBreaker.isOpen(targetRegion)) {
            // Use fallback region
            String fallbackRegion = fallbackStrategy.getFallback(targetRegion);
            return regions.get(fallbackRegion).createOrder(userId, request);
        }
        
        try {
            CompletableFuture<Order> result = regions.get(targetRegion)
                .createOrder(userId, request);
            circuitBreaker.recordSuccess(targetRegion);
            return result;
        } catch (Exception e) {
            circuitBreaker.recordFailure(targetRegion);
            String fallbackRegion = fallbackStrategy.getFallback(targetRegion);
            return regions.get(fallbackRegion).createOrder(userId, request);
        }
    }
}

class CircuitBreaker {
    private final int threshold;
    private final long resetTimeout;
    private final Map<String, RegionState> states = new ConcurrentHashMap<>();
    
    public CircuitBreaker(int threshold, long resetTimeout) {
        this.threshold = threshold;
        this.resetTimeout = resetTimeout;
    }
    
    public boolean isOpen(String region) {
        RegionState state = states.get(region);
        if (state == null) return false;
        
        if (state.isOpen && 
            System.currentTimeMillis() - state.lastFailure > resetTimeout) {
            state.isOpen = false;
            state.failures = 0;
        }
        return state.isOpen;
    }
    
    public void recordSuccess(String region) {
        RegionState state = states.computeIfAbsent(region, k -> new RegionState());
        state.failures = 0;
        state.isOpen = false;
    }
    
    public void recordFailure(String region) {
        RegionState state = states.computeIfAbsent(region, k -> new RegionState());
        state.failures++;
        state.lastFailure = System.currentTimeMillis();
        if (state.failures >= threshold) {
            state.isOpen = true;
        }
    }
    
    private static class RegionState {
        int failures = 0;
        long lastFailure = 0;
        boolean isOpen = false;
    }
}

class FallbackStrategy {
    private final Map<String, String> fallbacks = Map.of(
        "us-east", "us-west",
        "us-west", "us-east",
        "eu-west", "us-east",
        "ap-south", "eu-west"
    );
    
    public String getFallback(String region) {
        return fallbacks.getOrDefault(region, "us-east");
    }
}

// ============================================================================
// Event-Driven Order Sync
// ============================================================================

class OrderEventSync {
    
    private final MessageQueue messageQueue;
    private final Map<String, OrderRepository> regionalRepositories;
    private final ExecutorService syncExecutor;
    
    public OrderEventSync(MessageQueue messageQueue,
                          Map<String, OrderRepository> regionalRepositories) {
        this.messageQueue = messageQueue;
        this.regionalRepositories = regionalRepositories;
        this.syncExecutor = Executors.newFixedThreadPool(4);
    }
    
    /**
     * Publish order event for cross-region sync.
     */
    public void publishOrderEvent(Order order, String sourceRegion) {
        OrderSyncEvent event = new OrderSyncEvent(order, sourceRegion, Instant.now());
        messageQueue.publish("order-sync", event);
    }
    
    /**
     * Start consuming order sync events.
     */
    public void startSync() {
        syncExecutor.submit(this::consumeEvents);
    }
    
    private void consumeEvents() {
        while (!Thread.currentThread().isInterrupted()) {
            try {
                List<OrderSyncEvent> events = messageQueue.pollBatch("order-sync", 100);
                for (OrderSyncEvent event : events) {
                    syncToOtherRegions(event);
                }
            } catch (Exception e) {
                // Log and continue
            }
        }
    }
    
    private void syncToOtherRegions(OrderSyncEvent event) {
        for (Map.Entry<String, OrderRepository> entry : regionalRepositories.entrySet()) {
            if (!entry.getKey().equals(event.getSourceRegion())) {
                try {
                    entry.getValue().upsert(event.getOrder());
                } catch (Exception e) {
                    // Queue for retry
                }
            }
        }
    }
    
    public void shutdown() {
        syncExecutor.shutdown();
    }
}

class OrderSyncEvent {
    private final Order order;
    private final String sourceRegion;
    private final Instant timestamp;
    
    public OrderSyncEvent(Order order, String sourceRegion, Instant timestamp) {
        this.order = order;
        this.sourceRegion = sourceRegion;
        this.timestamp = timestamp;
    }
    
    public Order getOrder() { return order; }
    public String getSourceRegion() { return sourceRegion; }
}

// ============================================================================
// Supporting Classes
// ============================================================================

class GeoRouter {
    public String getOptimalRegion(double lat, double lng) {
        // Determine region based on coordinates
        if (lng < -100) return "us-west";
        if (lng < -30) return "us-east";
        if (lng < 40) return "eu-west";
        return "ap-south";
    }
}

interface GeoSearchIndex {
    List<GeoSearchHit> nearbyEntities(double lat, double lng, double radiusKm, int limit);
    void upsertPosition(String entityType, String entityId, double lat, double lng, long timestampMs);
}

class GeoSearchHit {
    private final String entityId;
    private final double distanceKm;

    public GeoSearchHit(String entityId, double distanceKm) {
        this.entityId = entityId;
        this.distanceKm = distanceKm;
    }

    public String getEntityId() { return entityId; }
    public double getDistanceKm() { return distanceKm; }
}

class RegionService {
    private final String region;
    
    public RegionService(String region) {
        this.region = region;
    }
    
    public CompletableFuture<Order> createOrder(String userId, CreateOrderRequest request) {
        // Regional order processing
        return CompletableFuture.completedFuture(new Order());
    }
    
    public Product getProduct(String productId) {
        return new Product();
    }
}

interface CrossRegionMessaging {
    CompletableFuture<Order> forwardOrder(String region, String userId, CreateOrderRequest request);
}

interface InventoryReplicationService {
    void scheduleTransfer(String productId, String toRegion, int quantity);
}

class ConflictResolver {
    // Last-write-wins or custom conflict resolution
}

interface MessageQueue {
    void publish(String topic, Object message);
    <T> List<T> pollBatch(String topic, int maxMessages);
}

interface OrderRepository {
    void upsert(Order order);
}

// Data classes
class Product {
    private int regionalStock;
    public void setRegionalStock(int stock) { this.regionalStock = stock; }
}

class Order {}

class OrderItem {
    private String productId;
    private int quantity;
    
    public String getProductId() { return productId; }
    public int getQuantity() { return quantity; }
}

class CreateOrderRequest {}

class InventoryReservation {
    private final String reservationId;
    private final List<OrderItem> items;
    private final String region;
    private final Instant expiresAt;
    
    public InventoryReservation(String reservationId, List<OrderItem> items,
                                 String region, Instant expiresAt) {
        this.reservationId = reservationId;
        this.items = items;
        this.region = region;
        this.expiresAt = expiresAt;
    }
    
    public List<OrderItem> getItems() { return items; }
}

// Exceptions
class InsufficientInventoryException extends RuntimeException {
    public InsufficientInventoryException(String productId) { 
        super("Insufficient inventory: " + productId); 
    }
}

class InsufficientGlobalInventoryException extends RuntimeException {
    public InsufficientGlobalInventoryException(String msg) { super(msg); }
}

// ============================================================================
// Pattern Integration Hooks (Real-time transport, contention, workflow durability)
// ============================================================================

enum DeliveryMode {
    POLLING,
    LONG_POLLING,
    SSE,
    WEBSOCKET
    // WebRTC can be layered for media/voice handoff when P2P is acceptable.
}

enum ContentionPolicy {
    OPTIMISTIC,
    PESSIMISTIC,
    SERIAL_QUEUE,
    DISTRIBUTED_LOCK
}

class ExecutionResult {
    private final boolean success;
    private final String checkpointId;
    private final String errorMessage;
    private final boolean retryable;

    private ExecutionResult(boolean success, String checkpointId, String errorMessage, boolean retryable) {
        this.success = success;
        this.checkpointId = checkpointId;
        this.errorMessage = errorMessage;
        this.retryable = retryable;
    }

    public static ExecutionResult success(String checkpointId) {
        return new ExecutionResult(true, checkpointId, null, false);
    }

    public static ExecutionResult failure(String checkpointId, String errorMessage, boolean retryable) {
        return new ExecutionResult(false, checkpointId, errorMessage, retryable);
    }

    public boolean isSuccess() { return success; }
    public String getCheckpointId() { return checkpointId; }
    public String getErrorMessage() { return errorMessage; }
    public boolean isRetryable() { return retryable; }
}

interface WorkflowStep {
    String name();
    ExecutionResult execute();
}

interface CompensationStep {
    String name();
    void compensate(String checkpointId);
}

interface WorkflowOrchestrator {
    ExecutionResult runStep(WorkflowStep step, String idempotencyKey, IdempotencyStore store);
    void registerCompensation(String checkpointId, CompensationStep compensationStep);
}

interface IdempotencyStore {
    boolean hasProcessed(String key);
    void markProcessed(String key, ExecutionResult result);
    Optional<ExecutionResult> getResult(String key);
}
