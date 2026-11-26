
public class Location {
    private final double lat;
    private final double lon;
    private final long timestamp;

    public Location(double lat, double lon) {
        this(lat, lon, 0L);
    }

    public Location(double lat, double lon, long timestamp) {
        this.lat = lat;
        this.lon = lon;
        this.timestamp = timestamp;
    }

    public double getLat() {
        return lat;
    }

    public double getLon() {
        return lon;
    }

    public long getTimestamp() {
        return timestamp;
    }

    public double distanceTo(Location other) {
        return Math.hypot(this.lat - other.lat, this.lon - other.lon);
    }
}
