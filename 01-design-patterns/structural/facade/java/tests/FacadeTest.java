import org.junit.jupiter.api.*;
import static org.junit.jupiter.api.Assertions.*;
import java.util.List;
import java.util.Map;

/**
 * Tests for Facade Pattern implementations.
 */
public class FacadeTest {

    @Test
    @DisplayName("Home theater facade should expose simple movie workflow")
    void testHomeTheaterFacadeWorkflow() {
        HomeTheaterFacade theater = new HomeTheaterFacade(
            new DVDPlayer(),
            new Projector(),
            new SoundSystem(),
            new Lights()
        );

        assertDoesNotThrow(() -> theater.watchMovie("Inception"));
        assertDoesNotThrow(theater::endMovie);
    }

    @Test
    @DisplayName("Checkout facade should place order and reserve stock")
    void testCheckoutPlacesOrderAndReservesStock() {
        InventoryService inventory = new InventoryService(Map.of("book", 2));
        CheckoutFacade checkout = new CheckoutFacade(
            inventory,
            new CheckoutPaymentService(),
            new ShippingService(),
            new NotificationService()
        );

        OrderConfirmation confirmation = checkout.placeOrder(
            "book",
            1,
            20.00,
            "tok_123",
            "10 Main St",
            "reader@example.com"
        );

        assertEquals("order-book-1", confirmation.getOrderId());
        assertEquals("pay-2500", confirmation.getPaymentId());
        assertEquals(1, inventory.available("book"));
    }

    @Test
    @DisplayName("Checkout facade should reject out-of-stock item before payment")
    void testCheckoutRejectsOutOfStockItem() {
        CheckoutFacade checkout = new CheckoutFacade(
            new InventoryService(Map.of("book", 0)),
            new CheckoutPaymentService(),
            new ShippingService(),
            new NotificationService()
        );

        assertThrows(IllegalArgumentException.class, () -> checkout.placeOrder(
            "book",
            1,
            20.00,
            "tok_123",
            "10 Main St",
            "reader@example.com"
        ));
    }

    @Test
    @DisplayName("Cloud facade should coordinate deployment subsystems")
    void testCloudFacadeDeployment() {
        CloudDeploymentFacade facade = new CloudDeploymentFacade(
            new ObjectStorageService(),
            new ComputeService(),
            new QueueService(),
            new MonitoringService()
        );

        DeploymentSummary deployment = facade.deployService(
            "feed-api",
            "build/feed-api.zip",
            3
        );

        assertEquals("feed-api", deployment.getServiceName());
        assertEquals(List.of("vm-feed-api-1", "vm-feed-api-2", "vm-feed-api-3"),
            deployment.getInstanceIds());
        assertEquals("queue-feed-api", deployment.getQueueName());
        assertEquals("/dashboards/feed-api", deployment.getDashboardUrl());
    }

    @Test
    @DisplayName("Cloud facade rollback should stop compute instances")
    void testCloudFacadeRollback() {
        ComputeService compute = new ComputeService();
        CloudDeploymentFacade facade = new CloudDeploymentFacade(
            new ObjectStorageService(),
            compute,
            new QueueService(),
            new MonitoringService()
        );
        DeploymentSummary deployment = facade.deployService("feed-api", "build/feed-api.zip", 2);

        List<String> stopped = facade.rollback(deployment);

        assertEquals(List.of("vm-feed-api-1", "vm-feed-api-2"), stopped);
        assertTrue(compute.getRunningInstances().isEmpty());
    }
}
