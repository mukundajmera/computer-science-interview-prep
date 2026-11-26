# 📚 GenAI Concepts & Patterns

Core concepts and trade-offs for designing LLM-powered systems. Each topic builds on classical distributed systems knowledge from [03-hld-concepts](../../03-hld-concepts/) and adds GenAI-specific depth.

---

## 📋 Concept Index

| Concept | Description | Classical Tie-in | Status |
|---------|-------------|------------------|--------|
| [RAG Architecture](./rag-architecture/) | Retriever/generator split, indexing, chunking, vector DB, ranking | [Caching](../../03-hld-concepts/caching/), [Message Queues](../../03-hld-concepts/message-queues/) | ✅ |
| [LLM-Oriented System Design](./llm-system-design/) | Mapping system design steps to LLM apps, token budgets, KV cache | [Load Balancing](../../03-hld-concepts/load-balancing/), [Caching](../../03-hld-concepts/caching/) | ✅ |
| [Prompting, Tools & Agents](./prompting-tools-agents/) | Prompt construction, function calling, agent loops, idempotent tools | [API Gateway](../../03-hld-concepts/api-gateway/), [Message Queues](../../03-hld-concepts/message-queues/) | ✅ |
| [Safety & Governance](./safety-governance/) | Hallucination mitigation, toxicity, PII handling, red-teaming | [Rate Limiting](../../03-hld-concepts/rate-limiting/), [Monitoring](../../03-hld-concepts/monitoring-observability/) | ✅ |
| [LLM Evaluation](./llm-evaluation/) | Offline/online eval, LLM-as-judge, golden sets, attack success rate | [Monitoring](../../03-hld-concepts/monitoring-observability/) | ✅ |
| [Model Generalization](./ml-generalization/) | Slice quality, drift diagnostics, calibration framing for production ML/LLM systems | [Monitoring](../../03-hld-concepts/monitoring-observability/), [Rate Limiting](../../03-hld-concepts/rate-limiting/) | ✅ |
| [Safety, Evaluation & Governance](./safety-eval/) | Attack surfaces, safety taxonomies, risk categories, evaluation metrics & benchmarks | [Monitoring](../../03-hld-concepts/monitoring-observability/), [Rate Limiting](../../03-hld-concepts/rate-limiting/) | ✅ |
| [Vector Databases](./vector-databases/) | Storing and querying embeddings at scale, ANN indexes, similarity metrics | [Database Sharding](../../03-hld-concepts/database-sharding/) | ✅ |
| [Model Routing & Orchestration](./model-routing-orchestration/) | Multi-model selection, cascading, fallback, orchestration patterns | [Load Balancing](../../03-hld-concepts/load-balancing/) | ✅ |
| [Streaming & KV-Cache](./streaming-kv-cache/) | Token-by-token delivery, KV-Cache, prompt & semantic caching, shared prefix/KV cache lifecycle & multi-tenant isolation | [Caching](../../03-hld-concepts/caching/), [CDN](../../03-hld-concepts/cdn/) | ✅ |
| [Token Economics: Cost & Latency](./token-cost-latency/) | BPE tokenization, cost modeling, latency breakdown, optimization | [Rate Limiting](../../03-hld-concepts/rate-limiting/), [Monitoring](../../03-hld-concepts/monitoring-observability/) | ✅ |
| [GenAI Design Patterns](./genai-design-patterns/) | RAG, Agent Loop, CoT, Guardrail Sandwich, Router, HITL, Feedback Loop | [All HLD Concepts](../../03-hld-concepts/) | ✅ |
| [Model Adaptation & LoRA](./model-adaptation-lora/) | Full FT vs PEFT, Intrinsic Dimensionality, QLoRA, Multi-Tenant LoRA Serving | [Caching](../../03-hld-concepts/caching/), [Monitoring](../../03-hld-concepts/monitoring-observability/) | ✅ |
| [RoPE Positional Embedding](./rope-positional-embedding/) | Absolute vs relative position, rotation matrix, NTK/YaRN context scaling | [Streaming & KV-Cache](./streaming-kv-cache/) | ✅ |

---

## 🧭 Suggested Learning Order

```
1. RAG Architecture           → Foundation for most GenAI systems
2. LLM-Oriented System Design → Mapping classical SD steps to LLM apps
3. Prompting, Tools & Agents  → Prompt engineering and agentic patterns
4. Safety & Governance        → Production readiness and compliance
5. LLM Evaluation             → Measuring quality and trustworthiness
6. Model Generalization       → Drift, slice quality, and rollout safety
7. Safety, Eval & Governance  → Attack surfaces, taxonomies, metrics & benchmarks
8. Vector Databases           → Core storage for RAG
9. Model Routing              → Multi-model orchestration
10. Streaming & KV-Cache      → Performance optimization
11. Token Economics           → Cost and latency modeling
12. GenAI Design Patterns     → Recurring architectural solutions
13. Model Adaptation & LoRA   → PEFT, QLoRA and multi-tenant serving
14. RoPE Positional Embedding → Scaling context windows via relative rotation
```

---

## 🔗 Cross-References

- **Classical HLD Concepts**: [03-hld-concepts](../../03-hld-concepts/) — load balancing, caching, sharding, queues
- **GenAI LLD Components**: [01-llm-lld-projects](../01-llm-lld-projects/) — hands-on practice building the components described here
- **GenAI HLD Systems**: [02-llm-hld-projects](../02-llm-hld-projects/) — full system designs that apply these concepts

---

*Fourteen core concepts are live (✅). Check back or contribute! 🚀*
