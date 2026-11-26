import sys
import os
import math

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'v1-basic')))

import pytest
from road_graph import RoadGraph, Node, Edge
from google_maps_service import GoogleMapsService, RouteOptimizer, TileCoordinate

@pytest.fixture
def setup_graph():
    graph = RoadGraph()
    
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

    service = GoogleMapsService(graph)
    return graph, service

def test_a_star_pathfinding(setup_graph):
    graph, service = setup_graph
    result = service.calculate_route("A", "C")
    assert result is not None
    assert len(result.path_nodes) == 3
    assert result.path_nodes[0].id == "A"
    assert result.path_nodes[1].id == "B"
    assert result.path_nodes[2].id == "C"
    
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
    assert len(instructions) > 0
    
    has_main_st = any("Main St" in instr and "150" in instr for instr in instructions)
    has_2nd_ave = any("2nd Ave" in instr and "100" in instr for instr in instructions)
    has_dest = any("destination" in instr for instr in instructions)
    
    assert has_main_st
    assert has_2nd_ave
    assert has_dest

def test_lat_lng_to_tile(setup_graph):
    graph, service = setup_graph
    tile0 = service.get_slippy_map_tile(37.7749, -122.4194, 0)
    assert tile0.x == 0
    assert tile0.y == 0
    
    lat = 37.7749
    lng = -122.4194
    zoom = 10
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
    
    path_str = "".join(n.id for n in rerouted.path_nodes)
    assert path_str == "ABEFC"
