package v3_distributed;

import java.util.*;
import java.util.concurrent.*;

public class DistributedContentModerationPlatformService {

    public static class ModerationEvent {
        public String contentId;
        public String actorId;
        public String text;
        public long timestamp;

        public ModerationEvent(String contentId, String actorId, String text, long timestamp) {
            this.contentId = contentId;
            this.actorId = actorId;
            this.text = text;
            this.timestamp = timestamp;
        }
    }

    // 1. Distributed streaming pipeline (Kafka partition mock by actor_id)
    public static class KafkaPartitionMock {
        private final int numPartitions;
        private final List<Queue<ModerationEvent>> partitions;

        public KafkaPartitionMock(int numPartitions) {
            this.numPartitions = numPartitions;
            this.partitions = new ArrayList<>();
            for (int i = 0; i < numPartitions; i++) {
                partitions.add(new ConcurrentLinkedQueue<>());
            }
        }

        public void publish(ModerationEvent event) {
            int partitionIndex = Math.abs(event.actorId.hashCode()) % numPartitions;
            partitions.get(partitionIndex).offer(event);
        }

        public ModerationEvent consume(int partitionIndex) {
            return partitions.get(partitionIndex).poll();
        }

        public int getNumPartitions() {
            return numPartitions;
        }
    }

    // 2. Multi-region active-active policy cache sync with conflict-free replication (LWW)
    public static class Policy {
        public String version;
        public double removeThreshold;
        public long timestamp;

        public Policy(String version, double removeThreshold, long timestamp) {
            this.version = version;
            this.removeThreshold = removeThreshold;
            this.timestamp = timestamp;
        }
    }

    public static class LwwPolicyCache {
        private final String region;
        private final ConcurrentHashMap<String, Policy> policies = new ConcurrentHashMap<>();
        private final List<LwwPolicyCache> peers = new ArrayList<>();

        public LwwPolicyCache(String region) {
            this.region = region;
        }

        public void addPeer(LwwPolicyCache peer) {
            peers.add(peer);
        }

        public void updatePolicy(String category, Policy newPolicy) {
            syncPolicy(category, newPolicy);
            // Replicate to peers
            for (LwwPolicyCache peer : peers) {
                peer.syncPolicy(category, newPolicy);
            }
        }

        public void syncPolicy(String category, Policy newPolicy) {
            policies.compute(category, (k, current) -> {
                if (current == null || newPolicy.timestamp > current.timestamp) {
                    return newPolicy;
                } else if (newPolicy.timestamp == current.timestamp && newPolicy.version.compareTo(current.version) > 0) {
                    return newPolicy; // tie-breaker
                }
                return current;
            });
        }

        public Policy getPolicy(String category) {
            return policies.get(category);
        }
    }

    // 3. ML inference canary router with shadow traffic evaluation
    public static class InferenceResult {
        public double riskScore;
        public double confidence;

        public InferenceResult(double riskScore, double confidence) {
            this.riskScore = riskScore;
            this.confidence = confidence;
        }
    }

    public interface ModelInference {
        InferenceResult evaluate(ModerationEvent event);
    }

    public static class CanaryRouter {
        private final ModelInference primaryModel;
        private final ModelInference canaryModel;
        private final double shadowTrafficRatio;
        private final List<String> shadowEvaluations;

        public CanaryRouter(ModelInference primaryModel, ModelInference canaryModel, double shadowTrafficRatio) {
            this.primaryModel = primaryModel;
            this.canaryModel = canaryModel;
            this.shadowTrafficRatio = shadowTrafficRatio;
            this.shadowEvaluations = new CopyOnWriteArrayList<>();
        }

        public InferenceResult process(ModerationEvent event, boolean forceShadow) {
            InferenceResult primaryResult = primaryModel.evaluate(event);

            // Shadow traffic
            if (forceShadow || Math.random() < shadowTrafficRatio) {
                InferenceResult canaryResult = canaryModel.evaluate(event);
                evaluateShadow(event.contentId, primaryResult, canaryResult);
            }

            return primaryResult;
        }

        private void evaluateShadow(String contentId, InferenceResult primary, InferenceResult canary) {
            shadowEvaluations.add(String.format("Content %s: Primary(%.2f), Canary(%.2f)", contentId, primary.riskScore, canary.riskScore));
        }

        public List<String> getShadowEvaluations() {
            return shadowEvaluations;
        }
    }

    // 4. Audit compliance immutable ledger
    public static class AuditRecord {
        public final String contentId;
        public final String action;
        public final String reason;
        public final long timestamp;
        public final String previousHash;
        public final String hash;

        public AuditRecord(String contentId, String action, String reason, long timestamp, String previousHash) {
            this.contentId = contentId;
            this.action = action;
            this.reason = reason;
            this.timestamp = timestamp;
            this.previousHash = previousHash;
            this.hash = generateHash();
        }

        private String generateHash() {
            // Simple hash mock
            return Integer.toHexString(Objects.hash(contentId, action, reason, timestamp, previousHash));
        }
    }

    public static class AuditLedger {
        private final List<AuditRecord> ledger = new ArrayList<>();
        private String lastHash = "0"; // Genesis hash

        public synchronized void appendRecord(String contentId, String action, String reason, long timestamp) {
            AuditRecord record = new AuditRecord(contentId, action, reason, timestamp, lastHash);
            ledger.add(record);
            lastHash = record.hash;
        }

        public synchronized List<AuditRecord> getRecords() {
            return new ArrayList<>(ledger);
        }

        public synchronized boolean verifyIntegrity() {
            String expectedPrevious = "0";
            for (AuditRecord record : ledger) {
                if (!record.previousHash.equals(expectedPrevious)) {
                    return false;
                }
                expectedPrevious = record.hash;
            }
            return true;
        }

        // Simulates tampering to verify integrity check fails
        public synchronized void tamperRecord(int index, AuditRecord newRecord) {
            if (index >= 0 && index < ledger.size()) {
                ledger.set(index, newRecord);
            }
        }
    }
}
