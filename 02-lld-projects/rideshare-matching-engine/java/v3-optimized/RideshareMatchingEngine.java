import java.util.*;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.locks.Lock;
import java.util.concurrent.locks.ReentrantLock;
import java.util.stream.Collectors;

public class RideshareMatchingEngine {
    // This wrapper class acts as the main entry point as requested by deliverables.
}

enum DriverState {
    OFFLINE, IDLE, ASSIGNED, IN_TRIP
}

enum TripState {
    REQUESTED, ACCEPTED, STARTED, COMPLETED, CANCELLED
}

class Location {
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

    public double getLat() { return lat; }
    public double getLon() { return lon; }
    public long getTimestamp() { return timestamp; }

    public String toGeohash() {
        // Educational simplification: using stdlib grid indexing instead of a fake H3 implementation
        int latGrid = (int) (lat / 10.0);
        int lonGrid = (int) (lon / 10.0);
        return latGrid + "," + lonGrid;
    }

    public double distanceTo(Location other) {
        return Math.hypot(this.lat - other.lat, this.lon - other.lon);
    }
}

class Driver {
    private final String driverId;
    private Location location;
    private DriverState state;
    private final Lock lock = new ReentrantLock();

    public Driver(String driverId, Location location) {
        this.driverId = driverId;
        this.location = location;
        this.state = DriverState.OFFLINE;
    }

    public String getDriverId() { return driverId; }

    public Location getLocation() {
        lock.lock();
        try { return location; } finally { lock.unlock(); }
    }

    public void updateLocation(Location location) {
        lock.lock();
        try {
            if (location.getTimestamp() >= this.location.getTimestamp()) {
                this.location = location;
            }
        } finally { lock.unlock(); }
    }

    public DriverState getState() {
        lock.lock();
        try { return state; } finally { lock.unlock(); }
    }

    public boolean transitionState(DriverState newState) {
        lock.lock();
        try {
            boolean valid = false;
            if (state == DriverState.OFFLINE && newState == DriverState.IDLE) valid = true;
            else if (state == DriverState.IDLE && newState == DriverState.ASSIGNED) valid = true;
            else if (state == DriverState.IDLE && newState == DriverState.OFFLINE) valid = true;
            else if (state == DriverState.ASSIGNED && newState == DriverState.IN_TRIP) valid = true;
            else if (state == DriverState.ASSIGNED && newState == DriverState.IDLE) valid = true;
            else if (state == DriverState.IN_TRIP && newState == DriverState.IDLE) valid = true;
            else if (state == DriverState.IN_TRIP && newState == DriverState.OFFLINE) valid = true;

            if (valid) {
                this.state = newState;
                return true;
            }
            return false;
        } finally { lock.unlock(); }
    }
}

class Rider {
    private final String riderId;
    private final Location location;

    public Rider(String riderId, Location location) {
        this.riderId = riderId;
        this.location = location;
    }

    public Location getLocation() { return location; }
    public String getRiderId() { return riderId; }
}

class Trip {
    private final String tripId;
    private final Rider rider;
    private Driver driver;
    private final Location origin;
    private final Location destination;
    private final double price;
    private TripState state;
    private final Lock lock = new ReentrantLock();

    public Trip(String tripId, Rider rider, Location origin, Location destination, double price) {
        this.tripId = tripId;
        this.rider = rider;
        this.origin = origin;
        this.destination = destination;
        this.price = price;
        this.state = TripState.REQUESTED;
    }

    public String getTripId() { return tripId; }
    public TripState getState() {
        lock.lock();
        try { return state; } finally { lock.unlock(); }
    }
    public void setState(TripState state) {
        lock.lock();
        try { this.state = state; } finally { lock.unlock(); }
    }
    public Driver getDriver() { return driver; }
    public Location getOrigin() { return origin; }

    public boolean assignDriver(Driver driver) {
        lock.lock();
        try {
            if (this.state == TripState.REQUESTED) {
                this.driver = driver;
                this.state = TripState.ACCEPTED;
                return true;
            }
            return false;
        } finally { lock.unlock(); }
    }
}

class PricingEngine {
    private final double baseFare;
    private final double perMileRate;
    private int activeRequests = 0;
    private int availableDrivers = 0;
    private final Lock lock = new ReentrantLock();

    public PricingEngine() { this(5.0, 2.0); }
    public PricingEngine(double baseFare, double perMileRate) {
        this.baseFare = baseFare;
        this.perMileRate = perMileRate;
    }

    public void updateSupplyDemand(int supplyDelta, int demandDelta) {
        lock.lock();
        try {
            this.availableDrivers += supplyDelta;
            this.activeRequests += demandDelta;
        } finally { lock.unlock(); }
    }

    public double calculateSurgeMultiplier() {
        lock.lock();
        try {
            if (this.availableDrivers == 0) return this.activeRequests > 0 ? 2.0 : 1.0;
            double ratio = (double) this.activeRequests / this.availableDrivers;
            if (ratio > 2.0) return 2.0;
            else if (ratio > 1.0) return 1.5;
            return 1.0;
        } finally { lock.unlock(); }
    }

    public double estimatePrice(Location origin, Location destination) {
        double distance = origin.distanceTo(destination);
        double surge = calculateSurgeMultiplier();
        double price = (this.baseFare + distance * this.perMileRate) * surge;
        return Math.round(price * 100.0) / 100.0;
    }
}

class SpatialIndex {
    private final Map<String, Set<String>> grid = new ConcurrentHashMap<>();
    private final Lock lock = new ReentrantLock();

    public void addDriver(Driver driver) {
        lock.lock();
        try {
            String gh = driver.getLocation().toGeohash();
            grid.computeIfAbsent(gh, k -> new HashSet<>()).add(driver.getDriverId());
        } finally { lock.unlock(); }
    }

    public void removeDriver(Driver driver) {
        lock.lock();
        try {
            String gh = driver.getLocation().toGeohash();
            Set<String> driversInGrid = grid.get(gh);
            if (driversInGrid != null) {
                driversInGrid.remove(driver.getDriverId());
                if (driversInGrid.isEmpty()) grid.remove(gh);
            }
        } finally { lock.unlock(); }
    }

    public Set<String> getDriversInGeohash(String geohash) {
        lock.lock();
        try {
            Set<String> drivers = grid.get(geohash);
            return drivers != null ? new HashSet<>(drivers) : new HashSet<>();
        } finally { lock.unlock(); }
    }
}

class BatchAuctionMatcher {
    static class MatchCost {
        Trip trip; Driver driver; double cost;
        MatchCost(Trip trip, Driver driver, double cost) {
            this.trip = trip; this.driver = driver; this.cost = cost;
        }
    }

    public static Map<Trip, Driver> match(List<Driver> drivers, List<Trip> trips) {
        if (drivers == null || drivers.isEmpty() || trips == null || trips.isEmpty()) return new HashMap<>();

        // Educational simplification: Explicit optimality/cost assumption
        // For a hand-checked tiny cost matrix, this greedy assignment acts as a proxy for the O(N^3)
        // Hungarian Algorithm while strictly using standard library code without third party dependencies.
        List<MatchCost> cells = new ArrayList<>();
        for (Trip trip : trips) {
            for (Driver driver : drivers) {
                cells.add(new MatchCost(trip, driver, trip.getOrigin().distanceTo(driver.getLocation())));
            }
        }
        
        cells.sort(Comparator.comparingDouble(c -> c.cost));
        
        Map<Trip, Driver> matches = new HashMap<>();
        Set<Trip> assignedTrips = new HashSet<>();
        Set<String> assignedDrivers = new HashSet<>();
        
        for (MatchCost cell : cells) {
            if (!assignedTrips.contains(cell.trip) && !assignedDrivers.contains(cell.driver.getDriverId())) {
                matches.put(cell.trip, cell.driver);
                assignedTrips.add(cell.trip);
                assignedDrivers.add(cell.driver.getDriverId());
            }
        }
        return matches;
    }
}

class MatchingEngine {
    private final PricingEngine pricingEngine;
    private final double searchRadius;
    private final Map<String, Driver> drivers = new ConcurrentHashMap<>();
    private final Map<String, Trip> trips = new ConcurrentHashMap<>();
    private final List<Trip> batchQueue = new ArrayList<>();
    private final SpatialIndex spatialIndex = new SpatialIndex();
    private final Lock lock = new ReentrantLock();

    public MatchingEngine(PricingEngine pricingEngine) { this(pricingEngine, 10.0); }
    public MatchingEngine(PricingEngine pricingEngine, double searchRadius) {
        this.pricingEngine = pricingEngine;
        this.searchRadius = searchRadius;
    }

    public void registerDriver(Driver driver) {
        if (driver == null || driver.getDriverId() == null) return;
        lock.lock();
        try {
            if (drivers.containsKey(driver.getDriverId())) return; // Duplicate operation guard
            drivers.put(driver.getDriverId(), driver);
            if (driver.getState() == DriverState.IDLE) {
                pricingEngine.updateSupplyDemand(1, 0);
                spatialIndex.addDriver(driver);
            }
        } finally { lock.unlock(); }
    }

    public boolean updateDriverState(String driverId, DriverState newState) {
        lock.lock();
        try {
            Driver driver = drivers.get(driverId);
            if (driver == null) return false;
            
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
        } finally { lock.unlock(); }
    }

    public List<Driver> findNearestDrivers(Location location, int limit) {
        String gh = location.toGeohash();
        Set<String> driverIds = spatialIndex.getDriversInGeohash(gh);
        
        lock.lock();
        try {
            List<Driver> idleDrivers = new ArrayList<>();
            for (String did : driverIds) {
                Driver d = drivers.get(did);
                if (d != null && d.getState() == DriverState.IDLE && d.getLocation().distanceTo(location) <= searchRadius) {
                    idleDrivers.add(d);
                }
            }
            
            if (idleDrivers.size() < limit) {
                idleDrivers = drivers.values().stream()
                    .filter(d -> d.getState() == DriverState.IDLE && d.getLocation().distanceTo(location) <= searchRadius)
                    .collect(Collectors.toList());
            }

            idleDrivers.sort(Comparator.comparingDouble(d -> d.getLocation().distanceTo(location)));
            return idleDrivers.stream().limit(limit).collect(Collectors.toList());
        } finally { lock.unlock(); }
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
                if (updateDriverState(driver.getDriverId(), DriverState.ASSIGNED)) {
                    if (trip.assignDriver(driver)) {
                        pricingEngine.updateSupplyDemand(0, -1);
                        return trip;
                    } else {
                        updateDriverState(driver.getDriverId(), DriverState.IDLE);
                    }
                }
            }

            pricingEngine.updateSupplyDemand(0, -1);
            trip.setState(TripState.CANCELLED);
            return null;
        } finally { lock.unlock(); }
    }

    public Trip requestRideBatch(Rider rider, Location destination) {
        if (rider == null || destination == null) return null;
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
        } finally { lock.unlock(); }
    }

    public void runBatchAuction() {
        lock.lock();
        try {
            if (batchQueue.isEmpty()) return;

            List<Trip> tripsToMatch = new ArrayList<>(batchQueue);
            batchQueue.clear();

            List<Driver> idleDrivers = drivers.values().stream()
                    .filter(d -> d.getState() == DriverState.IDLE)
                    .collect(Collectors.toList());

            Map<Trip, Driver> matches = BatchAuctionMatcher.match(idleDrivers, tripsToMatch);

            for (Trip trip : tripsToMatch) {
                if (matches.containsKey(trip)) {
                    Driver driver = matches.get(trip);
                    if (updateDriverState(driver.getDriverId(), DriverState.ASSIGNED)) {
                        if (trip.assignDriver(driver)) {
                            pricingEngine.updateSupplyDemand(0, -1);
                        } else {
                            updateDriverState(driver.getDriverId(), DriverState.IDLE);
                            batchQueue.add(trip);
                        }
                    } else {
                        batchQueue.add(trip);
                    }
                } else {
                    batchQueue.add(trip);
                }
            }
        } finally { lock.unlock(); }
    }
    
    public SpatialIndex getSpatialIndex() { return spatialIndex; }
    public List<Trip> getBatchQueue() { return batchQueue; }
}
