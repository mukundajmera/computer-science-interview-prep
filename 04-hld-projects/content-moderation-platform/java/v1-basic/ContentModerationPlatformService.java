import java.util.*;
import java.util.regex.Pattern;

public class ContentModerationPlatformService {

    public enum Action {
        ALLOW,
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

    private final List<String> blocklistKeywords;
    private final List<Pattern> blocklistPatterns;
    private final List<String> warningKeywords;
    private final List<AuditRecord> auditLedger;
    private final String currentPolicyVersion = "p1.0";

    public ContentModerationPlatformService(List<String> blocklistKeywords, List<String> warningKeywords, List<String> regexPatterns) {
        this.blocklistKeywords = blocklistKeywords != null ? new ArrayList<>(blocklistKeywords) : new ArrayList<>();
        this.warningKeywords = warningKeywords != null ? new ArrayList<>(warningKeywords) : new ArrayList<>();

        this.blocklistPatterns = new ArrayList<>();
        if (regexPatterns != null) {
            for (String regex : regexPatterns) {
                this.blocklistPatterns.add(Pattern.compile(regex, Pattern.CASE_INSENSITIVE));
            }
        }

        this.auditLedger = new ArrayList<>();
    }

    public ModerationResponse evaluate(ModerationRequest request) {
        List<String> reasons = new ArrayList<>();
        double riskScore = 0.0;
        double confidence = 1.0;

        if (request.text != null) {
            String lowerText = request.text.toLowerCase();

            for (String keyword : blocklistKeywords) {
                if (lowerText.contains(keyword.toLowerCase())) {
                    reasons.add("blocklist_keyword_match: " + keyword);
                    riskScore += 0.8;
                }
            }

            for (Pattern pattern : blocklistPatterns) {
                if (pattern.matcher(request.text).find()) {
                    reasons.add("regex_match: " + pattern.pattern());
                    riskScore += 0.8;
                }
            }

            for (String keyword : warningKeywords) {
                if (lowerText.contains(keyword.toLowerCase())) {
                    reasons.add("warning_keyword_match: " + keyword);
                    riskScore += 0.4;
                }
            }
        }

        if (request.mediaRefs != null && !request.mediaRefs.isEmpty()) {
            reasons.add("media_present");
            riskScore += 0.1;
            confidence -= 0.1; // lower confidence for media metadata only
        }

        riskScore = Math.min(riskScore, 1.0);

        Action action;
        if (riskScore >= 0.8) {
            action = Action.AUTO_REMOVE;
        } else if (riskScore >= 0.4) {
            action = Action.ESCALATE_TO_HUMAN;
        } else {
            action = Action.ALLOW;
        }

        ModerationResponse response = new ModerationResponse(riskScore, confidence, action, reasons, currentPolicyVersion);

        auditLedger.add(new AuditRecord(request.contentId, response, action, System.currentTimeMillis()));

        return response;
    }

    public void recordModeratorDecision(String contentId, Action finalAction) {
        for (AuditRecord record : auditLedger) {
            if (record.contentId.equals(contentId)) {
                record.finalAction = finalAction;
                record.decidedAt = System.currentTimeMillis();
            }
        }
    }

    public List<AuditRecord> getAuditLedger() {
        return new ArrayList<>(auditLedger);
    }
}
