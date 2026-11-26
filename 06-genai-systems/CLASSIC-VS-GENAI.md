# ⚖️ Classic vs GenAI System Design

> **GenAI system design interviews build on everything you know about classical distributed systems — then introduce entirely new dimensions.** Token economics, non-determinism, safety guardrails, and LLM evaluation don't replace traditional concerns like scalability and availability; they layer on top. This guide maps exactly what changes, what stays the same, and how to bridge the two in an interview.

---

## 📑 Table of Contents

- [Side-by-Side Comparison](#-side-by-side-comparison)
- [What Stays the Same](#what-stays-the-same)
- [What's New in GenAI SD](#-whats-new-in-genai-sd)
- [Interview Strategy: Bridging Classic and GenAI](#-interview-strategy-bridging-classic-and-genai)
- [Cross-Links](#-cross-links)

---

## 📊 Side-by-Side Comparison

| Dimension | Classic SD | GenAI SD |
|-----------|-----------|----------|
| **Core Challenge** | Scalability, availability, consistency | + Non-determinism, safety, cost per token |
| **Estimation** | QPS, storage, bandwidth | + Token counts, model costs, inference latency budget |
| **Data Flow** | Request → Service → DB → Response | + Retrieval → LLM inference → Safety filter → Response |
| **Caching** | Key-value caching (Redis, Memcached) | + Semantic caching, KV-cache reuse, prompt caching |
| **Scaling** | Horizontal scaling, sharding, replication | + GPU provisioning, model routing, request batching |
| **Failure Modes** | Server crash, network partition, data corruption | + Hallucinations, prompt injection, model drift, toxic output |
| **Evaluation** | Uptime, latency percentiles (p50/p99), error rates | + Quality metrics (BLEU/ROUGE), human eval, LLM-as-judge |
| **Cost Model** | Compute + storage + bandwidth | + Per-token pricing, model tier costs, GPU-hour costs |
| **Safety** | Authentication, authorization, rate limiting | + Content filtering, PII detection, toxicity checks, bias mitigation |
| **Data Model** | SQL/NoSQL schemas, indexes | + Embeddings, vector stores, prompt templates, conversation history |
| **Communication** | REST, gRPC, WebSocket | + Streaming (SSE), function calling, tool use protocols |
| **Trade-offs** | Consistency vs availability (CAP) | + Cost vs quality vs latency triangle |

---

<a id="what-stays-the-same"></a>

## 🏗️ What Stays the Same

GenAI systems are still distributed systems. These fundamentals apply directly:

| Fundamental | How It Applies in GenAI |
|-------------|------------------------|
| **Load Balancing** | Distribute inference requests across GPU pools; model-aware routing |
| **Caching** | Exact-match and semantic caching reduce redundant LLM calls |
| **Monitoring & Observability** | Trace prompt flows, track token usage, alert on quality drift |
| **API Design** | RESTful endpoints for sync calls, SSE/WebSocket for streaming |
| **Data Modeling** | Still need relational data for users, sessions, audit logs |
| **Message Queues** | Async inference pipelines, feedback ingestion, batch processing |
| **Rate Limiting** | Token-based rate limiting in addition to request-based |
| **Database Selection** | SQL for metadata, NoSQL for sessions, vector DB for embeddings |

> **Key insight:** Don't throw away your classical SD knowledge — you'll use 70–80% of it in every GenAI design. The remaining 20–30% is what makes GenAI interviews unique.

---

## 🔬 What's New in GenAI SD

These are the dimensions that don't exist (or are radically different) in classical system design:

### 1. The LLM Pipeline as a First-Class Component

In classical SD, the "compute" step is usually a stateless service calling a database. In GenAI SD, the LLM pipeline is a complex, multi-stage component:

```
Query → Retrieval → Reranking → Prompt Assembly → LLM Inference → Output Parsing → Safety Check
```

Each stage has its own latency, failure modes, and tuning knobs. You need to discuss the pipeline as deliberately as you would discuss a database schema in classical SD.

### 2. Token Economics and Cost Awareness

Classical SD estimation focuses on QPS, storage, and bandwidth. GenAI adds a **cost-per-request** dimension that can dominate your budget:

| Model Tier | Input Cost (per 1M tokens) | Output Cost (per 1M tokens) | Typical Use |
|------------|---------------------------|----------------------------|-------------|
| Small (GPT-3.5, Haiku) | ~$0.25 | ~$1.25 | Classification, routing, simple generation |
| Medium (GPT-4o-mini, Sonnet) | ~$3.00 | ~$15.00 | Complex generation, reasoning |
| Large (GPT-4, Opus) | ~$30.00 | ~$60.00 | Expert reasoning, critical decisions |

A 10× model upgrade can mean a 10–100× cost increase. Interviewers expect you to factor this into your design.

### 3. Safety and Guardrails as Mandatory

In classical SD, safety is primarily authentication and authorization. In GenAI SD, safety is a multi-layered system concern:

- **Input guardrails** — Prompt injection detection, PII scrubbing, topic boundary enforcement
- **Output guardrails** — Toxicity filtering, factuality verification, format validation
- **Policy engine** — Configurable rules that can be updated without redeployment
- **Audit trail** — Every prompt and response logged for compliance

Skipping this in an interview is like skipping authentication in a classical design — it signals a gap in your understanding.

### 4. Evaluation as a Continuous Process

Classical systems have well-defined correctness: the API returns the right data or it doesn't. GenAI output quality is subjective and multi-dimensional:

| Evaluation Layer | Method | When |
|-----------------|--------|------|
| **Offline** | Benchmark datasets, BLEU/ROUGE, accuracy | Before deployment |
| **Online — automated** | LLM-as-judge, consistency checks, format validation | Every request |
| **Online — human** | Human review queues, thumbs up/down, expert audit | Sampled or low-confidence |
| **A/B testing** | Side-by-side model/prompt comparison | Prompt or model changes |

You need all four layers, and you need to explain how feedback loops connect them.

### 5. Non-Determinism as a Design Constraint

Classical services are deterministic: same input → same output. LLMs are inherently probabilistic, which means:

- **Output validation** is mandatory (schema checks, format enforcement)
- **Retry logic** must handle semantic failures, not just HTTP errors
- **Confidence scoring** enables routing between automated and human paths
- **Temperature tuning** trades creativity for consistency based on use case
- **Structured output** (JSON mode, function calling) constrains the output space

Your architecture must explicitly account for the fact that the LLM might produce different — and sometimes wrong — output on every call.

---

## 🎯 Interview Strategy: Bridging Classic and GenAI

Use this approach to structure any GenAI system design answer:

### Step 1 — Start with Classic SD Structure

Begin exactly as you would in a classical interview:

1. **Clarify requirements** (functional + non-functional)
2. **Estimate scale** (QPS, storage, users)
3. **Define API contracts**
4. **Sketch high-level architecture** (clients, services, databases)

This shows the interviewer you have a solid foundation.

### Step 2 — Layer GenAI-Specific Concerns

Once the classical skeleton is in place, extend it:

1. **Add token & cost estimation** alongside QPS and storage estimates
2. **Insert the LLM pipeline** as a dedicated component (not a black box)
3. **Add safety layers** on both input and output paths
4. **Introduce vector stores** alongside traditional databases
5. **Discuss model selection** and routing strategy

### Step 3 — Address the GenAI Trade-off Triangle

Every GenAI design involves balancing three competing concerns:

```
        Cost
       /    \
      /      \
   Quality ── Latency
```

- **Cost ↔ Quality**: Bigger models produce better output but cost more
- **Cost ↔ Latency**: Caching reduces cost and latency but may serve stale results
- **Quality ↔ Latency**: Reranking and multi-step reasoning improve quality but add latency

State your trade-off choices explicitly: *"We prioritize quality over latency for this use case because…"*

### Step 4 — Close with Evaluation & Observability

End your design with:

- How you **measure quality** (offline metrics + online signals)
- How you **monitor costs** (per-request token tracking, budget alerts)
- How you **detect drift** (quality degradation over time)
- How you **iterate** (A/B testing prompts and models)

This closing section is what separates strong candidates from average ones.

---

## 🔗 Cross-Links

| Resource | Why It Helps |
|----------|-------------|
| [GenAI SD Framework](./GENAI-SD-FRAMEWORK.md) | The 6-step interview framework that operationalizes this comparison |
| [Top Interview Pitfalls](./PITFALLS.md) | The 10 most common mistakes when candidates miss GenAI-specific concerns |
| [GenAI Concepts](./00-concepts/) | Deep dives into RAG, safety, evaluation, model routing, and more |
| [GenAI HLD Projects](./02-llm-hld-projects/) | Full system designs that demonstrate the GenAI SD approach |
| [Classical HLD Concepts](../03-hld-concepts/) | The distributed systems foundations that GenAI SD builds on |
| [Classical HLD Projects](../04-hld-projects/) | Classical system designs for comparison and reference |

---

*Master both classical and GenAI system design — the best candidates show fluency in both and seamlessly bridge the gap during interviews.*
