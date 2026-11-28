import sys
import os
import math

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'v2-extended')))

import pytest
from road_graph_v2 import RoadGraphV2, Node, Edge
from google_maps_service_v2 import GoogleMapsServiceV2, RouteOptimizerV2, TileCoordinate
from telemetry_v2 import TelemetryBatcher


@pytest.fixture
def setup_graph():
    graph = RoadGraphV2()

    graph.add_node(Node("A", 37.7749, -122.4194))
    graph.add_node(Node("B", 37.7750, -122.4180))
    graph.add_node(Node("C", 37.7751, -122.4160))
    graph.add_node(Node("D", 37.7740, -122.4194))
    graph.add_node(Node("E", 37.7740, -122.4180))
    graph.add_node(Node("F", 37.7740, -122.4160))

    graph.add_edge(Edge("e1", "A", "B", 150, 50, "Main St"))
    graph.add_edge(Edge("e2", "B", "C", 200, 50, "Main St"))

    graph.add_edge(Edge("e3", "A", "D", 100, 40, "1st Ave"))
    graph.add_edge(Edge("e4", "B", "E", 100, 40, "2nd Ave"))
    graph.add_edge(Edge("e5", "C", "F", 100, 40, "3rd Ave"))

    graph.add_edge(Edge("e6", "D", "E", 150, 50, "South St"))
    graph.add_edge(Edge("e7", "E", "F", 200, 50, "South St"))

    service = GoogleMapsServiceV2(graph)
    return graph, service


# --- Parity with the v1 test scenarios ---

def test_a_star_pathfinding(setup_graph):
    graph, service = setup_graph
    result = service.calculate_route("A", "C")
    assert result is not None
    assert [n.id for n in result.path_nodes] == ["A", "B", "C"]

    expected_time = (150.0 / (50.0 * 1000.0 / 3600.0)) + (200.0 / (50.0 * 1000.0 / 3600.0))
    assert abs(result.total_time_seconds - expected_time) < 0.001


def test_traffic_eta_increase(setup_graph):
    graph, service = setup_graph
    graph.update_traffic("e2", 0.1)

    result = service.calculate_route("A", "F")
    assert result is not None
    path_node_ids = [n.id for n in result.path_nodes]
    assert "B" in path_node_ids
    assert "E" in path_node_ids

    graph.update_traffic("e2", 1.0)


def test_turn_by_turn_instructions(setup_graph):
    graph, service = setup_graph
    result = service.calculate_route("A", "F")
    assert result is not None
    instructions = result.turn_by_turn_instructions

    assert any("Main St" in instr and "150" in instr for instr in instructions)
    assert any("2nd Ave" in instr and "100" in instr for instr in instructions)
    assert any("destination" in instr for instr in instructions)


def test_lat_lng_to_tile(setup_graph):
    graph, service = setup_graph
    tile0 = service.get_slippy_map_tile(37.7749, -122.4194, 0)
    assert tile0.x == 0
    assert tile0.y == 0

    lat, lng, zoom = 37.7749, -122.4194, 10
    lat_rad = math.radians(lat)
    n = 1 << zoom
    expected_x = int((lng + 180.0) / 360.0 * n)
    expected_y = int((1.0 - math.log(math.tan(lat_rad) + (1 / math.cos(lat_rad))) / math.pi) / 2.0 * n)

    tile10 = service.get_slippy_map_tile(lat, lng, zoom)
    assert tile10.x == expected_x
    assert tile10.y == expected_y
    assert tile10.z == zoom


def test_dynamic_reroute_on_blocked_edge(setup_graph):
    graph, service = setup_graph
    graph.add_edge(Edge("e5_rev", "F", "C", 100, 40, "3rd Ave"))
    graph.add_edge(Edge("e4_rev", "E", "B", 100, 40, "2nd Ave"))

    rerouted = service.recalculate_route_on_blockage("A", "C", "e2")
    assert rerouted is not None
    assert "".join(n.id for n in rerouted.path_nodes) == "ABEFC"


# --- Improvement #2: closure detection with confidence threshold ---

def test_closure_below_threshold_stays_open(setup_graph):
    graph, service = setup_graph
    graph.record_reroute_avoidance("e2")
    graph.record_reroute_avoidance("e2")

    assert graph.evaluate_closures() == []
    assert not graph.get_edge("e2").is_blocked
    # The road is still routable.
    assert [n.id for n in service.calculate_route("A", "C").path_nodes] == ["A", "B", "C"]


def test_closure_at_threshold_blocks_edge(setup_graph):
    graph, service = setup_graph
    for _ in range(3):
        graph.record_reroute_avoidance("e2")

    assert graph.evaluate_closures() == ["e2"]
    assert graph.get_edge("e2").is_blocked


def test_traversal_resets_closure_confidence(setup_graph):
    graph, service = setup_graph
    graph.record_reroute_avoidance("e2")
    graph.record_reroute_avoidance("e2")
    graph.record_traversal("e2")  # someone got through: hypothesis wrong
    graph.record_reroute_avoidance("e2")
    graph.record_reroute_avoidance("e2")

    assert graph.avoidance_confidence("e2") == 2
    assert graph.evaluate_closures() == []
    assert not graph.get_edge("e2").is_blocked


# --- Improvement #1: offline corridor download ---

def test_offline_corridor_contains_route_and_surroundings(setup_graph):
    graph, service = setup_graph
    corridor = service.download_offline_corridor("A", "C", extra_hops=1)
    assert corridor is not None

    # Route nodes plus every node one hop off the route.
    assert set(corridor.nodes.keys()) == {"A", "B", "C", "D", "E", "F"}
    # Route edges plus one-hop alternates from A, B and C; edges leaving
    # D/E/F (two hops away from the route start) are not included.
    assert set(corridor.edges.keys()) == {"e1", "e2", "e3", "e4", "e5"}
    assert corridor.get_edge("e6") is None


def test_offline_corridor_supports_local_routing(setup_graph):
    graph, service = setup_graph
    corridor = service.download_offline_corridor("A", "C", extra_hops=1)

    offline_optimizer = RouteOptimizerV2(corridor)
    result = offline_optimizer.find_shortest_path("A", "C")
    assert result is not None
    assert [n.id for n in result.path_nodes] == ["A", "B", "C"]


def test_offline_corridor_none_without_route(setup_graph):
    graph, service = setup_graph
    assert service.download_offline_corridor("A", "UNKNOWN") is None


# --- Improvement #3: telemetry batching ---

def test_batcher_buffers_until_flush_interval():
    batcher = TelemetryBatcher(flush_interval_seconds=15.0, clock=lambda: 0.0)
    for t in range(15):
        assert batcher.record_ping(37.0, -122.0, timestamp=float(t)) is None
    assert batcher.pending_count() == 15

    batch = batcher.record_ping(37.0, -122.0, timestamp=15.0)
    assert batch is not None
    assert len(batch) == 16
    assert batch[0] == (37.0, -122.0, 0.0)
    assert batcher.pending_count() == 0


def test_batcher_keeps_partial_window_buffered():
    batcher = TelemetryBatcher(flush_interval_seconds=15.0, clock=lambda: 0.0)
    for t in range(6):
        assert batcher.record_ping(37.0, -122.0, timestamp=float(t)) is None
    assert batcher.pending_count() == 6
    assert len(batcher.flush(now=6.0)) == 6
    assert batcher.pending_count() == 0


def test_batcher_window_restarts_after_flush():
    batcher = TelemetryBatcher(flush_interval_seconds=15.0, clock=lambda: 0.0)
    assert batcher.record_ping(37.0, -122.0, timestamp=15.0) is not None
    assert batcher.record_ping(38.0, -123.0, timestamp=16.0) is None
    assert batcher.pending_count() == 1
