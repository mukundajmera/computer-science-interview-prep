import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.PriorityQueue;

class Solution {
    public int findCheapestPrice(int n, int[][] flights, int src, int dst, int k) {
        List<int[]>[] graph = new ArrayList[n];
        for (int i = 0; i < n; i++) {
            graph[i] = new ArrayList<>();
        }
        for (int[] flight : flights) {
            graph[flight[0]].add(new int[] {flight[1], flight[2]});
        }

        int maxEdges = k + 1;
        int[][] best = new int[n][maxEdges + 1];
        for (int[] row : best) {
            Arrays.fill(row, Integer.MAX_VALUE);
        }
        PriorityQueue<int[]> heap = new PriorityQueue<>((a, b) -> Integer.compare(a[0], b[0]));
        heap.add(new int[] {0, src, 0});
        best[src][0] = 0;
        while (!heap.isEmpty()) {
            int[] state = heap.remove();
            int cost = state[0];
            int city = state[1];
            int edges = state[2];
            if (city == dst) {
                return cost;
            }
            if (edges == maxEdges || cost != best[city][edges]) {
                continue;
            }
            for (int[] edge : graph[city]) {
                int nextCity = edge[0];
                int nextCost = cost + edge[1];
                int nextEdges = edges + 1;
                if (nextCost < best[nextCity][nextEdges]) {
                    best[nextCity][nextEdges] = nextCost;
                    heap.add(new int[] {nextCost, nextCity, nextEdges});
                }
            }
        }
        return -1;
    }
}
