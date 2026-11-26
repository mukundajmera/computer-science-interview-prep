
import java.util.List;

interface DistributedIdempotencyStore {
    boolean claim(String key, long ttlMs);
}

/**
 * Live Comments System - v3 distributed service contract.
 */
public interface DistributedLiveCommentsStreamService {
    String create(String ownerId, String payload, String region);
    void mutateWithReplayToken(String id, String mutationPayload, String idempotencyKey, String replayToken);
    List<String> readRegionView(String region, int limit);
}
