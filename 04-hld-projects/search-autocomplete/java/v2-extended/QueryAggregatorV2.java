import java.util.HashMap;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.atomic.LongAdder;

/**
 * v2 aggregator: all-time counts plus a sliding window of recent
 * (trending) counts. Counts land in fixed-size time buckets and buckets
 * older than the window are evicted on write, bounding memory by the
 * window length. Implements the fast-path half of FOLLOW-UPS.md #1.
 */
public class QueryAggregatorV2 {
    private final long bucketSeconds;
    private final int windowBuckets;
    private final ConcurrentHashMap<String, LongAdder> totalCounts;
    private final ConcurrentHashMap<Long, ConcurrentHashMap<String, LongAdder>> buckets;

    public QueryAggregatorV2(long bucketSeconds, int windowBuckets) {
        this.bucketSeconds = bucketSeconds;
        this.windowBuckets = windowBuckets;
        this.totalCounts = new ConcurrentHashMap<>();
        this.buckets = new ConcurrentHashMap<>();
    }

    public void addQuery(String query, long epochSeconds) {
        if (query == null || query.trim().isEmpty()) {
            return;
        }
        String clean = query.toLowerCase();
        long bucket = epochSeconds / bucketSeconds;
        totalCounts.computeIfAbsent(clean, k -> new LongAdder()).increment();
        buckets.computeIfAbsent(bucket, k -> new ConcurrentHashMap<>())
                .computeIfAbsent(clean, k -> new LongAdder())
                .increment();
        // Evict buckets that fell out of the sliding window.
        long oldest = bucket - windowBuckets + 1;
        buckets.keySet().removeIf(b -> b < oldest);
    }

    public Map<String, Long> getAggregatedFrequencies() {
        Map<String, Long> result = new HashMap<>();
        for (Map.Entry<String, LongAdder> entry : totalCounts.entrySet()) {
            result.put(entry.getKey(), entry.getValue().sum());
        }
        return result;
    }

    /** Per-query counts inside the current sliding window. */
    public Map<String, Long> getTrendingCounts(long epochSeconds) {
        long current = epochSeconds / bucketSeconds;
        long oldest = current - windowBuckets + 1;
        Map<String, Long> trending = new HashMap<>();
        for (Map.Entry<Long, ConcurrentHashMap<String, LongAdder>> bucket : buckets.entrySet()) {
            long index = bucket.getKey();
            if (index < oldest || index > current) {
                continue;
            }
            for (Map.Entry<String, LongAdder> entry : bucket.getValue().entrySet()) {
                trending.merge(entry.getKey(), entry.getValue().sum(), Long::sum);
            }
        }
        return trending;
    }
}
