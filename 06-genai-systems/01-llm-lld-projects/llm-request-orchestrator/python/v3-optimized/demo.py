#!/usr/bin/env python3
"""Demo for v3-optimized features."""

import sys
import os
import time

_here = os.path.dirname(os.path.abspath(__file__))
_v1_path = os.path.join(_here, "..", "v1-basic")
if _v1_path not in sys.path:
    sys.path.insert(0, _v1_path)

from provider import LLMProvider, LLMRequest, LLMResponse, MockProvider
from hedged_client import HedgedRequestExecutor
from latency_router import LatencyAdaptiveRouter

class SleepyProvider(LLMProvider):
    def __init__(self, delay, name):
        self.delay = delay
        self.name = name

    def complete(self, request):
        time.sleep(self.delay)
        return LLMResponse(content=f"{self.name} response", model="model")

def demo_hedged_client():
    print("--- Demo: Hedged Request Executor ---")

    # Primary is slow (500ms), secondary is fast (100ms)
    p1 = SleepyProvider(0.5, "Primary (Slow)")
    p2 = SleepyProvider(0.1, "Secondary (Fast)")

    # Threshold is 200ms
    hedged = HedgedRequestExecutor(p1, p2, 200.0)

    start = time.time()
    req = LLMRequest(prompt="Hello")
    resp = hedged.complete(req)
    duration = time.time() - start

    print(f"Hedged request took {duration:.3f}s, response: {resp.content}")
    print("Expected to see Secondary response since primary took >200ms.")
    print()

def demo_latency_router():
    print("--- Demo: Latency Adaptive Router ---")

    # We will simulate latency changes by updating the delay on the fly.
    p1 = SleepyProvider(0.1, "P1")
    p2 = SleepyProvider(0.3, "P2")

    router = LatencyAdaptiveRouter([p1, p2], alpha=0.5)

    req = LLMRequest(prompt="Hello")

    # Both are untested, P1 (index 0) is picked first
    print("Request 1:")
    resp = router.complete(req)
    print(f"Response: {resp.content}")
    print(f"EMA Latencies: {router.ema_latencies}")

    # P2 (index 1) is picked next because it's untested
    print("Request 2:")
    resp = router.complete(req)
    print(f"Response: {resp.content}")
    print(f"EMA Latencies: {router.ema_latencies}")

    # Now P1 has 100ms EMA, P2 has 300ms EMA, so P1 should be picked
    print("Request 3:")
    resp = router.complete(req)
    print(f"Response: {resp.content}")
    print(f"EMA Latencies: {router.ema_latencies}")

    # Suddenly P1 becomes slow
    p1.delay = 0.6
    print("Request 4 (P1 is now slow):")
    resp = router.complete(req)
    print(f"Response: {resp.content}")
    print(f"EMA Latencies: {router.ema_latencies}")

    # After a couple of requests, P1's EMA will cross P2's EMA (300ms)
    print("Request 5:")
    resp = router.complete(req)
    print(f"Response: {resp.content}")
    print(f"EMA Latencies: {router.ema_latencies}")

    print("Request 6:")
    resp = router.complete(req)
    print(f"Response: {resp.content}")
    print(f"EMA Latencies: {router.ema_latencies}")

    print()

if __name__ == "__main__":
    demo_hedged_client()
    demo_latency_router()
