package v3_distributed;

import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;
import java.util.List;

public class DistributedContentModerationPlatformServiceTest {

    @Test
    void testKafkaPartitionMock() {
        DistributedContentModerationPlatformService.KafkaPartitionMock kafka =
            new DistributedContentModerationPlatformService.KafkaPartitionMock(3);

        DistributedContentModerationPlatformService.ModerationEvent event1 =
            new DistributedContentModerationPlatformService.ModerationEvent("c1", "actor1", "text1", 100);
        DistributedContentModerationPlatformService.ModerationEvent event2 =
            new DistributedContentModerationPlatformService.ModerationEvent("c2", "actor2", "text2", 101);

        kafka.publish(event1);
        kafka.publish(event2);

        int p1 = Math.abs("actor1".hashCode()) % 3;
        int p2 = Math.abs("actor2".hashCode()) % 3;

        assertEquals(event1, kafka.consume(p1));
        assertEquals(event2, kafka.consume(p2));
    }

    @Test
    void testLwwPolicyCacheReplicationAndConflictResolution() {
        DistributedContentModerationPlatformService.LwwPolicyCache usEast = new DistributedContentModerationPlatformService.LwwPolicyCache("us-east");
        DistributedContentModerationPlatformService.LwwPolicyCache euWest = new DistributedContentModerationPlatformService.LwwPolicyCache("eu-west");

        usEast.addPeer(euWest);
        euWest.addPeer(usEast);

        // Concurrent update with different timestamps
        DistributedContentModerationPlatformService.Policy p1 = new DistributedContentModerationPlatformService.Policy("v1", 0.9, 1000);
        usEast.updatePolicy("violence", p1);

        assertEquals(0.9, usEast.getPolicy("violence").removeThreshold);
        assertEquals(0.9, euWest.getPolicy("violence").removeThreshold);

        // Conflict: older timestamp should be ignored
        DistributedContentModerationPlatformService.Policy pOld = new DistributedContentModerationPlatformService.Policy("v0", 0.8, 900);
        euWest.updatePolicy("violence", pOld);

        assertEquals(0.9, usEast.getPolicy("violence").removeThreshold); // Still v1
        assertEquals(0.9, euWest.getPolicy("violence").removeThreshold); // Still v1

        // Conflict: same timestamp, higher version string wins
        DistributedContentModerationPlatformService.Policy pTieBreaker = new DistributedContentModerationPlatformService.Policy("v2", 0.95, 1000);
        euWest.updatePolicy("violence", pTieBreaker);

        assertEquals(0.95, usEast.getPolicy("violence").removeThreshold);
        assertEquals(0.95, euWest.getPolicy("violence").removeThreshold);
    }

    @Test
    void testCanaryRouterShadowTraffic() {
        DistributedContentModerationPlatformService.ModelInference primary = event -> new DistributedContentModerationPlatformService.InferenceResult(0.8, 0.9);
        DistributedContentModerationPlatformService.ModelInference canary = event -> new DistributedContentModerationPlatformService.InferenceResult(0.85, 0.92);

        DistributedContentModerationPlatformService.CanaryRouter router = new DistributedContentModerationPlatformService.CanaryRouter(primary, canary, 0.0); // 0% natural shadow

        DistributedContentModerationPlatformService.ModerationEvent event = new DistributedContentModerationPlatformService.ModerationEvent("c1", "a1", "test", 1);

        // No shadow
        router.process(event, false);
        assertEquals(0, router.getShadowEvaluations().size());

        // Force shadow
        DistributedContentModerationPlatformService.InferenceResult result = router.process(event, true);
        assertEquals(0.8, result.riskScore); // Should return primary result
        assertEquals(1, router.getShadowEvaluations().size());
        assertTrue(router.getShadowEvaluations().get(0).contains("Primary(0.80)"));
        assertTrue(router.getShadowEvaluations().get(0).contains("Canary(0.85)"));
    }

    @Test
    void testAuditLedgerIntegrity() {
        DistributedContentModerationPlatformService.AuditLedger ledger = new DistributedContentModerationPlatformService.AuditLedger();

        ledger.appendRecord("c1", "remove", "violence", 100);
        ledger.appendRecord("c2", "demote", "spam", 101);

        assertTrue(ledger.verifyIntegrity());

        List<DistributedContentModerationPlatformService.AuditRecord> records = ledger.getRecords();
        assertEquals(2, records.size());

        // Tamper with the ledger
        DistributedContentModerationPlatformService.AuditRecord original = records.get(0);
        DistributedContentModerationPlatformService.AuditRecord tampered = new DistributedContentModerationPlatformService.AuditRecord(
            original.contentId, "allow", "tampered", original.timestamp, original.previousHash);

        ledger.tamperRecord(0, tampered);

        // Integrity check should fail because the next record's previousHash won't match the tampered record's hash
        assertFalse(ledger.verifyIntegrity());
    }
}
