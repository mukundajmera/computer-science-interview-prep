import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Queue;
import java.util.Set;

class Solution {
    public int numBusesToDestination(int[][] routes, int source, int target) {
        if (source == target) {
            return 0;
        }
        Map<Integer, List<Integer>> stopToRoutes = new HashMap<>();
        for (int route = 0; route < routes.length; route++) {
            for (int stop : routes[route]) {
                stopToRoutes.computeIfAbsent(stop, ignored -> new ArrayList<>()).add(route);
            }
        }
        Queue<int[]> queue = new ArrayDeque<>();
        Set<Integer> seenRoutes = new HashSet<>();
        for (int route : stopToRoutes.getOrDefault(source, new ArrayList<>())) {
            queue.add(new int[] {route, 1});
            seenRoutes.add(route);
        }
        Set<Integer> targetRoutes = new HashSet<>(stopToRoutes.getOrDefault(target, new ArrayList<>()));
        while (!queue.isEmpty()) {
            int[] state = queue.remove();
            int route = state[0];
            int buses = state[1];
            if (targetRoutes.contains(route)) {
                return buses;
            }
            for (int stop : routes[route]) {
                for (int nextRoute : stopToRoutes.getOrDefault(stop, new ArrayList<>())) {
                    if (seenRoutes.add(nextRoute)) {
                        queue.add(new int[] {nextRoute, buses + 1});
                    }
                }
            }
        }
        return -1;
    }
}
