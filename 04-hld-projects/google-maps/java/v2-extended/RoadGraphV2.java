import java.util.*;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.CopyOnWriteArrayList;

/**
 * v2 RoadGraph: telemetry-driven closure detection (v2 improvement #2).
 *
 * Implements FOLLOW-UPS.md #2: when users continuously reroute away from a
 * segment, the stream processor accumulates confidence and only marks the
 * segment closed once a threshold is met. Here the graph itself tracks
 * reroute-avoidance signals per edge; a genuine traversal resets the
 * confidence, and evaluateClosures() flips edges at or over the threshold.
 * See GoogleMapsServiceV2 for the full v2 improvement list.
 */
public class RoadGraphV2 {

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
    private final Map<String, Integer> avoidanceCounts = new ConcurrentHashMap<>();
    private final int closureConfidenceThreshold;

    public RoadGraphV2() {
        this(3);
    }

    public RoadGraphV2(int closureConfidenceThreshold) {
        if (closureConfidenceThreshold < 1) {
            throw new IllegalArgumentException("closure confidence threshold must be at least 1");
        }
        this.closureConfidenceThreshold = closureConfidenceThreshold;
    }

    public int getClosureConfidenceThreshold() {
        return closureConfidenceThreshold;
    }

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

    // --- Improvement #2: closure confidence from telemetry ---

    /**
     * A user rerouted away from this segment. Returns the segment's
     * accumulated avoidance confidence.
     */
    public int recordRerouteAvoidance(String edgeId) {
        if (!edges.containsKey(edgeId)) {
            throw new IllegalArgumentException("Edge " + edgeId + " not found");
        }
        return avoidanceCounts.merge(edgeId, 1, Integer::sum);
    }

    /**
     * A user successfully traversed this segment, so the closure hypothesis
     * is wrong: reset its avoidance confidence.
     */
    public void recordTraversal(String edgeId) {
        if (!edges.containsKey(edgeId)) {
            throw new IllegalArgumentException("Edge " + edgeId + " not found");
        }
        avoidanceCounts.put(edgeId, 0);
    }

    public int avoidanceConfidence(String edgeId) {
        return avoidanceCounts.getOrDefault(edgeId, 0);
    }

    /**
     * Marks every edge at or over the confidence threshold as blocked and
     * returns the newly closed edge ids. Edges below the threshold stay
     * open: a single detour never closes a road.
     */
    public List<String> evaluateClosures() {
        List<String> newlyClosed = new ArrayList<>();
        for (Map.Entry<String, Integer> entry : avoidanceCounts.entrySet()) {
            Edge edge = edges.get(entry.getKey());
            if (edge != null && entry.getValue() >= closureConfidenceThreshold && !edge.isBlocked()) {
                edge.setBlocked(true);
                newlyClosed.add(entry.getKey());
            }
        }
        return newlyClosed;
    }
}
