import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
import importlib

models = importlib.import_module('v2-extended.models')
tail_sampler = importlib.import_module('v2-extended.tail_sampler')
dag_assembler = importlib.import_module('v2-extended.dag_assembler')

Span = models.Span
TailSampler = tail_sampler.TailSampler
DAGAssembler = dag_assembler.DAGAssembler

NS = 1_000_000_000  # one second in nanoseconds


class TestDistributedTracingV2Parity(unittest.TestCase):
    """The v1 test scenarios re-run against v2 to lock in v1 behavior."""

    def test_tail_sampler_drops_normal_trace(self):
        sampler = TailSampler(NS)
        sampler.ingest(Span("trace1", "span1", None, "svc1", "op1", 0, 500_000_000, {}, False))
        self.assertEqual(len(sampler.evaluate_window("trace1")), 0)

    def test_tail_sampler_keeps_error_trace(self):
        sampler = TailSampler(NS)
        sampler.ingest(Span("trace2", "span1", None, "svc1", "op1", 0, 500_000_000, {}, False))
        sampler.ingest(Span("trace2", "span2", "span1", "svc2", "op2", 0, 100_000_000, {}, True))
        self.assertEqual(len(sampler.evaluate_window("trace2")), 2)

    def test_tail_sampler_keeps_slow_trace(self):
        sampler = TailSampler(NS)
        sampler.ingest(Span("trace3", "span1", None, "svc1", "op1", 0, 1_500_000_000, {}, False))
        self.assertEqual(len(sampler.evaluate_window("trace3")), 1)

    def test_dag_assembler(self):
        assembler = DAGAssembler()
        spans = [
            Span("trace4", "root", None, "svc1", "op1", 0, 1000, {}, False),
            Span("trace4", "child1", "root", "svc2", "op2", 100, 400, {}, False),
            Span("trace4", "child2", "root", "svc3", "op3", 500, 300, {}, False),
        ]
        roots = assembler.assemble(spans)
        self.assertEqual(len(roots), 1)
        self.assertEqual(roots[0].span.span_id, "root")
        self.assertEqual(len(roots[0].children), 2)

    def test_ingestion_worker_crash_loses_in_memory_spans(self):
        sampler = TailSampler(NS)
        sampler.ingest(Span("trace5", "span1", None, "svc1", "op1", 0, 1_500_000_000, {}, False))
        sampler.crash()
        self.assertEqual(len(sampler.evaluate_window("trace5")), 0)


class TestDistributedTracingV2(unittest.TestCase):
    """Tests for the three named v2 improvements."""

    # --- Improvement #2: deduplication of at-least-once replays ---

    def test_ingest_deduplicates_replays(self):
        sampler = TailSampler(NS)
        span = Span("t", "s1", None, "svc", "op", 0, 100, {}, False)
        self.assertTrue(sampler.ingest(span))
        self.assertFalse(sampler.ingest(Span("t", "s1", None, "svc", "op", 0, 100, {}, False)))
        # The window holds one span, not two; a normal trace still drops.
        self.assertEqual(len(sampler.buffers["t"]), 1)

    def test_dedup_applies_inside_kept_trace(self):
        sampler = TailSampler(NS)
        sampler.ingest(Span("t", "s1", None, "svc", "op", 0, 100, {}, True))
        sampler.ingest(Span("t", "s1", None, "svc", "op", 0, 100, {}, True))
        kept = sampler.evaluate_window("t")
        self.assertEqual(len(kept), 1)

    def test_dag_deduplicates_duplicate_span_ids(self):
        assembler = DAGAssembler()
        spans = [
            Span("t", "root", None, "svc1", "op1", 0, 1000, {}, False),
            Span("t", "child", "root", "svc2", "op2", 100, 400, {}, False),
            Span("t", "child", "root", "svc2", "op2", 100, 400, {}, False),
        ]
        roots = assembler.assemble(spans)
        self.assertEqual(len(roots), 1)
        self.assertEqual(len(roots[0].children), 1)

    # --- Improvement #1: clock-skew adjustment ---

    def test_child_starting_before_parent_is_clamped(self):
        assembler = DAGAssembler()
        spans = [
            Span("t", "root", None, "svc1", "op1", 1000, 1000, {}, False),
            Span("t", "child", "root", "svc2", "op2", 500, 400, {}, False),
        ]
        roots = assembler.assemble(spans)
        child = roots[0].children[0]
        self.assertEqual(roots[0].adjusted_start_ns, 1000)
        self.assertEqual(roots[0].adjusted_end_ns, 2000)
        self.assertEqual(child.adjusted_start_ns, 1000)  # clamped up from 500
        self.assertEqual(child.adjusted_end_ns, 1000)

    def test_child_ending_after_parent_is_clamped(self):
        assembler = DAGAssembler()
        spans = [
            Span("t", "root", None, "svc1", "op1", 1000, 1000, {}, False),
            Span("t", "child", "root", "svc2", "op2", 1200, 2000, {}, False),
        ]
        roots = assembler.assemble(spans)
        child = roots[0].children[0]
        self.assertEqual(child.adjusted_start_ns, 1200)
        self.assertEqual(child.adjusted_end_ns, 2000)  # clamped down from 3200

    def test_well_formed_child_keeps_original_times(self):
        assembler = DAGAssembler()
        spans = [
            Span("t", "root", None, "svc1", "op1", 1000, 1000, {}, False),
            Span("t", "child", "root", "svc2", "op2", 1100, 400, {}, False),
        ]
        roots = assembler.assemble(spans)
        child = roots[0].children[0]
        self.assertEqual(child.adjusted_start_ns, 1100)
        self.assertEqual(child.adjusted_end_ns, 1500)

    def test_self_parent_span_treated_as_root(self):
        assembler = DAGAssembler()
        roots = assembler.assemble([
            Span("t", "loop", "loop", "svc1", "op1", 0, 100, {}, False),
        ])
        self.assertEqual(len(roots), 1)
        self.assertEqual(len(roots[0].children), 0)

    # --- Improvement #3: windowed sampling with an injectable clock ---

    def make_clocked_sampler(self):
        now = [0]
        sampler = TailSampler(NS, clock=lambda: now[0])
        return sampler, now

    def test_flush_expired_evaluates_old_windows(self):
        sampler, now = self.make_clocked_sampler()
        sampler.ingest(Span("t", "s1", None, "svc", "op", 0, 100, {}, True))
        now[0] = 31 * NS
        flushed = sampler.flush_expired()
        self.assertEqual(list(flushed.keys()), ["t"])
        self.assertEqual(len(flushed["t"]), 1)
        self.assertEqual(sampler.evaluate_window("t"), [])  # already closed

    def test_flush_leaves_fresh_windows_buffered(self):
        sampler, now = self.make_clocked_sampler()
        sampler.ingest(Span("t", "s1", None, "svc", "op", 0, 100, {}, False))
        now[0] = 10 * NS
        self.assertEqual(sampler.flush_expired(), {})
        self.assertEqual(len(sampler.buffers["t"]), 1)

    def test_late_span_opens_new_fragment_window(self):
        sampler, now = self.make_clocked_sampler()
        sampler.ingest(Span("t", "s1", None, "svc", "op", 0, 100, {}, False))
        self.assertEqual(sampler.evaluate_window("t"), [])  # normal, dropped
        # A late span for the same trace is accepted as a new fragment and
        # judged on its own merits.
        self.assertTrue(sampler.ingest(Span("t", "s2", None, "svc", "op", 0, 2 * NS, {}, False)))
        self.assertEqual(len(sampler.evaluate_window("t")), 1)  # slow, kept


if __name__ == '__main__':
    unittest.main()
