import org.junit.jupiter.api.Test;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import java.util.stream.Collectors;

import static org.junit.jupiter.api.Assertions.*;

public class PriceTrackingPlatformServiceV2Test {

    static class InMemoryProjectionStore implements PriceTrackingPlatformServiceProjectionStore {
        private final List<String> history = new ArrayList<>();

        @Override
        public void upsertProjection(String id, String snapshot) {
            history.add(0, snapshot);
        }

        @Override
        public List<String> recent(int limit) {
            return history.stream().limit(limit).collect(Collectors.toList());
        }
    }

    static class InMemoryPriceTrackingPlatformServiceV2 implements PriceTrackingPlatformServiceV2 {
        private final PriceTrackingPlatformServiceProjectionStore projectionStore;
        private final Map<String, String> items = new HashMap<>();
        private final Map<String, String> idempotencyKeys = new HashMap<>();

        public InMemoryPriceTrackingPlatformServiceV2(PriceTrackingPlatformServiceProjectionStore projectionStore) {
            this.projectionStore = projectionStore;
        }

        @Override
        public String create(String ownerId, String payload) {
            String id = UUID.randomUUID().toString();
            items.put(id, payload);
            projectionStore.upsertProjection(id, payload);
            return id;
        }

        @Override
        public void publishMutation(String id, String mutationPayload, String idempotencyKey) {
            if (idempotencyKeys.containsKey(idempotencyKey)) {
                return;
            }
            if (items.containsKey(id)) {
                items.put(id, mutationPayload);
                projectionStore.upsertProjection(id, mutationPayload);
                idempotencyKeys.put(idempotencyKey, "PROCESSED");
            }
        }

        @Override
        public List<String> readRecent(int limit) {
            return projectionStore.recent(limit);
        }
    }

    @Test
    public void testCreateAndReadRecent() {
        InMemoryProjectionStore store = new InMemoryProjectionStore();
        PriceTrackingPlatformServiceV2 service = new InMemoryPriceTrackingPlatformServiceV2(store);
        
        service.create("user1", "payload1");
        service.create("user1", "payload2");
        
        List<String> recent = service.readRecent(5);
        assertEquals(2, recent.size());
        assertEquals("payload2", recent.get(0)); // most recent first
        assertEquals("payload1", recent.get(1));
    }

    @Test
    public void testPublishMutation() {
        InMemoryProjectionStore store = new InMemoryProjectionStore();
        PriceTrackingPlatformServiceV2 service = new InMemoryPriceTrackingPlatformServiceV2(store);
        
        String id = service.create("user1", "payload1");
        service.publishMutation(id, "payload1-mutated", "idem1");
        
        List<String> recent = service.readRecent(1);
        assertEquals(1, recent.size());
        assertEquals("payload1-mutated", recent.get(0));
    }

    @Test
    public void testPublishMutationIdempotency() {
        InMemoryProjectionStore store = new InMemoryProjectionStore();
        PriceTrackingPlatformServiceV2 service = new InMemoryPriceTrackingPlatformServiceV2(store);
        
        String id = service.create("user1", "payload1");
        service.publishMutation(id, "payload1-mutated", "idem1");
        service.publishMutation(id, "payload1-mutated-again", "idem1"); // Should ignore
        
        List<String> recent = service.readRecent(1);
        assertEquals("payload1-mutated", recent.get(0));
    }

    @Test
    public void testReadRecentLimit() {
        InMemoryProjectionStore store = new InMemoryProjectionStore();
        PriceTrackingPlatformServiceV2 service = new InMemoryPriceTrackingPlatformServiceV2(store);
        
        service.create("user1", "p1");
        service.create("user1", "p2");
        service.create("user1", "p3");
        
        List<String> recent = service.readRecent(2);
        assertEquals(2, recent.size());
        assertEquals("p3", recent.get(0));
        assertEquals("p2", recent.get(1));
    }
}
