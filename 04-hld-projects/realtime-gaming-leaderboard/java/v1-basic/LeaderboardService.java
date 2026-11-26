import java.util.List;

public class LeaderboardService {
    // We use the ScoreRangePartitionManager to fulfill the requirements, 
    // as it internally manages SkipListSortedSets and routes by score range.
    private final ScoreRangePartitionManager partitionManager;

    public LeaderboardService(int partitionSize) {
        this.partitionManager = new ScoreRangePartitionManager(partitionSize);
    }

    /**
     * FR1: Increment player score upon match win in real time.
     * Also updates tie-breaker timestamp.
     */
    public void incrementScore(String userId, int scoreIncrement, long timestamp) {
        partitionManager.updateScore(userId, scoreIncrement, timestamp);
    }

    /**
     * FR2: Retrieve the global Top 10 (or Top 100) players in real time.
     */
    public List<SkipListSortedSet.Entry> getTopK(int k) {
        return partitionManager.getTopK(k);
    }

    /**
     * FR3: Return a specific player's exact global rank.
     */
    public int getRank(String userId) {
        return partitionManager.getRank(userId);
    }

    /**
     * FR4: Return a relative rank window (e.g., 4 ranks above and below the player).
     */
    public List<SkipListSortedSet.Entry> getRelativeWindow(String userId, int radius) {
        return partitionManager.getRelativeWindow(userId, radius);
    }
    
    public Integer getScore(String userId) {
        return partitionManager.getScore(userId);
    }
}
