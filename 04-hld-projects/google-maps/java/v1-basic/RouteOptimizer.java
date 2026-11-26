import java.util.*;

public class RouteOptimizer {
    
    private final RoadGraph graph;

    public RouteOptimizer(RoadGraph graph) {
        this.graph = graph;
    }

    public static class RouteResult {
        public final List<RoadGraph.Node> pathNodes;
        public final List<RoadGraph.Edge> pathEdges;
        public final double totalTimeSeconds;
        public final List<String> turnByTurnInstructions;

        public RouteResult(List<RoadGraph.Node> pathNodes, List<RoadGraph.Edge> pathEdges, double totalTimeSeconds, List<String> turnByTurnInstructions) {
            this.pathNodes = pathNodes;
            this.pathEdges = pathEdges;
            this.totalTimeSeconds = totalTimeSeconds;
            this.turnByTurnInstructions = turnByTurnInstructions;
        }
    }

    private static class SearchNode implements Comparable<SearchNode> {
        final String nodeId;
        final double gCost; // Cost from start
        final double fCost; // gCost + hCost
        final SearchNode parent;
        final RoadGraph.Edge edgeFromParent;

        public SearchNode(String nodeId, double gCost, double fCost, SearchNode parent, RoadGraph.Edge edgeFromParent) {
            this.nodeId = nodeId;
            this.gCost = gCost;
            this.fCost = fCost;
            this.parent = parent;
            this.edgeFromParent = edgeFromParent;
        }

        @Override
        public int compareTo(SearchNode other) {
            return Double.compare(this.fCost, other.fCost);
        }
    }

    public RouteResult findShortestPath(String startNodeId, String endNodeId) {
        RoadGraph.Node startNode = graph.getNode(startNodeId);
        RoadGraph.Node endNode = graph.getNode(endNodeId);

        if (startNode == null || endNode == null) {
            return null;
        }

        PriorityQueue<SearchNode> openSet = new PriorityQueue<>();
        Map<String, SearchNode> allNodes = new HashMap<>();

        SearchNode start = new SearchNode(startNodeId, 0, heuristic(startNode, endNode), null, null);
        openSet.add(start);
        allNodes.put(startNodeId, start);

        Set<String> closedSet = new HashSet<>();

        while (!openSet.isEmpty()) {
            SearchNode current = openSet.poll();

            if (current.nodeId.equals(endNodeId)) {
                return constructPath(current);
            }

            closedSet.add(current.nodeId);

            for (RoadGraph.Edge edge : graph.getOutgoingEdges(current.nodeId)) {
                if (closedSet.contains(edge.targetId) || edge.isBlocked()) continue;

                double travelTime = edge.getTravelTimeSeconds();
                if (Double.isInfinite(travelTime)) continue;

                double tentativeGCost = current.gCost + travelTime;

                SearchNode neighborNode = allNodes.get(edge.targetId);

                if (neighborNode == null || tentativeGCost < neighborNode.gCost) {
                    RoadGraph.Node targetGraphNode = graph.getNode(edge.targetId);
                    double fCost = tentativeGCost + heuristic(targetGraphNode, endNode);
                    SearchNode newNeighborNode = new SearchNode(edge.targetId, tentativeGCost, fCost, current, edge);
                    
                    if (neighborNode != null) {
                        openSet.remove(neighborNode);
                    }
                    openSet.add(newNeighborNode);
                    allNodes.put(edge.targetId, newNeighborNode);
                }
            }
        }

        return null;
    }

    private double heuristic(RoadGraph.Node a, RoadGraph.Node b) {
        // Haversine formula to get straight line distance in meters, then convert to time by an optimistic speed
        double R = 6371e3; // metres
        double phi1 = a.lat * Math.PI / 180; // φ, λ in radians
        double phi2 = b.lat * Math.PI / 180;
        double deltaPhi = (b.lat - a.lat) * Math.PI / 180;
        double deltaLambda = (b.lng - a.lng) * Math.PI / 180;

        double aVal = Math.sin(deltaPhi / 2) * Math.sin(deltaPhi / 2) +
                Math.cos(phi1) * Math.cos(phi2) *
                        Math.sin(deltaLambda / 2) * Math.sin(deltaLambda / 2);
        double c = 2 * Math.atan2(Math.sqrt(aVal), Math.sqrt(1 - aVal));

        double distance = R * c; // in metres

        double optimisticSpeedMps = 120.0 * 1000.0 / 3600.0; // Assume max 120km/h
        return distance / optimisticSpeedMps; // heuristic cost in seconds
    }

    private RouteResult constructPath(SearchNode current) {
        List<RoadGraph.Node> pathNodes = new ArrayList<>();
        List<RoadGraph.Edge> pathEdges = new ArrayList<>();
        double totalTime = current.gCost;

        SearchNode node = current;
        while (node != null) {
            pathNodes.add(graph.getNode(node.nodeId));
            if (node.edgeFromParent != null) {
                pathEdges.add(node.edgeFromParent);
            }
            node = node.parent;
        }

        Collections.reverse(pathNodes);
        Collections.reverse(pathEdges);

        return new RouteResult(pathNodes, pathEdges, totalTime, generateTurnByTurn(pathEdges));
    }

    private List<String> generateTurnByTurn(List<RoadGraph.Edge> pathEdges) {
        List<String> instructions = new ArrayList<>();
        if (pathEdges.isEmpty()) return instructions;

        String currentStreet = pathEdges.get(0).streetName;
        double currentLength = pathEdges.get(0).baseDistanceMeters;

        for (int i = 1; i < pathEdges.size(); i++) {
            RoadGraph.Edge edge = pathEdges.get(i);
            if (edge.streetName.equals(currentStreet)) {
                currentLength += edge.baseDistanceMeters;
            } else {
                instructions.add(String.format("Continue on %s for %.0f meters", currentStreet, currentLength));
                instructions.add(String.format("Turn onto %s", edge.streetName));
                currentStreet = edge.streetName;
                currentLength = edge.baseDistanceMeters;
            }
        }
        instructions.add(String.format("Continue on %s for %.0f meters", currentStreet, currentLength));
        instructions.add("You have reached your destination");

        return instructions;
    }
}
