import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import java.util.Arrays;
import java.util.List;

import static org.junit.jupiter.api.Assertions.*;

public class ScaledContentModerationServiceTest {

    private MockMLService mlService;
    private ScaledContentModerationService service;

    static class MockMLService implements ScaledContentModerationService.MLModelService {
        boolean shouldFail = false;
        ScaledContentModerationService.MLPrediction response =
            new ScaledContentModerationService.MLPrediction(false, 1.0, "safe");

        @Override
        public ScaledContentModerationService.MLPrediction predict(String text) throws Exception {
            if (shouldFail) {
                throw new Exception("ML service timeout");
            }
            return response;
        }
    }

    @BeforeEach
    public void setUp() {
        mlService = new MockMLService();
        service = new ScaledContentModerationService(
            Arrays.asList("badword"),
            Arrays.asList("\\bviagra\\b"),
            mlService,
            200,
            2,
            2
        );
    }

    @Test
    public void testTier1FastPathBlock() {
        ScaledContentModerationService.ContentEvent event =
            new ScaledContentModerationService.ContentEvent("1", "u1", "This is a badword.");
        ScaledContentModerationService.ModerationResult result = service.evaluateContent(event);

        assertEquals(ScaledContentModerationService.ModerationStatus.BLOCKED, result.getStatus());
        assertTrue(result.getReason().contains("Blocked keyword"));
    }

    @Test
    public void testTier2MlHighConfidenceBlock() {
        mlService.response = new ScaledContentModerationService.MLPrediction(true, 0.95, "hate_speech");
        ScaledContentModerationService.ContentEvent event =
            new ScaledContentModerationService.ContentEvent("2", "u1", "This text is fine to tier1");
        ScaledContentModerationService.ModerationResult result = service.evaluateContent(event);

        assertEquals(ScaledContentModerationService.ModerationStatus.BLOCKED, result.getStatus());
        assertTrue(result.getReason().contains("ML blocked"));
    }

    @Test
    public void testTier2DegradedModeTimeout() {
        mlService.shouldFail = true;
        ScaledContentModerationService.ContentEvent event =
            new ScaledContentModerationService.ContentEvent("3", "u1", "Some normal text");
        ScaledContentModerationService.ModerationResult result = service.evaluateContent(event);

        assertEquals(ScaledContentModerationService.ModerationStatus.PASS, result.getStatus());
        assertTrue(result.getReason().contains("Degraded mode"));
    }

    @Test
    public void testQueueBackpressure() {
        mlService.response = new ScaledContentModerationService.MLPrediction(true, 0.75, "spam");

        // Fill queue
        service.evaluateContent(new ScaledContentModerationService.ContentEvent("q1", "u1", "Suspicious 1"));
        service.evaluateContent(new ScaledContentModerationService.ContentEvent("q2", "u1", "Suspicious 2"));

        assertEquals(2, service.getReviewQueue().size());

        // Exceed queue
        ScaledContentModerationService.ModerationResult result =
            service.evaluateContent(new ScaledContentModerationService.ContentEvent("q3", "u1", "Suspicious 3"));

        assertEquals(ScaledContentModerationService.ModerationStatus.PASS, result.getStatus());
        assertTrue(result.getReason().contains("Queue full"));
    }

    @Test
    public void testAppealsConsensusWorkflow() {
        mlService.response = new ScaledContentModerationService.MLPrediction(true, 0.75, "spam");
        ScaledContentModerationService.ContentEvent event =
            new ScaledContentModerationService.ContentEvent("a1", "u1", "Please review me");

        ScaledContentModerationService.ModerationResult result = service.evaluateContent(event);
        assertEquals(ScaledContentModerationService.ModerationStatus.NEEDS_REVIEW, result.getStatus());

        // First reviewer approves
        assertNull(service.processReview("a1", true));

        // Second reviewer approves
        ScaledContentModerationService.ModerationResult finalResult = service.processReview("a1", true);
        assertNotNull(finalResult);
        assertEquals(ScaledContentModerationService.ModerationStatus.PASS, finalResult.getStatus());
        assertTrue(finalResult.getReason().contains("consensus: approved"));
    }

    @Test
    public void testAppealsConsensusRejection() {
        mlService.response = new ScaledContentModerationService.MLPrediction(true, 0.75, "spam");
        ScaledContentModerationService.ContentEvent event =
            new ScaledContentModerationService.ContentEvent("a2", "u1", "Please review me");

        service.evaluateContent(event);

        // First reviewer rejects
        assertNull(service.processReview("a2", false));

        // Second reviewer rejects
        ScaledContentModerationService.ModerationResult finalResult = service.processReview("a2", false);
        assertNotNull(finalResult);
        assertEquals(ScaledContentModerationService.ModerationStatus.BLOCKED, finalResult.getStatus());
        assertTrue(finalResult.getReason().contains("consensus: rejected"));
    }
}
