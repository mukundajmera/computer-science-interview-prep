
import java.util.List;

interface LiveCommentsStreamServiceProjectionStore {
    void upsertProjection(String id, String snapshot);
    List<String> recent(int limit);
}

/**
 * Live Comments System - v2 scaled service boundary with projection updates.
 */
public interface LiveCommentsStreamServiceV2 {
    String create(String ownerId, String payload);
    void publishMutation(String id, String mutationPayload, String idempotencyKey);
    List<String> readRecent(int limit);
}
