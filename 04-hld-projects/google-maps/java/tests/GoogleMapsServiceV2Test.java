import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

import java.util.List;
import java.util.Set;
import java.util.HashSet;

public class GoogleMapsServiceV2Test {

    private RoadGraphV2 graph;
    private GoogleMapsServiceV2 service;

    @BeforeEach
    public void setup() {
        graph = new RoadGraphV2();
        graph.addNode(new RoadGraphV2.Node("A", 37.7749, -122.4194));
        graph.addNode(new RoadGraphV2.Node("B", 37.7750, -122.4180));
        graph.addNode(new RoadGraphV2.Node("C", 37.7751, -122.4160));
        graph.addNode(new RoadGraphV2.Node("D", 37.7740, -122.4194));
        graph.addNode(new RoadGraphV2.Node("E", 37.7740, -122.4180));
        graph.addNode(new RoadGraphV2.Node("F", 37.7740, -122.4160));

        graph.addEdge(new RoadGraphV2.Edge("e1", "A", "B", 150, 50, "Main St"));
        graph.addEdge(new RoadGraphV2.Edge("e2", "B", "C", 200, 50, "Main St"));
        graph.addEdge(new RoadGraphV2.Edge("e3", "A", "D", 100, 40, "1st Ave"));
        graph.addEdge(new RoadGraphV2.Edge("e4", "B", "E", 100, 40, "2nd Ave"));
        graph.addEdge(new RoadGraphV2.Edge("e5", "C", "F", 100, 40, "3rd Ave"));
        graph.addEdge(new RoadGraphV2.Edge("e6", "D", "E", 150, 50, "South St"));
        graph.addEdge(new RoadGraphV2.Edge("e7", "E", "F", 200, 50, "South St"));

        service = new GoogleMapsServiceV2(graph);
    }

    private String pathString(RouteOptimizerV2.RouteResult result) {
        StringBuilder sb = new StringBuilder();
        for (RoadGraphV2.Node node : result.pathNodes) {
            sb.append(node.id);
        }
        return sb.toString();
    }

    // --- Parity with the v1 test scenarios ---

    @Test
    public void testShortestPathAStarCalculatesOptimalRoute() {
        RouteOptimizerV2.RouteResult result = service.calculateRoute("A", "C");
        assertNotNull(result);
        assertEquals(3, result.pathNodes.size());
        assertEquals("ABC", pathString(result));

        double expectedTime = (150.0 / (50.0 * 1000.0 / 3600.0)) + (200.0 / (50.0 * 1000.0 / 3600.0));
        assertEquals(expectedTime, result.totalTimeSeconds, 0.001);
    }

    @Test
    public void testDynamicTrafficAdjustsRouteAndEta() {
        graph.updateTraffic("e2", 0.1);
        RouteOptimizerV2.RouteResult result = service.calculateRoute("A", "F");
        assertNotNull(result);
        String path = pathString(result);
        assertTrue(path.contains("B"));
        assertTrue(path.contains("E"));
        graph.updateTraffic("e2", 1.0);
    }

    @Test
    public void testTurnByTurnInstructionGeneration() {
        RouteOptimizerV2.RouteResult result = service.calculateRoute("A", "F");
        assertNotNull(result);
        List<String> instructions = result.turnByTurnInstructions;
        assertFalse(instructions.isEmpty());
        assertTrue(instructions.stream().anyMatch(i -> i.contains("Main St") && i.contains("150")));
        assertTrue(instructions.stream().anyMatch(i -> i.contains("2nd Ave") && i.contains("100")));
        assertTrue(instructions.stream().anyMatch(i -> i.contains("destination")));
    }

    @Test
    public void testSlippyMapTileCalculationAtZoomLevels() {
        GoogleMapsServiceV2.TileCoordinate tile0 = service.getSlippyMapTile(37.7749, -122.4194, 0);
        assertEquals(0, tile0.x);
        assertEquals(0, tile0.y);

        double lat = 37.7749, lng = -122.4194;
        int zoom = 10;
        double latRad = Math.toRadians(lat);
        int n = 1 << zoom;
        int expectedX = (int) Math.floor((lng + 180.0) / 360.0 * n);
        int expectedY = (int) Math.floor((1.0 - Math.log(Math.tan(latRad) + 1.0 / Math.cos(latRad)) / Math.PI) / 2.0 * n);

        GoogleMapsServiceV2.TileCoordinate tile10 = service.getSlippyMapTile(lat, lng, zoom);
        assertEquals(expectedX, tile10.x);
        assertEquals(expectedY, tile10.y);
        assertEquals(zoom, tile10.z);
    }

    @Test
    public void testRerouteOnBlockedRoadSegment() {
        graph.addEdge(new RoadGraphV2.Edge("e5_rev", "F", "C", 100, 40, "3rd Ave"));
        graph.addEdge(new RoadGraphV2.Edge("e4_rev", "E", "B", 100, 40, "2nd Ave"));

        RouteOptimizerV2.RouteResult rerouted = service.recalculateRouteOnBlockage("A", "C", "e2");
        assertNotNull(rerouted);
        assertEquals("ABEFC", pathString(rerouted));
    }

    // --- Improvement #2: closure detection with confidence threshold ---

    @Test
    public void testClosureBelowThresholdStaysOpen() {
        graph.recordRerouteAvoidance("e2");
        graph.recordRerouteAvoidance("e2");

        assertTrue(graph.evaluateClosures().isEmpty());
        assertFalse(graph.getEdge("e2").isBlocked());
        assertEquals("ABC", pathString(service.calculateRoute("A", "C")));
    }

    @Test
    public void testClosureAtThresholdBlocksEdge() {
        for (int i = 0; i < 3; i++) {
            graph.recordRerouteAvoidance("e2");
        }

        assertEquals(List.of("e2"), graph.evaluateClosures());
        assertTrue(graph.getEdge("e2").isBlocked());
    }

    @Test
    public void testTraversalResetsClosureConfidence() {
        graph.recordRerouteAvoidance("e2");
        graph.recordRerouteAvoidance("e2");
        graph.recordTraversal("e2"); // someone got through: hypothesis wrong
        graph.recordRerouteAvoidance("e2");
        graph.recordRerouteAvoidance("e2");

        assertEquals(2, graph.avoidanceConfidence("e2"));
        assertTrue(graph.evaluateClosures().isEmpty());
        assertFalse(graph.getEdge("e2").isBlocked());
    }

    // --- Improvement #1: offline corridor download ---

    @Test
    public void testOfflineCorridorContainsRouteAndSurroundings() {
        RoadGraphV2 corridor = service.downloadOfflineCorridor("A", "C", 1);
        assertNotNull(corridor);

        Set<String> nodeIds = new HashSet<>();
        for (String id : new String[]{"A", "B", "C", "D", "E", "F"}) {
            assertNotNull(corridor.getNode(id), "corridor should contain node " + id);
            nodeIds.add(id);
        }
        for (String id : new String[]{"e1", "e2", "e3", "e4", "e5"}) {
            assertNotNull(corridor.getEdge(id), "corridor should contain edge " + id);
        }
        // Edges leaving D/E/F are two hops from the route start: excluded.
        assertNull(corridor.getEdge("e6"));
        assertNull(corridor.getEdge("e7"));
    }

    @Test
    public void testOfflineCorridorSupportsLocalRouting() {
        RoadGraphV2 corridor = service.downloadOfflineCorridor("A", "C", 1);
        RouteOptimizerV2 offlineOptimizer = new RouteOptimizerV2(corridor);
        RouteOptimizerV2.RouteResult result = offlineOptimizer.findShortestPath("A", "C");
        assertNotNull(result);
        assertEquals("ABC", pathString(result));
    }

    @Test
    public void testOfflineCorridorNullWithoutRoute() {
        assertNull(service.downloadOfflineCorridor("A", "UNKNOWN", 1));
    }

    // --- Improvement #3: telemetry batching ---

    @Test
    public void testBatcherBuffersUntilFlushInterval() {
        TelemetryBatcherV2 batcher = new TelemetryBatcherV2(15.0, () -> 0.0);
        for (int t = 0; t < 15; t++) {
            assertNull(batcher.recordPing(37.0, -122.0, t));
        }
        assertEquals(15, batcher.pendingCount());

        List<TelemetryBatcherV2.Ping> batch = batcher.recordPing(37.0, -122.0, 15.0);
        assertNotNull(batch);
        assertEquals(16, batch.size());
        assertEquals(0.0, batch.get(0).timestampSeconds, 0.0001);
        assertEquals(0, batcher.pendingCount());
    }

    @Test
    public void testBatcherKeepsPartialWindowBuffered() {
        TelemetryBatcherV2 batcher = new TelemetryBatcherV2(15.0, () -> 0.0);
        for (int t = 0; t < 6; t++) {
            assertNull(batcher.recordPing(37.0, -122.0, t));
        }
        assertEquals(6, batcher.pendingCount());
        assertEquals(6, batcher.flush(6.0).size());
        assertEquals(0, batcher.pendingCount());
    }

    @Test
    public void testBatcherWindowRestartsAfterFlush() {
        TelemetryBatcherV2 batcher = new TelemetryBatcherV2(15.0, () -> 0.0);
        assertNotNull(batcher.recordPing(37.0, -122.0, 15.0));
        assertNull(batcher.recordPing(38.0, -123.0, 16.0));
        assertEquals(1, batcher.pendingCount());
    }
}
