import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

import java.math.BigDecimal;
import java.time.Instant;
import java.util.*;

import static org.junit.jupiter.api.Assertions.*;

public class EcommerceServiceTest {

    // Mock Repositories
    static class MockProductRepository implements ProductRepository {
        Map<String, Product> products = new HashMap<>();

        @Override
        public Product findById(String productId) {
            return products.get(productId);
        }

        @Override
        public List<Product> searchByName(String query, int page, int limit) {
            List<Product> result = new ArrayList<>();
            for (Product p : products.values()) {
                // Assuming reflection is needed to check name since there is no getName() in Product
                // But we don't have to test searchByName for our use cases.
            }
            return result;
        }

        @Override
        public List<Product> findByCategory(String categoryId, int page, int limit) {
            return new ArrayList<>();
        }
        
        public void addProduct(String id, BigDecimal price) {
            Product p = new Product() {
                @Override public String getProductId() { return id; }
                @Override public BigDecimal getPrice() { return price; }
            };
            products.put(id, p);
        }
    }

    static class MockCartRepository implements CartRepository {
        Map<String, Cart> carts = new HashMap<>();

        @Override
        public Cart findByUserId(String userId) {
            return carts.get(userId);
        }

        @Override
        public void save(Cart cart) {
            // Need to get user_id, assuming we use reflection if no getter
            // Actually Cart does not have getUserId(). We'll just assume one cart for the test user to avoid reflection.
            carts.put("test_user", cart);
        }
    }

    static class MockInventoryRepository implements InventoryRepository {
        Map<String, Inventory> inventories = new HashMap<>();
        Map<String, InventoryReservation> reservations = new HashMap<>();

        @Override
        public Inventory findByProductId(String productId) {
            return inventories.get(productId);
        }

        @Override
        public void save(Inventory inventory) {
            // we will use a workaround, in reality we should access private fields
            // but we can just use the memory reference since we populate it manually in setup.
            // No action needed for in-memory mock if object references are mutated directly.
        }

        @Override
        public InventoryReservation findReservation(String reservationId) {
            return reservations.get(reservationId);
        }

        @Override
        public void saveReservation(InventoryReservation reservation) {
            // Workaround for missing getReservationId
            try { java.lang.reflect.Field f = InventoryReservation.class.getDeclaredField("reservationId"); f.setAccessible(true); String id = (String) f.get(reservation); reservations.put(id, reservation); } catch (Exception e) {}
        }
    }

    static class MockOrderRepository implements OrderRepository {
        Map<String, Order> orders = new HashMap<>();

        @Override
        public void save(Order order) {
            orders.put(order.getOrderId(), order);
        }

        @Override
        public Order findById(String orderId) {
            return orders.get(orderId);
        }

        @Override
        public List<Order> findByUserId(String userId, int page, int limit) {
            List<Order> result = new ArrayList<>();
            for (Order o : orders.values()) {
                if (userId.equals(o.getUserId())) result.add(o);
            }
            return result;
        }
    }

    static class MockPaymentService implements PaymentService {
        @Override
        public PaymentResult processPayment(String orderId, BigDecimal amount, String paymentMethodId) {
            return new PaymentResult("pay_1", true, null);
        }

        @Override
        public void refund(String orderId) {
        }
    }

    private BasicCartService cartService;
    private BasicInventoryService inventoryService;
    private BasicOrderService orderService;
    private MockProductRepository productRepo;
    private MockCartRepository cartRepo;
    private MockInventoryRepository inventoryRepo;
    private MockOrderRepository orderRepo;
    private MockPaymentService paymentService;

    @BeforeEach
    void setUp() {
        productRepo = new MockProductRepository();
        cartRepo = new MockCartRepository();
        inventoryRepo = new MockInventoryRepository();
        orderRepo = new MockOrderRepository();
        paymentService = new MockPaymentService();

        cartService = new BasicCartService(cartRepo, productRepo);
        inventoryService = new BasicInventoryService(inventoryRepo);
        orderService = new BasicOrderService(orderRepo, cartService, inventoryService, paymentService);
    }

    @Test
    void testAddToCartCalculatesSubtotal() {
        String userId = "test_user";
        String productId = "prod_1";
        productRepo.addProduct(productId, new BigDecimal("100.00"));

        Cart cart = cartService.addItem(userId, productId, 2);
        
        assertEquals(1, cart.getItems().size());
        assertEquals(2, cart.getItems().get(0).getQuantity());
        // Since getSubtotal is missing on Cart in the class definition provided, we'll test the item subtotal
        // wait, let's use reflection to read private field
        try {
            java.lang.reflect.Field field = Cart.class.getDeclaredField("subtotal");
            field.setAccessible(true);
            BigDecimal subtotal = (BigDecimal) field.get(cart);
            assertEquals(new BigDecimal("200.00"), subtotal);
        } catch (Exception e) {
            fail("Failed to read subtotal via reflection");
        }
    }

    @Test
    void testInventoryReserve() {
        String productId = "prod_1";
        Inventory inv = new Inventory();
        try {
            java.lang.reflect.Field f = Inventory.class.getDeclaredField("productId");
            f.setAccessible(true);
            f.set(inv, productId);
        } catch (Exception e) {}
        inv.setAvailableQuantity(10);
        inv.setReservedQuantity(0);
        inventoryRepo.inventories.put(productId, inv);

        List<OrderItem> items = new ArrayList<>();
        items.add(new OrderItem(productId, 3, new BigDecimal("100.00")));
        
        InventoryReservation reservation = inventoryService.reserve("res_1", items);
        
        assertEquals(ReservationStatus.ACTIVE, reservation.getStatus());
        assertEquals(7, inv.getAvailableQuantity());
        assertEquals(3, inv.getReservedQuantity());

        // Test insufficient
        List<OrderItem> itemsTooMany = new ArrayList<>();
        itemsTooMany.add(new OrderItem(productId, 8, new BigDecimal("100.00")));
        assertThrows(InsufficientInventoryException.class, () -> {
            inventoryService.reserve("res_2", itemsTooMany);
        });
    }

    @Test
    void testCreateOrder() {
        String userId = "test_user";
        String productId = "prod_1";
        
        productRepo.addProduct(productId, new BigDecimal("100.00"));
        
        Inventory inv = new Inventory();
        try {
            java.lang.reflect.Field f = Inventory.class.getDeclaredField("productId");
            f.setAccessible(true);
            f.set(inv, productId);
        } catch (Exception e) {}
        inv.setAvailableQuantity(10);
        inv.setReservedQuantity(0);
        inventoryRepo.inventories.put(productId, inv);
        
        cartService.addItem(userId, productId, 2);
        
        CreateOrderRequest req = new CreateOrderRequest() {
            @Override public String getShippingAddressId() { return "addr_1"; }
            @Override public String getPaymentMethodId() { return "pm_1"; }
        };
        
        Order order = orderService.createOrder(userId, req);
        
        assertNotNull(order);
        assertEquals(OrderStatus.CONFIRMED, order.getStatus());
        assertEquals(new BigDecimal("200.00"), order.getSubtotal());
        assertEquals(0, new BigDecimal("16.00").compareTo(order.getTax())); // 8%
        assertEquals(0, new BigDecimal("216.00").compareTo(order.getTotal()));
        
        // Cart should be clear
        Cart cart = cartService.getCart(userId);
        assertTrue(cart.getItems().isEmpty());
        
        // Inventory should be committed (reserved reduced, available remains the same as post-reserve)
        assertEquals(8, inv.getAvailableQuantity());
        assertEquals(0, inv.getReservedQuantity());
    }
}
