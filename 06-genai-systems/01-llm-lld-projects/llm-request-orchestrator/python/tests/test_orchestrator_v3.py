"""Tests for v3-optimized LLM orchestrator features."""

import sys
import os
import time
import pytest

_here = os.path.dirname(os.path.abspath(__file__))
_v1_path = os.path.join(_here, "..", "v1-basic")
_v3_path = os.path.join(_here, "..", "v3-optimized")

if _v1_path not in sys.path:
    sys.path.insert(0, _v1_path)
if _v3_path not in sys.path:
    sys.path.insert(0, _v3_path)

from provider import LLMProvider, LLMRequest, LLMResponse, ProviderError
from hedged_client import HedgedRequestExecutor
from latency_router import LatencyAdaptiveRouter

class DummyProvider(LLMProvider):
    def __init__(self, response_content, delay=0.0, error=False):
        self.response_content = response_content
        self.delay = delay
        self.error = error

    def complete(self, request):
        if self.delay > 0:
            time.sleep(self.delay)
        if self.error:
            raise ProviderError(f"Error from {self.response_content}")
        return LLMResponse(content=self.response_content, model="dummy")

def test_hedged_client_primary_fast_enough():
    p1 = DummyProvider("Primary", delay=0.01)
    p2 = DummyProvider("Secondary", delay=0.01)

    executor = HedgedRequestExecutor(p1, p2, p95_latency_threshold_ms=100.0)
    req = LLMRequest(prompt="Test")

    resp = executor.complete(req)
    assert resp.content == "Primary"

def test_hedged_client_primary_slow():
    p1 = DummyProvider("Primary", delay=0.2)
    p2 = DummyProvider("Secondary", delay=0.01)

    executor = HedgedRequestExecutor(p1, p2, p95_latency_threshold_ms=50.0)
    req = LLMRequest(prompt="Test")

    resp = executor.complete(req)
    assert resp.content == "Secondary"

def test_hedged_client_both_fail():
    p1 = DummyProvider("Primary", error=True)
    p2 = DummyProvider("Secondary", error=True)

    executor = HedgedRequestExecutor(p1, p2, p95_latency_threshold_ms=50.0)
    req = LLMRequest(prompt="Test")

    with pytest.raises(ProviderError, match="Both primary and secondary requests failed"):
        executor.complete(req)

def test_hedged_client_primary_fails_secondary_succeeds():
    p1 = DummyProvider("Primary", error=True)
    p2 = DummyProvider("Secondary", delay=0.01)

    executor = HedgedRequestExecutor(p1, p2, p95_latency_threshold_ms=100.0)
    req = LLMRequest(prompt="Test")

    resp = executor.complete(req)
    assert resp.content == "Secondary"

def test_latency_router_empty_providers():
    router = LatencyAdaptiveRouter([])
    req = LLMRequest(prompt="Test")

    with pytest.raises(ProviderError, match="No providers available"):
        router.complete(req)

def test_latency_router_picks_untested_first():
    p1 = DummyProvider("P1")
    p2 = DummyProvider("P2")

    router = LatencyAdaptiveRouter([p1, p2])
    req = LLMRequest(prompt="Test")

    resp1 = router.complete(req)
    resp2 = router.complete(req)

    # Should pick P1 then P2 because both start untested (latency 0.0)
    assert set([resp1.content, resp2.content]) == {"P1", "P2"}

def test_latency_router_updates_ema_and_picks_fastest():
    p1 = DummyProvider("P1", delay=0.2)
    p2 = DummyProvider("P2", delay=0.01)

    router = LatencyAdaptiveRouter([p1, p2], alpha=1.0) # alpha=1.0 means it replaces old value completely
    req = LLMRequest(prompt="Test")

    router.complete(req) # P1
    router.complete(req) # P2

    # P1 is 200ms, P2 is 10ms
    assert router.ema_latencies[0] > 100
    assert router.ema_latencies[1] < 50

    # Next request should definitely go to P2
    resp3 = router.complete(req)
    assert resp3.content == "P2"

def test_latency_router_penalizes_errors():
    p1 = DummyProvider("P1", error=True)
    p2 = DummyProvider("P2", delay=0.01)

    router = LatencyAdaptiveRouter([p1, p2], alpha=1.0)
    req = LLMRequest(prompt="Test")

    with pytest.raises(ProviderError):
        router.complete(req) # P1 is tried and fails

    # P1 should have a high penalty
    assert router.ema_latencies[0] >= 10000.0

    # Next should go to P2
    resp2 = router.complete(req)
    assert resp2.content == "P2"

def test_hedged_client_does_not_block():
    # If primary is extremely slow, it shouldn't block the secondary from returning fast.
    # It also shouldn't block the caller while primary completes.
    p1 = DummyProvider("Primary", delay=5.0)
    p2 = DummyProvider("Secondary", delay=0.01)

    executor = HedgedRequestExecutor(p1, p2, p95_latency_threshold_ms=50.0)
    req = LLMRequest(prompt="Test")

    start_time = time.monotonic()
    resp = executor.complete(req)
    end_time = time.monotonic()

    assert resp.content == "Secondary"
    assert end_time - start_time < 1.0 # Should take ~50ms + 10ms = 60ms, so definitely < 1s
