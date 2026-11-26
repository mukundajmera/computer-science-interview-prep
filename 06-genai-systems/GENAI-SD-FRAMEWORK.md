# How to Answer Any GenAI System Design Question

> **This framework provides a reusable, 6-step structure for answering any GenAI/LLM-focused system design interview question.** Whether you're designing a chatbot, a RAG pipeline, an AI-powered search engine, or an autonomous agent system, follow these steps to deliver a structured, impressive answer in 35–45 minutes.

---

## Why a Separate Framework?

Traditional system design interviews focus on throughput, storage, and availability for deterministic systems. GenAI system design introduces fundamentally different challenges:

| Dimension | Classic SD | GenAI SD |
|-----------|-----------|----------|
| **Cost model** | Compute + storage | Token economics (per-request cost can be 100×) |
| **Determinism** | Same input → same output | Non-deterministic; temperature, sampling strategies |
| **Latency profile** | Millisecond DB lookups | Multi-second inference; time-to-first-token matters |
| **Correctness** | Unit-testable | Hallucinations, factuality is probabilistic |
| **Safety** | Input validation | Prompt injection, toxic output, PII leakage |
| **Evaluation** | Precision/recall on known sets | Subjective quality, human eval, LLM-as-judge |
| **Scaling** | Horizontal compute | GPU scarcity, model serving, KV-cache memory |

You cannot simply bolt an LLM onto a classical architecture — you need a purpose-built reasoning framework.

---

## The 6-Step Framework

```
┌──────────────────────────────────────────────────────────┐
│  Step 1  Clarify Use Case & LLM Role             5 min  │
│  Step 2  Estimate Tokens, Costs & Latency        5 min  │
│  Step 3  Sketch the Architecture                10 min  │
│  Step 4  Deep-Dive the LLM Pipeline             10 min  │
│  Step 5  Safety & Guardrails                     5 min  │
│  Step 6  Evaluation & Observability              5 min  │
└──────────────────────────────────────────────────────────┘
                  Total ≈ 40 minutes
```

---

### Step 1 — Clarify the Use Case & the LLM's Role (5 min)

**Goal:** Eliminate ambiguity before you draw a single box.

#### Determine the LLM Task Type

| Task Type | Example | Typical Models |
|-----------|---------|---------------|
| **Generation** | Draft emails, write code | GPT-4, Claude, Llama 3 |
| **Classification** | Ticket routing, sentiment | GPT-3.5, fine-tuned BERT |
| **Extraction** | Parse invoices, NER | GPT-3.5, Llama 3, regex+LLM |
| **Summarization** | Meeting notes, doc digests | GPT-4, Claude, Mistral |
| **Reasoning / Agents** | Multi-step research, tool use | GPT-4, Claude 3.5, o1 |

#### Is the LLM Core or Augmentation?

- **Core:** The product _is_ the LLM experience (e.g., ChatGPT, coding assistant). Latency and quality are existential.
- **Augmentation:** LLM enhances an existing product (e.g., smart search in an e-commerce app). Fallback paths are mandatory.

#### Key Clarifying Questions Checklist

Ask these _before_ designing:

- [ ] What is the primary user action and expected output format?
- [ ] Who are the end users — internal employees, developers, or consumers?
- [ ] What latency is acceptable? (real-time chat < 2s vs async report < 30s)
- [ ] What scale are we targeting? (QPS, concurrent users, document corpus size)
- [ ] Must the system use proprietary data? (→ RAG or fine-tuning decision)
- [ ] Are there compliance or data residency requirements? (→ model hosting)
- [ ] Is the system conversational (multi-turn) or single-shot?
- [ ] What is the tolerance for incorrect answers? (medical vs casual chat)
- [ ] Do we need multi-modal support? (images, audio, structured data)
- [ ] What is the budget ceiling for inference costs?

> **Interview tip:** Spending 5 minutes here shows the interviewer you think like a senior engineer — not someone who jumps to solutions.

---

### Step 2 — Estimate Token Budgets, Costs & Latency (5 min)

**Goal:** Prove you understand the unique economics of LLM systems.

#### Token Volume Estimation

```
Tokens per request = system_prompt + context_docs + user_query + output_tokens

Example:
  System prompt:    ~300 tokens  (fixed)
  Retrieved docs:  ~1500 tokens  (RAG context, 3 chunks × 500 tokens)
  User query:       ~100 tokens
  Output:           ~500 tokens
  ─────────────────────────────
  Total per request: ~2400 tokens
```

#### Model Cost Comparison Table

Pricing note (audited 2026-06-14): the dollar values below are historical interview-arithmetic examples, not current vendor pricing. Refresh them against provider pricing pages before quoting exact costs.

| Model | Input (per 1M tokens) | Output (per 1M tokens) | Context Window | Best For |
|-------|----------------------|------------------------|---------------|----------|
| GPT-4o | $2.50 | $10.00 | 128K | Complex reasoning, agents |
| GPT-4o-mini | $0.15 | $0.60 | 128K | Cost-sensitive classification |
| Claude 3.5 Sonnet | $3.00 | $15.00 | 200K | Long-context, analysis |
| Llama 3.1 70B (self-hosted) | ~$0.50* | ~$0.50* | 128K | Privacy-sensitive, high volume |
| Embedding (text-embedding-3-small) | $0.02 | — | 8K | Retrieval |

_*Self-hosted cost is approximate GPU amortization._

#### Monthly Cost Estimation Formula

```
Monthly Cost = (requests/day) × 30
             × [(input_tokens × input_price) + (output_tokens × output_price)]
             + embedding_costs + infrastructure_overhead

Example (Enterprise Q&A):
  500 req/day × 30 days = 15,000 requests/month
  Input:  15,000 × 1,900 tokens × ($2.50 / 1M) =  $71.25
  Output: 15,000 ×   500 tokens × ($10.00 / 1M) =  $75.00
  Embeddings (one-time ingest + queries):          ~$5.00
  ─────────────────────────────────────────────────────────
  Total: ~$151/month  (GPT-4o pricing)
```

#### Latency Waterfall

```
Total Latency = Network + Preprocessing + Inference + Postprocessing

  Network RTT:          ~50ms
  Preprocessing:        ~100ms  (retrieval, prompt assembly)
  Inference TTFT:       ~300ms  (time to first token)
  Token generation:     ~1500ms (500 tokens × ~3ms/token streaming)
  Postprocessing:       ~50ms   (guardrails, formatting)
  ────────────────────────────
  Total (streaming):    ~2000ms to complete
  Perceived (TTFT):     ~450ms  (user sees first token)
```

> **Interview tip:** Even rough numbers impress — interviewers want to see you _think_ about costs, not just architecture boxes.

---

### Step 3 — Sketch the Architecture (10 min)

**Goal:** Draw the right high-level architecture based on requirements.

#### Decision Tree: Which Pattern Do You Need?

```
Does the LLM need external knowledge?
├── YES → Does the knowledge change frequently?
│         ├── YES → RAG (Retrieval-Augmented Generation)
│         └── NO  → Fine-tuning or RAG (evaluate cost/quality trade-off)
└── NO  → Does the task require multi-step reasoning?
          ├── YES → Agent Loop (tool use, chain-of-thought)
          └── NO  → Direct LLM call (simplest path)

Do you need to route between models?
├── YES → Router Pattern (classify → route to appropriate model)
└── NO  → Single model path

Is real-time response critical?
├── YES → Streaming SSE/WebSocket
└── NO  → Batch / async processing
```

#### High-Level Component Diagram Template

```
┌─────────┐     ┌─────────────┐     ┌──────────────┐
│  Client  │────▶│ API Gateway │────▶│ Orchestrator │
└─────────┘     │ (Auth, Rate │     │  (LangChain/ │
                │  Limiting)  │     │  custom)     │
                └─────────────┘     └──────┬───────┘
                                           │
                    ┌──────────────────────┼──────────────────────┐
                    ▼                      ▼                      ▼
            ┌──────────────┐     ┌─────────────────┐    ┌────────────────┐
            │  Retrieval   │     │   LLM Service   │    │   Safety       │
            │  Service     │     │  (Model Router) │    │   Guardrails   │
            │              │     │                 │    │                │
            │ Vector DB    │     │ GPT-4 / Claude  │    │ Input Filter   │
            │ Reranker     │     │ Local Models    │    │ Output Filter  │
            └──────────────┘     └─────────────────┘    └────────────────┘
                    │                      │                      │
                    ▼                      ▼                      ▼
            ┌──────────────┐     ┌─────────────────┐    ┌────────────────┐
            │  Document    │     │   Cache Layer   │    │   Audit Log    │
            │  Store (S3)  │     │ (Semantic/KV)   │    │   & Traces     │
            └──────────────┘     └─────────────────┘    └────────────────┘
```

#### Key Architectural Patterns

| Pattern | When to Use | Key Components |
|---------|-------------|---------------|
| **RAG** | Need proprietary/current data | Chunker, Embedder, Vector DB, Reranker |
| **Agent Loop** | Multi-step tasks, tool use | Planner, Tool Registry, Memory, Executor |
| **Chain-of-Thought** | Complex reasoning in a single call | Structured prompts, step-by-step output |
| **Router** | Multiple models with different strengths | Classifier, Model Registry, Fallback logic |
| **Map-Reduce** | Long documents exceeding context | Splitter, Parallel LLM calls, Aggregator |

#### Data Flow for RAG Pattern

```
User Query
    │
    ▼
[1] Embed query → vector
    │
    ▼
[2] Search vector DB → top-K chunks
    │
    ▼
[3] Rerank chunks by relevance
    │
    ▼
[4] Assemble prompt: system_prompt + chunks + query
    │
    ▼
[5] LLM inference → streamed response
    │
    ▼
[6] Post-process: citations, guardrails, format
    │
    ▼
Response to user (with source references)
```

---

### Step 4 — Deep-Dive the LLM Pipeline (10 min)

**Goal:** Show depth in the component the interviewer cares most about.

#### Retrieval Pipeline

| Stage | Options | Trade-offs |
|-------|---------|-----------|
| **Chunking** | Fixed-size (512 tokens), semantic (paragraph), recursive | Fixed is simple; semantic preserves meaning but variable size |
| **Embedding** | OpenAI ada-3, Cohere embed, self-hosted e5-large | API cost vs self-hosting GPU cost; dimension size affects storage |
| **Vector DB** | Pinecone, Weaviate, Qdrant, pgvector | Managed vs self-hosted; filtering, scale, hybrid search support |
| **Retrieval** | Top-K similarity, hybrid (dense + sparse/BM25) | Hybrid improves recall for keyword-heavy queries |
| **Reranking** | Cross-encoder (Cohere Rerank, BGE), LLM-based | Reranking top-20 → top-5 significantly boosts precision |

#### Prompt Engineering

```
┌─ System Prompt ─────────────────────────────────────────┐
│ You are an expert assistant for {company}.              │
│ Answer ONLY from the provided context.                  │
│ If the context is insufficient, say "I don't know."     │
│ Cite sources using [Source N] notation.                 │
└─────────────────────────────────────────────────────────┘

┌─ Few-Shot Examples (optional) ──────────────────────────┐
│ Q: What is our refund policy?                           │
│ A: Based on [Source 1], the refund policy is ...        │
└─────────────────────────────────────────────────────────┘

┌─ Context Injection ─────────────────────────────────────┐
│ <context>                                               │
│   [Source 1] {chunk_text_1}                             │
│   [Source 2] {chunk_text_2}                             │
│ </context>                                              │
└─────────────────────────────────────────────────────────┘

┌─ User Query ────────────────────────────────────────────┐
│ {user_question}                                         │
└─────────────────────────────────────────────────────────┘
```

#### Model Selection & Routing

```
Incoming Request
    │
    ▼
[Classifier] — simple query?  ──YES──▶ GPT-4o-mini  (cheap, fast)
    │                                        │
    NO                                       ▼
    │                                   Response
    ▼
Complex / multi-step?  ──YES──▶ GPT-4o  (high quality)
    │                                │
    NO                               ▼
    │                           Response
    ▼
Privacy-sensitive?  ──YES──▶ Self-hosted Llama 3  (no data leaves infra)
    │
    ▼
Default → GPT-4o-mini
```

#### Streaming vs Batch

| Mode | Use When | Implementation |
|------|----------|---------------|
| **Streaming (SSE)** | Chat UIs, real-time interaction | Server-Sent Events; process tokens as they arrive |
| **Batch** | Offline processing, reports, bulk classification | Queue-based; optimize for throughput over latency |

#### Caching Strategies

| Cache Type | What It Stores | Hit Condition | Typical Savings |
|------------|---------------|---------------|----------------|
| **Exact prompt cache** | Full response keyed by hash(prompt) | Identical prompt | 100% inference cost |
| **Semantic cache** | Responses for semantically similar queries | Embedding similarity > threshold | 80-100% inference cost |
| **KV-cache (model-level)** | Attention key-value pairs | Shared prompt prefix | 30-60% TTFT reduction |
| **Document cache** | Retrieved chunks | Same doc query | Saves retrieval latency |

---

### Step 5 — Safety & Guardrails (5 min)

**Goal:** Show the interviewer you build _responsible_ AI systems.

#### Guardrail Architecture

```
User Input
    │
    ▼
┌──────────────────┐
│  PRE-LLM FILTER  │
│  ├─ PII Detection│  (redact SSNs, emails, credit cards)
│  ├─ Prompt Inj.  │  (detect jailbreak attempts)
│  ├─ Content Policy│  (block prohibited topics)
│  └─ Rate Limiting│  (per-user token budgets)
└────────┬─────────┘
         │ (cleaned input)
         ▼
┌──────────────────┐
│    LLM CALL      │
└────────┬─────────┘
         │ (raw output)
         ▼
┌──────────────────┐
│ POST-LLM FILTER  │
│  ├─ Toxicity     │  (classifier score < threshold)
│  ├─ Hallucination│  (verify claims against sources)
│  ├─ PII in Output│  (redact any leaked PII)
│  ├─ Format Valid.│  (JSON schema, length limits)
│  └─ Citation Check│ (ensure sources are referenced)
└────────┬─────────┘
         │ (safe output)
         ▼
    Response to User
```

#### Common Threat Vectors

| Threat | Description | Mitigation |
|--------|-------------|-----------|
| **Prompt injection** | User crafts input to override system prompt | Input classifier, delimiters, instruction hierarchy |
| **Jailbreaking** | Bypassing safety guidelines | Multi-layer filtering, model fine-tuning, red-teaming |
| **PII leakage** | Model memorizes/exposes training data | Output scanning, differential privacy, data sanitization |
| **Hallucination** | Confidently stating false information | RAG grounding, citation enforcement, confidence thresholds |
| **Data exfiltration** | Extracting proprietary context via clever queries | Output filtering, context isolation, audit logging |

#### Compliance Considerations

- **EU AI Act:** Classify system risk level; high-risk systems need conformity assessments
- **NIST AI RMF:** Map to Govern, Map, Measure, Manage functions
- **SOC 2 / HIPAA:** Audit trails, encryption at rest/transit, access controls
- **Human-in-the-loop:** Required for high-stakes decisions (medical, legal, financial)

---

### Step 6 — Evaluation & Observability (5 min)

**Goal:** Close the loop — how do you know the system is working?

#### Offline Evaluation

| Metric | What It Measures | When to Use |
|--------|-----------------|-------------|
| **Retrieval Recall@K** | % of relevant docs in top-K results | RAG systems |
| **BLEU / ROUGE** | N-gram overlap with reference answers | Summarization |
| **Faithfulness** | Does the answer stay true to context? | RAG (LLM-as-judge) |
| **Answer Relevance** | Does the answer address the question? | All Q&A systems |
| **Human Eval (1-5)** | Expert rating of quality | Gold standard, expensive |

#### Online Evaluation

| Signal | Collection Method | Latency |
|--------|------------------|---------|
| **Thumbs up/down** | UI button on every response | Immediate |
| **Explicit feedback** | "Was this helpful?" follow-up | Seconds |
| **Implicit signals** | Copy/paste rate, follow-up questions, session length | Async analytics |
| **A/B testing** | Split traffic between model versions | Days to weeks |

#### Observability Stack

```
┌──────────────────────────────────────────────────┐
│                 Observability Layer               │
│                                                  │
│  ┌─────────────┐  ┌──────────┐  ┌────────────┐  │
│  │ Prompt Traces│  │ Metrics  │  │ Cost       │  │
│  │ (LangSmith, │  │ (P50/P99 │  │ Dashboard  │  │
│  │  Phoenix)   │  │ latency) │  │ (tokens,$) │  │
│  └─────────────┘  └──────────┘  └────────────┘  │
│                                                  │
│  Key metrics to track:                           │
│  • Latency: TTFT (P50, P99), total response time│
│  • Tokens: input/output per request, daily total │
│  • Cost: per-request, per-user, daily aggregate  │
│  • Quality: guardrail trigger rate, feedback score│
│  • Errors: timeout rate, model API failures      │
└──────────────────────────────────────────────────┘
```

#### Feedback Loops

| Loop | Data Source | Action | Cadence |
|------|-----------|--------|---------|
| **Prompt tuning** | Low-rated responses | Refine system prompt, few-shot examples | Weekly |
| **Retrieval tuning** | "I don't know" responses | Improve chunking, add data sources | Weekly |
| **Fine-tuning** | Curated high-quality pairs | Train domain-specific model | Monthly |
| **RLHF** | Human preference rankings | Align model with user expectations | Quarterly |
| **Red-teaming** | Adversarial test suite | Harden guardrails | Before each release |

---

## Worked Example: "Design an Enterprise Document Q&A System"

> Walk-through of all 6 steps applied to a concrete problem.

### Step 1 — Clarify

| Question | Answer |
|----------|--------|
| What problem? | Employees ask questions about internal docs (policies, engineering docs, HR guides) |
| Users? | 10,000 employees, mostly non-technical |
| LLM role? | Core — this _is_ the product (internal knowledge assistant) |
| Latency? | < 3s for streaming first token; < 10s total |
| Scale? | ~500 queries/day initially, growing to 2,000/day |
| Data? | ~50,000 internal documents (Confluence, Google Docs, PDFs) |
| Compliance? | SOC 2; no PII in responses; audit trail required |
| Multi-turn? | Yes, support follow-up questions with conversation memory |

### Step 2 — Estimate

```
Per-request token budget:
  System prompt:       300 tokens
  Retrieved context: 1,500 tokens  (5 chunks × 300 tokens)
  User query:          100 tokens
  Output:              500 tokens
  Total:             2,400 tokens

Daily cost (500 queries, GPT-4o):
  Input:  500 × 1,900 × ($2.50 / 1M) = $2.38
  Output: 500 ×   500 × ($10.00 / 1M) = $2.50
  Daily total: ~$4.88 → Monthly: ~$146

Embedding cost (one-time, 50K docs × avg 2K tokens):
  100M tokens × ($0.02 / 1M) = $2.00

Infrastructure: Vector DB (~$70/mo), compute (~$200/mo)
Total monthly: ~$420
```

### Step 3 — Architecture

```
Employee (Browser/Slack)
    │
    ▼
┌──────────────┐
│ API Gateway   │  (Auth via SSO, rate limit: 20 req/min/user)
└──────┬───────┘
       ▼
┌──────────────┐
│ Orchestrator  │  (manages conversation state, routes requests)
└──┬───┬───┬───┘
   │   │   │
   ▼   ▼   ▼
┌─────┐ ┌─────┐ ┌───────────┐
│Retrieval│ │ LLM │ │ Guardrails│
│Service│ │(GPT-4o)│ │(pre+post) │
│       │ │       │ │           │
│Qdrant │ │Streaming│ │PII filter│
│+Rerank│ │  SSE  │ │Toxicity  │
└─────┘ └─────┘ └───────────┘
   │
   ▼
┌──────────────┐
│ Document Store│  (S3 + metadata DB)
│ Ingestion     │  (scheduled crawler for Confluence/GDocs)
└──────────────┘
```

**Pattern chosen:** RAG with streaming, conversation memory in Redis.

### Step 4 — Pipeline Deep-Dive

| Component | Choice | Rationale |
|-----------|--------|-----------|
| **Chunking** | Recursive, 300 tokens, 50-token overlap | Balances context preservation and retrieval precision |
| **Embedding** | OpenAI text-embedding-3-small (1536d) | Cost-effective, strong retrieval quality |
| **Vector DB** | Qdrant (self-hosted) | Open-source, metadata filtering, hybrid search |
| **Retrieval** | Hybrid (dense + BM25), top-20 | Catches both semantic and keyword matches |
| **Reranking** | Cohere Rerank, top-20 → top-5 | Significant precision boost for enterprise queries |
| **LLM** | GPT-4o (primary), GPT-4o-mini (simple questions) | Router based on query complexity classifier |
| **Cache** | Semantic cache (embedding similarity > 0.95) | Saves cost on repeated HR/policy questions |
| **Memory** | Last 5 turns stored in Redis, injected into prompt | Supports multi-turn without unbounded context growth |

### Step 5 — Safety

| Layer | Implementation |
|-------|---------------|
| **Input PII filter** | Presidio for entity detection; redact before sending to LLM |
| **Prompt injection** | Input classifier trained on known attack patterns; reject suspicious inputs |
| **Domain guardrail** | System prompt: "Do not provide medical, legal, or financial advice" |
| **Output PII scan** | Re-scan LLM output; redact any leaked employee data |
| **Citation enforcement** | Post-processing requires at least one [Source N] per claim |
| **Audit log** | Every query + response logged (with PII redacted) for compliance |

### Step 6 — Evaluation

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Retrieval Recall@5** | > 85% | Weekly eval on 200 labeled query-document pairs |
| **Answer Faithfulness** | > 90% | LLM-as-judge on sampled responses |
| **User satisfaction** | > 4.0/5.0 | Thumbs up/down + monthly survey |
| **TTFT** | < 1.5s (P95) | Prometheus + Grafana dashboards |
| **Guardrail trigger rate** | < 2% | Monitor for false positive spikes |
| **Cost per query** | < $0.02 | Daily cost tracking dashboard |

---

## Quick-Reference Checklist

Use this one-page checklist during your interview:

### Step 1 — Clarify
- [ ] Identified the LLM task type (generation / classification / extraction / summarization / agents)
- [ ] Determined if LLM is core product or augmentation
- [ ] Defined user personas and quality/latency expectations
- [ ] Asked about scale (QPS, corpus size, concurrent users)
- [ ] Clarified data sources and compliance requirements

### Step 2 — Estimate
- [ ] Calculated input/output token budget per request
- [ ] Selected model(s) and noted per-token pricing
- [ ] Estimated monthly cost with a worked formula
- [ ] Drew the latency waterfall (network → preprocessing → inference → postprocessing)

### Step 3 — Architecture
- [ ] Chose the right pattern (RAG / Agent / Router / Direct)
- [ ] Drew the high-level component diagram
- [ ] Identified data flow from user input to response
- [ ] Addressed streaming vs batch delivery

### Step 4 — Pipeline Deep-Dive
- [ ] Designed retrieval pipeline (chunking → embedding → vector DB → reranking)
- [ ] Crafted prompt structure (system prompt, few-shot, context injection)
- [ ] Defined model routing strategy
- [ ] Planned caching layers (semantic cache, KV-cache, prompt cache)

### Step 5 — Safety
- [ ] Added pre-LLM input filters (PII, prompt injection, content policy)
- [ ] Added post-LLM output filters (toxicity, hallucination, format validation)
- [ ] Addressed compliance requirements
- [ ] Identified where human-in-the-loop is needed

### Step 6 — Evaluation
- [ ] Defined offline metrics (retrieval recall, faithfulness, BLEU/ROUGE)
- [ ] Planned online signals (A/B tests, user feedback, implicit signals)
- [ ] Set up observability (traces, latency percentiles, cost dashboards)
- [ ] Designed feedback loops (prompt tuning, fine-tuning, red-teaming)

---

## Cross-Links

| Resource | Link | Description |
|----------|------|-------------|
| GenAI Concepts | [00-concepts/](./00-concepts/) | Deep dives on RAG, embeddings, agents, fine-tuning |
| GenAI LLD Components | [01-llm-lld-projects/](./01-llm-lld-projects/) | Hands-on implementation of individual components |
| GenAI HLD Projects | [02-llm-hld-projects/](./02-llm-hld-projects/) | Full system design case studies |
| Classic vs GenAI Comparison | [CLASSIC-VS-GENAI.md](./CLASSIC-VS-GENAI.md) | Side-by-side comparison of traditional and GenAI SD |
| GenAI Interview Pitfalls | [PITFALLS.md](./PITFALLS.md) | Common mistakes and how to avoid them |
| HLD Design Template | [../04-hld-projects/DESIGN-TEMPLATE.md](../04-hld-projects/DESIGN-TEMPLATE.md) | Reusable template for any HLD interview |

---

> **Remember:** The framework is a guide, not a script. Adapt the time allocation based on the interviewer's signals — if they probe on retrieval, spend more time on Step 4; if they care about production readiness, emphasize Steps 5 and 6.
