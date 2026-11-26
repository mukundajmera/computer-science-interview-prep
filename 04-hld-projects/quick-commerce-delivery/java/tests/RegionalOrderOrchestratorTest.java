import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

import java.util.*;
import java.lang.reflect.Field;

import static org.junit.jupiter.api.Assertions.*;

public class RegionalOrderOrchestratorTest {

    static class InMemoryRegionRouter implements RegionalOrderOrchestrator.RegionRouter {
        private final Map<String, String> regionMap = new HashMap<>();

        public void setRegion(double lat, double lng, String region) {
            regionMap.put(lat + "," + lng, region);
        }

        @Override
        public String readRegion(double lat, double lng) {
            return regionMap.getOrDefault(lat + "," + lng, "unknown");
        }

        @Override
        public String writeRegion(double lat, double lng) {
            return regionMap.getOrDefault(lat + "," + lng, "unknown");
        }
    }

    static class InMemoryReservationEngine implements RegionalOrderOrchestrator.ReservationEngine {
        private final Set<String> reservations = new HashSet<>();
        private boolean shouldFail = false;

        public void setShouldFail(boolean fail) {
            this.shouldFail = fail;
        }

        @Override
        public boolean reserve(String region, String orderId) {
            if (shouldFail) return false;
            reservations.add(region + ":" + orderId);
            return true;
        }

        @Override
        public void release(String region, String orderId) {
            reservations.remove(region + ":" + orderId);
        }

        public boolean isReserved(String region, String orderId) {
            return reservations.contains(region + ":" + orderId);
        }
    }

    static class InMemoryEventBus implements RegionalOrderOrchestrator.EventBus {
        private final List<Map<String, String>> publishedEvents = new ArrayList<>();

        @Override
        public void publish(String topic, Map<String, String> payload) {
            Map<String, String> event = new HashMap<>(payload);
            event.put("_topic", topic);
            publishedEvents.add(event);
        }

        public List<Map<String, String>> getEvents() {
            return publishedEvents;
        }
    }

    private InMemoryRegionRouter router;
    private InMemoryReservationEngine engine;
    private InMemoryEventBus eventBus;
    private RegionalOrderOrchestrator orchestrator;

    @BeforeEach
    void setUp() throws Exception {
        router = new InMemoryRegionRouter();
        engine = new InMemoryReservationEngine();
        eventBus = new InMemoryEventBus();
        orchestrator = new RegionalOrderOrchestrator();

        try {
            Field routerField = RegionalOrderOrchestrator.class.getDeclaredField("router");
            routerField.setAccessible(true);
            routerField.set(orchestrator, router);

            Field engineField = RegionalOrderOrchestrator.class.getDeclaredField("reservationEngine");
            engineField.setAccessible(true);
            engineField.set(orchestrator, engine);

            Field busField = RegionalOrderOrchestrator.class.getDeclaredField("eventBus");
            busField.setAccessible(true);
            busField.set(orchestrator, eventBus);

            // Adding orderRegions tracking inside the orchestrator for testing reconciliation if not present
            try {
                Field orderRegionsField = RegionalOrderOrchestrator.class.getDeclaredField("orderRegions");
                orderRegionsField.setAccessible(true);
                // Initialize map if user did not
                if (orderRegionsField.get(orchestrator) == null) {
                    orderRegionsField.set(orchestrator, new HashMap<String, String>());
                }
            } catch (NoSuchFieldException | IllegalAccessException e) {
                // Ignore
            }

        } catch (NoSuchFieldException e) {
            // Field injection might fail on skeleton
        }
    }

    @Test
    void testCreateRegionalOrderSuccessfully() {
        router.setRegion(10.0, 20.0, "us-east-1");

        try {
            String orderId = orchestrator.createRegionalOrder("user1", 10.0, 20.0, "req1");
            assertNotNull(orderId);
            assertTrue(engine.isReserved("us-east-1", orderId));
        } catch (UnsupportedOperationException e) {
            fail("createRegionalOrder is not implemented");
        }
    }

    @Test
    void testCreateRegionalOrderFailsForUnknownRegion() {
        try {
            assertThrows(IllegalStateException.class, () -> {
                orchestrator.createRegionalOrder("user1", 10.0, 20.0, "req1");
            });
        } catch (UnsupportedOperationException e) {
            fail("createRegionalOrder is not implemented");
        }
    }

    @Test
    void testCreateRegionalOrderFailsWhenReservationFails() {
        router.setRegion(10.0, 20.0, "us-east-1");
        engine.setShouldFail(true);

        try {
            assertThrows(IllegalStateException.class, () -> {
                orchestrator.createRegionalOrder("user1", 10.0, 20.0, "req1");
            });
        } catch (UnsupportedOperationException e) {
            fail("createRegionalOrder is not implemented");
        }
    }

    @Test
    @SuppressWarnings("unchecked")
    void testReconcileFailedOrderReleasesAndPublishes() {
        router.setRegion(10.0, 20.0, "us-east-1");
        
        try {
            // First we need to inject state manually since create order might not work
            String orderId = "order123";
            try {
                Field orderRegionsField = RegionalOrderOrchestrator.class.getDeclaredField("orderRegions");
                orderRegionsField.setAccessible(true);
                Map<String, String> orderRegions = (Map<String, String>) orderRegionsField.get(orchestrator);
                if (orderRegions != null) {
                    orderRegions.put(orderId, "us-east-1");
                }
            } catch (NoSuchFieldException | IllegalAccessException e) {
                // Ignore
            }

            engine.reserve("us-east-1", orderId);

            orchestrator.reconcileFailedOrder(orderId, "payment_failed");
            
            assertFalse(engine.isReserved("us-east-1", orderId));
            
            assertEquals(1, eventBus.getEvents().size());
            Map<String, String> event = eventBus.getEvents().get(0);
            assertEquals("order_failed", event.get("_topic"));
            assertEquals(orderId, event.get("orderId"));
            assertEquals("payment_failed", event.get("reason"));
            assertEquals("us-east-1", event.get("region"));
        } catch (UnsupportedOperationException e) {
            fail("reconcileFailedOrder is not implemented");
        }
    }
}
