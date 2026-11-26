# Context Window Manager

## Problem Statement

Design a Context Window Manager component that dynamically assembles an LLM prompt's context within strict token budgets (e.g., 4096 or 8192 tokens). The system must resolve contention between various context sources by enforcing rigorous priority levels and strategically reordering information to maximize model attention on critical segments.

---

## Functional Requirements

1. **Context Registration & Prioritization**: Accept and manage context segments categorized by strict priority:
   - Priority 1: System prompt / core rules.
   - Priority 2: Current user query.
   - Priority 3: Tool definitions.
   - Priority 4: Retrieved RAG context.
   - Priority 5: Chat history.
2. **Token Estimation**: Provide a standard-library approximation mechanism (e.g., a word-based estimator) to count tokens for individual text segments. (Note: No real external embedding or tokenizer equivalence is claimed).
3. **Budget Enforcement**: Truncate or evict segments from lowest priority to highest to ensure the total assembly fits exactly within the defined token limit.
4. **Sliding Window History Truncation**: Truncate chat history iteratively (oldest messages first) until the history segment fits the remaining budget.
5. **Conversation Summarization Hook**: Provide interfaces to detect when history overflows a soft threshold, triggering a compaction/summarization request.
6. **Lost-in-the-Middle Reordering**: Interleave or reorder the final context list to place high-priority chunks at the exact boundaries (beginning and end) of the context window to combat LLM attention decay.
7. **Model/Provider Independence**: Interfaces for tokenizers and models must be entirely independent of any specific LLM provider or vendor lock-in.

---

## Non-Functional Requirements

1. **Extensibility**: Injectable interfaces for tokenizers and model providers so that real services can replace approximations.
2. **Determinism**: The eviction order, budget calculation, and chunk reordering must be completely deterministic for a given set of inputs to allow exact fixture testing.
3. **Safety & Independence**: Operates as a single bounded microcomponent with explicit normal, error, cancellation, and privacy fixtures, and model/provider-independent interfaces. It must not rely on external network dependencies during tests.
4. **Language Constraints**: Utilize Python-first design using Python 3.8+ standard-library runtime features only. No external dependencies (e.g., Tiktoken or Langchain) for the core manager.

---

## Acceptance Cases (Test Traces)

1. **Exact Fit (No Eviction)** (Normal Fixture): (L4) Given segments totaling 3000 tokens and a budget of 4096, all segments are included, properly ordered.
2. **Strict Priority Eviction** (Normal Fixture): (L5) Given a 4096 budget and 6000 tokens of input, chat history is dropped or truncated first, followed by RAG context if needed, preserving system prompt, tools, and current user query.
3. **Lost-in-the-Middle Reordering** (Normal Fixture): (L5) High priority system prompt and user query are placed at absolute boundaries (index 0 and -1) when serialized.
4. **Overflow / Impossible Constraint** (Error Fixture): (L6/L7) System gracefully handles a condition where the combined mandatory (Priority 1 & 2) chunks exceed the entire token budget, rejecting the context assembly entirely or failing safely.
5. **Cancellation/Interrupt** (Cancellation Fixture): System correctly aborts budget enforcement or compilation mid-flight if a context assembly request is canceled.
6. **Tenant/Privacy Isolation** (Privacy Fixture): Concurrent context assemblies for different user tenants correctly isolate memory segments, preventing cross-tenant leakage.
