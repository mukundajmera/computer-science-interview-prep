import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.Map;
import java.util.TreeMap;
import java.util.concurrent.ConcurrentHashMap;

/**
 * Simulates partitioning the leaderboard by score ranges.
 * For example, if partitionSize = 1000, scores 0-999 go to partition 0,
 * scores 1000-1999 go to partition 1000, etc.
 */
public class ScoreRangePartitionManager {
    // Reverse order TreeMap so that higher score partitions are accessed first when finding top players
    private final TreeMap<Integer, SkipListSortedSet> partitions;
    private final int partitionSize;
    private final Map<String, Integer> userCurrentScore;

    public ScoreRangePartitionManager(int partitionSize) {
        this.partitions = new TreeMap<>(Collections.reverseOrder());
        this.partitionSize = partitionSize;
        this.userCurrentScore = new ConcurrentHashMap<>();
    }

    private SkipListSortedSet getPartition(int score) {
        int lowerBound = (score / partitionSize) * partitionSize;
        return partitions.computeIfAbsent(lowerBound, k -> new SkipListSortedSet());
    }

    public synchronized void updateScore(String userId, int scoreIncrement, long timestamp) {
        int currentScore = userCurrentScore.getOrDefault(userId, 0);
        int newScore = currentScore + scoreIncrement;

        int oldPartitionBound = (currentScore / partitionSize) * partitionSize;
        int newPartitionBound = (newScore / partitionSize) * partitionSize;

        if (userCurrentScore.containsKey(userId) && oldPartitionBound != newPartitionBound) {
            SkipListSortedSet oldPartition = partitions.get(oldPartitionBound);
            if (oldPartition != null) {
                oldPartition.removeUser(userId);
            }
        }

        userCurrentScore.put(userId, newScore);
        SkipListSortedSet newPartition = getPartition(newScore);
        newPartition.updateScore(userId, newScore, timestamp);
    }
    
    public synchronized List<SkipListSortedSet.Entry> getTopK(int k) {
        List<SkipListSortedSet.Entry> topK = new ArrayList<>();
        for (SkipListSortedSet partition : partitions.values()) {
            List<SkipListSortedSet.Entry> partitionTop = partition.getTopK(k - topK.size());
            topK.addAll(partitionTop);
            if (topK.size() >= k) {
                break;
            }
        }
        return topK;
    }
    
    public synchronized int getRank(String userId) {
        Integer score = userCurrentScore.get(userId);
        if (score == null) return -1;
        
        int partitionBound = (score / partitionSize) * partitionSize;
        int globalRank = 1;
        
        for (Map.Entry<Integer, SkipListSortedSet> entry : partitions.entrySet()) {
            if (entry.getKey() > partitionBound) {
                globalRank += entry.getValue().size();
            } else if (entry.getKey() == partitionBound) {
                int localRank = entry.getValue().getRank(userId);
                if (localRank != -1) {
                    return globalRank + localRank - 1;
                }
            } else {
                break;
            }
        }
        return -1;
    }

    public synchronized List<SkipListSortedSet.Entry> getRelativeWindow(String userId, int radius) {
        int rank = getRank(userId);
        if (rank == -1) return new ArrayList<>();

        int minRank = Math.max(1, rank - radius);
        int maxRank = rank + radius;

        List<SkipListSortedSet.Entry> window = new ArrayList<>();
        int currentRank = 1;
        
        for (SkipListSortedSet partition : partitions.values()) {
            for (SkipListSortedSet.Entry entry : partition.entries()) {
                if (currentRank >= minRank && currentRank <= maxRank) {
                    window.add(entry);
                }
                if (currentRank > maxRank) {
                    return window;
                }
                currentRank++;
            }
        }
        return window;
    }
    
    public Integer getScore(String userId) {
        return userCurrentScore.get(userId);
    }
}
