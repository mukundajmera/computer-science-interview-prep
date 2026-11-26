import java.util.List;

public class GoogleMapsService {
    
    private final RoadGraph graph;
    private final RouteOptimizer optimizer;

    public GoogleMapsService(RoadGraph graph) {
        this.graph = graph;
        this.optimizer = new RouteOptimizer(graph);
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
            if (obj == null || getClass() != obj.getClass()) return false;
            TileCoordinate other = (TileCoordinate) obj;
            return x == other.x && y == other.y && z == other.z;
        }

        @Override
        public String toString() {
            return String.format("Tile(x=%d, y=%d, z=%d)", x, y, z);
        }
    }

    public TileCoordinate getSlippyMapTile(double lat, double lng, int zoom) {
        double latRad = Math.toRadians(lat);
        int n = 1 << zoom;
        int xTile = (int) Math.floor((lng + 180.0) / 360.0 * n);
        int yTile = (int) Math.floor((1.0 - Math.log(Math.tan(latRad) + 1.0 / Math.cos(latRad)) / Math.PI) / 2.0 * n);
        
        return new TileCoordinate(xTile, yTile, zoom);
    }

    public RouteOptimizer.RouteResult calculateRoute(String startNodeId, String endNodeId) {
        return optimizer.findShortestPath(startNodeId, endNodeId);
    }

    public RouteOptimizer.RouteResult recalculateRouteOnBlockage(String startNodeId, String endNodeId, String blockedEdgeId) {
        graph.setRoadBlocked(blockedEdgeId, true);
        RouteOptimizer.RouteResult result = calculateRoute(startNodeId, endNodeId);
        graph.setRoadBlocked(blockedEdgeId, false); // Restore if needed, or caller's responsibility. Assuming the blockage is temporary or test-specific.
        return result;
    }
}
