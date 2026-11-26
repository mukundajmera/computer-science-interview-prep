#!/usr/bin/env python3
"""Demo for v2-extended features."""

import sys
import os

# Add v1-basic path
_here = os.path.dirname(os.path.abspath(__file__))
_v1_path = os.path.join(_here, "..", "v1-basic")
if _v1_path not in sys.path:
    sys.path.insert(0, _v1_path)

from provider import LLMRequest, MockProvider
from cost_router import DynamicCostRouter, ProviderStats
from priority_queue import PriorityQueue, Tier
from token_rate_limiter import TokenRateLimiter

def demo_cost_router():
    print("--- Demo: Dynamic Cost Router ---")
    p1 = MockProvider(response_content="OpenAI response")
    p2 = MockProvider(response_content="Anthropic response")

    stats1 = ProviderStats("OpenAI", p1, cost_per_1k_tokens=0.03, latency_ms_moving_avg=200.0)
    stats2 = ProviderStats("Anthropic", p2, cost_per_1k_tokens=0.01, latency_ms_moving_avg=400.0)

    router = DynamicCostRouter([stats1, stats2], latency_sla_ms=300.0)

    req = LLMRequest(prompt="Hello")
    resp = router.complete(req)

    print(f"Chosen provider latency SLA: 300ms")
    print(f"Response: {resp.content}")
    print(f"Expected to pick OpenAI (since Anthropic is > 300ms SLA, though cheaper)")
    print()

def demo_priority_queue():
    print("--- Demo: Priority Queue Load Shedding ---")
    pq = PriorityQueue(max_size=2)

    pq.enqueue("Free request 1", Tier.FREE)
    pq.enqueue("Free request 2", Tier.FREE)

    print(f"Queue size before VIP: {pq.qsize()}")

    # This should evict one of the FREE requests
    enqueued = pq.enqueue("VIP request", Tier.VIP)
    print(f"VIP enqueued? {enqueued}")

    item1 = pq.dequeue()
    item2 = pq.dequeue()

    print(f"Dequeued 1: {item1}")
    print(f"Dequeued 2: {item2}")
    print()

def demo_token_rate_limiter():
    print("--- Demo: Token Rate Limiter ---")
    rl = TokenRateLimiter(max_rpm=10, max_tpm=100)

    # Try to acquire 60 tokens
    success1 = rl.acquire(60)
    print(f"Acquire 60 tokens (expect True): {success1}")

    # Try to acquire 50 tokens (should fail, only 40 left)
    success2 = rl.acquire(50)
    print(f"Acquire 50 tokens (expect False): {success2}")
    print()

if __name__ == "__main__":
    demo_cost_router()
    demo_priority_queue()
    demo_token_rate_limiter()
