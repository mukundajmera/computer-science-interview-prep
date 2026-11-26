
import java.util.List;

/**
 * Instagram-oriented variant boundary for media-heavy feed delivery.
 */
public interface InstagramVariantFeedService {
    List<String> getHomeFeed(String userId, String cursor, int limit);
    String createMediaPost(String userId, String mediaKey, String caption);
    void registerMediaDerivative(String postId, String derivativeKey);
}
