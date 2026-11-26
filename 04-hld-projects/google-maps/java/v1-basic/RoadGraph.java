import java.util.*;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.CopyOnWriteArrayList;

public class RoadGraph {

    public static class Node {
        public final String id;
        public final double lat;
        public final double lng;

        public Node(String id, double lat, double lng) {
            this.id = id;
            this.lat = lat;
            this.lng = lng;
        }
    }

    public static class Edge {
        public final String id;
        public final String sourceId;
        public final String targetId;
        public final double baseDistanceMeters;
        public final double baseSpeedLimitKmph;
        public final String streetName;
        private volatile double trafficMultiplier = 1.0; 
        private volatile boolean isBlocked = false;

        public Edge(String id, String sourceId, String targetId, double baseDistanceMeters, double baseSpeedLimitKmph, String streetName) {
            this.id = id;
            this.sourceId = sourceId;
            this.targetId = targetId;
            this.baseDistanceMeters = baseDistanceMeters;
            this.baseSpeedLimitKmph = baseSpeedLimitKmph;
            this.streetName = streetName;
        }

        public void setTrafficMultiplier(double multiplier) {
            this.trafficMultiplier = multiplier;
        }

        public void setBlocked(boolean blocked) {
            this.isBlocked = blocked;
        }

        public boolean isBlocked() {
            return this.isBlocked;
        }

        public double getTravelTimeSeconds() {
            if (isBlocked) {
                return Double.POSITIVE_INFINITY;
            }
            double speedMps = (baseSpeedLimitKmph * 1000.0 / 3600.0) * trafficMultiplier;
            if (speedMps <= 0) return Double.POSITIVE_INFINITY;
            return baseDistanceMeters / speedMps;
        }
    }

    private final Map<String, Node> nodes = new ConcurrentHashMap<>();
    private final Map<String, List<Edge>> adjacencyList = new ConcurrentHashMap<>();
    private final Map<String, Edge> edges = new ConcurrentHashMap<>();

    public void addNode(Node node) {
        nodes.put(node.id, node);
        adjacencyList.putIfAbsent(node.id, new CopyOnWriteArrayList<>());
    }

    public void addEdge(Edge edge) {
        edges.put(edge.id, edge);
        adjacencyList.computeIfAbsent(edge.sourceId, k -> new CopyOnWriteArrayList<>()).add(edge);
    }

    public Node getNode(String id) {
        return nodes.get(id);
    }

    public Edge getEdge(String id) {
        return edges.get(id);
    }

    public List<Edge> getOutgoingEdges(String nodeId) {
        return adjacencyList.getOrDefault(nodeId, Collections.emptyList());
    }

    public void updateTraffic(String edgeId, double multiplier) {
        Edge edge = edges.get(edgeId);
        if (edge != null) {
            edge.setTrafficMultiplier(multiplier);
        }
    }

    public void setRoadBlocked(String edgeId, boolean blocked) {
        Edge edge = edges.get(edgeId);
        if (edge != null) {
            edge.setBlocked(blocked);
        }
    }
}
