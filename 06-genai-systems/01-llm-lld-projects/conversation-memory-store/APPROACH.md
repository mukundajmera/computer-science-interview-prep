# Design Approach for Conversation Memory Store

A step-by-step thought process for designing the conversation memory store.

---

## Step 1: Identify Core Entities

Extract nouns from the problem statement:

| Noun | Entity? | Reasoning |
|------|---------|-----------|
| Message | ✅ Yes | Fundamental data unit — a single conversation turn |
| Role | ✅ Yes | Enum classifying message origin (user/assistant/system) |
| Conversation | ✅ Yes | Ordered container of messages |
| Memory Strategy | ✅ Yes | Algorithm that decides which messages to keep |
| Memory Store | ✅ Yes | Registry of conversations keyed by ID |
| Summarizer | ✅ Yes | Pluggable component that compresses message sequences |
| Token Budget | ❌ No | Configuration parameter, not an entity |
| Context Window | ❌ No | Output of a strategy, not a persistent entity |

**Final Entities**: Message, Role, Conversation, MemoryStrategy, MemoryStore, Summarizer

---

## Step 2: Define Relationships

```
MemoryStore (1) ──manages──> (n) Conversation
Conversation (1) ──contains──> (n) Message
Message (1) ──has──> (1) Role
MemoryStrategy (1) ──wraps──> (1) Conversation
SummaryMemory (1) ──uses──> (1) Summarizer
```

### Relationship Types

| Relationship | Type | Description |
|--------------|------|-------------|
| MemoryStore → Conversation | Aggregation | Store indexes independent conversations |
| Conversation → Message | Composition | Messages belong to their conversation |
| MemoryStrategy → Conversation | Composition | Strategy owns its internal conversation |
| SummaryMemory → Summarizer | Aggregation | Summarizer is injected, exists independently |

---

## Step 3: Choose Design Patterns

### Pattern Analysis

| Pattern | Apply? | Justification |
|---------|--------|---------------|
| **Strategy** | ✅ Yes | Swap memory algorithms at runtime without changing callers |
| **Chain of Responsibility** | 🔄 v2 | Pipeline stages (summarize → trim → format) |
| **Observer** | 🔄 v2 | Notify listeners when memory is trimmed or summarized |
| **Template Method** | ✅ Yes | Common add/get flow with strategy-specific trimming |
| **Factory** | 🔄 v2 | Create strategies from configuration |

### Pattern Application

1. **Strategy Pattern** — MemoryStrategy
   - `BufferMemory`, `WindowMemory`, `SummaryMemory`, `TokenLimitedMemory` are interchangeable strategies.
   - Callers program to the `MemoryStrategy` interface; the concrete class determines what context is returned.

2. **Template Method** — get_context flow
   - Every strategy follows: retrieve messages → apply policy → format context.
   - Subclasses override the "apply policy" step.

3. **Dependency Injection** — Summarizer
   - `SummaryMemory` receives a `Summarizer` instance rather than creating one, enabling deterministic testing stubs.

---

## Step 4: Design Classes

### MemoryStrategy (ABC)
- **Methods**:
  - `add_message(message: Message) → None` — append a turn
  - `get_messages() → List[Message]` — retrieve current visible messages
  - `get_context() → str` — render messages into an LLM-ready context string
  - `clear() → None` — reset memory

### BufferMemory
- Stores all messages in an unbounded list.
- `get_messages()` returns the full list.

### WindowMemory
- Configured with `window_size: int` (number of recent turns to keep).
- `get_messages()` returns the last `window_size` messages.
- Older messages are still stored internally but excluded from context.

### SummaryMemory
- Configured with `max_recent: int` and a `Summarizer`.
- When messages exceed `max_recent`, older ones are summarized into a single system message.
- `get_messages()` returns `[summary_message] + recent_messages`.

### TokenLimitedMemory
- Configured with `max_tokens: int`.
- Uses a word-count heuristic to estimate tokens.
- `get_messages()` returns as many recent messages as fit within budget.

### MemoryStore
- `Dict[str, MemoryStrategy]` keyed by conversation ID.
- Provides `create_conversation()`, `get_conversation()`, `list_conversations()`, `delete_conversation()`.

### Summarizer (ABC)
- `summarize(messages: List[Message]) → str`
- **SimpleSummarizer** — extracts the first sentence of each message (deterministic stub).
- **NullSummarizer** — returns empty string (no-op).

---

## Step 5: Handle Edge Cases

### Input Validation
- Empty or blank message content
- Unknown conversation ID in store lookups
- Negative or zero window size / token budget

### Boundary Conditions
- Window larger than total messages → return all messages
- Token budget smaller than any single message → return at least the most recent one
- Summary of zero messages → return empty summary
- First message added to SummaryMemory → no summarization yet

### Strategy-Specific
- SummaryMemory: summary itself grows large over repeated summarizations
- TokenLimitedMemory: single message exceeding budget entirely
- WindowMemory: system prompt should ideally always be included (v2 enhancement)

---

## Step 6: Optimization Opportunities

### Data Structures

| Operation | Approach | Complexity |
|-----------|----------|------------|
| Add message | Append to list | O(1) |
| Get last N messages | Slice from end | O(N) |
| Token counting | Iterate words | O(W) where W = total words |
| Keyword search | Linear scan | O(M) where M = total messages |

### Future Optimizations
- **Lazy summarization**: only summarize when context is requested, not on every add.
- **Incremental summaries**: append to existing summary rather than re-summarizing everything.
- **Token caching**: precompute and cache token counts per message.
- **Copy-on-write branching**: share message history until a branch diverges.

---

## Step 7: Version Progression

### v1-basic
- Core data model (Message, Role, Conversation)
- Four memory strategies with deterministic behavior
- SimpleSummarizer and NullSummarizer stubs
- MemoryStore for multi-conversation management
- Comprehensive unit tests

### v2-extended
- Conversation forking/branching
- Keyword-based relevance retrieval
- Observer notifications on trim/summarize events
- Persistent storage adapter (JSON file)

### v3-optimized
- Thread-safe strategies with locking
- Token-aware incremental summarization
- Streaming context assembly for large conversations
- Strategy composition (chain multiple strategies)

---

## Code Organization

```
conversation-memory-store/
├── PROBLEM.md
├── APPROACH.md
├── DESIGN.md
├── python/
│   ├── v1-basic/
│   │   ├── __init__.py
│   │   ├── message.py        # Message, Role, Conversation
│   │   ├── memory.py         # MemoryStrategy ABC + 4 strategies + MemoryStore
│   │   ├── summarizer.py     # Summarizer ABC + SimpleSummarizer + NullSummarizer
│   │   └── demo.py           # Runnable demo
│   └── tests/
│       ├── __init__.py
│       └── test_memory.py    # Unit tests for all components
```

---

## Interview Discussion Points

1. **Why Strategy for memory management?**
   - Different LLM applications have different context constraints.
   - Chat assistants may use WindowMemory; document Q&A may need SummaryMemory.
   - Strategies are swappable at runtime without changing the calling code.

2. **Why a Summarizer interface instead of inline logic?**
   - In production the summarizer calls an LLM; in tests it must be deterministic.
   - Dependency injection allows swapping real and stub implementations.

3. **How would you handle very long conversations?**
   - Combine SummaryMemory with TokenLimitedMemory: summarize old turns, then trim to budget.
   - v3 introduces strategy composition for exactly this use case.

4. **How does this relate to RAG?**
   - Memory store manages conversation state; RAG retrieves external knowledge.
   - Both contribute to the context window sent to the LLM.
   - A unified context assembler (v3) could merge memory + RAG results.
