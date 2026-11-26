
import java.util.List;

interface DistributedIdempotencyStore {
    boolean claim(String key, long ttlMs);
}

/**
 * Online Auction System - v3 distributed service contract.
 */
public interface DistributedAuctionPlatformService {
    String create(String ownerId, String payload, String region);
    void mutateWithReplayToken(String id, String mutationPayload, String idempotencyKey, String replayToken);
    List<String> readRegionView(String region, int limit);
}
