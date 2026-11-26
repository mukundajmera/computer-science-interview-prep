
import java.util.Optional;

/**
 * Live Comments System - v1 basic service boundary.
 */
public interface LiveCommentsStreamService {
    String create(String ownerId, String payload);
    Optional<String> getById(String id);
    void mutate(String id, String mutationPayload, String idempotencyKey);
}
