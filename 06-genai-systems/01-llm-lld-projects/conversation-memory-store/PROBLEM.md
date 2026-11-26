# Conversation Memory Store

## Problem Statement

Design a conversation memory store that manages chat history for LLM-based applications. The system must support multiple memory strategies—buffer, sliding window, summary, and token-limited—to balance context quality against token budget constraints.

---

## Functional Requirements

1. **Store Conversation Turns**: Persist user, assistant, and system messages with timestamps and metadata.
2. **Short-Term Memory**: Maintain a sliding window of the most recent N turns for immediate context.
3. **Long-Term Memory**: Summarize older turns so their essence is retained without consuming the full token budget.
4. **Configurable Memory Strategies**:
   - **BufferMemory** — keep every message (unbounded).
   - **WindowMemory** — keep the last N turns only.
   - **SummaryMemory** — summarize messages beyond a recency threshold, keep recent turns verbatim.
   - **TokenLimitedMemory** — keep as many recent messages as fit within a token budget.
5. **Multi-Conversation Management**: Isolate and retrieve conversations by unique ID.
6. **Conversation Forking/Branching**: Create a branch from a conversation at a specific point to explore alternate paths.
7. **Message Retrieval**: Fetch messages by recency or by simple keyword relevance.

---

## Non-Functional Requirements

1. **Memory-Efficient**: Strategies should discard or compress history to stay within budgets.
2. **Deterministic Summarization Stub**: Provide a pluggable summarizer interface with a deterministic stub for testing (no external LLM calls).
3. **Extensible Strategies**: New memory strategies can be added without modifying existing code (Open/Closed Principle).
4. **Thread-Safety Ready**: Design should accommodate future thread-safe extensions.

---

## Constraints & Assumptions

- Messages are plain text with a `role` (USER, ASSISTANT, SYSTEM).
- Token estimation uses a simple word-count heuristic (1 word ≈ 1 token) to avoid external tokenizer dependencies.
- Summarization is represented by a pluggable interface; the v1 stub concatenates first sentences.
- No persistence layer (in-memory only); durable storage is a v2 concern.
- No external dependencies—standard library only.

---

## Sample Interactions

```
1. Create a new conversation "conv-1"
2. Add system message: "You are a helpful assistant."
3. Add user message: "What is caching?"
4. Add assistant message: "Caching stores copies of data..."
5. Add user message: "How does Redis work?"
6. Add assistant message: "Redis is an in-memory key-value store..."
7. Request context with WindowMemory(window_size=2):
   → Returns last 2 turns (messages 5–6)
8. Request context with SummaryMemory(max_recent=2):
   → Returns summary of messages 1–4 + messages 5–6 verbatim
9. Request context with TokenLimitedMemory(max_tokens=20):
   → Returns as many recent messages as fit within 20 tokens
10. Fork conversation at message 4 → new "conv-1-branch"
    → Branch starts with messages 1–4, diverges from there
```

---

## Clarifying Questions to Ask

1. "What is the expected token budget range for conversations?"
2. "Should the summarizer be synchronous or support async LLM calls?"
3. "Do we need to support message editing or deletion after insertion?"
4. "Should forked conversations share history (copy-on-write) or deep copy?"
5. "Is there a maximum number of concurrent conversations?"
6. "Do we need to support multimedia messages or text only?"
7. "Should relevance search use embeddings or simple keyword matching?"
8. "Do we need an event/callback system when memory is trimmed?"

---

## Entities to Identify

| Entity | Responsibility |
|--------|---------------|
| Message | Single conversation turn with role, content, timestamp, metadata |
| Role | Enum distinguishing USER, ASSISTANT, SYSTEM messages |
| Conversation | Ordered collection of messages for one chat session |
| MemoryStrategy | Abstract interface for memory management algorithms |
| BufferMemory | Strategy that retains all messages |
| WindowMemory | Strategy that keeps last N turns |
| SummaryMemory | Strategy that summarizes old messages, keeps recent ones |
| TokenLimitedMemory | Strategy that enforces a token budget |
| MemoryStore | Registry managing multiple conversations by ID |
| Summarizer | Pluggable interface for text summarization |

---

## Version Roadmap

| Version | Features |
|---------|----------|
| v1-basic | Core entities, four memory strategies, deterministic summarizer stub, multi-conversation store |
| v2-extended | Persistent storage adapter, async summarizer, conversation forking, relevance search |
| v3-optimized | Thread-safe strategies, token-aware compression, streaming context assembly |
