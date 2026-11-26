import sys
import os

# Add the v1-simple folder to sys.path so we can import the target module
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'v1-simple'))

from postgres_read_write_planner import (
    PostgresReadWritePlanner,
    QueryContext,
    OperationType,
    Route,
)

def test_write_operation_routes_to_primary():
    planner = PostgresReadWritePlanner()
    context = QueryContext(operation_type=OperationType.WRITE, requires_read_after_write=False, max_replica_lag_ms=1000)
    route = planner.decide_route(context, 100)
    assert route == Route.PRIMARY

def test_read_with_read_after_write_routes_to_primary():
    planner = PostgresReadWritePlanner()
    context = QueryContext(operation_type=OperationType.READ, requires_read_after_write=True, max_replica_lag_ms=1000)
    route = planner.decide_route(context, 100)
    assert route == Route.PRIMARY

def test_read_with_high_lag_routes_to_primary():
    planner = PostgresReadWritePlanner()
    context = QueryContext(operation_type=OperationType.READ, requires_read_after_write=False, max_replica_lag_ms=100)
    route = planner.decide_route(context, 200)
    assert route == Route.PRIMARY

def test_read_with_low_lag_routes_to_replica():
    planner = PostgresReadWritePlanner()
    context = QueryContext(operation_type=OperationType.READ, requires_read_after_write=False, max_replica_lag_ms=500)
    route = planner.decide_route(context, 100)
    assert route == Route.REPLICA
