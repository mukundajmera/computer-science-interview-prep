package v2_scaled;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import java.util.Arrays;
import java.util.List;
import java.util.concurrent.CompletableFuture;

import static org.junit.jupiter.api.Assertions.*;

class ScaledContentModerationPlatformServiceTest {

    private ScaledContentModerationPlatformService service;

    @BeforeEach
    void setUp() {
        ScaledContentModerationPlatformService.Policy policy = new ScaledContentModerationPlatformService.Policy(
                "p2.0", 0.9, 0.6, 0.4);
        service = new ScaledContentModerationPlatformService(policy, 4);
    }

    @org.junit.jupiter.api.AfterEach
    void tearDown() {
        if (service != null) {
            service.shutdown();
        }
    }

    @Test
    void testAsyncFanOutPipeline() throws Exception {
        ScaledContentModerationPlatformService.ModerationRequest request = new ScaledContentModerationPlatformService.ModerationRequest(
                "c1", "This is spam", Arrays.asList("bad_image"), "feed"
        );

        CompletableFuture<ScaledContentModerationPlatformService.ModerationResponse> future = service.evaluateAsync(request);
        ScaledContentModerationPlatformService.ModerationResponse response = future.get(); // wait for completion

        assertEquals(ScaledContentModerationPlatformService.Action.AUTO_REMOVE, response.action);
        assertTrue(response.reasons.contains("spam"));
        assertTrue(response.reasons.contains("known_bad_media"));
    }

    @Test
    void testPriorityReviewerQueueSlaSorting() throws Exception {
        service.updatePolicy(new ScaledContentModerationPlatformService.Policy("p_test", 0.9, 0.4, 0.2));

        // Clear the queue to discard old tasks
        while (service.getNextReviewTask() != null) {}

        service.evaluateAsync(new ScaledContentModerationPlatformService.ModerationRequest(
                "c_high2", "hate", null, "feed" // hate -> 0.8
        )).get();

        service.evaluateAsync(new ScaledContentModerationPlatformService.ModerationRequest(
                "c_med2", "spam", null, "feed" // spam -> 0.5
        )).get();

        // The review queue should yield the 0.8 priority first
        ScaledContentModerationPlatformService.ReviewTask task1 = service.getNextReviewTask();
        assertNotNull(task1);
        assertEquals(80, task1.priority);

        ScaledContentModerationPlatformService.ReviewTask task2 = service.getNextReviewTask();
        assertNotNull(task2);
        assertEquals(50, task2.priority);
    }

    @Test
    void testReviewerConflictResolutionMajorityVote() throws Exception {
        service.updatePolicy(new ScaledContentModerationPlatformService.Policy("p_test", 0.9, 0.4, 0.2));

        service.evaluateAsync(new ScaledContentModerationPlatformService.ModerationRequest(
                "c1", "hate", null, "feed"
        )).get();

        ScaledContentModerationPlatformService.ReviewTask task = service.getNextReviewTask();
        assertNotNull(task);
        assertFalse(task.resolved);

        boolean resolved = service.submitReviewVote(task.taskId, "rev1", ScaledContentModerationPlatformService.Action.DEMOTE, 3);
        assertFalse(resolved);

        resolved = service.submitReviewVote(task.taskId, "rev2", ScaledContentModerationPlatformService.Action.AUTO_REMOVE, 3);
        assertFalse(resolved);

        resolved = service.submitReviewVote(task.taskId, "rev3", ScaledContentModerationPlatformService.Action.AUTO_REMOVE, 3);
        assertTrue(resolved);

        assertEquals(ScaledContentModerationPlatformService.Action.AUTO_REMOVE, task.finalAction);
        assertTrue(task.resolved);
    }

    @Test
    void testFastRollbackPolicyCache() throws Exception {
        // Initially p2.0
        assertEquals("p2.0", service.getActivePolicy().version);

        ScaledContentModerationPlatformService.Policy newPolicy = new ScaledContentModerationPlatformService.Policy(
                "p2.1", 0.95, 0.65, 0.45);
        service.updatePolicy(newPolicy);

        assertEquals("p2.1", service.getActivePolicy().version);

        // Rollback
        service.rollbackPolicy("p2.0");
        assertEquals("p2.0", service.getActivePolicy().version);

        // Invalid rollback
        assertThrows(IllegalArgumentException.class, () -> {
            service.rollbackPolicy("p_nonexistent");
        });
    }
}
