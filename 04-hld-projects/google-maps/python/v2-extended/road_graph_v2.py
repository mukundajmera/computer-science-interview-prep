"""v2 RoadGraph: telemetry-driven closure detection (v2 improvement #2).

Implements FOLLOW-UPS.md #2: when users continuously reroute away from a
segment, the stream processor accumulates confidence and only marks the
segment closed once a threshold is met. Here the graph itself tracks
reroute-avoidance signals per edge; a genuine traversal resets the
confidence, and evaluate_closures() flips edges at or over the threshold.
See google_maps_service_v2.py for the full v2 improvement list.
"""
from threading import RLock


class Node:
    def __init__(self, node_id: str, lat: float, lng: float):
        self.id = node_id
        self.lat = lat
        self.lng = lng


class Edge:
    def __init__(self, edge_id: str, source_id: str, target_id: str, base_distance_meters: float, base_speed_limit_kmph: float, street_name: str):
        self.id = edge_id
        self.source_id = source_id
        self.target_id = target_id
        self.base_distance_meters = base_distance_meters
        self.base_speed_limit_kmph = base_speed_limit_kmph
        self.street_name = street_name
        self._traffic_multiplier = 1.0
        self._is_blocked = False
        self._lock = RLock()

    @property
    def traffic_multiplier(self) -> float:
        with self._lock:
            return self._traffic_multiplier

    @traffic_multiplier.setter
    def traffic_multiplier(self, value: float):
        with self._lock:
            self._traffic_multiplier = value

    @property
    def is_blocked(self) -> bool:
        with self._lock:
            return self._is_blocked

    @is_blocked.setter
    def is_blocked(self, value: bool):
        with self._lock:
            self._is_blocked = value

    def get_travel_time_seconds(self) -> float:
        with self._lock:
            if self._is_blocked:
                return float('inf')
            speed_mps = (self.base_speed_limit_kmph * 1000.0 / 3600.0) * self._traffic_multiplier
            if speed_mps <= 0:
                return float('inf')
            return self.base_distance_meters / speed_mps


class RoadGraphV2:
    def __init__(self, closure_confidence_threshold: int = 3):
        if closure_confidence_threshold < 1:
            raise ValueError("closure confidence threshold must be at least 1")
        self.nodes = {}
        self.edges = {}
        self.adjacency_list = {}
        self._lock = RLock()
        self.closure_confidence_threshold = closure_confidence_threshold
        self._avoidance_counts = {}

    def add_node(self, node: Node):
        with self._lock:
            self.nodes[node.id] = node
            if node.id not in self.adjacency_list:
                self.adjacency_list[node.id] = []

    def add_edge(self, edge: Edge):
        with self._lock:
            self.edges[edge.id] = edge
            if edge.source_id not in self.adjacency_list:
                self.adjacency_list[edge.source_id] = []
            self.adjacency_list[edge.source_id].append(edge)

    def get_node(self, node_id: str) -> Node:
        with self._lock:
            return self.nodes.get(node_id)

    def get_edge(self, edge_id: str) -> Edge:
        with self._lock:
            return self.edges.get(edge_id)

    def get_outgoing_edges(self, node_id: str) -> list:
        with self._lock:
            return list(self.adjacency_list.get(node_id, []))

    def update_traffic(self, edge_id: str, multiplier: float):
        with self._lock:
            edge = self.edges.get(edge_id)
            if edge:
                edge.traffic_multiplier = multiplier

    def set_road_blocked(self, edge_id: str, blocked: bool):
        with self._lock:
            edge = self.edges.get(edge_id)
            if edge:
                edge.is_blocked = blocked

    # --- Improvement #2: closure confidence from telemetry ---

    def record_reroute_avoidance(self, edge_id: str) -> int:
        """A user rerouted away from this segment. Returns the segment's
        accumulated avoidance confidence."""
        with self._lock:
            if edge_id not in self.edges:
                raise KeyError(f"Edge {edge_id} not found")
            self._avoidance_counts[edge_id] = self._avoidance_counts.get(edge_id, 0) + 1
            return self._avoidance_counts[edge_id]

    def record_traversal(self, edge_id: str):
        """A user successfully traversed this segment, so the closure
        hypothesis is wrong: reset its avoidance confidence."""
        with self._lock:
            if edge_id not in self.edges:
                raise KeyError(f"Edge {edge_id} not found")
            self._avoidance_counts[edge_id] = 0

    def avoidance_confidence(self, edge_id: str) -> int:
        with self._lock:
            return self._avoidance_counts.get(edge_id, 0)

    def evaluate_closures(self) -> list:
        """Marks every edge at or over the confidence threshold as blocked
        and returns the newly closed edge ids. Edges below the threshold
        stay open: a single detour never closes a road."""
        newly_closed = []
        with self._lock:
            for edge_id, count in self._avoidance_counts.items():
                edge = self.edges.get(edge_id)
                if edge and count >= self.closure_confidence_threshold and not edge.is_blocked:
                    edge.is_blocked = True
                    newly_closed.append(edge_id)
        return newly_closed
