
import java.util.Optional;

/**
 * Social Post Search System - v1 basic service boundary.
 */
public interface SocialPostSearchService {
    String create(String ownerId, String payload);
    Optional<String> getById(String id);
    void mutate(String id, String mutationPayload, String idempotencyKey);
}
