/**
 * Ride Sharing System - V2 Extended Demo
 */
public class RideSharingDemo {
    
    public static void main(String[] args) {
        System.out.println("=".repeat(60));
        System.out.println("Ride Sharing System - V2 Extended Demo");
        System.out.println("=".repeat(60));
        
        RideSharingService service = new RideSharingService();
        
        // Register riders
        System.out.println("\n1. Registering users...");
        Rider alice = service.registerRider("Alice", "555-0101", "alice@email.com");
        Rider bob = service.registerRider("Bob", "555-0102", "bob@email.com");
        
        // Register drivers with detailed vehicles
        Vehicle car1 = new Vehicle("V1", VehicleType.CAR, "ABC-1234", "Toyota Camry", "White");
        Vehicle premium1 = new Vehicle("V2", VehicleType.PREMIUM, "LUX-5678", "BMW 5 Series", "Black");
        Vehicle bike1 = new Vehicle("V3", VehicleType.BIKE, "BIKE-001", "Honda Activa", "Red");
        
        Driver john = service.registerDriver("John", "555-0201", car1);
        Driver mike = service.registerDriver("Mike", "555-0202", premium1);
        Driver sam = service.registerDriver("Sam", "555-0203", bike1);
        
        // Set locations and availability
        john.updateLocation(new Location(12.9, 77.6));
        john.setAvailable();
        
        mike.updateLocation(new Location(12.85, 77.58));
        mike.setAvailable();
        
        sam.updateLocation(new Location(12.88, 77.55));
        sam.setAvailable();
        
        System.out.println("   Drivers ready:");
        for (Driver d : service.getAvailableDrivers()) {
            System.out.println("   - " + d + " with " + d.getVehicle());
        }
        
        // Test different matching strategies
        System.out.println("\n2. Using Nearest Driver Strategy (default)...");
        Location pickup = new Location(12.87, 77.57);
        Location dropoff = new Location(12.95, 77.65);
        
        Trip trip1 = service.requestRide(alice, pickup, dropoff, VehicleType.CAR);
        System.out.println("   Matched: " + trip1.getDriver().getName());
        
        // Complete trip
        service.startTrip(trip1);
        service.completeTrip(trip1, 20);
        trip1.getFare().displayBreakdown();
        trip1.rateDriver(5);
        
        // Switch to Priority Strategy
        System.out.println("\n3. Using Priority Driver Strategy...");
        service.setMatchingStrategy(new PriorityDriverStrategy());
        
        Trip trip2 = service.requestRide(bob, pickup, dropoff, VehicleType.CAR);
        System.out.println("   Matched: " + trip2.getDriver().getName() + 
            " (rating: " + trip2.getDriver().getRating() + ")");
        
        service.startTrip(trip2);
        service.completeTrip(trip2, 18);
        trip2.rateDriver(4);
        
        // Test surge pricing
        System.out.println("\n4. Testing Surge Pricing (2x)...");
        service.setPricingStrategy(new SurgePricing(2.0));
        
        Fare surgeFare = service.getEstimatedFare(pickup, dropoff, VehicleType.CAR);
        System.out.println("   Estimated fare with 2x surge:");
        surgeFare.displayBreakdown();
        
        // Test premium vehicle
        System.out.println("\n5. Requesting Premium ride...");
        service.setPricingStrategy(new StandardPricing());
        
        Trip trip3 = service.requestRide(alice, pickup, dropoff, VehicleType.PREMIUM);
        if (trip3.getDriver() != null) {
            System.out.println("   Premium vehicle: " + trip3.getDriver().getVehicle());
            service.startTrip(trip3);
            service.completeTrip(trip3, 25);
            trip3.getFare().displayBreakdown();
        }
        
        // Show driver stats
        System.out.println("\n6. Driver Statistics:");
        for (Driver d : service.getAvailableDrivers()) {
            System.out.printf("   %s - Rating: %.1f, Trips: %d%n",
                d.getName(), d.getRating(), d.getCompletedTrips());
        }
        
        System.out.println("\n" + "=".repeat(60));
        System.out.println("Demo completed!");
        System.out.println("=".repeat(60));
    }
}
