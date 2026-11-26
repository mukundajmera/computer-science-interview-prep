package v2_scaled;

import java.util.*;
import java.util.concurrent.*;
import java.util.stream.Collectors;

public class ScaledContentModerationPlatformService {

    public enum Action {
        ALLOW,
        DEMOTE,
        ESCALATE_TO_HUMAN,
        AUTO_REMOVE
    }

    public static class ModerationRequest {
        public String contentId;
        public String text;
        public List<String> mediaRefs;
        public String surface;

        public ModerationRequest(String contentId, String text, List<String> mediaRefs, String surface) {
            this.contentId = contentId;
            this.text = text;
            this.mediaRefs = mediaRefs != null ? new ArrayList<>(mediaRefs) : new ArrayList<>();
            this.surface = surface;
        }
    }

    public static class ModerationResponse {
        public double riskScore;
        public double confidence;
        public Action action;
        public List<String> reasons;
        public String policyVersion;

        public ModerationResponse(double riskScore, double confidence, Action action, List<String> reasons, String policyVersion) {
            this.riskScore = riskScore;
            this.confidence = confidence;
            this.action = action;
            this.reasons = new ArrayList<>(reasons);
            this.policyVersion = policyVersion;
        }
    }

    public static class Policy {
        public String version;
        public double autoRemoveThreshold;
        public double escalateThreshold;
        public double demoteThreshold;

        public Policy(String version, double autoRemoveThreshold, double escalateThreshold, double demoteThreshold) {
            this.version = version;
            this.autoRemoveThreshold = autoRemoveThreshold;
            this.escalateThreshold = escalateThreshold;
            this.demoteThreshold = demoteThreshold;
        }
    }

    public static class ReviewTask implements Comparable<ReviewTask> {
        public String taskId;
        public String contentId;
        public int priority;
        public long createdAt;
        public Map<String, Action> reviewerVotes = new HashMap<>();
        public boolean resolved;
        public Action finalAction;

        public ReviewTask(String contentId, int priority) {
            this.taskId = UUID.randomUUID().toString();
            this.contentId = contentId;
            this.priority = priority;
            this.createdAt = System.currentTimeMillis();
            this.resolved = false;
        }

        @Override
        public int compareTo(ReviewTask other) {
            if (this.priority != other.priority) {
                return Integer.compare(other.priority, this.priority); // Higher priority first
            }
            return Long.compare(this.createdAt, other.createdAt); // Older tasks first
        }
    }

    public static class AuditRecord {
        public String contentId;
        public ModerationResponse initialDecision;
        public Action finalAction;
        public long decidedAt;

        public AuditRecord(String contentId, ModerationResponse initialDecision, Action finalAction, long decidedAt) {
            this.contentId = contentId;
            this.initialDecision = initialDecision;
            this.finalAction = finalAction;
            this.decidedAt = decidedAt;
        }
    }

    private Policy activePolicy;
    private final Map<String, Policy> policyCache = new ConcurrentHashMap<>();
    private final PriorityBlockingQueue<ReviewTask> reviewQueue = new PriorityBlockingQueue<>();
    private final List<AuditRecord> auditLedger = new CopyOnWriteArrayList<>();
    private final ExecutorService executor;
    private final Map<String, ReviewTask> taskMap = new ConcurrentHashMap<>();

    public ScaledContentModerationPlatformService(Policy initialPolicy, int threadPoolSize) {
        this.activePolicy = initialPolicy;
        this.policyCache.put(initialPolicy.version, initialPolicy);
        this.executor = Executors.newFixedThreadPool(threadPoolSize);
    }

    public void updatePolicy(Policy newPolicy) {
        this.policyCache.put(newPolicy.version, newPolicy);
        this.activePolicy = newPolicy;
    }

    public void rollbackPolicy(String version) {
        if (policyCache.containsKey(version)) {
            this.activePolicy = policyCache.get(version);
        } else {
            throw new IllegalArgumentException("Policy version not found in cache: " + version);
        }
    }

    public Policy getActivePolicy() {
        return this.activePolicy;
    }

    // Models
    private CompletableFuture<ModelResult> runTextSafetyModel(String text) {
        return CompletableFuture.supplyAsync(() -> {
            // Simulated model
            if (text == null || text.isEmpty()) {
                return new ModelResult(0.0, 1.0, Collections.emptyList());
            }
            String lower = text.toLowerCase();
            List<String> reasons = new ArrayList<>();
            double score = 0.0;
            double conf = 0.9;
            if (lower.contains("hate")) {
                score += 0.8;
                reasons.add("hate_speech");
            }
            if (lower.contains("spam")) {
                score += 0.5;
                reasons.add("spam");
            }
            return new ModelResult(Math.min(score, 1.0), conf, reasons);
        }, executor);
    }

    private CompletableFuture<ModelResult> runMediaHashCheck(List<String> mediaRefs) {
        return CompletableFuture.supplyAsync(() -> {
            // Simulated media check
            if (mediaRefs == null || mediaRefs.isEmpty()) {
                return new ModelResult(0.0, 1.0, Collections.emptyList());
            }
            List<String> reasons = new ArrayList<>();
            double score = 0.0;
            double conf = 0.8;
            for (String ref : mediaRefs) {
                if (ref.contains("bad")) {
                    score += 0.9;
                    reasons.add("known_bad_media");
                } else {
                    score += 0.1;
                    reasons.add("unknown_media");
                    conf -= 0.1;
                }
            }
            return new ModelResult(Math.min(score, 1.0), Math.max(0.1, conf), reasons);
        }, executor);
    }

    private static class ModelResult {
        double score;
        double confidence;
        List<String> reasons;
        ModelResult(double s, double c, List<String> r) { score = s; confidence = c; reasons = r; }
    }

    public CompletableFuture<ModerationResponse> evaluateAsync(ModerationRequest request) {
        Policy policy = this.activePolicy;

        CompletableFuture<ModelResult> textCheck = runTextSafetyModel(request.text);
        CompletableFuture<ModelResult> mediaCheck = runMediaHashCheck(request.mediaRefs);

        return textCheck.thenCombine(mediaCheck, (textRes, mediaRes) -> {
            double finalScore = Math.max(textRes.score, mediaRes.score);
            double finalConfidence = Math.min(textRes.confidence, mediaRes.confidence);
            List<String> allReasons = new ArrayList<>();
            allReasons.addAll(textRes.reasons);
            allReasons.addAll(mediaRes.reasons);

            Action action;
            int priority = 0;
            if (finalScore >= policy.autoRemoveThreshold) {
                action = Action.AUTO_REMOVE;
            } else if (finalScore >= policy.escalateThreshold) {
                action = Action.ESCALATE_TO_HUMAN;
                priority = (int)(finalScore * 100); // Higher score -> higher priority
            } else if (finalScore >= policy.demoteThreshold) {
                action = Action.DEMOTE;
            } else {
                action = Action.ALLOW;
            }

            ModerationResponse response = new ModerationResponse(finalScore, finalConfidence, action, allReasons, policy.version);

            auditLedger.add(new AuditRecord(request.contentId, response, action, System.currentTimeMillis()));

            if (action == Action.ESCALATE_TO_HUMAN) {
                ReviewTask task = new ReviewTask(request.contentId, priority);
                reviewQueue.offer(task);
                taskMap.put(task.taskId, task);
            }

            return response;
        });
    }

    public ReviewTask getNextReviewTask() {
        return reviewQueue.poll();
    }

    public boolean submitReviewVote(String taskId, String reviewerId, Action vote, int requiredConsensusSize) {
        ReviewTask task = taskMap.get(taskId);
        if (task == null || task.resolved) {
            return false;
        }

        synchronized (task) {
            if (task.resolved) return false;
            task.reviewerVotes.put(reviewerId, vote);

            if (task.reviewerVotes.size() >= requiredConsensusSize) {
                // Determine majority vote
                Map<Action, Long> counts = task.reviewerVotes.values().stream()
                        .collect(Collectors.groupingBy(v -> v, Collectors.counting()));

                Action majorityAction = Action.ESCALATE_TO_HUMAN; // fallback
                long maxVotes = -1;
                for (Map.Entry<Action, Long> entry : counts.entrySet()) {
                    if (entry.getValue() > maxVotes) {
                        maxVotes = entry.getValue();
                        majorityAction = entry.getKey();
                    }
                }

                // For a true majority, we'd check if maxVotes > requiredConsensusSize / 2
                // We'll just take the plurality for simplicity or majority if strictly defined.
                task.finalAction = majorityAction;
                task.resolved = true;

                // Update audit ledger
                for (AuditRecord record : auditLedger) {
                    if (record.contentId.equals(task.contentId)) {
                        record.finalAction = majorityAction;
                        record.decidedAt = System.currentTimeMillis();
                    }
                }
                return true;
            }
        }
        return false;
    }

    public List<AuditRecord> getAuditLedger() {
        return new ArrayList<>(auditLedger);
    }

    public void shutdown() {
        executor.shutdown();
    }
}
