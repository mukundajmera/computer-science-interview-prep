import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.concurrent.locks.ReadWriteLock;
import java.util.concurrent.locks.ReentrantReadWriteLock;

/**
 * v2-extended proximity service.
 *
 * Improvements over v1-basic (each has dedicated tests):
 *
 * 1. Dense-area pagination with exact distances on the candidate set
 *    (FOLLOW-UPS.md #3): search results are strictly paginated
 *    (pageSize + page) and the response carries the total match count,
 *    so a Manhattan cell with thousands of businesses never floods the
 *    client. Exact haversine distances are still computed for every
 *    candidate before ranking, so page 1 is always the true closest set.
 *
 * 2. Secondary attribute filtering (FOLLOW-UPS.md #4): businesses carry
 *    category, rating and openNow attributes, and search accepts filters
 *    on them, applied before distance ranking - the in-memory answer to
 *    "open now, highly rated, within 2km" that pure geohash lookup
 *    cannot express.
 *
 * 3. Geohash-prefix sharding with observability (FOLLOW-UPS.md #1 10x
 *    scale): the index is partitioned into shards keyed by the first
 *    geohash character, the way a Redis cluster would hash by geohash,
 *    and a query scans only the shards its 9 cells live in. The shard
 *    count each query touches is exposed as a metric.
 */
public class ProximityServiceV2 {
    private final Map<String, BusinessV2> businesses;
    // Improvement #3: shard key -> {geohash: business ids}
    private final Map<String, Map<String, Set<String>>> shards;
    private final ReadWriteLock lock;

    // Metrics (improvements #1 and #3).
    private long queriesRun = 0;
    private int lastQueryShardsTouched = 0;

    public static class SearchPage {
        public final List<BusinessV2> businesses;
        public final int total;
        public final int page;
        public final Integer pageSize;

        public SearchPage(List<BusinessV2> businesses, int total, int page, Integer pageSize) {
            this.businesses = businesses;
            this.total = total;
            this.page = page;
            this.pageSize = pageSize;
        }
    }

    private static class DistanceAndBusiness {
        final double distance;
        final BusinessV2 business;

        DistanceAndBusiness(double distance, BusinessV2 business) {
            this.distance = distance;
            this.business = business;
        }
    }

    public ProximityServiceV2() {
        this.businesses = new HashMap<>();
        this.shards = new HashMap<>();
        this.lock = new ReentrantReadWriteLock();
    }

    private static void validateCoordinates(double lat, double lon) {
        if (lat < -90.0 || lat > 90.0) {
            throw new IllegalArgumentException("latitude out of range: " + lat);
        }
        if (lon < -180.0 || lon > 180.0) {
            throw new IllegalArgumentException("longitude out of range: " + lon);
        }
    }

    private static String shardKey(String geohash) {
        return geohash.substring(0, 1);
    }

    public void addBusiness(BusinessV2 business) {
        validateCoordinates(business.getLat(), business.getLon());
        lock.writeLock().lock();
        try {
            removeBusinessInternal(business.getId());

            businesses.put(business.getId(), business);
            String geohash = GeohashUtilV2.encode(business.getLat(), business.getLon(), 6);
            shards.computeIfAbsent(shardKey(geohash), k -> new HashMap<>())
                    .computeIfAbsent(geohash, k -> new HashSet<>())
                    .add(business.getId());
        } finally {
            lock.writeLock().unlock();
        }
    }

    public void removeBusiness(String businessId) {
        lock.writeLock().lock();
        try {
            removeBusinessInternal(businessId);
        } finally {
            lock.writeLock().unlock();
        }
    }

    private void removeBusinessInternal(String businessId) {
        BusinessV2 business = businesses.get(businessId);
        if (business != null) {
            String geohash = GeohashUtilV2.encode(business.getLat(), business.getLon(), 6);
            String shardKey = shardKey(geohash);
            Map<String, Set<String>> shard = shards.get(shardKey);
            if (shard != null) {
                Set<String> ids = shard.get(geohash);
                if (ids != null) {
                    ids.remove(businessId);
                    if (ids.isEmpty()) {
                        shard.remove(geohash);
                    }
                }
                if (shard.isEmpty()) {
                    shards.remove(shardKey);
                }
            }
            businesses.remove(businessId);
        }
    }

    private List<BusinessV2> searchInternal(double lat, double lon, double radiusKm,
                                            String category, Double minRating, Boolean openNow) {
        validateCoordinates(lat, lon);
        int precision = getPrecisionForRadius(radiusKm);
        String centerGeohash = GeohashUtilV2.encode(lat, lon, precision);

        List<String> geohashesToSearch = new ArrayList<>();
        geohashesToSearch.add(centerGeohash);
        geohashesToSearch.addAll(GeohashUtilV2.getNeighbors(centerGeohash));

        List<DistanceAndBusiness> results = new ArrayList<>();
        lock.writeLock().lock();
        try {
            Set<String> touchedShards = new HashSet<>();
            for (String geohash : geohashesToSearch) {
                Map<String, Set<String>> shard = shards.get(shardKey(geohash));
                if (shard == null) {
                    continue;
                }
                touchedShards.add(shardKey(geohash));
                for (Map.Entry<String, Set<String>> entry : shard.entrySet()) {
                    if (entry.getKey().startsWith(geohash)) {
                        for (String bId : entry.getValue()) {
                            BusinessV2 b = businesses.get(bId);
                            // Improvement #2: attribute filters first.
                            if (category != null && !category.equals(b.getCategory())) {
                                continue;
                            }
                            if (minRating != null && b.getRating() < minRating) {
                                continue;
                            }
                            if (openNow != null && b.isOpenNow() != openNow) {
                                continue;
                            }
                            double dist = GeohashUtilV2.haversineDistance(lat, lon, b.getLat(), b.getLon());
                            if (dist <= radiusKm) {
                                results.add(new DistanceAndBusiness(dist, b));
                            }
                        }
                    }
                }
            }
            queriesRun++;
            lastQueryShardsTouched = touchedShards.size();
        } finally {
            lock.writeLock().unlock();
        }

        results.sort((a, b) -> Double.compare(a.distance, b.distance));
        List<BusinessV2> sorted = new ArrayList<>();
        for (DistanceAndBusiness dab : results) {
            sorted.add(dab.business);
        }
        return sorted;
    }

    /** v1-compatible: every match within the radius, distance-ranked. */
    public List<BusinessV2> getNearbyBusinesses(double lat, double lon, double radiusKm) {
        return searchInternal(lat, lon, radiusKm, null, null, null);
    }

    /**
     * Improvements #1 and #2: filtered, paginated search. With no
     * filters and no pageSize this is exactly v1's full result list.
     * Pagination is strict: page 1 is the closest pageSize businesses
     * after exact-distance ranking.
     */
    public SearchPage searchNearby(double lat, double lon, double radiusKm,
                                   String category, Double minRating, Boolean openNow,
                                   Integer pageSize, int page) {
        if (page < 1) {
            throw new IllegalArgumentException("page must be >= 1");
        }
        if (pageSize != null && pageSize <= 0) {
            throw new IllegalArgumentException("pageSize must be positive");
        }

        List<BusinessV2> matches = searchInternal(lat, lon, radiusKm, category, minRating, openNow);
        int total = matches.size();

        if (pageSize != null) {
            int start = (page - 1) * pageSize;
            int end = Math.min(start + pageSize, matches.size());
            matches = start >= matches.size() ? new ArrayList<>() : new ArrayList<>(matches.subList(start, end));
        }

        return new SearchPage(matches, total, page, pageSize);
    }

    public long getQueriesRun() {
        return queriesRun;
    }

    public int getLastQueryShardsTouched() {
        return lastQueryShardsTouched;
    }

    /** Test hook: number of live shards. */
    public int shardCount() {
        lock.readLock().lock();
        try {
            return shards.size();
        } finally {
            lock.readLock().unlock();
        }
    }

    private int getPrecisionForRadius(double radiusKm) {
        if (radiusKm <= 0.15) return 7;
        if (radiusKm <= 1.2) return 6;
        if (radiusKm <= 5.0) return 5;
        if (radiusKm <= 40.0) return 4;
        if (radiusKm <= 150.0) return 3;
        if (radiusKm <= 1200.0) return 2;
        return 1;
    }
}
