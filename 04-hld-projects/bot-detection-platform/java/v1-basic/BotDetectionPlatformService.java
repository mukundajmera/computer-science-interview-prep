package v1.basic;

import java.util.*;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.ConcurrentLinkedQueue;
import java.util.stream.Collectors;

public class BotDetectionPlatformService {

    public enum RemediationAction {
        PASS,
        CHALLENGE_CAPTCHA,
        BLOCK
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

    // In-memory data stores for v1
    private final Map<String, List<Event>> accountEvents = new ConcurrentHashMap<>();
    private final Queue<InvestigationTask> investigationQueue = new ConcurrentLinkedQueue<>();

    // Mock features/configuration for IP reputation & device fingerprint entropy
    private final Map<String, Double> ipReputationScores = new ConcurrentHashMap<>();

    public BotDetectionPlatformService() {
    }

    public void setIpReputation(String ip, double score) {
        ipReputationScores.put(ip, score);
    }

    public void ingestEvent(Event event) {
        accountEvents.computeIfAbsent(event.accountId, k -> Collections.synchronizedList(new ArrayList<>())).add(event);
    }

    public BotRiskResponse evaluate(Event currentEvent) {
        // Ingest the event as part of evaluation pipeline
        ingestEvent(currentEvent);

        List<Event> history = accountEvents.get(currentEvent.accountId);
        if (history == null) history = new ArrayList<>();

        long now = currentEvent.timestamp;

        // Multi-signal feature extraction

        // 1. Behavioral velocity (events in last 60 seconds)
        long oneMinuteAgo = now - 60000;
        long recentEventsCount = history.stream()
                .filter(e -> e.timestamp >= oneMinuteAgo)
                .count();
        double velocityScore = Math.min(1.0, recentEventsCount / 50.0); // Normalizing over 50 events/min

        // 2. IP reputation (e.g. 0.0 is good, 1.0 is bad)
        String ip = (String) currentEvent.context.getOrDefault("ip", "");
        double ipRepScore = ipReputationScores.getOrDefault(ip, 0.0);

        // 3. Device fingerprint entropy (mocked simply by presence/format of device_id)
        String deviceId = (String) currentEvent.context.getOrDefault("device_id", "");
        double deviceEntropyScore = deviceId.isEmpty() ? 0.8 : (deviceId.length() < 5 ? 0.5 : 0.1);

        // Combine features for risk score (simple weighted sum)
        double riskScore = (velocityScore * 0.3) + (ipRepScore * 0.6) + (deviceEntropyScore * 0.1);
        riskScore = Math.min(1.0, Math.max(0.0, riskScore));

        double confidence = 0.5 + (Math.min(history.size(), 100) / 200.0); // Confidence grows with history size up to 1.0

        List<String> reasons = new ArrayList<>();
        if (velocityScore > 0.6) reasons.add("velocity_spike");
        if (ipRepScore > 0.6) reasons.add("bad_ip_reputation");
        if (deviceEntropyScore > 0.6) reasons.add("device_anomaly");

        RemediationAction action;
        boolean queueForInvestigation = false;

        // Tiered scoring engine
        if (riskScore >= 0.8) {
            action = RemediationAction.BLOCK;
        } else if (riskScore >= 0.5) {
            action = RemediationAction.CHALLENGE_CAPTCHA;
            queueForInvestigation = true;
        } else {
            action = RemediationAction.PASS;
        }

        if (queueForInvestigation) {
            investigationQueue.add(new InvestigationTask(currentEvent.accountId, riskScore, reasons, now));
        }

        return new BotRiskResponse(riskScore, confidence, action, reasons, "v1-basic-policy", queueForInvestigation);
    }

    public List<InvestigationTask> getInvestigationQueue() {
        return new ArrayList<>(investigationQueue);
    }
}
