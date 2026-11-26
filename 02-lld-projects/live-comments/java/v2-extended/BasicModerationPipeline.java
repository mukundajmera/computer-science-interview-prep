import java.util.Set;

public class BasicModerationPipeline implements ModerationPipeline {
    private final Set<String> blockedWords;

    public BasicModerationPipeline(Set<String> blockedWords) {
        this.blockedWords = blockedWords;
    }

    @Override
    public boolean isApproved(String payload) {
        if (payload == null || payload.trim().isEmpty()) {
            return false;
        }
        String lowerPayload = payload.toLowerCase();
        for (String word : blockedWords) {
            if (lowerPayload.contains(word.toLowerCase())) {
                return false;
            }
        }
        return true;
    }
}
