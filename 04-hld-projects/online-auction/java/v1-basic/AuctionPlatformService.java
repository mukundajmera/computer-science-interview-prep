
import java.util.Optional;

/**
 * Online Auction System - v1 basic service boundary.
 */
public interface AuctionPlatformService {
    String create(String ownerId, String payload);
    Optional<String> getById(String id);
    void mutate(String id, String mutationPayload, String idempotencyKey);
}
