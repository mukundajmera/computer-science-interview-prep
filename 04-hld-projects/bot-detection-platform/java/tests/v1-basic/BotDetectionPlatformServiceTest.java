package v1.basic;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

import java.util.HashMap;
import java.util.Map;

import static org.junit.jupiter.api.Assertions.*;

class BotDetectionPlatformServiceTest {

    private BotDetectionPlatformService service;

    @BeforeEach
    void setUp() {
        service = new BotDetectionPlatformService();
    }

    @Test
    void testPassActionForNormalUser() {
        Map<String, Object> context = new HashMap<>();
        context.put("ip", "192.168.1.1");
        context.put("device_id", "valid-device-12345");

        BotDetectionPlatformService.Event event = new BotDetectionPlatformService.Event(
                "user1", "login", context, System.currentTimeMillis());

        BotDetectionPlatformService.BotRiskResponse response = service.evaluate(event);

        assertEquals(BotDetectionPlatformService.RemediationAction.PASS, response.action);
        assertTrue(response.riskScore < 0.5);
        assertFalse(response.queuedForInvestigation);
        assertTrue(response.reasons.isEmpty());
    }

    @Test
    void testChallengeCaptchaForSuspiciousIP() {
        service.setIpReputation("10.0.0.99", 0.9); // bad IP

        Map<String, Object> context = new HashMap<>();
        context.put("ip", "10.0.0.99");
        context.put("device_id", "valid-device-12345");

        BotDetectionPlatformService.Event event = new BotDetectionPlatformService.Event(
                "user2", "post_comment", context, System.currentTimeMillis());

        BotDetectionPlatformService.BotRiskResponse response = service.evaluate(event);

        assertEquals(BotDetectionPlatformService.RemediationAction.CHALLENGE_CAPTCHA, response.action);
        assertTrue(response.riskScore >= 0.5 && response.riskScore < 0.8);
        assertTrue(response.queuedForInvestigation);
        assertTrue(response.reasons.contains("bad_ip_reputation"));

        assertEquals(1, service.getInvestigationQueue().size());
        assertEquals("user2", service.getInvestigationQueue().get(0).accountId);
    }

    @Test
    void testBlockActionForBotBehavior() {
        service.setIpReputation("10.0.0.99", 1.0); // very bad IP

        long now = System.currentTimeMillis();
        Map<String, Object> context = new HashMap<>();
        context.put("ip", "10.0.0.99");
        context.put("device_id", ""); // empty device id triggers entropy anomaly

        // Simulate high velocity
        for (int i = 0; i < 45; i++) {
            BotDetectionPlatformService.Event event = new BotDetectionPlatformService.Event(
                    "bot_user", "scraping", context, now - 10000 + i * 100);
            service.ingestEvent(event);
        }

        BotDetectionPlatformService.Event finalEvent = new BotDetectionPlatformService.Event(
                "bot_user", "scraping", context, now);

        BotDetectionPlatformService.BotRiskResponse response = service.evaluate(finalEvent);

        assertEquals(BotDetectionPlatformService.RemediationAction.BLOCK, response.action);
        assertTrue(response.riskScore >= 0.8);
        assertTrue(response.reasons.contains("bad_ip_reputation"));
        assertTrue(response.reasons.contains("device_anomaly"));
        assertTrue(response.reasons.contains("velocity_spike"));
    }

    @Test
    void testVelocitySpikeAlone() {
        long now = System.currentTimeMillis();
        Map<String, Object> context = new HashMap<>();
        context.put("ip", "192.168.1.1");
        context.put("device_id", "valid-device-12345");

        // Simulate high velocity (over 50 events/min)
        for (int i = 0; i < 55; i++) {
            BotDetectionPlatformService.Event event = new BotDetectionPlatformService.Event(
                    "spammer", "send_message", context, now - 50000 + i * 500);
            service.ingestEvent(event);
        }

        BotDetectionPlatformService.Event finalEvent = new BotDetectionPlatformService.Event(
                "spammer", "send_message", context, now);

        BotDetectionPlatformService.BotRiskResponse response = service.evaluate(finalEvent);

        assertTrue(response.reasons.contains("velocity_spike"));
        assertTrue(response.confidence > 0.5); // confidence should be higher with more history
    }
}
