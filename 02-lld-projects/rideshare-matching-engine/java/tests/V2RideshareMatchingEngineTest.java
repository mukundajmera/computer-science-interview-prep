import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

public class V2RideshareMatchingEngineTest {

    @Test
    public void testBatchAuctionMatching() {
        PricingEngine pricing = new PricingEngine(5.0, 2.0);
        RideshareMatchingEngine matchingEngine = new RideshareMatchingEngine(pricing);

        Driver d1 = new Driver("d1", new Location(1, 1));
        Driver d2 = new Driver("d2", new Location(5, 5));
        d1.transitionState(DriverState.IDLE);
        d2.transitionState(DriverState.IDLE);

        matchingEngine.registerDriver(d1);
        matchingEngine.registerDriver(d2);

        Rider r1 = new Rider("r1", new Location(1, 2));
        Rider r2 = new Rider("r2", new Location(6, 6));

        Trip t1 = matchingEngine.requestRide(r1, new Location(10, 10));
        Trip t2 = matchingEngine.requestRide(r2, new Location(10, 10));

        assertEquals(TripState.REQUESTED, t1.getState());
        assertEquals(TripState.REQUESTED, t2.getState());
        assertEquals(2, matchingEngine.getBatchQueue().size());

        matchingEngine.runBatchAuction();

        assertEquals(TripState.ACCEPTED, t1.getState());
        assertEquals(TripState.ACCEPTED, t2.getState());
        assertEquals("d1", t1.getDriver().getDriverId());
        assertEquals("d2", t2.getDriver().getDriverId());
        assertEquals(0, matchingEngine.getBatchQueue().size());
    }

    @Test
    public void testBatchAuctionUnmatched() {
        PricingEngine pricing = new PricingEngine();
        RideshareMatchingEngine matchingEngine = new RideshareMatchingEngine(pricing);

        Driver d1 = new Driver("d1", new Location(1, 1));
        d1.transitionState(DriverState.IDLE);
        matchingEngine.registerDriver(d1);

        Rider r1 = new Rider("r1", new Location(1, 2));
        Rider r2 = new Rider("r2", new Location(6, 6));

        Trip t1 = matchingEngine.requestRide(r1, new Location(10, 10));
        Trip t2 = matchingEngine.requestRide(r2, new Location(10, 10));

        matchingEngine.runBatchAuction();

        assertEquals(1, matchingEngine.getBatchQueue().size());
        assertTrue((t1.getState() == TripState.ACCEPTED && t2.getState() == TripState.REQUESTED) ||
                   (t2.getState() == TripState.ACCEPTED && t1.getState() == TripState.REQUESTED));
    }
}
