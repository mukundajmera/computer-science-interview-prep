package tests.v3.distributed;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import v3.distributed.DistributedBotDetectionPlatformService;
import v3.distributed.DistributedBotDetectionPlatformService.Event;
import v3.distributed.DistributedBotDetectionPlatformService.RemediationAction;
import v3.distributed.DistributedBotDetectionPlatformService.BotRiskResponse;

import java.util.Arrays;
import java.util.HashMap;
import java.util.Map;

import static org.junit.jupiter.api.Assertions.*;

public class DistributedBotDetectionPlatformServiceTest {

    private DistributedBotDetectionPlatformService service;

    @BeforeEach
    public void setup() {
        service = new DistributedBotDetectionPlatformService("node-1", Arrays.asList("node-1", "node-2", "node-3"));
    }

    @Test
    public void testShadowModeEvaluation() {
        service.setShadowModeEnabled(true);
        service.setMlServiceAvailable(false);
        service.updateGlobalIpReputation("192.168.1.1", 1.0); // Will trigger block

        Map<String, Object> context = new HashMap<>();
        context.put("ip", "192.168.1.1");
        context.put("device_id", "12345");
        Event event = new Event("acc-1", "login", context, System.currentTimeMillis());

        BotRiskResponse response = service.evaluate(event);

        assertEquals(RemediationAction.SHADOW_BLOCK, response.action);
        assertTrue(response.reasons.contains("bad_ip_reputation"));
    }

    @Test
    public void testBloomFilterAndRedisIpReputation() {
        service.setMlServiceAvailable(false);
        service.updateGlobalIpReputation("10.0.0.1", 0.9); // Should go to bloom filter

        Map<String, Object> context = new HashMap<>();
        context.put("ip", "10.0.0.1");
        context.put("device_id", "12345");
        Event event = new Event("acc-2", "login", context, System.currentTimeMillis());

        BotRiskResponse response = service.evaluate(event);
        assertEquals(RemediationAction.BLOCK, response.action);
        assertTrue(response.reasons.contains("bad_ip_reputation"));

        service.updateGlobalIpReputation("10.0.0.1", 0.1); // Update to good reputation

        Map<String, Object> context2 = new HashMap<>();
        context2.put("ip", "10.0.0.1");
        context2.put("device_id", "12345");
        Event event2 = new Event("acc-3", "login", context2, System.currentTimeMillis());

        BotRiskResponse response2 = service.evaluate(event2);
        assertEquals(RemediationAction.PASS, response2.action);
    }

    @Test
    public void testKafkaAuditTelemetrySink() {
        Map<String, Object> context = new HashMap<>();
        context.put("ip", "172.16.0.1");
        context.put("device_id", "12345");
        Event event = new Event("acc-4", "login", context, System.currentTimeMillis());

        service.evaluate(event);
        service.evaluate(event);

        assertEquals(2, service.getKafkaAuditTelemetrySink().size());
        assertEquals("acc-4", service.getKafkaAuditTelemetrySink().get(0).event.accountId);
    }

    @Test
    public void testClusterConsensus() {
        assertTrue(service.checkClusterConsensus(), "Cluster should have consensus with 3 nodes");

        // Test with different cluster configuration
        DistributedBotDetectionPlatformService minorityService = new DistributedBotDetectionPlatformService("node-1", Arrays.asList("node-1"));
        assertTrue(minorityService.checkClusterConsensus(), "Cluster with 1 node always has consensus");
    }

    @Test
    public void testRateLimitingTriggersBlock() {
        Map<String, Object> context = new HashMap<>();
        context.put("ip", "172.16.0.2");
        context.put("device_id", "12345678"); // Good device

        long now = System.currentTimeMillis();

        // Spam requests to trigger rate limit (bucket capacity is 100 tokens, sending 101 requests)
        for (int i = 0; i < 100; i++) {
            Event event = new Event("acc-spam", "login", context, now + i);
            service.evaluate(event);
        }

        Event finalEvent = new Event("acc-spam", "login", context, now + 100);
        BotRiskResponse response = service.evaluate(finalEvent);

        assertEquals(RemediationAction.BLOCK, response.action);
        assertTrue(response.reasons.contains("rate_limited"));
    }
}
