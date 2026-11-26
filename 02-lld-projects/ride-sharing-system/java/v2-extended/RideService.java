import models.*;
import java.util.*;

/**
 * RideService.java - Singleton ride matching service.
 */
public class RideService {
    private static RideService instance;
    private final Map<String, Driver> drivers;
    private final Map<String, Rider> riders;
    private final Map<String, Ride> rides;
    private int rideCounter;

    private RideService() {
        drivers = new HashMap<>();
        riders = new HashMap<>();
        rides = new HashMap<>();
        rideCounter = 0;
    }

    public static synchronized RideService getInstance() {
        if (instance == null)
            instance = new RideService();
        return instance;
    }

    public void registerDriver(Driver d) {
        drivers.put(d.getId(), d);
    }

    public void registerRider(Rider r) {
        riders.put(r.getId(), r);
    }

    public Ride requestRide(String riderId, Location pickup, Location dropoff) {
        Rider rider = riders.get(riderId);
        if (rider == null)
            return null;

        String rideId = "RIDE-" + (++rideCounter);
        Ride ride = new Ride(rideId, rider, pickup, dropoff);
        rides.put(rideId, ride);

        // Match with nearest available driver
        Driver driver = findNearestDriver(pickup);
        if (driver != null) {
            ride.assignDriver(driver);
            driver.setAvailable(false);
            System.out.println("Matched: " + driver.getName());
        }

        return ride;
    }

    private Driver findNearestDriver(Location pickup) {
        Driver nearest = null;
        double minDist = Double.MAX_VALUE;
        for (Driver d : drivers.values()) {
            if (d.isAvailable() && d.getCurrentLocation() != null) {
                double dist = d.getCurrentLocation().distanceTo(pickup);
                if (dist < minDist) {
                    minDist = dist;
                    nearest = d;
                }
            }
        }
        return nearest;
    }

    public void completeRide(String rideId) {
        Ride ride = rides.get(rideId);
        if (ride != null && ride.getDriver() != null) {
            ride.complete();
            ride.getDriver().setAvailable(true);
            System.out.printf("Ride completed. Fare: $%.2f%n", ride.getFare());
        }
    }
}
