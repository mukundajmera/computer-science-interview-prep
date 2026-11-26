# Context Window Manager - Follow-ups

This document covers Optional Staff Follow-ups and unimplemented features for the Context Window Manager, distinct from the Mandatory Interview Baseline requirements.

## 1. Production Tokenizer Integration
**Unimplemented Extension (Mandatory Interview Baseline):**
The current project relies on a standard library `FallbackTokenizer` approximation for deterministic offline behavior.

**Follow-up Task (Optional Staff Follow-up):** Implement a production-grade tokenizer adapter (e.g., using `tiktoken` for OpenAI models or specific Hugging Face tokenizers) adhering to the `TokenizerInterface`. This adapter would require managing networking or heavy model file loading and robust handling for disparate language encoding behavior.

## 2. Active LLM Summarization Hook
**Unimplemented Extension (Mandatory Interview Baseline):**
The baseline implements `requires_summarization()` as a flag that trips when `Priority.HISTORY` tokens cross the `soft_limit_ratio` (e.g., 80% of budget), but leaves the actual summarization up to the caller.

**Follow-up Task (Optional Staff Follow-up):** Design and integrate an asynchronous summarizer queue. Once `requires_summarization()` is true, a side-car routine invokes an external LLM call to compress the oldest history chunks into a dense summary string, subsequently replacing the raw chat segments in the internal `_segments` list and recalculating budgets seamlessly.

## 3. Dynamic Priority Scoring
**Unimplemented Extension (Mandatory Interview Baseline):**
The manager currently uses a rigid enum categorization (1 through 5) where Chat History (5) is always evicted prior to RAG context (4) and Tool Definitions (3).

**Follow-up Task (Optional Staff Follow-up):** Replace the strict enum eviction loop with a dynamic scoring engine. Depending on the conversational turn context, an agent might decide an older query (History) is temporarily more vital than unrelated RAG context chunks, generating dynamic float priority values to drive the `_evict_to_fit` array sorting logic.

## Code Parity
If implementing the dynamic priority scoring:

```python
# Python: Priority as a dynamic score interface
class DynamicScorer(ABC):
    @abstractmethod
    def calculate_score(self, segment: ContextSegment, context: TurnContext) -> float:
        pass
```

## References
- [Python Source](python/v1-basic/context_manager.py)
