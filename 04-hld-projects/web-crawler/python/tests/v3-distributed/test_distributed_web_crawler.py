import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'v3-distributed')))
from distributed_web_crawler import DistributedWebCrawler


@pytest.fixture
def crawler():
    return DistributedWebCrawler()


def test_hash_ring_partitioning(crawler):
    w1 = crawler.add_worker("worker-1")
    w2 = crawler.add_worker("worker-2")
    w3 = crawler.add_worker("worker-3")

    url1 = "http://example.com/page1"
    url2 = "http://test.com/page1"

    crawler.submit_to_cluster(url1)
    crawler.submit_to_cluster(url2)

    total = len(w1.get_local_frontier()) + len(w2.get_local_frontier()) + len(w3.get_local_frontier())
    assert total == 2

    crawler.submit_to_cluster("http://example.com/page2")

    example_worker = None
    if url1 in w1.get_local_frontier():
        example_worker = w1
    elif url1 in w2.get_local_frontier():
        example_worker = w2
    elif url1 in w3.get_local_frontier():
        example_worker = w3

    assert example_worker is not None
    assert "http://example.com/page2" in example_worker.get_local_frontier()


def test_distributed_deduplication(crawler):
    w1 = crawler.add_worker("worker-1")

    crawler.submit_to_cluster("http://example.com/page1")
    crawler.submit_to_cluster("http://example.com/page1")

    assert len(w1.get_local_frontier()) == 1

    crawler.submit_to_cluster("http://example.com/page2")
    assert len(w1.get_local_frontier()) == 2


def test_worker_failure_recovery(crawler):
    w1 = crawler.add_worker("worker-1")

    url1 = "http://example1.com/page1"
    url2 = "http://example2.com/page1"

    crawler.submit_to_cluster(url1)
    crawler.submit_to_cluster(url2)

    assert len(w1.get_local_frontier()) == 2

    w2 = crawler.add_worker("worker-2")

    w1.stop()
    # Simulate timeout by setting heartbeat back in time
    crawler.coordinator.last_heartbeat[w1.worker_id] -= 10.0

    crawler.detect_and_recover_failures(timeout_seconds=5.0)

    assert len(w2.get_local_frontier()) == 2
    assert url1 in w2.get_local_frontier()
    assert url2 in w2.get_local_frontier()


def test_politeness_rate_limiting(crawler):
    w1 = crawler.add_worker("worker-1")

    for i in range(10):
        w1.force_submit_local(f"http://example.com/page{i}")

    # First 5 should succeed (bucket capacity = 5)
    for _ in range(5):
        assert w1.fetch_next() is not None

    # Next attempt should be rate limited
    assert w1.fetch_next() is None
