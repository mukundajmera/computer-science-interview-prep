import java.util.*;

/**
 * Ride Sharing System - V1 Basic
 * Core entities for the ride sharing system.
 */

/**
 * Represents GPS coordinates.
 */
class Location {
    private final double latitude;
    private final double longitude;
    
    public Location(double latitude, double longitude) {
        this.latitude = latitude;
        this.longitude = longitude;
    }
    
    public double getLatitude() { return latitude; }
    public double getLongitude() { return longitude; }
    
    /**
     * Calculate distance to another location (simplified Euclidean).
     */
    public double distanceTo(Location other) {
        double latDiff = this.latitude - other.latitude;
        double lonDiff = this.longitude - other.longitude;
        // Simplified: 1 degree ≈ 111 km
        return Math.sqrt(latDiff * latDiff + lonDiff * lonDiff) * 111;
    }
    
    @Override
    public String toString() {
        return String.format("(%.4f, %.4f)", latitude, longitude);
    }
}

/**
 * Vehicle types available.
 */
enum VehicleType {
    BIKE(1, 1.0),
    AUTO(3, 1.5),
    CAR(4, 2.0),
    PREMIUM(4, 3.0);
    
    private final int capacity;
    private final double rateMultiplier;
    
    VehicleType(int capacity, double rateMultiplier) {
        this.capacity = capacity;
        this.rateMultiplier = rateMultiplier;
    }
    
    public int getCapacity() { return capacity; }
    public double getRateMultiplier() { return rateMultiplier; }
}

/**
 * Driver status.
 */
enum DriverStatus {
    AVAILABLE, BUSY, OFFLINE
}

/**
 * Trip status.
 */
enum TripStatus {
    REQUESTED, MATCHED, IN_PROGRESS, COMPLETED, CANCELLED
}

/**
 * Represents a vehicle.
 */
class Vehicle {
    private final String id;
    private final VehicleType type;
    private final String licensePlate;
    
    public Vehicle(String id, VehicleType type, String licensePlate) {
        this.id = id;
        this.type = type;
        this.licensePlate = licensePlate;
    }
    
    public String getId() { return id; }
    public VehicleType getType() { return type; }
    public String getLicensePlate() { return licensePlate; }
}

/**
 * Represents a rider (passenger).
 */
class Rider {
    private final String id;
    private final String name;
    private final String phone;
    private Location currentLocation;
    private final List<Trip> tripHistory;
    private double rating;
    private int ratingCount;
    
    public Rider(String id, String name, String phone) {
        this.id = id;
        this.name = name;
        this.phone = phone;
        this.tripHistory = new ArrayList<>();
        this.rating = 5.0;
        this.ratingCount = 0;
    }
    
    public String getId() { return id; }
    public String getName() { return name; }
    public String getPhone() { return phone; }
    public Location getCurrentLocation() { return currentLocation; }
    public List<Trip> getTripHistory() { return new ArrayList<>(tripHistory); }
    public double getRating() { return rating; }
    
    public void setCurrentLocation(Location location) {
        this.currentLocation = location;
    }
    
    public void addTrip(Trip trip) {
        tripHistory.add(trip);
    }
    
    public void addRating(int stars) {
        ratingCount++;
        rating = ((rating * (ratingCount - 1)) + stars) / ratingCount;
    }
    
    @Override
    public String toString() {
        return String.format("Rider[%s] %s", id, name);
    }
}

/**
 * Represents a driver.
 */
class Driver {
    private final String id;
    private final String name;
    private final String phone;
    private final Vehicle vehicle;
    private Location currentLocation;
    private DriverStatus status;
    private double rating;
    private int ratingCount;
    private final List<Trip> tripHistory;
    
    public Driver(String id, String name, String phone, Vehicle vehicle) {
        this.id = id;
        this.name = name;
        this.phone = phone;
        this.vehicle = vehicle;
        this.status = DriverStatus.OFFLINE;
        this.rating = 5.0;
        this.ratingCount = 0;
        this.tripHistory = new ArrayList<>();
    }
    
    public String getId() { return id; }
    public String getName() { return name; }
    public String getPhone() { return phone; }
    public Vehicle getVehicle() { return vehicle; }
    public Location getCurrentLocation() { return currentLocation; }
    public DriverStatus getStatus() { return status; }
    public double getRating() { return rating; }
    public List<Trip> getTripHistory() { return new ArrayList<>(tripHistory); }
    
    public void updateLocation(Location location) {
        this.currentLocation = location;
    }
    
    public void setStatus(DriverStatus status) {
        this.status = status;
    }
    
    public void setAvailable() {
        this.status = DriverStatus.AVAILABLE;
    }
    
    public void setBusy() {
        this.status = DriverStatus.BUSY;
    }
    
    public void setOffline() {
        this.status = DriverStatus.OFFLINE;
    }
    
    public void addTrip(Trip trip) {
        tripHistory.add(trip);
    }
    
    public void addRating(int stars) {
        ratingCount++;
        rating = ((rating * (ratingCount - 1)) + stars) / ratingCount;
    }
    
    public boolean isAvailable() {
        return status == DriverStatus.AVAILABLE && currentLocation != null;
    }
    
    @Override
    public String toString() {
        return String.format("Driver[%s] %s (%s)", id, name, vehicle.getType());
    }
}

/**
 * Represents fare calculation.
 */
class Fare {
    private static final double BASE_FARE = 5.0;
    private static final double PER_KM_RATE = 1.0;
    private static final double PER_MINUTE_RATE = 0.15;
    
    private final double distance;
    private final int durationMinutes;
    private final VehicleType vehicleType;
    private double total;
    
    public Fare(double distance, int durationMinutes, VehicleType vehicleType) {
        this.distance = distance;
        this.durationMinutes = durationMinutes;
        this.vehicleType = vehicleType;
        calculate();
    }
    
    private void calculate() {
        double basePart = BASE_FARE;
        double distancePart = distance * PER_KM_RATE;
        double timePart = durationMinutes * PER_MINUTE_RATE;
        
        this.total = (basePart + distancePart + timePart) * vehicleType.getRateMultiplier();
    }
    
    public double getTotal() { return total; }
    public double getDistance() { return distance; }
    
    public void display() {
        System.out.printf("Fare: $%.2f (%.1f km, %d min, %s)%n", 
            total, distance, durationMinutes, vehicleType);
    }
    
    @Override
    public String toString() {
        return String.format("$%.2f", total);
    }
}

/**
 * Represents a trip/ride.
 */
class Trip {
    private final String id;
    private final Rider rider;
    private Driver driver;
    private final Location pickup;
    private final Location dropoff;
    private final VehicleType requestedType;
    private TripStatus status;
    private Fare fare;
    private final Date requestTime;
    private Date startTime;
    private Date endTime;
    private int riderRating;
    private int driverRating;
    
    public Trip(String id, Rider rider, Location pickup, Location dropoff, VehicleType type) {
        this.id = id;
        this.rider = rider;
        this.pickup = pickup;
        this.dropoff = dropoff;
        this.requestedType = type;
        this.status = TripStatus.REQUESTED;
        this.requestTime = new Date();
    }
    
    public String getId() { return id; }
    public Rider getRider() { return rider; }
    public Driver getDriver() { return driver; }
    public Location getPickup() { return pickup; }
    public Location getDropoff() { return dropoff; }
    public VehicleType getRequestedType() { return requestedType; }
    public TripStatus getStatus() { return status; }
    public Fare getFare() { return fare; }
    public Date getRequestTime() { return requestTime; }
    public Date getStartTime() { return startTime; }
    public Date getEndTime() { return endTime; }
    
    public void assignDriver(Driver driver) {
        this.driver = driver;
        this.status = TripStatus.MATCHED;
        driver.setBusy();
    }
    
    public void start() {
        if (status != TripStatus.MATCHED) {
            throw new IllegalStateException("Cannot start trip in state: " + status);
        }
        this.status = TripStatus.IN_PROGRESS;
        this.startTime = new Date();
    }
    
    public void complete(int durationMinutes) {
        if (status != TripStatus.IN_PROGRESS) {
            throw new IllegalStateException("Cannot complete trip in state: " + status);
        }
        this.status = TripStatus.COMPLETED;
        this.endTime = new Date();
        
        double distance = pickup.distanceTo(dropoff);
        this.fare = new Fare(distance, durationMinutes, requestedType);
        
        if (driver != null) {
            driver.setAvailable();
            driver.addTrip(this);
        }
        rider.addTrip(this);
    }
    
    public void cancel() {
        if (status == TripStatus.IN_PROGRESS || status == TripStatus.COMPLETED) {
            throw new IllegalStateException("Cannot cancel trip in state: " + status);
        }
        this.status = TripStatus.CANCELLED;
        if (driver != null) {
            driver.setAvailable();
        }
    }
    
    public void rateDriver(int stars) {
        if (status != TripStatus.COMPLETED) {
            throw new IllegalStateException("Can only rate after completion");
        }
        if (stars < 1 || stars > 5) {
            throw new IllegalArgumentException("Rating must be 1-5");
        }
        this.driverRating = stars;
        if (driver != null) {
            driver.addRating(stars);
        }
    }
    
    public void rateRider(int stars) {
        if (status != TripStatus.COMPLETED) {
            throw new IllegalStateException("Can only rate after completion");
        }
        if (stars < 1 || stars > 5) {
            throw new IllegalArgumentException("Rating must be 1-5");
        }
        this.riderRating = stars;
        rider.addRating(stars);
    }
    
    public double getEstimatedDistance() {
        return pickup.distanceTo(dropoff);
    }
    
    public Fare getEstimatedFare() {
        double distance = pickup.distanceTo(dropoff);
        int estimatedMinutes = (int)(distance * 3); // ~3 min per km
        return new Fare(distance, estimatedMinutes, requestedType);
    }
    
    @Override
    public String toString() {
        return String.format("Trip[%s] %s -> %s [%s]", id, pickup, dropoff, status);
    }
}

/**
 * Ride sharing service (Singleton).
 */
class RideSharingService {
    private final Map<String, Rider> riders;
    private final Map<String, Driver> drivers;
    private final Map<String, Trip> trips;
    private int riderCounter = 0;
    private int driverCounter = 0;
    private int tripCounter = 0;
    
    private static RideSharingService instance;
    
    private RideSharingService() {
        this.riders = new HashMap<>();
        this.drivers = new HashMap<>();
        this.trips = new HashMap<>();
    }
    
    public static synchronized RideSharingService getInstance() {
        if (instance == null) {
            instance = new RideSharingService();
        }
        return instance;
    }
    
    public static void resetInstance() {
        instance = null;
    }
    
    // Registration
    public Rider registerRider(String name, String phone) {
        String id = "R" + (++riderCounter);
        Rider rider = new Rider(id, name, phone);
        riders.put(id, rider);
        return rider;
    }
    
    public Driver registerDriver(String name, String phone, Vehicle vehicle) {
        String id = "D" + (++driverCounter);
        Driver driver = new Driver(id, name, phone, vehicle);
        drivers.put(id, driver);
        return driver;
    }
    
    // Trip management
    public Trip requestRide(String riderId, Location pickup, Location dropoff, VehicleType type) {
        Rider rider = riders.get(riderId);
        if (rider == null) {
            throw new IllegalArgumentException("Rider not found: " + riderId);
        }
        
        String tripId = "T" + (++tripCounter);
        Trip trip = new Trip(tripId, rider, pickup, dropoff, type);
        trips.put(tripId, trip);
        
        // Try to match driver
        Driver matchedDriver = findNearestDriver(pickup, type);
        if (matchedDriver != null) {
            trip.assignDriver(matchedDriver);
            System.out.printf("Matched with %s (%.1f km away)%n", 
                matchedDriver.getName(),
                matchedDriver.getCurrentLocation().distanceTo(pickup));
        } else {
            System.out.println("No drivers available. Waiting...");
        }
        
        return trip;
    }
    
    private Driver findNearestDriver(Location pickup, VehicleType type) {
        Driver nearest = null;
        double minDistance = Double.MAX_VALUE;
        
        for (Driver driver : drivers.values()) {
            if (!driver.isAvailable()) continue;
            if (driver.getVehicle().getType() != type) continue;
            
            double distance = driver.getCurrentLocation().distanceTo(pickup);
            if (distance < minDistance) {
                minDistance = distance;
                nearest = driver;
            }
        }
        
        return nearest;
    }
    
    public void startTrip(String tripId) {
        Trip trip = trips.get(tripId);
        if (trip == null) {
            throw new IllegalArgumentException("Trip not found: " + tripId);
        }
        trip.start();
        System.out.println("Trip started: " + tripId);
    }
    
    public void completeTrip(String tripId, int durationMinutes) {
        Trip trip = trips.get(tripId);
        if (trip == null) {
            throw new IllegalArgumentException("Trip not found: " + tripId);
        }
        trip.complete(durationMinutes);
        System.out.printf("Trip completed: %s - Fare: %s%n", tripId, trip.getFare());
    }
    
    public void cancelTrip(String tripId) {
        Trip trip = trips.get(tripId);
        if (trip == null) {
            throw new IllegalArgumentException("Trip not found: " + tripId);
        }
        trip.cancel();
        System.out.println("Trip cancelled: " + tripId);
    }
    
    public void rateDriver(String tripId, int stars) {
        Trip trip = trips.get(tripId);
        if (trip == null) {
            throw new IllegalArgumentException("Trip not found: " + tripId);
        }
        trip.rateDriver(stars);
        System.out.printf("Driver rated: %d stars%n", stars);
    }
    
    // Getters
    public Rider getRider(String id) { return riders.get(id); }
    public Driver getDriver(String id) { return drivers.get(id); }
    public Trip getTrip(String id) { return trips.get(id); }
    
    public List<Driver> getAvailableDrivers() {
        return drivers.values().stream()
            .filter(Driver::isAvailable)
            .toList();
    }
    
    public List<Driver> getAvailableDrivers(VehicleType type) {
        return drivers.values().stream()
            .filter(d -> d.isAvailable() && d.getVehicle().getType() == type)
            .toList();
    }
}
