import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

import java.util.List;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.junit.jupiter.api.Assertions.assertThrows;

public class ProximityServiceV2Test {

    private ProximityServiceV2 service;

    @BeforeEach
    public void setUp() {
        service = new ProximityServiceV2();
    }

    @Test
    public void testGeohashEncodeDecodeAccuracy() {
        double lat = 37.7749;
        double lon = -122.4194;
        String geohash = GeohashUtilV2.encode(lat, lon, 6);
        assertEquals(6, geohash.length());

        double[] coords = GeohashUtilV2.decode(geohash);
        assertTrue(Math.abs(coords[0] - lat) < 0.01);
        assertTrue(Math.abs(coords[1] - lon) < 0.01);
    }

    @Test
    public void testEightNeighborExpansion() {
        String geohash = GeohashUtilV2.encode(37.7749, -122.4194, 6);
        List<String> neighbors = GeohashUtilV2.getNeighbors(geohash);
        assertEquals(8, neighbors.size());
        assertFalse(neighbors.contains(geohash));
        for (String n : neighbors) {
            assertEquals(6, n.length());
        }
    }

    @Test
    public void testNearbySearchFiltersWithinRadius() {
        service.addBusiness(new BusinessV2("1", 37.7749, -122.4194));
        service.addBusiness(new BusinessV2("2", 37.7839, -122.4194));
        service.addBusiness(new BusinessV2("3", 37.8649, -122.4194));

        List<BusinessV2> nearby2km = service.getNearbyBusinesses(37.7749, -122.4194, 2.0);
        assertEquals(2, nearby2km.size());

        List<BusinessV2> nearby20km = service.getNearbyBusinesses(37.7749, -122.4194, 20.0);
        assertEquals(3, nearby20km.size());
    }

    @Test
    public void testHaversineDistanceSorting() {
        service.addBusiness(new BusinessV2("b1", 40.7138, -74.0060)); // Closest
        service.addBusiness(new BusinessV2("b2", 40.7158, -74.0060)); // Furthest
        service.addBusiness(new BusinessV2("b3", 40.7148, -74.0060)); // Middle

        List<BusinessV2> results = service.getNearbyBusinesses(40.7128, -74.0060, 5.0);
        assertEquals(3, results.size());
        assertEquals("b1", results.get(0).getId());
        assertEquals("b3", results.get(1).getId());
        assertEquals("b2", results.get(2).getId());
    }

    @Test
    public void testBusinessUpsertAndRemoval() {
        service.addBusiness(new BusinessV2("1", 37.0, -122.0));

        List<BusinessV2> results = service.getNearbyBusinesses(37.0, -122.0, 1.0);
        assertEquals(1, results.size());

        service.addBusiness(new BusinessV2("1", 38.0, -122.0));
        results = service.getNearbyBusinesses(37.0, -122.0, 1.0);
        assertEquals(0, results.size());

        results = service.getNearbyBusinesses(38.0, -122.0, 1.0);
        assertEquals(1, results.size());

        service.removeBusiness("1");
        results = service.getNearbyBusinesses(38.0, -122.0, 1.0);
        assertEquals(0, results.size());
    }
    // ------------------------------------------------------------------
    // v2-only tests: one or more per improvement.
    // ------------------------------------------------------------------

    private ProximityServiceV2 denseService() {
        ProximityServiceV2 service = new ProximityServiceV2();
        for (int i = 1; i <= 6; i++) {
            service.addBusiness(new BusinessV2("b" + i, 37.7749 + i * 0.001, -122.4194));
        }
        return service;
    }

    // Improvement #1: dense-area pagination (FOLLOW-UPS.md #3).

    @Test
    public void testPaginationPagesInDistanceOrder() {
        ProximityServiceV2 service = denseService();

        ProximityServiceV2.SearchPage page1 = service.searchNearby(37.7749, -122.4194, 2.0, null, null, null, 2, 1);
        assertEquals(6, page1.total);
        assertEquals("b1", page1.businesses.get(0).getId());
        assertEquals("b2", page1.businesses.get(1).getId());

        ProximityServiceV2.SearchPage page2 = service.searchNearby(37.7749, -122.4194, 2.0, null, null, null, 2, 2);
        assertEquals("b3", page2.businesses.get(0).getId());
        assertEquals("b4", page2.businesses.get(1).getId());

        ProximityServiceV2.SearchPage page3 = service.searchNearby(37.7749, -122.4194, 2.0, null, null, null, 2, 3);
        assertEquals("b5", page3.businesses.get(0).getId());
        assertEquals("b6", page3.businesses.get(1).getId());
    }

    @Test
    public void testPaginationBeyondEndAndValidation() {
        ProximityServiceV2 service = denseService();

        ProximityServiceV2.SearchPage beyond = service.searchNearby(37.7749, -122.4194, 2.0, null, null, null, 2, 4);
        assertTrue(beyond.businesses.isEmpty());
        assertEquals(6, beyond.total, "total counts all matches, not the page");

        assertThrows(IllegalArgumentException.class,
                () -> service.searchNearby(37.7749, -122.4194, 2.0, null, null, null, 0, 1));
        assertThrows(IllegalArgumentException.class,
                () -> service.searchNearby(37.7749, -122.4194, 2.0, null, null, null, 2, 0));
    }

    // Improvement #2: attribute filtering (FOLLOW-UPS.md #4).

    @Test
    public void testFilterByCategory() {
        ProximityServiceV2 service = new ProximityServiceV2();
        service.addBusiness(new BusinessV2("r1", 37.7759, -122.4194, "restaurant", 4.0, true));
        service.addBusiness(new BusinessV2("c1", 37.7769, -122.4194, "cafe", 4.0, true));

        ProximityServiceV2.SearchPage result = service.searchNearby(37.7749, -122.4194, 2.0, "cafe", null, null, null, 1);
        assertEquals(1, result.total);
        assertEquals("c1", result.businesses.get(0).getId());
    }

    @Test
    public void testFilterByMinRatingAndOpenNow() {
        ProximityServiceV2 service = new ProximityServiceV2();
        service.addBusiness(new BusinessV2("low", 37.7759, -122.4194, "restaurant", 3.5, true));
        service.addBusiness(new BusinessV2("high-closed", 37.7769, -122.4194, "restaurant", 4.8, false));
        service.addBusiness(new BusinessV2("high-open", 37.7779, -122.4194, "restaurant", 4.5, true));

        ProximityServiceV2.SearchPage result = service.searchNearby(37.7749, -122.4194, 2.0, null, 4.0, true, null, 1);
        assertEquals(1, result.total);
        assertEquals("high-open", result.businesses.get(0).getId());

        ProximityServiceV2.SearchPage allRated = service.searchNearby(37.7749, -122.4194, 2.0, null, 4.0, null, null, 1);
        assertEquals(2, allRated.total);
        assertEquals("high-closed", allRated.businesses.get(0).getId());
        assertEquals("high-open", allRated.businesses.get(1).getId());
    }

    // Improvement #3: geohash-prefix sharding with observability
    // (FOLLOW-UPS.md #1).

    @Test
    public void testShardedQueryTouchesOnlyRelevantShards() {
        ProximityServiceV2 service = new ProximityServiceV2();
        service.addBusiness(new BusinessV2("sf1", 37.7749, -122.4194));
        service.addBusiness(new BusinessV2("nyc1", 40.7128, -74.0060));

        assertEquals(2, service.shardCount(), "businesses land in different shards");

        service.getNearbyBusinesses(37.7749, -122.4194, 2.0);
        assertEquals(1, service.getLastQueryShardsTouched(), "SF query scans only the SF shard");
        assertEquals(1, service.getQueriesRun());
    }

    @Test
    public void testShardedIndexFindsSameResultsAsFullScan() {
        ProximityServiceV2 service = new ProximityServiceV2();
        double[][] points = {
            {37.7749, -122.4194}, {37.7849, -122.4094},
            {37.7649, -122.4294}, {38.7749, -122.4194},
        };
        String[] ids = {"a", "b", "c", "d"};
        for (int i = 0; i < ids.length; i++) {
            service.addBusiness(new BusinessV2(ids[i], points[i][0], points[i][1]));
        }

        List<BusinessV2> found = service.getNearbyBusinesses(37.7749, -122.4194, 3.0);

        // Independent full scan without the shard structure.
        List<String> expected = new java.util.ArrayList<>();
        for (int i = 0; i < ids.length; i++) {
            double dist = GeohashUtilV2.haversineDistance(37.7749, -122.4194, points[i][0], points[i][1]);
            if (dist <= 3.0) {
                expected.add(ids[i]);
            }
        }
        expected.sort((x, y) -> Double.compare(
                GeohashUtilV2.haversineDistance(37.7749, -122.4194, points[indexOf(ids, x)][0], points[indexOf(ids, x)][1]),
                GeohashUtilV2.haversineDistance(37.7749, -122.4194, points[indexOf(ids, y)][0], points[indexOf(ids, y)][1])));

        List<String> foundIds = new java.util.ArrayList<>();
        for (BusinessV2 b : found) {
            foundIds.add(b.getId());
        }
        assertEquals(expected, foundIds);
    }

    private static int indexOf(String[] ids, String id) {
        for (int i = 0; i < ids.length; i++) {
            if (ids[i].equals(id)) {
                return i;
            }
        }
        return -1;
    }

    @Test
    public void testRemovalCleansEmptyShard() {
        ProximityServiceV2 service = new ProximityServiceV2();
        service.addBusiness(new BusinessV2("only", 37.7749, -122.4194));
        assertEquals(1, service.shardCount());

        service.removeBusiness("only");
        assertEquals(0, service.shardCount(), "empty shards are reclaimed");
    }
}
