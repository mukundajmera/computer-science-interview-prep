"""
Tests for LLM Evaluation Harness (v1-basic).
"""
import unittest
import sys
import os

# Add v1-basic to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'v1-basic'))


class TestExactMatchMetric(unittest.TestCase):
    """Tests for ExactMatchMetric."""

    def setUp(self):
        from metrics import ExactMatchMetric
        self.ExactMatchMetric = ExactMatchMetric

    def test_exact_match_identical(self):
        """Identical strings should score 1.0."""
        metric = self.ExactMatchMetric()
        self.assertEqual(metric.score("hello", "hello"), 1.0)

    def test_exact_match_case_insensitive(self):
        """Case-insensitive mode should treat 'Hello' == 'hello'."""
        metric = self.ExactMatchMetric(case_sensitive=False)
        self.assertEqual(metric.score("Hello World", "hello world"), 1.0)

    def test_exact_match_case_sensitive(self):
        """Case-sensitive mode should distinguish 'Hello' from 'hello'."""
        metric = self.ExactMatchMetric(case_sensitive=True)
        self.assertEqual(metric.score("Hello", "hello"), 0.0)

    def test_exact_match_different(self):
        """Different strings should score 0.0."""
        metric = self.ExactMatchMetric()
        self.assertEqual(metric.score("foo", "bar"), 0.0)

    def test_exact_match_empty_strings(self):
        """Two empty strings should score 1.0."""
        metric = self.ExactMatchMetric()
        self.assertEqual(metric.score("", ""), 1.0)

    def test_exact_match_name(self):
        """Metric name should be 'exact_match'."""
        self.assertEqual(self.ExactMatchMetric().name, "exact_match")


class TestNGramOverlapMetric(unittest.TestCase):
    """Tests for NGramOverlapMetric."""

    def setUp(self):
        from metrics import NGramOverlapMetric
        self.NGramOverlapMetric = NGramOverlapMetric

    def test_unigram_perfect_overlap(self):
        """Identical text should score 1.0 for unigrams."""
        metric = self.NGramOverlapMetric(n=1)
        self.assertAlmostEqual(metric.score("the cat sat", "the cat sat"), 1.0)

    def test_unigram_partial_overlap(self):
        """Partial overlap should produce a fractional score."""
        metric = self.NGramOverlapMetric(n=1)
        score = metric.score("the cat sat", "the dog sat")
        # 'the' and 'sat' match (2 out of 3)
        self.assertAlmostEqual(score, 2.0 / 3.0, places=3)

    def test_unigram_no_overlap(self):
        """No shared tokens should score 0.0."""
        metric = self.NGramOverlapMetric(n=1)
        self.assertEqual(metric.score("hello world", "foo bar"), 0.0)

    def test_bigram_overlap(self):
        """Bigram overlap should consider pairs of consecutive words."""
        metric = self.NGramOverlapMetric(n=2)
        score = metric.score("a b c", "a b d")
        # Expected bigrams: (a,b), (b,c). Actual: (a,b), (b,d). Overlap: 1/2
        self.assertAlmostEqual(score, 0.5, places=3)

    def test_ngram_empty_expected(self):
        """Empty expected text should score 1.0 (vacuously true)."""
        metric = self.NGramOverlapMetric(n=1)
        self.assertEqual(metric.score("", "some text"), 1.0)

    def test_ngram_empty_actual(self):
        """Empty actual with non-empty expected should score 0.0."""
        metric = self.NGramOverlapMetric(n=1)
        self.assertEqual(metric.score("some text", ""), 0.0)

    def test_n_larger_than_tokens(self):
        """N-gram size larger than token count gives 1.0 (vacuously true — no expected n-grams)."""
        metric = self.NGramOverlapMetric(n=5)
        # Both texts produce zero n-grams → empty expected → vacuously 1.0
        self.assertEqual(metric.score("short", "short"), 1.0)

    def test_n_larger_expected_has_ngrams(self):
        """When expected has n-grams but actual does not, score should be 0.0."""
        metric = self.NGramOverlapMetric(n=2)
        # Expected: "a b" has one bigram; actual: "c" has none
        self.assertEqual(metric.score("a b", "c"), 0.0)

    def test_invalid_n_raises(self):
        """n < 1 should raise ValueError."""
        with self.assertRaises(ValueError):
            self.NGramOverlapMetric(n=0)

    def test_name_includes_n(self):
        """Metric name should reflect the n-gram size."""
        self.assertEqual(self.NGramOverlapMetric(n=2).name, "2gram_overlap")


class TestKeywordPresenceMetric(unittest.TestCase):
    """Tests for KeywordPresenceMetric."""

    def setUp(self):
        from metrics import KeywordPresenceMetric
        self.KeywordPresenceMetric = KeywordPresenceMetric

    def test_all_keywords_present(self):
        """All keywords present should score 1.0."""
        metric = self.KeywordPresenceMetric(keywords=["cat", "dog"])
        self.assertEqual(metric.score("", "the cat and dog"), 1.0)

    def test_some_keywords_present(self):
        """Partial keyword presence should produce fractional score."""
        metric = self.KeywordPresenceMetric(keywords=["cat", "dog", "bird"])
        score = metric.score("", "the cat is here")
        self.assertAlmostEqual(score, 1.0 / 3.0, places=3)

    def test_no_keywords_present(self):
        """No keywords present should score 0.0."""
        metric = self.KeywordPresenceMetric(keywords=["xyz"])
        self.assertEqual(metric.score("", "hello world"), 0.0)

    def test_case_insensitive(self):
        """Keyword matching should be case-insensitive."""
        metric = self.KeywordPresenceMetric(keywords=["RAG"])
        self.assertEqual(metric.score("", "rag is useful"), 1.0)

    def test_empty_keywords(self):
        """Empty keyword list should score 1.0 (vacuously true)."""
        metric = self.KeywordPresenceMetric(keywords=[])
        self.assertEqual(metric.score("", "anything"), 1.0)

    def test_name(self):
        """Metric name should be 'keyword_presence'."""
        self.assertEqual(
            self.KeywordPresenceMetric(keywords=[]).name, "keyword_presence"
        )


class TestLengthComplianceMetric(unittest.TestCase):
    """Tests for LengthComplianceMetric."""

    def setUp(self):
        from metrics import LengthComplianceMetric
        self.LengthComplianceMetric = LengthComplianceMetric

    def test_within_bounds(self):
        """Output within bounds should score 1.0."""
        metric = self.LengthComplianceMetric(min_length=5, max_length=20)
        self.assertEqual(metric.score("", "hello world"), 1.0)

    def test_too_short(self):
        """Output shorter than min_length should score 0.0."""
        metric = self.LengthComplianceMetric(min_length=100, max_length=200)
        self.assertEqual(metric.score("", "short"), 0.0)

    def test_too_long(self):
        """Output longer than max_length should score 0.0."""
        metric = self.LengthComplianceMetric(min_length=0, max_length=5)
        self.assertEqual(metric.score("", "way too long"), 0.0)

    def test_exact_boundary(self):
        """Output at exact boundary should score 1.0."""
        metric = self.LengthComplianceMetric(min_length=5, max_length=5)
        self.assertEqual(metric.score("", "hello"), 1.0)

    def test_invalid_bounds_raises(self):
        """min_length > max_length should raise ValueError."""
        with self.assertRaises(ValueError):
            self.LengthComplianceMetric(min_length=10, max_length=5)

    def test_negative_bounds_raises(self):
        """Negative bounds should raise ValueError."""
        with self.assertRaises(ValueError):
            self.LengthComplianceMetric(min_length=-1)

    def test_name(self):
        """Metric name should be 'length_compliance'."""
        self.assertEqual(
            self.LengthComplianceMetric().name, "length_compliance"
        )


class TestCustomMetric(unittest.TestCase):
    """Tests for CustomMetric."""

    def setUp(self):
        from metrics import CustomMetric
        self.CustomMetric = CustomMetric

    def test_custom_function(self):
        """Custom function should be called with expected and actual."""
        metric = self.CustomMetric(
            "overlap_ratio",
            lambda exp, act: len(set(exp) & set(act)) / max(len(set(exp)), 1),
        )
        score = metric.score("abc", "abd")
        # Shared chars: a, b → 2/3
        self.assertAlmostEqual(score, 2.0 / 3.0, places=3)

    def test_clamping_high(self):
        """Scores > 1.0 should be clamped to 1.0."""
        metric = self.CustomMetric("over", lambda e, a: 5.0)
        self.assertEqual(metric.score("", ""), 1.0)

    def test_clamping_low(self):
        """Scores < 0.0 should be clamped to 0.0."""
        metric = self.CustomMetric("under", lambda e, a: -3.0)
        self.assertEqual(metric.score("", ""), 0.0)

    def test_name(self):
        """Metric name should be the caller-supplied name."""
        metric = self.CustomMetric("my_metric", lambda e, a: 0.5)
        self.assertEqual(metric.name, "my_metric")


class TestEchoAdapter(unittest.TestCase):
    """Tests for EchoAdapter."""

    def setUp(self):
        from model_adapter import EchoAdapter
        self.adapter = EchoAdapter()

    def test_returns_input(self):
        """EchoAdapter should return the input text unchanged."""
        self.assertEqual(self.adapter.generate("hello"), "hello")

    def test_empty_input(self):
        """EchoAdapter should handle empty input."""
        self.assertEqual(self.adapter.generate(""), "")


class TestStaticAdapter(unittest.TestCase):
    """Tests for StaticAdapter."""

    def setUp(self):
        from model_adapter import StaticAdapter
        self.StaticAdapter = StaticAdapter

    def test_returns_configured_response(self):
        """StaticAdapter should always return the configured response."""
        adapter = self.StaticAdapter(response="fixed")
        self.assertEqual(adapter.generate("any input"), "fixed")
        self.assertEqual(adapter.generate("another input"), "fixed")

    def test_empty_response(self):
        """StaticAdapter should support empty response."""
        adapter = self.StaticAdapter(response="")
        self.assertEqual(adapter.generate("input"), "")


class TestTestSuite(unittest.TestCase):
    """Tests for TestCase and TestSuite."""

    def setUp(self):
        from test_case import TestCase, TestSuite
        self.TestCase = TestCase
        self.TestSuite = TestSuite

    def test_add_case(self):
        """Adding cases should increase suite size."""
        suite = self.TestSuite(name="test")
        suite.add_case(self.TestCase(input_text="q", expected_output="a"))
        self.assertEqual(suite.size(), 1)

    def test_filter_by_tag(self):
        """Filtering should return only cases with matching tag."""
        suite = self.TestSuite(name="test")
        suite.add_case(self.TestCase(
            input_text="q1", expected_output="a1", tags=["alpha"]
        ))
        suite.add_case(self.TestCase(
            input_text="q2", expected_output="a2", tags=["beta"]
        ))
        suite.add_case(self.TestCase(
            input_text="q3", expected_output="a3", tags=["alpha", "beta"]
        ))
        self.assertEqual(len(suite.filter_by_tag("alpha")), 2)
        self.assertEqual(len(suite.filter_by_tag("beta")), 2)
        self.assertEqual(len(suite.filter_by_tag("gamma")), 0)

    def test_empty_suite(self):
        """Empty suite should have size 0."""
        suite = self.TestSuite(name="empty")
        self.assertEqual(suite.size(), 0)

    def test_case_id_auto_generated(self):
        """TestCase should auto-generate a UUID case_id."""
        tc = self.TestCase(input_text="q", expected_output="a")
        self.assertTrue(len(tc.case_id) > 0)

    def test_case_id_unique(self):
        """Each TestCase should have a unique case_id."""
        tc1 = self.TestCase(input_text="q", expected_output="a")
        tc2 = self.TestCase(input_text="q", expected_output="a")
        self.assertNotEqual(tc1.case_id, tc2.case_id)

    def test_default_tags_and_metadata(self):
        """Tags and metadata should default to empty."""
        tc = self.TestCase(input_text="q", expected_output="a")
        self.assertEqual(tc.tags, [])
        self.assertEqual(tc.metadata, {})


class TestEvaluationRunner(unittest.TestCase):
    """Tests for EvaluationRunner."""

    def setUp(self):
        from metrics import ExactMatchMetric, NGramOverlapMetric
        from model_adapter import EchoAdapter, StaticAdapter
        from runner import EvaluationRunner
        from test_case import TestCase, TestSuite
        self.ExactMatchMetric = ExactMatchMetric
        self.NGramOverlapMetric = NGramOverlapMetric
        self.EchoAdapter = EchoAdapter
        self.StaticAdapter = StaticAdapter
        self.EvaluationRunner = EvaluationRunner
        self.TestCase = TestCase
        self.TestSuite = TestSuite

    def test_evaluate_case_echo_exact_match(self):
        """Echo adapter with exact match should pass when input == expected."""
        tc = self.TestCase(input_text="hello", expected_output="hello")
        runner = self.EvaluationRunner(
            adapter=self.EchoAdapter(),
            metrics=[self.ExactMatchMetric()],
        )
        result = runner.evaluate_case(tc, pass_threshold=0.5)
        self.assertTrue(result.passed)
        self.assertEqual(result.scores["exact_match"], 1.0)
        self.assertEqual(result.actual_output, "hello")

    def test_evaluate_case_static_mismatch(self):
        """Static adapter returning wrong answer should fail exact match."""
        tc = self.TestCase(input_text="q", expected_output="correct answer")
        runner = self.EvaluationRunner(
            adapter=self.StaticAdapter(response="wrong answer"),
            metrics=[self.ExactMatchMetric()],
        )
        result = runner.evaluate_case(tc, pass_threshold=0.5)
        self.assertFalse(result.passed)
        self.assertEqual(result.scores["exact_match"], 0.0)

    def test_evaluate_case_has_duration(self):
        """Evaluation result should record a positive duration."""
        tc = self.TestCase(input_text="q", expected_output="a")
        runner = self.EvaluationRunner(
            adapter=self.EchoAdapter(), metrics=[self.ExactMatchMetric()]
        )
        result = runner.evaluate_case(tc)
        self.assertGreater(result.duration_ms, 0.0)

    def test_evaluate_case_no_metrics(self):
        """With no metrics, scores should be empty and case should fail."""
        tc = self.TestCase(input_text="q", expected_output="a")
        runner = self.EvaluationRunner(
            adapter=self.EchoAdapter(), metrics=[]
        )
        result = runner.evaluate_case(tc, pass_threshold=0.5)
        self.assertEqual(result.scores, {})
        self.assertFalse(result.passed)

    def test_evaluate_suite_pass_rate(self):
        """Suite evaluation should compute correct pass rate."""
        suite = self.TestSuite(name="test")
        suite.add_case(self.TestCase(input_text="yes", expected_output="yes"))
        suite.add_case(self.TestCase(input_text="no", expected_output="different"))
        runner = self.EvaluationRunner(
            adapter=self.EchoAdapter(), metrics=[self.ExactMatchMetric()]
        )
        report = runner.evaluate_suite(suite, pass_threshold=0.5)
        # First case passes (echo matches), second fails
        self.assertEqual(report.pass_rate, 0.5)

    def test_evaluate_suite_aggregate_scores(self):
        """Aggregate scores should be the mean across all cases."""
        suite = self.TestSuite(name="test")
        suite.add_case(self.TestCase(input_text="a", expected_output="a"))
        suite.add_case(self.TestCase(input_text="b", expected_output="b"))
        runner = self.EvaluationRunner(
            adapter=self.EchoAdapter(), metrics=[self.ExactMatchMetric()]
        )
        report = runner.evaluate_suite(suite)
        # Both cases match exactly → mean = 1.0
        self.assertEqual(report.aggregate_scores["exact_match"], 1.0)

    def test_evaluate_suite_total_duration(self):
        """Total duration should be sum of individual durations."""
        suite = self.TestSuite(name="test")
        suite.add_case(self.TestCase(input_text="a", expected_output="a"))
        suite.add_case(self.TestCase(input_text="b", expected_output="b"))
        runner = self.EvaluationRunner(
            adapter=self.EchoAdapter(), metrics=[self.ExactMatchMetric()]
        )
        report = runner.evaluate_suite(suite)
        expected_total = sum(r.duration_ms for r in report.results)
        self.assertAlmostEqual(report.total_duration_ms, expected_total, places=3)

    def test_evaluate_suite_has_timestamp(self):
        """Report should have an ISO-format timestamp."""
        suite = self.TestSuite(name="test")
        suite.add_case(self.TestCase(input_text="a", expected_output="a"))
        runner = self.EvaluationRunner(
            adapter=self.EchoAdapter(), metrics=[self.ExactMatchMetric()]
        )
        report = runner.evaluate_suite(suite)
        self.assertIn("T", report.timestamp)  # ISO-8601 contains 'T'

    def test_evaluate_empty_suite(self):
        """Empty suite should produce an empty report with 0.0 pass rate."""
        suite = self.TestSuite(name="empty")
        runner = self.EvaluationRunner(
            adapter=self.EchoAdapter(), metrics=[self.ExactMatchMetric()]
        )
        report = runner.evaluate_suite(suite)
        self.assertEqual(len(report.results), 0)
        self.assertEqual(report.pass_rate, 0.0)
        self.assertEqual(report.aggregate_scores, {})

    def test_evaluate_suite_pass_threshold(self):
        """High threshold should cause more failures."""
        suite = self.TestSuite(name="test")
        suite.add_case(self.TestCase(
            input_text="hello world", expected_output="hello world"
        ))
        runner = self.EvaluationRunner(
            adapter=self.EchoAdapter(),
            metrics=[self.ExactMatchMetric(), self.NGramOverlapMetric(n=1)],
        )
        # Threshold 0.5 — should pass (both metrics = 1.0)
        report_low = runner.evaluate_suite(suite, pass_threshold=0.5)
        self.assertEqual(report_low.pass_rate, 1.0)


class TestEvaluationReportComparison(unittest.TestCase):
    """Tests for compare_reports regression detection."""

    def setUp(self):
        from metrics import ExactMatchMetric, NGramOverlapMetric
        from model_adapter import EchoAdapter, StaticAdapter
        from runner import EvaluationRunner
        from test_case import TestCase, TestSuite
        self.ExactMatchMetric = ExactMatchMetric
        self.NGramOverlapMetric = NGramOverlapMetric
        self.EchoAdapter = EchoAdapter
        self.StaticAdapter = StaticAdapter
        self.EvaluationRunner = EvaluationRunner
        self.TestCase = TestCase
        self.TestSuite = TestSuite

    def _make_suite(self):
        suite = self.TestSuite(name="compare-test")
        suite.add_case(self.TestCase(
            input_text="hello", expected_output="hello"
        ))
        suite.add_case(self.TestCase(
            input_text="world", expected_output="world"
        ))
        return suite

    def test_regression_detected(self):
        """Switching from echo (perfect) to static (wrong) should show negative delta."""
        suite = self._make_suite()
        metrics = [self.ExactMatchMetric()]
        baseline = self.EvaluationRunner(
            self.EchoAdapter(), metrics
        ).evaluate_suite(suite)
        current = self.EvaluationRunner(
            self.StaticAdapter(response="nope"), metrics
        ).evaluate_suite(suite)
        comparison = self.EvaluationRunner.compare_reports(baseline, current)
        self.assertIn("exact_match", comparison)
        self.assertLess(comparison["exact_match"]["delta"], 0.0)

    def test_improvement_detected(self):
        """Switching from static (wrong) to echo (perfect) should show positive delta."""
        suite = self._make_suite()
        metrics = [self.ExactMatchMetric()]
        baseline = self.EvaluationRunner(
            self.StaticAdapter(response="nope"), metrics
        ).evaluate_suite(suite)
        current = self.EvaluationRunner(
            self.EchoAdapter(), metrics
        ).evaluate_suite(suite)
        comparison = self.EvaluationRunner.compare_reports(baseline, current)
        self.assertGreater(comparison["exact_match"]["delta"], 0.0)

    def test_no_change(self):
        """Same adapter for both should show zero delta."""
        suite = self._make_suite()
        metrics = [self.ExactMatchMetric()]
        runner = self.EvaluationRunner(self.EchoAdapter(), metrics)
        baseline = runner.evaluate_suite(suite)
        current = runner.evaluate_suite(suite)
        comparison = self.EvaluationRunner.compare_reports(baseline, current)
        self.assertAlmostEqual(comparison["exact_match"]["delta"], 0.0)

    def test_comparison_includes_all_metrics(self):
        """Comparison should include all metrics from both reports."""
        suite = self._make_suite()
        m1 = [self.ExactMatchMetric()]
        m2 = [self.ExactMatchMetric(), self.NGramOverlapMetric(n=1)]
        baseline = self.EvaluationRunner(
            self.EchoAdapter(), m1
        ).evaluate_suite(suite)
        current = self.EvaluationRunner(
            self.EchoAdapter(), m2
        ).evaluate_suite(suite)
        comparison = self.EvaluationRunner.compare_reports(baseline, current)
        self.assertIn("exact_match", comparison)
        self.assertIn("1gram_overlap", comparison)


class TestEdgeCases(unittest.TestCase):
    """Edge case tests for the evaluation harness."""

    def setUp(self):
        from metrics import ExactMatchMetric, LengthComplianceMetric
        from model_adapter import EchoAdapter
        from runner import EvaluationRunner
        from test_case import TestCase, TestSuite
        self.ExactMatchMetric = ExactMatchMetric
        self.LengthComplianceMetric = LengthComplianceMetric
        self.EchoAdapter = EchoAdapter
        self.EvaluationRunner = EvaluationRunner
        self.TestCase = TestCase
        self.TestSuite = TestSuite

    def test_empty_input_and_expected(self):
        """Empty input and expected should still produce a result."""
        tc = self.TestCase(input_text="", expected_output="")
        runner = self.EvaluationRunner(
            adapter=self.EchoAdapter(), metrics=[self.ExactMatchMetric()]
        )
        result = runner.evaluate_case(tc)
        self.assertEqual(result.scores["exact_match"], 1.0)

    def test_empty_expected_non_empty_actual(self):
        """Empty expected with non-empty actual should score 0.0 for exact match."""
        tc = self.TestCase(input_text="something", expected_output="")
        runner = self.EvaluationRunner(
            adapter=self.EchoAdapter(), metrics=[self.ExactMatchMetric()]
        )
        result = runner.evaluate_case(tc)
        self.assertEqual(result.scores["exact_match"], 0.0)

    def test_threshold_zero_all_pass(self):
        """Pass threshold of 0.0 should make all cases pass."""
        suite = self.TestSuite(name="test")
        suite.add_case(self.TestCase(
            input_text="wrong", expected_output="right"
        ))
        runner = self.EvaluationRunner(
            adapter=self.EchoAdapter(), metrics=[self.ExactMatchMetric()]
        )
        report = runner.evaluate_suite(suite, pass_threshold=0.0)
        self.assertEqual(report.pass_rate, 1.0)

    def test_threshold_above_one_all_fail(self):
        """Pass threshold > 1.0 should make all cases fail."""
        suite = self.TestSuite(name="test")
        suite.add_case(self.TestCase(
            input_text="hello", expected_output="hello"
        ))
        runner = self.EvaluationRunner(
            adapter=self.EchoAdapter(), metrics=[self.ExactMatchMetric()]
        )
        report = runner.evaluate_suite(suite, pass_threshold=1.1)
        self.assertEqual(report.pass_rate, 0.0)

    def test_unicode_text(self):
        """Unicode characters should be handled correctly."""
        tc = self.TestCase(input_text="こんにちは", expected_output="こんにちは")
        runner = self.EvaluationRunner(
            adapter=self.EchoAdapter(), metrics=[self.ExactMatchMetric()]
        )
        result = runner.evaluate_case(tc)
        self.assertEqual(result.scores["exact_match"], 1.0)

    def test_multiple_metrics(self):
        """Multiple metrics should all be scored independently."""
        tc = self.TestCase(input_text="hello world", expected_output="hello world")
        runner = self.EvaluationRunner(
            adapter=self.EchoAdapter(),
            metrics=[
                self.ExactMatchMetric(),
                self.LengthComplianceMetric(min_length=1, max_length=100),
            ],
        )
        result = runner.evaluate_case(tc)
        self.assertEqual(len(result.scores), 2)
        self.assertIn("exact_match", result.scores)
        self.assertIn("length_compliance", result.scores)


class TestDomainMetrics(unittest.TestCase):
    """Tests for domain-specific metric helpers."""

    def setUp(self):
        from domain_metrics import (
            ClassificationMetrics,
            HeuristicGenerationMetrics,
            RankingMetrics,
        )
        self.ClassificationMetrics = ClassificationMetrics
        self.RankingMetrics = RankingMetrics
        self.HeuristicGenerationMetrics = HeuristicGenerationMetrics

    def test_classification_precision_recall_f1(self):
        """Precision/recall/F1 should match expected deterministic values."""
        y_true = [1, 0, 1, 1, 0]
        y_pred = [1, 1, 1, 0, 0]
        precision = self.ClassificationMetrics.precision(y_true, y_pred)
        recall = self.ClassificationMetrics.recall(y_true, y_pred)
        f1 = self.ClassificationMetrics.f1(y_true, y_pred)
        self.assertAlmostEqual(precision, 2.0 / 3.0, places=5)
        self.assertAlmostEqual(recall, 2.0 / 3.0, places=5)
        self.assertAlmostEqual(f1, 2.0 / 3.0, places=5)

    def test_classification_zero_denominator(self):
        """Metrics should return 0.0 when denominator is zero."""
        y_true = [0, 0, 0]
        y_pred = [0, 0, 0]
        self.assertEqual(self.ClassificationMetrics.precision(y_true, y_pred), 0.0)
        self.assertEqual(self.ClassificationMetrics.recall(y_true, y_pred), 0.0)
        self.assertEqual(self.ClassificationMetrics.f1(y_true, y_pred), 0.0)

    def test_ranking_mrr(self):
        """MRR should average reciprocal ranks across rows."""
        rows = [
            [0, 1, 0],  # rr = 1/2
            [0, 0, 1],  # rr = 1/3
            [1, 0, 0],  # rr = 1
        ]
        mrr = self.RankingMetrics.mrr(rows)
        self.assertAlmostEqual(mrr, (1.0 / 2 + 1.0 / 3 + 1.0) / 3, places=6)

    def test_ranking_ndcg(self):
        """NDCG should be in [0, 1] and equal 1.0 for ideal ranking."""
        ideal = [3, 2, 1]
        self.assertAlmostEqual(self.RankingMetrics.ndcg(ideal), 1.0, places=6)
        non_ideal = [1, 3, 2]
        ndcg = self.RankingMetrics.ndcg(non_ideal)
        self.assertGreaterEqual(ndcg, 0.0)
        self.assertLessEqual(ndcg, 1.0)

    def test_generation_heuristics(self):
        """Heuristic generation metrics should be deterministic."""
        gm = self.HeuristicGenerationMetrics()
        faith = gm.faithfulness(
            "refund policy allows returns",
            "our refund policy allows returns within 30 days",
        )
        rel = gm.relevance("refund policy", "the refund policy is 30 days")
        self.assertGreater(faith, 0.0)
        self.assertGreater(rel, 0.0)


if __name__ == "__main__":
    unittest.main()
