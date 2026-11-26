/**
 * Location.java - GPS location.
 */
public class Location {
    private final double latitude;
    private final double longitude;
    private final String address;

    public Location(double lat, double lng, String address) {
        this.latitude = lat;
        this.longitude = lng;
        this.address = address;
    }

    public double getLatitude() {
        return latitude;
    }

    public double getLongitude() {
        return longitude;
    }

    public String getAddress() {
        return address;
    }

    public double distanceTo(Location other) {
        double latDiff = Math.abs(this.latitude - other.latitude);
        double lngDiff = Math.abs(this.longitude - other.longitude);
        return Math.sqrt(latDiff * latDiff + lngDiff * lngDiff) * 111; // approx km
    }

    @Override
    public String toString() {
        return address;
    }
}
