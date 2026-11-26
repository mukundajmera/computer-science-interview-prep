package v2_extended;

import java.util.List;
import java.util.Optional;

public class PostIngestionServiceV2 {
    private final InvertedIndex index;
    private final QueryPlanner queryPlanner;
    private final SearchRankingService rankingService;

    public PostIngestionServiceV2() {
        this.index = new InvertedIndex();
        this.queryPlanner = new QueryPlanner(this.index);
        this.rankingService = new SearchRankingService(this.index);
    }

    public void upsert(String postId, String content) {
        index.indexPost(postId, content);
    }

    public Optional<String> get(String postId) {
        return Optional.ofNullable(index.getDocuments().get(postId));
    }

    public void delete(String postId) {
        index.deletePost(postId);
    }
    
    public List<String> search(String rawQuery) {
        List<String> candidates = queryPlanner.planAndExecute(rawQuery);
        return rankingService.rank(rawQuery, candidates);
    }
}
