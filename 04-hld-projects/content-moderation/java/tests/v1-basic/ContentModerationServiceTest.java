import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import java.util.Arrays;
import java.util.List;

import static org.junit.jupiter.api.Assertions.*;

class ContentModerationServiceTest {

    private ContentModerationService service;

    @BeforeEach
    void setUp() {
        List<String> blocklist = Arrays.asList("badword");
        List<String> flagPatterns = Arrays.asList("\\d{3}-\\d{2}-\\d{4}");
        service = new ContentModerationService(blocklist, flagPatterns);
    }

    @Test
    void testContentModerationPass() {
        ContentModerationService.ContentEvent event = new ContentModerationService.ContentEvent("1", "user1", "Hello world! This is a nice post.");
        ContentModerationService.ModerationResult result = service.evaluateContent(event);

        assertEquals(ContentModerationService.ModerationStatus.PASS, result.getStatus());
        assertTrue(service.getReviewQueue().isEmpty());

        List<ContentModerationService.ModerationResult> auditLog = service.getAuditLog();
        assertEquals(1, auditLog.size());
        assertEquals(ContentModerationService.ModerationStatus.PASS, auditLog.get(0).getStatus());
    }

    @Test
    void testContentModerationBlocked() {
        ContentModerationService.ContentEvent event = new ContentModerationService.ContentEvent("2", "user2", "This post contains a badword.");
        ContentModerationService.ModerationResult result = service.evaluateContent(event);

        assertEquals(ContentModerationService.ModerationStatus.BLOCKED, result.getStatus());
        assertTrue(result.getReason().contains("badword"));
        assertTrue(service.getReviewQueue().isEmpty());

        List<ContentModerationService.ModerationResult> auditLog = service.getAuditLog();
        assertEquals(1, auditLog.size());
        assertEquals(ContentModerationService.ModerationStatus.BLOCKED, auditLog.get(0).getStatus());
    }

    @Test
    void testContentModerationFlagged() {
        ContentModerationService.ContentEvent event = new ContentModerationService.ContentEvent("3", "user3", "My SSN is 123-45-6789.");
        ContentModerationService.ModerationResult result = service.evaluateContent(event);

        assertEquals(ContentModerationService.ModerationStatus.FLAGGED, result.getStatus());
        assertTrue(result.getReason().contains("pattern"));
        assertEquals(1, service.getReviewQueue().size());
        assertEquals("3", service.getReviewQueue().get(0).getContentId());

        List<ContentModerationService.ModerationResult> auditLog = service.getAuditLog();
        assertEquals(1, auditLog.size());
        assertEquals(ContentModerationService.ModerationStatus.FLAGGED, auditLog.get(0).getStatus());
    }

    @Test
    void testHumanReviewProcess() {
        ContentModerationService.ContentEvent event1 = new ContentModerationService.ContentEvent("4", "user4", "Please 123-45-6789 here.");
        ContentModerationService.ContentEvent event2 = new ContentModerationService.ContentEvent("5", "user5", "Another 123-45-6789 post.");

        service.evaluateContent(event1);
        service.evaluateContent(event2);

        assertEquals(2, service.getReviewQueue().size());

        // Process approval
        ContentModerationService.ModerationResult resultApproved = service.processReview("4", true);
        assertEquals(ContentModerationService.ModerationStatus.PASS, resultApproved.getStatus());
        assertEquals("Human review approved", resultApproved.getReason());

        // Process rejection
        ContentModerationService.ModerationResult resultRejected = service.processReview("5", false);
        assertEquals(ContentModerationService.ModerationStatus.BLOCKED, resultRejected.getStatus());
        assertEquals("Human review rejected", resultRejected.getReason());

        assertTrue(service.getReviewQueue().isEmpty());

        List<ContentModerationService.ModerationResult> auditLog = service.getAuditLog();
        assertEquals(4, auditLog.size()); // 2 evaluates, 2 reviews
    }

    @Test
    void testHumanReviewNotFound() {
        Exception exception = assertThrows(IllegalArgumentException.class, () -> {
            service.processReview("nonexistent_id", true);
        });

        assertTrue(exception.getMessage().contains("not found in review queue"));
    }
}
