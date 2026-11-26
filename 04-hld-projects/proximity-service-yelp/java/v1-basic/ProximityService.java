import java.util.ArrayList;
import java.util.Collections;
import java.util.Comparator;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.concurrent.locks.ReadWriteLock;
import java.util.concurrent.locks.ReentrantReadWriteLock;

public class ProximityService {
    private final Map<String, Business> businesses;
    private final Map<String, Set<String>> geohashIndex;
    private final ReadWriteLock lock;

    public ProximityService() {
        this.businesses = new HashMap<>();
        this.geohashIndex = new HashMap<>();
        this.lock = new ReentrantReadWriteLock();
    }

    public void addBusiness(Business business) {
        lock.writeLock().lock();
        try {
            removeBusinessInternal(business.getId());

            businesses.put(business.getId(), business);
            String geohash = GeohashUtil.encode(business.getLat(), business.getLon(), 6);
            geohashIndex.computeIfAbsent(geohash, k -> new HashSet<>()).add(business.getId());
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
        Business business = businesses.get(businessId);
        if (business != null) {
            String geohash = GeohashUtil.encode(business.getLat(), business.getLon(), 6);
            Set<String> ids = geohashIndex.get(geohash);
            if (ids != null) {
                ids.remove(businessId);
                if (ids.isEmpty()) {
                    geohashIndex.remove(geohash);
                }
            }
            businesses.remove(businessId);
        }
    }

    public List<Business> getNearbyBusinesses(double lat, double lon, double radiusKm) {
        int precision = getPrecisionForRadius(radiusKm);
        String centerGeohash = GeohashUtil.encode(lat, lon, precision);

        List<String> geohashesToSearch = new ArrayList<>();
        geohashesToSearch.add(centerGeohash);
        geohashesToSearch.addAll(GeohashUtil.getNeighbors(centerGeohash));

        List<DistanceAndBusiness> results = new ArrayList<>();

        lock.readLock().lock();
        try {
            for (String geohash : geohashesToSearch) {
                for (Map.Entry<String, Set<String>> entry : geohashIndex.entrySet()) {
                    if (entry.getKey().startsWith(geohash)) {
                        for (String bId : entry.getValue()) {
                            Business b = businesses.get(bId);
                            if (b != null) {
                                double dist = GeohashUtil.haversineDistance(lat, lon, b.getLat(), b.getLon());
                                if (dist <= radiusKm) {
                                    results.add(new DistanceAndBusiness(dist, b));
                                }
                            }
                        }
                    }
                }
            }
        } finally {
            lock.readLock().unlock();
        }

        results.sort(Comparator.comparingDouble(a -> a.distance));

        List<Business> finalResults = new ArrayList<>();
        for (DistanceAndBusiness db : results) {
            finalResults.add(db.business);
        }

        return finalResults;
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

    private static class DistanceAndBusiness {
        double distance;
        Business business;

        DistanceAndBusiness(double distance, Business business) {
            this.distance = distance;
            this.business = business;
        }
    }
}