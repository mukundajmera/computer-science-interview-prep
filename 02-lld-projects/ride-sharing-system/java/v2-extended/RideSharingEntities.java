import java.util.*;

/**
 * Ride Sharing System - V2 Extended
 * With strategy patterns for matching and pricing.
 */

// ================ Enums ================

enum VehicleType {
    BIKE(1, 1.0, "Bike"),
    AUTO(3, 1.5, "Auto Rickshaw"),
    CAR(4, 2.0, "Car"),
    PREMIUM(4, 3.0, "Premium Car"),
    SUV(6, 2.5, "SUV");
    
    private final int capacity;
    private final double rateMultiplier;
    private final String displayName;
    
    VehicleType(int capacity, double rateMultiplier, String displayName) {
        this.capacity = capacity;
        this.rateMultiplier = rateMultiplier;
        this.displayName = displayName;
    }
    
    public int getCapacity() { return capacity; }
    public double getRateMultiplier() { return rateMultiplier; }
    public String getDisplayName() { return displayName; }
}

enum DriverStatus { AVAILABLE, BUSY, OFFLINE }
enum TripStatus { REQUESTED, MATCHED, DRIVER_EN_ROUTE, IN_PROGRESS, COMPLETED, CANCELLED }

// ================ Value Objects ================

class Location {
    private final double latitude;
    private final double longitude;
    
    public Location(double latitude, double longitude) {
        this.latitude = latitude;
        this.longitude = longitude;
    }
    
    public double getLatitude() { return latitude; }
    public double getLongitude() { return longitude; }
    
    public double distanceTo(Location other) {
        double latDiff = this.latitude - other.latitude;
        double lonDiff = this.longitude - other.longitude;
        return Math.sqrt(latDiff * latDiff + lonDiff * lonDiff) * 111;
    }
    
    @Override
    public String toString() {
        return String.format("(%.4f, %.4f)", latitude, longitude);
    }
}

// ================ Strategy Interfaces ================

interface MatchingStrategy {
    Driver findDriver(Location pickup, VehicleType type, List<Driver> availableDrivers);
}

interface PricingStrategy {
    Fare calculateFare(double distance, int durationMinutes, VehicleType type);
}

// ================ Matching Strategies ================

class NearestDriverStrategy implements MatchingStrategy {
    @Override
    public Driver findDriver(Location pickup, VehicleType type, List<Driver> drivers) {
        Driver nearest = null;
        double minDistance = Double.MAX_VALUE;
        
        for (Driver driver : drivers) {
            if (driver.getVehicle().getType() != type) continue;
            
            double distance = driver.getCurrentLocation().distanceTo(pickup);
            if (distance < minDistance) {
                minDistance = distance;
                nearest = driver;
            }
        }
        return nearest;
    }
}

class PriorityDriverStrategy implements MatchingStrategy {
    @Override
    public Driver findDriver(Location pickup, VehicleType type, List<Driver> drivers) {
        Driver best = null;
        double bestScore = -1;
        
        for (Driver driver : drivers) {
            if (driver.getVehicle().getType() != type) continue;
            
            double distance = driver.getCurrentLocation().distanceTo(pickup);
            double rating = driver.getRating();
            
            // Score: higher rating, lower distance = better
            double score = (rating * 10) / (distance + 1);
            if (score > bestScore) {
                bestScore = score;
                best = driver;
            }
        }
        return best;
    }
}

// ================ Pricing Strategies ================

class StandardPricing implements PricingStrategy {
    private static final double BASE_FARE = 5.0;
    private static final double PER_KM = 1.0;
    private static final double PER_MIN = 0.15;
    
    @Override
    public Fare calculateFare(double distance, int duration, VehicleType type) {
        double base = BASE_FARE;
        double distCost = distance * PER_KM;
        double timeCost = duration * PER_MIN;
        double total = (base + distCost + timeCost) * type.getRateMultiplier();
        return new Fare(base, distCost, timeCost, 1.0, total, distance, duration);
    }
}

class SurgePricing implements PricingStrategy {
    private final double surgeMultiplier;
    
    public SurgePricing(double surgeMultiplier) {
        this.surgeMultiplier = surgeMultiplier;
    }
    
    @Override
    public Fare calculateFare(double distance, int duration, VehicleType type) {
        double base = 5.0;
        double distCost = distance * 1.0;
        double timeCost = duration * 0.15;
        double subtotal = (base + distCost + timeCost) * type.getRateMultiplier();
        double total = subtotal * surgeMultiplier;
        return new Fare(base, distCost, timeCost, surgeMultiplier, total, distance, duration);
    }
}

// ================ Core Entities ================

class Vehicle {
    private final String id;
    private final VehicleType type;
    private final String licensePlate;
    private final String model;
    private final String color;
    
    public Vehicle(String id, VehicleType type, String licensePlate, String model, String color) {
        this.id = id;
        this.type = type;
        this.licensePlate = licensePlate;
        this.model = model;
        this.color = color;
    }
    
    public String getId() { return id; }
    public VehicleType getType() { return type; }
    public String getLicensePlate() { return licensePlate; }
    public String getModel() { return model; }
    public String getColor() { return color; }
    
    @Override
    public String toString() {
        return String.format("%s %s (%s)", color, model, licensePlate);
    }
}

class Rider {
    private final String id;
    private final String name;
    private final String phone;
    private final String email;
    private Location currentLocation;
    private final List<Trip> tripHistory = new ArrayList<>();
    private double rating = 5.0;
    private int ratingCount = 0;
    
    public Rider(String id, String name, String phone, String email) {
        this.id = id;
        this.name = name;
        this.phone = phone;
        this.email = email;
    }
    
    public String getId() { return id; }
    public String getName() { return name; }
    public Location getCurrentLocation() { return currentLocation; }
    public double getRating() { return rating; }
    
    public void setCurrentLocation(Location loc) { this.currentLocation = loc; }
    public void addTrip(Trip trip) { tripHistory.add(trip); }
    
    public void addRating(int stars) {
        ratingCount++;
        rating = ((rating * (ratingCount - 1)) + stars) / ratingCount;
    }
}

class Driver {
    private final String id;
    private final String name;
    private final String phone;
    private final Vehicle vehicle;
    private Location currentLocation;
    private DriverStatus status = DriverStatus.OFFLINE;
    private double rating = 5.0;
    private int ratingCount = 0;
    private int completedTrips = 0;
    
    public Driver(String id, String name, String phone, Vehicle vehicle) {
        this.id = id;
        this.name = name;
        this.phone = phone;
        this.vehicle = vehicle;
    }
    
    public String getId() { return id; }
    public String getName() { return name; }
    public Vehicle getVehicle() { return vehicle; }
    public Location getCurrentLocation() { return currentLocation; }
    public DriverStatus getStatus() { return status; }
    public double getRating() { return rating; }
    public int getCompletedTrips() { return completedTrips; }
    
    public void updateLocation(Location loc) { this.currentLocation = loc; }
    public void setStatus(DriverStatus s) { this.status = s; }
    public void setAvailable() { this.status = DriverStatus.AVAILABLE; }
    public void setBusy() { this.status = DriverStatus.BUSY; }
    
    public boolean isAvailable() {
        return status == DriverStatus.AVAILABLE && currentLocation != null;
    }
    
    public void addRating(int stars) {
        ratingCount++;
        rating = ((rating * (ratingCount - 1)) + stars) / ratingCount;
    }
    
    public void completeTrip() { completedTrips++; }
    
    @Override
    public String toString() {
        return String.format("%s (%.1f★, %d trips)", name, rating, completedTrips);
    }
}

class Fare {
    private final double baseFare;
    private final double distanceCost;
    private final double timeCost;
    private final double surgeMultiplier;
    private final double total;
    private final double distance;
    private final int duration;
    
    public Fare(double base, double dist, double time, double surge, 
                double total, double distance, int duration) {
        this.baseFare = base;
        this.distanceCost = dist;
        this.timeCost = time;
        this.surgeMultiplier = surge;
        this.total = total;
        this.distance = distance;
        this.duration = duration;
    }
    
    public double getTotal() { return total; }
    
    public void displayBreakdown() {
        System.out.println("=== Fare Breakdown ===");
        System.out.printf("Base fare: $%.2f%n", baseFare);
        System.out.printf("Distance (%.1f km): $%.2f%n", distance, distanceCost);
        System.out.printf("Time (%d min): $%.2f%n", duration, timeCost);
        if (surgeMultiplier > 1.0) {
            System.out.printf("Surge (%.1fx): +$%.2f%n", surgeMultiplier, 
                total - (baseFare + distanceCost + timeCost));
        }
        System.out.printf("Total: $%.2f%n", total);
    }
    
    @Override
    public String toString() { return String.format("$%.2f", total); }
}

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
    private Date matchTime;
    private Date startTime;
    private Date endTime;
    private int driverRating;
    private int riderRating;
    
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
    
    public void assignDriver(Driver d) {
        this.driver = d;
        this.status = TripStatus.MATCHED;
        this.matchTime = new Date();
        d.setBusy();
    }
    
    public void driverEnRoute() {
        this.status = TripStatus.DRIVER_EN_ROUTE;
    }
    
    public void start() {
        this.status = TripStatus.IN_PROGRESS;
        this.startTime = new Date();
    }
    
    public void complete(Fare fare) {
        this.status = TripStatus.COMPLETED;
        this.fare = fare;
        this.endTime = new Date();
        if (driver != null) {
            driver.setAvailable();
            driver.completeTrip();
        }
        rider.addTrip(this);
    }
    
    public void cancel() {
        this.status = TripStatus.CANCELLED;
        if (driver != null) driver.setAvailable();
    }
    
    public void rateDriver(int stars) {
        this.driverRating = stars;
        if (driver != null) driver.addRating(stars);
    }
    
    public void rateRider(int stars) {
        this.riderRating = stars;
        rider.addRating(stars);
    }
    
    public double getEstimatedDistance() {
        return pickup.distanceTo(dropoff);
    }
}

// ================ Service ================

class RideSharingService {
    // Note: V2 uses HashMap for simplicity in single-threaded demo contexts.
    // For production multi-threaded usage, use ConcurrentHashMap (see v3-optimized).
    private final Map<String, Rider> riders = new HashMap<>();
    private final Map<String, Driver> drivers = new HashMap<>();
    private final Map<String, Trip> trips = new HashMap<>();
    private MatchingStrategy matchingStrategy;
    private PricingStrategy pricingStrategy;
    private int riderCounter = 0;
    private int driverCounter = 0;
    private int tripCounter = 0;
    
    public RideSharingService() {
        this.matchingStrategy = new NearestDriverStrategy();
        this.pricingStrategy = new StandardPricing();
    }
    
    public void setMatchingStrategy(MatchingStrategy strategy) {
        this.matchingStrategy = strategy;
    }
    
    public void setPricingStrategy(PricingStrategy strategy) {
        this.pricingStrategy = strategy;
    }
    
    public Rider registerRider(String name, String phone, String email) {
        String id = "R" + (++riderCounter);
        Rider rider = new Rider(id, name, phone, email);
        riders.put(id, rider);
        return rider;
    }
    
    public Driver registerDriver(String name, String phone, Vehicle vehicle) {
        String id = "D" + (++driverCounter);
        Driver driver = new Driver(id, name, phone, vehicle);
        drivers.put(id, driver);
        return driver;
    }
    
    public List<Driver> getAvailableDrivers() {
        return drivers.values().stream()
            .filter(Driver::isAvailable)
            .toList();
    }
    
    public Trip requestRide(Rider rider, Location pickup, Location dropoff, VehicleType type) {
        String id = "T" + (++tripCounter);
        Trip trip = new Trip(id, rider, pickup, dropoff, type);
        trips.put(id, trip);
        
        // Match driver
        List<Driver> available = getAvailableDrivers();
        Driver matched = matchingStrategy.findDriver(pickup, type, available);
        
        if (matched != null) {
            trip.assignDriver(matched);
            double eta = matched.getCurrentLocation().distanceTo(pickup) * 2; // ~2 min/km
            System.out.printf("Driver matched: %s (ETA: %.0f min)%n", matched.getName(), eta);
        } else {
            System.out.println("No drivers available for " + type.getDisplayName());
        }
        
        return trip;
    }
    
    public void startTrip(Trip trip) {
        trip.driverEnRoute();
        trip.start();
    }
    
    public void completeTrip(Trip trip, int durationMinutes) {
        double distance = trip.getEstimatedDistance();
        Fare fare = pricingStrategy.calculateFare(distance, durationMinutes, trip.getRequestedType());
        trip.complete(fare);
    }
    
    public Fare getEstimatedFare(Location pickup, Location dropoff, VehicleType type) {
        double distance = pickup.distanceTo(dropoff);
        int estMinutes = (int)(distance * 3);
        return pricingStrategy.calculateFare(distance, estMinutes, type);
    }
}
