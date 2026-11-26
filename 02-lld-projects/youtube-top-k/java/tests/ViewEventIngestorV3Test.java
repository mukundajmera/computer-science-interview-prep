import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import java.util.*;

class MockDistributedRepository implements DistributedRepository {
    private final Map<String, String> store = new HashMap<>();

    @Override
    public void save(String key, String value, String region) {
        store.put(key + ":" + region, value);
    }

    @Override
    public Optional<String> find(String key, String region) {
        return Optional.ofNullable(store.get(key + ":" + region));
    }
}

class MockIdempotencyStore implements IdempotencyStore {
    private final Set<String> claims = new HashSet<>();

    @Override
    public boolean claim(String key, long ttlMs) {
        if (claims.contains(key)) return false;
        claims.add(key);
        return true;
    }
}

public class ViewEventIngestorV3Test {
    private MockDistributedRepository repo;
    private MockIdempotencyStore idemp;
    private ViewEventIngestorV3 service;

    @BeforeEach
    void setUp() {
        repo = new MockDistributedRepository();
        idemp = new MockIdempotencyStore();
        service = new ViewEventIngestorV3(repo, idemp, 3);
    }

    @Test
    void testV3Idempotency() {
        long currTime = 1000L;
        String region = "us-east";
        Assertions.assertTrue(service.ingest("v1", currTime, "event1", region));
        Assertions.assertFalse(service.ingest("v1", currTime, "event1", region));
        Assertions.assertTrue(service.ingest("v1", currTime, "event2", region));
        Assertions.assertTrue(service.ingest("v2", currTime, "event3", region));
        
        List<String> topK = service.topK("window_0", 2, region);
        Assertions.assertEquals(2, topK.size());
        Assertions.assertEquals("v1", topK.get(0));
        Assertions.assertEquals("v2", topK.get(1));
    }

    @Test
    void testV3TieBreaking() {
        long currTime = 2000L;
        String region = "us-east";
        service.ingest("vA", currTime, "ev1", region);
        service.ingest("vB", currTime, "ev2", region);
        service.ingest("vC", currTime, "ev3", region);
        
        List<String> topK = service.topK("window_0", 2, region);
        Assertions.assertEquals(2, topK.size());
        Assertions.assertEquals("vA", topK.get(0));
        Assertions.assertEquals("vB", topK.get(1));
    }

    @Test
    void testV3EmptyStream() {
        List<String> topK = service.topK("window_1000", 3, "us-east");
        Assertions.assertTrue(topK.isEmpty());
    }

    @Test
    void testV3ExactStreamComparison() {
        long currTime = 3000L;
        String regionStr = "us-east";
        for (int i=0; i<50; i++) service.ingest("v1", currTime, "e1_"+i, regionStr);
        for (int i=0; i<20; i++) service.ingest("v2", currTime, "e2_"+i, regionStr);
        for (int i=0; i<10; i++) service.ingest("v3", currTime, "e3_"+i, regionStr);
        for (int i=0; i<5; i++) service.ingest("v4", currTime, "e4_"+i, regionStr);
        
        List<String> topK = service.topK("window_0", 3, regionStr);
        Assertions.assertEquals(3, topK.size());
        Assertions.assertEquals("v1", topK.get(0));
        Assertions.assertEquals("v2", topK.get(1));
        Assertions.assertEquals("v3", topK.get(2));
    }

    @Test
    void testV3WindowRotationAndBounds() {
        long baseTime = 4000L * 3600 * 1000L;
        String region = "us-east";
        for (int i=0; i<6; i++) {
            long timeMs = baseTime + (i * 3600L * 1000L);
            service.ingest("v" + i, timeMs, "ev_"+i, region);
        }
        
        List<String> topK = service.topK("window_" + baseTime, 1, region);
        Assertions.assertEquals(1, topK.size());
        Assertions.assertEquals("v0", topK.get(0));
    }

    @Test
    void testV3RollbackIgnored() {
        WindowState ws = new WindowState(1000, 5);
        ws.cms.add("v1", -1);
        Assertions.assertEquals(0, ws.cms.estimate("v1"));
    }
}
