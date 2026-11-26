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
        queue = deque([source])
        seen_stops = {source}
        boarded = set()
        buses = 0
        while queue:
            buses += 1
            for _ in range(len(queue)):
                stop = queue.popleft()
                for route in stop_to_routes[stop]:
                    if route in boarded:
                        continue
                    boarded.add(route)
                    for next_stop in routes[route]:
                        if next_stop == target:
                            return buses
                        if next_stop not in seen_stops:
                            seen_stops.add(next_stop)
                            queue.append(next_stop)
        return -1
