
import java.util.List;

interface PriceTrackingPlatformServiceProjectionStore {
    void upsertProjection(String id, String snapshot);
    List<String> recent(int limit);
}

/**
 * Price Tracking Service - v2 scaled service boundary with projection updates.
 */
public interface PriceTrackingPlatformServiceV2 {
    String create(String ownerId, String payload);
    void publishMutation(String id, String mutationPayload, String idempotencyKey);
    List<String> readRecent(int limit);
}
