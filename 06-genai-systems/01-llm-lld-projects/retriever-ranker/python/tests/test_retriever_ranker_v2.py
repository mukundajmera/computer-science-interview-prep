import unittest
import sys
import os

# Insert v2-extended directory into sys.path to resolve imports properly
# given the specific folder structure.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'v2-extended')))

from result import RetrievalResult
from rrf_ranker import RRFRanker
from dynamic_alpha import compute_dynamic_alpha, DynamicHybridRetriever
from cross_encoder_mock import CrossEncoderMockRanker
from retriever import DenseRetriever, SparseRetriever


class TestRRFRanker(unittest.TestCase):
    """Tests for Reciprocal Rank Fusion Ranker."""

    def test_rrf_scoring(self):
        """Test that RRF calculates correct reciprocal ranks."""
        ranker = RRFRanker(k=60)
        results = [
            RetrievalResult(chunk_id="d1", content="doc 1", score=0.9, source="dense"),
            RetrievalResult(chunk_id="d2", content="doc 2", score=0.8, source="dense"),
            RetrievalResult(chunk_id="d2", content="doc 2", score=0.95, source="sparse"),
            RetrievalResult(chunk_id="d3", content="doc 3", score=0.5, source="sparse"),
        ]

        ranked = ranker.rank(results, top_k=3)

        # d2 is rank 2 in dense, rank 1 in sparse
        # RRF(d2) = 1/(60+2) + 1/(60+1) = 1/62 + 1/61 ~= 0.016129 + 0.016393 = 0.032522
        # d1 is rank 1 in dense
        # RRF(d1) = 1/(60+1) = 1/61 ~= 0.016393

        self.assertEqual(ranked.results[0].chunk_id, "d2")
        self.assertEqual(ranked.results[1].chunk_id, "d1")
        self.assertEqual(ranked.results[2].chunk_id, "d3")
        self.assertEqual(ranked.results[0].source, "rrf")


class TestDynamicAlpha(unittest.TestCase):
    """Tests for dynamic alpha computation and DynamicHybridRetriever."""

    def test_compute_dynamic_alpha_keywords(self):
        """Short keyword queries should lean towards sparse retrieval (lower alpha)."""
        alpha = compute_dynamic_alpha("fast dog")
        self.assertLess(alpha, 0.5)

    def test_compute_dynamic_alpha_question(self):
        """Question queries should lean towards dense retrieval (higher alpha)."""
        alpha = compute_dynamic_alpha("What is the meaning of life?")
        self.assertGreater(alpha, 0.5)

    def test_dynamic_hybrid_retriever(self):
        """Test DynamicHybridRetriever dynamically sets alpha based on query text."""
        dense = DenseRetriever()
        sparse = SparseRetriever()

        dense.add_document("doc1", "long text answering a complex question", [1.0, 0.0])
        sparse.add_document("doc1", "long text answering a complex question")

        retriever = DynamicHybridRetriever(dense, sparse)

        # Test with keyword query
        retriever.retrieve(([1.0, 0.0], "keyword search"), top_k=1)
        alpha_keyword = retriever.alpha

        # Test with question
        retriever.retrieve(([1.0, 0.0], "Can you explain this detailed topic?"), top_k=1)
        alpha_question = retriever.alpha

        self.assertLess(alpha_keyword, alpha_question)


class TestCrossEncoderMockRanker(unittest.TestCase):
    """Tests for CrossEncoderMockRanker."""

    def test_cross_encoder_mock_scoring(self):
        """Test that the mock cross encoder uses Jaccard similarity."""
        ranker = CrossEncoderMockRanker()
        results = [
            RetrievalResult(chunk_id="d1", content="the quick brown fox", score=0.1, source="dense"),
            RetrievalResult(chunk_id="d2", content="a slow red dog", score=0.9, source="dense"),
        ]

        # Query has high overlap with d1
        query = "quick brown"

        ranked = ranker.rank(results, top_k=2, query=query)

        self.assertEqual(ranked.results[0].chunk_id, "d1")
        self.assertEqual(ranked.results[0].source, "cross_encoder")

    def test_cross_encoder_mock_tuple_query(self):
        """Test that the mock cross encoder handles tuple queries."""
        ranker = CrossEncoderMockRanker()
        results = [
            RetrievalResult(chunk_id="d1", content="the quick brown fox", score=0.1, source="dense"),
        ]

        query = ([1.0, 0.0], "quick")

        ranked = ranker.rank(results, top_k=1, query=query)

        # "quick" in query, "the quick brown fox" in doc
        # union = {"quick", "the", "brown", "fox"}
        # intersection = {"quick"}
        # score = 1 / 4 = 0.25
        self.assertEqual(ranked.results[0].score, 0.25)


if __name__ == "__main__":
    unittest.main()
