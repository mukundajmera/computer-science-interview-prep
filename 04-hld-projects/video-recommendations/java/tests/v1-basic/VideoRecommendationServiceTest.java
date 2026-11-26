import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

import java.util.List;

import static org.junit.jupiter.api.Assertions.*;

public class VideoRecommendationServiceTest {

    private VideoRecommendationService service;

    @BeforeEach
    public void setUp() {
        service = new VideoRecommendationService();
        service.addVideo(new VideoRecommendationService.Video("v1", "action", 0.8, 1000));
        service.addVideo(new VideoRecommendationService.Video("v2", "comedy", 0.9, 2000));
        service.addVideo(new VideoRecommendationService.Video("v3", "action", 0.5, 3000));
        service.addVideo(new VideoRecommendationService.Video("v4", "drama", 0.7, 4000));
        service.addVideo(new VideoRecommendationService.Video("v5", "action", 0.2, 5000));
    }

    @Test
    public void testCandidateGenerationAndCategoryMatching() {
        // User watched an action movie entirely
        service.recordWatchEvent("user1", "v1", 1.0, 6000);

        List<VideoRecommendationService.Video> recs = service.getRecommendations("user1", 2, 7000);
        assertEquals(2, recs.size());

        // Since user watched action, v5 and v3 should be favored (v5 is newer, v3 is older)
        assertTrue(recs.stream().anyMatch(v -> v.id.equals("v5") || v.id.equals("v3")));
    }

    @Test
    public void testPopularityFallback() {
        // New user, no history
        List<VideoRecommendationService.Video> recs = service.getRecommendations("new_user", 2, 7000);
        assertEquals(2, recs.size());

        // Should rely on popularity + recency. v5 is most recent, v4 is second. v2 is most popular.
        assertNotNull(recs);
        assertFalse(recs.isEmpty());
    }

    @Test
    public void testUnseenVideoFiltering() {
        service.recordWatchEvent("user1", "v1", 1.0, 6000);
        service.recordWatchEvent("user1", "v3", 1.0, 6000);
        service.recordWatchEvent("user1", "v5", 1.0, 6000);

        // User has watched all action videos
        List<VideoRecommendationService.Video> recs = service.getRecommendations("user1", 5, 7000);

        // Output shouldn't contain v1, v3, v5
        assertFalse(recs.stream().anyMatch(v -> v.id.equals("v1") || v.id.equals("v3") || v.id.equals("v5")));
        assertTrue(recs.stream().anyMatch(v -> v.id.equals("v2")));
        assertTrue(recs.stream().anyMatch(v -> v.id.equals("v4")));
    }

    @Test
    public void testTopKRanking() {
        service.recordWatchEvent("user1", "v1", 1.0, 6000);
        List<VideoRecommendationService.Video> recs = service.getRecommendations("user1", 1, 7000);
        assertEquals(1, recs.size());

        // Top 1 should probably be v5 because it's action and most recent
        assertEquals("v5", recs.get(0).id);
    }
}
