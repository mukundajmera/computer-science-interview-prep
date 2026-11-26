"""Hedged request executor."""

import concurrent.futures
import time
import os
import sys
from typing import Optional

_here = os.path.dirname(os.path.abspath(__file__))
_v1_path = os.path.join(_here, "..", "v1-basic")
if _v1_path not in sys.path:
    sys.path.insert(0, _v1_path)

from provider import LLMProvider, LLMRequest, LLMResponse, ProviderError

class HedgedRequestExecutor(LLMProvider):
    """Fires speculative secondary request if primary doesn't return within threshold."""

    def __init__(self, primary: LLMProvider, secondary: LLMProvider, p95_latency_threshold_ms: float):
        self.primary = primary
        self.secondary = secondary
        self.p95_latency_threshold_ms = p95_latency_threshold_ms
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=10) # Reusable executor

    def complete(self, request: LLMRequest) -> LLMResponse:
        timeout_sec = self.p95_latency_threshold_ms / 1000.0

        primary_future = self.executor.submit(self.primary.complete, request)

        try:
            # Wait for primary to complete within the threshold
            return primary_future.result(timeout=timeout_sec)
        except concurrent.futures.TimeoutError:
            pass
        except Exception:
            # Primary failed quickly, we will fallback to secondary below
            pass

        # Primary timed out or failed quickly, fire secondary
        secondary_future = self.executor.submit(self.secondary.complete, request)

        futures = [primary_future, secondary_future]
        exceptions = []

        # Wait for any future to complete successfully.
        for future in concurrent.futures.as_completed(futures):
            try:
                return future.result()
            except Exception as e:
                exceptions.append(e)

        # If both failed
        raise ProviderError(f"Both primary and secondary requests failed. Errors: {exceptions}")
