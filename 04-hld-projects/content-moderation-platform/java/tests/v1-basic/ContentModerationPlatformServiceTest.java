import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

import java.util.Arrays;
import java.util.Collections;
import java.util.List;

import static org.junit.jupiter.api.Assertions.*;

public class ContentModerationPlatformServiceTest {

    private ContentModerationPlatformService service;

    @BeforeEach
    public void setUp() {
        List<String> blocklist = Arrays.asList("violence", "hate");
        List<String> warnings = Arrays.asList("scam", "suspicious");
        List<String> regexps = Arrays.asList("\\b[a-z]+[0-9]{5,}\\b"); // e.g., words with many numbers
        service = new ContentModerationPlatformService(blocklist, warnings, regexps);
    }

    @Test
    public void testCleanContentIsAllowed() {
        ContentModerationPlatformService.ModerationRequest request =
            new ContentModerationPlatformService.ModerationRequest("c1", "This is a lovely day", null, "feed");

        ContentModerationPlatformService.ModerationResponse response = service.evaluate(request);

        assertEquals(ContentModerationPlatformService.Action.ALLOW, response.action);
        assertTrue(response.riskScore < 0.4);
        assertEquals(1.0, response.confidence);
        assertTrue(response.reasons.isEmpty());
    }

    @Test
    public void testBlocklistContentIsRemoved() {
        ContentModerationPlatformService.ModerationRequest request =
            new ContentModerationPlatformService.ModerationRequest("c2", "I love violence and hate", null, "feed");

        ContentModerationPlatformService.ModerationResponse response = service.evaluate(request);

        assertEquals(ContentModerationPlatformService.Action.AUTO_REMOVE, response.action);
        assertTrue(response.riskScore >= 0.8);
        assertTrue(response.reasons.contains("blocklist_keyword_match: violence"));
        assertTrue(response.reasons.contains("blocklist_keyword_match: hate"));
    }

    @Test
    public void testWarningContentIsEscalated() {
        ContentModerationPlatformService.ModerationRequest request =
            new ContentModerationPlatformService.ModerationRequest("c3", "This looks like a scam", Collections.singletonList("img1"), "feed");

        ContentModerationPlatformService.ModerationResponse response = service.evaluate(request);

        assertEquals(ContentModerationPlatformService.Action.ESCALATE_TO_HUMAN, response.action);
        assertTrue(response.riskScore >= 0.4 && response.riskScore < 0.8);
        assertTrue(response.reasons.contains("warning_keyword_match: scam"));
        assertTrue(response.reasons.contains("media_present"));
    }

    @Test
    public void testRegexMatchIsRemoved() {
        ContentModerationPlatformService.ModerationRequest request =
            new ContentModerationPlatformService.ModerationRequest("c4", "Check out my link user123456", null, "feed");

        ContentModerationPlatformService.ModerationResponse response = service.evaluate(request);

        assertEquals(ContentModerationPlatformService.Action.AUTO_REMOVE, response.action);
        assertTrue(response.reasons.stream().anyMatch(r -> r.startsWith("regex_match: ")));
    }

    @Test
    public void testAuditLedgerAndModeratorDecision() {
        ContentModerationPlatformService.ModerationRequest request =
            new ContentModerationPlatformService.ModerationRequest("c5", "Some suspicious stuff", null, "feed");

        service.evaluate(request);

        List<ContentModerationPlatformService.AuditRecord> ledger = service.getAuditLedger();
        assertEquals(1, ledger.size());
        assertEquals("c5", ledger.get(0).contentId);
        assertEquals(ContentModerationPlatformService.Action.ESCALATE_TO_HUMAN, ledger.get(0).finalAction);

        service.recordModeratorDecision("c5", ContentModerationPlatformService.Action.ALLOW);

        ledger = service.getAuditLedger();
        assertEquals(1, ledger.size());
        assertEquals(ContentModerationPlatformService.Action.ALLOW, ledger.get(0).finalAction);
    }
}
