/**
 * Ride Sharing System - V1 Basic Demo
 */
public class RideSharingDemo {
    
    public static void main(String[] args) {
        System.out.println("=".repeat(60));
        System.out.println("Ride Sharing System - V1 Basic Demo");
        System.out.println("=".repeat(60));
        
        // Reset for clean demo
        RideSharingService.resetInstance();
        RideSharingService service = RideSharingService.getInstance();
        
        // Register riders
        System.out.println("\n1. Registering riders...");
        Rider alice = service.registerRider("Alice", "555-0101");
        Rider bob = service.registerRider("Bob", "555-0102");
        System.out.println("   Registered: " + alice);
        System.out.println("   Registered: " + bob);
        
        // Register drivers with vehicles
        System.out.println("\n2. Registering drivers...");
        Vehicle car1 = new Vehicle("V1", VehicleType.CAR, "ABC-1234");
        Vehicle car2 = new Vehicle("V2", VehicleType.CAR, "XYZ-5678");
        Vehicle bike1 = new Vehicle("V3", VehicleType.BIKE, "BIKE-001");
        
        Driver john = service.registerDriver("John", "555-0201", car1);
        Driver mike = service.registerDriver("Mike", "555-0202", car2);
        Driver sam = service.registerDriver("Sam", "555-0203", bike1);
        
        // Set driver locations and availability
        john.updateLocation(new Location(12.9, 77.6));
        john.setAvailable();
        
        mike.updateLocation(new Location(12.8, 77.5));
        mike.setAvailable();
        
        sam.updateLocation(new Location(12.85, 77.55));
        sam.setAvailable();
        
        System.out.println("   Registered: " + john + " at " + john.getCurrentLocation());
        System.out.println("   Registered: " + mike + " at " + mike.getCurrentLocation());
        System.out.println("   Registered: " + sam + " at " + sam.getCurrentLocation());
        
        // Show available drivers
        System.out.println("\n3. Available drivers:");
        for (Driver d : service.getAvailableDrivers()) {
            System.out.println("   - " + d);
        }
        
        // Alice requests a ride
        System.out.println("\n4. Alice requests a CAR ride...");
        alice.setCurrentLocation(new Location(12.85, 77.55));
        Location pickup1 = new Location(12.85, 77.55);
        Location dropoff1 = new Location(12.95, 77.65);
        
        Trip trip1 = service.requestRide(alice.getId(), pickup1, dropoff1, VehicleType.CAR);
        System.out.println("   Trip created: " + trip1);
        System.out.println("   Estimated fare: " + trip1.getEstimatedFare());
        
        // Start trip
        System.out.println("\n5. Starting trip...");
        service.startTrip(trip1.getId());
        System.out.println("   Trip status: " + trip1.getStatus());
        
        // Complete trip
        System.out.println("\n6. Completing trip (15 minutes)...");
        service.completeTrip(trip1.getId(), 15);
        trip1.getFare().display();
        
        // Rate driver
        System.out.println("\n7. Alice rates driver...");
        service.rateDriver(trip1.getId(), 5);
        System.out.printf("   Driver %s rating: %.1f%n", 
            trip1.getDriver().getName(), 
            trip1.getDriver().getRating());
        
        // Bob requests a BIKE ride
        System.out.println("\n8. Bob requests a BIKE ride...");
        bob.setCurrentLocation(new Location(12.82, 77.52));
        Location pickup2 = new Location(12.82, 77.52);
        Location dropoff2 = new Location(12.88, 77.58);
        
        Trip trip2 = service.requestRide(bob.getId(), pickup2, dropoff2, VehicleType.BIKE);
        System.out.println("   Trip: " + trip2);
        
        // Start and complete
        service.startTrip(trip2.getId());
        service.completeTrip(trip2.getId(), 10);
        service.rateDriver(trip2.getId(), 4);
        
        // Show trip history
        System.out.println("\n9. Trip history:");
        System.out.println("   Alice's trips: " + alice.getTripHistory().size());
        System.out.println("   Bob's trips: " + bob.getTripHistory().size());
        
        // Try to cancel in-progress trip (should fail)
        System.out.println("\n10. Testing cancellation...");
        try {
            service.cancelTrip(trip1.getId());
        } catch (IllegalStateException e) {
            System.out.println("    Cannot cancel completed trip (expected)");
        }
        
        // New ride and cancel before start
        Trip trip3 = service.requestRide(alice.getId(), pickup1, dropoff1, VehicleType.CAR);
        service.cancelTrip(trip3.getId());
        System.out.println("    Cancelled pending trip: " + trip3.getStatus());
        
        System.out.println("\n" + "=".repeat(60));
        System.out.println("Demo completed!");
        System.out.println("=".repeat(60));
    }
}
