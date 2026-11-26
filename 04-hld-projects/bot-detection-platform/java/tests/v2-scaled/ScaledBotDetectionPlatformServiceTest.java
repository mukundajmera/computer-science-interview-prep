package v2.scaled;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import java.util.HashMap;
import java.util.Map;
import java.util.List;

import static org.junit.jupiter.api.Assertions.*;

public class ScaledBotDetectionPlatformServiceTest {

    private ScaledBotDetectionPlatformService service;

    @BeforeEach
    public void setUp() {
        service = new ScaledBotDetectionPlatformService();
    }

    @Test
    public void testPassForNormalActivity() {
        Map<String, Object> context = new HashMap<>();
        context.put("ip", "1.2.3.4");
        context.put("device_id", "valid_device");

        service.setIpReputation("1.2.3.4", 0.1);

        ScaledBotDetectionPlatformService.Event event = new ScaledBotDetectionPlatformService.Event(
            "user_normal", "login", context, 1000L
        );

        ScaledBotDetectionPlatformService.BotRiskResponse response = service.evaluate(event);

        assertEquals(ScaledBotDetectionPlatformService.RemediationAction.PASS, response.action);
        assertTrue(response.riskScore < 0.4);
        assertFalse(response.queuedForInvestigation);
    }

    @Test
    public void testChallengeSilentPowForModerateRisk() {
        Map<String, Object> context = new HashMap<>();
        context.put("ip", "1.2.3.5");
        context.put("device_id", "valid");

        service.setIpReputation("1.2.3.5", 0.65); // High IP risk, triggers moderate overall risk (0.6 * 0.65 = 0.39) + base = approx 0.4

        ScaledBotDetectionPlatformService.Event event = new ScaledBotDetectionPlatformService.Event(
            "user_moderate", "login", context, 1000L
        );

        ScaledBotDetectionPlatformService.BotRiskResponse response = service.evaluate(event);

        assertEquals(ScaledBotDetectionPlatformService.RemediationAction.CHALLENGE_SILENT_POW, response.action);
        assertTrue(response.reasons.contains("bad_ip_reputation"));
    }

    @Test
    public void testChallengeCaptchaForHighRisk() {
        Map<String, Object> context = new HashMap<>();
        context.put("ip", "1.2.3.6");
        // missing device_id triggers high entropy risk (0.1 * 0.8 = 0.08)

        service.setIpReputation("1.2.3.6", 1.0); // Highest IP risk (0.6 * 1.0 = 0.6)

        // velocity 0 for first event
        // Score = 0.6 + 0.08 = 0.68 -> CAPTCHA

        ScaledBotDetectionPlatformService.Event event = new ScaledBotDetectionPlatformService.Event(
            "user_high", "login", context, 1000L
        );

        ScaledBotDetectionPlatformService.BotRiskResponse response = service.evaluate(event);

        assertEquals(ScaledBotDetectionPlatformService.RemediationAction.CHALLENGE_CAPTCHA, response.action);
        assertTrue(response.queuedForInvestigation);

        List<ScaledBotDetectionPlatformService.InvestigationTask> queue = service.getInvestigationQueue();
        assertEquals(1, queue.size());
        assertEquals("user_high", queue.get(0).accountId);
    }

    @Test
    public void testBlockAndRateLimit() {
        Map<String, Object> context = new HashMap<>();
        context.put("ip", "1.2.3.7");
        service.setIpReputation("1.2.3.7", 0.95);

        // Exhaust rate limit
        for (int i = 0; i < 150; i++) {
            ScaledBotDetectionPlatformService.Event event = new ScaledBotDetectionPlatformService.Event(
                "user_spammer", "send_msg", context, 1000L + i * 10
            );
            ScaledBotDetectionPlatformService.BotRiskResponse response = service.evaluate(event);

            if (response.action == ScaledBotDetectionPlatformService.RemediationAction.BLOCK) {
                assertTrue(response.reasons.contains("rate_limited") || response.riskScore >= 0.8);
                break;
            }
        }
    }

    @Test
    public void testDegradedRuleOnlyFallback() {
        service.setMlServiceAvailable(false);

        Map<String, Object> context = new HashMap<>();
        context.put("ip", "1.2.3.8");
        service.setIpReputation("1.2.3.8", 0.7);

        ScaledBotDetectionPlatformService.Event event = new ScaledBotDetectionPlatformService.Event(
            "user_degraded", "login", context, 1000L
        );

        ScaledBotDetectionPlatformService.BotRiskResponse response = service.evaluate(event);

        assertTrue(response.reasons.contains("degraded_rule_mode"));
        assertEquals(0.4, response.confidence, 0.01);
        assertEquals(0.7, response.riskScore, 0.01);
    }

    @Test
    public void testAuditLogStream() {
        Map<String, Object> context = new HashMap<>();
        ScaledBotDetectionPlatformService.Event event = new ScaledBotDetectionPlatformService.Event(
            "user_audit", "login", context, 1000L
        );

        service.evaluate(event);

        List<ScaledBotDetectionPlatformService.AuditLog> stream = service.getAuditLogStream();
        assertEquals(1, stream.size());
        assertEquals("user_audit", stream.get(0).event.accountId);
    }
}
