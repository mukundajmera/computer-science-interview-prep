"""Dynamic cost and latency SLA router."""

from typing import List, Optional, Callable, Dict
import time
from dataclasses import dataclass, field
import sys
import os

# Add v1-basic path
_here = os.path.dirname(os.path.abspath(__file__))
_v1_path = os.path.join(_here, "..", "v1-basic")
if _v1_path not in sys.path:
    sys.path.insert(0, _v1_path)

from provider import LLMProvider, LLMRequest, LLMResponse, ProviderError

@dataclass
class ProviderStats:
    name: str
    provider: LLMProvider
    cost_per_1k_tokens: float
    latency_ms_moving_avg: float = 0.0

class DynamicCostRouter(LLMProvider):
    """Routes requests to the optimal provider based on cost and SLA."""

    def __init__(self, providers: List[ProviderStats], latency_sla_ms: float, alpha: float = 0.2):
        self.providers = providers
        self.latency_sla_ms = latency_sla_ms
        self.alpha = alpha

    def get_cheapest_under_sla(self) -> ProviderStats:
        """Find the cheapest provider that meets the latency SLA."""
        # First try to find eligible providers under SLA
        eligible = [p for p in self.providers if p.latency_ms_moving_avg <= self.latency_sla_ms or p.latency_ms_moving_avg == 0.0]

        if not eligible:
            # If no provider is under SLA, fallback to the fastest one
            sorted_by_latency = sorted(self.providers, key=lambda p: p.latency_ms_moving_avg)
            return sorted_by_latency[0]

        # Sort eligible by cost ascending
        eligible.sort(key=lambda p: p.cost_per_1k_tokens)
        return eligible[0]

    def _update_latency(self, provider_name: str, latency_ms: float) -> None:
        """Update moving average latency for a provider."""
        for p in self.providers:
            if p.name == provider_name:
                if p.latency_ms_moving_avg == 0.0:
                    p.latency_ms_moving_avg = latency_ms
                else:
                    p.latency_ms_moving_avg = (self.alpha * latency_ms) + ((1.0 - self.alpha) * p.latency_ms_moving_avg)
                break

    def complete(self, request: LLMRequest) -> LLMResponse:
        best_provider = self.get_cheapest_under_sla()

        start_time = time.monotonic()
        try:
            response = best_provider.provider.complete(request)
            latency_ms = (time.monotonic() - start_time) * 1000
            self._update_latency(best_provider.name, latency_ms)
            return response
        except Exception as e:
            # Optionally update latency on error if appropriate or skip
            raise e
