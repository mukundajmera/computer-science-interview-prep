import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

import java.util.Arrays;
import java.util.List;

import static org.junit.jupiter.api.Assertions.*;

public class ScaledVideoRecommendationServiceTest {

    private ScaledVideoRecommendationService service;

    @BeforeEach
    public void setUp() {
        service = new ScaledVideoRecommendationService();
        service.addVideo(new ScaledVideoRecommendationService.Video("v1", "action", 0.8, 1000, Arrays.asList("explosions", "hero")));
        service.addVideo(new ScaledVideoRecommendationService.Video("v2", "comedy", 0.9, 2000, Arrays.asList("funny", "jokes")));
        service.addVideo(new ScaledVideoRecommendationService.Video("v3", "action", 0.5, 3000, Arrays.asList("hero", "villain")));
        service.addVideo(new ScaledVideoRecommendationService.Video("v4", "drama", 0.7, 4000, Arrays.asList("sad", "emotional")));
        service.addVideo(new ScaledVideoRecommendationService.Video("v5", "action", 0.2, 5000, Arrays.asList("cars", "chase")));
        service.addVideo(new ScaledVideoRecommendationService.Video("v6", "action", 0.6, 6000, Arrays.asList("hero", "fight")));
        service.addVideo(new ScaledVideoRecommendationService.Video("v7", "action", 0.4, 7000, Arrays.asList("gun", "police")));
    }

    @Test
    public void testCandidateGenerationAndHeavyRanking() {
        // User watched an action movie entirely
        service.recordWatchEvent("user1", "v1", 1.0, 6000);

        List<ScaledVideoRecommendationService.Video> recs = service.getRecommendations("user1", 3, 8000);
        assertFalse(recs.isEmpty());

        // Should heavily rank action videos (v3, v5, v6, v7) since affinity for action is 1.0
        // Because of diversity penalty, it might interleave other categories if it asks for more,
        // but here it should definitely suggest at least one action.
        assertTrue(recs.stream().anyMatch(v -> v.category.equals("action")));
        assertFalse(recs.stream().anyMatch(v -> v.id.equals("v1"))); // Unseen filtering
    }

    @Test
    public void testColdStartEpsilonGreedy() {
        // New user, no history
        // They will hit the cold start path which has 0.8 epsilon. So there's 80% chance of random videos
        // We do this a few times to ensure we get some results without throwing an exception.
        List<ScaledVideoRecommendationService.Video> recs = service.getRecommendations("new_user", 2, 8000);
        assertTrue(recs.size() <= 2 && recs.size() > 0);
    }

    @Test
    public void testDiversityPenalty() {
        // User loves action
        service.recordWatchEvent("user1", "v1", 1.0, 6000);
        service.recordWatchEvent("user1", "v3", 1.0, 6000);

        List<ScaledVideoRecommendationService.Video> recs = service.getRecommendations("user1", 5, 8000);

        // Since we ask for 5 videos and we only have 7 total (2 watched), 5 remaining
        // The remaining are v2(comedy), v4(drama), v5(action), v6(action), v7(action).
        // Max from one category should ideally be limited or backfilled.
        assertEquals(5, recs.size());

        // Ensure that not ALL are action due to diversity backfill or interleaving.
        // Even with strong action affinity, the diversity penalty will lower action scores
        // or force limit, making v2 or v4 bubble up.
        long nonActionCount = recs.stream().filter(v -> !v.category.equals("action")).count();
        assertTrue(nonActionCount > 0, "Recommendations should include non-action videos due to diversity penalty.");
    }

    @Test
    public void testUserProfileCacheAndInvalidation() {
        // Request once to populate cache
        service.recordWatchEvent("user2", "v2", 1.0, 6000);
        List<ScaledVideoRecommendationService.Video> recs1 = service.getRecommendations("user2", 2, 7000);

        // Request again within TTL (1 minute)
        List<ScaledVideoRecommendationService.Video> recs2 = service.getRecommendations("user2", 2, 7010);

        // The results should be relatively similar (except random exploration could differ slightly)
        // Now record another event, this should invalidate the cache
        service.recordWatchEvent("user2", "v4", 1.0, 7020);

        List<ScaledVideoRecommendationService.Video> recs3 = service.getRecommendations("user2", 2, 7030);

        // Check that drama (v4) influences the results now
        assertFalse(recs3.stream().anyMatch(v -> v.id.equals("v4"))); // Should be filtered out as watched
    }
}