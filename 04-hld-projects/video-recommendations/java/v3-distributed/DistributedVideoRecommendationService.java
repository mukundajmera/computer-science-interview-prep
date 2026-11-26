package v3_distributed;

import java.util.*;
import java.util.concurrent.*;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.stream.Collectors;

public class DistributedVideoRecommendationService {

    // Candidate Generator interface
    public interface CandidateGenerator {
        List<VideoCandidate> getCandidates(String userId, String contextVideoId, int limit);
    }

    public static class VideoCandidate {
        public final String videoId;
        public final String source;
        public final double baseScore;

        public VideoCandidate(String videoId, String source, double baseScore) {
            this.videoId = videoId;
            this.source = source;
            this.baseScore = baseScore;
        }

        @Override
        public boolean equals(Object o) {
            if (this == o) return true;
            if (o == null || getClass() != o.getClass()) return false;
            VideoCandidate that = (VideoCandidate) o;
            return videoId.equals(that.videoId);
        }

        @Override
        public int hashCode() {
            return Objects.hash(videoId);
        }
    }

    public static class RankScore {
        public final String videoId;
        public final double score;

        public RankScore(String videoId, double score) {
            this.videoId = videoId;
            this.score = score;
        }
    }

    // Heavy Ranker Shard
    public interface RankingShard {
        List<RankScore> rankCandidates(String userId, List<VideoCandidate> candidates);
        String getShardId();
    }

    public static class CircuitBreaker {
        private final int failureThreshold;
        private final long resetTimeoutMs;
        private final AtomicInteger failures = new AtomicInteger(0);
        private volatile long lastFailureTime = 0;
        private volatile State state = State.CLOSED;

        public enum State { CLOSED, OPEN, HALF_OPEN }

        public CircuitBreaker(int failureThreshold, long resetTimeoutMs) {
            this.failureThreshold = failureThreshold;
            this.resetTimeoutMs = resetTimeoutMs;
        }

        public synchronized boolean allowRequest() {
            if (state == State.OPEN) {
                if (System.currentTimeMillis() - lastFailureTime > resetTimeoutMs) {
                    state = State.HALF_OPEN;
                    return true;
                }
                return false;
            }
            return true;
        }

        public synchronized void recordSuccess() {
            if (state == State.HALF_OPEN) {
                state = State.CLOSED;
            }
            failures.set(0);
        }

        public synchronized void recordFailure() {
            lastFailureTime = System.currentTimeMillis();
            if (failures.incrementAndGet() >= failureThreshold) {
                state = State.OPEN;
            }
        }
    }

    private final List<CandidateGenerator> candidateGenerators;
    private final List<RankingShard> rankingShards;
    private final Map<String, CircuitBreaker> shardCircuitBreakers;
    private final ExecutorService executor;
    private final int rankTimeoutMs;

    // Real-time feedback storage (simplified)
    private final Map<String, Map<String, Double>> userVideoScores = new ConcurrentHashMap<>();

    public DistributedVideoRecommendationService(List<CandidateGenerator> candidateGenerators,
                                                 List<RankingShard> rankingShards,
                                                 int rankTimeoutMs) {
        this.candidateGenerators = candidateGenerators;
        this.rankingShards = rankingShards;
        this.shardCircuitBreakers = new ConcurrentHashMap<>();
        for (RankingShard shard : rankingShards) {
            this.shardCircuitBreakers.put(shard.getShardId(), new CircuitBreaker(3, 5000));
        }
        this.executor = Executors.newFixedThreadPool(Runtime.getRuntime().availableProcessors() * 2 + 2);
        this.rankTimeoutMs = rankTimeoutMs;
    }

    public void recordFeedback(String userId, String videoId, String eventType, double dwellMs) {
        // Near-real-time streaming update simulation
        double scoreDelta = 0;
        switch(eventType) {
            case "CLICK": scoreDelta = 1.0; break;
            case "WATCH": scoreDelta = Math.min(10.0, dwellMs / 1000.0); break;
            case "SKIP": scoreDelta = -2.0; break;
            case "LIKE": scoreDelta = 5.0; break;
        }

        userVideoScores.computeIfAbsent(userId, k -> new ConcurrentHashMap<>())
                       .merge(videoId, scoreDelta, Double::sum);
    }

    public List<String> getRecommendations(String userId, String contextVideoId, int limit) {
        // 1. Two-stage candidate retrieval (scatter-gather)
        List<Future<List<VideoCandidate>>> futureCandidates = new ArrayList<>();
        for (CandidateGenerator generator : candidateGenerators) {
            futureCandidates.add(executor.submit(() -> generator.getCandidates(userId, contextVideoId, limit * 2)));
        }

        Set<VideoCandidate> uniqueCandidates = new HashSet<>();
        long candidateDeadline = System.currentTimeMillis() + 100;
        for (Future<List<VideoCandidate>> future : futureCandidates) {
            long timeLeft = candidateDeadline - System.currentTimeMillis();
            if (timeLeft <= 0) break;
            try {
                uniqueCandidates.addAll(future.get(timeLeft, TimeUnit.MILLISECONDS));
            } catch (Exception e) {
                // Ignore failures from individual generators (partial results acceptable)
            }
        }

        List<VideoCandidate> candidatesList = new ArrayList<>(uniqueCandidates);
        if (candidatesList.isEmpty()) {
            return Collections.emptyList();
        }

        // 2. Partition candidates across ranking shards
        int shardsCount = rankingShards.size();
        List<List<VideoCandidate>> partitions = new ArrayList<>();
        for (int i = 0; i < shardsCount; i++) partitions.add(new ArrayList<>());
        for (int i = 0; i < candidatesList.size(); i++) {
            partitions.get(i % shardsCount).add(candidatesList.get(i));
        }

        // 3. Distributed heavy ranking with circuit breaker and timeout
        List<Future<List<RankScore>>> futureRankings = new ArrayList<>();
        for (int i = 0; i < shardsCount; i++) {
            final int shardIndex = i;
            RankingShard shard = rankingShards.get(shardIndex);
            List<VideoCandidate> partition = partitions.get(shardIndex);
            CircuitBreaker cb = shardCircuitBreakers.get(shard.getShardId());

            if (cb.allowRequest()) {
                futureRankings.add(executor.submit(() -> {
                    try {
                        List<RankScore> results = shard.rankCandidates(userId, partition);
                        cb.recordSuccess();
                        return results;
                    } catch (Exception e) {
                        cb.recordFailure();
                        throw e;
                    }
                }));
            } else {
                // Fallback for tripped circuit breaker: lightweight baseline scoring
                List<RankScore> fallback = new ArrayList<>();
                for (VideoCandidate c : partition) {
                    fallback.add(new RankScore(c.videoId, c.baseScore));
                }
                futureRankings.add(CompletableFuture.completedFuture(fallback));
            }
        }

        List<RankScore> finalScores = new ArrayList<>();
        long rankDeadline = System.currentTimeMillis() + rankTimeoutMs;
        for (int i = 0; i < futureRankings.size(); i++) {
            Future<List<RankScore>> future = futureRankings.get(i);
            long timeLeft = rankDeadline - System.currentTimeMillis();
            try {
                if (timeLeft <= 0) {
                    throw new TimeoutException("Ranking timeout");
                }
                finalScores.addAll(future.get(timeLeft, TimeUnit.MILLISECONDS));
            } catch (TimeoutException e) {
                // Timeout fallback for this partition
                CircuitBreaker cb = shardCircuitBreakers.get(rankingShards.get(i).getShardId());
                cb.recordFailure();
                future.cancel(true);
                // add fallback scores
                for (VideoCandidate c : partitions.get(i)) {
                    finalScores.add(new RankScore(c.videoId, c.baseScore));
                }
            } catch (Exception e) {
                 // add fallback scores
                for (VideoCandidate c : partitions.get(i)) {
                    finalScores.add(new RankScore(c.videoId, c.baseScore));
                }
            }
        }

        // 4. Apply real-time feedback adjustments
        Map<String, Double> userAdjustments = userVideoScores.getOrDefault(userId, Collections.emptyMap());
        for (int i = 0; i < finalScores.size(); i++) {
            RankScore rs = finalScores.get(i);
            double adjustment = userAdjustments.getOrDefault(rs.videoId, 0.0);
            finalScores.set(i, new RankScore(rs.videoId, rs.score + adjustment));
        }

        // Sort and limit
        finalScores.sort((a, b) -> Double.compare(b.score, a.score));
        return finalScores.stream()
                .limit(limit)
                .map(rs -> rs.videoId)
                .collect(Collectors.toList());
    }

    public void shutdown() {
        executor.shutdownNow();
    }
}