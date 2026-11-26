import java.util.ArrayList;
import java.util.List;

class Solution {
    public int countComponents(int n, int[][] edges) {
        List<List<Integer>> graph = new ArrayList<>();
        for (int i = 0; i < n; i++) {
            graph.add(new ArrayList<>());
        }
        for (int[] edge : edges) {
            graph.get(edge[0]).add(edge[1]);
            graph.get(edge[1]).add(edge[0]);
        }
        boolean[] visited = new boolean[n];
        int components = 0;
        for (int node = 0; node < n; node++) {
            if (!visited[node]) {
                components++;
                dfs(node, graph, visited);
            }
        }
        return components;
    }

    private void dfs(int node, List<List<Integer>> graph, boolean[] visited) {
        if (visited[node]) {
            return;
        }
        visited[node] = true;
        for (int neighbor : graph.get(node)) {
            dfs(neighbor, graph, visited);
        }
    }
}
