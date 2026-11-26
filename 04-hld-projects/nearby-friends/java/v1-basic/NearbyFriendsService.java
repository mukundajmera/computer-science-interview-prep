import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.ConcurrentHashMap;
import java.util.function.Consumer;

public class NearbyFriendsService {
    private final PubSubBus pubSubBus;
    private final ConcurrentHashMap<String, LocationUpdate> activeUserLocations;
    
    private static final double EARTH_RADIUS_MILES = 3958.8;
    private static final double MAX_DISTANCE_MILES = 5.0;
    private static final long TTL_MILLIS = 10 * 60 * 1000; // 10 minutes

    public NearbyFriendsService(PubSubBus pubSubBus) {
        this.pubSubBus = pubSubBus;
        this.activeUserLocations = new ConcurrentHashMap<>();
    }

    /**
     * Updates location for a user and dispatches it to their channel.
     */
    public void updateLocation(String userId, double latitude, double longitude, long timestamp) {
        LocationUpdate update = new LocationUpdate(userId, latitude, longitude, timestamp);
        activeUserLocations.put(userId, update);
        pubSubBus.publish(userId, update);
    }
    
    /**
     * Subscribe to a friend's location updates. Only receives updates if within TTL and max distance.
     * Returns the wrapper consumer so the client can unsubscribe later.
     */
    public Consumer<LocationUpdate> subscribeToFriend(String userId, String friendId, Consumer<LocationUpdate> clientCallback) {
        Consumer<LocationUpdate> handler = friendUpdate -> {
            LocationUpdate userLocation = activeUserLocations.get(userId);
            if (userLocation != null) {
                long currentTime = System.currentTimeMillis();
                if (friendUpdate.getTimestamp() >= currentTime - TTL_MILLIS) {
                    double distance = calculateHaversineDistance(
                        userLocation.getLatitude(), userLocation.getLongitude(),
                        friendUpdate.getLatitude(), friendUpdate.getLongitude()
                    );
                    if (distance <= MAX_DISTANCE_MILES) {
                        clientCallback.accept(friendUpdate);
                    }
                }
            }
        };
        pubSubBus.subscribe(friendId, handler);
        return handler;
    }

    /**
     * Unsubscribe from a friend's updates using the handler returned by subscribeToFriend.
     */
    public void unsubscribeFromFriend(String friendId, Consumer<LocationUpdate> handler) {
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

    public LocationUpdate getUserLocation(String userId) {
        return activeUserLocations.get(userId);
    }
}
