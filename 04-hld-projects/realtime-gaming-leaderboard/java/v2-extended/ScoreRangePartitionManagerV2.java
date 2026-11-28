import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.Map;
import java.util.TreeMap;
import java.util.concurrent.ConcurrentHashMap;

/**
 * v2 ScoreRangePartitionManager: v1 score-range partitioning plus
 * improvement #3, hot-shard hash subdivision (FOLLOW-UPS.md #5). The
 * densest lowest bucket (where every new player starts) is subdivided
 * into N hash sub-shards by user id, spreading write contention the way
 * bucket_0_100_shard_1..N would. Top-k, rank and relative window
 * scatter-gather across sub-shards so global ordering is preserved.
 * See LeaderboardServiceV2 for the full v2 list.
 */
public class ScoreRangePartitionManagerV2 {
    // Reverse order TreeMap so that higher score partitions are accessed first
    private final TreeMap<Integer, List<SkipListSortedSetV2>> partitions;
    private final int partitionSize;
    private final int denseSubdivisions;
    private final Map<String, Integer> userCurrentScore;

    public ScoreRangePartitionManagerV2(int partitionSize) {
        this(partitionSize, 1);
    }

    public ScoreRangePartitionManagerV2(int partitionSize, int denseSubdivisions) {
        if (denseSubdivisions < 1) {
            throw new IllegalArgumentException("denseSubdivisions must be >= 1");
        }
        this.partitions = new TreeMap<>(Collections.reverseOrder());
        this.partitionSize = partitionSize;
        this.denseSubdivisions = denseSubdivisions;
        this.userCurrentScore = new ConcurrentHashMap<>();
    }

    /** Only the densest lowest bucket is subdivided (FOLLOW-UPS.md #5). */
    private int subdivisionsFor(int bound) {
        return bound == 0 ? denseSubdivisions : 1;
    }

    private int subIndex(String userId, int count) {
        return Math.floorMod(userId.hashCode(), count);
    }

    private List<SkipListSortedSetV2> getPartitionList(int bound) {
        return partitions.computeIfAbsent(bound, k -> {
            List<SkipListSortedSetV2> subs = new ArrayList<>();
            for (int i = 0; i < subdivisionsFor(k); i++) {
                subs.add(new SkipListSortedSetV2());
            }
            return subs;
        });
    }

    private SkipListSortedSetV2 route(int bound, String userId) {
        List<SkipListSortedSetV2> subs = getPartitionList(bound);
        return subs.get(subIndex(userId, subs.size()));
    }

    private static List<SkipListSortedSetV2.Entry> mergedEntries(List<SkipListSortedSetV2> subs) {
        List<SkipListSortedSetV2.Entry> merged = new ArrayList<>();
        for (SkipListSortedSetV2 sub : subs) {
            for (SkipListSortedSetV2.Entry entry : sub.entries()) {
                merged.add(entry);
            }
        }
        merged.sort(null);
        return merged;
    }

    public synchronized void updateScore(String userId, int scoreIncrement, long timestamp) {
        int currentScore = userCurrentScore.getOrDefault(userId, 0);
        int newScore = currentScore + scoreIncrement;

        int oldPartitionBound = (currentScore / partitionSize) * partitionSize;
        int newPartitionBound = (newScore / partitionSize) * partitionSize;

        if (userCurrentScore.containsKey(userId) && oldPartitionBound != newPartitionBound) {
            List<SkipListSortedSetV2> oldPartition = partitions.get(oldPartitionBound);
            if (oldPartition != null) {
                route(oldPartitionBound, userId).removeUser(userId);
            }
        }

        userCurrentScore.put(userId, newScore);
        route(newPartitionBound, userId).updateScore(userId, newScore, timestamp);
    }

    public synchronized List<SkipListSortedSetV2.Entry> getTopK(int k) {
        List<SkipListSortedSetV2.Entry> topK = new ArrayList<>();
        for (List<SkipListSortedSetV2> partition : partitions.values()) {
            List<SkipListSortedSetV2.Entry> merged = mergedEntries(partition);
            int remaining = k - topK.size();
            if (remaining <= 0) {
                break;
            }
            topK.addAll(merged.subList(0, Math.min(remaining, merged.size())));
        }
        return topK;
    }

    public synchronized int getRank(String userId) {
        Integer score = userCurrentScore.get(userId);
        if (score == null) return -1;

        int partitionBound = (score / partitionSize) * partitionSize;
        int globalRank = 1;

        for (Map.Entry<Integer, List<SkipListSortedSetV2>> entry : partitions.entrySet()) {
            if (entry.getKey() > partitionBound) {
                for (SkipListSortedSetV2 sub : entry.getValue()) {
                    globalRank += sub.size();
                }
            } else if (entry.getKey() == partitionBound) {
                // Scatter-gather: rank inside the merged bucket.
                List<SkipListSortedSetV2.Entry> merged = mergedEntries(entry.getValue());
                for (int i = 0; i < merged.size(); i++) {
                    if (merged.get(i).userId.equals(userId)) {
                        return globalRank + i;
                    }
                }
            } else {
                break;
            }
        }
        return -1;
    }

    public synchronized List<SkipListSortedSetV2.Entry> getRelativeWindow(String userId, int radius) {
        int rank = getRank(userId);
        if (rank == -1) return new ArrayList<>();

        int minRank = Math.max(1, rank - radius);
        int maxRank = rank + radius;

        List<SkipListSortedSetV2.Entry> window = new ArrayList<>();
        int currentRank = 1;

        for (List<SkipListSortedSetV2> partition : partitions.values()) {
            for (SkipListSortedSetV2.Entry entry : mergedEntries(partition)) {
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

    /** Test hook: number of sub-shards for a bound, 0 if absent. */
    public synchronized int subShardCount(int bound) {
        List<SkipListSortedSetV2> subs = partitions.get(bound);
        return subs == null ? 0 : subs.size();
    }
}
