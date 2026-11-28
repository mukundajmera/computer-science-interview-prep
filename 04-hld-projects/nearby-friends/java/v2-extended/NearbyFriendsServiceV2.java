import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.atomic.AtomicLong;
import java.util.function.Consumer;

/**
 * v2-extended nearby friends service.
 *
 * Improvements over v1-basic (each has dedicated tests):
 *
 * 1. Offline-to-online initial state (FOLLOW-UPS.md #2): subscribing to
 *    a friend immediately delivers the friend's last known location when
 *    it is fresh and in range, so a user who opens the app after being
 *    offline sees the map without waiting for the friend's next move.
 *
 * 2. Fan-out throttling with per-channel publish metrics
 *    (FOLLOW-UPS.md #3 celebrity problem, PITFALLS.md #3 fan-out
 *    multiplier): PubSubBusV2 counts publishes per channel so the
 *    read-to-write ratio is observable, and the service can throttle a
 *    friend's updates to at most one delivery per interval per
 *    subscriber, always delivering the first update after a quiet
 *    period.
 *
 * 3. Out-of-order and invalid update hardening (FOLLOW-UPS.md #4
 *    reconnect storms): a location update older than the stored one is
 *    ignored instead of regressing the user's position, and coordinates
 *    are validated so NaN or out-of-range values never enter the system.
 */
public class NearbyFriendsServiceV2 {
    private final PubSubBusV2 pubSubBus;
    private final ConcurrentHashMap<String, LocationUpdateV2> activeUserLocations;
    private final long throttleIntervalMillis; // 0 means no throttle (v1 behavior)

    private static final double EARTH_RADIUS_MILES = 3958.8;
    private static final double MAX_DISTANCE_MILES = 5.0;
    private static final long TTL_MILLIS = 10 * 60 * 1000; // 10 minutes

    public NearbyFriendsServiceV2(PubSubBusV2 pubSubBus) {
        this(pubSubBus, 0);
    }

    public NearbyFriendsServiceV2(PubSubBusV2 pubSubBus, long throttleIntervalMillis) {
        this.pubSubBus = pubSubBus;
        this.throttleIntervalMillis = throttleIntervalMillis;
        this.activeUserLocations = new ConcurrentHashMap<>();
    }

    /**
     * Updates location for a user and dispatches it to their channel.
     * Out-of-order updates (older than the stored one) are ignored and
     * invalid coordinates are rejected (improvement #3).
     */
    public void updateLocation(String userId, double latitude, double longitude, long timestamp) {
        validateCoordinates(latitude, longitude);
        LocationUpdateV2 update = new LocationUpdateV2(userId, latitude, longitude, timestamp);
        LocationUpdateV2 existing = activeUserLocations.get(userId);
        if (existing != null && timestamp < existing.getTimestamp()) {
            return; // delayed reconnect-storm duplicate must not regress
        }
        activeUserLocations.put(userId, update);
        pubSubBus.publish(userId, update);
    }

    private static void validateCoordinates(double latitude, double longitude) {
        if (Double.isNaN(latitude) || Double.isNaN(longitude)) {
            throw new IllegalArgumentException("coordinates must not be NaN");
        }
        if (latitude < -90.0 || latitude > 90.0) {
            throw new IllegalArgumentException("latitude out of range: " + latitude);
        }
        if (longitude < -180.0 || longitude > 180.0) {
            throw new IllegalArgumentException("longitude out of range: " + longitude);
        }
    }

    /**
     * Subscribe to a friend's location updates. Only receives updates if
     * within TTL and max distance. Delivers the friend's last known
     * location immediately when fresh and in range (improvement #1), and
     * throttles bursts when a throttle interval is configured
     * (improvement #2). Returns the wrapper consumer so the client can
     * unsubscribe later.
     */
    public Consumer<LocationUpdateV2> subscribeToFriend(String userId, String friendId, Consumer<LocationUpdateV2> clientCallback) {
        final AtomicLong lastDelivery = new AtomicLong(Long.MIN_VALUE);

        Consumer<LocationUpdateV2> handler = friendUpdate -> {
            LocationUpdateV2 userLocation = activeUserLocations.get(userId);
            if (userLocation != null) {
                long currentTime = System.currentTimeMillis();
                if (friendUpdate.getTimestamp() >= currentTime - TTL_MILLIS) {
                    double distance = calculateHaversineDistance(
                        userLocation.getLatitude(), userLocation.getLongitude(),
                        friendUpdate.getLatitude(), friendUpdate.getLongitude()
                    );
                    if (distance <= MAX_DISTANCE_MILES) {
                        long now = System.currentTimeMillis();
                        long previous = lastDelivery.get();
                        if (throttleIntervalMillis > 0
                                && previous != Long.MIN_VALUE
                                && now - previous < throttleIntervalMillis) {
                            return; // throttled burst (improvement #2)
                        }
                        lastDelivery.set(now);
                        clientCallback.accept(friendUpdate);
                    }
                }
            }
        };
        pubSubBus.subscribe(friendId, handler);

        // Improvement #1: offline-to-online catch-up snapshot.
        LocationUpdateV2 friendLocation = activeUserLocations.get(friendId);
        LocationUpdateV2 userLocation = activeUserLocations.get(userId);
        if (friendLocation != null && userLocation != null) {
            long currentTime = System.currentTimeMillis();
            if (friendLocation.getTimestamp() >= currentTime - TTL_MILLIS) {
                double distance = calculateHaversineDistance(
                    userLocation.getLatitude(), userLocation.getLongitude(),
                    friendLocation.getLatitude(), friendLocation.getLongitude()
                );
                if (distance <= MAX_DISTANCE_MILES) {
                    lastDelivery.set(System.currentTimeMillis());
                    clientCallback.accept(friendLocation);
                }
            }
        }

        return handler;
    }

    /**
     * Unsubscribe from a friend's updates using the handler returned by subscribeToFriend.
     */
    public void unsubscribeFromFriend(String friendId, Consumer<LocationUpdateV2> handler) {
        pubSubBus.unsubscribe(friendId, handler);
    }

    /**
     * Calculates distance between two coordinates using Haversine formula in miles.
     */
    public static double calculateHaversineDistance(double lat1, double lon1, double lat2, double lon2) {
        double dLat = Math.toRadians(lat2 - lat1);
        double dLon = Math.toRadians(lon2 - lon1);
        lat1 = Math.toRadians(lat1);
        lat2 = Math.toRadians(lat2);

        double a = Math.sin(dLat / 2) * Math.sin(dLat / 2) +
                Math.sin(dLon / 2) * Math.sin(dLon / 2) * Math.cos(lat1) * Math.cos(lat2);
        double c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
        return EARTH_RADIUS_MILES * c;
    }

    public LocationUpdateV2 getUserLocation(String userId) {
        return activeUserLocations.get(userId);
    }
}
