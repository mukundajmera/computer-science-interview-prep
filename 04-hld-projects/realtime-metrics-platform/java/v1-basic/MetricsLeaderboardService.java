package metrics.v1;

import java.util.List;

/**
 * Leaderboard projection for metric-driven ranking use cases.
 */
interface LeaderboardProjection {
    void recordResult(String leaderboardId, String actorId, double score, long eventTimestampMs);
    List<LeaderboardEntry> topK(String leaderboardId, int k);
    LeaderboardSnapshot snapshot(String leaderboardId, int limit);
}

record LeaderboardEntry(String actorId, double score, long updatedAtMs) {}

record LeaderboardSnapshot(String leaderboardId, List<LeaderboardEntry> entries, long computedAtMs) {}

/**
 * Service boundary for metric and activity leaderboards.
 */
public interface MetricsLeaderboardService {
    void ingestPoint(String metricName, String actorId, double value, long timestampMs);
    LeaderboardSnapshot getSnapshot(String leaderboardId, int limit);
}
