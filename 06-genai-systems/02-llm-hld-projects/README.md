# 🌐 GenAI HLD Projects

Full system design case studies for LLM-powered applications. Each project follows the [GenAI HLD Design Template](./DESIGN-TEMPLATE.md) (extending the standard [HLD Design Template](../../04-hld-projects/DESIGN-TEMPLATE.md)) with GenAI-specific additions for model selection, RAG pipelines, safety, evaluation, and cost analysis.

---

## 📋 Project Index

| # | System | Description | Key GenAI Patterns | Difficulty | Status |
|---|--------|-------------|-------------------|------------|--------|
| 1 | [Document Q&A (RAG)](./document-qa-rag/) | LLM-powered document Q&A with cited answers | RAG, hybrid retrieval, reranking, citations | ⭐⭐⭐ | ✅ |
| 2 | [Multi-Tenant Chat Assistant](./multi-tenant-chat-assistant/) | ChatGPT-as-a-Service for enterprises | Tenant isolation, per-org safety, model routing | ⭐⭐⭐ | ✅ |
| 3 | [AI Coding Copilot](./ai-coding-copilot/) | In-IDE code completion and chat | FIM, dual-path (fast+rich), context engineering | ⭐⭐⭐⭐ | ✅ |
| 4 | [Agentic Workflow Orchestrator](./agentic-workflow-orchestrator/) | LLM agents that execute multi-step tasks | Tool calling, ReAct, human-in-the-loop, durable execution | ⭐⭐⭐⭐ | ✅ |
| 5 | [LLM Evaluation & Benchmark Platform](./llm-eval-benchmark-platform/) | Automated regression evaluation, red-teaming, RAG triad, and ELO benchmarking | LLM-as-a-Judge, Evol-Instruct, ELO Rating, self-consistency | ⭐⭐⭐⭐ | ✅ |
| 6 | [Semantic Retrieval Platform](./semantic-retrieval-platform/) | Low-latency, permission-aware retrieval APIs for RAG apps | Hybrid retrieval, ACL filtering, reranking, index lifecycle | ⭐⭐⭐⭐ | ⚠️ |
| 7 | [LLM Inference Serving Engine](./llm-inference-serving-engine/) | High-throughput, low-latency LLM serving API | Continuous batching, PagedAttention KV cache, Tensor Parallelism | ⭐⭐⭐⭐⭐ | ✅ |
| 8 | [Multi-Tenant Enterprise RAG](./multi-tenant-enterprise-rag/) | Enterprise RAG with strict ACLs and tenant isolation | Single-stage ACL filtering, hybrid search, cross-encoder reranking | ⭐⭐⭐⭐⭐ | ✅ |

---

## 🗂️ Project Structure (per project)

Each project follows this layout:

```
<system-name>/
├── PROBLEM.md            # Problem statement and scope
├── APPROACH.md           # How to approach the design
├── DESIGN.md             # Full system design document
└── diagrams/             # Mermaid (.mmd) architecture diagrams
```

### GenAI-Specific Design Sections

In addition to the standard HLD template, each GenAI project includes:

| Section | What to Cover |
|---------|---------------|
| **Model Selection & Routing** | Which LLM(s), why, and how requests are routed |
| **RAG Pipeline** | Ingestion, chunking, embedding, retrieval, reranking (if applicable) |
| **Safety & Guardrails** | Input/output filtering, hallucination mitigation, toxicity checks |
| **Evaluation & Observability** | Metrics, feedback loops, A/B testing, red-teaming |
| **Cost & Latency Analysis** | Token budgets, caching strategies, scaling economics |

---

## 🔗 Cross-References

- **GenAI Concepts**: [00-concepts](../00-concepts/) — building blocks used across these systems
- **GenAI LLD Components**: [01-llm-lld-projects](../01-llm-lld-projects/) — individual components that compose these systems
- **Classical HLD Projects**: [04-hld-projects](../../04-hld-projects/) — traditional system designs for comparison
- **Classical HLD Concepts**: [03-hld-concepts](../../03-hld-concepts/) — distributed systems foundations

---

*All 8 GenAI HLD projects are available! Pick the system closest to your interview prompt and start designing. 🚀*
