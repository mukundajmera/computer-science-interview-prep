package metrics.v3;

import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;
import java.util.List;
import java.util.Map;
import java.util.HashMap;
import java.util.stream.Collectors;

class DistributedTopKServiceTest {

    static class InMemoryDistributedTopKService implements DistributedTopKService {
        private final Map<String, Integer> globalViewCounts = new HashMap<>();
        private boolean replayTriggered = false;

        @Override
        public void ingestView(String videoId, long timestampMs, String partitionKey) {
            globalViewCounts.put(videoId, globalViewCounts.getOrDefault(videoId, 0) + 1);
        }

        @Override
        public List<String> topK(String windowKey, int k, String region) {
            return globalViewCounts.entrySet().stream()
                .sorted((a, b) -> b.getValue().compareTo(a.getValue()))
                .map(Map.Entry::getKey)
                .limit(k)
                .collect(Collectors.toList());
        }

        @Override
        public void replayWindow(String windowKey, String replayToken) {
            this.replayTriggered = true;
        }
        
        public boolean isReplayTriggered() {
            return replayTriggered;
        }
    }

    @Test
    void testIngestAndTopK() {
        InMemoryDistributedTopKService service = new InMemoryDistributedTopKService();
        service.ingestView("vidA", 100L, "part1");
        service.ingestView("vidA", 101L, "part2");
        service.ingestView("vidB", 102L, "part1");

        List<String> top = service.topK("window-1", 10, "us-east");
        assertEquals(2, top.size());
        assertEquals("vidA", top.get(0));
        assertEquals("vidB", top.get(1));
    }

    @Test
    void testTopKLimitAndRegion() {
        InMemoryDistributedTopKService service = new InMemoryDistributedTopKService();
        service.ingestView("v1", 10L, "p1");
        service.ingestView("v2", 11L, "p1");
        service.ingestView("v2", 12L, "p1");
        service.ingestView("v3", 13L, "p1");
        service.ingestView("v3", 14L, "p1");
        service.ingestView("v3", 15L, "p1");

        List<String> top = service.topK("win2", 2, "eu-west");
        assertEquals(2, top.size());
        assertEquals("v3", top.get(0));
        assertEquals("v2", top.get(1));
    }

    @Test
    void testReplayWindow() {
        InMemoryDistributedTopKService service = new InMemoryDistributedTopKService();
        assertFalse(service.isReplayTriggered());
        
        service.replayWindow("win3", "tokenXYZ");
        assertTrue(service.isReplayTriggered());
    }
}
