import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'v3-distributed')))

from distributed_metrics_monitoring_service import (
    DistributedMetricsMonitoringService,
    MetricPoint,
    MetricType,
    ConsistentHashRing
)

def test_consistent_hash_ring():
    ring = ConsistentHashRing(virtual_nodes=10)
    ring.add_node("node1")
    ring.add_node("node2")
    ring.add_node("node3")

    nodes = ring.get_nodes("test_metric", 2)
    assert len(nodes) == 2
    assert len(set(nodes)) == 2

    ring.remove_node(nodes[0])
    new_nodes = ring.get_nodes("test_metric", 2)
    assert len(new_nodes) == 2
    assert nodes[0] not in new_nodes


def test_ingest_and_query_scatter_gather():
    service = DistributedMetricsMonitoringService(num_nodes=3, replication_factor=2)

    p1 = MetricPoint("http_requests", MetricType.COUNTER, {"method": "GET"}, 1000, 1.0)
    p2 = MetricPoint("http_requests", MetricType.COUNTER, {"method": "GET"}, 2000, 2.0)
    p3 = MetricPoint("cpu_usage", MetricType.GAUGE, {"host": "web1"}, 1500, 85.5)

    service.ingest(p1)
    service.ingest(p2)
    service.ingest(p3)

    total = service.get_counter_total("http_requests", {"method": "GET"}, 0, 3000)
    assert total == 3.0

    gauge = service.get_gauge_latest("cpu_usage", {"host": "web1"}, 0, 3000)
    assert gauge == 85.5


def test_tiered_storage_flush():
    service = DistributedMetricsMonitoringService(num_nodes=1, replication_factor=1)
    node = service.nodes["node_0"]

    # 3600000 is 1 hour chunk size
    p1 = MetricPoint("test", MetricType.COUNTER, {}, 1000, 5.0)
    service.ingest(p1)

    assert len(node.wal) == 1
    assert len(node.local_chunks) == 0

    service.flush_all()
    assert len(node.wal) == 0
    assert len(node.local_chunks) == 1

    # In cold store?
    service.cold_flush_all(0)
    assert len(node.local_chunks) == 0

    # Can still query?
    total = service.get_counter_total("test", {}, 0, 2000)
    assert total == 5.0


def test_node_failover_and_reconciliation():
    service = DistributedMetricsMonitoringService(num_nodes=3, replication_factor=2)

    p1 = MetricPoint("reqs", MetricType.COUNTER, {}, 1000, 10.0)

    shard_key = service._get_shard_key(p1.name, p1.tags)
    target_nodes = service.ring.get_nodes(shard_key, 2)

    # Mark one target node down
    down_node = target_nodes[0]
    up_node = target_nodes[1]

    service.set_node_status(down_node, False)

    # Ingest should succeed on the remaining up_node
    service.ingest(p1)

    # Bring node back up
    service.set_node_status(down_node, True)

    # Before reconciliation, down_node has no data
    assert len(service.nodes[down_node].query("reqs", {}, 0, 2000)) == 0

    # Reconcile
    service.reconcile_replicas("reqs", {}, 0, 2000)

    # Both nodes should have the data
    assert len(service.nodes[down_node].query("reqs", {}, 0, 2000)) == 1
    assert len(service.nodes[up_node].query("reqs", {}, 0, 2000)) == 1
