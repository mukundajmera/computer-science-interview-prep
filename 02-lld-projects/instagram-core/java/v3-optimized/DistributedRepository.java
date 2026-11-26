import java.util.Optional;
import java.util.Map;
import java.util.List;
import java.util.ArrayList;
import java.util.Collections;
import java.util.concurrent.ConcurrentHashMap;

public class DistributedRepository {
    private final Map<String, PostMetadataV3> store = new ConcurrentHashMap<>();

    public void save(String key, PostMetadataV3 post, String region) {
        store.put(key, post);
    }

    public Optional<PostMetadataV3> find(String key, String region) {
        PostMetadataV3 post = store.get(key);
        if (post != null && region.equals(post.getRegion())) {
            return Optional.of(post);
        }
        return Optional.empty();
    }
    
    public Map<String, PostMetadataV3> getAllPosts() {
        return Collections.unmodifiableMap(store);
    }
    
    public void delete(String key) {
        store.remove(key);
    }
}
