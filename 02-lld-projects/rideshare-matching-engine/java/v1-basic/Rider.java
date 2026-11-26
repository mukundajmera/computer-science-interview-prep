package v1_basic;

public class Rider {
    private final String riderId;
    private final Location location;

    public Rider(String riderId, Location location) {
        this.riderId = riderId;
        this.location = location;
    }

    public String getRiderId() {
        return riderId;
    }

    public Location getLocation() {
        return location;
    }
}
