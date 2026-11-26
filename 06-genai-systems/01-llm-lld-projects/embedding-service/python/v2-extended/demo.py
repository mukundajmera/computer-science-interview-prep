"""
Embedding Service demo — v2 extended.

Showcases advanced features:
1. MultiModelRegistry and DimensionalityAdapter
2. QuantizedCache
3. DynamicBatchEmbedder
"""

import sys
import os

# Add parent directory to path so we can import v1_basic components if needed,
# or simply mock the HashEmbeddingModel for the demo.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..')))

from typing import List
import hashlib
import time

from multi_model_registry import MultiModelRegistry, EmbeddingModel
from quantized_cache import QuantizedCache
from batched_embedder import DynamicBatchEmbedder


class DemoHashModel(EmbeddingModel):
    def __init__(self, dimensions: int = 128):
        self._dimensions = dimensions

    @property
    def model_name(self) -> str:
        return "demo-hash"

    @property
    def dimensions(self) -> int:
        return self._dimensions

    def embed(self, text: str) -> List[float]:
        digest = hashlib.sha256(text.encode("utf-8")).digest()
        values = []
        for i in range(self._dimensions):
            byte_val = digest[i % len(digest)]
            # Map to range [-1.0, 1.0] to mimic normalized embeddings
            values.append((byte_val / 127.5) - 1.0)
        return values

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        # Add a tiny sleep to simulate latency and show batching
        time.sleep(0.01)
        return [self.embed(t) for t in texts]


def main() -> None:
    print("=" * 60)
    print("EMBEDDING SERVICE DEMO (v2-extended)")
    print("=" * 60)

    # 1. MultiModelRegistry and DimensionalityAdapter
    print("\n--- Multi-Model Registry & Dimensionality Projection ---")
    registry = MultiModelRegistry()
    base_model = DemoHashModel(dimensions=64)
    registry.register(base_model)

    text = "Hello world"
    full_embed = registry.route(text, "demo-hash")
    proj_embed = registry.route(text, "demo-hash", target_dimensions=16)

    print(f"Full dimensions: {len(full_embed)}")
    print(f"Projected dimensions: {len(proj_embed)}")

    # 2. Quantized Cache
    print("\n--- Quantized Cache ---")
    cache = QuantizedCache(max_size=10, ttl_seconds=60)
    # Use projected embedding which is already normalized in adapter
    cache.put("key1", proj_embed)
    cached_embed = cache.get("key1")

    print(f"Original (first 3): {[round(x, 4) for x in proj_embed[:3]]}")
    print(f"Quantized->Dequantized (first 3): {[round(x, 4) for x in cached_embed[:3]]}")
    print(f"Stats: {cache.stats()}")

    # 3. Dynamic Batch Embedder
    print("\n--- Dynamic Batch Embedder ---")
    embedder = DynamicBatchEmbedder(base_model, max_batch_size=5, timeout_ms=50)

    print("Submitting 10 async requests...")
    futures = [embedder.embed_async(f"text {i}") for i in range(10)]

    # Wait for all
    results = [f.result() for f in futures]
    print(f"Successfully processed {len(results)} items.")
    embedder.shutdown()

    print("\n" + "=" * 60)
    print("Demo complete.")
    print("=" * 60)


if __name__ == "__main__":
    main()
