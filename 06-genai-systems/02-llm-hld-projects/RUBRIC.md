# GenAI HLD — Interview Scoring Rubric

A structured rubric for evaluating GenAI / LLM system design interviews across 8 dimensions, each scored from 1 (Poor) to 5 (Strong). This rubric extends the [classical HLD rubric](../../04-hld-projects/url-shortener/RUBRIC.md) with GenAI-specific dimensions.

> **Applies to:** [Document Q&A RAG](./document-qa-rag/) · [Multi-Tenant Chat Assistant](./multi-tenant-chat-assistant/) · [AI Coding Copilot](./ai-coding-copilot/) · [Agentic Workflow Orchestrator](./agentic-workflow-orchestrator/) · [LLM Eval & Safety Platform](./llm-evaluation-safety-platform/) · [LLM Safety & Eval (Governance)](./llm-safety-eval-platform/) · [Semantic Retrieval Platform](./semantic-retrieval-platform/)

---

## Scoring Overview

| # | Dimension | Weight | Key Signal |
|---|-----------|--------|------------|
| 1 | Requirements & Scope | 10% | Clarifying questions, GenAI-specific NFRs (latency, cost, safety) |
| 2 | Estimation & Cost Modeling | 10% | Token math, cost per query, latency budget, GPU/infra sizing |
| 3 | API & Prompt Design | 10% | REST/streaming endpoints, prompt templates, tool schemas |
| 4 | Data Model & RAG Pipeline | 15% | Embedding storage, chunk schema, conversation state, retrieval flow |
| 5 | Architecture | 20% | Components, data flow, model placement, serving infrastructure |
| 6 | GenAI Deep Dives | 20% | Model selection, RAG tuning, safety guardrails, evaluation, caching |
| 7 | Safety, Evaluation & Governance | 10% | Guardrail sandwich, hallucination mitigation, red-teaming, compliance |
| 8 | Trade-offs & Communication | 5% | Cost-quality-latency triangle, justification, clear explanation |

---

## 1. Requirements & Scope

| Score | Descriptor |
|-------|------------|
| **1 — Poor** | Jumps into design without clarifying GenAI-specific constraints. Does not ask about model choice, latency SLA, safety requirements, or cost budget. Treats the system like a classical CRUD app. |
| **3 — Acceptable** | Asks about user volume, model preference (hosted vs self-hosted), latency targets, and basic safety needs. Identifies core functional requirements and mentions at least two non-functional requirements (availability, cost). Distinguishes what is in/out of scope. |
| **5 — Strong** | Systematically clarifies: DAU, concurrent sessions, response latency SLA, monthly token/cost budget, safety/compliance requirements (PII, regulated industry?), multi-tenancy needs, evaluation requirements. Separates functional (chat, search, code completion) from non-functional (p99 latency, cost ceiling, safety SLA). Explicitly scopes out items like fine-tuning, training, billing. |

---

## 2. Estimation & Cost Modeling

| Score | Descriptor |
|-------|------------|
| **1 — Poor** | No estimation of token volume, cost, or latency. Cannot reason about input vs output token costs. No sense of model pricing. |
| **3 — Acceptable** | Estimates daily request volume and average tokens per request. Calculates approximate daily cost for one model tier. Mentions that output tokens cost more than input tokens. Gives a rough latency budget (TTFT + generation). |
| **5 — Strong** | Derives full cost model: requests/day × avg input tokens × input price + avg output tokens × output price. Compares at least two model tiers (e.g., GPT-4o vs GPT-4o-mini) with concrete numbers. Computes cache hit rate impact on cost. Breaks down latency: network RTT + TTFT (prefill) + token generation (output_tokens / TPS). Estimates embedding costs for RAG systems. Identifies that model routing can save 40–70% cost. |

---

## 3. API & Prompt Design

| Score | Descriptor |
|-------|------------|
| **1 — Poor** | No API definition. No mention of streaming. Prompt engineering is an afterthought. No tool/function calling schema. |
| **3 — Acceptable** | Defines key REST endpoints (e.g., `POST /chat`, `POST /search`). Mentions streaming via SSE. Shows a basic prompt template with system prompt + user message. Mentions at least one tool schema if agents are involved. |
| **5 — Strong** | Provides versioned API with streaming and non-streaming modes. Shows complete prompt template with system prompt, context injection slots, and few-shot examples. Discusses prompt compression techniques. Defines tool/function calling schemas with parameter types. Addresses idempotency for tool calls. Mentions prompt versioning and A/B testing. |

---

## 4. Data Model & RAG Pipeline

| Score | Descriptor |
|-------|------------|
| **1 — Poor** | No data model for embeddings, conversations, or documents. Ignores the retrieval pipeline. No mention of vector databases. |
| **3 — Acceptable** | Defines schemas for documents/chunks, embeddings, and conversations. Chooses a vector database with brief rationale. Describes the indexing pipeline: ingest → chunk → embed → store. Mentions basic retrieval (top-k similarity). |
| **5 — Strong** | Complete schemas for: document corpus (chunks with metadata), embedding index (with dimension, distance metric), conversation history (session, turns, token counts), user preferences. Describes a two-stage retrieval pipeline: bi-encoder recall → cross-encoder reranking. Discusses chunking strategy (size, overlap, semantic). Addresses metadata filtering in vector search. Explains hybrid search (dense + sparse). Covers multi-tenant data isolation. |

---

## 5. Architecture

| Score | Descriptor |
|-------|------------|
| **1 — Poor** | Single box labeled "LLM." No distinction between retrieval, generation, and safety layers. Missing core components (vector DB, cache, queue). |
| **3 — Acceptable** | Shows a layered architecture: client → API gateway → orchestrator → retrieval → LLM → response. Includes vector database, cache, and a safety filter. Separates the indexing pipeline from the serving pipeline. Mentions a message queue for async tasks. |
| **5 — Strong** | Complete architecture with: API gateway (rate limiting, auth) → orchestrator → router (model selection) → retrieval pipeline (embed → vector DB → reranker) → prompt assembly → LLM (with streaming) → safety post-filter → response. Includes: async indexing pipeline (source → chunker → embedder → vector DB), feedback collection pipeline (Kafka → analytics), cache layers (semantic cache, KV-cache/prefix caching), monitoring & tracing. Separates control plane (config, model registry) from data plane (serving). Shows multi-region or edge deployment if relevant. |

---

## 6. GenAI Deep Dives

| Score | Descriptor |
|-------|------------|
| **1 — Poor** | Cannot explain model selection rationale. No discussion of RAG quality, caching, or streaming. Treats the LLM as a black box. |
| **3 — Acceptable** | Explains why a specific model was chosen (cost, quality, context window). Discusses at least one of: RAG chunking strategy, caching (semantic or prefix), streaming (SSE). Mentions model routing as a cost optimization. |
| **5 — Strong** | Covers 3+ deep dives with depth comparable to a senior engineer: **Model selection** — compares models on cost/quality/latency, recommends routing strategy. **RAG quality** — chunking strategy, embedding model choice, reranking, lost-in-the-middle mitigation. **Caching** — semantic cache for repeated queries, prefix caching for shared system prompts, KV-cache management (PagedAttention). **Streaming** — SSE implementation, backpressure handling, token aggregation for safety checks. **Agentic patterns** — ReAct loop, tool calling, max-iteration guards, durable execution. Discusses at least two with concrete trade-offs. |

---

## 7. Safety, Evaluation & Governance

| Score | Descriptor |
|-------|------------|
| **1 — Poor** | No mention of safety, hallucination, or evaluation. Ignores that LLMs can produce harmful or incorrect output. |
| **3 — Acceptable** | Mentions the guardrail sandwich (pre-filter → LLM → post-filter). Identifies hallucination as a risk and suggests citations/grounding. Proposes at least one evaluation metric (e.g., relevance, correctness). Mentions logging for monitoring. |
| **5 — Strong** | Designs a complete safety pipeline: input validation (toxicity, PII detection, jailbreak patterns) → LLM generation → output validation (factual grounding check, PII redaction, policy compliance). Proposes an evaluation strategy: offline eval (golden sets, LLM-as-judge), online eval (user feedback, A/B testing). Discusses red-teaming and attack surface (prompt injection, data poisoning). Mentions compliance requirements (EU AI Act, SOC2) if relevant. Connects safety metrics to dashboards and alerting. |

---

## 8. Trade-offs & Communication

| Score | Descriptor |
|-------|------------|
| **1 — Poor** | Makes choices without explaining why. Cannot articulate the cost-quality-latency triangle. Answers are disorganized. |
| **3 — Acceptable** | Explains at least two trade-offs (e.g., model size vs cost, accuracy vs latency). Communicates the design in a logical order. Responds adequately to follow-ups. |
| **5 — Strong** | Proactively surfaces the cost-quality-latency triangle at each decision. Articulates the evolution path (v1 single model → v2 RAG + caching → v3 multi-model routing + eval). Discusses build vs buy (managed API vs self-hosted). Mentions when to use fine-tuning vs RAG vs prompt engineering. Communicates clearly with diagrams and time awareness. |

---

## Quick Calibration Guide

| Total Score (out of 40) | Rating | Recommendation |
|--------------------------|--------|----------------|
| 34–40 | 🟢 Strong Hire | Demonstrates GenAI systems expertise across all dimensions |
| 26–33 | 🟡 Hire | Solid fundamentals with minor gaps in GenAI depth |
| 18–25 | 🟠 Lean No Hire | Understands basics but missing critical GenAI-specific depth |
| 8–17 | 🔴 No Hire | Significant gaps in both classical and GenAI design thinking |

---

## GenAI vs Classical HLD — What's Different?

| Classical HLD | GenAI HLD Addition |
|---------------|-------------------|
| Traffic estimation (QPS) | Token estimation (input + output tokens/day, cost/day) |
| Database schema | Embedding schema + vector DB + chunking strategy |
| Caching (Redis, CDN) | Semantic caching, prefix caching, KV-cache |
| Load balancing | Model routing (complexity-based, cost-aware) |
| Monitoring (latency, errors) | LLM-specific metrics (TTFT, TPS, hallucination rate, safety incidents) |
| API design | Prompt design + tool schemas + streaming |
| Security (auth, encryption) | Safety (guardrails, PII, jailbreak defense, red-teaming) |
| Testing (unit, integration) | Evaluation (golden sets, LLM-as-judge, A/B testing) |

---

## 🔗 See Also
- [GenAI SD Framework](../GENAI-SD-FRAMEWORK.md) — 6-step interview approach
- [Classic vs GenAI Comparison](../CLASSIC-VS-GENAI.md) — side-by-side differences
- [GenAI Interview Pitfalls](../PITFALLS.md) — common mistakes
- [Token Economics](../00-concepts/token-cost-latency/) — cost modeling deep dive
- [Safety & Governance](../00-concepts/safety-governance/) — safety patterns
- [LLM Evaluation](../00-concepts/llm-evaluation/) — evaluation strategies
- [GenAI Design Patterns](../00-concepts/genai-design-patterns/) — pattern catalog

---

*Use this rubric alongside individual project design docs for calibration and the [GenAI Pitfalls](../PITFALLS.md) guide to identify common failure modes.*
