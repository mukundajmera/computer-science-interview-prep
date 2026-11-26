package metrics.v1;

import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;
import java.util.List;
import java.util.ArrayList;

class MetricsLeaderboardServiceTest {

    static class InMemoryMetricsLeaderboardService implements MetricsLeaderboardService {
        private final List<LeaderboardEntry> entries = new ArrayList<>();
        
        @Override
        public void ingestPoint(String metricName, String actorId, double value, long timestampMs) {
            entries.add(new LeaderboardEntry(actorId, value, timestampMs));
            entries.sort((a, b) -> Double.compare(b.score(), a.score()));
        }

        @Override
        public LeaderboardSnapshot getSnapshot(String leaderboardId, int limit) {
            List<LeaderboardEntry> limited = entries.subList(0, Math.min(limit, entries.size()));
            return new LeaderboardSnapshot(leaderboardId, new ArrayList<>(limited), System.currentTimeMillis());
        }
    }

    @Test
    void testIngestPointAndGetSnapshot() {
        MetricsLeaderboardService service = new InMemoryMetricsLeaderboardService();
        service.ingestPoint("views", "actor1", 10.0, 1000L);
        LeaderboardSnapshot snapshot = service.getSnapshot("views-leaderboard", 10);
        assertEquals("views-leaderboard", snapshot.leaderboardId());
        assertEquals(1, snapshot.entries().size());
        assertEquals("actor1", snapshot.entries().get(0).actorId());
        assertEquals(10.0, snapshot.entries().get(0).score());
        assertEquals(1000L, snapshot.entries().get(0).updatedAtMs());
    }

    @Test
    void testSnapshotRespectsLimit() {
        MetricsLeaderboardService service = new InMemoryMetricsLeaderboardService();
        service.ingestPoint("views", "actor1", 10.0, 1000L);
        service.ingestPoint("views", "actor2", 20.0, 1001L);
        service.ingestPoint("views", "actor3", 5.0, 1002L);
        
        LeaderboardSnapshot snapshot = service.getSnapshot("views-leaderboard", 2);
        assertEquals(2, snapshot.entries().size());
        assertEquals("actor2", snapshot.entries().get(0).actorId());
        assertEquals("actor1", snapshot.entries().get(1).actorId());
    }

    @Test
    void testEmptySnapshot() {
        MetricsLeaderboardService service = new InMemoryMetricsLeaderboardService();
        LeaderboardSnapshot snapshot = service.getSnapshot("views-leaderboard", 10);
        assertEquals("views-leaderboard", snapshot.leaderboardId());
        assertTrue(snapshot.entries().isEmpty());
    }
}
