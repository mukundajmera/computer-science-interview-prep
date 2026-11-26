# 📋 GenAI HLD Design Template

Use this template as a framework for designing LLM-powered systems in interviews. It extends the [standard HLD Design Template](../../04-hld-projects/DESIGN-TEMPLATE.md) with GenAI-specific sections.

---

## 1. 📝 Requirements Clarification

### Functional Requirements
*What should the system do?*

- [ ] Core feature 1: ___
- [ ] Core feature 2: ___
- [ ] Core feature 3: ___
- [ ] Core feature 4: ___

### Non-Functional Requirements
*How should the system behave?*

| Requirement | Target |
|-------------|--------|
| Availability | ___% (e.g., 99.9%) |
| Latency (first token) | ___ ms |
| Latency (full response) | ___ ms |
| Throughput | ___ QPS |
| Data durability | ___ |
| Consistency | Strong / Eventual |

### GenAI-Specific Requirements

| Requirement | Target |
|-------------|--------|
| Response quality | ___ (e.g., groundedness > 90%) |
| Hallucination rate | < ___% |
| Safety / toxicity | ___ |
| Max context window | ___ tokens |
| Max output length | ___ tokens |
| Cost per query | < $___ |

### Assumptions
- 
- 

### Out of Scope
- 
- 

---

## 2. 📊 Back-of-Envelope Estimation

### Users & Traffic

| Metric | Value | Calculation |
|--------|-------|-------------|
| Total users | ___ | |
| Daily Active Users (DAU) | ___ | |
| Requests per user per day | ___ | |
| Total daily requests | ___ | DAU × requests/user |
| QPS (Queries Per Second) | ___ | daily requests / 86400 |
| Peak QPS | ___ | QPS × 2–3 |

### Token & Model Traffic

| Metric | Value | Calculation |
|--------|-------|-------------|
| Avg input tokens / request | ___ | |
| Avg output tokens / request | ___ | |
| Daily input tokens | ___ | daily requests × input tokens |
| Daily output tokens | ___ | daily requests × output tokens |
| Peak tokens / second | ___ | |

### Storage

| Data Type | Size | Count/Day | Daily Storage | Yearly Storage |
|-----------|------|-----------|---------------|----------------|
| Documents / knowledge base | ___ | ___ | ___ | ___ |
| Embeddings / vectors | ___ | ___ | ___ | ___ |
| Conversation logs | ___ | ___ | ___ | ___ |
| **Total** | | | ___ | ___ |

### Cost Estimation

| Component | Unit Cost | Daily Volume | Daily Cost | Monthly Cost |
|-----------|-----------|-------------|------------|--------------|
| LLM inference (input) | $___/1M tokens | ___ tokens | $___ | $___ |
| LLM inference (output) | $___/1M tokens | ___ tokens | $___ | $___ |
| Embedding | $___/1M tokens | ___ tokens | $___ | $___ |
| Vector DB hosting | | | | $___ |
| **Total** | | | $___ | $___ |

---

## 3. 🔌 API Design

### Endpoint 1: ___

```
[METHOD] /api/v1/resource

Headers:
  Authorization: Bearer <token>
  X-Request-ID: <uuid>

Request:
{
    "query": "...",
    "context": { ... }
}

Response (streaming SSE):
data: {"type": "chunk", "content": "..."}
data: {"type": "chunk", "content": "..."}
data: {"type": "done", "metadata": { "tokens_used": 150, "sources": [...] }}

Errors:
- 400: Bad Request (invalid input)
- 401: Unauthorized
- 429: Rate Limited / Token Budget Exceeded
- 500: Internal Server Error
- 503: Model Unavailable
```

---

## 4. 🗄️ Data Model

### Database Choices
- **Relational DB**: ___ (metadata, users, configs)
- **Vector DB**: ___ (embeddings for retrieval)
- **Cache**: ___ (session state, hot data)
- **Object Store**: ___ (raw documents, artifacts)

### Schema Design

**Table 1: ___**
```
{
    id:           uuid (PK)
    field1:       type
    field2:       type
    created_at:   timestamp
}

Indexes:
- id (primary)
- field1 (for lookups)
```

**Vector Store Collection: ___**
```
{
    id:           string
    embedding:    float[DIMS]
    content:      text
    metadata:     json { source, page, chunk_index }
}
```

---

## 5. 🏗️ High-Level Architecture

### Component Diagram

```
┌──────────────────────────────────────────────────────────┐
│                        Clients                           │
│              (Web, Mobile, IDE, API)                     │
└──────────────────────────┬───────────────────────────────┘
                           │
                           ▼
              ┌────────────────────────┐
              │  API Gateway / LB      │
              │  (Auth, Rate Limit)    │
              └───────────┬────────────┘
                          │
         ┌────────────────┼────────────────┐
         ▼                ▼                ▼
   ┌──────────┐    ┌──────────┐    ┌──────────┐
   │ App      │    │ App      │    │ App      │
   │ Server   │    │ Server   │    │ Server   │
   └─────┬────┘    └────┬─────┘    └────┬─────┘
         │              │              │
    ┌────┴──────┬───────┴──────┬───────┘
    ▼           ▼              ▼
┌────────┐ ┌──────────┐ ┌──────────┐
│ Vector │ │  LLM     │ │ Metadata │
│ Store  │ │ Gateway  │ │ Store    │
└────────┘ └────┬─────┘ └──────────┘
                │
       ┌────────┼────────┐
       ▼        ▼        ▼
   ┌──────┐ ┌──────┐ ┌──────┐
   │Model │ │Model │ │Model │
   │  A   │ │  B   │ │  C   │
   └──────┘ └──────┘ └──────┘
```

### Data Flow

1. **Query Path**: Client → Gateway → App → Retriever → LLM → Streaming Response
2. **Ingestion Path**: Source → Processor → Chunker → Embedder → Vector Store

---

## 6. 🤖 GenAI Deep Dives

### 6.1 Model Selection & Routing

| Use Case | Model | Latency | Cost/1K tokens | Why |
|----------|-------|---------|----------------|-----|
| ___ | ___ | ___ ms | $___ | ___ |
| ___ | ___ | ___ ms | $___ | ___ |

**Routing Strategy**: ___

### 6.2 RAG Pipeline (if applicable)

| Stage | Approach | Details |
|-------|----------|---------|
| Document Ingestion | ___ | ___ |
| Chunking | ___ | Size: ___ tokens, overlap: ___ |
| Embedding | ___ | Model: ___, dims: ___ |
| Retrieval | ___ | Top-k: ___, method: ___ |
| Reranking | ___ | Model: ___ |
| Generation | ___ | Prompt template: ___ |

### 6.3 Safety & Guardrails

| Layer | Check | Action on Failure |
|-------|-------|-------------------|
| Input | ___ (e.g., prompt injection detection) | ___ |
| Retrieval | ___ (e.g., access control) | ___ |
| Output | ___ (e.g., hallucination check) | ___ |
| Output | ___ (e.g., toxicity filter) | ___ |

### 6.4 Evaluation & Observability

| Metric | How Measured | Target |
|--------|-------------|--------|
| Answer relevance | ___ | > ___% |
| Faithfulness / groundedness | ___ | > ___% |
| Latency (P50 / P99) | ___ | ___ ms / ___ ms |
| User satisfaction | ___ | > ___% |
| Cost per query | ___ | < $___ |

### 6.5 Cost & Latency Optimization

| Technique | Impact | Trade-off |
|-----------|--------|-----------|
| Semantic caching | ___ | ___ |
| Model routing (small → large) | ___ | ___ |
| Prompt compression | ___ | ___ |
| Batch inference | ___ | ___ |

---

## 7. 🔍 Classical Deep Dives

### 7.1 Scaling Strategy
- Horizontal scaling: ___
- Auto-scaling triggers: ___

### 7.2 Caching

| Cache Layer | What to Cache | TTL | Invalidation |
|-------------|---------------|-----|--------------|
| Semantic cache | ___ | ___ | ___ |
| Session/context | ___ | ___ | ___ |
| Application | ___ | ___ | ___ |

### 7.3 Database & Partitioning
- Sharding strategy: ___
- Replication: ___

---

## 8. ⚖️ Trade-offs

### Decision 1: ___

| Option A | Option B |
|----------|----------|
| Pros: | Pros: |
| Cons: | Cons: |

**Chose:** ___ because ___

### Decision 2: ___

| Option A | Option B |
|----------|----------|
| Pros: | Pros: |
| Cons: | Cons: |

**Chose:** ___ because ___

---

## 9. ⚠️ LLM-Specific Risks

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| Hallucination | ___ | ___ | ___ |
| Prompt injection | ___ | ___ | ___ |
| Data leakage | ___ | ___ | ___ |
| Model degradation | ___ | ___ | ___ |
| Cost overrun | ___ | ___ | ___ |

---

## 10. 🔮 Follow-up Questions

### Scaling
- **What if traffic increases 10x?** ___
- **What if we go multi-region?** ___

### LLM-Specific
- **What if the model provider has an outage?** ___
- **How do you handle model version upgrades?** ___
- **How do you reduce hallucinations further?** ___

### Feature Extensions
- **How would you add ___?** ___

---

## 📌 Interview Checklist

Before wrapping up, verify:

- [ ] Requirements clearly defined (functional + non-functional + GenAI-specific)
- [ ] Token budget and cost estimation make sense
- [ ] API covers core functionality (including streaming)
- [ ] Data model includes vector store schema
- [ ] Architecture diagram shows LLM integration clearly
- [ ] Model selection justified with latency/cost trade-offs
- [ ] RAG pipeline stages defined (if applicable)
- [ ] Safety guardrails at input and output layers
- [ ] Evaluation metrics and observability planned
- [ ] Cost analysis with token budgets
- [ ] LLM-specific risks identified with mitigations
- [ ] Scaling approach is concrete
- [ ] Trade-offs discussed with justification
- [ ] Can answer follow-up questions

---

*Copy this template for each GenAI system you practice! See also the [standard HLD template](../../04-hld-projects/DESIGN-TEMPLATE.md) for classical systems.*
