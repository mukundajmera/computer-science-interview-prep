import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

public class V3RideshareMatchingEngineTest {

    @Test
    public void testLocationGeohash() {
        Location loc1 = new Location(15.0, 25.0);
        assertEquals("1,2", loc1.toGeohash());
    }

    @Test
    public void testSpatialIndex() {
        PricingEngine pricing = new PricingEngine();
        MatchingEngine matching = new MatchingEngine(pricing);

        Driver d1 = new Driver("d1", new Location(15.0, 25.0));
        Driver d2 = new Driver("d2", new Location(16.0, 26.0));
        Driver d3 = new Driver("d3", new Location(55.0, 55.0));

        d1.transitionState(DriverState.IDLE);
        d2.transitionState(DriverState.IDLE);
        d3.transitionState(DriverState.IDLE);

        matching.registerDriver(d1);
        matching.registerDriver(d2);
        matching.registerDriver(d3);

        String gh = "1,2";
        assertTrue(matching.getSpatialIndex().getDriversInGeohash(gh).contains("d1"));
        assertTrue(matching.getSpatialIndex().getDriversInGeohash(gh).contains("d2"));
        assertFalse(matching.getSpatialIndex().getDriversInGeohash(gh).contains("d3"));

        matching.updateDriverState("d1", DriverState.OFFLINE);
        assertFalse(matching.getSpatialIndex().getDriversInGeohash(gh).contains("d1"));
    }

    @Test
    public void testFastFindNearest() {
        PricingEngine pricing = new PricingEngine();
        MatchingEngine matching = new MatchingEngine(pricing);

        Driver d1 = new Driver("d1", new Location(12.0, 12.0));
        d1.transitionState(DriverState.IDLE);
        matching.registerDriver(d1);

        Rider r1 = new Rider("r1", new Location(11.0, 11.0));
        assertEquals(1, matching.findNearestDrivers(r1.getLocation(), 5).size());
        assertEquals("d1", matching.findNearestDrivers(r1.getLocation(), 5).get(0).getDriverId());
    }

    @Test
    public void testBatchAuctionMatching() {
        PricingEngine pricing = new PricingEngine();
        MatchingEngine matchingEngine = new MatchingEngine(pricing);

        Driver d1 = new Driver("d1", new Location(1, 1));
        Driver d2 = new Driver("d2", new Location(5, 5));
        d1.transitionState(DriverState.IDLE);
        d2.transitionState(DriverState.IDLE);

        matchingEngine.registerDriver(d1);
        matchingEngine.registerDriver(d2);

        Rider r1 = new Rider("r1", new Location(1, 2));
        Rider r2 = new Rider("r2", new Location(6, 6));

        Trip t1 = matchingEngine.requestRideBatch(r1, new Location(10, 10));
        Trip t2 = matchingEngine.requestRideBatch(r2, new Location(10, 10));

        assertEquals(TripState.REQUESTED, t1.getState());
        assertEquals(2, matchingEngine.getBatchQueue().size());

        matchingEngine.runBatchAuction();

        assertEquals(TripState.ACCEPTED, t1.getState());
        assertEquals(TripState.ACCEPTED, t2.getState());
        assertEquals(0, matchingEngine.getBatchQueue().size());
    }

    @Test
    public void testEdgeCases() {
        PricingEngine pricing = new PricingEngine();
        MatchingEngine matching = new MatchingEngine(pricing);

        // Invalid input
        assertNull(matching.requestRide(null, new Location(0, 0)));

        // Duplicate addition guard is tested implicitly if we can call register again safely
        Driver d1 = new Driver("d1", new Location(1, 1));
        d1.transitionState(DriverState.IDLE);
        matching.registerDriver(d1);
        matching.registerDriver(d1);

        // Capacity boundary / Failure rollback
        Rider r1 = new Rider("r1", new Location(1, 1));
        matching.updateDriverState("d1", DriverState.OFFLINE);
        Trip t1 = matching.requestRide(r1, new Location(5, 5));
        assertNull(t1); // No available drivers, gracefully handles capacity failure
    }
}
