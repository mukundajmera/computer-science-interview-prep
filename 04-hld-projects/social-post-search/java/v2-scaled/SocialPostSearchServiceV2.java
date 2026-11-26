
import java.util.List;

interface SocialPostSearchServiceProjectionStore {
    void upsertProjection(String id, String snapshot);
    List<String> recent(int limit);
}

/**
 * Social Post Search System - v2 scaled service boundary with projection updates.
 */
public interface SocialPostSearchServiceV2 {
    String create(String ownerId, String payload);
    void publishMutation(String id, String mutationPayload, String idempotencyKey);
    List<String> readRecent(int limit);
}
