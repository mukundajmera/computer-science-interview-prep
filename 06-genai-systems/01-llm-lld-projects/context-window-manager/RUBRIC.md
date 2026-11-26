# Context Window Manager - Grading Rubric

This rubric evaluates the candidate's structural design and deterministic logic for managing context segments under a strict budget.

## Level 4: Intuitive Minimum Example (Core Logic & Fit)

**Acceptance Cases:**
- **Exact Fit (No Eviction):** Demonstrated in `test_exact_fit_no_eviction_required`. The candidate can assemble a context list correctly when all tokens fit under the total budget.
- **Summarization Hooks:** Demonstrated in `test_requires_summarization_threshold_hook`. The manager correctly computes token totals for soft limit thresholds (e.g., `Priority.HISTORY`) without executing actual compaction logic.
- **Token Estimation Approximation:** Uses an interface for token counting (e.g., `TokenizerInterface`), allowing offline string-based testing instead of live external LLM API calls.

**Assessment:** The implementation establishes basic segment structure, budget tracking, and simple summarization warnings, meeting standard application needs.

## Level 5: Trade-offs (Eviction & Reordering)

**Acceptance Cases:**
- **Strict Priority Eviction:** Demonstrated in `test_strict_priority_eviction_strategy`. The logic rigorously evicts segments starting from lowest priority (5 - History) up, preserving mandatory tokens (1 - System, 2 - User Query).
- **Lost-in-the-Middle Reordering:** Demonstrated in `test_lost_in_the_middle_attention_reordering`. High priority context explicitly circumvents the middle-decay of LLM attention by placing System at index 0 and User Query at index -1 during compilation.

**Assessment:** The solution explicitly solves LLM-specific architectural trade-offs: strict token budgeting and positional attention guarantees.

## Level 6/Level 7: Optional Failure Trace & Strict Boundaries

**Acceptance Cases:**
- **Overflow Impossible Constraint:** Demonstrated in `test_overflow_rejects_impossible_constraint`. Handles cases where mandatory context alone (System + Query) exceeds the total token budget by gracefully throwing an explicit error (e.g., `ContextOverflowError`) instead of silently corrupting state.
- **Tenant Isolation:** Demonstrated in `test_tenant_isolation_new_instances`. Complete structural encapsulation that prevents state leakage of conversational segments across concurrent requests or different instantiations.

**Assessment:** The candidate anticipates absolute failure edges and implements defensive boundary testing, ensuring the framework would not accidentally leak or bypass foundational safety rules under impossible constraints.

## Code Parity

```python
# Python Interface Example
class TokenizerInterface(ABC):
    @abstractmethod
    def estimate_tokens(self, text: str) -> int:
        pass
```

## References
- [Python Source](python/v1-basic/context_manager.py)
- [Python Tests](python/tests/test_context_manager.py)
