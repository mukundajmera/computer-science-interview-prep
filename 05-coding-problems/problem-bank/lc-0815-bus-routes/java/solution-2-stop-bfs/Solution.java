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
        Queue<Integer> queue = new ArrayDeque<>();
        queue.add(source);
        Set<Integer> seenStops = new HashSet<>();
        seenStops.add(source);
        Set<Integer> boarded = new HashSet<>();
        int buses = 0;
        while (!queue.isEmpty()) {
            buses++;
            for (int size = queue.size(); size > 0; size--) {
                int stop = queue.remove();
                for (int route : stopToRoutes.getOrDefault(stop, new ArrayList<>())) {
                    if (!boarded.add(route)) {
                        continue;
                    }
                    for (int nextStop : routes[route]) {
                        if (nextStop == target) {
                            return buses;
                        }
                        if (seenStops.add(nextStop)) {
                            queue.add(nextStop);
                        }
                    }
                }
            }
        }
        return -1;
    }
}
