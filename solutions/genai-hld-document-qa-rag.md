# 🏆 Coach Answer: Document Q&A (RAG) — GenAI HLD

> **Type:** Generative AI System Design  
> **Difficulty:** Advanced  
> **Time Target:** 45 minutes

---

## Phase 1 — Clarify Use Case & LLM Role (5 min)

Say: "I will design this as a retrieval-grounded answer system. The model writes the final answer, but the source of truth is the indexed document corpus and the retrieved citations."

### System Goal
Build a system that lets users ask natural-language questions over a corpus of internal documents (e.g., company knowledge base) and receive accurate, grounded answers with source citations.

### LLM Role
- The LLM **generates** the final answer given retrieved context.
- The LLM does **not** memorize the documents — it reads relevant chunks at query time.
- This is a classic **Retrieval-Augmented Generation (RAG)** architecture.

### Key Clarifications
- Q: How large is the corpus? → 100K–1M documents, 10–100 pages each.
- Q: Multi-modal? → Text-only for V1; images and tables in V2.
- Q: Real-time or batch? → Real-time queries; batch ingestion of new documents.
- Q: Who are the users? → Internal employees; authenticated access.

### Out of Scope (V1)
- Multi-turn conversation / chat memory.
- Document editing or collaboration.
- Custom model fine-tuning.

---

## Phase 2 — Token Budget & Cost Estimation (5 min)

Say: "Before drawing boxes, I want a rough token and latency budget because RAG quality, cost, and response time all move together."

| Metric | Estimate |
|--------|----------|
| Average query | ~100 tokens (input question) |
| Retrieved context | ~2,000 tokens (5 chunks × 400 tokens each) |
| System prompt | ~200 tokens |
| Total input per query | ~2,300 tokens |
| Generated answer | ~300 tokens |
| Total tokens per query | ~2,600 tokens |
| Cost per query (GPT-4 class) | ~$0.05 |
| Daily queries | 10,000 |
| Monthly cost (LLM only) | ~$15,000 |
| Latency waterfall | Embedding: 50ms + Vector search: 30ms + LLM generation: 1.5s ≈ **~2s total** |

### Cost Optimization Levers
- Use cheaper model for simple questions (model routing).
- Cache answers for repeated/similar queries.
- Use smaller model (GPT-3.5 class) for first pass, escalate to GPT-4 if confidence is low.

---

## Phase 3 — Architecture Sketch (10 min)

Say: "There are two separate pipelines: ingestion builds a permission-aware index, while query time retrieves, reranks, constructs a bounded prompt, and validates the answer."

```
┌──────────────┐
│    Users     │
└──────┬───────┘
       ▼
┌──────────────┐     ┌──────────────────┐
│  API Gateway │────▶│   Query Service  │
└──────────────┘     └──────┬───────────┘
                            │
              ┌─────────────┼──────────────┐
              ▼             ▼              ▼
       ┌────────────┐ ┌──────────┐ ┌────────────┐
       │  Embedding │ │  Vector  │ │   LLM      │
       │  Service   │ │  Store   │ │  Gateway   │
       └────────────┘ │(Pinecone)│ └────────────┘
                      └──────────┘
                            ▲
                    ┌───────┴────────┐
                    │  Ingestion     │
                    │  Pipeline      │
                    │ (async/batch)  │
                    └───────┬────────┘
                            ▼
                    ┌────────────────┐
                    │  Document      │
                    │  Store (S3)    │
                    └────────────────┘
```

### Two Pipelines

**Ingestion Pipeline (Batch/Async)**
1. New documents uploaded to Document Store (S3).
2. Chunker splits documents into 400-token chunks with overlap.
3. Embedding Service generates vector for each chunk.
4. Vectors stored in Vector Store with metadata (doc_id, chunk_index, title).

**Query Pipeline (Real-Time)**
1. User submits question via API.
2. Embedding Service converts question to vector.
3. Vector Store returns top-K most similar chunks (K=10).
4. Re-ranker scores and selects top 5 chunks.
5. Prompt Builder assembles: system prompt + context chunks + user question.
6. LLM Gateway sends prompt to LLM, streams response back.
7. Post-processor extracts citations and validates answer.

---

## Phase 4 — LLM Pipeline Deep Dive (10 min)

Say: "The most important GenAI choices are chunking, hybrid retrieval, reranking, prompt construction, and groundedness checks."

### Chunking Strategy
- **Method:** Recursive text splitter — split by paragraphs, then sentences.
- **Chunk size:** 400 tokens with 50-token overlap.
- **Why overlap:** Ensures context isn't lost at chunk boundaries.
- **Metadata per chunk:** document_id, chunk_index, section_title, page_number.

### Embedding
- **Model:** `text-embedding-3-small` (OpenAI) or open-source `bge-large-en`.
- **Dimension:** 1536 (OpenAI) or 1024 (bge).
- **Batch embedding** during ingestion for throughput.

### Retrieval
- **Vector search:** Approximate Nearest Neighbor (ANN) via Pinecone/Weaviate.
- **Hybrid search:** Combine vector similarity + BM25 keyword search for better recall.
- **Top-K:** Retrieve 10, re-rank to 5.

### Re-Ranking
- Cross-encoder re-ranker (e.g., `bge-reranker-large`) scores each (query, chunk) pair.
- More accurate than embedding similarity alone but slower — apply only to top-K candidates.

### Prompt Construction
```
System: You are a helpful assistant that answers questions based on the provided
context. If the context doesn't contain the answer, say "I don't know."
Always cite your sources using [Source: doc_title, page X].

Context:
[Chunk 1: ...]
[Chunk 2: ...]
...

User: {question}
```

### Context Window Management
- If total context exceeds model limit, truncate lowest-ranked chunks.
- Reserve 500 tokens for the answer.

---

## Phase 5 — Safety & Guardrails (5 min)

Say: "The highest-risk failures are prompt injection from retrieved text, cross-tenant leakage, and confident answers without evidence."

| Layer | Mechanism |
|-------|-----------|
| **Input filtering** | Block prompt injection attempts (e.g., "ignore previous instructions"). Use regex + classifier. |
| **Output validation** | Check that citations reference actual retrieved chunks (groundedness check). |
| **Hallucination mitigation** | Instruct model to say "I don't know" when context is insufficient. Verify answer tokens overlap with context. |
| **PII handling** | Scan documents during ingestion; redact or flag PII. Scan LLM output before returning. |
| **Access control** | Document-level permissions — only retrieve chunks the user is authorized to see. |
| **Rate limiting** | Per-user query limits to prevent abuse and cost overruns. |

---

## Phase 6 — Evaluation & Observability (5 min)

Say: "I would not launch this on generic accuracy alone; I need retrieval recall, faithfulness, citation accuracy, latency, and cost metrics."

### Offline Metrics (Pre-Launch)
| Metric | How Measured |
|--------|-------------|
| **Faithfulness** | % of answer claims supported by retrieved context (LLM-as-judge or human eval) |
| **Relevance** | Are retrieved chunks relevant to the question? (nDCG@5) |
| **Answer correctness** | Gold-standard Q&A pairs; compare LLM answer to reference |

### Online Monitoring (Post-Launch)
| Signal | Tool |
|--------|------|
| Latency (p50, p95, p99) | Prometheus / Datadog |
| Error rate | API gateway metrics |
| Token usage / cost | LLM Gateway logging |
| User satisfaction | Thumbs up/down on each answer |
| Retrieval quality | Log retrieved chunk IDs for debugging |

### Feedback Loop
- Low-rated answers queued for human review.
- Human corrections become evaluation golden set.
- Weekly regression tests against golden set.

---

## Phase 7 — Wrap-Up (5 min)

Say: "The design optimizes for grounded answers with citations. The trade-off is extra ingestion, retrieval, and evaluation complexity, but that is what keeps the system trustworthy."

### Key Trade-Offs

| Decision | Option A | Option B | Chosen |
|----------|----------|----------|--------|
| Chunk size | Small (200 tokens) — precise | Large (800 tokens) — more context | 400 tokens — balanced |
| Vector DB | Managed (Pinecone) | Self-hosted (Weaviate) | Managed for V1 — faster to ship |
| Model | GPT-4 (quality) | GPT-3.5 (cost/speed) | GPT-4 with model routing for simple queries |
| Search | Vector only | Hybrid (vector + BM25) | Hybrid — better recall for keyword-heavy queries |

### Follow-Up Extensions
1. **Multi-turn chat** — Add conversation memory store; include recent turns in prompt context.
2. **Multi-modal** — Process tables/images during ingestion; use vision-capable model.
3. **Streaming** — Stream LLM tokens to UI for perceived latency reduction.
4. **Fine-tuning** — Fine-tune embedding model on domain data for better retrieval.

---

*This is a "strong answer" outline. Adapt depth to interviewer focus — some interviewers care most about retrieval quality, others about cost optimization or safety.*
