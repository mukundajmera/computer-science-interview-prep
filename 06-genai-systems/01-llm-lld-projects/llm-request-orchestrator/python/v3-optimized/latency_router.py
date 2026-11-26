"""Latency-adaptive router."""

import time
import os
import sys
from typing import List, Dict

_here = os.path.dirname(os.path.abspath(__file__))
_v1_path = os.path.join(_here, "..", "v1-basic")
if _v1_path not in sys.path:
    sys.path.insert(0, _v1_path)

from provider import LLMProvider, LLMRequest, LLMResponse, ProviderError

class LatencyAdaptiveRouter(LLMProvider):
    """Tracks moving EMA p99 latency and routes traffic to the healthiest provider."""

    def __init__(self, providers: List[LLMProvider], alpha: float = 0.1):
        self.providers = providers
        self.alpha = alpha

        # We track latency by provider index or id. Since we just have a list, we use index.
        # Initialize EMA latency to 0.0
        self.ema_latencies = {i: 0.0 for i in range(len(providers))}

    def _get_healthiest_provider_index(self) -> int:
        # If any provider has 0 latency (untested), use it first
        for i, lat in self.ema_latencies.items():
            if lat == 0.0:
                return i

        # Otherwise, pick the one with the lowest EMA latency
        return min(self.ema_latencies, key=self.ema_latencies.get)

    def complete(self, request: LLMRequest) -> LLMResponse:
        if not self.providers:
            raise ProviderError("No providers available")

        # In a real system, if the healthiest fails, we might try the next one.
        # But as a router, we might just try the best and let the orchestrator retry.
        idx = self._get_healthiest_provider_index()
        provider = self.providers[idx]

        start_time = time.monotonic()
        try:
            response = provider.complete(request)
            latency_ms = (time.monotonic() - start_time) * 1000

            # Update EMA latency
            current_ema = self.ema_latencies[idx]
            if current_ema == 0.0:
                self.ema_latencies[idx] = latency_ms
            else:
                self.ema_latencies[idx] = (self.alpha * latency_ms) + ((1.0 - self.alpha) * current_ema)

            return response
        except Exception as e:
            # On failure, we might heavily penalize the latency so it's not chosen again soon.
            # E.g., set latency to a very high value or max out.
            current_ema = self.ema_latencies[idx]
            penalty = 10000.0 # 10s penalty
            if current_ema == 0.0:
                self.ema_latencies[idx] = penalty
            else:
                self.ema_latencies[idx] = (self.alpha * penalty) + ((1.0 - self.alpha) * current_ema)
            raise e
