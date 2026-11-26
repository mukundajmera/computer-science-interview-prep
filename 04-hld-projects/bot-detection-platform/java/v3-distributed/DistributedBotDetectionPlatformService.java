package v3.distributed;

import java.util.*;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.ConcurrentLinkedQueue;
import java.util.stream.Collectors;

public class DistributedBotDetectionPlatformService {

    public enum RemediationAction {
        PASS,
        CHALLENGE_SILENT_POW,
        CHALLENGE_CAPTCHA,
        BLOCK,
        SHADOW_BLOCK // For shadow mode testing without actually blocking
    }

    public static class BotRiskResponse {
        public double riskScore;
        public double confidence;
        public RemediationAction action;
        public List<String> reasons;
        public String policyVersion;
        public boolean queuedForInvestigation;

        public BotRiskResponse(double riskScore, double confidence, RemediationAction action, List<String> reasons, String policyVersion, boolean queuedForInvestigation) {
            this.riskScore = riskScore;
            this.confidence = confidence;
            this.action = action;
            this.reasons = reasons;
            this.policyVersion = policyVersion;
            this.queuedForInvestigation = queuedForInvestigation;
        }
    }

    public static class Event {
        public String accountId;
        public String action;
        public Map<String, Object> context;
        public long timestamp;

        public Event(String accountId, String action, Map<String, Object> context, long timestamp) {
            this.accountId = accountId;
            this.action = action;
            this.context = context != null ? context : new HashMap<>();
            this.timestamp = timestamp;
        }
    }

    public static class InvestigationTask {
        public String accountId;
        public double riskScore;
        public List<String> reasons;
        public long timestamp;

        public InvestigationTask(String accountId, double riskScore, List<String> reasons, long timestamp) {
            this.accountId = accountId;
            this.riskScore = riskScore;
            this.reasons = reasons;
            this.timestamp = timestamp;
        }
    }

    public static class AuditLog {
        public Event event;
        public BotRiskResponse response;
        public long timestamp;

        public AuditLog(Event event, BotRiskResponse response, long timestamp) {
            this.event = event;
            this.response = response;
            this.timestamp = timestamp;
        }
    }

    // Mock Kafka sink
    private final Queue<AuditLog> kafkaAuditTelemetrySink = new ConcurrentLinkedQueue<>();
    private final Queue<InvestigationTask> investigationQueue = new ConcurrentLinkedQueue<>();

    // Rate limiting properties
    private final Map<String, TreeMap<Long, Long>> accountVelocityCounters = new ConcurrentHashMap<>();
    private final Map<String, Double> leakyBuckets = new ConcurrentHashMap<>();
    private final Map<String, Long> lastLeakTimes = new ConcurrentHashMap<>();
    private final double bucketCapacity = 100.0;
    private final double leakRatePerMs = 100.0 / 60000.0; // 100 tokens per minute

    // Mock Redis Cluster for global IP reputation and sync
    private final Map<String, Double> redisIpReputationStore = new ConcurrentHashMap<>();

    // Mock Bloom Filter for quick global blocked IP checks (saves Redis round-trips for known bad IPs)
    private final Set<String> bloomFilterBlockedIps = ConcurrentHashMap.newKeySet();

    private boolean mlServiceAvailable = true;
    private boolean shadowModeEnabled = false;

    // Distributed cluster node ID
    private final String nodeId;
    // Simple consensus: list of known node IDs to report sync state
    private final List<String> clusterNodes;

    public DistributedBotDetectionPlatformService(String nodeId, List<String> clusterNodes) {
        this.nodeId = nodeId;
        this.clusterNodes = new ArrayList<>(clusterNodes);
    }

    public void setShadowModeEnabled(boolean enabled) {
        this.shadowModeEnabled = enabled;
    }

    public void setMlServiceAvailable(boolean available) {
        this.mlServiceAvailable = available;
    }

    // Update global IP reputation in Redis and sync with bloom filter if blocked
    public void updateGlobalIpReputation(String ip, double score) {
        redisIpReputationStore.put(ip, score);
        if (score >= 0.8) {
            bloomFilterBlockedIps.add(ip);
        } else {
            bloomFilterBlockedIps.remove(ip);
        }
    }

    public double getGlobalIpReputation(String ip) {
        return redisIpReputationStore.getOrDefault(ip, 0.0);
    }

    // Node consensus health check simulation
    public boolean checkClusterConsensus() {
        // Mocking consensus check: require majority (this node + others)
        int requiredMajority = (clusterNodes.size() / 2) + 1;
        int activeNodes = 1; // self is active
        for (String node : clusterNodes) {
            if (!node.equals(nodeId)) {
                activeNodes++; // simulate others are active
            }
        }
        return activeNodes >= requiredMajority;
    }

    private void recordVelocity(String accountId, long timestamp) {
        long bucket = timestamp / 1000;
        accountVelocityCounters.compute(accountId, (k, v) -> {
            if (v == null) {
                v = new TreeMap<>();
            }
            v.put(bucket, v.getOrDefault(bucket, 0L) + 1);
            long oneMinuteAgo = (timestamp - 60000) / 1000;
            v.headMap(oneMinuteAgo).clear();
            return v;
        });
    }

    private long getRecentEventsCount(String accountId, long timestamp) {
        TreeMap<Long, Long> counters = accountVelocityCounters.get(accountId);
        if (counters == null) return 0;
        long count = 0;
        long oneMinuteAgo = (timestamp - 60000) / 1000;
        for (Map.Entry<Long, Long> entry : counters.tailMap(oneMinuteAgo).entrySet()) {
            count += entry.getValue();
        }
        return count;
    }

    private boolean checkRateLimit(String accountId, long timestamp) {
        long lastTime = lastLeakTimes.getOrDefault(accountId, timestamp);
        double tokens = leakyBuckets.getOrDefault(accountId, bucketCapacity);

        long timePassed = timestamp - lastTime;
        if (timePassed > 0) {
            tokens += timePassed * leakRatePerMs;
            if (tokens > bucketCapacity) tokens = bucketCapacity;
        }

        if (tokens >= 1.0) {
            tokens -= 1.0;
            leakyBuckets.put(accountId, tokens);
            lastLeakTimes.put(accountId, timestamp);
            return false;
        } else {
            leakyBuckets.put(accountId, tokens);
            lastLeakTimes.put(accountId, timestamp);
            return true;
        }
    }

    public BotRiskResponse evaluate(Event currentEvent) {
        long now = currentEvent.timestamp;
        String accountId = currentEvent.accountId;
        String ip = (String) currentEvent.context.getOrDefault("ip", "");

        recordVelocity(accountId, now);
        boolean isRateLimited = checkRateLimit(accountId, now);
        long recentEventsCount = getRecentEventsCount(accountId, now);
        double velocityScore = Math.min(1.0, recentEventsCount / 50.0);

        // Fast path check using Bloom Filter
        double ipRepScore = 0.0;
        if (bloomFilterBlockedIps.contains(ip)) {
            ipRepScore = 1.0;
        } else {
            ipRepScore = redisIpReputationStore.getOrDefault(ip, 0.0);
        }

        String deviceId = (String) currentEvent.context.getOrDefault("device_id", "");
        double deviceEntropyScore = deviceId.isEmpty() ? 0.8 : (deviceId.length() < 5 ? 0.5 : 0.1);

        double riskScore;
        double confidence;
        List<String> reasons = new ArrayList<>();

        if (mlServiceAvailable) {
            riskScore = (velocityScore * 0.3) + (ipRepScore * 0.6) + (deviceEntropyScore * 0.1);
            confidence = 0.5 + (Math.min(recentEventsCount, 100) / 200.0);
        } else {
            riskScore = Math.max(velocityScore, ipRepScore);
            confidence = 0.4;
            reasons.add("degraded_rule_mode");
        }

        if (isRateLimited) {
            riskScore = Math.max(riskScore, 0.85);
            reasons.add("rate_limited");
        }

        riskScore = Math.min(1.0, Math.max(0.0, riskScore));

        if (velocityScore > 0.6) reasons.add("velocity_spike");
        if (ipRepScore > 0.6) reasons.add("bad_ip_reputation");
        if (deviceEntropyScore > 0.6) reasons.add("device_anomaly");

        RemediationAction action;
        boolean queueForInvestigation = false;

        if (riskScore >= 0.8) {
            action = shadowModeEnabled ? RemediationAction.SHADOW_BLOCK : RemediationAction.BLOCK;
        } else if (riskScore >= 0.6) {
            action = RemediationAction.CHALLENGE_CAPTCHA;
            queueForInvestigation = true;
        } else if (riskScore >= 0.4) {
            action = RemediationAction.CHALLENGE_SILENT_POW;
        } else {
            action = RemediationAction.PASS;
        }

        if (queueForInvestigation) {
            investigationQueue.add(new InvestigationTask(accountId, riskScore, reasons, now));
        }

        BotRiskResponse response = new BotRiskResponse(riskScore, confidence, action, reasons, "v3-distributed-policy", queueForInvestigation);

        // Push to Kafka audit telemetry sink
        kafkaAuditTelemetrySink.add(new AuditLog(currentEvent, response, now));

        return response;
    }

    public List<InvestigationTask> getInvestigationQueue() {
        return new ArrayList<>(investigationQueue);
    }

    public List<AuditLog> getKafkaAuditTelemetrySink() {
        return new ArrayList<>(kafkaAuditTelemetrySink);
    }
}
