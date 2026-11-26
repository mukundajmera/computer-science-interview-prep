"""Tests for v2-extended LLM orchestrator features."""

import sys
import os
import time
import pytest

_here = os.path.dirname(os.path.abspath(__file__))
_v1_path = os.path.join(_here, "..", "v1-basic")
_v2_path = os.path.join(_here, "..", "v2-extended")

if _v1_path not in sys.path:
    sys.path.insert(0, _v1_path)
if _v2_path not in sys.path:
    sys.path.insert(0, _v2_path)

from provider import LLMRequest, MockProvider
from cost_router import DynamicCostRouter, ProviderStats
from priority_queue import PriorityQueue, Tier
from token_rate_limiter import TokenRateLimiter


def test_cost_router_selects_cheapest_under_sla():
    p1 = MockProvider(response_content="P1")
    p2 = MockProvider(response_content="P2")
    p3 = MockProvider(response_content="P3")

    stats1 = ProviderStats("P1", p1, cost_per_1k_tokens=0.03, latency_ms_moving_avg=150.0)
    stats2 = ProviderStats("P2", p2, cost_per_1k_tokens=0.01, latency_ms_moving_avg=400.0)
    stats3 = ProviderStats("P3", p3, cost_per_1k_tokens=0.02, latency_ms_moving_avg=200.0)

    # SLA 250ms -> P1 (150ms, $0.03) and P3 (200ms, $0.02) are eligible.
    # P3 is cheaper ($0.02 vs $0.03), so P3 should be chosen.
    router = DynamicCostRouter([stats1, stats2, stats3], latency_sla_ms=250.0)
    req = LLMRequest(prompt="Test")

    resp = router.complete(req)
    assert resp.content == "P3"

    # Check that latency was updated (will be slightly non-zero based on MockProvider speed)
    # alpha is 0.2, new avg = (0.2 * new) + (0.8 * old)
    assert stats3.latency_ms_moving_avg != 200.0


def test_cost_router_fallback_when_all_above_sla():
    p1 = MockProvider(response_content="P1")
    p2 = MockProvider(response_content="P2")

    stats1 = ProviderStats("P1", p1, cost_per_1k_tokens=0.03, latency_ms_moving_avg=300.0)
    stats2 = ProviderStats("P2", p2, cost_per_1k_tokens=0.01, latency_ms_moving_avg=400.0)

    # SLA 250ms -> None eligible.
    # Should fallback to fastest one, which is P1 (300ms).
    router = DynamicCostRouter([stats1, stats2], latency_sla_ms=250.0)
    req = LLMRequest(prompt="Test")

    resp = router.complete(req)
    assert resp.content == "P1"


def test_priority_queue_ordering():
    pq = PriorityQueue(max_size=5)

    pq.enqueue("Item Free", Tier.FREE)
    pq.enqueue("Item VIP", Tier.VIP)
    pq.enqueue("Item Paid", Tier.PAID)

    # VIP should come first, then Paid, then Free
    assert pq.dequeue() == "Item VIP"
    assert pq.dequeue() == "Item Paid"
    assert pq.dequeue() == "Item Free"
    assert pq.dequeue() is None


def test_priority_queue_load_shedding():
    pq = PriorityQueue(max_size=2)

    pq.enqueue("Free 1", Tier.FREE)
    pq.enqueue("Free 2", Tier.FREE)

    # Queue is full with Free requests.
    # Enqueuing VIP should shed one Free request (the last one inserted, but depends on logic).
    enqueued = pq.enqueue("VIP", Tier.VIP)
    assert enqueued is True

    item1 = pq.dequeue()
    assert item1 == "VIP"

    item2 = pq.dequeue()
    assert item2 == "Free 1"  # Free 2 was shed

    assert pq.dequeue() is None

    # If we fill with VIP, a Free request should be rejected
    pq.enqueue("VIP 1", Tier.VIP)
    pq.enqueue("VIP 2", Tier.VIP)

    enqueued = pq.enqueue("Free Reject", Tier.FREE)
    assert enqueued is False
    assert pq.qsize() == 2


def test_token_rate_limiter():
    rl = TokenRateLimiter(max_rpm=10, max_tpm=100)

    # Acquire 60 tokens
    assert rl.acquire(60) is True

    # Acquire 50 tokens should fail
    assert rl.acquire(50) is False

    # Refund 20 tokens (60 used - 20 = 40 used, so 60 available)
    rl.refund(20)

    # Now acquire 50 should succeed
    assert rl.acquire(50) is True

    # Check max rpm
    rl = TokenRateLimiter(max_rpm=1, max_tpm=100)
    assert rl.acquire(10) is True
    assert rl.acquire(10) is False # Out of RPM tokens
