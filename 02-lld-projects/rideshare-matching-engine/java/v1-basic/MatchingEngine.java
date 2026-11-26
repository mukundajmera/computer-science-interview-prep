package v1_basic;

import java.util.*;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.locks.Lock;
import java.util.concurrent.locks.ReentrantLock;
import java.util.stream.Collectors;

/**
 * V1 Basic Version: Uses brute force spatial search and lock-free/coarse-grained driver lists.
 */
public class MatchingEngine {
    private final PricingEngine pricingEngine;
    private final double searchRadius;
    private final Map<String, Driver> drivers = new ConcurrentHashMap<>();
    private final Map<String, Trip> trips = new ConcurrentHashMap<>();
    private final Lock lock = new ReentrantLock();

    public MatchingEngine(PricingEngine pricingEngine) {
        this(pricingEngine, 10.0);
    }

    public MatchingEngine(PricingEngine pricingEngine, double searchRadius) {
        this.pricingEngine = pricingEngine;
        this.searchRadius = searchRadius;
    }

    public void registerDriver(Driver driver) {
        if (driver == null) return;
        lock.lock();
        try {
            if (drivers.containsKey(driver.getDriverId())) return;
            drivers.put(driver.getDriverId(), driver);
            if (driver.getState() == DriverState.IDLE) {
                pricingEngine.updateSupplyDemand(1, 0);
            }
        } finally {
            lock.unlock();
        }
    }

    public boolean updateDriverState(String driverId, DriverState newState) {
        lock.lock();
        try {
            Driver driver = drivers.get(driverId);
            if (driver == null) {
                return false;
            }

            DriverState oldState = driver.getState();
            boolean success = driver.transitionState(newState);

            if (success) {
                if (oldState == DriverState.IDLE && newState != DriverState.IDLE) {
                    pricingEngine.updateSupplyDemand(-1, 0);
                } else if (oldState != DriverState.IDLE && newState == DriverState.IDLE) {
                    pricingEngine.updateSupplyDemand(1, 0);
                }
            }
            return success;
        } finally {
            lock.unlock();
        }
    }

    public List<Driver> findNearestDrivers(Location location, int limit) {
        lock.lock();
        try {
            List<Driver> idleDrivers = drivers.values().stream()
                    .filter(d -> d.getState() == DriverState.IDLE && d.getLocation().distanceTo(location) <= searchRadius)
                    .collect(Collectors.toList());

            idleDrivers.sort(Comparator.comparingDouble(d -> d.getLocation().distanceTo(location)));

            return idleDrivers.stream().limit(limit).collect(Collectors.toList());
        } finally {
            lock.unlock();
        }
    }

    public Trip requestRide(Rider rider, Location destination) {
        if (rider == null || destination == null) return null;
        Location origin = rider.getLocation();

        pricingEngine.updateSupplyDemand(0, 1);
        double price = pricingEngine.estimatePrice(origin, destination);

        String tripId = UUID.randomUUID().toString();
        Trip trip = new Trip(tripId, rider, origin, destination, price);

        lock.lock();
        try {
            trips.put(tripId, trip);

            List<Driver> nearestDrivers = findNearestDrivers(origin, 5);
            for (Driver driver : nearestDrivers) {
                if (driver.transitionState(DriverState.ASSIGNED)) {
                    if (trip.assignDriver(driver)) {
                        pricingEngine.updateSupplyDemand(-1, -1);
                        return trip;
                    } else {
                        driver.transitionState(DriverState.IDLE);
                    }
                }
            }

            pricingEngine.updateSupplyDemand(0, -1);
            trip.setState(TripState.CANCELLED);
            return null; // Equivalent to returning None in Python when matched driver is not found
        } finally {
            lock.unlock();
        }
    }
}
