
import java.util.*;

public class Solutions {
    public boolean canFinish(int numCourses, int[][] prerequisites) {
        int[] indegree = new int[numCourses];
        List<List<Integer>> adj = new ArrayList<>();
        for (int i = 0; i < numCourses; i++) adj.add(new ArrayList<>());
        
        for (int[] pre : prerequisites) {
            adj.get(pre[1]).add(pre[0]);
            indegree[pre[0]]++;
        }
        
        Queue<Integer> q = new LinkedList<>();
        for (int i = 0; i < numCourses; i++) {
            if (indegree[i] == 0) q.offer(i);
        }
        
        int count = 0;
        while (!q.isEmpty()) {
            int curr = q.poll();
            count++;
            for (int nxt : adj.get(curr)) {
                indegree[nxt]--;
                if (indegree[nxt] == 0) q.offer(nxt);
            }
        }
        return count == numCourses;
    }

    public int[] findOrder(int numCourses, int[][] prerequisites) {
        int[] indegree = new int[numCourses];
        List<List<Integer>> adj = new ArrayList<>();
        for (int i = 0; i < numCourses; i++) adj.add(new ArrayList<>());
        
        for (int[] pre : prerequisites) {
            adj.get(pre[1]).add(pre[0]);
            indegree[pre[0]]++;
        }
        
        Queue<Integer> q = new LinkedList<>();
        for (int i = 0; i < numCourses; i++) {
            if (indegree[i] == 0) q.offer(i);
        }
        
        int[] order = new int[numCourses];
        int count = 0;
        while (!q.isEmpty()) {
            int curr = q.poll();
            order[count++] = curr;
            for (int nxt : adj.get(curr)) {
                indegree[nxt]--;
                if (indegree[nxt] == 0) q.offer(nxt);
            }
        }
        return count == numCourses ? order : new int[0];
    }

    public boolean validTree(int n, int[][] edges) {
        if (edges.length != n - 1) return false;
        List<List<Integer>> adj = new ArrayList<>();
        for (int i = 0; i < n; i++) adj.add(new ArrayList<>());
        for (int[] edge : edges) {
            adj.get(edge[0]).add(edge[1]);
            adj.get(edge[1]).add(edge[0]);
        }
        
        Set<Integer> visited = new HashSet<>();
        Queue<Integer> q = new LinkedList<>();
        q.offer(0);
        visited.add(0);
        
        while (!q.isEmpty()) {
            int curr = q.poll();
            for (int nxt : adj.get(curr)) {
                if (!visited.contains(nxt)) {
                    visited.add(nxt);
                    q.offer(nxt);
                }
            }
        }
        return visited.size() == n;
    }

    public String alienOrder(String[] words) {
        Map<Character, List<Character>> adj = new HashMap<>();
        Map<Character, Integer> counts = new HashMap<>();
        for (String w : words) {
            for (char c : w.toCharArray()) {
                counts.put(c, 0);
                adj.put(c, new ArrayList<>());
            }
        }
        
        for (int i = 0; i < words.length - 1; i++) {
            String w1 = words[i];
            String w2 = words[i + 1];
            if (w1.length() > w2.length() && w1.startsWith(w2)) {
                return "";
            }
            for (int j = 0; j < Math.min(w1.length(), w2.length()); j++) {
                if (w1.charAt(j) != w2.charAt(j)) {
                    adj.get(w1.charAt(j)).add(w2.charAt(j));
                    counts.put(w2.charAt(j), counts.get(w2.charAt(j)) + 1);
                    break;
                }
            }
        }
        
        Queue<Character> q = new LinkedList<>();
        for (char c : counts.keySet()) {
            if (counts.get(c) == 0) q.offer(c);
        }
        
        StringBuilder sb = new StringBuilder();
        while (!q.isEmpty()) {
            char c = q.poll();
            sb.append(c);
            for (char next : adj.get(c)) {
                counts.put(next, counts.get(next) - 1);
                if (counts.get(next) == 0) {
                    q.offer(next);
                }
            }
        }
        
        return sb.length() == counts.size() ? sb.toString() : "";
    }

    public int networkDelayTime(int[][] times, int n, int k) {
        Map<Integer, List<int[]>> adj = new HashMap<>();
        for (int[] t : times) {
            adj.putIfAbsent(t[0], new ArrayList<>());
            adj.get(t[0]).add(new int[]{t[1], t[2]});
        }
        
        PriorityQueue<int[]> pq = new PriorityQueue<>((a, b) -> a[0] - b[0]);
        pq.offer(new int[]{0, k});
        Set<Integer> visited = new HashSet<>();
        int res = 0;
        
        while (!pq.isEmpty()) {
            int[] curr = pq.poll();
            int w1 = curr[0], n1 = curr[1];
            if (visited.contains(n1)) continue;
            visited.add(n1);
            res = Math.max(res, w1);
            
            if (adj.containsKey(n1)) {
                for (int[] edge : adj.get(n1)) {
                    int n2 = edge[0], w2 = edge[1];
                    if (!visited.contains(n2)) {
                        pq.offer(new int[]{w1 + w2, n2});
                    }
                }
            }
        }
        return visited.size() == n ? res : -1;
    }

    public int findCheapestPrice(int n, int[][] flights, int src, int dst, int k) {
        int[] prices = new int[n];
        Arrays.fill(prices, Integer.MAX_VALUE);
        prices[src] = 0;
        
        for (int i = 0; i <= k; i++) {
            int[] tmpPrices = Arrays.copyOf(prices, n);
            for (int[] flight : flights) {
                int s = flight[0], d = flight[1], p = flight[2];
                if (prices[s] != Integer.MAX_VALUE && prices[s] + p < tmpPrices[d]) {
                    tmpPrices[d] = prices[s] + p;
                }
            }
            prices = tmpPrices;
        }
        return prices[dst] == Integer.MAX_VALUE ? -1 : prices[dst];
    }

    public int minCostConnectPoints(int[][] points) {
        int n = points.length;
        PriorityQueue<int[]> pq = new PriorityQueue<>((a, b) -> a[0] - b[0]);
        pq.offer(new int[]{0, 0});
        Set<Integer> visited = new HashSet<>();
        int cost = 0;
        
        while (visited.size() < n) {
            int[] curr = pq.poll();
            int w = curr[0], i = curr[1];
            if (visited.contains(i)) continue;
            visited.add(i);
            cost += w;
            
            for (int j = 0; j < n; j++) {
                if (!visited.contains(j)) {
                    int dist = Math.abs(points[i][0] - points[j][0]) + Math.abs(points[i][1] - points[j][1]);
                    pq.offer(new int[]{dist, j});
                }
            }
        }
        return cost;
    }
}
