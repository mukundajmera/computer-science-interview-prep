
import java.util.Optional;

/**
 * Price Tracking Service - v1 basic service boundary.
 */
public interface PriceTrackingPlatformService {
    String create(String ownerId, String payload);
    Optional<String> getById(String id);
    void mutate(String id, String mutationPayload, String idempotencyKey);
}
