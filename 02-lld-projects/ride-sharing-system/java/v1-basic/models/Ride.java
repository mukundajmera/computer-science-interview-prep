import enums.RideStatus;

/**
 * Ride.java - A ride request.
 */
public class Ride {
    private final String id;
    private final Rider rider;
    private Driver driver;
    private final Location pickup;
    private final Location dropoff;
    private RideStatus status;
    private double fare;
    private static final double BASE_FARE = 5.0;
    private static final double PER_KM = 2.0;

    public Ride(String id, Rider rider, Location pickup, Location dropoff) {
        this.id = id;
        this.rider = rider;
        this.pickup = pickup;
        this.dropoff = dropoff;
        this.status = RideStatus.REQUESTED;
        this.fare = calculateFare();
    }

    private double calculateFare() {
        double distance = pickup.distanceTo(dropoff);
        return BASE_FARE + (distance * PER_KM);
    }

    public void assignDriver(Driver d) {
        this.driver = d;
        this.status = RideStatus.MATCHED;
    }

    public void start() {
        this.status = RideStatus.IN_PROGRESS;
    }

    public void complete() {
        this.status = RideStatus.COMPLETED;
    }

    public void cancel() {
        this.status = RideStatus.CANCELLED;
    }

    public String getId() {
        return id;
    }

    public Rider getRider() {
        return rider;
    }

    public Driver getDriver() {
        return driver;
    }

    public RideStatus getStatus() {
        return status;
    }

    public double getFare() {
        return fare;
    }

    @Override
    public String toString() {
        return String.format("Ride[%s: %s -> %s, $%.2f, %s]", id, pickup, dropoff, fare, status);
    }
}
