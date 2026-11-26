# 📋 GenAI HLD Design Template

> Extends the classical [HLD Design Template](../../04-hld-projects/DESIGN-TEMPLATE.md) with GenAI-specific sections for LLM-powered system designs.

Use this template as a framework for practicing **GenAI system design interviews**. It retains every classical HLD section and adds five GenAI-specific deep dives.

**Related Concept Docs:**
[RAG Architecture](../00-concepts/rag-architecture/) · [LLM System Design](../00-concepts/llm-system-design/) · [Prompting, Tools & Agents](../00-concepts/prompting-tools-agents/) · [Safety & Governance](../00-concepts/safety-governance/) · [LLM Evaluation](../00-concepts/llm-evaluation/)

---

## 1. 📝 Requirements Clarification

### Functional Requirements
*What should the system do?*

- [ ] Core GenAI feature 1: ___ (e.g., conversational Q&A)
- [ ] Core GenAI feature 2: ___ (e.g., document summarization)
- [ ] Core GenAI feature 3: ___ (e.g., retrieval-augmented generation)
- [ ] Core GenAI feature 4: ___ (e.g., multi-turn chat with memory)

### Non-Functional Requirements
*How should the system behave?*

| Requirement | Target |
|-------------|--------|
| Availability | ___% (e.g., 99.9%) |
| Latency (P50 / P99) | ___ ms / ___ ms (time to first token / full response) |
| Throughput | ___ QPS |
| Token budget per request | ___ tokens (input + output) |
| Cost ceiling | $___/1K requests |
| Data privacy | PII handling: ___ |
| Consistency | Strong / Eventual |

### Assumptions
- Model provider (self-hosted / third-party API): ___
- Corpus size for retrieval: ___

### Out of Scope
- 

---

## 2. 📊 Back-of-Envelope Estimation

### Users & Traffic

| Metric | Value | Calculation |
|--------|-------|-------------|
| Total users | ___ | |
| Daily Active Users (DAU) | ___ | |
| Queries per user per day | ___ | |
| Total daily queries | ___ | DAU × queries/user |
| QPS (Queries Per Second) | ___ | daily queries / 86400 |
| Peak QPS | ___ | QPS × 2 or 3 |

### Token & Cost Estimation

| Metric | Value | Calculation |
|--------|-------|-------------|
| Avg input tokens/query | ___ | prompt + context |
| Avg output tokens/query | ___ | |
| Daily total tokens (in+out) | ___ | daily queries × avg tokens |
| Cost per 1K input/output tokens | $___/$___ | per model pricing |
| **Daily / Monthly LLM cost** | $___/$___ | |

### Storage

| Data Type | Size | Count/Day | Daily Storage | Yearly Storage |
|-----------|------|-----------|---------------|----------------|
| Chat logs | ___ bytes | ___ | ___ | ___ |
| Embeddings | ___ bytes | ___ | ___ | ___ |
| Document chunks | ___ bytes | ___ | ___ | ___ |
| **Total** | | | ___ | ___ |

### Bandwidth

| Direction | Calculation | Result |
|-----------|-------------|--------|
| Incoming | QPS × avg request size | ___ MB/s |
| Outgoing | QPS × avg response size (streamed) | ___ MB/s |

---

## 3. 🔌 API Design

### Endpoint 1: Chat Completion

```
POST /api/v1/chat/completions

Request:
{
    "session_id": "uuid", "model": "gpt-4o", "stream": true,
    "messages": [{"role": "user", "content": "..."}],
    "max_tokens": 1024
}

Response (streamed):
{
    "id": "resp-uuid",
    "choices": [{"delta": {"content": "..."}, "finish_reason": null}],
    "usage": {"prompt_tokens": 512, "completion_tokens": 256}
}

Errors: 400 Bad Request · 429 Token Budget Exceeded · 503 Model Unavailable
```

### Endpoint 2: Document Ingestion (for RAG)

```
POST /api/v1/documents/ingest

Request:  { "source": "url|file|text", "content": "...", "metadata": {} }
Response: { "document_id": "uuid", "chunks_created": 42, "status": "indexed" }
```

### Endpoint 3: ___

```
[METHOD] /api/v1/resource
Request:  { }
Response: { }
```

---

## 4. 🗄️ Data Model

### Database Choice
- **Primary Database**: ___ (e.g., PostgreSQL) · **Vector Store**: ___ (e.g., pgvector / Pinecone)

### Schema Design

**conversations**
```
{
    id: uuid (PK), user_id: uuid (FK), model: string,
    system_prompt: text, created_at: timestamp, updated_at: timestamp
}
Indexes: id (primary), user_id (history lookups)
```

**messages**
```
{
    id: uuid (PK), conversation_id: uuid (FK),
    role: enum(system, user, assistant, tool), content: text,
    token_count: int, latency_ms: int, model: string, created_at: timestamp
}
Indexes: id (primary), conversation_id (thread retrieval)
```

**documents**
```
{
    id: uuid (PK), title: string, source_url: string,
    content_type: string, size_bytes: int,
    uploaded_by: uuid (FK → users), created_at: timestamp, updated_at: timestamp
}
Indexes: id (primary), uploaded_by, created_at
```

**document_chunks (Vector Store)**
```
{
    chunk_id: uuid (PK), document_id: uuid (FK → documents),
    content: text, embedding: vector(1536),
    metadata: jsonb, created_at: timestamp
}
Indexes: chunk_id (primary), embedding (HNSW), document_id
```

### Relationships
```
conversations (1) ── (n) messages    documents (1) ── (n) document_chunks
users         (1) ── (n) conversations
```

---

## 5. 🏗️ High-Level Architecture

```
┌──────────────────────────────────────────┐
│              Clients                     │
└──────────────────┬───────────────────────┘
                   ▼
      ┌────────────────────────┐
      │  API Gateway (Auth/RL) │
      └───────────┬────────────┘
     ┌────────────┼─────────────────┐
     ▼            ▼                 ▼
┌─────────┐ ┌───────────┐   ┌───────────┐
│ Safety  │ │Orchestrator│   │ Ingestion │
│ Filter  │▶│  Service   │   │ Pipeline  │
└─────────┘ └─────┬──────┘   └─────┬─────┘
         ┌────────┼────────┐       ▼
         ▼        ▼        │ ┌───────────┐
   ┌─────────┐┌────────┐  │ │  Vector   │
   │ Prompt  ││Retrieval│──┘ │  Store    │
   │ Builder ││Service  │    └───────────┘
   └────┬────┘└────────┘
        ▼
   ┌──────────┐
   │LLM Router├──┬──────┬──────┐
   └──────────┘  ▼      ▼      ▼
              [Mod A] [Mod B] [Mod C]
                  │
        ┌────────┴────────┐  ┌────────────────┐
        │ Semantic Cache   │  │ Logging & Eval │
        └─────────────────┘  └────────────────┘
```

### Data Flow

1. **Query Path (RAG):** Client → Gateway → Safety Filter → Orchestrator → Retrieval (embed → vector search) → Prompt Builder → LLM Router → Model → Safety Filter (output) → Client
2. **Ingestion Path:** Client → Gateway → Ingestion → Chunker → Embedder → Vector Store
3. **Streaming:** Model → SSE/WebSocket → Safety Filter (incremental) → Client

---

## 6. 🔍 Deep Dives — Classical

### 6.1 Scaling Strategy

**Horizontal:** API servers: ___ · GPU fleet / API rate limits: ___ · Vector Store: ___

### 6.2 Caching Approach

| Cache Layer | What to Cache | TTL | Invalidation |
|-------------|---------------|-----|--------------|
| Semantic cache | Similar queries → responses | ___ | Corpus update |
| Prompt template | Compiled system prompts | ___ | Deployment |
| Retrieval cache | Top-K chunk results | ___ | Re-index |

### 6.3 Database & Vector Store Partitioning

**Vector Store:** Shard key: ___ · Index: HNSW / IVF / PQ · Dimension: ___
**Replication:** Master: ___ · Replicas: ___ · Consistency: ___

---

## 7. 🔍 Deep Dives — GenAI-Specific

### 7.1 🎯 Token & Context Budget Planning

> See also: [Prompting, Tools & Agents](../00-concepts/prompting-tools-agents/)

**Context Window Allocation:**
```
┌─────────────────────────────────────────────┐
│           Context Window (___ tokens)        │
├─────────────┬──────────┬─────────┬──────────┤
│System Prompt│ Retrieved│  Chat   │  Output  │
│ (___ tk)    │ (___ tk) │ (___ tk)│ (___ tk) │
└─────────────┴──────────┴─────────┴──────────┘
```

| Budget Component | Allocation | Notes |
|------------------|-----------|-------|
| System prompt | ___ | Static; version-controlled |
| Retrieved context | ___ | Top-K chunks × avg chunk size |
| Conversation history | ___ | Sliding window / summarization |
| Output (max_tokens) | ___ | Capped per response |

**Cost-per-Query:**
```
Cost = (input_tokens/1K × input_price) + (output_tokens/1K × output_price)
Example: 2000 in × $0.005/1K + 500 out × $0.015/1K = $0.0175/query
```

**Overflow Strategy:**
- [ ] Truncate oldest history · Summarize with cheaper model
- [ ] Reduce Top-K chunks · Fallback to smaller context model

### 7.2 📚 RAG vs Fine-Tuning Decision

> See also: [RAG Architecture](../00-concepts/rag-architecture/)

| Criterion | RAG | Fine-Tuning | Prompt Eng. |
|-----------|-----|-------------|------------|
| Knowledge freshness | ✅ Real-time | ❌ Stale | ❌ Context-limited |
| Setup cost | Medium | High | Low |
| Per-query cost | Higher | Lower | Lowest |
| Domain adaptation | Good | Best | Limited |
| Hallucination ctrl | Good | Medium | Weak |
| Data privacy | Internal | Training data | In prompt |

**Decision:**
- [ ] **RAG** — because ___
- [ ] **Fine-Tuning** — because ___
- [ ] **Prompt Engineering** — because ___
- [ ] **Hybrid** — because ___

### 7.3 🔀 LLM Routing / Model Selection

> See also: [LLM System Design](../00-concepts/llm-system-design/)

| Model | Use Case | Context | Cost (in/out per 1K) | Latency |
|-------|----------|---------|----------------------|---------|
| ___ | Complex reasoning | ___ tokens | $___/$___ | ___ ms |
| ___ | Simple Q&A | ___ tokens | $___/$___ | ___ ms |
| ___ | Embeddings | N/A | $___/N/A | ___ ms |
| ___ | Fallback / local | ___ tokens | $___/$___ | ___ ms |

**Routing Strategy:**
```
User Query → Classify Intent → Simple? → Model B (fast/cheap)
                              → Complex? → Model A (powerful)
                              → Fail/Timeout → Model C (fallback)
```

**Fallback Chain:** Primary: ___ (___ ms) → Secondary: ___ (___ ms) → Fallback: ___

### 7.4 🛡️ Safety / Moderation / Red-Teaming Hooks

> See also: [Safety & Governance](../00-concepts/safety-governance/)

**Input Filters:**

| Check | Method | Action on Fail |
|-------|--------|---------------|
| Prompt injection | Classifier / regex | Block + log |
| PII detection | NER / regex patterns | Redact or reject |
| Toxicity | Moderation API | Block + alert |
| Jailbreak attempts | Canary tokens / classifier | Block + flag |

**Output Filters:**

| Check | Method | Action on Fail |
|-------|--------|---------------|
| Hallucination grounding | Cross-ref with sources | Add disclaimer |
| PII leakage | NER scan on output | Redact |
| Toxicity | Moderation API | Suppress + fallback |
| Off-topic / refusal | Classifier | Retry with guardrail |

**PII Handling:**
- [ ] Redact before sending to LLM · On-premise model for PII workloads
- [ ] Encrypt at rest, mask in logs · Retention policy: ___ days

**Red-Teaming:**
- [ ] Automated adversarial test suite · Periodic human reviews · Shadow mode for new deployments

### 7.5 📈 Evaluation and Feedback Loops

> See also: [LLM Evaluation](../00-concepts/llm-evaluation/)

**Offline Evaluation:**

| Metric | Method | Target |
|--------|--------|--------|
| Relevance | LLM-as-judge / human eval | ≥ ___% |
| Faithfulness | Claim verification vs sources | ≥ ___% |
| Retrieval recall@K | Ground-truth test set | ≥ ___% |
| Cost per query | Token accounting | ≤ $___ |

**Online Monitoring:**

| Signal | Collection Method | Alert Threshold |
|--------|------------------|-----------------|
| User thumbs up/down | In-app feedback | Satisfaction < ___% |
| Response latency | APM instrumentation | P99 > ___ ms |
| Token usage | Usage logging | Daily spend > $___ |
| Safety filter triggers | Pipeline logs | Rate > ___% |

**Feedback Loop:**
```
User ──query──▶ System ──response──▶ User
  │                │                    │ (thumbs up/down, flag)
  └───────────────▶│◀───────────────────┘
                   ▼
            Feedback Store ──▶ [A/B Test] [Retrain] [Prompt Tuning]
```

**A/B Testing:**
- [ ] Split: ___%/___% · Compare: latency, satisfaction, cost · Min sample: ___ · Rollout: ___

---

## 8. ⚖️ Trade-offs

### Decision 1: ___

| Option A | Option B |
|----------|----------|
| Pros:    | Pros:    |
| Cons:    | Cons:    |

**Chose:** ___ because ___

### Decision 2: ___

| Option A | Option B |
|----------|----------|
| Pros:    | Pros:    |
| Cons:    | Cons:    |

**Chose:** ___ because ___

### GenAI Trade-off: ___

| Option A (e.g., Larger model) | Option B (e.g., Smaller model) |
|-------------------------------|-------------------------------|
| Pros:    | Pros:    |
| Cons:    | Cons:    |

**Chose:** ___ because ___

---

## 9. 🔮 Follow-up Questions

### Scaling Questions
- **What if traffic increases 10x?** ___
- **What if we need to go multi-region?** ___

### Failure Scenarios
- **What if the primary LLM provider goes down?** ___
- **What if the vector store becomes unavailable?** ___

### GenAI-Specific Questions
- **What if the model starts hallucinating more after an update?** ___
- **How would you handle a new regulation on AI-generated content?** ___
- **What if cost per query doubles due to pricing changes?** ___

### Feature Extensions
- **How would you add ___?** ___

---

## 📌 Interview Checklist

Before wrapping up, verify:

**Classical HLD:**
- [ ] Requirements clearly defined and prioritized
- [ ] Back-of-envelope numbers make sense
- [ ] API covers all core functionality
- [ ] Database schema supports all operations
- [ ] Architecture diagram is clear
- [ ] Scaling approach is concrete
- [ ] Trade-offs discussed with justification
- [ ] Can answer follow-up questions

**GenAI-Specific:**
- [ ] Token budget fits within context window limits
- [ ] Cost-per-query estimated and within budget
- [ ] RAG vs fine-tuning decision justified
- [ ] Model selection and fallback chain defined
- [ ] Safety filters cover input AND output
- [ ] PII handling strategy documented
- [ ] Evaluation metrics and targets set
- [ ] Feedback loop captures user signals
- [ ] A/B testing plan for model/prompt changes
- [ ] Streaming response strategy addressed

---

*Copy this template for each GenAI system you practice! For classical (non-LLM) systems, use the [HLD Design Template](../../04-hld-projects/DESIGN-TEMPLATE.md) instead.*
