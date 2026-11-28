import java.util.HashSet;
import java.util.Set;

/**
 * v2-extended Google Maps service.
 *
 * Improvements over v1-basic (each has dedicated tests):
 *
 * 1. Offline corridor download (FOLLOW-UPS.md #1): the client preemptively
 *    downloads a generalized subgraph for the planned corridor so it can
 *    reroute locally with no network. downloadOfflineCorridor() computes
 *    the route, then returns a RoadGraphV2 containing the route's nodes
 *    and edges plus their surroundings out to extraHops hops.
 *
 * 2. Telemetry-driven closure detection with a confidence threshold
 *    (FOLLOW-UPS.md #2): implemented in RoadGraphV2; repeated
 *    reroute-avoidance signals close a segment only once the threshold is
 *    met, and a real traversal resets the confidence.
 *
 * 3. Client-side telemetry batching (PITFALLS.md #5): implemented in
 *    TelemetryBatcherV2; pings are collected continuously but sent in one
 *    batched payload per flush interval.
 */
public class GoogleMapsServiceV2 {

    private final RoadGraphV2 graph;
    private final RouteOptimizerV2 optimizer;

    public GoogleMapsServiceV2(RoadGraphV2 graph) {
        this.graph = graph;
        this.optimizer = new RouteOptimizerV2(graph);
    }

    public static class TileCoordinate {
        public final int x;
        public final int y;
        public final int z;

        public TileCoordinate(int x, int y, int z) {
            this.x = x;
            this.y = y;
            this.z = z;
        }

        @Override
        public boolean equals(Object obj) {
            if (this == obj) return true;
            if (!(obj instanceof TileCoordinate)) return false;
            TileCoordinate other = (TileCoordinate) obj;
            return x == other.x && y == other.y && z == other.z;
        }
    }

    public TileCoordinate getSlippyMapTile(double lat, double lng, int zoom) {
        double latRad = Math.toRadians(lat);
        int n = 1 << zoom;
        int xTile = (int) Math.floor((lng + 180.0) / 360.0 * n);
        int yTile = (int) Math.floor((1.0 - Math.log(Math.tan(latRad) + 1.0 / Math.cos(latRad)) / Math.PI) / 2.0 * n);
        return new TileCoordinate(xTile, yTile, zoom);
    }

    public RouteOptimizerV2.RouteResult calculateRoute(String startNodeId, String endNodeId) {
        return optimizer.findShortestPath(startNodeId, endNodeId);
    }

    public RouteOptimizerV2.RouteResult recalculateRouteOnBlockage(String startNodeId, String endNodeId, String blockedEdgeId) {
        graph.setRoadBlocked(blockedEdgeId, true);
        RouteOptimizerV2.RouteResult result = calculateRoute(startNodeId, endNodeId);
        graph.setRoadBlocked(blockedEdgeId, false);
        return result;
    }

    /**
     * Improvement #1 (FOLLOW-UPS.md #1): builds the generalized subgraph a
     * client downloads for offline routing. Contains the planned route's
     * nodes and edges plus everything reachable from the route within
     * extraHops hops, so local rerouting works when the user deviates.
     * Returns null when no route exists.
     */
    public RoadGraphV2 downloadOfflineCorridor(String startNodeId, String endNodeId, int extraHops) {
        if (extraHops < 0) {
            throw new IllegalArgumentException("extraHops can't be negative");
        }
        RouteOptimizerV2.RouteResult route = calculateRoute(startNodeId, endNodeId);
        if (route == null) {
            return null;
        }

        Set<String> includedNodes = new HashSet<>();
        for (RoadGraphV2.Node node : route.pathNodes) {
            includedNodes.add(node.id);
        }
        // The planned route's own edges are always in the corridor, even
        // with extraHops=0.
        Set<String> includedEdges = new HashSet<>();
        for (RoadGraphV2.Edge edge : route.pathEdges) {
            includedEdges.add(edge.id);
        }

        Set<String> frontier = new HashSet<>(includedNodes);
        for (int hop = 0; hop < extraHops; hop++) {
            Set<String> nextFrontier = new HashSet<>();
            for (String nodeId : frontier) {
                for (RoadGraphV2.Edge edge : graph.getOutgoingEdges(nodeId)) {
                    includedEdges.add(edge.id);
                    if (includedNodes.add(edge.targetId)) {
                        nextFrontier.add(edge.targetId);
                    }
                }
            }
            frontier = nextFrontier;
        }

        RoadGraphV2 corridor = new RoadGraphV2(graph.getClosureConfidenceThreshold());
        for (String nodeId : includedNodes) {
            corridor.addNode(graph.getNode(nodeId));
        }
        for (String edgeId : includedEdges) {
            corridor.addEdge(graph.getEdge(edgeId));
        }
        return corridor;
    }
}
