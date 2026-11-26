import org.junit.jupiter.api.Test;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import java.util.stream.Collectors;

import static org.junit.jupiter.api.Assertions.*;

public class DistributedPriceTrackingPlatformServiceTest {

    static class InMemoryDistributedIdempotencyStore implements DistributedIdempotencyStore {
        private final Map<String, Long> claims = new HashMap<>();

        @Override
        public boolean claim(String key, long ttlMs) {
            long now = System.currentTimeMillis();
            if (claims.containsKey(key) && claims.get(key) > now) {
                return false; // Already claimed and not expired
            }
            claims.put(key, now + ttlMs);
            return true;
        }
    }

    static class InMemoryDistributedPriceTrackingPlatformService implements DistributedPriceTrackingPlatformService {
        private final DistributedIdempotencyStore idempotencyStore;
        private final Map<String, Map<String, String>> regionalData = new HashMap<>(); // region -> (id -> payload)
        private final Map<String, List<String>> regionalViews = new HashMap<>(); // region -> list of payloads

        public InMemoryDistributedPriceTrackingPlatformService(DistributedIdempotencyStore idempotencyStore) {
            this.idempotencyStore = idempotencyStore;
        }

        @Override
        public String create(String ownerId, String payload, String region) {
            String id = UUID.randomUUID().toString();
            regionalData.computeIfAbsent(region, k -> new HashMap<>()).put(id, payload);
            regionalViews.computeIfAbsent(region, k -> new ArrayList<>()).add(0, payload);
            return id;
        }

        @Override
        public void mutateWithReplayToken(String id, String mutationPayload, String idempotencyKey, String replayToken) {
            if (!idempotencyStore.claim(idempotencyKey, 60000)) {
                return; // Duplicate
            }
            
            // For testing, we just update all regions that have this id
            for (String region : regionalData.keySet()) {
                if (regionalData.get(region).containsKey(id)) {
                    regionalData.get(region).put(id, mutationPayload);
                    regionalViews.get(region).add(0, mutationPayload); // Append to view for simplicity
                }
            }
        }

        @Override
        public List<String> readRegionView(String region, int limit) {
            return regionalViews.getOrDefault(region, new ArrayList<>())
                    .stream().limit(limit).collect(Collectors.toList());
        }
    }

    @Test
    public void testCreateAndReadRegionView() {
        InMemoryDistributedIdempotencyStore store = new InMemoryDistributedIdempotencyStore();
        DistributedPriceTrackingPlatformService service = new InMemoryDistributedPriceTrackingPlatformService(store);
        
        service.create("user1", "payload-us-1", "us-east");
        service.create("user2", "payload-eu-1", "eu-west");
        service.create("user1", "payload-us-2", "us-east");
        
        List<String> usView = service.readRegionView("us-east", 5);
        assertEquals(2, usView.size());
        assertEquals("payload-us-2", usView.get(0));
        
        List<String> euView = service.readRegionView("eu-west", 5);
        assertEquals(1, euView.size());
        assertEquals("payload-eu-1", euView.get(0));
    }

    @Test
    public void testMutateWithReplayToken() {
        InMemoryDistributedIdempotencyStore store = new InMemoryDistributedIdempotencyStore();
        DistributedPriceTrackingPlatformService service = new InMemoryDistributedPriceTrackingPlatformService(store);
        
        String id = service.create("user1", "payload1", "us-east");
        service.mutateWithReplayToken(id, "payload1-mutated", "idem1", "token1");
        
        List<String> usView = service.readRegionView("us-east", 1);
        assertEquals(1, usView.size());
        assertEquals("payload1-mutated", usView.get(0));
    }

    @Test
    public void testMutateWithReplayTokenIdempotency() {
        InMemoryDistributedIdempotencyStore store = new InMemoryDistributedIdempotencyStore();
        DistributedPriceTrackingPlatformService service = new InMemoryDistributedPriceTrackingPlatformService(store);
        
        String id = service.create("user1", "payload1", "us-east");
        service.mutateWithReplayToken(id, "payload1-mutated", "idem1", "token1");
        service.mutateWithReplayToken(id, "payload1-mutated-again", "idem1", "token2"); // Ignored
        
        List<String> usView = service.readRegionView("us-east", 2); // gets the original and first mutation
        assertEquals("payload1-mutated", usView.get(0));
    }
}
