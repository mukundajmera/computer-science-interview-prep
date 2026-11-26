/**
 * E-commerce Backend - V1 Basic Implementation
 * 
 * Core product catalog, cart, order, and inventory functionality.
 */

import java.util.*;
import java.math.BigDecimal;
import java.time.Instant;

// ============================================================================
// Product Service
// ============================================================================

interface ProductService {
    Product getProduct(String productId);
    List<Product> searchProducts(String query, int page, int limit);
    List<Product> getProductsByCategory(String categoryId, int page, int limit);
}

class BasicProductService implements ProductService {
    
    private final ProductRepository productRepository;
    
    public BasicProductService(ProductRepository productRepository) {
        this.productRepository = productRepository;
    }
    
    @Override
    public Product getProduct(String productId) {
        return productRepository.findById(productId);
    }
    
    @Override
    public List<Product> searchProducts(String query, int page, int limit) {
        // Basic SQL LIKE search in v1
        return productRepository.searchByName(query, page, limit);
    }
    
    @Override
    public List<Product> getProductsByCategory(String categoryId, int page, int limit) {
        return productRepository.findByCategory(categoryId, page, limit);
    }
}

// ============================================================================
// Cart Service
// ============================================================================

interface CartService {
    Cart getCart(String userId);
    Cart addItem(String userId, String productId, int quantity);
    Cart updateItemQuantity(String userId, String productId, int quantity);
    Cart removeItem(String userId, String productId);
    void clearCart(String userId);
}

class BasicCartService implements CartService {
    
    private final CartRepository cartRepository;
    private final ProductRepository productRepository;
    
    public BasicCartService(CartRepository cartRepository, ProductRepository productRepository) {
        this.cartRepository = cartRepository;
        this.productRepository = productRepository;
    }
    
    @Override
    public Cart getCart(String userId) {
        Cart cart = cartRepository.findByUserId(userId);
        if (cart == null) {
            cart = new Cart(generateCartId(), userId);
            cartRepository.save(cart);
        }
        return cart;
    }
    
    @Override
    public Cart addItem(String userId, String productId, int quantity) {
        Cart cart = getCart(userId);
        Product product = productRepository.findById(productId);
        
        if (product == null) {
            throw new ProductNotFoundException(productId);
        }
        
        CartItem existingItem = cart.getItem(productId);
        if (existingItem != null) {
            existingItem.setQuantity(existingItem.getQuantity() + quantity);
        } else {
            CartItem newItem = new CartItem(productId, quantity, product.getPrice());
            cart.addItem(newItem);
        }
        
        cart.recalculateTotals();
        cartRepository.save(cart);
        return cart;
    }
    
    @Override
    public Cart updateItemQuantity(String userId, String productId, int quantity) {
        Cart cart = getCart(userId);
        
        if (quantity <= 0) {
            return removeItem(userId, productId);
        }
        
        CartItem item = cart.getItem(productId);
        if (item != null) {
            item.setQuantity(quantity);
            cart.recalculateTotals();
            cartRepository.save(cart);
        }
        return cart;
    }
    
    @Override
    public Cart removeItem(String userId, String productId) {
        Cart cart = getCart(userId);
        cart.removeItem(productId);
        cart.recalculateTotals();
        cartRepository.save(cart);
        return cart;
    }
    
    @Override
    public void clearCart(String userId) {
        Cart cart = getCart(userId);
        cart.clear();
        cartRepository.save(cart);
    }
    
    private String generateCartId() {
        return "cart_" + UUID.randomUUID().toString().substring(0, 12);
    }
}

// ============================================================================
// Inventory Service
// ============================================================================

interface InventoryService {
    boolean checkAvailability(String productId, int quantity);
    InventoryReservation reserve(String reservationId, List<OrderItem> items);
    void commit(String reservationId);
    void release(String reservationId);
}

class BasicInventoryService implements InventoryService {
    
    private final InventoryRepository inventoryRepository;
    
    public BasicInventoryService(InventoryRepository inventoryRepository) {
        this.inventoryRepository = inventoryRepository;
    }
    
    @Override
    public boolean checkAvailability(String productId, int quantity) {
        Inventory inventory = inventoryRepository.findByProductId(productId);
        return inventory != null && inventory.getAvailableQuantity() >= quantity;
    }
    
    @Override
    public synchronized InventoryReservation reserve(String reservationId, List<OrderItem> items) {
        // Check all items first
        for (OrderItem item : items) {
            if (!checkAvailability(item.getProductId(), item.getQuantity())) {
                throw new InsufficientInventoryException(item.getProductId());
            }
        }
        
        // Reserve all items
        for (OrderItem item : items) {
            Inventory inventory = inventoryRepository.findByProductId(item.getProductId());
            inventory.setAvailableQuantity(
                inventory.getAvailableQuantity() - item.getQuantity()
            );
            inventory.setReservedQuantity(
                inventory.getReservedQuantity() + item.getQuantity()
            );
            inventoryRepository.save(inventory);
        }
        
        // Create reservation record
        InventoryReservation reservation = new InventoryReservation(
            reservationId, 
            items, 
            ReservationStatus.ACTIVE,
            Instant.now().plusSeconds(600) // 10 minute expiry
        );
        inventoryRepository.saveReservation(reservation);
        
        return reservation;
    }
    
    @Override
    public void commit(String reservationId) {
        InventoryReservation reservation = inventoryRepository.findReservation(reservationId);
        if (reservation == null || reservation.getStatus() != ReservationStatus.ACTIVE) {
            throw new InvalidReservationException(reservationId);
        }
        
        // Convert reserved to committed (permanent deduction)
        for (OrderItem item : reservation.getItems()) {
            Inventory inventory = inventoryRepository.findByProductId(item.getProductId());
            inventory.setReservedQuantity(
                inventory.getReservedQuantity() - item.getQuantity()
            );
            inventoryRepository.save(inventory);
        }
        
        reservation.setStatus(ReservationStatus.COMMITTED);
        inventoryRepository.saveReservation(reservation);
    }
    
    @Override
    public void release(String reservationId) {
        InventoryReservation reservation = inventoryRepository.findReservation(reservationId);
        if (reservation == null) {
            return;
        }
        
        if (reservation.getStatus() == ReservationStatus.ACTIVE) {
            // Restore available quantity
            for (OrderItem item : reservation.getItems()) {
                Inventory inventory = inventoryRepository.findByProductId(item.getProductId());
                inventory.setAvailableQuantity(
                    inventory.getAvailableQuantity() + item.getQuantity()
                );
                inventory.setReservedQuantity(
                    inventory.getReservedQuantity() - item.getQuantity()
                );
                inventoryRepository.save(inventory);
            }
            
            reservation.setStatus(ReservationStatus.RELEASED);
            inventoryRepository.saveReservation(reservation);
        }
    }
}

// ============================================================================
// Order Service
// ============================================================================

interface OrderService {
    Order createOrder(String userId, CreateOrderRequest request);
    Order getOrder(String orderId);
    List<Order> getUserOrders(String userId, int page, int limit);
    Order cancelOrder(String orderId);
}

class BasicOrderService implements OrderService {
    
    private final OrderRepository orderRepository;
    private final CartService cartService;
    private final InventoryService inventoryService;
    private final PaymentService paymentService;
    
    public BasicOrderService(OrderRepository orderRepository, CartService cartService,
                             InventoryService inventoryService, PaymentService paymentService) {
        this.orderRepository = orderRepository;
        this.cartService = cartService;
        this.inventoryService = inventoryService;
        this.paymentService = paymentService;
    }
    
    @Override
    public Order createOrder(String userId, CreateOrderRequest request) {
        // Get cart items
        Cart cart = cartService.getCart(userId);
        if (cart.getItems().isEmpty()) {
            throw new EmptyCartException();
        }
        
        // Create order
        Order order = new Order();
        order.setOrderId(generateOrderId());
        order.setUserId(userId);
        order.setStatus(OrderStatus.PENDING_PAYMENT);
        order.setShippingAddressId(request.getShippingAddressId());
        order.setPaymentMethodId(request.getPaymentMethodId());
        
        // Convert cart items to order items
        List<OrderItem> items = new ArrayList<>();
        BigDecimal subtotal = BigDecimal.ZERO;
        for (CartItem cartItem : cart.getItems()) {
            OrderItem orderItem = new OrderItem(
                cartItem.getProductId(),
                cartItem.getQuantity(),
                cartItem.getUnitPrice()
            );
            items.add(orderItem);
            subtotal = subtotal.add(cartItem.getSubtotal());
        }
        order.setItems(items);
        order.setSubtotal(subtotal);
        order.setTax(subtotal.multiply(new BigDecimal("0.08"))); // 8% tax
        order.setTotal(order.getSubtotal().add(order.getTax()));
        order.setCreatedAt(Instant.now());
        
        orderRepository.save(order);
        
        // Reserve inventory
        String reservationId = "res_" + order.getOrderId();
        try {
            inventoryService.reserve(reservationId, items);
        } catch (InsufficientInventoryException e) {
            order.setStatus(OrderStatus.CANCELLED);
            orderRepository.save(order);
            throw e;
        }
        
        // Process payment
        try {
            PaymentResult payment = paymentService.processPayment(
                order.getOrderId(),
                order.getTotal(),
                request.getPaymentMethodId()
            );
            
            if (payment.isSuccessful()) {
                inventoryService.commit(reservationId);
                order.setStatus(OrderStatus.CONFIRMED);
                cartService.clearCart(userId);
            } else {
                inventoryService.release(reservationId);
                order.setStatus(OrderStatus.CANCELLED);
            }
        } catch (Exception e) {
            inventoryService.release(reservationId);
            order.setStatus(OrderStatus.CANCELLED);
            throw new PaymentFailedException(e.getMessage());
        }
        
        orderRepository.save(order);
        return order;
    }
    
    @Override
    public Order getOrder(String orderId) {
        return orderRepository.findById(orderId);
    }
    
    @Override
    public List<Order> getUserOrders(String userId, int page, int limit) {
        return orderRepository.findByUserId(userId, page, limit);
    }
    
    @Override
    public Order cancelOrder(String orderId) {
        Order order = orderRepository.findById(orderId);
        if (order == null) {
            throw new OrderNotFoundException(orderId);
        }
        
        if (order.getStatus() != OrderStatus.CONFIRMED && 
            order.getStatus() != OrderStatus.PROCESSING) {
            throw new OrderCancellationException("Order cannot be cancelled");
        }
        
        order.setStatus(OrderStatus.CANCELLED);
        orderRepository.save(order);
        
        // Initiate refund if payment was made
        // paymentService.refund(orderId);
        
        return order;
    }
    
    private String generateOrderId() {
        return "ord_" + UUID.randomUUID().toString().substring(0, 12);
    }
}

// ============================================================================
// Payment Service
// ============================================================================

interface PaymentService {
    PaymentResult processPayment(String orderId, BigDecimal amount, String paymentMethodId);
    void refund(String orderId);
}

class BasicPaymentService implements PaymentService {
    
    private final PaymentRepository paymentRepository;
    
    public BasicPaymentService(PaymentRepository paymentRepository) {
        this.paymentRepository = paymentRepository;
    }
    
    @Override
    public PaymentResult processPayment(String orderId, BigDecimal amount, String paymentMethodId) {
        // Create payment record
        Payment payment = new Payment();
        payment.setPaymentId("pay_" + UUID.randomUUID().toString().substring(0, 12));
        payment.setOrderId(orderId);
        payment.setAmount(amount);
        payment.setStatus(PaymentStatus.PENDING);
        payment.setCreatedAt(Instant.now());
        
        paymentRepository.save(payment);
        
        // Simulate payment processing
        // In production, call actual payment provider
        boolean success = simulatePaymentProvider(amount, paymentMethodId);
        
        if (success) {
            payment.setStatus(PaymentStatus.COMPLETED);
            payment.setCompletedAt(Instant.now());
        } else {
            payment.setStatus(PaymentStatus.FAILED);
            payment.setFailureReason("Payment declined");
        }
        
        paymentRepository.save(payment);
        
        return new PaymentResult(payment.getPaymentId(), success, payment.getFailureReason());
    }
    
    @Override
    public void refund(String orderId) {
        Payment payment = paymentRepository.findByOrderId(orderId);
        if (payment != null && payment.getStatus() == PaymentStatus.COMPLETED) {
            payment.setStatus(PaymentStatus.REFUNDED);
            paymentRepository.save(payment);
        }
    }
    
    private boolean simulatePaymentProvider(BigDecimal amount, String methodId) {
        // Simulate 95% success rate
        return Math.random() < 0.95;
    }
}

// ============================================================================
// Data Classes
// ============================================================================

class Product {
    private String productId;
    private String name;
    private String description;
    private BigDecimal price;
    private String categoryId;
    private float rating;
    private boolean inStock;
    
    public String getProductId() { return productId; }
    public BigDecimal getPrice() { return price; }
}

class Cart {
    private String cartId;
    private String userId;
    private List<CartItem> items;
    private BigDecimal subtotal;
    
    public Cart(String cartId, String userId) {
        this.cartId = cartId;
        this.userId = userId;
        this.items = new ArrayList<>();
        this.subtotal = BigDecimal.ZERO;
    }
    
    public List<CartItem> getItems() { return items; }
    
    public CartItem getItem(String productId) {
        return items.stream()
            .filter(i -> i.getProductId().equals(productId))
            .findFirst()
            .orElse(null);
    }
    
    public void addItem(CartItem item) { items.add(item); }
    
    public void removeItem(String productId) {
        items.removeIf(i -> i.getProductId().equals(productId));
    }
    
    public void clear() { items.clear(); subtotal = BigDecimal.ZERO; }
    
    public void recalculateTotals() {
        subtotal = items.stream()
            .map(CartItem::getSubtotal)
            .reduce(BigDecimal.ZERO, BigDecimal::add);
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
    public void setQuantity(int qty) { this.quantity = qty; }
    public BigDecimal getUnitPrice() { return unitPrice; }
    public BigDecimal getSubtotal() { return unitPrice.multiply(new BigDecimal(quantity)); }
}

class Order {
    private String orderId;
    private String userId;
    private OrderStatus status;
    private List<OrderItem> items;
    private BigDecimal subtotal;
    private BigDecimal tax;
    private BigDecimal total;
    private String shippingAddressId;
    private String paymentMethodId;
    private Instant createdAt;
    
    public String getOrderId() { return orderId; }
    public void setOrderId(String id) { this.orderId = id; }
    public String getUserId() { return userId; }
    public void setUserId(String id) { this.userId = id; }
    public OrderStatus getStatus() { return status; }
    public void setStatus(OrderStatus s) { this.status = s; }
    public List<OrderItem> getItems() { return items; }
    public void setItems(List<OrderItem> items) { this.items = items; }
    public BigDecimal getSubtotal() { return subtotal; }
    public void setSubtotal(BigDecimal s) { this.subtotal = s; }
    public BigDecimal getTax() { return tax; }
    public void setTax(BigDecimal t) { this.tax = t; }
    public BigDecimal getTotal() { return total; }
    public void setTotal(BigDecimal t) { this.total = t; }
    public void setShippingAddressId(String id) { this.shippingAddressId = id; }
    public void setPaymentMethodId(String id) { this.paymentMethodId = id; }
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
    private String productId;
    private int availableQuantity;
    private int reservedQuantity;
    
    public int getAvailableQuantity() { return availableQuantity; }
    public void setAvailableQuantity(int q) { this.availableQuantity = q; }
    public int getReservedQuantity() { return reservedQuantity; }
    public void setReservedQuantity(int q) { this.reservedQuantity = q; }
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
    
    public List<OrderItem> getItems() { return items; }
    public ReservationStatus getStatus() { return status; }
    public void setStatus(ReservationStatus s) { this.status = s; }
}

class Payment {
    private String paymentId;
    private String orderId;
    private BigDecimal amount;
    private PaymentStatus status;
    private String failureReason;
    private Instant createdAt;
    private Instant completedAt;
    
    public String getPaymentId() { return paymentId; }
    public void setPaymentId(String id) { this.paymentId = id; }
    public void setOrderId(String id) { this.orderId = id; }
    public void setAmount(BigDecimal a) { this.amount = a; }
    public PaymentStatus getStatus() { return status; }
    public void setStatus(PaymentStatus s) { this.status = s; }
    public String getFailureReason() { return failureReason; }
    public void setFailureReason(String r) { this.failureReason = r; }
    public void setCreatedAt(Instant t) { this.createdAt = t; }
    public void setCompletedAt(Instant t) { this.completedAt = t; }
}

class PaymentResult {
    private String paymentId;
    private boolean successful;
    private String failureReason;
    
    public PaymentResult(String paymentId, boolean successful, String failureReason) {
        this.paymentId = paymentId;
        this.successful = successful;
        this.failureReason = failureReason;
    }
    
    public boolean isSuccessful() { return successful; }
}

class CreateOrderRequest {
    private String shippingAddressId;
    private String paymentMethodId;
    
    public String getShippingAddressId() { return shippingAddressId; }
    public String getPaymentMethodId() { return paymentMethodId; }
}

enum OrderStatus {
    PENDING_PAYMENT, CONFIRMED, PROCESSING, SHIPPED, DELIVERED, CANCELLED, REFUNDED
}

enum ReservationStatus {
    ACTIVE, COMMITTED, RELEASED, EXPIRED
}

enum PaymentStatus {
    PENDING, COMPLETED, FAILED, REFUNDED
}

// Exceptions
class ProductNotFoundException extends RuntimeException {
    public ProductNotFoundException(String productId) { super("Product not found: " + productId); }
}

class InsufficientInventoryException extends RuntimeException {
    public InsufficientInventoryException(String productId) { super("Insufficient inventory: " + productId); }
}

class InvalidReservationException extends RuntimeException {
    public InvalidReservationException(String id) { super("Invalid reservation: " + id); }
}

class EmptyCartException extends RuntimeException {
    public EmptyCartException() { super("Cart is empty"); }
}

class OrderNotFoundException extends RuntimeException {
    public OrderNotFoundException(String id) { super("Order not found: " + id); }
}

class OrderCancellationException extends RuntimeException {
    public OrderCancellationException(String msg) { super(msg); }
}

class PaymentFailedException extends RuntimeException {
    public PaymentFailedException(String msg) { super(msg); }
}

// Repository Interfaces
interface ProductRepository {
    Product findById(String productId);
    List<Product> searchByName(String query, int page, int limit);
    List<Product> findByCategory(String categoryId, int page, int limit);
}

interface CartRepository {
    Cart findByUserId(String userId);
    void save(Cart cart);
}

interface InventoryRepository {
    Inventory findByProductId(String productId);
    void save(Inventory inventory);
    InventoryReservation findReservation(String reservationId);
    void saveReservation(InventoryReservation reservation);
}

interface OrderRepository {
    void save(Order order);
    Order findById(String orderId);
    List<Order> findByUserId(String userId, int page, int limit);
}

interface PaymentRepository {
    void save(Payment payment);
    Payment findByOrderId(String orderId);
}
