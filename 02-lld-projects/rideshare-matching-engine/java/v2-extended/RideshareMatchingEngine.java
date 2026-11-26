import java.util.*;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.locks.Lock;
import java.util.concurrent.locks.ReentrantLock;
import java.util.stream.Collectors;

public class RideshareMatchingEngine {
    private final PricingEngine pricingEngine;
    private final double searchRadius;
    private final Map<String, Driver> drivers = new ConcurrentHashMap<>();
    private final Map<String, Trip> trips = new ConcurrentHashMap<>();
    private final List<Trip> batchQueue = new ArrayList<>();
    private final SpatialIndex spatialIndex = new SpatialIndex();
    private final Lock lock = new ReentrantLock();

    public RideshareMatchingEngine(PricingEngine pricingEngine) {
        this(pricingEngine, 10.0);
    }

    public RideshareMatchingEngine(PricingEngine pricingEngine, double searchRadius) {
        this.pricingEngine = pricingEngine;
        this.searchRadius = searchRadius;
    }

    public void registerDriver(Driver driver) {
        lock.lock();
        try {
            drivers.put(driver.getDriverId(), driver);
            if (driver.getState() == DriverState.IDLE) {
                pricingEngine.updateSupplyDemand(1, 0);
                spatialIndex.addDriver(driver);
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
                    spatialIndex.removeDriver(driver);
                } else if (oldState != DriverState.IDLE && newState == DriverState.IDLE) {
                    pricingEngine.updateSupplyDemand(1, 0);
                    spatialIndex.addDriver(driver);
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
            String gh = spatialIndex.toGeohash(location, 5);
            Set<String> driverIds = spatialIndex.getDriversInGeohash(gh);
            
            List<Driver> idleDrivers;
            if (driverIds.size() >= limit) {
                 idleDrivers = driverIds.stream()
                    .map(drivers::get)
                    .filter(d -> d.getState() == DriverState.IDLE && d.getLocation().distanceTo(location) <= searchRadius)
                    .collect(Collectors.toList());
            } else {
                 idleDrivers = drivers.values().stream()
                    .filter(d -> d.getState() == DriverState.IDLE && d.getLocation().distanceTo(location) <= searchRadius)
                    .collect(Collectors.toList());
            }

            idleDrivers.sort(Comparator.comparingDouble(d -> d.getLocation().distanceTo(location)));

            return idleDrivers.stream().limit(limit).collect(Collectors.toList());
        } finally {
            lock.unlock();
        }
    }

    public Trip requestRide(Rider rider, Location destination) {
        Location origin = rider.getLocation();

        pricingEngine.updateSupplyDemand(0, 1);
        double price = pricingEngine.estimatePrice(origin, destination);

        String tripId = UUID.randomUUID().toString();
        Trip trip = new Trip(tripId, rider, origin, destination, price);

        lock.lock();
        try {
            trips.put(tripId, trip);
            batchQueue.add(trip);
            return trip;
        } finally {
            lock.unlock();
        }
    }

    public void runBatchAuction() {
        lock.lock();
        try {
            if (batchQueue.isEmpty()) {
                return;
            }

            List<Trip> tripsToMatch = new ArrayList<>(batchQueue);
            batchQueue.clear();

            List<Driver> idleDrivers = drivers.values().stream()
                    .filter(d -> d.getState() == DriverState.IDLE)
                    .collect(Collectors.toList());

            Map<Trip, Driver> matches = BatchAuctionMatcher.match(idleDrivers, tripsToMatch);

            for (Trip trip : tripsToMatch) {
                if (matches.containsKey(trip)) {
                    Driver driver = matches.get(trip);
                    if (driver.transitionState(DriverState.ASSIGNED)) {
                        spatialIndex.removeDriver(driver);
                        if (trip.assignDriver(driver)) {
                            pricingEngine.updateSupplyDemand(-1, -1);
                        } else {
                            driver.transitionState(DriverState.IDLE);
                            spatialIndex.addDriver(driver);
                            batchQueue.add(trip); // retry next batch
                        }
                    } else {
                        batchQueue.add(trip); // retry next batch
                    }
                } else {
                    batchQueue.add(trip); // failed to find driver this batch
                }
            }
        } finally {
            lock.unlock();
        }
    }

    public List<Trip> getBatchQueue() {
        return batchQueue;
    }
}
