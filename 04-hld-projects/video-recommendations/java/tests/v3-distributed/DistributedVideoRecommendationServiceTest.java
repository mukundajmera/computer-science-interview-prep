package v3_distributed;

import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

import java.util.Arrays;
import java.util.List;
import java.util.stream.Collectors;

import static org.junit.jupiter.api.Assertions.*;

public class DistributedVideoRecommendationServiceTest {

    private DistributedVideoRecommendationService service;

    private static class DummyGenerator implements DistributedVideoRecommendationService.CandidateGenerator {
        private final String prefix;
        public DummyGenerator(String prefix) { this.prefix = prefix; }

        @Override
        public List<DistributedVideoRecommendationService.VideoCandidate> getCandidates(String userId, String contextVideoId, int limit) {
            return Arrays.asList(
                new DistributedVideoRecommendationService.VideoCandidate(prefix + "1", "src", 1.0),
                new DistributedVideoRecommendationService.VideoCandidate(prefix + "2", "src", 2.0)
            );
        }
    }

    private static class DummyShard implements DistributedVideoRecommendationService.RankingShard {
        private final String id;
        private final boolean slow;
        private final boolean fail;

        public DummyShard(String id, boolean slow, boolean fail) {
            this.id = id;
            this.slow = slow;
            this.fail = fail;
        }

        @Override
        public List<DistributedVideoRecommendationService.RankScore> rankCandidates(String userId, List<DistributedVideoRecommendationService.VideoCandidate> candidates) {
            if (fail) throw new RuntimeException("Shard failed");
            if (slow) {
                try { Thread.sleep(200); } catch (InterruptedException e) {}
            }
            return candidates.stream()
                .map(c -> new DistributedVideoRecommendationService.RankScore(c.videoId, c.baseScore * 10))
                .collect(Collectors.toList());
        }

        @Override
        public String getShardId() { return id; }
    }

    @BeforeEach
    void setUp() {
        // Will initialize per test if specific behavior is needed
    }

    @AfterEach
    void tearDown() {
        if (service != null) {
            service.shutdown();
        }
    }

    @Test
    void testBasicDistributedRetrievalAndRanking() {
        List<DistributedVideoRecommendationService.CandidateGenerator> generators = Arrays.asList(
            new DummyGenerator("A"), new DummyGenerator("B")
        );
        List<DistributedVideoRecommendationService.RankingShard> shards = Arrays.asList(
            new DummyShard("S1", false, false), new DummyShard("S2", false, false)
        );

        service = new DistributedVideoRecommendationService(generators, shards, 500);

        List<String> recommendations = service.getRecommendations("user1", "ctx", 10);

        assertEquals(4, recommendations.size());
        assertTrue(recommendations.contains("A1"));
        assertTrue(recommendations.contains("A2"));
        assertTrue(recommendations.contains("B1"));
        assertTrue(recommendations.contains("B2"));

        // highest score first (B2 or A2 will have baseScore 2.0 -> rank score 20)
        assertTrue(recommendations.get(0).endsWith("2"));
    }

    @Test
    void testTimeoutFallbackOnSlowShard() {
        List<DistributedVideoRecommendationService.CandidateGenerator> generators = Arrays.asList(
            new DummyGenerator("A")
        );
        // Set timeout to 50ms, but shard takes 200ms
        List<DistributedVideoRecommendationService.RankingShard> shards = Arrays.asList(
            new DummyShard("S1", true, false)
        );

        service = new DistributedVideoRecommendationService(generators, shards, 50);

        List<String> recommendations = service.getRecommendations("user1", "ctx", 10);
        assertEquals(2, recommendations.size());

        // Since it timed out, fallback uses base scores (1.0 and 2.0)
        // A2 has 2.0 base score
        assertEquals("A2", recommendations.get(0));
    }

    @Test
    void testCircuitBreakerOnFailingShard() {
        List<DistributedVideoRecommendationService.CandidateGenerator> generators = Arrays.asList(
            new DummyGenerator("A")
        );
        List<DistributedVideoRecommendationService.RankingShard> shards = Arrays.asList(
            new DummyShard("S1", false, true) // Always fails
        );

        service = new DistributedVideoRecommendationService(generators, shards, 500);

        // Multiple requests to trip the circuit breaker
        for(int i = 0; i < 5; i++) {
            List<String> recommendations = service.getRecommendations("user1", "ctx", 10);
            assertEquals(2, recommendations.size());
        }

        // Even when tripped, we get the fallback candidates.
        List<String> recommendations = service.getRecommendations("user1", "ctx", 10);
        assertEquals("A2", recommendations.get(0));
    }

    @Test
    void testRealTimeFeedbackAdjustments() {
        List<DistributedVideoRecommendationService.CandidateGenerator> generators = Arrays.asList(
            new DummyGenerator("A")
        );
        List<DistributedVideoRecommendationService.RankingShard> shards = Arrays.asList(
            new DummyShard("S1", false, false)
        );

        service = new DistributedVideoRecommendationService(generators, shards, 500);

        // Normally A2 > A1 (20 vs 10 rank score)
        List<String> recsBefore = service.getRecommendations("user1", "ctx", 10);
        assertEquals("A2", recsBefore.get(0));
        assertEquals("A1", recsBefore.get(1));

        // Add huge negative feedback to A2
        service.recordFeedback("user1", "A2", "SKIP", 0);
        service.recordFeedback("user1", "A2", "SKIP", 0); // -4 total
        // But 20 - 4 = 16. Still greater than 10.
        // Let's make it larger by repeatedly skipping
        for(int i = 0; i < 5; i++) service.recordFeedback("user1", "A2", "SKIP", 0); // -10 more, total -14. 20 - 14 = 6.

        // Add huge positive feedback to A1
        service.recordFeedback("user1", "A1", "LIKE", 0); // +5. 10 + 5 = 15.

        // Now A1 should beat A2 (15 vs 6)
        List<String> recsAfter = service.getRecommendations("user1", "ctx", 10);
        assertEquals("A1", recsAfter.get(0));
        assertEquals("A2", recsAfter.get(1));
    }
}