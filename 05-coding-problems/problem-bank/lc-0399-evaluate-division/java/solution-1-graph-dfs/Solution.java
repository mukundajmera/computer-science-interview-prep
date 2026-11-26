import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;

class Solution {
    public double[] calcEquation(List<List<String>> equations, double[] values, List<List<String>> queries) {
        Map<String, List<Edge>> graph = new HashMap<>();
        for (int i = 0; i < equations.size(); i++) {
            String left = equations.get(i).get(0);
            String right = equations.get(i).get(1);
            double ratio = values[i];
            graph.computeIfAbsent(left, unused -> new ArrayList<>()).add(new Edge(right, ratio));
            graph.computeIfAbsent(right, unused -> new ArrayList<>()).add(new Edge(left, 1.0d / ratio));
        }

        double[] answers = new double[queries.size()];
        for (int i = 0; i < queries.size(); i++) {
            String start = queries.get(i).get(0);
            String end = queries.get(i).get(1);
            if (!graph.containsKey(start) || !graph.containsKey(end)) {
                answers[i] = -1.0d;
            } else {
                answers[i] = search(graph, start, end, new HashSet<>(), 1.0d);
            }
        }
        return answers;
    }

    private double search(Map<String, List<Edge>> graph, String node, String target, Set<String> seen, double product) {
        if (node.equals(target)) {
            return product;
        }
        seen.add(node);
        for (Edge edge : graph.getOrDefault(node, List.of())) {
            if (seen.contains(edge.to)) {
                continue;
            }
            double result = search(graph, edge.to, target, seen, product * edge.ratio);
            if (result != -1.0d) {
                return result;
            }
        }
        return -1.0d;
    }

    private static class Edge {
        private final String to;
        private final double ratio;

        private Edge(String to, double ratio) {
            this.to = to;
            this.ratio = ratio;
        }
    }
}
