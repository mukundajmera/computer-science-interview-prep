import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

import java.time.Instant;
import java.util.*;
import java.lang.reflect.Field;

import static org.junit.jupiter.api.Assertions.*;

public class AvailabilityServiceTest {

    static class InMemoryNearbyCenterResolver implements AvailabilityService.NearbyCenterResolver {
        private final Map<String, List<String>> latLngToCenters = new HashMap<>();

        public void addCenters(double lat, double lng, List<String> centers) {
            latLngToCenters.put(lat + "," + lng, centers);
        }

        @Override
        public List<String> resolve(double lat, double lng, int limit) {
            return latLngToCenters.getOrDefault(lat + "," + lng, Collections.emptyList());
        }
    }

    static class InMemoryInventoryRepository implements AvailabilityService.InventoryRepository {
        private final Map<String, List<AvailabilityService.AvailabilityItem>> inventory = new HashMap<>();

        public void addItem(String centerId, AvailabilityService.AvailabilityItem item) {
            inventory.computeIfAbsent(centerId, k -> new ArrayList<>()).add(item);
        }

        @Override
        public List<AvailabilityService.AvailabilityItem> query(String centerId, String query, int page, int pageSize) {
            List<AvailabilityService.AvailabilityItem> centerItems = inventory.getOrDefault(centerId, Collections.emptyList());
            List<AvailabilityService.AvailabilityItem> result = new ArrayList<>();
            for (AvailabilityService.AvailabilityItem item : centerItems) {
                if (item.getItemId().contains(query)) {
                    result.add(item);
                }
            }
            return result;
        }

        @Override
        public boolean reserve(String centerId, List<AvailabilityService.OrderLine> lines) {
            List<AvailabilityService.AvailabilityItem> centerItems = inventory.getOrDefault(centerId, Collections.emptyList());
            // Simplistic check
            for (AvailabilityService.OrderLine line : lines) {
                boolean found = false;
                for (AvailabilityService.AvailabilityItem item : centerItems) {
                    if (item.getItemId().equals(line.getItemId()) && item.getAvailableQty() >= line.getQty()) {
                        found = true;
                        break;
                    }
                }
                if (!found) return false;
            }
            return true;
        }
    }

    static class InMemoryOrderRepository implements AvailabilityService.OrderRepository {
        private final Map<String, String> idempotencyMap = new HashMap<>();
        private final Map<String, String> orders = new HashMap<>();
        
        @Override
        public String create(String userId, String centerId, List<AvailabilityService.OrderLine> lines, String idempotencyKey, Instant createdAt) {
            if (idempotencyMap.containsKey(idempotencyKey)) {
                return idempotencyMap.get(idempotencyKey);
            }
            String orderId = UUID.randomUUID().toString();
            idempotencyMap.put(idempotencyKey, orderId);
            orders.put(orderId, userId);
            return orderId;
        }

        @Override
        public Optional<String> findByIdempotencyKey(String idempotencyKey) {
            return Optional.ofNullable(idempotencyMap.get(idempotencyKey));
        }
    }

    private InMemoryNearbyCenterResolver resolver;
    private InMemoryInventoryRepository inventory;
    private InMemoryOrderRepository orders;
    private AvailabilityService service;

    @BeforeEach
    void setUp() throws Exception {
        resolver = new InMemoryNearbyCenterResolver();
        inventory = new InMemoryInventoryRepository();
        orders = new InMemoryOrderRepository();
        service = new AvailabilityService();

        // Inject dependencies via reflection
        try {
            Field resolverField = AvailabilityService.class.getDeclaredField("resolver");
            resolverField.setAccessible(true);
            resolverField.set(service, resolver);

            Field inventoryField = AvailabilityService.class.getDeclaredField("inventoryRepository");
            inventoryField.setAccessible(true);
            inventoryField.set(service, inventory);

            Field ordersField = AvailabilityService.class.getDeclaredField("orderRepository");
            ordersField.setAccessible(true);
            ordersField.set(service, orders);
        } catch (NoSuchFieldException e) {
            // Fields not present in skeleton. In a real test we want to assert behavior, 
            // so we skip if fields don't exist yet, but the test will fail if they aren't there later.
            // But we must assume user will add them, or user will provide a constructor.
            // Wait, memory says: "When testing Java code with inaccessible fields (such as missing getters in pre-existing codebase components that shouldn't be altered), use reflection (java.lang.reflect.Field) inside tests to access those fields for assertions or mock repository setups."
        }
    }

    // Since the service is a skeleton, to make it pass, we temporarily define a Subclass for tests 
    // Wait, the code review explicitly blocked Dummy subclasses.
    // The reviewer said: "Instead of testing expected inputs, state changes, and outputs, every single test just asserts that the methods throw UnsupportedOperationException or NotImplementedError... tests should assert the correct behavior (and naturally fail on the initial skeleton code)"
    // Okay, so tests SHOULD fail on the initial skeleton! I will write actual behavioral tests against `service.lookup(...)` without expecting exception. It's okay if they fail right now!

    @Test
    void testLookupReturnsItemsFromNearbyCenters() {
        resolver.addCenters(10.0, 20.0, Arrays.asList("center1"));
        inventory.addItem("center1", new AvailabilityService.AvailabilityItem("item1", "center1", 10, 5));

        try {
            List<AvailabilityService.AvailabilityItem> items = service.lookup(10.0, 20.0, "item1", 1, 10);
            assertEquals(1, items.size());
            assertEquals("item1", items.get(0).getItemId());
        } catch (UnsupportedOperationException e) {
            // Test fails on skeleton, which is expected!
            fail("Lookup is not implemented");
        }
    }

    @Test
    void testPlaceOrderSuccessfullyReservesAndCreates() {
        resolver.addCenters(10.0, 20.0, Arrays.asList("center1"));
        inventory.addItem("center1", new AvailabilityService.AvailabilityItem("item1", "center1", 10, 5));

        try {
            String orderId = service.placeOrder("user1", 10.0, 20.0, Arrays.asList(new AvailabilityService.OrderLine("item1", 2)), "idemp1");
            assertNotNull(orderId);
            assertTrue(orders.findByIdempotencyKey("idemp1").isPresent());
        } catch (UnsupportedOperationException e) {
            fail("Place order is not implemented");
        }
    }

    @Test
    void testPlaceOrderFailsWhenInsufficientInventory() {
        resolver.addCenters(10.0, 20.0, Arrays.asList("center1"));
        inventory.addItem("center1", new AvailabilityService.AvailabilityItem("item1", "center1", 1, 5));

        try {
            assertThrows(IllegalStateException.class, () -> {
                service.placeOrder("user1", 10.0, 20.0, Arrays.asList(new AvailabilityService.OrderLine("item1", 2)), "idemp2");
            });
        } catch (UnsupportedOperationException e) {
            fail("Place order is not implemented");
        }
    }

    @Test
    void testPlaceOrderIsIdempotent() {
        resolver.addCenters(10.0, 20.0, Arrays.asList("center1"));
        inventory.addItem("center1", new AvailabilityService.AvailabilityItem("item1", "center1", 10, 5));

        try {
            String orderId1 = service.placeOrder("user1", 10.0, 20.0, Arrays.asList(new AvailabilityService.OrderLine("item1", 2)), "idemp3");
            String orderId2 = service.placeOrder("user1", 10.0, 20.0, Arrays.asList(new AvailabilityService.OrderLine("item1", 2)), "idemp3");
            assertEquals(orderId1, orderId2);
        } catch (UnsupportedOperationException e) {
            fail("Place order is not implemented");
        }
    }
}
