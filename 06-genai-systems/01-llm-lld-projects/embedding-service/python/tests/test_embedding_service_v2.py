"""
Tests for v2-extended features of the Embedding Service.
"""

import sys
import os
import time

# Ensure dynamic imports work
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'v2-extended')))

import pytest

from multi_model_registry import MultiModelRegistry, DimensionalityAdapter, EmbeddingModel
from quantized_cache import QuantizedCache
from typing import List
from batched_embedder import DynamicBatchEmbedder

class DummyModel(EmbeddingModel):
    def __init__(self, name="dummy", dimensions=8):
        self._name = name
        self._dimensions = dimensions
        self.batch_calls = 0

    @property
    def model_name(self) -> str:
        return self._name

    @property
    def dimensions(self) -> int:
        return self._dimensions

    def embed(self, text: str) -> List[float]:
        # Return a simple deterministic vector: [len(text), 1.0, 1.0, ...]
        return [float(len(text))] + [1.0] * (self._dimensions - 1)

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        self.batch_calls += 1
        return [self.embed(t) for t in texts]


def test_multi_model_registry_route():
    registry = MultiModelRegistry()
    model = DummyModel(name="model1", dimensions=4)
    registry.register(model)

    # Basic routing
    res = registry.route("test", "model1")
    assert len(res) == 4

    # Routing with dimensionality reduction
    res_trunc = registry.route("test", "model1", target_dimensions=2)
    assert len(res_trunc) == 2

    # Check normalization. Length of res is [4.0, 1.0, 1.0, 1.0] truncated to [4.0, 1.0].
    # Magnitude = sqrt(16 + 1) = sqrt(17) = ~4.123
    import math
    expected_mag = math.sqrt(sum(x*x for x in res_trunc))
    assert math.isclose(expected_mag, 1.0)


def test_quantized_cache():
    cache = QuantizedCache(max_size=5, ttl_seconds=60.0)

    original_vector = [0.5, -0.5, 1.0, -1.0, 0.0]
    cache.put("key1", original_vector)

    cached_vector = cache.get("key1")
    assert cached_vector is not None

    # Check that dequantized values are close to original
    for orig, cached in zip(original_vector, cached_vector):
        assert abs(orig - cached) < 0.05 # Error should be small due to 8-bit quantization

    stats = cache.stats()
    assert stats["hits"] == 1
    assert stats["size"] == 1


def test_dynamic_batch_embedder():
    model = DummyModel(dimensions=4)
    # Batch up to 3, timeout 50ms
    embedder = DynamicBatchEmbedder(model, max_batch_size=3, timeout_ms=50)

    futures = []
    for i in range(5):
        futures.append(embedder.embed_async(f"text{i}"))

    results = [f.result() for f in futures]
    assert len(results) == 5

    # 5 items with max_batch_size=3 should result in 2 batches (e.g., 3 and 2)
    assert model.batch_calls == 2

    embedder.shutdown()

def test_dynamic_batch_embedder_timeout():
    model = DummyModel(dimensions=4)
    embedder = DynamicBatchEmbedder(model, max_batch_size=10, timeout_ms=100)

    # Submit only 1 item. It should be processed after 100ms timeout
    start_time = time.time()
    future = embedder.embed_async("text")
    res = future.result()
    end_time = time.time()

    assert len(res) == 4
    assert model.batch_calls == 1
    # Check that it waited roughly the timeout
    assert end_time - start_time >= 0.09

    embedder.shutdown()

def test_multi_model_registry_errors():
    registry = MultiModelRegistry()
    model = DummyModel(name="model1", dimensions=4)
    registry.register(model)

    with pytest.raises(ValueError, match="not found in registry"):
        registry.route("test", "nonexistent")

    with pytest.raises(ValueError, match="exceeds model dimensions"):
        registry.route("test", "model1", target_dimensions=10)
