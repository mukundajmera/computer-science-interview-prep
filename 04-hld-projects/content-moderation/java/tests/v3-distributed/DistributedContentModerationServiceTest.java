import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import java.util.Arrays;
import java.util.List;
import java.util.Set;
import java.util.regex.Pattern;

import static org.junit.jupiter.api.Assertions.*;

public class DistributedContentModerationServiceTest {

    private DistributedContentModerationService.Policy policy1;
    private DistributedContentModerationService.Policy policy2;
    private DistributedContentModerationService.ConsensusNode rejectNode;
    private DistributedContentModerationService.ConsensusNode acceptNode;

    @BeforeEach
    public void setup() {
        policy1 = new DistributedContentModerationService.Policy(
            1,
            Set.of("badword"),
            List.of(Pattern.compile("flag\\d+")),
            true
        );
        policy2 = new DistributedContentModerationService.Policy(
            2,
            Set.of("worseword"),
            List.of(Pattern.compile("flag\\d+")),
            false
        );

        rejectNode = (event, policy) -> false;
        acceptNode = (event, policy) -> true;
    }

    @Test
    public void testConsistentHashShardRouting() {
        List<String> shards = Arrays.asList("shard-1", "shard-2", "shard-3");
        DistributedContentModerationService service = new DistributedContentModerationService(
            shards, "us-east", policy1, List.of(), 1
        );

        String shardUserA = service.routeShard("userA");
        String shardUserB = service.routeShard("userB");
        String shardUserC = service.routeShard("userC");

        assertTrue(shards.contains(shardUserA));
        assertTrue(shards.contains(shardUserB));
        assertTrue(shards.contains(shardUserC));

        // Same routing key gives same shard
        assertEquals(shardUserA, service.routeShard("userA"));
    }

    @Test
    public void testMultiDatacenterPolicySync() {
        DistributedContentModerationService service = new DistributedContentModerationService(
            List.of("s1"), "us-east", policy1, List.of(), 1
        );

        // Sync a newer policy for the current region
        service.syncPolicy("us-east", policy2);

        DistributedContentModerationService.ContentEvent event =
            new DistributedContentModerationService.ContentEvent("c1", "a1", "this has worseword in it");

        DistributedContentModerationService.ModerationResult result = service.evaluateContent(event);
        assertEquals(DistributedContentModerationService.ModerationStatus.BLOCKED, result.getStatus());
        assertTrue(result.getReason().contains("worseword"));
    }

    @Test
    public void testDistributedConsensusHighSeverity() {
        List<DistributedContentModerationService.ConsensusNode> nodes = Arrays.asList(acceptNode, acceptNode, rejectNode);
        DistributedContentModerationService service = new DistributedContentModerationService(
            List.of("s1"), "us-east", policy1, nodes, 2 // Threshold 2
        );

        // flagged by pattern
        DistributedContentModerationService.ContentEvent event =
            new DistributedContentModerationService.ContentEvent("c1", "a1", "this is flag123 pattern");

        DistributedContentModerationService.ModerationResult result = service.evaluateContent(event);
        assertEquals(DistributedContentModerationService.ModerationStatus.BLOCKED, result.getStatus());
        assertTrue(result.getReason().contains("Consensus blocked"));
    }

    @Test
    public void testClusterPartitioningFallback() {
        // Needs review normally, but in partitioned mode, with fallback deterministic = true, it just passes
        // to avoid manual review queues backing up
        DistributedContentModerationService service = new DistributedContentModerationService(
            List.of("s1"), "us-east", policy1, List.of(rejectNode, rejectNode), 2
        );

        DistributedContentModerationService.ContentEvent event =
            new DistributedContentModerationService.ContentEvent("c1", "a1", "this is flag123 pattern");

        // Not partitioned -> NEEDS_REVIEW
        DistributedContentModerationService.ModerationResult result1 = service.evaluateContent(event);
        assertEquals(DistributedContentModerationService.ModerationStatus.NEEDS_REVIEW, result1.getStatus());

        // Partitioned -> PASS (because policy1 isFallbackDeterministic = true)
        service.setPartitioned(true);
        DistributedContentModerationService.ModerationResult result2 = service.evaluateContent(event);
        assertEquals(DistributedContentModerationService.ModerationStatus.PASS, result2.getStatus());
        assertTrue(result2.getReason().contains("Partition fallback"));
    }

}
