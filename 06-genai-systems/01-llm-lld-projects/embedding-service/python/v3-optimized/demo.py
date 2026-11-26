"""
Embedding Service demo — v3 optimized.

Showcases dynamic asyncio batching and product quantization.
"""

import sys
import os
import asyncio
import time
from typing import List

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..')))

from product_quantizer import ProductQuantizer
from dynamic_batcher import DynamicBatcher

# Dummy async batch process function
async def process_batch(texts: List[str]) -> List[List[float]]:
    # Simulate network/GPU latency
    await asyncio.sleep(0.1)

    results = []
    for text in texts:
        # Create a simple deterministic embedding
        # e.g., a 128-dimensional vector based on text length and some arbitrary values
        dim = 128
        val = len(text) / 100.0
        vec = [val * (i % 5) / 5.0 for i in range(dim)]
        results.append(vec)

    print(f"Processed batch of size {len(texts)}")
    return results

async def main():
    print("=" * 60)
    print("EMBEDDING SERVICE DEMO (v3-optimized)")
    print("=" * 60)

    # 1. Product Quantizer
    print("\n--- Product Quantizer ---")
    dimensions = 128
    num_subvectors = 16
    quantizer = ProductQuantizer(dimensions=dimensions, num_subvectors=num_subvectors)

    # Create a random float32 vector
    original_vector = [((i % 10) / 10.0) * 2 - 1.0 for i in range(dimensions)]

    encoded = quantizer.encode(original_vector)
    decoded = quantizer.decode(encoded)

    print(f"Original vector dimensions: {len(original_vector)}")
    print(f"Original vector size (approx bytes): {len(original_vector) * 4}")
    print(f"Encoded size (bytes): {len(encoded)}")
    print(f"Original (first 5): {[round(x, 4) for x in original_vector[:5]]}")
    print(f"Decoded (first 5):  {[round(x, 4) for x in decoded[:5]]}")
    print(f"Encoded representation: {encoded.hex()}")

    # 2. Dynamic Batcher
    print("\n--- Dynamic Batcher ---")
    batcher = DynamicBatcher(process_batch_fn=process_batch, max_batch_size=5, timeout_ms=50)
    batcher.start()

    print("Submitting 12 async requests concurrently...")

    async def submit_request(i):
        text = f"demo text {i}"
        return await batcher.submit(text)

    start_time = time.time()

    # Submit requests
    tasks = [submit_request(i) for i in range(12)]
    results = await asyncio.gather(*tasks)

    end_time = time.time()

    print(f"Successfully processed {len(results)} items in {end_time - start_time:.4f} seconds.")
    print("Expected 3 batches (5, 5, 2).")

    await batcher.stop()

    print("\n" + "=" * 60)
    print("Demo complete.")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
