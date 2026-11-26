import java.util.List;
import java.util.Optional;

interface IdempotencyStore {
    boolean claim(String key, long ttlMs);
}

// In V3, we want to replace the generic 'DistributedRepository' with
// something more appropriate to the comment domain in distributed context.
interface DistributedCommentStore {
    void appendComment(String streamId, String commentPayload, String region);
    List<String> getRecentComments(String streamId, String region, int limit);
}

interface DistributedSessionRegistry {
    void registerSession(String streamId, String sessionId, String userId, String region);
    void unregisterSession(String streamId, String sessionId, String region);
}

interface DistributedFanoutService {
    void broadcast(String streamId, String commentPayload, String region);
}

interface ModerationPipelineV3 {
    boolean isApproved(String payload);
}

public class CommentIngressServiceV3 {
    private final DistributedCommentStore commentStore;
    private final IdempotencyStore idempotencyStore;
    private final DistributedFanoutService fanoutService;
    private final DistributedSessionRegistry sessionRegistry;
    private final ModerationPipelineV3 moderationPipeline;

    public CommentIngressServiceV3(
            DistributedCommentStore commentStore, 
            IdempotencyStore idempotencyStore,
            DistributedFanoutService fanoutService,
            DistributedSessionRegistry sessionRegistry,
            ModerationPipelineV3 moderationPipeline) {
        this.commentStore = commentStore;
        this.idempotencyStore = idempotencyStore;
        this.fanoutService = fanoutService;
        this.sessionRegistry = sessionRegistry;
        this.moderationPipeline = moderationPipeline;
    }

    public boolean publishComment(String streamId, String payload, String idempotencyKey, String region) {
        if (!idempotencyStore.claim(idempotencyKey, 60_000)) {
            return false; // Already processed
        }
        
        if (!moderationPipeline.isApproved(payload)) {
            return false; // Rejected
        }

        commentStore.appendComment(streamId, payload, region);
        fanoutService.broadcast(streamId, payload, region);
        return true;
    }

    public List<String> joinStream(String streamId, String sessionId, String userId, String region) {
        sessionRegistry.registerSession(streamId, sessionId, userId, region);
        return commentStore.getRecentComments(streamId, region, 50);
    }
    
    public void leaveStream(String streamId, String sessionId, String region) {
        sessionRegistry.unregisterSession(streamId, sessionId, region);
    }
}
