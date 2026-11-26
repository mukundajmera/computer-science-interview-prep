import sys
import os
import unittest

# Ensure the correct module path for tests
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../v1-basic')))
from context_manager import ContextWindowManager, Priority, ContextOverflowError, TokenizerInterface
sys.path.pop(0)

class FakeExactTokenizer(TokenizerInterface):
    """
    A fake tokenizer for exact token counting in tests based on string length, for determinism.
    """
    def estimate_tokens(self, text: str) -> int:
        if text.startswith("TOKEN_COUNT:"):
            parts = text.split(":")
            return int(parts[1])
        return len(text)

class TestContextWindowManager(unittest.TestCase):
    
    def setUp(self) -> None:
        self.tokenizer = FakeExactTokenizer()

    def test_exact_fit_no_eviction_required(self) -> None:
        """
        Acceptance Case 1: Exact Fit (No Eviction):
        Given segments totaling 3000 tokens and a budget of 4096,
        all segments are included, properly ordered.
        """
        ctx_manager = ContextWindowManager(total_budget=4096, tokenizer=self.tokenizer)
        
        ctx_manager.add_segment("TOKEN_COUNT:1000", Priority.HISTORY, "hist-1")
        ctx_manager.add_segment("TOKEN_COUNT:500", Priority.RAG_CONTEXT, "rag-1")
        ctx_manager.add_segment("TOKEN_COUNT:1000", Priority.USER_QUERY, "query-1")
        ctx_manager.add_segment("TOKEN_COUNT:500", Priority.SYSTEM, "sys-1")
        
        compiled_result = ctx_manager.compile()
        
        self.assertEqual(len(compiled_result), 4)
        self.assertEqual(compiled_result[0], "TOKEN_COUNT:500") 
        self.assertEqual(compiled_result[-1], "TOKEN_COUNT:1000") 

    def test_strict_priority_eviction_strategy(self) -> None:
        """
        Acceptance Case 2: Strict Priority Eviction:
        Given a 4096 budget and 6000 tokens of input, chat history is dropped or truncated first,
        followed by RAG context if needed, preserving system prompt, tools, and current user query.
        """
        ctx_manager = ContextWindowManager(total_budget=4096, tokenizer=self.tokenizer)
        
        ctx_manager.add_segment("TOKEN_COUNT:1000", Priority.SYSTEM, "sys-1")
        ctx_manager.add_segment("TOKEN_COUNT:1000", Priority.HISTORY, "hist-old")
        ctx_manager.add_segment("TOKEN_COUNT:1000", Priority.HISTORY, "hist-new")
        ctx_manager.add_segment("TOKEN_COUNT:1500", Priority.RAG_CONTEXT, "rag-1")
        ctx_manager.add_segment("TOKEN_COUNT:1000", Priority.TOOL_DEF, "tool-1")
        ctx_manager.add_segment("TOKEN_COUNT:500", Priority.USER_QUERY, "query-1")
        
        compiled_result = ctx_manager.compile()
        
        self.assertEqual(len(compiled_result), 4)
        self.assertEqual(compiled_result[0], "TOKEN_COUNT:1000") 
        self.assertEqual(compiled_result[-1], "TOKEN_COUNT:500") 
        
        self.assertEqual(compiled_result.count("TOKEN_COUNT:1500"), 1) 
        self.assertEqual(compiled_result.count("TOKEN_COUNT:1000"), 2) 

    def test_lost_in_the_middle_attention_reordering(self) -> None:
        """
        Acceptance Case 3: Lost-in-the-Middle Reordering:
        High priority system prompt and user query are placed at absolute boundaries (index 0 and -1) when serialized.
        """
        ctx_manager = ContextWindowManager(total_budget=8192, tokenizer=self.tokenizer)
        
        ctx_manager.add_segment("TOKEN_COUNT:100", Priority.HISTORY, "hist-1")
        ctx_manager.add_segment("TOKEN_COUNT:100", Priority.USER_QUERY, "query-1")
        ctx_manager.add_segment("TOKEN_COUNT:100", Priority.TOOL_DEF, "tool-1")
        ctx_manager.add_segment("TOKEN_COUNT:100", Priority.SYSTEM, "sys-1")
        ctx_manager.add_segment("TOKEN_COUNT:100", Priority.RAG_CONTEXT, "rag-1")
        
        ctx_manager._segments[0].text = "history_text"
        ctx_manager._segments[1].text = "query_text"
        ctx_manager._segments[2].text = "tool_text"
        ctx_manager._segments[3].text = "system_text"
        ctx_manager._segments[4].text = "rag_text"
        
        compiled_result = ctx_manager.compile()
        
        self.assertEqual(compiled_result[0], "system_text")
        self.assertEqual(compiled_result[-1], "query_text")
        self.assertEqual(compiled_result[1:4], ["history_text", "tool_text", "rag_text"])

    def test_overflow_rejects_impossible_constraint(self) -> None:
        """
        Acceptance Case 4: Overflow / Impossible Constraint:
        System gracefully handles a condition where the combined mandatory (Priority 1 & 2)
        chunks exceed the entire token budget, rejecting the context assembly entirely or failing safely.
        """
        ctx_manager = ContextWindowManager(total_budget=1000, tokenizer=self.tokenizer)
        
        ctx_manager.add_segment("TOKEN_COUNT:600", Priority.SYSTEM, "sys-1")
        ctx_manager.add_segment("TOKEN_COUNT:500", Priority.USER_QUERY, "query-1")
        ctx_manager.add_segment("TOKEN_COUNT:100", Priority.HISTORY, "hist-1")
        
        with self.assertRaises(ContextOverflowError) as context:
            ctx_manager.compile()
        self.assertIn("Mandatory context", str(context.exception))

    def test_requires_summarization_threshold_hook(self) -> None:
        """
        Extra test for the conversation summarization hook based on the soft limit ratio.
        """
        ctx_manager = ContextWindowManager(total_budget=1000, soft_limit_ratio=0.8, tokenizer=self.tokenizer)
        
        ctx_manager.add_segment("TOKEN_COUNT:700", Priority.HISTORY, "hist-1")
        self.assertFalse(ctx_manager.requires_summarization())
        
        ctx_manager.add_segment("TOKEN_COUNT:150", Priority.HISTORY, "hist-2")
        self.assertTrue(ctx_manager.requires_summarization())

    def test_tenant_isolation_new_instances(self) -> None:
        """
        Tests tenant isolation by ensuring a new manager instance is completely clean.
        """
        manager_a = ContextWindowManager(total_budget=4096, tokenizer=self.tokenizer)
        manager_a.add_segment("TOKEN_COUNT:100", Priority.SYSTEM, "sys-1")
        
        manager_b = ContextWindowManager(total_budget=4096, tokenizer=self.tokenizer)
        manager_b.add_segment("TOKEN_COUNT:100", Priority.USER_QUERY, "query-1")
        
        result_a = manager_a.compile()
        result_b = manager_b.compile()
        
        self.assertEqual(len(result_a), 1)
        self.assertEqual(len(result_b), 1)
        self.assertEqual(result_a[0], "TOKEN_COUNT:100")
        self.assertEqual(manager_a._segments[0].priority, Priority.SYSTEM)
        self.assertEqual(manager_b._segments[0].priority, Priority.USER_QUERY)

    def test_privacy_and_no_external_calls(self) -> None:
        """
        Tests that no external provider calls or sensitive prompt logs happen.
        Asserts that compiled text strictly matches added text and doesn't inject external API data.
        """
        ctx_manager = ContextWindowManager(total_budget=4096, tokenizer=self.tokenizer)
        sensitive_text = "TOKEN_COUNT:50:USER_PII_DATA"
        ctx_manager.add_segment(sensitive_text, Priority.USER_QUERY, "query-1")
        compiled = ctx_manager.compile()
        
        self.assertEqual(len(compiled), 1)
        self.assertEqual(compiled[0], sensitive_text)
        
        self.assertFalse(hasattr(ctx_manager, 'logger'))

    def test_cancellation_interrupt(self) -> None:
        """
        Acceptance Case 5: Cancellation/Interrupt:
        System correctly aborts budget enforcement or compilation mid-flight if a context assembly request is canceled.
        """
        import asyncio
        ctx_manager = ContextWindowManager(total_budget=4096, tokenizer=self.tokenizer)
        ctx_manager.add_segment("TOKEN_COUNT:1000", Priority.SYSTEM, "sys-1")
        ctx_manager.add_segment("TOKEN_COUNT:5000", Priority.HISTORY, "hist-1")
        
        ctx_manager.cancel()
        
        with self.assertRaises(asyncio.CancelledError):
            ctx_manager.compile()

if __name__ == '__main__':
    unittest.main()
