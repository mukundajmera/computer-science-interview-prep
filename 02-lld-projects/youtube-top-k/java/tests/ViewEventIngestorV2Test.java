import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

class MockWindowStateStore implements WindowStateStore {
    private final Map<String, String> store = new HashMap<>();

    @Override
    public void save(String windowKey, String statePayload) {
        store.put(windowKey, statePayload);
    }

    @Override
    public String load(String windowKey) {
        return store.get(windowKey);
    }
}

public class ViewEventIngestorV2Test {
    
    private MockWindowStateStore store;
    private ViewEventIngestorV2 service;
    
    @BeforeEach
    void setUp() {
        store = new MockWindowStateStore();
        service = new ViewEventIngestorV2(store, 3);
    }

    @Test
    void testIngestAndTopK() {
        long currTime = 1000L;
        for (int i = 0; i < 5; i++) service.ingest("v1", currTime);
        for (int i = 0; i < 3; i++) service.ingest("v2", currTime);
        for (int i = 0; i < 4; i++) service.ingest("v3", currTime);
        for (int i = 0; i < 2; i++) service.ingest("v4", currTime);

        // Window size is 1 hour = 3600000ms. 1000L belongs to "window_0"
        String windowKey = "window_0";
        List<String> topK = service.topK(windowKey, 3);

        Assertions.assertEquals(3, topK.size());
        Assertions.assertEquals("v1", topK.get(0));
        Assertions.assertEquals("v3", topK.get(1));
        Assertions.assertEquals("v2", topK.get(2));
    }

    @Test
    void testTieBreaking() {
        long currTime = 2000L;
        service.ingest("vA", currTime);
        service.ingest("vB", currTime);
        service.ingest("vC", currTime);

        String windowKey = "window_0";
        List<String> topK = service.topK(windowKey, 2);

        Assertions.assertEquals(2, topK.size());
        // Lexicographically smaller string should win the tie in rank
        Assertions.assertEquals("vA", topK.get(0));
        Assertions.assertEquals("vB", topK.get(1));
    }

    @Test
    void testEmptyStream() {
        List<String> topK = service.topK("non_existent_window", 3);
        Assertions.assertTrue(topK.isEmpty());
    }

    @Test
    void testExactStreamComparison() {
        long currTime = 3000L;
        for (int i = 0; i < 50; i++) service.ingest("v1", currTime);
        for (int i = 0; i < 20; i++) service.ingest("v2", currTime);
        for (int i = 0; i < 10; i++) service.ingest("v3", currTime);
        for (int i = 0; i < 5; i++) service.ingest("v4", currTime);

        String windowKey = "window_0";
        List<String> topK = service.topK(windowKey, 3);
        
        Assertions.assertEquals(3, topK.size());
        Assertions.assertEquals("v1", topK.get(0));
        Assertions.assertEquals("v2", topK.get(1));
        Assertions.assertEquals("v3", topK.get(2));
    }

    @Test
    void testWindowRotationAndBounds() {
        long baseTime = 4000L * 3600L * 1000L;
        for (int i = 0; i < 6; i++) {
            long timeMs = baseTime + (i * 3600L * 1000L);
            service.ingest("v" + i, timeMs);
        }

        String windowKey0 = "window_" + baseTime;
        
        // Due to eviction (max size 5), the oldest window is removed from memory,
        // but topK logic should gracefully load it from the store via fromPayload.
        List<String> topK = service.topK(windowKey0, 1);
        Assertions.assertEquals(1, topK.size());
        Assertions.assertEquals("v0", topK.get(0));
    }

    @Test
    void testRollbackIgnored() {
        // Using CountMinSketch inside a dummy WindowState to verify it ignores negative updates
        WindowState ws = new WindowState(1000, 5);
        ws.cms.add("v1", -1);
        Assertions.assertEquals(0, ws.cms.estimate("v1"));
    }
}
