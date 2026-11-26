import java.time.Instant;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.Optional;
import java.util.Set;
import java.util.HashSet;
import java.util.regex.Pattern;
import java.util.stream.Collectors;

public class ContentModerationService {

    public enum ModerationStatus {
        PASS,
        FLAGGED,
        BLOCKED
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
        private final Instant decidedAt;

        public ModerationResult(String contentId, ModerationStatus status, String reason) {
            this.contentId = contentId;
            this.status = status;
            this.reason = reason;
            this.decidedAt = Instant.now();
        }

        public String getContentId() { return contentId; }
        public ModerationStatus getStatus() { return status; }
        public String getReason() { return reason; }
        public Instant getDecidedAt() { return decidedAt; }
    }

    private final Set<String> blocklist;
    private final List<Pattern> flagPatterns;
    private final List<ContentEvent> reviewQueue;
    private final List<ModerationResult> auditLog;

    public ContentModerationService(List<String> blocklist, List<String> flagPatterns) {
        this.blocklist = blocklist != null ?
            blocklist.stream().map(String::toLowerCase).collect(Collectors.toSet()) :
            new HashSet<>();

        this.flagPatterns = flagPatterns != null ?
            flagPatterns.stream().map(Pattern::compile).collect(Collectors.toList()) :
            new ArrayList<>();

        this.reviewQueue = new ArrayList<>();
        this.auditLog = new ArrayList<>();
    }

    public ModerationResult evaluateContent(ContentEvent event) {
        String textLower = event.getText().toLowerCase();

        // 1. Check for blocked keywords
        for (String word : blocklist) {
            if (textLower.contains(word)) {
                return recordDecision(event.getContentId(), ModerationStatus.BLOCKED, "Blocked keyword: " + word);
            }
        }

        // 2. Check for flagged patterns
        for (Pattern pattern : flagPatterns) {
            if (pattern.matcher(event.getText()).find()) {
                reviewQueue.add(event);
                return recordDecision(event.getContentId(), ModerationStatus.FLAGGED, "Flagged by pattern: " + pattern.pattern());
            }
        }

        // 3. Default to PASS
        return recordDecision(event.getContentId(), ModerationStatus.PASS, null);
    }

    private ModerationResult recordDecision(String contentId, ModerationStatus status, String reason) {
        ModerationResult result = new ModerationResult(contentId, status, reason);
        auditLog.add(result);
        return result;
    }

    public List<ContentEvent> getReviewQueue() {
        return Collections.unmodifiableList(new ArrayList<>(reviewQueue));
    }

    public ModerationResult processReview(String contentId, boolean approved) {
        Optional<ContentEvent> targetEvent = reviewQueue.stream()
            .filter(e -> e.getContentId().equals(contentId))
            .findFirst();

        if (targetEvent.isEmpty()) {
            throw new IllegalArgumentException("Content " + contentId + " not found in review queue");
        }

        reviewQueue.remove(targetEvent.get());

        ModerationStatus status = approved ? ModerationStatus.PASS : ModerationStatus.BLOCKED;
        String reason = approved ? "Human review approved" : "Human review rejected";

        return recordDecision(contentId, status, reason);
    }

    public List<ModerationResult> getAuditLog() {
        return Collections.unmodifiableList(new ArrayList<>(auditLog));
    }
}
