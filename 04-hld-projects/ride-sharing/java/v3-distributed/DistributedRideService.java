package ridesharing.v3;

import java.util.*;
import java.util.concurrent.locks.ReentrantLock;

public interface DistributedRideService {
    String resolveCityShard(double pickupLat, double pickupLng);
    void replicateRideEvent(String shard, RideEvent event);
    void reconcileAssignments(String shard);
}

class GeoDriverCandidate {
    public final String driverId;
    public final double etaMinutes;
    public final double distanceKm;

    public GeoDriverCandidate(String driverId, double etaMinutes, double distanceKm) {
        this.driverId = driverId;
        this.etaMinutes = etaMinutes;
        this.distanceKm = distanceKm;
    }
}

/**
 * GeoSearchIndex keeps location queries explicit in the distributed matching path.
 */
interface GeoSearchIndex {
    List<GeoDriverCandidate> nearbyEntities(double lat, double lng, double radiusKm, int limit);
    void upsertPosition(String entityId, double lat, double lng);
}

/**
 * OfflineActivityBuffer models intermittent-connectivity buffering for drivers.
 */
interface OfflineActivityBuffer {
    void appendPoint(String driverId, double lat, double lng, long timestampMillis);
    List<RideEvent> flushBatch(String driverId, int maxItems);
}

final class RideEvent {
    public final String rideId;
    public final String eventType;
    public final long timestampMillis;

    public RideEvent(String rideId, String eventType, long timestampMillis) {
        this.rideId = rideId;
        this.eventType = eventType;
        this.timestampMillis = timestampMillis;
    }
}

class MatchRequest {
    public final String rideId;
    public final double lat;
    public final double lng;

    public MatchRequest(String rideId, double lat, double lng) {
        this.rideId = rideId;
        this.lat = lat;
        this.lng = lng;
    }
}

class Edge {
    public final String rideId;
    public final String driverId;
    public final double etaMinutes;

    public Edge(String rideId, String driverId, double etaMinutes) {
        this.rideId = rideId;
        this.driverId = driverId;
        this.etaMinutes = etaMinutes;
    }
}

class BatchedBipartiteDispatcher {
    private final GeoSearchIndex geoIndex;
    private final List<MatchRequest> pendingRequests = new ArrayList<>();
    private final ReentrantLock lock = new ReentrantLock();

    public BatchedBipartiteDispatcher(GeoSearchIndex geoIndex) {
        this.geoIndex = geoIndex;
    }

    public void submitRequest(String rideId, double lat, double lng) {
        lock.lock();
        try {
            pendingRequests.add(new MatchRequest(rideId, lat, lng));
        } finally {
            lock.unlock();
        }
    }

    public Map<String, String> dispatchBatch() {
        List<MatchRequest> requestsToProcess;
        lock.lock();
        try {
            if (pendingRequests.isEmpty()) {
                return new HashMap<>();
            }
            requestsToProcess = new ArrayList<>(pendingRequests);
            pendingRequests.clear();
        } finally {
            lock.unlock();
        }

        List<Edge> edges = new ArrayList<>();
        Set<String> availableDrivers = new HashSet<>();

        for (MatchRequest req : requestsToProcess) {
            List<GeoDriverCandidate> candidates = geoIndex.nearbyEntities(req.lat, req.lng, 5.0, 10);
            for (GeoDriverCandidate cand : candidates) {
                edges.add(new Edge(req.rideId, cand.driverId, cand.etaMinutes));
                availableDrivers.add(cand.driverId);
            }
        }

        edges.sort(Comparator.comparingDouble(e -> e.etaMinutes));

        Set<String> assignedRides = new HashSet<>();
        Set<String> assignedDrivers = new HashSet<>();
        Map<String, String> matches = new HashMap<>();

        for (Edge edge : edges) {
            if (!assignedRides.contains(edge.rideId) && !assignedDrivers.contains(edge.driverId)) {
                assignedRides.add(edge.rideId);
                assignedDrivers.add(edge.driverId);
                matches.put(edge.rideId, edge.driverId);
            }
        }

        return matches;
    }
}
