from collections import defaultdict, deque
from typing import List


class Solution:
    def numBusesToDestination(self, routes: List[List[int]], source: int, target: int) -> int:
        if source == target:
            return 0
        stop_to_routes = defaultdict(list)
        for route, stops in enumerate(routes):
            for stop in stops:
                stop_to_routes[stop].append(route)
        target_routes = set(stop_to_routes.get(target, []))
        queue = deque((route, 1) for route in stop_to_routes.get(source, []))
        seen_routes = {route for route, _ in queue}
        while queue:
            route, buses = queue.popleft()
            if route in target_routes:
                return buses
            for stop in routes[route]:
                for next_route in stop_to_routes[stop]:
                    if next_route not in seen_routes:
                        seen_routes.add(next_route)
                        queue.append((next_route, buses + 1))
        return -1
