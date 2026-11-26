package v1_basic;

import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

import java.util.List;

public class RideshareMatchingEngineTest {

    @Test
    public void testDriverFsmLifecycle() {
        Driver driver = new Driver("d1", new Location(0, 0));
        assertEquals(DriverState.OFFLINE, driver.getState());

        assertTrue(driver.transitionState(DriverState.IDLE));
        assertEquals(DriverState.IDLE, driver.getState());

        assertFalse(driver.transitionState(DriverState.IN_TRIP));
        assertEquals(DriverState.IDLE, driver.getState());

        assertTrue(driver.transitionState(DriverState.ASSIGNED));
        assertTrue(driver.transitionState(DriverState.IN_TRIP));
        assertTrue(driver.transitionState(DriverState.IDLE));
        assertTrue(driver.transitionState(DriverState.OFFLINE));
        assertEquals(DriverState.OFFLINE, driver.getState());
    }

    @Test
    public void testDynamicSurgePricing() {
        PricingEngine pricing = new PricingEngine(5.0, 2.0);

        pricing.updateSupplyDemand(10, 1);
        assertEquals(1.0, pricing.calculateSurgeMultiplier());

        pricing.updateSupplyDemand(0, 20); // 10 drivers, 21 requests -> ratio > 2
        assertEquals(2.0, pricing.calculateSurgeMultiplier());

        pricing.updateSupplyDemand(10, 0); // 20 drivers, 21 requests -> ratio > 1, < 2
        assertEquals(1.5, pricing.calculateSurgeMultiplier());
    }

    @Test
    public void testNearestDriverSpatialRanking() {
        PricingEngine pricing = new PricingEngine();
        MatchingEngine engine = new MatchingEngine(pricing, 10.0);

        Driver d1 = new Driver("d1", new Location(10, 10));
        Driver d2 = new Driver("d2", new Location(2, 2));
        Driver d3 = new Driver("d3", new Location(5, 5));
        Driver d4 = new Driver("d4", new Location(20, 20));

        d1.transitionState(DriverState.IDLE);
        d2.transitionState(DriverState.IDLE);
        d3.transitionState(DriverState.IDLE);
        d4.transitionState(DriverState.IDLE);

        engine.registerDriver(d1);
        engine.registerDriver(d2);
        engine.registerDriver(d3);
        engine.registerDriver(d4);

        List<Driver> nearest = engine.findNearestDrivers(new Location(0, 0), 5);

        assertEquals(2, nearest.size());
        assertEquals("d2", nearest.get(0).getDriverId());
        assertEquals("d3", nearest.get(1).getDriverId());
    }

    @Test
    public void testAtomicSingleDriverDispatch() throws InterruptedException {
        PricingEngine pricing = new PricingEngine();
        MatchingEngine engine = new MatchingEngine(pricing);

        Driver driver = new Driver("d1", new Location(0, 0));
        driver.transitionState(DriverState.IDLE);
        engine.registerDriver(driver);

        Rider rider1 = new Rider("r1", new Location(1, 1));
        Rider rider2 = new Rider("r2", new Location(1, 1));

        Trip[] results = new Trip[2];

        Thread t1 = new Thread(() -> {
            results[0] = engine.requestRide(rider1, new Location(5, 5));
        });

        Thread t2 = new Thread(() -> {
            results[1] = engine.requestRide(rider2, new Location(5, 5));
        });

        t1.start();
        t2.start();
        t1.join();
        t2.join();

        int successCount = 0;
        Trip successfulTrip = null;

        for (Trip trip : results) {
            if (trip != null && trip.getState() == TripState.ACCEPTED) {
                successCount++;
                successfulTrip = trip;
            }
        }

        assertEquals(1, successCount);
        assertNotNull(successfulTrip);
        assertEquals("d1", successfulTrip.getDriver().getDriverId());
        assertEquals(DriverState.ASSIGNED, driver.getState());
    }

    @Test
    public void testNoDriverAvailable() {
        PricingEngine pricing = new PricingEngine();
        MatchingEngine engine = new MatchingEngine(pricing);

        Rider rider = new Rider("r1", new Location(1, 1));
        Trip trip = engine.requestRide(rider, new Location(5, 5));
        
        assertNull(trip);
    }

    @Test
    public void testEdgeCases() {
        PricingEngine pricing = new PricingEngine();
        MatchingEngine matching = new MatchingEngine(pricing);

        // Invalid input
        assertNull(matching.requestRide(null, new Location(0, 0)));

        // Duplicate operation
        Driver d1 = new Driver("d1", new Location(1, 1));
        d1.transitionState(DriverState.IDLE);
        matching.registerDriver(d1);
        matching.registerDriver(d1); // should not crash or duplicate supply

        // Capacity boundary & Failure rollback
        Rider r1 = new Rider("r1", new Location(1, 1));
        matching.updateDriverState("d1", DriverState.OFFLINE);
        Trip t1 = matching.requestRide(r1, new Location(5, 5));
        assertNull(t1); // No available drivers, gracefully handles capacity failure
    }

    @Test
    public void testLocationTimestampUpdate() {
        Driver driver = new Driver("d1", new Location(0, 0, 100));
        
        driver.updateLocation(new Location(1, 1, 90));
        assertEquals(0, driver.getLocation().getLat());
        assertEquals(0, driver.getLocation().getLon());

        driver.updateLocation(new Location(2, 2, 110));
        assertEquals(2, driver.getLocation().getLat());
        assertEquals(2, driver.getLocation().getLon());
    }
}
