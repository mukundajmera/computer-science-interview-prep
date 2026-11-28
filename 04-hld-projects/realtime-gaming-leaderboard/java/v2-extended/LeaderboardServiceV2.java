import java.util.ArrayList;
import java.util.List;

/**
 * v2-extended real-time gaming leaderboard.
 *
 * Improvements over v1-basic (each has dedicated tests):
 *
 * 1. Cheat-resistant score validation (FOLLOW-UPS.md #3): increments
 *    above a configured per-update cap are rejected as anomalous instead
 *    of entering the ranking, rejections are counted, and rejected
 *    updates never reach the event log. This models the server-side
 *    validation the doc demands in place of trusting raw client scores.
 *
 * 2. Durable event log with replay rebuild (FOLLOW-UPS.md #4,
 *    PITFALLS.md #2): every accepted update is appended to an event log,
 *    and replayLog() rebuilds the full ranking state from it - the
 *    in-memory version of reconciling a fresh Redis primary against the
 *    MySQL source of truth after a failover.
 *
 * 3. Hot-shard hash subdivision (FOLLOW-UPS.md #5): see
 *    ScoreRangePartitionManagerV2.
 */
public class LeaderboardServiceV2 {

    /** One accepted score update in the durable event log. */
    public static class ScoreEvent {
        public final String userId;
        public final int scoreIncrement;
        public final long timestamp;

        public ScoreEvent(String userId, int scoreIncrement, long timestamp) {
            this.userId = userId;
            this.scoreIncrement = scoreIncrement;
            this.timestamp = timestamp;
        }
    }

    private final int partitionSize;
    private final int denseSubdivisions;
    private final Integer maxIncrement; // null disables validation (v1 behavior)
    private ScoreRangePartitionManagerV2 partitionManager;
    private long suspiciousRejected = 0;
    private final List<ScoreEvent> eventLog = new ArrayList<>();

    public LeaderboardServiceV2(int partitionSize) {
        this(partitionSize, null, 1);
    }

    public LeaderboardServiceV2(int partitionSize, Integer maxIncrement, int denseSubdivisions) {
        this.partitionSize = partitionSize;
        this.denseSubdivisions = denseSubdivisions;
        this.maxIncrement = maxIncrement;
        this.partitionManager = new ScoreRangePartitionManagerV2(partitionSize, denseSubdivisions);
    }

    /**
     * FR1: Increment player score upon match win in real time.
     * Improvement #1: increments above maxIncrement are rejected as
     * anomalous and counted; nothing is stored or logged for them.
     * Returns true when the update was accepted.
     */
    public synchronized boolean incrementScore(String userId, int scoreIncrement, long timestamp) {
        if (maxIncrement != null && scoreIncrement > maxIncrement) {
            suspiciousRejected++;
            return false;
        }
        partitionManager.updateScore(userId, scoreIncrement, timestamp);
        // Improvement #2: only accepted updates reach the durable log.
        eventLog.add(new ScoreEvent(userId, scoreIncrement, timestamp));
        return true;
    }

    /**
     * FR2: Retrieve the global Top 10 (or Top 100) players in real time.
     */
    public synchronized List<SkipListSortedSetV2.Entry> getTopK(int k) {
        return partitionManager.getTopK(k);
    }

    /**
     * FR3: Return a specific player's exact global rank.
     */
    public synchronized int getRank(String userId) {
        return partitionManager.getRank(userId);
    }

    /**
     * FR4: Return a relative rank window (e.g., 4 ranks above and below the player).
     */
    public synchronized List<SkipListSortedSetV2.Entry> getRelativeWindow(String userId, int radius) {
        return partitionManager.getRelativeWindow(userId, radius);
    }

    public synchronized Integer getScore(String userId) {
        return partitionManager.getScore(userId);
    }

    public long getSuspiciousRejected() {
        return suspiciousRejected;
    }

    public synchronized List<ScoreEvent> getEventLog() {
        return new ArrayList<>(eventLog);
    }

    /**
     * Improvement #2: rebuild the full ranking state from a durable
     * event log. This is the reconciliation answer to a crashed
     * in-memory primary (FOLLOW-UPS.md #4): wipe, then replay every
     * accepted update in order. Validation is bypassed because the log
     * only ever holds updates that were already accepted.
     */
    public synchronized void replayLog(List<ScoreEvent> log) {
        ScoreRangePartitionManagerV2 fresh = new ScoreRangePartitionManagerV2(partitionSize, denseSubdivisions);
        for (ScoreEvent event : log) {
            fresh.updateScore(event.userId, event.scoreIncrement, event.timestamp);
        }
        this.partitionManager = fresh;
        eventLog.clear();
        eventLog.addAll(log);
    }
}
