/**
 * v2 LocationUpdate: identical value shape to v1.
 * See NearbyFriendsServiceV2 for the v2 improvement list.
 */
public class LocationUpdateV2 {
    private final String userId;
    private final double latitude;
    private final double longitude;
    private final long timestamp;

    public LocationUpdateV2(String userId, double latitude, double longitude, long timestamp) {
        this.userId = userId;
        this.latitude = latitude;
        this.longitude = longitude;
        this.timestamp = timestamp;
    }

    public String getUserId() {
        return userId;
    }

    public double getLatitude() {
        return latitude;
    }

    public double getLongitude() {
        return longitude;
    }

    public long getTimestamp() {
        return timestamp;
    }
}
