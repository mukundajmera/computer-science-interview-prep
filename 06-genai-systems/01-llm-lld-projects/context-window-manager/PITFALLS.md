# Context Window Manager - Pitfalls

This document details common architectural missteps and boundaries in the Context Window Manager implementation.

## 1. Precise Tokenization Assumptions
**Counterexample:**
Assuming that offline unit tests can exactly predict production token consumption using standard library features.
**Implementation Boundary:**
The current `FallbackTokenizer` is a rough approximation (`len(text.split()) * 1.3`). Relying on this for production systems without injecting a precise tokenizer (e.g., `tiktoken`) will result in unexpected token-budget overflows or sub-optimal context truncation on live networks. This design intentionally trades strict accuracy for deterministic offline testing.

## 2. Silent Truncation of Core Context
**Counterexample:**
Silently omitting portions of the `SYSTEM` or `USER_QUERY` prompts when the context exceeds bounds without notifying the upstream calling logic.
**Implementation Boundary:**
The code explicitly rejects attempts to violate mandatory context bounds. In `ContextWindowManager._evict_to_fit()`, if the total tokens for Priority 1 and 2 segments exceed `total_budget`, the system raises a `ContextOverflowError` rather than silently degrading core behaviors.

## 3. Position and Attention Decay
**Counterexample:**
Appending new RAG context indiscriminately at the end of the context array.
**Implementation Boundary:**
The LLM "lost-in-the-middle" effect heavily discounts context near the center of long sequences. The `ContextWindowManager._reorder_for_attention()` method strictly anchors the `Priority.SYSTEM` segment at index `0` and `Priority.USER_QUERY` at index `-1` regardless of the order items were added. Failing to execute this logic results in decreased accuracy on critical safety and query rules.

## 4. Tenant State Leakage
**Counterexample:**
Storing context segments as global class properties or in static arrays rather than encapsulating them within independent instance boundaries.
**Implementation Boundary:**
Tenant isolation is enforced by storing `_segments` as an instance attribute instantiated within the constructor (`__init__`). The `test_tenant_isolation_new_instances` verifies that parallel initialization logic prevents one context operation from leaking conversational memory into an adjacent request.

## Code Parity

```python
# Python exception boundary
if mandatory_total > self._total_budget:
    raise ContextOverflowError("Mandatory context (System + User Query) exceeds total token budget.")
```

## References
- [Python Source](python/v1-basic/context_manager.py)
