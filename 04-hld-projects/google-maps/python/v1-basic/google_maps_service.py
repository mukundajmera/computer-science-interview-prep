import math
import heapq
from typing import List, Tuple, Dict, Optional
from road_graph import RoadGraph, Node, Edge

class RouteResult:
    def __init__(self, path_nodes: List[Node], path_edges: List[Edge], total_time_seconds: float, turn_by_turn_instructions: List[str]):
        self.path_nodes = path_nodes
        self.path_edges = path_edges
        self.total_time_seconds = total_time_seconds
        self.turn_by_turn_instructions = turn_by_turn_instructions

class RouteOptimizer:
    def __init__(self, graph: RoadGraph):
        self.graph = graph

    class SearchNode:
        def __init__(self, node_id: str, g_cost: float, f_cost: float, parent: Optional['RouteOptimizer.SearchNode'], edge_from_parent: Optional[Edge]):
            self.node_id = node_id
            self.g_cost = g_cost
            self.f_cost = f_cost
            self.parent = parent
            self.edge_from_parent = edge_from_parent

        def __lt__(self, other):
            return self.f_cost < other.f_cost

    def find_shortest_path(self, start_node_id: str, end_node_id: str) -> Optional[RouteResult]:
        start_node = self.graph.get_node(start_node_id)
        end_node = self.graph.get_node(end_node_id)

        if not start_node or not end_node:
            return None

        open_set = []
        all_nodes = {}

        start_search_node = self.SearchNode(start_node_id, 0.0, self._heuristic(start_node, end_node), None, None)
        heapq.heappush(open_set, start_search_node)
        all_nodes[start_node_id] = start_search_node

        closed_set = set()

        while open_set:
            current = heapq.heappop(open_set)

            if current.node_id == end_node_id:
                return self._construct_path(current)

            closed_set.add(current.node_id)

            for edge in self.graph.get_outgoing_edges(current.node_id):
                if edge.target_id in closed_set or edge.is_blocked:
                    continue

                travel_time = edge.get_travel_time_seconds()
                if math.isinf(travel_time):
                    continue

                tentative_g_cost = current.g_cost + travel_time

                neighbor_node = all_nodes.get(edge.target_id)

                if neighbor_node is None or tentative_g_cost < neighbor_node.g_cost:
                    target_graph_node = self.graph.get_node(edge.target_id)
                    f_cost = tentative_g_cost + self._heuristic(target_graph_node, end_node)
                    new_neighbor_node = self.SearchNode(edge.target_id, tentative_g_cost, f_cost, current, edge)
                    
                    # We can't easily remove from heapq, so we just push the new one.
                    # It will be popped before the old one because f_cost is smaller.
                    # The closed_set check will ignore the old one when it is popped.
                    heapq.heappush(open_set, new_neighbor_node)
                    all_nodes[edge.target_id] = new_neighbor_node

        return None

    def _heuristic(self, a: Node, b: Node) -> float:
        R = 6371e3
        phi1 = math.radians(a.lat)
        phi2 = math.radians(b.lat)
        delta_phi = math.radians(b.lat - a.lat)
        delta_lambda = math.radians(b.lng - a.lng)

        a_val = math.sin(delta_phi / 2.0)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0)**2
        c = 2 * math.atan2(math.sqrt(a_val), math.sqrt(1 - a_val))

        distance = R * c
        optimistic_speed_mps = 120.0 * 1000.0 / 3600.0
        return distance / optimistic_speed_mps

    def _construct_path(self, current: SearchNode) -> RouteResult:
        path_nodes = []
        path_edges = []
        total_time = current.g_cost

        node = current
        while node:
            path_nodes.append(self.graph.get_node(node.node_id))
            if node.edge_from_parent:
                path_edges.append(node.edge_from_parent)
            node = node.parent

        path_nodes.reverse()
        path_edges.reverse()

        return RouteResult(path_nodes, path_edges, total_time, self._generate_turn_by_turn(path_edges))

    def _generate_turn_by_turn(self, path_edges: List[Edge]) -> List[str]:
        instructions = []
        if not path_edges:
            return instructions

        current_street = path_edges[0].street_name
        current_length = path_edges[0].base_distance_meters

        for edge in path_edges[1:]:
            if edge.street_name == current_street:
                current_length += edge.base_distance_meters
            else:
                instructions.append(f"Continue on {current_street} for {int(current_length)} meters")
                instructions.append(f"Turn onto {edge.street_name}")
                current_street = edge.street_name
                current_length = edge.base_distance_meters

        instructions.append(f"Continue on {current_street} for {int(current_length)} meters")
        instructions.append("You have reached your destination")

        return instructions


class TileCoordinate:
    def __init__(self, x: int, y: int, z: int):
        self.x = x
        self.y = y
        self.z = z

    def __eq__(self, other):
        if not isinstance(other, TileCoordinate):
            return False
        return self.x == other.x and self.y == other.y and self.z == other.z

    def __repr__(self):
        return f"Tile(x={self.x}, y={self.y}, z={self.z})"


class GoogleMapsService:
    def __init__(self, graph: RoadGraph):
        self.graph = graph
        self.optimizer = RouteOptimizer(graph)

    def get_slippy_map_tile(self, lat: float, lng: float, zoom: int) -> TileCoordinate:
        lat_rad = math.radians(lat)
        n = 1 << zoom
        x_tile = int((lng + 180.0) / 360.0 * n)
        y_tile = int((1.0 - math.log(math.tan(lat_rad) + (1 / math.cos(lat_rad))) / math.pi) / 2.0 * n)
        return TileCoordinate(x_tile, y_tile, zoom)

    def calculate_route(self, start_node_id: str, end_node_id: str) -> Optional[RouteResult]:
        return self.optimizer.find_shortest_path(start_node_id, end_node_id)

    def recalculate_route_on_blockage(self, start_node_id: str, end_node_id: str, blocked_edge_id: str) -> Optional[RouteResult]:
        self.graph.set_road_blocked(blocked_edge_id, True)
        result = self.calculate_route(start_node_id, end_node_id)
        self.graph.set_road_blocked(blocked_edge_id, False)
        return result
