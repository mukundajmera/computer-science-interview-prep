import sys
import os
import asyncio
import threading
import unittest

# Match test_context_manager.py's sys.path handling for the versioned dirs.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../v2-extended')))
from context_manager_v2 import (
    ContextOverflowError,
    ContextWindowManager,
    DynamicScorer,
    Priority,
    SummarizerInterface,
    TokenizerInterface,
    TurnContext,
)
sys.path.pop(0)


class FakeExactTokenizer(TokenizerInterface):
    """Deterministic tokenizer: TOKEN_COUNT:<n> strings cost exactly n tokens."""

    def estimate_tokens(self, text: str) -> int:
        if text.startswith("TOKEN_COUNT:"):
            parts = text.split(":")
            return int(parts[1])
        return len(text)


class FakeSummarizer(SummarizerInterface):
    """Deterministic summarizer recording the order it received texts."""

    def __init__(self, summary: str = "TOKEN_COUNT:50") -> None:
        self.summary = summary
        self.received = []

    def summarize(self, texts):
        self.received.append(list(texts))
        return self.summary


class KeepHistoryScorer(DynamicScorer):
    """Scores HISTORY highest and RAG_CONTEXT lowest: the reverse of v1 order."""

    def calculate_score(self, segment, context: TurnContext) -> float:
        if segment.priority == Priority.HISTORY:
            return 100.0
        if segment.priority == Priority.RAG_CONTEXT:
            return 1.0
        return 50.0


class TestV2ThreadSafety(unittest.TestCase):
    """v2 improvement: thread safety around shared segment state."""

    def test_concurrent_add_compile_cancel_no_errors(self) -> None:
        manager = ContextWindowManager(total_budget=4096, tokenizer=FakeExactTokenizer())
        errors = []

        def writer(worker_id: int) -> None:
            try:
                for i in range(200):
                    manager.add_segment("TOKEN_COUNT:10", Priority.HISTORY,
                                        "w%d-h%d" % (worker_id, i))
            except Exception as exc:  # pragma: no cover - failure path
                errors.append(exc)

        def reader() -> None:
            try:
                for _ in range(200):
                    result = manager.compile()
                    total = sum(int(r.split(":")[1]) for r in result)
                    self.assertLessEqual(total, 4096)
            except Exception as exc:  # pragma: no cover - failure path
                errors.append(exc)

        threads = ([threading.Thread(target=writer, args=(w,)) for w in range(4)]
                   + [threading.Thread(target=reader) for _ in range(2)])
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        self.assertEqual(errors, [])

    def test_locking_disabled_still_functions(self) -> None:
        manager = ContextWindowManager(total_budget=4096, tokenizer=FakeExactTokenizer(),
                                       enable_locking=False)
        manager.add_segment("TOKEN_COUNT:10", Priority.SYSTEM, "sys")
        manager.add_segment("TOKEN_COUNT:20", Priority.USER_QUERY, "q")
        self.assertEqual(manager.compile(), ["TOKEN_COUNT:10", "TOKEN_COUNT:20"])


class TestV2DynamicScoring(unittest.TestCase):
    """v2 improvement: DynamicScorer-driven eviction (FOLLOW-UPS section 3)."""

    def test_scorer_overrides_enum_eviction_order(self) -> None:
        # Budget 4096; total 5000. v1 enum order would evict HISTORY first;
        # the scorer keeps history and evicts RAG instead.
        manager = ContextWindowManager(total_budget=4096, tokenizer=FakeExactTokenizer(),
                                       scorer=KeepHistoryScorer())
        manager.add_segment("TOKEN_COUNT:500", Priority.SYSTEM, "sys")
        manager.add_segment("TOKEN_COUNT:500", Priority.USER_QUERY, "q")
        manager.add_segment("TOKEN_COUNT:2000", Priority.HISTORY, "hist-keep")
        manager.add_segment("TOKEN_COUNT:2000", Priority.RAG_CONTEXT, "rag-drop")

        compiled = manager.compile(TurnContext(turn_index=3))

        self.assertIn("TOKEN_COUNT:2000", compiled)  # history kept
        # RAG evicted: only one TOKEN_COUNT:2000 (the history) remains.
        self.assertEqual(compiled.count("TOKEN_COUNT:2000"), 1)
        self.assertEqual(compiled[0], "TOKEN_COUNT:500")
        self.assertEqual(compiled[-1], "TOKEN_COUNT:500")

    def test_scorer_is_deterministic_across_runs(self) -> None:
        def build_and_compile() -> list:
            manager = ContextWindowManager(total_budget=100, tokenizer=FakeExactTokenizer(),
                                           scorer=KeepHistoryScorer())
            for i in range(5):
                manager.add_segment("TOKEN_COUNT:30", Priority.RAG_CONTEXT, "rag-%d" % i)
            manager.add_segment("TOKEN_COUNT:10", Priority.SYSTEM, "sys")
            manager.add_segment("TOKEN_COUNT:10", Priority.USER_QUERY, "q")
            return manager.compile()

        first = build_and_compile()
        second = build_and_compile()
        self.assertEqual(first, second)
        # 170 tokens in, budget 100: three RAG segments evicted (oldest first).
        self.assertEqual(len(first), 4)

    def test_scorer_never_evicts_mandatory_segments(self) -> None:
        class ZeroScorer(DynamicScorer):
            def calculate_score(self, segment, context: TurnContext) -> float:
                return 0.0

        manager = ContextWindowManager(total_budget=100, tokenizer=FakeExactTokenizer(),
                                       scorer=ZeroScorer())
        manager.add_segment("TOKEN_COUNT:60", Priority.SYSTEM, "sys")
        manager.add_segment("TOKEN_COUNT:60", Priority.USER_QUERY, "q")
        with self.assertRaises(ContextOverflowError):
            manager.compile()


class TestV2SummarizationHook(unittest.TestCase):
    """v2 improvement: active compact_history (FOLLOW-UPS section 2)."""

    def _history_manager(self, summarizer) -> ContextWindowManager:
        manager = ContextWindowManager(total_budget=100, soft_limit_ratio=0.5,
                                       tokenizer=FakeExactTokenizer(),
                                       summarizer=summarizer)
        manager.add_segment("TOKEN_COUNT:10", Priority.SYSTEM, "sys")
        manager.add_segment("TOKEN_COUNT:30", Priority.HISTORY, "hist-old")
        manager.add_segment("TOKEN_COUNT:30", Priority.HISTORY, "hist-new")
        return manager

    def test_compact_history_replaces_segments_with_summary(self) -> None:
        summarizer = FakeSummarizer()
        manager = self._history_manager(summarizer)
        self.assertTrue(manager.requires_summarization())

        self.assertTrue(manager.compact_history())

        self.assertFalse(manager.requires_summarization())
        compiled = manager.compile()
        self.assertIn("TOKEN_COUNT:50", compiled)
        # Two history entries collapsed into one summary segment.
        self.assertEqual(len(compiled), 2)

    def test_summarizer_receives_oldest_first(self) -> None:
        summarizer = FakeSummarizer()
        manager = self._history_manager(summarizer)
        manager.compact_history()
        self.assertEqual(summarizer.received,
                         [["TOKEN_COUNT:30", "TOKEN_COUNT:30"]])
        self.assertEqual(len(summarizer.received), 1)

    def test_compact_history_noop_under_threshold(self) -> None:
        summarizer = FakeSummarizer()
        manager = ContextWindowManager(total_budget=100, soft_limit_ratio=0.9,
                                       tokenizer=FakeExactTokenizer(),
                                       summarizer=summarizer)
        manager.add_segment("TOKEN_COUNT:10", Priority.HISTORY, "hist")
        self.assertFalse(manager.compact_history())
        self.assertEqual(summarizer.received, [])

    def test_compact_history_without_summarizer_raises(self) -> None:
        manager = ContextWindowManager(total_budget=100, soft_limit_ratio=0.5,
                                       tokenizer=FakeExactTokenizer())
        manager.add_segment("TOKEN_COUNT:60", Priority.HISTORY, "hist")
        self.assertTrue(manager.requires_summarization())
        with self.assertRaises(RuntimeError):
            manager.compact_history()

    def test_compact_history_rejects_empty_summary(self) -> None:
        manager = self._history_manager(FakeSummarizer(summary=""))
        with self.assertRaises(ValueError):
            manager.compact_history()


class TestV2ValidationAndParity(unittest.TestCase):
    """v2 validation and v1-behavior parity."""

    def test_constructor_validation(self) -> None:
        with self.assertRaises(ValueError):
            ContextWindowManager(total_budget=0)
        with self.assertRaises(ValueError):
            ContextWindowManager(total_budget=100, soft_limit_ratio=0.0)
        with self.assertRaises(ValueError):
            ContextWindowManager(total_budget=100, soft_limit_ratio=1.0)

    def test_add_segment_validation(self) -> None:
        manager = ContextWindowManager(total_budget=100, tokenizer=FakeExactTokenizer())
        with self.assertRaises(ValueError):
            manager.add_segment("", Priority.HISTORY, "hist")
        with self.assertRaises(ValueError):
            manager.add_segment("TOKEN_COUNT:10", Priority.HISTORY, "")

    def test_v1_parity_strict_priority_eviction(self) -> None:
        manager = ContextWindowManager(total_budget=4096, tokenizer=FakeExactTokenizer())
        manager.add_segment("TOKEN_COUNT:1000", Priority.SYSTEM, "sys-1")
        manager.add_segment("TOKEN_COUNT:1000", Priority.HISTORY, "hist-old")
        manager.add_segment("TOKEN_COUNT:1000", Priority.HISTORY, "hist-new")
        manager.add_segment("TOKEN_COUNT:1500", Priority.RAG_CONTEXT, "rag-1")
        manager.add_segment("TOKEN_COUNT:1000", Priority.TOOL_DEF, "tool-1")
        manager.add_segment("TOKEN_COUNT:500", Priority.USER_QUERY, "query-1")

        compiled = manager.compile()

        # History evicted first (both), then RAG truncated to fit 4096:
        # 1000 sys + 1500 rag + 1000 tool + 500 query = 4000 <= 4096.
        self.assertEqual(len(compiled), 4)
        self.assertEqual(compiled[0], "TOKEN_COUNT:1000")
        self.assertEqual(compiled[-1], "TOKEN_COUNT:500")

    def test_v1_parity_cancellation(self) -> None:
        manager = ContextWindowManager(total_budget=4096, tokenizer=FakeExactTokenizer())
        manager.add_segment("TOKEN_COUNT:10", Priority.SYSTEM, "sys")
        manager.cancel()
        with self.assertRaises(asyncio.CancelledError):
            manager.compile()
        with self.assertRaises(asyncio.CancelledError):
            manager.compact_history()


if __name__ == "__main__":
    unittest.main()
