import asyncio
import sys
import os
import unittest
from typing import AsyncGenerator, List, Tuple

# Match test_streaming_server.py's sys.path handling for the versioned dirs.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "v2-extended")))
from streaming_server_v2 import (
    ChunkingPolicy,
    LLMProvider,
    StreamMetrics,
    stream_response,
)
sys.path.pop(0)


class FakeProvider(LLMProvider):
    """Same fake shape as the v1 tests: (token, delay) scripted tokens."""

    def __init__(self, tokens: List[Tuple[str, float]], expected_tenant: str = None):
        self.tokens = tokens
        self.aborted = False
        self.expected_tenant = expected_tenant

    async def async_generate(self, prompt: str, tenant_id: str) -> AsyncGenerator[str, None]:
        if self.expected_tenant and tenant_id != self.expected_tenant:
            raise ValueError("Unauthorized tenant: %s" % tenant_id)
        for token, delay in self.tokens:
            if delay > 0:
                await asyncio.sleep(delay)
            yield token

    def abort(self) -> None:
        self.aborted = True


class PausableProvider(FakeProvider):
    """Provider with explicit backpressure signaling (FOLLOW-UPS extension 2)."""

    def __init__(self, tokens: List[Tuple[str, float]], **kwargs):
        super().__init__(tokens, **kwargs)
        self.pause_calls = 0
        self.resume_calls = 0

    def pause(self) -> None:
        self.pause_calls += 1

    def resume(self) -> None:
        self.resume_calls += 1


def run_stream(provider, *args, **kwargs):
    """Collects all SSE events from one stream."""
    async def _collect():
        events = []
        async for event in stream_response(provider, *args, **kwargs):
            events.append(event)
        return events
    return asyncio.run(_collect())


class TestV2Backpressure(unittest.TestCase):
    """v2 improvement: bounded queue + explicit pause/resume signaling."""

    def test_bounded_queue_pauses_and_resumes_provider(self) -> None:
        # 12 instant tokens, buffer of 2: the producer outruns the consumer,
        # fills the queue, and must signal pause/resume.
        tokens = [("t%d " % i, 0.0) for i in range(12)]
        provider = PausableProvider(tokens)
        metrics = StreamMetrics()

        events = run_stream(provider, "prompt", "tenant1",
                            max_buffered_tokens=2, metrics=metrics)

        self.assertIn("data: [DONE]\n\n", events)
        self.assertGreaterEqual(provider.pause_calls, 1)
        self.assertGreaterEqual(provider.resume_calls, 1)
        snap = metrics.snapshot()
        self.assertEqual(snap["tokens_received"], 12)
        self.assertEqual(snap["pauses"], provider.pause_calls)
        self.assertGreaterEqual(snap["resumes"], 1)

    def test_bounded_queue_works_without_pausable_provider(self) -> None:
        tokens = [("Hel", 0.0), ("lo", 0.0), (" ", 0.0), ("world", 0.0)]
        provider = FakeProvider(tokens)
        events = run_stream(provider, "prompt", "tenant1", max_buffered_tokens=1)
        self.assertIn("data: Hello \n\n", events)
        self.assertIn("data: world\n\n", events)
        self.assertIn("data: [DONE]\n\n", events)

    def test_bounded_queue_cancellation_aborts_and_cleans_up(self) -> None:
        async def _test():
            # Slow provider: cancellation lands mid-stream.
            tokens = [("a", 0.05) for _ in range(50)]
            provider = PausableProvider(tokens)
            gen = stream_response(provider, "prompt", "tenant1",
                                  max_buffered_tokens=2)
            iterator = gen.__aiter__()
            await iterator.__anext__()
            await gen.aclose()
            return provider

        provider = asyncio.run(_test())
        self.assertTrue(provider.aborted)


class TestV2ChunkingPolicy(unittest.TestCase):
    """v2 improvement: configurable chunking."""

    def test_max_chunk_chars_flushes_fixed_size_pieces(self) -> None:
        # No boundary chars anywhere: v1 would only flush at the end.
        provider = FakeProvider([("ab", 0.0), ("cd", 0.0), ("ef", 0.0)])
        policy = ChunkingPolicy(flush_on_boundary=False, max_chunk_chars=3)
        events = run_stream(provider, "prompt", "t", chunking_policy=policy)
        self.assertIn("data: abc\n\n", events)
        self.assertIn("data: def\n\n", events)
        self.assertIn("data: [DONE]\n\n", events)

    def test_boundary_disabled_flushes_once_at_end(self) -> None:
        provider = FakeProvider([("Hel", 0.0), ("lo ", 0.0), ("world", 0.0)])
        policy = ChunkingPolicy(flush_on_boundary=False)
        events = run_stream(provider, "prompt", "t", chunking_policy=policy)
        data_events = [e for e in events if e.startswith("data: ") and e != "data: [DONE]\n\n"]
        self.assertEqual(data_events, ["data: Hello world\n\n"])

    def test_size_then_boundary_combination(self) -> None:
        provider = FakeProvider([("hello ", 0.0), ("wor", 0.0)])
        policy = ChunkingPolicy(flush_on_boundary=True, max_chunk_chars=4)
        events = run_stream(provider, "prompt", "t", chunking_policy=policy)
        # "hello " -> size flush "hell", then "o " remains; boundary on " "
        # flushes "o "; then "wor" flushed as remainder.
        self.assertIn("data: hell\n\n", events)
        self.assertIn("data: o \n\n", events)
        self.assertIn("data: wor\n\n", events)


class TestV2MetricsAndHeartbeat(unittest.TestCase):
    """v2 improvements: metrics hooks, configurable heartbeat."""

    def test_metrics_hook_receives_events_with_tenant(self) -> None:
        captured = []

        def hook(event: str, tenant_id: str) -> None:
            captured.append((event, tenant_id))

        provider = FakeProvider([("hi ", 0.0)])
        run_stream(provider, "prompt", "tenant_x", metrics_hook=hook)
        self.assertIn(("tokens_received", "tenant_x"), captured)
        self.assertIn(("chunks_flushed", "tenant_x"), captured)

    def test_configurable_heartbeat_fires(self) -> None:
        # A 0.2s pause with a 0.05s heartbeat: v1's fixed 15s would never fire.
        provider = FakeProvider([("a", 0.0), (".", 0.2)])
        metrics = StreamMetrics()
        events = run_stream(provider, "prompt", "t",
                            heartbeat_timeout=0.05, metrics=metrics)
        self.assertIn("event: ping\ndata: {}\n\n", events)
        self.assertGreaterEqual(metrics.snapshot()["heartbeats_sent"], 1)

    def test_metrics_unknown_event_raises(self) -> None:
        metrics = StreamMetrics()
        with self.assertRaises(ValueError):
            metrics.record("nonsense")


class TestV2ValidationAndParity(unittest.TestCase):
    """v2 validation and v1-behavior parity."""

    def test_input_validation(self) -> None:
        provider = FakeProvider([("a", 0.0)])
        for kwargs in (
            {"prompt": "", "tenant_id": "t"},
            {"prompt": "p", "tenant_id": ""},
            {"prompt": "p", "tenant_id": "t", "max_tokens": 0},
            {"prompt": "p", "tenant_id": "t", "heartbeat_timeout": 0},
            {"prompt": "p", "tenant_id": "t", "max_buffered_tokens": 0},
        ):
            with self.assertRaises(ValueError):
                run_stream(provider, **kwargs)

    def test_budget_abort_parity(self) -> None:
        provider = FakeProvider([("a", 0.0), ("b", 0.0), ("c", 0.0)])
        metrics = StreamMetrics()
        events = run_stream(provider, "prompt", "t", max_tokens=2, metrics=metrics)
        self.assertTrue(provider.aborted)
        self.assertIn('event: error\ndata: {"message": "Budget exceeded"}\n\n', events)
        self.assertIn("data: [DONE]\n\n", events)
        self.assertEqual(metrics.snapshot()["aborts"], 1)

    def test_cancellation_aborts_provider_parity(self) -> None:
        async def _test():
            tokens = [("x", 0.05) for _ in range(50)]
            provider = FakeProvider(tokens)
            gen = stream_response(provider, "prompt", "t")
            iterator = gen.__aiter__()
            await iterator.__anext__()
            await gen.aclose()
            return provider

        provider = asyncio.run(_test())
        self.assertTrue(provider.aborted)

    def test_remainder_flush_parity(self) -> None:
        provider = FakeProvider([("no", 0.0), ("boundary", 0.0)])
        events = run_stream(provider, "prompt", "t")
        self.assertIn("data: noboundary\n\n", events)
        self.assertIn("data: [DONE]\n\n", events)

    def test_provider_error_event_parity(self) -> None:
        provider = FakeProvider([("a", 0.0)], expected_tenant="other")
        events = run_stream(provider, "prompt", "t")
        self.assertTrue(any(e.startswith("event: error") for e in events))
        self.assertIn("data: [DONE]\n\n", events)


if __name__ == "__main__":
    unittest.main()
