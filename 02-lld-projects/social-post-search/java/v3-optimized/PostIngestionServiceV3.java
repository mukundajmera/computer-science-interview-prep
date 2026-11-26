package v3_optimized;

import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.concurrent.ConcurrentHashMap;

public class PostIngestionServiceV3 {
    private final InvertedIndex index;
    private final QueryPlanner queryPlanner;
    private final SearchRankingService rankingService;
    private final Map<String, Long> idempotencyKeys;

    public PostIngestionServiceV3() {
        this.index = new InvertedIndex();
        this.queryPlanner = new QueryPlanner(this.index);
        this.rankingService = new SearchRankingService(this.index);
        this.idempotencyKeys = new ConcurrentHashMap<>();
    }

    public boolean upsert(String postId, String content, String idempotencyKey, String region) {
        long currentTime = System.currentTimeMillis();
        Long existingTime = idempotencyKeys.get(idempotencyKey);
        
        if (existingTime != null && (currentTime - existingTime) < 60000) {
            return false; // Idempotency check failed (already processed recently)
        }
        
        idempotencyKeys.put(idempotencyKey, currentTime);
        index.indexPost(postId, content);
        return true;
    }

    public void delete(String postId, String region) {
        index.deletePost(postId);
    }

    public Optional<String> get(String postId, String region) {
        return Optional.ofNullable(index.getDocuments().get(postId));
    }
    
    public List<String> search(String rawQuery, String region) {
        List<String> candidates = queryPlanner.planAndExecute(rawQuery);
        return rankingService.rank(rawQuery, candidates);
    }
}

