# 🤖 GenAI System Design One-Pager

A quick-reference guide for GenAI system design interviews. Follow this 5-step flow.

---

## 🎯 The 5-Step GenAI Design Flow

```
Step 1: Clarify Use Case ──→ Step 2: Estimate Token Budgets ──→ Step 3: Sketch Architecture
                                                                          │
Step 5: Trade-offs & Safety ←── Step 4: Deep Dive RAG/Routing ←──────────┘
```

---

## Step 1: Clarify Use Case (5 min)

### Questions to Ask

| Area | Questions |
|------|-----------|
| **Inputs** | What does the user send? (text, code, documents, images?) |
| **Outputs** | What does the system return? (answer, summary, suggestion, action?) |
| **Grounding** | Is there a knowledge base? How often is it updated? |
| **Scale** | How many requests per day? Concurrent users? |
| **Latency** | Real-time (streaming) or batch? Acceptable time-to-first-token? |
| **Quality** | How critical is accuracy? Tolerance for hallucination? |
| **Safety** | User-facing? Content restrictions? PII handling? |

### Common GenAI Interview Prompts

| Prompt | Key Focus |
|--------|-----------|
| "Design ChatGPT" | Multi-turn conversation, memory, streaming, safety |
| "Design enterprise search with AI" | RAG pipeline, hybrid retrieval, grounding |
| "Design an AI copilot" | Code context retrieval, inline suggestions, streaming |
| "Design content moderation" | Multi-modal analysis, tiered escalation, policy engine |
| "Design AI customer support" | RAG + conversation, handoff to humans, feedback loop |

---

## Step 2: Estimate Token Budgets (5 min)

### Token Budget Template

```
Context Window (e.g., 128K tokens):
├── System Prompt:          ~200–500 tokens
├── Retrieved Context:      ~2,000–8,000 tokens
├── Conversation History:   ~1,000–4,000 tokens
├── User Query:             ~50–500 tokens
├── Reserved for Output:    ~500–2,000 tokens
└── Safety Margin:          ~500 tokens
```

### Cost Estimation Quick Math

Pricing note (audited 2026-06-14): use these dollar values for interview arithmetic only. Refresh provider pricing pages before quoting exact costs.

| Model Tier | Input Cost | Output Cost | Use Case |
|------------|------------|-------------|----------|
| Small (GPT-4o-mini, Haiku) | ~$0.15/1M tokens | ~$0.60/1M tokens | Simple classification, routing |
| Medium (GPT-4o, Sonnet) | ~$2.50/1M tokens | ~$10/1M tokens | General generation, RAG |
| Large (GPT-4, Opus) | ~$10/1M tokens | ~$30/1M tokens | Complex reasoning, coding |

### Quick Cost Formula

```
Daily Cost = (requests/day) × (avg_input_tokens × input_price + avg_output_tokens × output_price)

Example: 1M requests/day, 1000 input + 300 output tokens, medium model
= 1M × (1000 × $2.50/1M + 300 × $10/1M)
= 1M × ($0.0025 + $0.003)
= $5,500/day ≈ $165K/month
```

### Latency Estimation

| Metric | Typical Value |
|--------|---------------|
| Time to first token | 200–800 ms |
| Tokens per second (streaming) | 30–100 tokens/sec |
| Embedding call | 10–50 ms |
| Vector search (ANN) | 5–20 ms |
| Reranking (cross-encoder) | 50–200 ms per query |

---

## Step 3: Sketch Architecture (15 min)

### Universal GenAI Architecture Pattern

```
┌─────────────────────────────────────────────────────────────────┐
│                        Client Layer                              │
│         (Web App / Mobile / IDE Plugin / API)                    │
└────────────────────────────┬────────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────────┐
│                      API Gateway                                 │
│     (Auth, Rate Limiting, Token Budget Enforcement)              │
└────────────────────────────┬────────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────────┐
│                    Request Orchestrator                           │
│   (Route, Classify, Select Model, Manage Retries/Fallbacks)     │
└───────┬─────────────┬──────────────┬─────────────┬──────────────┘
        │             │              │             │
   ┌────▼────┐  ┌─────▼─────┐  ┌────▼────┐  ┌────▼────┐
   │ Safety  │  │  Prompt   │  │  Memory │  │ Tool    │
   │ Filter  │  │  Builder  │  │  Store  │  │ Router  │
   │ (in/out)│  │           │  │         │  │         │
   └─────────┘  └─────┬─────┘  └─────────┘  └─────────┘
                      │
              ┌───────▼───────┐
              │  Retriever    │──→ Vector DB / Search Index
              │  & Ranker     │
              └───────┬───────┘
                      │
              ┌───────▼───────┐
              │  LLM Service  │──→ Model Provider (OpenAI/Anthropic/Self-hosted)
              │  (Inference)  │
              └───────┬───────┘
                      │
              ┌───────▼───────┐
              │  Output       │──→ Safety Filter → Response Cache → Client
              │  Pipeline     │
              └───────────────┘
```

### Ingestion Pipeline (for RAG systems)

```
Source Documents → Chunker → Embedder → Vector DB
                     │
                     └→ Metadata Indexer → Metadata Store
```

### Key Components to Mention

| Component | Purpose | Technology Examples |
|-----------|---------|-------------------|
| **API Gateway** | Auth, rate limiting, routing | Kong, AWS API Gateway |
| **Orchestrator** | Model routing, retries, fallbacks | Custom service |
| **Retriever** | Find relevant context | Elasticsearch, Pinecone, Weaviate |
| **Prompt Builder** | Assemble prompt from components | Custom service |
| **Memory Store** | Conversation history | Redis, DynamoDB |
| **Safety Filter** | Input/output validation | Custom + LLM classifier |
| **LLM Service** | Inference | OpenAI API, vLLM, TGI |
| **Vector DB** | Embedding storage and search | Pinecone, Qdrant, pgvector |
| **Cache** | Semantic response caching | Redis + embedding similarity |
| **Message Queue** | Async processing | Kafka, SQS |

---

## Step 4: Deep Dive RAG/Routing (15 min)

### RAG Pipeline Deep Dive

```
Query → Embed → Retrieve (Top-K) → Rerank → Build Prompt → Generate → Filter → Stream
         │          │                  │
         │     ┌────┴────┐        ┌────┴────┐
         │     │ Sparse  │        │ Cross-  │
         │     │ (BM25)  │        │ Encoder │
         │     ├─────────┤        └─────────┘
         │     │ Dense   │
         │     │ (Vector)│
         │     └─────────┘
         │
    Embedding
    Model
```

### Retrieval Strategy Decision Tree

```
What kind of queries?
├── Keyword-heavy → Sparse retrieval (BM25/Elasticsearch)
├── Semantic/conceptual → Dense retrieval (vector search)
├── Mixed → Hybrid (sparse + dense + reciprocal rank fusion)
└── High precision needed → Add cross-encoder reranking
```

### Model Routing Decision Tree

```
Query complexity?
├── Simple (FAQ, classification) → Small model (fast, cheap)
├── Standard (summarization, QA) → Medium model (balanced)
├── Complex (reasoning, coding) → Large model (best quality)
└── Unknown → Classify first with small model, then route
```

### Caching Strategies

| Strategy | How It Works | When to Use |
|----------|-------------|-------------|
| **Exact match** | Cache by query hash | FAQ, repeated queries |
| **Semantic cache** | Cache by embedding similarity | Similar questions, paraphrases |
| **Prompt-level cache** | Cache assembled prompts | Same context + different queries |
| **KV-Cache (inference)** | Reuse attention states | Multi-turn conversations |

---

## Step 5: Trade-offs & Safety (5 min)

### GenAI-Specific Trade-offs

| Trade-off | Option A | Option B |
|-----------|----------|----------|
| **Cost vs Quality** | Small model (cheap, fast, less accurate) | Large model (expensive, slow, more accurate) |
| **Latency vs Thoroughness** | Single retrieval pass (fast) | Cascading retrieval + rerank (slower, better) |
| **Freshness vs Speed** | Real-time indexing (always current) | Batch indexing (faster queries, stale data) |
| **Safety vs UX** | Strict filtering (blocks edge cases) | Lenient filtering (better UX, more risk) |
| **Context vs Cost** | Large context window (more info, costly) | Shorter context (cheaper, may miss info) |
| **RAG vs Fine-tuning** | RAG (flexible, current data) | Fine-tuning (faster inference, static knowledge) |
| **Streaming vs Batch** | Streaming (lower TTFT, complex) | Batch (simpler, higher latency) |

### Safety Checklist (Always Mention)

- [ ] **Input filtering** — Block prompt injection, toxic inputs
- [ ] **Output filtering** — Check for hallucinations, toxic content, PII leaks
- [ ] **Grounding** — Cite sources, verify against retrieved context
- [ ] **Rate limiting** — Token-based limits per user/org
- [ ] **Audit logging** — Log all LLM inputs/outputs for compliance
- [ ] **Human escalation** — Fallback path when LLM confidence is low

### Evaluation Metrics to Mention

| Metric | What It Measures |
|--------|-----------------|
| **Faithfulness** | Does the answer match the retrieved context? |
| **Answer relevance** | Does the answer address the user's question? |
| **Context relevance** | Did we retrieve the right documents? |
| **Latency (TTFT)** | Time to first token for streaming responses |
| **Cost per query** | Total inference + retrieval cost |
| **Safety rate** | % of responses passing safety filters |

---

## 📊 Quick Reference Card

### GenAI Interview Buzzwords → Components

| Interviewer Says | You Should Discuss |
|------------------|--------------------|
| "knowledge base" or "documents" | RAG pipeline, chunking, vector DB |
| "conversation" or "multi-turn" | Memory store, session management |
| "real-time" or "streaming" | SSE/WebSocket, streaming inference |
| "accuracy" or "hallucination" | Grounding, retrieval quality, evaluation |
| "cost" or "budget" | Model routing, caching, token budgets |
| "safety" or "moderation" | Input/output filters, policy engine |
| "code" or "developer tool" | Code context retrieval, AST parsing |
| "scale" or "millions of users" | Caching, batching, model routing |
| "multiple data sources" | Federated retrieval, metadata filtering |

### Estimation Cheat Numbers

| Metric | Value |
|--------|-------|
| 1 token ≈ | 4 characters (English) |
| 1 page of text ≈ | 500–800 tokens |
| Embedding (1536-dim, float32) ≈ | 6 KB |
| 1M embeddings storage ≈ | 6 GB |
| LLM inference (medium model) ≈ | 300–800 ms |
| Vector search (1M vectors) ≈ | 5–20 ms |
| Semantic cache check ≈ | 10–30 ms |

---

## 🔗 Related Resources

- [RAG Architecture Cheatsheet](rag-architecture-cheatsheet.md) — Detailed RAG patterns
- [Trade-offs Matrix](trade-offs-matrix.md) — Classical trade-offs
- [HLD Components Map](hld-components-map.md) — Classical components
- [GenAI Concepts](../../06-genai-systems/00-concepts/) — Deep theory
- [GenAI HLD Projects](../../06-genai-systems/02-llm-hld-projects/) — Full system designs

---

*Use this one-pager to structure your GenAI system design interview from start to finish! 🚀*
