import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

import java.util.List;

public class SimpleServiceRegistryTest {

    private SimpleServiceRegistry registry;

    @BeforeEach
    public void setUp() {
        registry = new SimpleServiceRegistry();
    }

    @Test
    public void testRegisterAndDiscover() {
        registry.register("auth-service", "192.168.1.10", 9000);
        registry.register("auth-service", "192.168.1.11", 9000);
        registry.register("payment-service", "192.168.1.12", 9001);

        List<SimpleServiceRegistry.ServiceInstance> authInstances = registry.discover("auth-service");
        assertEquals(2, authInstances.size());
        
        boolean found10 = false;
        boolean found11 = false;
        for (SimpleServiceRegistry.ServiceInstance instance : authInstances) {
            if (instance.host.equals("192.168.1.10") && instance.port == 9000) found10 = true;
            if (instance.host.equals("192.168.1.11") && instance.port == 9000) found11 = true;
        }
        assertTrue(found10);
        assertTrue(found11);

        List<SimpleServiceRegistry.ServiceInstance> paymentInstances = registry.discover("payment-service");
        assertEquals(1, paymentInstances.size());
        assertEquals("192.168.1.12", paymentInstances.get(0).host);
        assertEquals(9001, paymentInstances.get(0).port);

        // Discovering unknown service returns empty list
        List<SimpleServiceRegistry.ServiceInstance> unknownInstances = registry.discover("unknown-service");
        assertTrue(unknownInstances.isEmpty());
    }

    @Test
    public void testDeregister() {
        registry.register("auth-service", "192.168.1.10", 9000);
        registry.register("auth-service", "192.168.1.11", 9000);

        // Deregister one instance
        registry.deregister("auth-service", "192.168.1.10", 9000);
        List<SimpleServiceRegistry.ServiceInstance> authInstances = registry.discover("auth-service");
        assertEquals(1, authInstances.size());
        assertEquals("192.168.1.11", authInstances.get(0).host);
        assertEquals(9000, authInstances.get(0).port);

        // Deregister a non-existent instance does nothing
        registry.deregister("auth-service", "192.168.1.10", 9000);
        assertEquals(1, registry.discover("auth-service").size());

        // Deregister a non-existent service does nothing
        registry.deregister("unknown-service", "192.168.1.10", 9000);
        assertEquals(1, registry.discover("auth-service").size());
    }

    @Test
    public void testDiscoverOne() {
        registry.register("auth-service", "192.168.1.10", 9000);

        SimpleServiceRegistry.ServiceInstance instance = registry.discoverOne("auth-service");
        assertEquals("192.168.1.10", instance.host);
        assertEquals(9000, instance.port);

        // Test exception on unknown service
        Exception exception = assertThrows(RuntimeException.class, () -> {
            registry.discoverOne("unknown-service");
        });
        assertTrue(exception.getMessage().contains("No instances found for: unknown-service"));
    }
}
