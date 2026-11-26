"""
Tests for Retriever–Ranker Pipeline (v1-basic).
"""
import unittest
import sys
import os

# Add v1-basic to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'v1-basic'))


class TestDenseRetriever(unittest.TestCase):
    """Tests for DenseRetriever (cosine similarity)."""

    def setUp(self):
        from retriever import DenseRetriever
        self.DenseRetriever = DenseRetriever
        self.retriever = DenseRetriever()
        self.retriever.add_document("c1", "close match", [1.0, 0.0, 0.0])
        self.retriever.add_document("c2", "medium match", [0.5, 0.5, 0.0])
        self.retriever.add_document("c3", "far match", [0.0, 0.0, 1.0])

    def test_retrieve_returns_sorted_by_score(self):
        """Results should be sorted by descending cosine similarity."""
        results = self.retriever.retrieve([1.0, 0.0, 0.0], top_k=3)
        self.assertEqual(results[0].chunk_id, "c1")
        self.assertGreaterEqual(results[0].score, results[1].score)
        self.assertGreaterEqual(results[1].score, results[2].score)

    def test_top_k_limits_results(self):
        """Retrieve should return at most top_k results."""
        results = self.retriever.retrieve([1.0, 0.0, 0.0], top_k=2)
        self.assertEqual(len(results), 2)

    def test_identical_vector_has_score_near_one(self):
        """A query identical to a stored vector should have score ≈ 1.0."""
        results = self.retriever.retrieve([1.0, 0.0, 0.0], top_k=1)
        self.assertAlmostEqual(results[0].score, 1.0, places=5)

    def test_empty_embedding_raises(self):
        """Adding a document with empty embedding should raise ValueError."""
        with self.assertRaises(ValueError):
            self.retriever.add_document("cx", "text", [])

    def test_empty_query_raises(self):
        """Querying with empty embedding should raise ValueError."""
        with self.assertRaises(ValueError):
            self.retriever.retrieve([], top_k=1)

    def test_dimension_mismatch_raises(self):
        """Querying with mismatched dimensions should raise ValueError."""
        with self.assertRaises(ValueError):
            self.retriever.retrieve([1.0, 0.0], top_k=1)

    def test_invalid_top_k_raises(self):
        """top_k <= 0 should raise ValueError."""
        with self.assertRaises(ValueError):
            self.retriever.retrieve([1.0, 0.0, 0.0], top_k=0)

    def test_source_is_dense(self):
        """Results from DenseRetriever should have source='dense'."""
        results = self.retriever.retrieve([1.0, 0.0, 0.0], top_k=1)
        self.assertEqual(results[0].source, "dense")

    def test_empty_corpus_returns_empty(self):
        """Querying an empty retriever should return an empty list."""
        empty = self.DenseRetriever()
        results = empty.retrieve([1.0, 0.0], top_k=5)
        self.assertEqual(results, [])

    def test_metadata_preserved(self):
        """Metadata added with a document should appear in results."""
        r = self.DenseRetriever()
        r.add_document("m1", "text", [1.0], metadata={"key": "val"})
        results = r.retrieve([1.0], top_k=1)
        self.assertEqual(results[0].metadata["key"], "val")


class TestSparseRetriever(unittest.TestCase):
    """Tests for SparseRetriever (TF-IDF)."""

    def setUp(self):
        from retriever import SparseRetriever
        self.SparseRetriever = SparseRetriever
        self.retriever = SparseRetriever()
        self.retriever.add_document("s1", "dense vector retrieval")
        self.retriever.add_document("s2", "sparse keyword matching")
        self.retriever.add_document("s3", "hybrid dense sparse retrieval")

    def test_bm25_parameters(self):
        """Test BM25 scoring behavior with parameters."""
        results = self.retriever.retrieve("retrieval", top_k=3)
        self.assertGreater(len(results), 0)
        self.assertGreater(results[0].score, 0.0)

    def test_keyword_match_ranks_higher(self):
        """Documents matching query keywords should rank higher."""
        results = self.retriever.retrieve("dense retrieval", top_k=3)
        # s1 ("dense vector retrieval") or s3 should rank above s2
        top_ids = [r.chunk_id for r in results[:2]]
        self.assertIn("s1", top_ids)

    def test_no_match_has_zero_score(self):
        """A document with no matching terms should have score 0."""
        results = self.retriever.retrieve("quantum computing", top_k=3)
        for r in results:
            self.assertAlmostEqual(r.score, 0.0, places=5)

    def test_empty_query_returns_empty(self):
        """An empty query string should return no results."""
        results = self.retriever.retrieve("", top_k=3)
        self.assertEqual(results, [])

    def test_source_is_sparse(self):
        """Results from SparseRetriever should have source='sparse'."""
        results = self.retriever.retrieve("dense", top_k=1)
        self.assertEqual(results[0].source, "sparse")

    def test_size_property(self):
        """Size should reflect the number of indexed documents."""
        self.assertEqual(self.retriever.size, 3)


class TestHybridRetriever(unittest.TestCase):
    """Tests for HybridRetriever (composite alpha blending)."""

    def setUp(self):
        from retriever import DenseRetriever, HybridRetriever, SparseRetriever
        self.HybridRetriever = HybridRetriever
        self.dense = DenseRetriever()
        self.sparse = SparseRetriever()
        # Shared corpus
        self.dense.add_document("h1", "dense retrieval", [1.0, 0.0])
        self.dense.add_document("h2", "sparse matching", [0.0, 1.0])
        self.sparse.add_document("h1", "dense retrieval")
        self.sparse.add_document("h2", "sparse matching")

    def test_hybrid_returns_results(self):
        """Hybrid retrieval should return blended results."""
        hybrid = self.HybridRetriever(self.dense, self.sparse, alpha=0.5)
        results = hybrid.retrieve(([1.0, 0.0], "dense retrieval"), top_k=2)
        self.assertEqual(len(results), 2)

    def test_alpha_one_favors_dense(self):
        """With alpha=1.0 only dense scores contribute."""
        hybrid = self.HybridRetriever(self.dense, self.sparse, alpha=1.0)
        results = hybrid.retrieve(([1.0, 0.0], "sparse matching"), top_k=2)
        # Dense prefers h1 (embedding [1,0] vs query [1,0])
        self.assertEqual(results[0].chunk_id, "h1")

    def test_alpha_zero_favors_sparse(self):
        """With alpha=0.0 only sparse scores contribute."""
        hybrid = self.HybridRetriever(self.dense, self.sparse, alpha=0.0)
        results = hybrid.retrieve(([1.0, 0.0], "sparse matching"), top_k=2)
        # Sparse prefers h2 ("sparse matching" matches query)
        self.assertEqual(results[0].chunk_id, "h2")

    def test_source_is_hybrid(self):
        """Hybrid results should have source='hybrid'."""
        hybrid = self.HybridRetriever(self.dense, self.sparse, alpha=0.5)
        results = hybrid.retrieve(([1.0, 0.0], "dense"), top_k=1)
        self.assertEqual(results[0].source, "hybrid")

    def test_invalid_alpha_raises(self):
        """Alpha outside [0, 1] should raise ValueError."""
        with self.assertRaises(ValueError):
            self.HybridRetriever(self.dense, self.sparse, alpha=1.5)
        with self.assertRaises(ValueError):
            self.HybridRetriever(self.dense, self.sparse, alpha=-0.1)

    def test_invalid_query_format_raises(self):
        """Non-tuple query should raise ValueError."""
        hybrid = self.HybridRetriever(self.dense, self.sparse, alpha=0.5)
        with self.assertRaises(ValueError):
            hybrid.retrieve("just a string", top_k=2)


class TestScoreRanker(unittest.TestCase):
    """Tests for ScoreRanker (sort by score)."""

    def setUp(self):
        from ranker import ScoreRanker
        from result import RetrievalResult
        self.ScoreRanker = ScoreRanker
        self.RetrievalResult = RetrievalResult

    def test_ranks_by_descending_score(self):
        """Results should be ordered by descending score."""
        results = [
            self.RetrievalResult("a", "text-a", score=0.3),
            self.RetrievalResult("b", "text-b", score=0.9),
            self.RetrievalResult("c", "text-c", score=0.6),
        ]
        ranked = self.ScoreRanker().rank(results, top_k=3)
        scores = [r.score for r in ranked]
        self.assertEqual(scores, sorted(scores, reverse=True))

    def test_top_k_truncates(self):
        """Rank should return at most top_k results."""
        results = [
            self.RetrievalResult(f"r{i}", f"text-{i}", score=float(i) / 10)
            for i in range(10)
        ]
        ranked = self.ScoreRanker().rank(results, top_k=3)
        self.assertEqual(len(ranked), 3)

    def test_total_candidates_correct(self):
        """total_candidates should reflect the original count."""
        results = [
            self.RetrievalResult(f"r{i}", f"text-{i}", score=0.5)
            for i in range(7)
        ]
        ranked = self.ScoreRanker().rank(results, top_k=3)
        self.assertEqual(ranked.total_candidates, 7)


class TestWeightedRanker(unittest.TestCase):
    """Tests for WeightedRanker (source-weighted scoring)."""

    def setUp(self):
        from ranker import WeightedRanker
        from result import RetrievalResult
        self.WeightedRanker = WeightedRanker
        self.RetrievalResult = RetrievalResult

    def test_weights_applied(self):
        """Dense source with high weight should rank above sparse with same raw score."""
        results = [
            self.RetrievalResult("d1", "dense", score=0.5, source="dense"),
            self.RetrievalResult("s1", "sparse", score=0.5, source="sparse"),
        ]
        ranker = self.WeightedRanker(weights={"dense": 2.0, "sparse": 1.0})
        ranked = ranker.rank(results, top_k=2)
        self.assertEqual(ranked.results[0].chunk_id, "d1")
        self.assertAlmostEqual(ranked.results[0].score, 1.0)

    def test_default_weight_used(self):
        """Unknown sources should use the default weight."""
        results = [
            self.RetrievalResult("u1", "unknown", score=0.8, source="custom"),
        ]
        ranker = self.WeightedRanker(default_weight=0.5)
        ranked = ranker.rank(results, top_k=1)
        self.assertAlmostEqual(ranked.results[0].score, 0.4)

    def test_empty_results(self):
        """Ranking empty results should return an empty result set."""
        ranker = self.WeightedRanker()
        ranked = ranker.rank([], top_k=5)
        self.assertEqual(len(ranked), 0)


class TestRetrievalPipeline(unittest.TestCase):
    """Tests for RetrievalPipeline (retriever → ranker chain)."""

    def setUp(self):
        from ranker import RetrievalPipeline, ScoreRanker, WeightedRanker
        from retriever import DenseRetriever
        self.DenseRetriever = DenseRetriever
        self.ScoreRanker = ScoreRanker
        self.WeightedRanker = WeightedRanker
        self.RetrievalPipeline = RetrievalPipeline

        self.retriever = DenseRetriever()
        self.retriever.add_document("p1", "first doc", [1.0, 0.0])
        self.retriever.add_document("p2", "second doc", [0.0, 1.0])
        self.retriever.add_document("p3", "third doc", [0.5, 0.5])

    def test_pipeline_returns_ranked_results(self):
        """Pipeline should return a RankedResultSet."""
        from result import RankedResultSet
        pipeline = self.RetrievalPipeline(self.retriever, self.ScoreRanker())
        result_set = pipeline.query([1.0, 0.0], top_k=2)
        self.assertIsInstance(result_set, RankedResultSet)
        self.assertLessEqual(len(result_set), 2)

    def test_pipeline_top_result_is_best_match(self):
        """Pipeline should return the best matching document first."""
        pipeline = self.RetrievalPipeline(self.retriever, self.ScoreRanker())
        result_set = pipeline.query([1.0, 0.0], top_k=1)
        self.assertEqual(result_set.results[0].chunk_id, "p1")

    def test_pipeline_with_weighted_ranker(self):
        """Pipeline should work with any Ranker implementation."""
        ranker = self.WeightedRanker(weights={"dense": 2.0})
        pipeline = self.RetrievalPipeline(self.retriever, ranker)
        result_set = pipeline.query([1.0, 0.0], top_k=3)
        # Weighted scores should be 2× the original
        self.assertGreater(result_set.results[0].score, 0.0)

    def test_pipeline_properties(self):
        """Pipeline should expose retriever and ranker properties."""
        ranker = self.ScoreRanker()
        pipeline = self.RetrievalPipeline(self.retriever, ranker)
        self.assertIs(pipeline.retriever, self.retriever)
        self.assertIs(pipeline.ranker, ranker)


class TestRankedResultSet(unittest.TestCase):
    """Tests for RankedResultSet data class."""

    def setUp(self):
        from result import RankedResultSet, RetrievalResult
        self.RankedResultSet = RankedResultSet
        self.RetrievalResult = RetrievalResult

    def test_top_truncates(self):
        """top(k) should return at most k results."""
        results = [self.RetrievalResult(f"r{i}", f"t{i}") for i in range(5)]
        rs = self.RankedResultSet(results, total_candidates=10)
        top3 = rs.top(3)
        self.assertEqual(len(top3), 3)
        self.assertEqual(top3.total_candidates, 10)

    def test_top_invalid_k_raises(self):
        """top(k) with k <= 0 should raise ValueError."""
        rs = self.RankedResultSet([])
        with self.assertRaises(ValueError):
            rs.top(0)

    def test_len_and_iter(self):
        """RankedResultSet should support len() and iteration."""
        results = [self.RetrievalResult(f"r{i}", f"t{i}") for i in range(3)]
        rs = self.RankedResultSet(results)
        self.assertEqual(len(rs), 3)
        self.assertEqual(list(rs), results)


if __name__ == "__main__":
    unittest.main()
