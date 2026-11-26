import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.atomic.AtomicLong;

public class CommentIngressServiceV2 {
    private final CommentFanoutService fanoutService;
    private final LiveSessionRegistry sessionRegistry;
    private final CommentReplayStore replayStore;
    private final ModerationPipeline moderationPipeline;

    public CommentIngressServiceV2(
            CommentFanoutService fanoutService,
            LiveSessionRegistry sessionRegistry,
            CommentReplayStore replayStore,
            ModerationPipeline moderationPipeline) {
        this.fanoutService = fanoutService;
        this.sessionRegistry = sessionRegistry;
        this.replayStore = replayStore;
        this.moderationPipeline = moderationPipeline;
    }

    public void publishComment(String streamId, String userId, String payload, long eventTimeMs) {
        if (!moderationPipeline.isApproved(payload)) {
            return;
        }

        fanoutService.fanout(streamId, payload, eventTimeMs);
        if (replayStore instanceof CircularRingBufferReplayStore) {
            ((CircularRingBufferReplayStore) replayStore).addComment(streamId, payload);
        }
    }

    public List<String> joinStream(String streamId, String sessionId, String userId) {
        sessionRegistry.register(streamId, sessionId, userId);
        return replayStore.replay(streamId, null, 50); // replay last 50 comments
    }

    public void leaveStream(String streamId, String sessionId) {
        sessionRegistry.unregister(streamId, sessionId);
    }
}
