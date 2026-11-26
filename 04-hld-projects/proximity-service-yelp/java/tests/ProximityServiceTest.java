import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

import java.util.List;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

public class ProximityServiceTest {

    private ProximityService service;

    @BeforeEach
    public void setUp() {
        service = new ProximityService();
    }

    @Test
    public void testGeohashEncodeDecodeAccuracy() {
        double lat = 37.7749;
        double lon = -122.4194;
        String geohash = GeohashUtil.encode(lat, lon, 6);
        assertEquals(6, geohash.length());

        double[] coords = GeohashUtil.decode(geohash);
        assertTrue(Math.abs(coords[0] - lat) < 0.01);
        assertTrue(Math.abs(coords[1] - lon) < 0.01);
    }

    @Test
    public void testEightNeighborExpansion() {
        String geohash = GeohashUtil.encode(37.7749, -122.4194, 6);
        List<String> neighbors = GeohashUtil.getNeighbors(geohash);
        assertEquals(8, neighbors.size());
        assertFalse(neighbors.contains(geohash));
        for (String n : neighbors) {
            assertEquals(6, n.length());
        }
    }

    @Test
    public void testNearbySearchFiltersWithinRadius() {
        service.addBusiness(new Business("1", 37.7749, -122.4194));
        service.addBusiness(new Business("2", 37.7839, -122.4194));
        service.addBusiness(new Business("3", 37.8649, -122.4194));

        List<Business> nearby2km = service.getNearbyBusinesses(37.7749, -122.4194, 2.0);
        assertEquals(2, nearby2km.size());

        List<Business> nearby20km = service.getNearbyBusinesses(37.7749, -122.4194, 20.0);
        assertEquals(3, nearby20km.size());
    }

    @Test
    public void testHaversineDistanceSorting() {
        service.addBusiness(new Business("b1", 40.7138, -74.0060)); // Closest
        service.addBusiness(new Business("b2", 40.7158, -74.0060)); // Furthest
        service.addBusiness(new Business("b3", 40.7148, -74.0060)); // Middle

        List<Business> results = service.getNearbyBusinesses(40.7128, -74.0060, 5.0);
        assertEquals(3, results.size());
        assertEquals("b1", results.get(0).getId());
        assertEquals("b3", results.get(1).getId());
        assertEquals("b2", results.get(2).getId());
    }

    @Test
    public void testBusinessUpsertAndRemoval() {
        service.addBusiness(new Business("1", 37.0, -122.0));

        List<Business> results = service.getNearbyBusinesses(37.0, -122.0, 1.0);
        assertEquals(1, results.size());

        service.addBusiness(new Business("1", 38.0, -122.0));
        results = service.getNearbyBusinesses(37.0, -122.0, 1.0);
        assertEquals(0, results.size());

        results = service.getNearbyBusinesses(38.0, -122.0, 1.0);
        assertEquals(1, results.size());

        service.removeBusiness("1");
        results = service.getNearbyBusinesses(38.0, -122.0, 1.0);
        assertEquals(0, results.size());
    }
}