import java.util.*;

/** A* route optimizer over a RoadGraphV2. Mirrors v1's algorithm exactly. */
public class RouteOptimizerV2 {

    private final RoadGraphV2 graph;

    public RouteOptimizerV2(RoadGraphV2 graph) {
        this.graph = graph;
    }

    public static class RouteResult {
        public final List<RoadGraphV2.Node> pathNodes;
        public final List<RoadGraphV2.Edge> pathEdges;
        public final double totalTimeSeconds;
        public final List<String> turnByTurnInstructions;

        public RouteResult(List<RoadGraphV2.Node> pathNodes, List<RoadGraphV2.Edge> pathEdges, double totalTimeSeconds, List<String> turnByTurnInstructions) {
            this.pathNodes = pathNodes;
            this.pathEdges = pathEdges;
            this.totalTimeSeconds = totalTimeSeconds;
            this.turnByTurnInstructions = turnByTurnInstructions;
        }
    }

    private static class SearchNode implements Comparable<SearchNode> {
        String nodeId;
        double gCost;
        double fCost;
        SearchNode parent;
        RoadGraphV2.Edge edgeFromParent;

        public SearchNode(String nodeId, double gCost, double fCost, SearchNode parent, RoadGraphV2.Edge edgeFromParent) {
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
        RoadGraphV2.Node startNode = graph.getNode(startNodeId);
        RoadGraphV2.Node endNode = graph.getNode(endNodeId);

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

            for (RoadGraphV2.Edge edge : graph.getOutgoingEdges(current.nodeId)) {
                if (closedSet.contains(edge.targetId) || edge.isBlocked()) continue;

                double travelTime = edge.getTravelTimeSeconds();
                if (Double.isInfinite(travelTime)) continue;

                double tentativeGCost = current.gCost + travelTime;

                SearchNode neighborNode = allNodes.get(edge.targetId);

                if (neighborNode == null || tentativeGCost < neighborNode.gCost) {
                    RoadGraphV2.Node targetGraphNode = graph.getNode(edge.targetId);
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

    private double heuristic(RoadGraphV2.Node a, RoadGraphV2.Node b) {
        double R = 6371e3;
        double phi1 = a.lat * Math.PI / 180;
        double phi2 = b.lat * Math.PI / 180;
        double deltaPhi = (b.lat - a.lat) * Math.PI / 180;
        double deltaLambda = (b.lng - a.lng) * Math.PI / 180;

        double aVal = Math.sin(deltaPhi / 2) * Math.sin(deltaPhi / 2) +
                Math.cos(phi1) * Math.cos(phi2) *
                        Math.sin(deltaLambda / 2) * Math.sin(deltaLambda / 2);
        double c = 2 * Math.atan2(Math.sqrt(aVal), Math.sqrt(1 - aVal));

        double distance = R * c;
        double optimisticSpeedMps = 120.0 * 1000.0 / 3600.0;
        return distance / optimisticSpeedMps;
    }

    private RouteResult constructPath(SearchNode current) {
        List<RoadGraphV2.Node> pathNodes = new ArrayList<>();
        List<RoadGraphV2.Edge> pathEdges = new ArrayList<>();
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

    private List<String> generateTurnByTurn(List<RoadGraphV2.Edge> pathEdges) {
        List<String> instructions = new ArrayList<>();
        if (pathEdges.isEmpty()) return instructions;

        String currentStreet = pathEdges.get(0).streetName;
        double currentLength = pathEdges.get(0).baseDistanceMeters;

        for (int i = 1; i < pathEdges.size(); i++) {
            RoadGraphV2.Edge edge = pathEdges.get(i);
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
