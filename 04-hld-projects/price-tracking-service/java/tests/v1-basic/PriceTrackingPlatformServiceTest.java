import org.junit.jupiter.api.Test;
import java.util.HashMap;
import java.util.Map;
import java.util.Optional;
import java.util.UUID;
import static org.junit.jupiter.api.Assertions.*;

public class PriceTrackingPlatformServiceTest {

    static class InMemoryPriceTrackingPlatformService implements PriceTrackingPlatformService {
        private final Map<String, String> items = new HashMap<>();
        private final Map<String, String> idempotencyKeys = new HashMap<>();

        @Override
        public String create(String ownerId, String payload) {
            String id = UUID.randomUUID().toString();
            items.put(id, payload);
            return id;
        }

        @Override
        public Optional<String> getById(String id) {
            return Optional.ofNullable(items.get(id));
        }

        @Override
        public void mutate(String id, String mutationPayload, String idempotencyKey) {
            if (idempotencyKeys.containsKey(idempotencyKey)) {
                return; // Idempotent
            }
            if (items.containsKey(id)) {
                items.put(id, mutationPayload); // Simple overwrite for testing
                idempotencyKeys.put(idempotencyKey, "PROCESSED");
            }
        }
    }

    @Test
    public void testCreateAndGet() {
        PriceTrackingPlatformService service = new InMemoryPriceTrackingPlatformService();
        String id = service.create("user1", "payload1");
        assertNotNull(id);
        
        Optional<String> result = service.getById(id);
        assertTrue(result.isPresent());
        assertEquals("payload1", result.get());
    }

    @Test
    public void testMutateUpdatesPayload() {
        PriceTrackingPlatformService service = new InMemoryPriceTrackingPlatformService();
        String id = service.create("user1", "payload1");
        
        service.mutate(id, "payload2", "idem1");
        Optional<String> result = service.getById(id);
        assertTrue(result.isPresent());
        assertEquals("payload2", result.get());
    }

    @Test
    public void testMutateIdempotency() {
        PriceTrackingPlatformService service = new InMemoryPriceTrackingPlatformService();
        String id = service.create("user1", "payload1");
        
        service.mutate(id, "payload2", "idem1");
        // Should ignore second mutation with same key
        service.mutate(id, "payload3", "idem1");
        
        Optional<String> result = service.getById(id);
        assertTrue(result.isPresent());
        assertEquals("payload2", result.get());
    }
    
    @Test
    public void testGetNonExistent() {
        PriceTrackingPlatformService service = new InMemoryPriceTrackingPlatformService();
        Optional<String> result = service.getById("nonexistent");
        assertFalse(result.isPresent());
    }
}
