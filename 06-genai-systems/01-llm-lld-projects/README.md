# 🏗️ GenAI LLD Projects

Component-level low-level design exercises for Generative AI systems. Each project focuses on a single microcomponent that appears in real-world LLM-powered architectures.

> **Python-first**: GenAI stacks are predominantly Python, so all projects provide Python implementations as the primary language. Java implementations are welcome but optional.

---

## 📋 Project Index

| Project | Description | Difficulty | Key Concepts | Status |
|---------|-------------|------------|--------------|--------|
| [Chunker & Metadata Indexer](chunker-metadata-indexer/) | Split, tag, and index documents for retrieval | ⭐⭐ | Strategy pattern, chunking, cosine similarity | ✅ |
| [Retriever & Ranker](retriever-ranker/) | Dense/sparse/hybrid retrieval with pluggable ranking | ⭐⭐⭐ | Strategy, Composite, cosine similarity, TF-IDF | ✅ |
| [Prompt Builder](prompt-builder/) | Assemble prompts from templates with budget guarding | ⭐⭐ | Builder pattern, token budgeting, safe interpolation | ✅ |
| [Conversation Memory Store](conversation-memory-store/) | Multi-turn memory with configurable strategies | ⭐⭐⭐ | Strategy pattern, sliding window, summarization | ✅ |
| [Safety Filter & Policy Engine](safety-filter-policy-engine/) | Content policies, rule evaluation, moderation | ⭐⭐⭐ | Chain of Responsibility, plugin architecture | ✅ |
| [LLM Request Orchestrator](llm-request-orchestrator/) | Retry, backoff, circuit breaker, observability | ⭐⭐⭐ | Circuit Breaker, Proxy, Observer, idempotency | ✅ |
| [Embedding Service](embedding-service/) | Generate and cache vector embeddings | ⭐⭐ | Strategy, Proxy, caching, L2 normalization | ✅ |
| [Tool Router](tool-router/) | Route LLM tool-call requests to handlers | ⭐⭐⭐ | Registry, Command, Chain of Responsibility | ✅ |
| [Evaluation Harness](evaluation-harness/) | Run and score LLM outputs against test cases | ⭐⭐⭐⭐ | Strategy, Template Method, metrics, batch eval | ✅ |
| [Streaming Token Aggregator](streaming-token-aggregator/) | Stream tokens over SSE with backpressure | ⭐⭐⭐ | Ring Buffer, Concurrency, wait/notify, SSE | ✅ |
| [Semantic Embedding Cache](semantic-embedding-cache/) | In-memory semantic cache for LLM responses | ⭐⭐ | LRU Cache, cosine similarity, multi-tenancy | ✅ |
| [Speculative Decoding Cache](speculative-decoding-cache/) | Manage draft tokens for LLM generation speedup | ⭐⭐⭐ | Target distribution, KV cache length management | ✅ |
| [Multi-Agent Orchestrator](multi-agent-orchestrator/) | State and flow for interacting AI agents | ⭐⭐⭐⭐ | Stateful blackboard, supervisor routing | ✅ |
| [Context Window Manager](context-window-manager/) | Dynamic assembly of prompt context within limits | ⭐⭐⭐ | Token budgets, contention resolution | ✅ |
| [Token Streaming Server](token-streaming-server/) | Async token streams to HTTP clients | ⭐⭐⭐ | Server-Sent Events (SSE), queueing | ✅ |
| [AI Safety Guardrails](ai-safety-guardrails/) | Multistage input/output LLM content blocking | ⭐⭐⭐ | Decorator, pipeline execution | ✅ |
| [Vector Store & Inverted Index](vector-store-inverted-index/) | Storing vectors and inverted index metadata | ⭐⭐⭐⭐ | Similarity search, metadata filtering | ✅ |

---

## 🗂️ Project Structure (per project)

Each project follows this layout:

```
<project-name>/
├── PROBLEM.md            # Requirements and constraints
├── python/
│   ├── v1-basic/         # Minimal working implementation
│   ├── v2-extended/      # Added features and patterns
│   ├── v3-optimized/     # Production-quality version
│   └── tests/            # Unit and integration tests
└── java/                 # Optional Java implementation
    ├── v1-basic/
    └── tests/
```

---

## 🔗 Cross-References

- **GenAI Concepts**: [00-concepts](../00-concepts/) — theoretical foundations for each component
- **Classical LLD Projects**: [02-lld-projects](../../02-lld-projects/) — OOP-focused exercises using the same versioned approach
- **GenAI HLD Systems**: [02-llm-hld-projects](../02-llm-hld-projects/) — full systems that compose these components

---

*All 17 GenAI LLD projects are available! Pick a component and start building. 🚀*
