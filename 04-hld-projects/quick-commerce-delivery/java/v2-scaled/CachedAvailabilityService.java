/**
 * Quick Commerce Delivery - V2 Scaled
 * Skeleton for cache-backed availability and invalidation.
 */

import java.time.Instant;
import java.util.List;
import java.util.Optional;

public class CachedAvailabilityService {

    public interface AvailabilityCache {
        Optional<List<String>> get(String key);
        void put(String key, List<String> itemIds, int ttlSeconds);
        void invalidateCenter(String centerId);
    }

    public interface AvailabilitySource {
        List<String> queryCenter(String centerId, String keyword, int page, int pageSize);
        List<String> resolveNearbyCenters(double lat, double lng, int limit);
    }

    public interface InvalidationStream {
        void publishInventoryDelta(String centerId, String itemId, int availableQty, Instant at);
    }


    private AvailabilityCache cache;
    private AvailabilitySource source;

    public CachedAvailabilityService() {}

    public CachedAvailabilityService(AvailabilityCache cache, AvailabilitySource source) {
        this.cache = cache;
        this.source = source;
    }

    public List<String> search(double lat, double lng, String keyword, int page, int pageSize) {
        List<String> centers = source.resolveNearbyCenters(lat, lng, 10);
        List<String> allResults = new java.util.ArrayList<>();
        
        for (String centerId : centers) {
            String cacheKey = centerId + ":" + keyword + ":" + page;
            Optional<List<String>> cached = cache.get(cacheKey);
            
            if (cached.isPresent()) {
                allResults.addAll(cached.get());
            } else {
                List<String> results = source.queryCenter(centerId, keyword, page, pageSize);
                cache.put(cacheKey, results, 60);
                allResults.addAll(results);
            }
        }
        
        if (allResults.size() > pageSize) {
            return allResults.subList(0, pageSize);
        }
        
        return allResults;
    }

    public void onInventoryDelta(String centerId, String itemId, int availableQty, Instant at) {

        if (availableQty == 0) {
            cache.invalidateCenter(centerId);
        }
    }
}

