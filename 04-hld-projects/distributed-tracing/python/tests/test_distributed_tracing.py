import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
import importlib

models = importlib.import_module('v1-basic.models')
tail_sampler = importlib.import_module('v1-basic.tail_sampler')
dag_assembler = importlib.import_module('v1-basic.dag_assembler')

Span = models.Span
TailSampler = tail_sampler.TailSampler
DAGAssembler = dag_assembler.DAGAssembler

class TestDistributedTracing(unittest.TestCase):
    def test_tail_sampler_drops_normal_trace(self):
        sampler = TailSampler(1_000_000_000) # 1s
        sampler.ingest(Span("trace1", "span1", None, "svc1", "op1", 0, 500_000_000, {}, False))
        kept = sampler.evaluate_window("trace1")
        self.assertEqual(len(kept), 0)

    def test_tail_sampler_keeps_error_trace(self):
        sampler = TailSampler(1_000_000_000)
        sampler.ingest(Span("trace2", "span1", None, "svc1", "op1", 0, 500_000_000, {}, False))
        sampler.ingest(Span("trace2", "span2", "span1", "svc2", "op2", 0, 100_000_000, {}, True))
        kept = sampler.evaluate_window("trace2")
        self.assertEqual(len(kept), 2)

    def test_tail_sampler_keeps_slow_trace(self):
        sampler = TailSampler(1_000_000_000)
        sampler.ingest(Span("trace3", "span1", None, "svc1", "op1", 0, 1_500_000_000, {}, False))
        kept = sampler.evaluate_window("trace3")
        self.assertEqual(len(kept), 1)

    def test_dag_assembler(self):
        assembler = DAGAssembler()
        spans = [
            Span("trace4", "root", None, "svc1", "op1", 0, 1000, {}, False),
            Span("trace4", "child1", "root", "svc2", "op2", 100, 400, {}, False),
            Span("trace4", "child2", "root", "svc3", "op3", 500, 300, {}, False)
        ]
        roots = assembler.assemble(spans)
        self.assertEqual(len(roots), 1)
        self.assertEqual(roots[0].span.span_id, "root")
        self.assertEqual(len(roots[0].children), 2)

    def test_ingestion_worker_crash_loses_in_memory_spans(self):
        # Simplifications:
        # - Transport: Spans are passed as direct method calls, not over network (HTTP/gRPC)
        # - Clock: Durations are static provided values rather than computed from system time
        # - Security: Missing auth headers, tokens, and SSL encapsulation
        # - Consistency: Worker crash simulates local drop rather than partitioned Kafka replay issues
        sampler = TailSampler(1_000_000_000)
        sampler.ingest(Span("trace5", "span1", None, "svc1", "op1", 0, 1_500_000_000, {}, False))
        sampler.crash()
        kept = sampler.evaluate_window("trace5")
        self.assertEqual(len(kept), 0)

if __name__ == '__main__':
    unittest.main()
