import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.List;
import java.util.Queue;

class Solution {
    public List<Integer> findMinHeightTrees(int n, int[][] edges) {
        List<List<Integer>> graph = buildGraph(n, edges);
        int bestHeight = Integer.MAX_VALUE;
        List<Integer> result = new ArrayList<>();
        for (int root = 0; root < n; root++) {
            int height = height(root, graph);
            if (height < bestHeight) {
                bestHeight = height;
                result.clear();
            }
            if (height == bestHeight) {
                result.add(root);
            }
        }
        return result;
    }

    private List<List<Integer>> buildGraph(int n, int[][] edges) {
        List<List<Integer>> graph = new ArrayList<>();
        for (int i = 0; i < n; i++) {
            graph.add(new ArrayList<>());
        }
        for (int[] edge : edges) {
            graph.get(edge[0]).add(edge[1]);
            graph.get(edge[1]).add(edge[0]);
        }
        return graph;
    }

    private int height(int root, List<List<Integer>> graph) {
        boolean[] seen = new boolean[graph.size()];
        Queue<Integer> queue = new ArrayDeque<>();
        queue.offer(root);
        seen[root] = true;
        int height = -1;
        while (!queue.isEmpty()) {
            int size = queue.size();
            height++;
            for (int i = 0; i < size; i++) {
                int node = queue.poll();
                for (int neighbor : graph.get(node)) {
                    if (!seen[neighbor]) {
                        seen[neighbor] = true;
                        queue.offer(neighbor);
                    }
                }
            }
        }
        return height;
    }
}
