import java.util.ArrayList;
import java.util.Comparator;
import java.util.List;
import java.util.Map;
import java.util.PriorityQueue;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.atomic.AtomicLong;

public class VideoRankingService {
    private final ConcurrentHashMap<String, AtomicLong> viewCounts;

    public VideoRankingService() {
        this.viewCounts = new ConcurrentHashMap<>();
    }

    public void recordView(String videoId) {
        viewCounts.computeIfAbsent(videoId, k -> new AtomicLong(0)).incrementAndGet();
    }

    public long getViewCount(String videoId) {
        AtomicLong count = viewCounts.get(videoId);
        return count != null ? count.get() : 0;
    }

    public List<VideoRank> getTopK(int k) {
        if (k <= 0) {
            return new ArrayList<>();
        }

        // Min-heap to keep track of the top K elements
        // Compare by view count ascending. For ties, compare by videoId descending
        // so that the one with "smaller" videoId stays when popped. Wait, if we want
        // the top-k, and there's a tie, we should keep the one that should rank higher.
        // Let's define ranking tie-breaker: higher videoId means lower rank?
        // Let's stick to standard tie-breaking: higher viewCount wins.
        // If viewCount is equal, lexicographically smaller videoId wins (ranks higher).
        // A min-heap keeps the SMALLEST element at the root. We want to pop the "smallest"
        // so it doesn't stay in top K.
        // Thus, the element that is "worse" should be at the top of the min-heap.
        // Worse means: lower view count, or (if equal) LARGER videoId.
        Comparator<Map.Entry<String, AtomicLong>> comparator = (a, b) -> {
            long countA = a.getValue().get();
            long countB = b.getValue().get();
            if (countA != countB) {
                return Long.compare(countA, countB);
            }
            // If view counts are equal, the one with LARGER videoId is considered "smaller" in our order 
            // because we want to eject it first. 
            // So if a.videoId > b.videoId, a should be at root (return -1) -> b.getKey().compareTo(a.getKey())
            return b.getKey().compareTo(a.getKey());
        };

        PriorityQueue<Map.Entry<String, AtomicLong>> minHeap = new PriorityQueue<>(comparator);

        for (Map.Entry<String, AtomicLong> entry : viewCounts.entrySet()) {
            minHeap.offer(entry);
            if (minHeap.size() > k) {
                minHeap.poll();
            }
        }

        // Extract elements into a list
        List<Map.Entry<String, AtomicLong>> topElements = new ArrayList<>();
        while (!minHeap.isEmpty()) {
            topElements.add(minHeap.poll());
        }

        // Reverse to get them in descending order of rank
        List<VideoRank> result = new ArrayList<>();
        int currentRank = 1;
        for (int i = topElements.size() - 1; i >= 0; i--) {
            Map.Entry<String, AtomicLong> entry = topElements.get(i);
            result.add(new VideoRank(entry.getKey(), entry.getValue().get(), currentRank++));
        }

        return result;
    }

    public void resetWindow() {
        viewCounts.clear();
    }
}
