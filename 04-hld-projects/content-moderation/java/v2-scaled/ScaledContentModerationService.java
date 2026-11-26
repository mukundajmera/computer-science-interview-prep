import java.time.Instant;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.HashSet;
import java.util.concurrent.ConcurrentHashMap;
import java.util.regex.Pattern;
import java.util.stream.Collectors;

public class ScaledContentModerationService {

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
        private final Instant decidedAt;

        public ModerationResult(String contentId, ModerationStatus status, String reason, double confidence) {
            this.contentId = contentId;
            this.status = status;
            this.reason = reason;
            this.confidence = confidence;
            this.decidedAt = Instant.now();
        }

        public String getContentId() { return contentId; }
        public ModerationStatus getStatus() { return status; }
        public String getReason() { return reason; }
        public double getConfidence() { return confidence; }
        public Instant getDecidedAt() { return decidedAt; }
    }

    public static class MLPrediction {
        private final boolean isHarmful;
        private final double confidence;
        private final String category;

        public MLPrediction(boolean isHarmful, double confidence, String category) {
            this.isHarmful = isHarmful;
            this.confidence = confidence;
            this.category = category;
        }

        public boolean isHarmful() { return isHarmful; }
        public double getConfidence() { return confidence; }
        public String getCategory() { return category; }
    }

    public interface MLModelService {
        MLPrediction predict(String text) throws Exception;
    }

    private static class ReviewItem {
        private final ContentEvent event;
        private final String reason;
        private final double confidence;
        private final List<Boolean> reviewerDecisions;

        public ReviewItem(ContentEvent event, String reason, double confidence) {
            this.event = event;
            this.reason = reason;
            this.confidence = confidence;
            this.reviewerDecisions = Collections.synchronizedList(new ArrayList<>());
        }

        public void addDecision(boolean approved) {
            reviewerDecisions.add(approved);
        }

        public int countApprovals() {
            return (int) reviewerDecisions.stream().filter(b -> b).count();
        }

        public int countRejections() {
            return (int) reviewerDecisions.stream().filter(b -> !b).count();
        }
    }

    private final Set<String> blocklist;
    private final List<Pattern> flagPatterns;
    private final MLModelService mlService;
    private final int mlTimeoutMs;
    private final int reviewConsensusThreshold;
    private final int maxQueueSize;

    private final Map<String, ReviewItem> reviewQueue;
    private final List<ModerationResult> auditLog;

    public ScaledContentModerationService(
            List<String> blocklist,
            List<String> flagPatterns,
            MLModelService mlService,
            int mlTimeoutMs,
            int reviewConsensusThreshold,
            int maxQueueSize) {

        this.blocklist = blocklist != null ?
            blocklist.stream().map(String::toLowerCase).collect(Collectors.toSet()) :
            new HashSet<>();

        this.flagPatterns = flagPatterns != null ?
            flagPatterns.stream().map(Pattern::compile).collect(Collectors.toList()) :
            new ArrayList<>();

        this.mlService = mlService;
        this.mlTimeoutMs = mlTimeoutMs;
        this.reviewConsensusThreshold = reviewConsensusThreshold;
        this.maxQueueSize = maxQueueSize;

        this.reviewQueue = new ConcurrentHashMap<>();
        this.auditLog = Collections.synchronizedList(new ArrayList<>());
    }

    public ModerationResult evaluateContent(ContentEvent event) {
        String textLower = event.getText().toLowerCase();

        // Tier 1: Fast heuristic check
        for (String word : blocklist) {
            if (textLower.contains(word)) {
                return recordDecision(event.getContentId(), ModerationStatus.BLOCKED, "Blocked keyword: " + word, 1.0);
            }
        }

        for (Pattern pattern : flagPatterns) {
            if (pattern.matcher(event.getText()).find()) {
                return enqueueReview(event, "Flagged by pattern: " + pattern.pattern(), 1.0);
            }
        }

        // Tier 2: ML Model Inference
        try {
            MLPrediction prediction = mlService.predict(event.getText());

            if (prediction.isHarmful()) {
                if (prediction.getConfidence() > 0.9) {
                    return recordDecision(event.getContentId(), ModerationStatus.BLOCKED, "ML blocked: " + prediction.getCategory(), prediction.getConfidence());
                } else if (prediction.getConfidence() > 0.6) {
                    return enqueueReview(event, "ML flagged: " + prediction.getCategory(), prediction.getConfidence());
                } else {
                    return recordDecision(event.getContentId(), ModerationStatus.PASS, "ML low confidence harmful", prediction.getConfidence());
                }
            } else {
                return recordDecision(event.getContentId(), ModerationStatus.PASS, "ML passed", prediction.getConfidence());
            }
        } catch (Exception e) {
            // Degraded mode fallback
            return recordDecision(event.getContentId(), ModerationStatus.PASS, "Degraded mode: " + e.getMessage(), 0.0);
        }
    }

    private ModerationResult enqueueReview(ContentEvent event, String reason, double confidence) {
        if (reviewQueue.size() >= maxQueueSize) {
            // Queue backpressure handling
            return recordDecision(event.getContentId(), ModerationStatus.PASS, "Queue full, degraded: " + reason, confidence);
        }

        ReviewItem item = new ReviewItem(event, reason, confidence);
        reviewQueue.put(event.getContentId(), item);
        return recordDecision(event.getContentId(), ModerationStatus.NEEDS_REVIEW, reason, confidence);
    }

    private ModerationResult recordDecision(String contentId, ModerationStatus status, String reason, double confidence) {
        ModerationResult result = new ModerationResult(contentId, status, reason, confidence);
        auditLog.add(result);
        return result;
    }

    public ModerationResult processReview(String contentId, boolean approved) {
        ReviewItem item = reviewQueue.get(contentId);
        if (item == null) {
            throw new IllegalArgumentException("Content " + contentId + " not found in review queue");
        }

        item.addDecision(approved);

        if (item.countApprovals() >= reviewConsensusThreshold) {
            reviewQueue.remove(contentId);
            return recordDecision(contentId, ModerationStatus.PASS, "Appeals consensus: approved", 1.0);
        } else if (item.countRejections() >= reviewConsensusThreshold) {
            reviewQueue.remove(contentId);
            return recordDecision(contentId, ModerationStatus.BLOCKED, "Appeals consensus: rejected", 1.0);
        }

        return null; // Need more reviews
    }

    public List<ContentEvent> getReviewQueue() {
        return reviewQueue.values().stream().map(item -> item.event).collect(Collectors.toList());
    }

    public List<ModerationResult> getAuditLog() {
        return Collections.unmodifiableList(new ArrayList<>(auditLog));
    }
}
