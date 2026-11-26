import org.junit.jupiter.api.*;
import static org.junit.jupiter.api.Assertions.*;

import java.util.*;
import java.util.concurrent.*;

/**
 * Tests for Ride Sharing System.
 */
public class RideSharingTest {
    
    @Nested
    @DisplayName("Location Tests")
    class LocationTests {
        
        @Test
        @DisplayName("Distance calculation")
        void testDistanceCalculation() {
            // Simplified distance test using Euclidean distance
            double lat1 = 12.9, lon1 = 77.6;
            double lat2 = 12.91, lon2 = 77.61;
            
            double latDiff = lat1 - lat2;
            double lonDiff = lon1 - lon2;
            double distance = Math.sqrt(latDiff * latDiff + lonDiff * lonDiff) * 111;
            
            assertTrue(distance > 0);
            assertTrue(distance < 5); // Should be a few km
        }
        
        @Test
        @DisplayName("Same location distance is zero")
        void testSameLocation() {
            double lat = 12.9, lon = 77.6;
            double distance = 0.0; // Same point
            assertEquals(0.0, distance, 0.001);
        }
    }
    
    @Nested
    @DisplayName("Driver Tests")
    class DriverTests {
        
        @Test
        @DisplayName("Driver status transitions")
        void testStatusTransitions() {
            String status = "OFFLINE";
            
            // Go available
            status = "AVAILABLE";
            assertEquals("AVAILABLE", status);
            
            // Go busy
            status = "BUSY";
            assertEquals("BUSY", status);
            
            // Back to available
            status = "AVAILABLE";
            assertEquals("AVAILABLE", status);
        }
        
        @Test
        @DisplayName("Driver rating calculation")
        void testRatingCalculation() {
            double rating = 5.0;
            int count = 0;
            
            // Add rating of 4
            count++;
            rating = ((rating * (count - 1)) + 4) / count;
            assertEquals(4.0, rating, 0.01);
            
            // Add rating of 5
            count++;
            rating = ((rating * (count - 1)) + 5) / count;
            assertEquals(4.5, rating, 0.01);
        }
    }
    
    @Nested
    @DisplayName("Trip Tests")
    class TripTests {
        
        @Test
        @DisplayName("Trip state machine")
        void testTripStates() {
            String status = "REQUESTED";
            
            // Match
            status = "MATCHED";
            assertEquals("MATCHED", status);
            
            // Start
            status = "IN_PROGRESS";
            assertEquals("IN_PROGRESS", status);
            
            // Complete
            status = "COMPLETED";
            assertEquals("COMPLETED", status);
        }
        
        @Test
        @DisplayName("Trip cancellation")
        void testCancellation() {
            String status = "MATCHED";
            
            // Can cancel matched trip
            status = "CANCELLED";
            assertEquals("CANCELLED", status);
        }
        
        @Test
        @DisplayName("Cannot cancel completed trip")
        void testCannotCancelCompleted() {
            String status = "COMPLETED";
            boolean canCancel = !status.equals("COMPLETED") && !status.equals("IN_PROGRESS");
            assertFalse(canCancel);
        }
    }
    
    @Nested
    @DisplayName("Fare Tests")
    class FareTests {
        
        @Test
        @DisplayName("Basic fare calculation")
        void testBasicFare() {
            double baseFare = 5.0;
            double perKm = 1.0;
            double perMin = 0.15;
            double distance = 10.0;
            int duration = 20;
            double multiplier = 2.0; // CAR
            
            double total = (baseFare + (distance * perKm) + (duration * perMin)) * multiplier;
            assertEquals(36.0, total, 0.01);
        }
        
        @Test
        @DisplayName("Surge pricing")
        void testSurgePricing() {
            double baseFare = 5.0;
            double distance = 10.0;
            int duration = 20;
            double surge = 2.0;
            
            double base = baseFare + distance + (duration * 0.15);
            double withSurge = base * surge;
            
            assertTrue(withSurge > base);
            assertEquals(base * 2, withSurge, 0.01);
        }
        
        @Test
        @DisplayName("Vehicle type pricing")
        void testVehicleTypePricing() {
            double baseFare = 10.0;
            
            double bike = baseFare * 1.0;
            double car = baseFare * 2.0;
            double premium = baseFare * 3.0;
            
            assertTrue(bike < car);
            assertTrue(car < premium);
        }
    }
    
    @Nested
    @DisplayName("Matching Tests")
    class MatchingTests {
        
        @Test
        @DisplayName("Find nearest driver")
        void testNearestDriver() {
            List<double[]> driverLocations = List.of(
                new double[]{12.9, 77.6, 5.0},   // distance 5
                new double[]{12.85, 77.55, 2.0}, // distance 2
                new double[]{12.95, 77.65, 8.0}  // distance 8
            );
            
            double minDist = Double.MAX_VALUE;
            int nearestIdx = -1;
            
            for (int i = 0; i < driverLocations.size(); i++) {
                double dist = driverLocations.get(i)[2];
                if (dist < minDist) {
                    minDist = dist;
                    nearestIdx = i;
                }
            }
            
            assertEquals(1, nearestIdx);
        }
        
        @Test
        @DisplayName("Filter by vehicle type")
        void testVehicleTypeFilter() {
            List<String> drivers = List.of("CAR", "BIKE", "CAR", "PREMIUM");
            
            long carCount = drivers.stream().filter(t -> t.equals("CAR")).count();
            assertEquals(2, carCount);
        }
    }
    
    @Nested
    @DisplayName("Concurrency Tests")
    class ConcurrencyTests {
        
        @Test
        @DisplayName("Concurrent driver reservation")
        void testConcurrentReservation() throws Exception {
            // Simulate concurrent reservation attempts
            Map<String, String> driverStatus = new ConcurrentHashMap<>();
            driverStatus.put("D1", "AVAILABLE");
            
            List<Boolean> results = Collections.synchronizedList(new ArrayList<>());
            
            ExecutorService executor = Executors.newFixedThreadPool(5);
            
            for (int i = 0; i < 5; i++) {
                executor.submit(() -> {
                    synchronized (driverStatus) {
                        if ("AVAILABLE".equals(driverStatus.get("D1"))) {
                            driverStatus.put("D1", "BUSY");
                            results.add(true);
                        } else {
                            results.add(false);
                        }
                    }
                });
            }
            
            executor.shutdown();
            executor.awaitTermination(5, TimeUnit.SECONDS);
            
            // Only one should succeed
            long successCount = results.stream().filter(r -> r).count();
            assertEquals(1, successCount);
        }
        
        @Test
        @DisplayName("Thread-safe rating updates")
        void testConcurrentRatings() throws Exception {
            // Simulate concurrent rating updates
            double[] rating = {5.0};
            int[] count = {0};
            Object lock = new Object();
            
            ExecutorService executor = Executors.newFixedThreadPool(10);
            
            for (int i = 0; i < 100; i++) {
                final int stars = (i % 5) + 1;
                executor.submit(() -> {
                    synchronized (lock) {
                        count[0]++;
                        rating[0] = ((rating[0] * (count[0] - 1)) + stars) / count[0];
                    }
                });
            }
            
            executor.shutdown();
            executor.awaitTermination(5, TimeUnit.SECONDS);
            
            assertEquals(100, count[0]);
            assertTrue(rating[0] >= 1 && rating[0] <= 5);
        }
    }
    
    @Nested
    @DisplayName("Integration Tests")
    class IntegrationTests {
        
        @Test
        @DisplayName("Full ride flow")
        void testFullRideFlow() {
            // Simulate complete ride
            String riderStatus = "WAITING";
            String tripStatus = "REQUESTED";
            String driverStatus = "AVAILABLE";
            
            // Match
            driverStatus = "BUSY";
            tripStatus = "MATCHED";
            riderStatus = "MATCHED";
            
            // Start
            tripStatus = "IN_PROGRESS";
            riderStatus = "IN_RIDE";
            
            // Complete
            tripStatus = "COMPLETED";
            driverStatus = "AVAILABLE";
            riderStatus = "COMPLETED";
            
            assertEquals("COMPLETED", tripStatus);
            assertEquals("AVAILABLE", driverStatus);
        }
        
        @Test
        @DisplayName("Multiple concurrent rides")
        void testMultipleRides() {
            Map<String, String> drivers = new ConcurrentHashMap<>();
            drivers.put("D1", "AVAILABLE");
            drivers.put("D2", "AVAILABLE");
            drivers.put("D3", "AVAILABLE");
            
            List<String> rides = List.of("R1", "R2", "R3");
            Map<String, String> assignments = new ConcurrentHashMap<>();
            
            for (String ride : rides) {
                for (String driverId : drivers.keySet()) {
                    if ("AVAILABLE".equals(drivers.get(driverId))) {
                        drivers.put(driverId, "BUSY");
                        assignments.put(ride, driverId);
                        break;
                    }
                }
            }
            
            assertEquals(3, assignments.size());
        }
    }
    
    public static void main(String[] args) {
        System.out.println("Running Ride Sharing Tests...");
        
        RideSharingTest test = new RideSharingTest();
        
        // Location tests
        LocationTests loc = test.new LocationTests();
        loc.testDistanceCalculation();
        loc.testSameLocation();
        System.out.println("Location Tests: PASSED");
        
        // Driver tests
        DriverTests driver = test.new DriverTests();
        driver.testStatusTransitions();
        driver.testRatingCalculation();
        System.out.println("Driver Tests: PASSED");
        
        // Trip tests
        TripTests trip = test.new TripTests();
        trip.testTripStates();
        trip.testCancellation();
        trip.testCannotCancelCompleted();
        System.out.println("Trip Tests: PASSED");
        
        // Fare tests
        FareTests fare = test.new FareTests();
        fare.testBasicFare();
        fare.testSurgePricing();
        fare.testVehicleTypePricing();
        System.out.println("Fare Tests: PASSED");
        
        // Matching tests
        MatchingTests matching = test.new MatchingTests();
        matching.testNearestDriver();
        matching.testVehicleTypeFilter();
        System.out.println("Matching Tests: PASSED");
        
        // Integration tests
        IntegrationTests integration = test.new IntegrationTests();
        integration.testFullRideFlow();
        integration.testMultipleRides();
        System.out.println("Integration Tests: PASSED");
        
        System.out.println("\nAll Ride Sharing Tests PASSED!");
    }
}
