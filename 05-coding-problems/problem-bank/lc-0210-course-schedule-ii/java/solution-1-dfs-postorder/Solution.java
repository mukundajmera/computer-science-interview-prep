import java.util.ArrayList;
import java.util.Collections;
import java.util.List;

class Solution {
    public int[] findOrder(int numCourses, int[][] prerequisites) {
        List<List<Integer>> graph = new ArrayList<>();
        for (int i = 0; i < numCourses; i++) {
            graph.add(new ArrayList<>());
        }
        for (int[] edge : prerequisites) {
            graph.get(edge[1]).add(edge[0]);
        }
        int[] state = new int[numCourses];
        List<Integer> order = new ArrayList<>();
        for (int course = 0; course < numCourses; course++) {
            if (!dfs(course, graph, state, order)) {
                return new int[0];
            }
        }
        Collections.reverse(order);
        int[] result = new int[order.size()];
        for (int i = 0; i < order.size(); i++) {
            result[i] = order.get(i);
        }
        return result;
    }

    private boolean dfs(int course, List<List<Integer>> graph, int[] state, List<Integer> order) {
        if (state[course] == 1) {
            return false;
        }
        if (state[course] == 2) {
            return true;
        }
        state[course] = 1;
        for (int next : graph.get(course)) {
            if (!dfs(next, graph, state, order)) {
                return false;
            }
        }
        state[course] = 2;
        order.add(course);
        return true;
    }
}
