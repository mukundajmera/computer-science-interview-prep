import pytest
import asyncio
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'v3-optimized')))

from retriever import DenseRetriever, SparseRetriever
from async_pipeline import AsyncHybridRetriever, AsyncRetrievalPipeline
from rrf_fusion import RRFFusionRanker
from result import RetrievalResult

class TestAsyncHybridRetriever:
    def test_async_retrieve(self):
        dense = DenseRetriever()
        sparse = SparseRetriever()

        dense.add_document("doc1", "test one", [1.0, 0.0], {})
        sparse.add_document("doc1", "test one", {})

        dense.add_document("doc2", "test two", [0.0, 1.0], {})
        sparse.add_document("doc2", "test two", {})

        retriever = AsyncHybridRetriever(dense, sparse, alpha=0.5)

        query = ([1.0, 0.0], "test one")

        async def run_test():
            results = await retriever.retrieve(query, top_k=2)
            assert len(results) == 2
            assert results[0].chunk_id == "doc1"
            assert results[0].source == "hybrid"

        asyncio.run(run_test())

    def test_alpha_blending(self):
        dense = DenseRetriever()
        sparse = SparseRetriever()

        # doc1 matches perfectly on dense
        dense.add_document("doc1", "test one", [1.0, 0.0], {})
        sparse.add_document("doc1", "unrelated", {})

        # doc2 matches perfectly on sparse
        dense.add_document("doc2", "unrelated", [0.0, 1.0], {})
        sparse.add_document("doc2", "test two", {})

        # Alpha 1.0 favors dense
        retriever_dense_biased = AsyncHybridRetriever(dense, sparse, alpha=1.0)

        query = ([1.0, 0.0], "test two") # dense likes doc1, sparse likes doc2

        async def run_test_dense():
            results = await retriever_dense_biased.retrieve(query, top_k=2)
            assert results[0].chunk_id == "doc1"

        asyncio.run(run_test_dense())

        # Alpha 0.0 favors sparse
        retriever_sparse_biased = AsyncHybridRetriever(dense, sparse, alpha=0.0)
        async def run_test_sparse():
            results = await retriever_sparse_biased.retrieve(query, top_k=2)
            assert results[0].chunk_id == "doc2"

        asyncio.run(run_test_sparse())


class TestRRFFusionRanker:
    def test_rrf_normalization(self):
        ranker = RRFFusionRanker(k=60)
        results = [
            RetrievalResult(chunk_id="doc1", content="", score=0.9, source="dense"),
            RetrievalResult(chunk_id="doc2", content="", score=0.8, source="dense"),
            RetrievalResult(chunk_id="doc1", content="", score=0.9, source="sparse"),
            RetrievalResult(chunk_id="doc3", content="", score=0.7, source="sparse"),
        ]

        ranked = ranker.rank(results, top_k=3)

        assert len(ranked.results) == 3

        # doc1 should be rank 1
        assert ranked.results[0].chunk_id == "doc1"
        assert ranked.results[0].score == 1.0 # normalized

        # Check source is updated
        assert ranked.results[0].source == "rrf"


class TestAsyncRetrievalPipeline:
    def test_async_pipeline(self):
        dense = DenseRetriever()
        sparse = SparseRetriever()

        dense.add_document("doc1", "hello world", [1.0, 0.0], {})
        sparse.add_document("doc1", "hello world", {})

        retriever = AsyncHybridRetriever(dense, sparse, alpha=0.5)
        ranker = RRFFusionRanker()

        pipeline = AsyncRetrievalPipeline(retriever, ranker)

        query = ([1.0, 0.0], "hello world")

        async def run_test():
            ranked = await pipeline.query(query, top_k=1)
            assert len(ranked.results) == 1
            assert ranked.results[0].chunk_id == "doc1"
            assert ranked.results[0].source == "rrf"

        asyncio.run(run_test())

    def test_async_pipeline_truncation(self):
        dense = DenseRetriever()
        sparse = SparseRetriever()

        for i in range(5):
            dense.add_document(f"doc{i}", f"test {i}", [1.0, 0.0], {})
            sparse.add_document(f"doc{i}", f"test {i}", {})

        retriever = AsyncHybridRetriever(dense, sparse, alpha=0.5)
        ranker = RRFFusionRanker()

        pipeline = AsyncRetrievalPipeline(retriever, ranker)

        query = ([1.0, 0.0], "test 1")

        async def run_test():
            ranked = await pipeline.query(query, top_k=2)
            assert len(ranked.results) == 2
            assert ranked.total_candidates == 5 # fetch_k is top_k * 3, capped at available corpus size

        asyncio.run(run_test())
