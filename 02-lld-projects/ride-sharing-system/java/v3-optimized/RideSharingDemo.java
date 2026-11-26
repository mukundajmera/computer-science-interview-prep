import java.util.*;

/**
 * Ride Sharing System - V3 Optimized Demo
 * Demonstrates:
 * 1. Thread-safe driver/rider registration & dispatch.
 * 2. Driver filter pipeline (minimum rating filtering).
 * 3. Geospatial dynamic surge pricing calculation.
 * 4. Shared ride pooling (UberPool route matching & discounted split fares).
 */
public class RideSharingDemo {
    
    public static void main(String[] args) {
        System.out.println("=".repeat(60));
        System.out.println("Ride Sharing System - V3 Optimized Demo");
        System.out.println("=".repeat(60));
        
        RideSharingService service = new RideSharingService();
        
        // 1. Register users
        System.out.println("\n1. Registering riders and drivers...");
        Rider alice = service.registerRider("Alice", "555-0101", "alice@email.com");
        Rider bob = service.registerRider("Bob", "555-0102", "bob@email.com");
        Rider charlie = service.registerRider("Charlie", "555-0103", "charlie@email.com");
        
        Vehicle car1 = new Vehicle("V1", VehicleType.CAR, "ABC-1234", "Toyota Camry", "White");
        Vehicle car2 = new Vehicle("V2", VehicleType.CAR, "XYZ-9876", "Hyundai Elantra", "Silver");
        Vehicle premium1 = new Vehicle("V3", VehicleType.PREMIUM, "LUX-5678", "BMW 5 Series", "Black");
        
        Driver john = service.registerDriver("John", "555-0201", car1);   // Will have 4.9★
        Driver dave = service.registerDriver("Dave", "555-0202", car2);   // Will have 4.2★
        Driver mike = service.registerDriver("Mike", "555-0203", premium1);
        
        // Set ratings
        john.addRating(5);
        john.addRating(5);
        dave.addRating(4);
        dave.addRating(4);
        mike.addRating(5);
        
        // Set driver positions
        john.updateLocation(new Location(12.900, 77.600));
        john.setAvailable();
        dave.updateLocation(new Location(12.890, 77.595)); // Closer to pickup than John
        dave.setAvailable();
        mike.updateLocation(new Location(12.850, 77.580));
        mike.setAvailable();
        
        System.out.println("   Registered Drivers:");
        for (Driver d : service.getAvailableDrivers()) {
            System.out.println("   - " + d + " with " + d.getVehicle());
        }
        
        // 2. Driver Rating Filter Pipeline Test
        System.out.println("\n2. Requesting Ride with Minimum Rating Filter (>= 4.8★)...");
        Location pickup1 = new Location(12.885, 77.590);
        Location dropoff1 = new Location(12.960, 77.650);
        
        List<DriverFilter> filters = List.of(new MinRatingDriverFilter(4.8));
        Trip trip1 = service.requestRide(alice, pickup1, dropoff1, VehicleType.CAR, filters);
        
        if (trip1.getDriver() != null) {
            System.out.println("   Assigned Driver: " + trip1.getDriver().getName() + 
                " (Rating: " + trip1.getDriver().getRating() + "★) - Dave was skipped due to 4.2★ rating");
            service.startTrip(trip1);
            service.completeTrip(trip1, 22);
            trip1.getFare().displayBreakdown();
        }
        
        // 3. Geospatial Dynamic Surge Pricing Test
        System.out.println("\n3. Testing Geospatial Dynamic Surge Pricing (Zone: 15 requests, 3 drivers)...");
        GeospatialDynamicSurgePricing dynamicSurge = new GeospatialDynamicSurgePricing(15, 3);
        service.setPricingStrategy(dynamicSurge);
        
        double multiplier = dynamicSurge.computeMultiplier();
        System.out.printf("   Calculated Zone Surge Multiplier: %.1fx%n", multiplier);
        Fare surgeFare = service.getEstimatedFare(pickup1, dropoff1, VehicleType.CAR);
        surgeFare.displayBreakdown();
        
        // Reset to standard pricing
        service.setPricingStrategy(new StandardPricing());
        
        // 4. Shared Ride Pooling (UberPool) Corridor Matching Test
        System.out.println("\n4. Testing UberPool Route Matching & Shared Pooling Fares...");
        john.updateLocation(new Location(12.870, 77.570));
        john.setAvailable();
        
        Location p1 = new Location(12.880, 77.580);
        Location d1 = new Location(12.950, 77.650);
        Location p2 = new Location(12.890, 77.590); // Along same corridor
        Location d2 = new Location(12.960, 77.660);
        
        List<Trip> pooledTrips = service.requestPooledRide(bob, p1, d1, charlie, p2, d2, VehicleType.CAR);
        if (pooledTrips.size() == 2) {
            Trip tBob = pooledTrips.get(0);
            Trip tCharlie = pooledTrips.get(1);
            
            System.out.println("\n   Completing Bob's pooled trip...");
            service.startTrip(tBob);
            service.completeTrip(tBob, 20);
            tBob.getFare().displayBreakdown();
            
            System.out.println("\n   Completing Charlie's pooled trip...");
            service.startTrip(tCharlie);
            service.completeTrip(tCharlie, 25);
            tCharlie.getFare().displayBreakdown();
        }
        
        System.out.println("\n" + "=".repeat(60));
        System.out.println("Ride Sharing V3 Optimized Demo Completed Successfully!");
        System.out.println("=".repeat(60));
    }
}
