package metrics.v2;

import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;
import java.util.List;
import java.util.Map;
import java.util.HashMap;
import java.util.stream.Collectors;

class WindowedTopKServiceTest {

    static class InMemoryWindowedTopKService implements WindowedTopKService {
        private final Map<String, Integer> viewCounts = new HashMap<>();

        @Override
        public void ingestView(String videoId, long timestampMs) {
            viewCounts.put(videoId, viewCounts.getOrDefault(videoId, 0) + 1);
        }

        @Override
        public List<String> topK(String windowKey, int k) {
            return viewCounts.entrySet().stream()
                .sorted((a, b) -> b.getValue().compareTo(a.getValue()))
                .map(Map.Entry::getKey)
                .limit(k)
                .collect(Collectors.toList());
        }
    }

    @Test
    void testIngestAndTopK() {
        WindowedTopKService service = new InMemoryWindowedTopKService();
        service.ingestView("vid1", 1000L);
        service.ingestView("vid1", 1001L);
        service.ingestView("vid2", 1002L);
        
        List<String> top = service.topK("window1", 10);
        assertEquals(2, top.size());
        assertEquals("vid1", top.get(0));
        assertEquals("vid2", top.get(1));
    }

    @Test
    void testTopKLimit() {
        WindowedTopKService service = new InMemoryWindowedTopKService();
        service.ingestView("vid1", 1000L);
        service.ingestView("vid2", 1001L);
        service.ingestView("vid2", 1002L);
        service.ingestView("vid3", 1003L);
        service.ingestView("vid3", 1004L);
        service.ingestView("vid3", 1005L);
        
        List<String> top = service.topK("window1", 2);
        assertEquals(2, top.size());
        assertEquals("vid3", top.get(0));
        assertEquals("vid2", top.get(1));
    }

    @Test
    void testEmptyTopK() {
        WindowedTopKService service = new InMemoryWindowedTopKService();
        List<String> top = service.topK("window1", 5);
        assertTrue(top.isEmpty());
    }
}
