import java.util.*;
import java.util.stream.Collectors;

public class VideoRecommendationService {

    public static class Video {
        public String id;
        public String category;
        public double popularity;
        public long publishTime;

        public Video(String id, String category, double popularity, long publishTime) {
            this.id = id;
            this.category = category;
            this.popularity = popularity;
            this.publishTime = publishTime;
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

    private final Map<String, Video> videoCatalog = new HashMap<>();
    private final Map<String, List<WatchEvent>> userWatchHistory = new HashMap<>();

    public void addVideo(Video video) {
        videoCatalog.put(video.id, video);
    }

    public void recordWatchEvent(String userId, String videoId, double completionPercentage, long timestamp) {
        userWatchHistory.computeIfAbsent(userId, k -> new ArrayList<>())
                .add(new WatchEvent(userId, videoId, completionPercentage, timestamp));
    }

    public List<Video> getRecommendations(String userId, int k, long currentTime) {
        List<WatchEvent> history = userWatchHistory.getOrDefault(userId, Collections.emptyList());
        Set<String> watchedVideoIds = history.stream().map(e -> e.videoId).collect(Collectors.toSet());

        // Watch completion weight determines category affinity
        Map<String, Double> categoryAffinity = new HashMap<>();
        for (WatchEvent event : history) {
            Video video = videoCatalog.get(event.videoId);
            if (video != null) {
                categoryAffinity.merge(video.category, event.completionPercentage, Double::sum);
            }
        }

        List<Video> candidates = new ArrayList<>();
        Map<String, Double> videoScores = new HashMap<>();

        for (Video video : videoCatalog.values()) {
            if (watchedVideoIds.contains(video.id)) {
                continue; // Unseen video filtering
            }

            double score = 0.0;

            // Candidate generation: category matching
            double affinity = categoryAffinity.getOrDefault(video.category, 0.0);
            if (affinity > 0) {
                score += affinity * 20;
            } else {
                // Popularity fallback
                score += video.popularity;
            }

            // Relevance scoring: Recency boost
            long ageInSeconds = Math.max(0, (currentTime - video.publishTime) / 1000);
            double recencyBoost = 100.0 / (1.0 + ageInSeconds / 3600.0); // Decays over hours
            score += recencyBoost;

            videoScores.put(video.id, score);
            candidates.add(video);
        }

        // Top-K recommendation ranking
        candidates.sort((v1, v2) -> Double.compare(videoScores.get(v2.id), videoScores.get(v1.id)));

        return candidates.stream().limit(k).collect(Collectors.toList());
    }
}
