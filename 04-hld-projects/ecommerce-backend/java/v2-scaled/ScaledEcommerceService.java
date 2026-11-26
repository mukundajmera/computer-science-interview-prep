/**
 * E-commerce Backend - V2 Scaled Implementation
 * 
 * Adds Redis caching, Elasticsearch search, async order processing,
 * and saga pattern for distributed transactions.
 */

import java.util.*;
import java.util.concurrent.*;
import java.math.BigDecimal;
import java.time.Instant;
import java.time.Duration;

// ============================================================================
// Cached Product Service with Elasticsearch
// ============================================================================

public class CachedProductService {
    
    private final ProductRepository productRepository;
    private final Cache<String, Product> productCache;
    private final SearchIndex searchIndex;
    
    public CachedProductService(ProductRepository productRepository,
                                 Cache<String, Product> productCache,
                                 SearchIndex searchIndex) {
        this.productRepository = productRepository;
        this.productCache = productCache;
        this.searchIndex = searchIndex;
    }
    
    /**
     * Get product with cache-aside pattern.
     */
    public Product getProduct(String productId) {
        Product cached = productCache.get(productId);
        if (cached != null) {
            return cached;
        }
        
        Product product = productRepository.findById(productId);
        if (product != null) {
            productCache.put(productId, product, Duration.ofMinutes(5));
        }
        return product;
    }
    
    /**
     * Search products using Elasticsearch.
     */
    public SearchResult searchProducts(SearchRequest request) {
        return searchIndex.search(request);
    }
    
    /**
     * Invalidate product cache on update.
     */
    public void invalidateCache(String productId) {
        productCache.invalidate(productId);
    }
}

// ============================================================================
// Redis Cart Service
// ============================================================================

class RedisCartService {
    
    private final RedisClient redis;
    private final ProductService productService;
    private final int cartTtlDays = 30;
    
    public RedisCartService(RedisClient redis, ProductService productService) {
        this.redis = redis;
        this.productService = productService;
    }
    
    /**
     * Get cart from Redis.
     */
    public Cart getCart(String userId) {
        String cartKey = "cart:" + userId;
        Map<String, String> items = redis.hgetall(cartKey);
        
        Cart cart = new Cart(userId);
        for (Map.Entry<String, String> entry : items.entrySet()) {
            CartItem item = deserializeCartItem(entry.getValue());
            cart.addItem(item);
        }
        cart.recalculateTotals();
        return cart;
    }
    
    /**
     * Add item to cart atomically.
     */
    public Cart addItem(String userId, String productId, int quantity) {
        String cartKey = "cart:" + userId;
        
        // Get product details
        Product product = productService.getProduct(productId);
        if (product == null) {
            throw new ProductNotFoundException(productId);
        }
        
        // Check existing quantity
        String existing = redis.hget(cartKey, productId);
        int newQuantity = quantity;
        if (existing != null) {
            CartItem existingItem = deserializeCartItem(existing);
            newQuantity += existingItem.getQuantity();
        }
        
        // Update cart
        CartItem item = new CartItem(productId, newQuantity, product.getPrice());
        redis.hset(cartKey, productId, serializeCartItem(item));
        redis.expire(cartKey, cartTtlDays * 24 * 3600);
        
        return getCart(userId);
    }
    
    /**
     * Remove item from cart.
     */
    public Cart removeItem(String userId, String productId) {
        String cartKey = "cart:" + userId;
        redis.hdel(cartKey, productId);
        return getCart(userId);
    }
    
    /**
     * Clear cart after successful order.
     */
    public void clearCart(String userId) {
        String cartKey = "cart:" + userId;
        redis.del(cartKey);
    }
    
    private String serializeCartItem(CartItem item) {
        return String.format("%s:%d:%s", 
            item.getProductId(), item.getQuantity(), item.getUnitPrice().toString());
    }
    
    private CartItem deserializeCartItem(String data) {
        String[] parts = data.split(":");
        return new CartItem(parts[0], Integer.parseInt(parts[1]), new BigDecimal(parts[2]));
    }
}

// ============================================================================
// Saga-based Order Service
// ============================================================================

class SagaOrderService {
    
    private final OrderRepository orderRepository;
    private final RedisCartService cartService;
    private final InventoryService inventoryService;
    private final PaymentService paymentService;
    private final MessageQueue messageQueue;
    private final SagaOrchestrator sagaOrchestrator;
    
    public SagaOrderService(OrderRepository orderRepository,
                            RedisCartService cartService,
                            InventoryService inventoryService,
                            PaymentService paymentService,
                            MessageQueue messageQueue) {
        this.orderRepository = orderRepository;
        this.cartService = cartService;
        this.inventoryService = inventoryService;
        this.paymentService = paymentService;
        this.messageQueue = messageQueue;
        this.sagaOrchestrator = new SagaOrchestrator();
    }
    
    /**
     * Create order using saga pattern.
     */
    public CompletableFuture<Order> createOrderAsync(String userId, CreateOrderRequest request) {
        return CompletableFuture.supplyAsync(() -> {
            // Get cart
            Cart cart = cartService.getCart(userId);
            if (cart.getItems().isEmpty()) {
                throw new EmptyCartException();
            }
            
            // Create order
            Order order = createPendingOrder(userId, cart, request);
            orderRepository.save(order);
            
            // Execute saga
            String sagaId = "saga_" + order.getOrderId();
            OrderSaga saga = new OrderSaga(sagaId, order, cart);
            
            try {
                // Step 1: Reserve inventory
                saga.reserveInventory(inventoryService);
                
                // Step 2: Process payment
                saga.processPayment(paymentService);
                
                // Step 3: Commit inventory
                saga.commitInventory(inventoryService);
                
                // Step 4: Confirm order
                order.setStatus(OrderStatus.CONFIRMED);
                orderRepository.save(order);
                
                // Step 5: Clear cart
                cartService.clearCart(userId);
                
                // Step 6: Send notification
                messageQueue.publish("order-notifications", new OrderConfirmedEvent(order));
                
                return order;
                
            } catch (Exception e) {
                // Execute compensating transactions
                saga.compensate(inventoryService, paymentService);
                order.setStatus(OrderStatus.CANCELLED);
                orderRepository.save(order);
                throw e;
            }
        });
    }
    
    private Order createPendingOrder(String userId, Cart cart, CreateOrderRequest request) {
        Order order = new Order();
        order.setOrderId("ord_" + UUID.randomUUID().toString().substring(0, 12));
        order.setUserId(userId);
        order.setStatus(OrderStatus.PENDING_PAYMENT);
        order.setItems(convertCartItems(cart.getItems()));
        order.setSubtotal(cart.getSubtotal());
        order.setTax(cart.getSubtotal().multiply(new BigDecimal("0.08")));
        order.setTotal(order.getSubtotal().add(order.getTax()));
        order.setCreatedAt(Instant.now());
        return order;
    }
    
    private List<OrderItem> convertCartItems(List<CartItem> cartItems) {
        List<OrderItem> orderItems = new ArrayList<>();
        for (CartItem ci : cartItems) {
            orderItems.add(new OrderItem(ci.getProductId(), ci.getQuantity(), ci.getUnitPrice()));
        }
        return orderItems;
    }
}

/**
 * Order saga for managing distributed transaction.
 */
class OrderSaga {
    
    private final String sagaId;
    private final Order order;
    private final Cart cart;
    private String reservationId;
    private String paymentId;
    private SagaState state;
    
    public OrderSaga(String sagaId, Order order, Cart cart) {
        this.sagaId = sagaId;
        this.order = order;
        this.cart = cart;
        this.state = SagaState.STARTED;
    }
    
    public void reserveInventory(InventoryService inventoryService) {
        reservationId = "res_" + order.getOrderId();
        inventoryService.reserve(reservationId, order.getItems());
        state = SagaState.INVENTORY_RESERVED;
    }
    
    public void processPayment(PaymentService paymentService) {
        PaymentResult result = paymentService.processPayment(
            order.getOrderId(), order.getTotal(), order.getPaymentMethodId()
        );
        if (!result.isSuccessful()) {
            throw new PaymentFailedException(result.getFailureReason());
        }
        paymentId = result.getPaymentId();
        state = SagaState.PAYMENT_PROCESSED;
    }
    
    public void commitInventory(InventoryService inventoryService) {
        inventoryService.commit(reservationId);
        state = SagaState.INVENTORY_COMMITTED;
    }
    
    public void compensate(InventoryService inventoryService, PaymentService paymentService) {
        // Compensating actions in reverse order
        if (state.ordinal() >= SagaState.PAYMENT_PROCESSED.ordinal()) {
            paymentService.refund(order.getOrderId());
        }
        if (state.ordinal() >= SagaState.INVENTORY_RESERVED.ordinal()) {
            inventoryService.release(reservationId);
        }
    }
    
    enum SagaState {
        STARTED, INVENTORY_RESERVED, PAYMENT_PROCESSED, INVENTORY_COMMITTED, COMPLETED
    }
}

// ============================================================================
// Optimistic Locking Inventory Service
// ============================================================================

class OptimisticLockingInventoryService {
    
    private final InventoryRepository inventoryRepository;
    private final Cache<String, Integer> hotInventoryCache;
    private final int maxRetries = 3;
    
    public OptimisticLockingInventoryService(InventoryRepository inventoryRepository,
                                              Cache<String, Integer> hotInventoryCache) {
        this.inventoryRepository = inventoryRepository;
        this.hotInventoryCache = hotInventoryCache;
    }
    
    /**
     * Reserve inventory with optimistic locking and retry.
     */
    public InventoryReservation reserve(String reservationId, List<OrderItem> items) {
        for (int attempt = 0; attempt < maxRetries; attempt++) {
            try {
                return attemptReservation(reservationId, items);
            } catch (OptimisticLockException e) {
                if (attempt == maxRetries - 1) {
                    throw new InventoryConflictException("Failed after " + maxRetries + " attempts");
                }
                // Exponential backoff
                try {
                    Thread.sleep((long) (Math.pow(2, attempt) * 10));
                } catch (InterruptedException ie) {
                    Thread.currentThread().interrupt();
                    throw new RuntimeException(ie);
                }
            }
        }
        throw new InventoryConflictException("Unexpected state");
    }
    
    private InventoryReservation attemptReservation(String reservationId, 
                                                     List<OrderItem> items) {
        // Check all items first
        Map<String, Inventory> inventories = new HashMap<>();
        for (OrderItem item : items) {
            Inventory inv = inventoryRepository.findByProductId(item.getProductId());
            if (inv == null || inv.getAvailableQuantity() < item.getQuantity()) {
                throw new InsufficientInventoryException(item.getProductId());
            }
            inventories.put(item.getProductId(), inv);
        }
        
        // Try to update all with optimistic locking
        for (OrderItem item : items) {
            Inventory inv = inventories.get(item.getProductId());
            int expectedVersion = inv.getVersion();
            
            inv.setAvailableQuantity(inv.getAvailableQuantity() - item.getQuantity());
            inv.setReservedQuantity(inv.getReservedQuantity() + item.getQuantity());
            inv.setVersion(expectedVersion + 1);
            
            boolean updated = inventoryRepository.updateWithVersion(inv, expectedVersion);
            if (!updated) {
                throw new OptimisticLockException("Version conflict for " + item.getProductId());
            }
            
            // Invalidate cache
            hotInventoryCache.invalidate(item.getProductId());
        }
        
        // Create reservation record
        InventoryReservation reservation = new InventoryReservation(
            reservationId, items, ReservationStatus.ACTIVE,
            Instant.now().plusSeconds(600)
        );
        inventoryRepository.saveReservation(reservation);
        
        return reservation;
    }
}

// ============================================================================
// Async Order Event Processor
// ============================================================================

class OrderEventProcessor {
    
    private final MessageQueue messageQueue;
    private final NotificationService notificationService;
    private final ExecutorService executor;
    
    public OrderEventProcessor(MessageQueue messageQueue, 
                               NotificationService notificationService,
                               int numWorkers) {
        this.messageQueue = messageQueue;
        this.notificationService = notificationService;
        this.executor = Executors.newFixedThreadPool(numWorkers);
    }
    
    public void start() {
        for (int i = 0; i < Runtime.getRuntime().availableProcessors(); i++) {
            executor.submit(this::processEvents);
        }
    }
    
    private void processEvents() {
        while (!Thread.currentThread().isInterrupted()) {
            try {
                List<OrderEvent> events = messageQueue.pollBatch("order-notifications", 10);
                for (OrderEvent event : events) {
                    processEvent(event);
                }
            } catch (Exception e) {
                // Log and continue
            }
        }
    }
    
    private void processEvent(OrderEvent event) {
        if (event instanceof OrderConfirmedEvent) {
            OrderConfirmedEvent confirmed = (OrderConfirmedEvent) event;
            notificationService.sendOrderConfirmation(confirmed.getOrder());
        } else if (event instanceof OrderShippedEvent) {
            OrderShippedEvent shipped = (OrderShippedEvent) event;
            notificationService.sendShippingNotification(shipped.getOrder());
        }
    }
    
    public void shutdown() {
        executor.shutdown();
    }
}

// ============================================================================
// Supporting Classes and Interfaces
// ============================================================================

interface Cache<K, V> {
    V get(K key);
    void put(K key, V value, Duration ttl);
    void invalidate(K key);
}

interface SearchIndex {
    SearchResult search(SearchRequest request);
}

interface RedisClient {
    Map<String, String> hgetall(String key);
    String hget(String key, String field);
    void hset(String key, String field, String value);
    void hdel(String key, String field);
    void del(String key);
    void expire(String key, int seconds);
}

interface MessageQueue {
    void publish(String topic, Object message);
    <T> List<T> pollBatch(String topic, int maxMessages);
}

interface NotificationService {
    void sendOrderConfirmation(Order order);
    void sendShippingNotification(Order order);
}

interface ProductService {
    Product getProduct(String productId);
}

interface InventoryService {
    void reserve(String reservationId, List<OrderItem> items);
    void commit(String reservationId);
    void release(String reservationId);
}

interface PaymentService {
    PaymentResult processPayment(String orderId, BigDecimal amount, String paymentMethodId);
    void refund(String orderId);
}

class SearchRequest {
    private String query;
    private Map<String, String> filters;
    private int page;
    private int limit;
    
    public String getQuery() { return query; }
}

class SearchResult {
    private List<Product> products;
    private int totalCount;
    private Map<String, List<FacetValue>> facets;
}

class FacetValue {
    private String name;
    private int count;
}

class OrderEvent {}

class OrderConfirmedEvent extends OrderEvent {
    private Order order;
    public OrderConfirmedEvent(Order order) { this.order = order; }
    public Order getOrder() { return order; }
}

class OrderShippedEvent extends OrderEvent {
    private Order order;
    public OrderShippedEvent(Order order) { this.order = order; }
    public Order getOrder() { return order; }
}

// Import from v1
class Product { 
    private BigDecimal price;
    public BigDecimal getPrice() { return price; }
}

class Cart {
    private String userId;
    private List<CartItem> items = new ArrayList<>();
    private BigDecimal subtotal = BigDecimal.ZERO;
    
    public Cart(String userId) { this.userId = userId; }
    public List<CartItem> getItems() { return items; }
    public void addItem(CartItem item) { items.add(item); }
    public BigDecimal getSubtotal() { return subtotal; }
    public void recalculateTotals() {
        subtotal = items.stream().map(CartItem::getSubtotal).reduce(BigDecimal.ZERO, BigDecimal::add);
    }
}

class CartItem {
    private String productId;
    private int quantity;
    private BigDecimal unitPrice;
    
    public CartItem(String productId, int quantity, BigDecimal unitPrice) {
        this.productId = productId;
        this.quantity = quantity;
        this.unitPrice = unitPrice;
    }
    
    public String getProductId() { return productId; }
    public int getQuantity() { return quantity; }
    public BigDecimal getUnitPrice() { return unitPrice; }
    public BigDecimal getSubtotal() { return unitPrice.multiply(new BigDecimal(quantity)); }
}

class Order {
    private String orderId;
    private String userId;
    private OrderStatus status;
    private List<OrderItem> items;
    private BigDecimal subtotal, tax, total;
    private String paymentMethodId;
    private Instant createdAt;
    
    public String getOrderId() { return orderId; }
    public void setOrderId(String id) { this.orderId = id; }
    public void setUserId(String id) { this.userId = id; }
    public OrderStatus getStatus() { return status; }
    public void setStatus(OrderStatus s) { this.status = s; }
    public List<OrderItem> getItems() { return items; }
    public void setItems(List<OrderItem> i) { this.items = i; }
    public BigDecimal getSubtotal() { return subtotal; }
    public void setSubtotal(BigDecimal s) { this.subtotal = s; }
    public BigDecimal getTax() { return tax; }
    public void setTax(BigDecimal t) { this.tax = t; }
    public BigDecimal getTotal() { return total; }
    public void setTotal(BigDecimal t) { this.total = t; }
    public String getPaymentMethodId() { return paymentMethodId; }
    public void setCreatedAt(Instant t) { this.createdAt = t; }
}

class OrderItem {
    private String productId;
    private int quantity;
    private BigDecimal unitPrice;
    
    public OrderItem(String productId, int quantity, BigDecimal unitPrice) {
        this.productId = productId;
        this.quantity = quantity;
        this.unitPrice = unitPrice;
    }
    
    public String getProductId() { return productId; }
    public int getQuantity() { return quantity; }
}

class Inventory {
    private int availableQuantity;
    private int reservedQuantity;
    private int version;
    
    public int getAvailableQuantity() { return availableQuantity; }
    public void setAvailableQuantity(int q) { this.availableQuantity = q; }
    public int getReservedQuantity() { return reservedQuantity; }
    public void setReservedQuantity(int q) { this.reservedQuantity = q; }
    public int getVersion() { return version; }
    public void setVersion(int v) { this.version = v; }
}

class InventoryReservation {
    private String reservationId;
    private List<OrderItem> items;
    private ReservationStatus status;
    private Instant expiresAt;
    
    public InventoryReservation(String id, List<OrderItem> items, ReservationStatus status, Instant expires) {
        this.reservationId = id;
        this.items = items;
        this.status = status;
        this.expiresAt = expires;
    }
}

class PaymentResult {
    private String paymentId;
    private boolean successful;
    private String failureReason;
    
    public PaymentResult(String id, boolean success, String reason) {
        this.paymentId = id;
        this.successful = success;
        this.failureReason = reason;
    }
    
    public String getPaymentId() { return paymentId; }
    public boolean isSuccessful() { return successful; }
    public String getFailureReason() { return failureReason; }
}

class CreateOrderRequest {}

enum OrderStatus {
    PENDING_PAYMENT, CONFIRMED, PROCESSING, SHIPPED, DELIVERED, CANCELLED, REFUNDED
}

enum ReservationStatus {
    ACTIVE, COMMITTED, RELEASED, EXPIRED
}

// Exceptions
class ProductNotFoundException extends RuntimeException {
    public ProductNotFoundException(String id) { super(id); }
}

class EmptyCartException extends RuntimeException {}

class InsufficientInventoryException extends RuntimeException {
    public InsufficientInventoryException(String id) { super(id); }
}

class OptimisticLockException extends RuntimeException {
    public OptimisticLockException(String msg) { super(msg); }
}

class InventoryConflictException extends RuntimeException {
    public InventoryConflictException(String msg) { super(msg); }
}

class PaymentFailedException extends RuntimeException {
    public PaymentFailedException(String msg) { super(msg); }
}

// Repositories
interface ProductRepository {
    Product findById(String productId);
}

interface OrderRepository {
    void save(Order order);
}

interface InventoryRepository {
    Inventory findByProductId(String productId);
    boolean updateWithVersion(Inventory inventory, int expectedVersion);
    void saveReservation(InventoryReservation reservation);
}
