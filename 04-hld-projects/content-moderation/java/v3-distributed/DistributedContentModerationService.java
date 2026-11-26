import java.time.Instant;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.HashSet;
import java.util.SortedMap;
import java.util.TreeMap;
import java.util.concurrent.ConcurrentHashMap;
import java.util.regex.Pattern;
import java.util.stream.Collectors;

public class DistributedContentModerationService {

    public enum ModerationStatus {
        PASS,
        FLAGGED,
        BLOCKED,
        NEEDS_REVIEW
    }

    public static class ContentEvent {
        private final String contentId;
        private final String authorId;
        private final String text;
        private final Instant createdAt;

        public ContentEvent(String contentId, String authorId, String text) {
            this(contentId, authorId, text, Instant.now());
        }

        public ContentEvent(String contentId, String authorId, String text, Instant createdAt) {
            this.contentId = contentId;
            this.authorId = authorId;
            this.text = text;
            this.createdAt = createdAt != null ? createdAt : Instant.now();
        }

        public String getContentId() { return contentId; }
        public String getAuthorId() { return authorId; }
        public String getText() { return text; }
        public Instant getCreatedAt() { return createdAt; }
    }

    public static class ModerationResult {
        private final String contentId;
        private final ModerationStatus status;
        private final String reason;
        private final double confidence;
        private final String shardId;
        private final Instant decidedAt;

        public ModerationResult(String contentId, ModerationStatus status, String reason, double confidence, String shardId) {
            this.contentId = contentId;
            this.status = status;
            this.reason = reason;
            this.confidence = confidence;
            this.shardId = shardId;
            this.decidedAt = Instant.now();
        }

        public String getContentId() { return contentId; }
        public ModerationStatus getStatus() { return status; }
        public String getReason() { return reason; }
        public double getConfidence() { return confidence; }
        public String getShardId() { return shardId; }
        public Instant getDecidedAt() { return decidedAt; }
    }

    public static class Policy {
        private final long version;
        private final Set<String> blocklist;
        private final List<Pattern> flagPatterns;
        private final boolean isFallbackDeterministic;

        public Policy(long version, Set<String> blocklist, List<Pattern> flagPatterns, boolean isFallbackDeterministic) {
            this.version = version;
            this.blocklist = blocklist != null ? new HashSet<>(blocklist) : new HashSet<>();
            this.flagPatterns = flagPatterns != null ? new ArrayList<>(flagPatterns) : new ArrayList<>();
            this.isFallbackDeterministic = isFallbackDeterministic;
        }

        public long getVersion() { return version; }
        public Set<String> getBlocklist() { return blocklist; }
        public List<Pattern> getFlagPatterns() { return flagPatterns; }
        public boolean isFallbackDeterministic() { return isFallbackDeterministic; }
    }

    // A mock external node for consensus
    public interface ConsensusNode {
        boolean agreeToBlock(ContentEvent event, Policy policy);
    }

    private final SortedMap<Integer, String> hashRing = new TreeMap<>();
    private final Map<String, Policy> regionPolicies = new ConcurrentHashMap<>();
    private final List<ConsensusNode> consensusNodes;
    private final int consensusThreshold;
    private final String currentRegion;

    private boolean isPartitioned = false; // Simulate cluster partition
    private volatile Policy activePolicy;

    public DistributedContentModerationService(
            List<String> shards,
            String currentRegion,
            Policy initialPolicy,
            List<ConsensusNode> consensusNodes,
            int consensusThreshold) {
        this.currentRegion = currentRegion;
        this.activePolicy = initialPolicy;
        this.consensusNodes = consensusNodes != null ? consensusNodes : new ArrayList<>();
        this.consensusThreshold = consensusThreshold;

        // Initialize consistent hash ring (3 virtual nodes per shard)
        if (shards != null) {
            for (String shard : shards) {
                for (int i = 0; i < 3; i++) {
                    hashRing.put(hash(shard + ":" + i), shard);
                }
            }
        }
    }

    private int hash(String key) {
        return key.hashCode() & Integer.MAX_VALUE;
    }

    public String routeShard(String routingKey) {
        if (hashRing.isEmpty()) {
            return "default-shard";
        }
        int hash = hash(routingKey);
        SortedMap<Integer, String> tailMap = hashRing.tailMap(hash);
        if (tailMap.isEmpty()) {
            return hashRing.get(hashRing.firstKey());
        }
        return tailMap.get(tailMap.firstKey());
    }

    public void syncPolicy(String region, Policy policy) {
        regionPolicies.put(region, policy);
        if (currentRegion.equals(region) || "global".equals(region)) {
            // Apply policy with the highest version
            if (activePolicy == null || policy.getVersion() > activePolicy.getVersion()) {
                this.activePolicy = policy;
            }
        }
    }

    public void setPartitioned(boolean partitioned) {
        this.isPartitioned = partitioned;
    }

    public ModerationResult evaluateContent(ContentEvent event) {
        String shardId = routeShard(event.getAuthorId());
        String textLower = event.getText().toLowerCase();

        Policy policy = this.activePolicy;
        if (policy == null) {
            return new ModerationResult(event.getContentId(), ModerationStatus.PASS, "No active policy", 0.0, shardId);
        }

        // Fast deterministic checks
        for (String word : policy.getBlocklist()) {
            if (textLower.contains(word)) {
                return new ModerationResult(event.getContentId(), ModerationStatus.BLOCKED, "Deterministic block: " + word, 1.0, shardId);
            }
        }

        boolean flagged = false;
        String flagReason = null;
        for (Pattern pattern : policy.getFlagPatterns()) {
            if (pattern.matcher(event.getText()).find()) {
                flagged = true;
                flagReason = "Flagged by pattern: " + pattern.pattern();
                break;
            }
        }

        if (flagged) {
            if (isPartitioned) {
                // Cluster partitioning fallback: use high-precision deterministic rules
                // If it's only flagged and not in blocklist, but we are partitioned, we might just pass or need manual review.
                if (policy.isFallbackDeterministic()) {
                    return new ModerationResult(event.getContentId(), ModerationStatus.PASS, "Partition fallback: bypassed flag", 0.0, shardId);
                } else {
                    return new ModerationResult(event.getContentId(), ModerationStatus.NEEDS_REVIEW, "Partition fallback: " + flagReason, 0.5, shardId);
                }
            }

            // Distributed consensus for high-severity
            int approvals = 0;
            for (ConsensusNode node : consensusNodes) {
                if (node.agreeToBlock(event, policy)) {
                    approvals++;
                }
            }
            if (approvals >= consensusThreshold) {
                return new ModerationResult(event.getContentId(), ModerationStatus.BLOCKED, "Consensus blocked", 0.9, shardId);
            }

            return new ModerationResult(event.getContentId(), ModerationStatus.NEEDS_REVIEW, flagReason, 0.8, shardId);
        }

        return new ModerationResult(event.getContentId(), ModerationStatus.PASS, "Passed all checks", 1.0, shardId);
    }
}
