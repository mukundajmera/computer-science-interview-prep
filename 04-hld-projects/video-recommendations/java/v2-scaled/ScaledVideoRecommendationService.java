import java.util.*;
import java.util.stream.Collectors;

public class ScaledVideoRecommendationService {

    public static class Video {
        public String id;
        public String category;
        public double popularity;
        public long publishTime;
        public List<String> tags; // Useful for graph/relatedness

        public Video(String id, String category, double popularity, long publishTime, List<String> tags) {
            this.id = id;
            this.category = category;
            this.popularity = popularity;
            this.publishTime = publishTime;
            this.tags = tags;
        }
    }

    public static class WatchEvent {
        public String userId;
        public String videoId;
        public double completionPercentage;
        public long timestamp;

        public WatchEvent(String userId, String videoId, double completionPercentage, long timestamp) {
            this.userId = userId;
            this.videoId = videoId;
            this.completionPercentage = completionPercentage;
            this.timestamp = timestamp;
        }
    }

    public static class UserProfile {
        public String userId;
        public Map<String, Double> categoryAffinity;
        public Set<String> watchedVideoIds;
        public long lastUpdated;

        public UserProfile(String userId, Map<String, Double> categoryAffinity, Set<String> watchedVideoIds, long lastUpdated) {
            this.userId = userId;
            this.categoryAffinity = categoryAffinity;
            this.watchedVideoIds = watchedVideoIds;
            this.lastUpdated = lastUpdated;
        }
    }

    private final Map<String, Video> videoCatalog = new HashMap<>();
    private final Map<String, List<WatchEvent>> userWatchHistory = new HashMap<>();

    // User profile feature cache
    private final Map<String, UserProfile> userProfileCache = new HashMap<>();
    private final long profileCacheTtlMs = 60000; // 60 seconds

    private final Random random = new Random();

    public void addVideo(Video video) {
        videoCatalog.put(video.id, video);
    }

    public void recordWatchEvent(String userId, String videoId, double completionPercentage, long timestamp) {
        userWatchHistory.computeIfAbsent(userId, k -> new ArrayList<>())
                .add(new WatchEvent(userId, videoId, completionPercentage, timestamp));
        // Invalidate cache
        userProfileCache.remove(userId);
    }

    private UserProfile getUserProfile(String userId, long currentTime) {
        UserProfile cached = userProfileCache.get(userId);
        if (cached != null && (currentTime - cached.lastUpdated) < profileCacheTtlMs) {
            return cached;
        }

        List<WatchEvent> history = userWatchHistory.getOrDefault(userId, Collections.emptyList());
        Set<String> watchedVideoIds = history.stream().map(e -> e.videoId).collect(Collectors.toSet());

        Map<String, Double> categoryAffinity = new HashMap<>();
        for (WatchEvent event : history) {
            Video video = videoCatalog.get(event.videoId);
            if (video != null) {
                categoryAffinity.merge(video.category, event.completionPercentage, Double::sum);
            }
        }

        UserProfile profile = new UserProfile(userId, categoryAffinity, watchedVideoIds, currentTime);
        userProfileCache.put(userId, profile);
        return profile;
    }

    public List<Video> getRecommendations(String userId, int k, long currentTime) {
        UserProfile profile = getUserProfile(userId, currentTime);

        // 1. Candidate Generation: Multi-source retrieval (Category, Trending, Graph/Tags)
        Set<Video> candidates = new HashSet<>();

        // Category retrieval (based on top categories in affinity)
        List<String> topCategories = profile.categoryAffinity.entrySet().stream()
                .sorted((e1, e2) -> Double.compare(e2.getValue(), e1.getValue()))
                .limit(3)
                .map(Map.Entry::getKey)
                .collect(Collectors.toList());

        // Trending retrieval
        List<Video> trendingVideos = videoCatalog.values().stream()
                .sorted((v1, v2) -> Double.compare(v2.popularity, v1.popularity))
                .limit(50)
                .collect(Collectors.toList());
        candidates.addAll(trendingVideos);

        for (Video video : videoCatalog.values()) {
            if (topCategories.contains(video.category)) {
                candidates.add(video);
            }
        }

        // 2. Cold-start epsilon-greedy exploration
        boolean isColdStart = profile.watchedVideoIds.isEmpty();
        double epsilon = isColdStart ? 0.8 : 0.1; // More exploration if cold start

        if (random.nextDouble() < epsilon) {
            // Add some random videos for exploration
            List<Video> allVideos = new ArrayList<>(videoCatalog.values());
            Collections.shuffle(allVideos, random);
            candidates.addAll(allVideos.subList(0, Math.min(20, allVideos.size())));
        }

        // Filter out already watched videos
        List<Video> validCandidates = candidates.stream()
                .filter(v -> !profile.watchedVideoIds.contains(v.id))
                .collect(Collectors.toList());

        // 3. Heavy Ranking: multi-factor scoring with watch-time completion prediction and diversity penalty
        Map<String, Double> videoScores = new HashMap<>();
        for (Video video : validCandidates) {
            double baseScore = 0.0;

            // Feature 1: Category Affinity (Watch-time completion proxy)
            double affinity = profile.categoryAffinity.getOrDefault(video.category, 0.0);
            baseScore += affinity * 15.0;

            // Feature 2: Popularity
            baseScore += video.popularity * 2.0;

            // Feature 3: Recency
            long ageInSeconds = Math.max(0, (currentTime - video.publishTime) / 1000);
            double recencyBoost = 100.0 / (1.0 + ageInSeconds / 3600.0);
            baseScore += recencyBoost;

            videoScores.put(video.id, baseScore);
        }

        // Sort by initial heavy rank
        validCandidates.sort((v1, v2) -> Double.compare(videoScores.get(v2.id), videoScores.get(v1.id)));

        // Apply Diversity Penalty during final selection
        List<Video> finalRecommendations = new ArrayList<>();
        Map<String, Integer> categoryCounts = new HashMap<>();

        for (Video video : validCandidates) {
            if (finalRecommendations.size() >= k) break;

            int count = categoryCounts.getOrDefault(video.category, 0);
            double diversityPenalty = count * 5.0; // Penalty increases with more items of the same category

            double adjustedScore = videoScores.get(video.id) - diversityPenalty;

            // Only add if score is still somewhat reasonable, but we just re-rank or skip
            // A simpler approach is to skip if too many from same category to force diversity
            if (count < Math.max(2, k / 3)) { // Ensure not too many from same category
                finalRecommendations.add(video);
                categoryCounts.put(video.category, count + 1);
            }
        }

        // If we don't have enough due to diversity constraints, backfill
        if (finalRecommendations.size() < k) {
            for (Video video : validCandidates) {
                if (finalRecommendations.size() >= k) break;
                if (!finalRecommendations.contains(video)) {
                    finalRecommendations.add(video);
                }
            }
        }

        return finalRecommendations;
    }
}
