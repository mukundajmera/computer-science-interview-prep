import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.Collections;

// Dummy implementation for v1
class InMemoryAuctionPlatformV1 implements AuctionPlatformService {
    private final Map<String, String> items = new HashMap<>();
    private int nextId = 1;
    public final List<String> mutations = new ArrayList<>();

    @Override
    public String create(String ownerId, String payload) {
        String id = String.valueOf(nextId++);
        items.put(id, payload);
        return id;
    }

    @Override
    public Optional<String> getById(String id) {
        return Optional.ofNullable(items.get(id));
    }

    @Override
    public void mutate(String id, String mutationPayload, String idempotencyKey) {
        if (items.containsKey(id)) {
            mutations.add(id + ":" + mutationPayload + ":" + idempotencyKey);
        }
    }
}

// Dummy implementation for v2
class InMemoryProjectionStore implements AuctionPlatformServiceProjectionStore {
    private final Map<String, String> projections = new HashMap<>();
    private final List<String> recentIds = new ArrayList<>();

    @Override
    public void upsertProjection(String id, String snapshot) {
        projections.put(id, snapshot);
        recentIds.remove(id);
        recentIds.add(id);
    }

    @Override
    public List<String> recent(int limit) {
        List<String> result = new ArrayList<>();
        int start = Math.max(0, recentIds.size() - limit);
        for (int i = recentIds.size() - 1; i >= start; i--) {
            result.add(projections.get(recentIds.get(i)));
        }
        return result;
    }
}

class InMemoryAuctionPlatformV2 implements AuctionPlatformServiceV2 {
    private final AuctionPlatformServiceProjectionStore projectionStore;
    private int nextId = 1;

    public InMemoryAuctionPlatformV2(AuctionPlatformServiceProjectionStore projectionStore) {
        this.projectionStore = projectionStore;
    }

    @Override
    public String create(String ownerId, String payload) {
        String id = String.valueOf(nextId++);
        projectionStore.upsertProjection(id, payload);
        return id;
    }

    @Override
    public void publishMutation(String id, String mutationPayload, String idempotencyKey) {
        projectionStore.upsertProjection(id, mutationPayload);
    }

    @Override
    public List<String> readRecent(int limit) {
        return projectionStore.recent(limit);
    }
}

// Dummy implementation for v3
class InMemoryDistributedIdempotencyStore implements DistributedIdempotencyStore {
    private final Map<String, Boolean> claimed = new HashMap<>();

    @Override
    public boolean claim(String key, long ttlMs) {
        if (claimed.containsKey(key)) {
            return false;
        }
        claimed.put(key, true);
        return true;
    }
}

class InMemoryDistributedAuctionPlatform implements DistributedAuctionPlatformService {
    private final DistributedIdempotencyStore idempotencyStore;
    private int nextId = 1;
    
    // id -> region
    private final Map<String, String> itemRegion = new HashMap<>();
    // region -> list of payloads
    private final Map<String, List<String>> regionData = new HashMap<>();

    public InMemoryDistributedAuctionPlatform(DistributedIdempotencyStore idempotencyStore) {
        this.idempotencyStore = idempotencyStore;
    }

    @Override
    public String create(String ownerId, String payload, String region) {
        String id = String.valueOf(nextId++);
        itemRegion.put(id, region);
        regionData.computeIfAbsent(region, k -> new ArrayList<>()).add(payload);
        return id;
    }

    @Override
    public void mutateWithReplayToken(String id, String mutationPayload, String idempotencyKey, String replayToken) {
        if (idempotencyStore.claim(idempotencyKey, 1000)) {
            String region = itemRegion.get(id);
            if (region != null) {
                regionData.get(region).add(mutationPayload);
            }
        }
    }

    @Override
    public List<String> readRegionView(String region, int limit) {
        List<String> list = regionData.getOrDefault(region, Collections.emptyList());
        List<String> result = new ArrayList<>();
        int start = Math.max(0, list.size() - limit);
        for (int i = list.size() - 1; i >= start; i--) {
            result.add(list.get(i));
        }
        return result;
    }
}

public class AuctionPlatformServiceTest {

    @Test
    public void testV1CreateAndGet() {
        AuctionPlatformService service = new InMemoryAuctionPlatformV1();
        String id = service.create("user1", "Item A");
        
        assertEquals("1", id);
        assertTrue(service.getById(id).isPresent());
        assertEquals("Item A", service.getById(id).get());
        assertFalse(service.getById("999").isPresent());
    }

    @Test
    public void testV1Mutate() {
        InMemoryAuctionPlatformV1 service = new InMemoryAuctionPlatformV1();
        String id = service.create("user1", "Item A");
        service.mutate(id, "Bid 100", "idem-1");
        
        assertEquals(1, service.mutations.size());
        assertEquals(id + ":Bid 100:idem-1", service.mutations.get(0));
    }

    @Test
    public void testV2PublishAndReadRecent() {
        AuctionPlatformServiceProjectionStore projectionStore = new InMemoryProjectionStore();
        AuctionPlatformServiceV2 service = new InMemoryAuctionPlatformV2(projectionStore);
        
        String id1 = service.create("user1", "Item A");
        String id2 = service.create("user2", "Item B");
        
        List<String> recent = service.readRecent(2);
        assertEquals(2, recent.size());
        assertEquals("Item B", recent.get(0));
        assertEquals("Item A", recent.get(1));
        
        service.publishMutation(id1, "Item A - Bid 100", "idem-2");
        
        List<String> recentAfterMut = service.readRecent(2);
        assertEquals("Item A - Bid 100", recentAfterMut.get(0));
        assertEquals("Item B", recentAfterMut.get(1));
    }

    @Test
    public void testV3IdempotentMutationAndRegionView() {
        DistributedIdempotencyStore idemStore = new InMemoryDistributedIdempotencyStore();
        DistributedAuctionPlatformService service = new InMemoryDistributedAuctionPlatform(idemStore);
        
        String id1 = service.create("user1", "Item A", "US-EAST");
        String id2 = service.create("user2", "Item B", "EU-WEST");
        
        service.mutateWithReplayToken(id1, "Item A - Bid 100", "idem-3", "token-1");
        // Same idempotency key, should be ignored
        service.mutateWithReplayToken(id1, "Item A - Bid 150", "idem-3", "token-2");
        
        List<String> usEastView = service.readRegionView("US-EAST", 5);
        assertEquals(2, usEastView.size());
        assertEquals("Item A - Bid 100", usEastView.get(0));
        assertEquals("Item A", usEastView.get(1));
        
        List<String> euWestView = service.readRegionView("EU-WEST", 5);
        assertEquals(1, euWestView.size());
        assertEquals("Item B", euWestView.get(0));
    }
}
