"""
Tests for v3-optimized features of the Embedding Service.
"""

import sys
import os
import asyncio
import time
import pytest
from typing import List

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'v3-optimized')))

from product_quantizer import ProductQuantizer
from dynamic_batcher import DynamicBatcher


def test_product_quantizer_initialization():
    # Valid initialization
    pq = ProductQuantizer(dimensions=128, num_subvectors=16, codebook_size=256)
    assert pq.dimensions == 128
    assert pq.num_subvectors == 16
    assert pq.subvector_dim == 8

    # Invalid dimensions (not divisible)
    with pytest.raises(ValueError):
        ProductQuantizer(dimensions=130, num_subvectors=16)

    # Invalid codebook size
    with pytest.raises(ValueError):
        ProductQuantizer(dimensions=128, num_subvectors=16, codebook_size=300)


def test_product_quantizer_encode_decode():
    pq = ProductQuantizer(dimensions=128, num_subvectors=16, codebook_size=256)

    # Create a simple vector
    vector = [(i / 128.0) * 2 - 1.0 for i in range(128)]

    # Encode
    encoded = pq.encode(vector)
    assert len(encoded) == 16
    assert isinstance(encoded, bytes)

    # Decode
    decoded = pq.decode(encoded)
    assert len(decoded) == 128

    # Test invalid vector size
    with pytest.raises(ValueError):
        pq.encode(vector[:100])

    # Test invalid bytes length
    with pytest.raises(ValueError):
        pq.decode(encoded[:10])


def test_dynamic_batcher_size_flush():
    """Test that the batcher flushes when it reaches max_batch_size."""
    batch_calls = []

    async def process_batch(texts: List[str]) -> List[List[float]]:
        batch_calls.append(len(texts))
        return [[float(len(t))] for t in texts]

    async def run_test():
        batcher = DynamicBatcher(process_batch_fn=process_batch, max_batch_size=3, timeout_ms=500)
        batcher.start()

        # Submit 3 items immediately
        tasks = [batcher.submit(f"text{i}") for i in range(3)]

        results = await asyncio.gather(*tasks)

        assert len(results) == 3
        assert batch_calls == [3]

        await batcher.stop()

    asyncio.run(run_test())


def test_dynamic_batcher_timeout_flush():
    """Test that the batcher flushes when the timeout expires."""
    batch_calls = []

    async def process_batch(texts: List[str]) -> List[List[float]]:
        batch_calls.append(len(texts))
        return [[float(len(t))] for t in texts]

    async def run_test():
        batcher = DynamicBatcher(process_batch_fn=process_batch, max_batch_size=10, timeout_ms=100)
        batcher.start()

        start_time = time.time()

        # Submit only 1 item, so it must wait for the timeout
        res = await batcher.submit("text")

        end_time = time.time()

        assert len(res) == 1
        assert batch_calls == [1]

        # Should have waited roughly 100ms
        assert end_time - start_time >= 0.09

        await batcher.stop()

    asyncio.run(run_test())


def test_dynamic_batcher_stop_flush():
    """Test that stopping the batcher flushes the remaining queue."""
    batch_calls = []

    async def process_batch(texts: List[str]) -> List[List[float]]:
        batch_calls.append(len(texts))
        return [[float(len(t))] for t in texts]

    async def run_test():
        batcher = DynamicBatcher(process_batch_fn=process_batch, max_batch_size=10, timeout_ms=500)
        batcher.start()

        # Submit 2 items (less than max_batch_size, more than timeout)
        task1 = asyncio.create_task(batcher.submit("text1"))
        task2 = asyncio.create_task(batcher.submit("text2"))

        # Yield to event loop to allow tasks to add to queue before stopping
        await asyncio.sleep(0.01)

        # Stop immediately, which should trigger a flush of the 2 items
        await batcher.stop()

        res1 = await task1
        res2 = await task2

        assert res1 == [5.0]
        assert res2 == [5.0]
        assert batch_calls == [2]

    asyncio.run(run_test())

def test_dynamic_batcher_error_propagation():
    """Test that exceptions in the process function are propagated to futures."""

    async def failing_process(texts: List[str]) -> List[List[float]]:
        raise ValueError("Batch processing failed!")

    async def run_test():
        batcher = DynamicBatcher(process_batch_fn=failing_process, max_batch_size=2, timeout_ms=100)
        batcher.start()

        with pytest.raises(ValueError, match="Batch processing failed!"):
            await batcher.submit("text1")

        await batcher.stop()

    asyncio.run(run_test())
