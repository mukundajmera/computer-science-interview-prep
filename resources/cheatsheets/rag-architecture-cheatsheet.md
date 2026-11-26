# 🔍 RAG Architecture Cheatsheet

Quick reference for Retrieval-Augmented Generation patterns, flows, and design decisions.

---

## 📋 What Is RAG?

**Retrieval-Augmented Generation (RAG)** combines information retrieval with LLM generation to produce grounded, up-to-date answers using external knowledge.

```
User Query → Retrieve Relevant Context → Augment Prompt → Generate Answer
```

**Why RAG over alternatives?**

| Approach | Pros | Cons | Best For |
|----------|------|------|----------|
| **Prompt-only** | Simple, no infra | Limited to model training data | General knowledge QA |
| **Fine-tuning** | Fast inference, no retrieval | Expensive to update, static knowledge | Domain-specific tone/style |
| **RAG** | Current data, verifiable, flexible | More components, higher latency | Enterprise search, support, knowledge bases |

---

## 🏗️ RAG Pipelines

### Ingestion Pipeline (Offline)

```
Source Documents
    │
    ▼
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│  Document    │───→│  Chunker    │───→│  Embedding  │───→│  Vector DB  │
│  Loader     │    │             │    │  Model      │    │  (Index)    │
└─────────────┘    └──────┬──────┘    └─────────────┘    └─────────────┘
                          │
                          ▼
                   ┌─────────────┐    ┌─────────────┐
                   │  Metadata   │───→│  Metadata   │
                   │  Extractor  │    │  Store      │
                   └─────────────┘    └─────────────┘
```

**Key decisions at ingestion:**

| Decision | Options | Recommendation |
|----------|---------|----------------|
| Chunk size | 256, 512, 1024 tokens | 512 tokens is a good default |
| Chunk overlap | 0%, 10%, 20% | 10–20% overlap preserves context |
| Embedding model | OpenAI, Cohere, open-source | Match query and doc embedding models |
| Index type | HNSW, IVF, flat | HNSW for <10M docs, IVF for larger |

### Query Pipeline (Online)

```
User Query
    │
    ▼
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│  Query      │───→│  Retriever  │───→│  Reranker   │───→│  Prompt     │
│  Embedder   │    │  (Top-K)    │    │  (Top-N)    │    │  Builder    │
└─────────────┘    └─────────────┘    └─────────────┘    └──────┬──────┘
                                                                │
                                                                ▼
                                                         ┌─────────────┐
                    ┌─────────────┐                      │  LLM        │
                    │  Output     │←─────────────────────│  (Generate) │
                    │  (Answer)   │                      └─────────────┘
                    └─────────────┘
```

**Key decisions at query time:**

| Decision | Options | Recommendation |
|----------|---------|----------------|
| Retrieval Top-K | 5, 10, 20, 50 | 10–20 for reranking, 3–5 for final context |
| Retrieval method | Sparse, dense, hybrid | Hybrid for best recall |
| Reranking | None, cross-encoder, LLM | Cross-encoder for quality-sensitive apps |
| Response format | Full answer, citations, streaming | Streaming with inline citations |

---

## 🔄 Retrieval Patterns

### 1. Sparse Retrieval (BM25 / TF-IDF)

```
Query: "rate limiting algorithms"
    │
    ▼
┌─────────────────┐
│  Inverted Index  │ ──→ Match on keywords: "rate", "limiting", "algorithms"
│  (Elasticsearch) │
└─────────────────┘
```

| Pros | Cons |
|------|------|
| Fast, well-understood | Misses semantic meaning |
| No embedding needed | Keyword mismatch problem |
| Good for exact terms | Poor for paraphrases |

**Best for:** Technical docs, code search, exact terminology

---

### 2. Dense Retrieval (Vector Search)

```
Query: "how to prevent API abuse" → embed → [0.12, -0.34, 0.56, ...]
    │
    ▼
┌─────────────────┐
│  Vector Index    │ ──→ ANN search: find nearest embeddings
│  (Pinecone/HNSW)│
└─────────────────┘
```

| Pros | Cons |
|------|------|
| Understands semantics | Requires embedding model |
| Handles paraphrases | Misses exact keywords |
| Language-agnostic | Needs good embeddings |

**Best for:** Conceptual queries, multilingual, FAQ matching

---

### 3. Hybrid Retrieval (Sparse + Dense)

```
Query → ┌─ BM25 (sparse) ─→ Results A ─┐
        │                                ├→ Reciprocal Rank Fusion → Merged Results
        └─ Vector (dense) ─→ Results B ─┘
```

**Reciprocal Rank Fusion (RRF):**
```
score(doc) = Σ 1 / (k + rank_in_list)    where k = 60 (constant)
```

| Pros | Cons |
|------|------|
| Best recall (covers both types) | More infrastructure |
| Handles diverse queries | Higher latency |
| Robust to query type | Need to tune fusion weights |

**Best for:** Production systems, enterprise search — this is the recommended default

---

### 4. Cascading Retrieval

```
Query → Sparse (BM25)    → Top 100
         └→ Dense (Vector) → Top 20
              └→ Cross-Encoder Reranker → Top 5
                   └→ LLM Generation
```

| Stage | Speed | Quality | Candidates |
|-------|-------|---------|------------|
| Sparse retrieval | ~5 ms | Low precision | 100s |
| Dense retrieval | ~10 ms | Medium precision | 10s |
| Cross-encoder rerank | ~100 ms | High precision | 3–5 |

**Best for:** High-quality RAG where precision matters more than speed

---

## 🏢 RAG Architecture Patterns

### Pattern 1: Centralized RAG

```
All documents → Single Vector DB → Single Retriever → LLM
```

| When to Use | Trade-offs |
|-------------|------------|
| Single data source | Simple but limited |
| Small-to-medium corpus (<1M docs) | All-or-nothing retrieval |
| Uniform document types | Single index to maintain |

---

### Pattern 2: Federated RAG

```
                    ┌→ Vector DB (Docs)      → Results ─┐
Query → Router ────→├→ Vector DB (Code)      → Results ─├→ Merge → LLM
                    ├→ SQL DB (Structured)   → Results ─┤
                    └→ API (Real-time data)  → Results ─┘
```

| When to Use | Trade-offs |
|-------------|------------|
| Multiple data sources | More complex routing |
| Mixed data types (docs, code, structured) | Need to merge heterogeneous results |
| Different update frequencies | Higher latency (parallel queries help) |

---

### Pattern 3: Cascading RAG (Multi-Stage)

```
Query → Cache Check → [hit] → Return cached answer
           │
        [miss]
           │
           ▼
     Simple Retrieval → Confidence check → [high] → Generate → Cache → Return
           │
        [low confidence]
           │
           ▼
     Deep Retrieval + Reranking → Generate → Return
```

| When to Use | Trade-offs |
|-------------|------------|
| Need to optimize cost | More complex pipeline |
| Mix of simple and complex queries | Need confidence scoring |
| High query volume with repetition | Cache management overhead |

---

### Pattern 4: Streaming RAG

```
Query → Retrieve → Build Prompt → LLM (stream) ──→ Token-by-token → Client
                                       │
                                  [SSE/WebSocket]
```

| When to Use | Trade-offs |
|-------------|------------|
| User-facing chat interfaces | Cannot filter complete response before sending |
| Low time-to-first-token needed | Client must handle partial responses |
| Long-form responses | Safety filtering on partial output is harder |

**Streaming + Safety Pattern:**
```
LLM stream → Buffer (sentence-level) → Safety check → Release to client
```

---

## 📊 Chunking Strategy Quick Reference

| Strategy | How It Works | Best For |
|----------|-------------|----------|
| **Fixed-size** | Split every N tokens with overlap | General purpose, simple |
| **Sentence** | Split on sentence boundaries | Factual content, QA |
| **Paragraph** | Split on paragraph/section breaks | Structured documents |
| **Semantic** | Split when embedding similarity drops | Narrative content |
| **Recursive** | Try large splits, recurse if too big | Mixed content types |
| **Document-aware** | Respect headers, tables, code blocks | Technical documentation |

### Chunk Size Impact

| Small Chunks (128–256 tokens) | Large Chunks (512–1024 tokens) |
|------------------------------|-------------------------------|
| More precise retrieval | More context per chunk |
| More chunks to search | Fewer chunks to search |
| May lose context | May include irrelevant info |
| Better for factoid QA | Better for summarization |

---

## 🔧 Vector Database Comparison

| Database | Type | ANN Algorithm | Filtering | Managed | Best For |
|----------|------|---------------|-----------|---------|----------|
| **Pinecone** | Cloud-native | Proprietary | Metadata | Yes | Production SaaS, managed simplicity |
| **Weaviate** | Open source | HNSW | GraphQL + filters | Yes/Self | Multi-modal, flexible schema |
| **Qdrant** | Open source | HNSW | Rich filtering | Yes/Self | High-performance, custom filtering |
| **Milvus** | Open source | IVF, HNSW | Attribute | Yes/Self | Large-scale (100M+ vectors) |
| **pgvector** | Extension | IVF, HNSW | SQL WHERE | Self | Already using PostgreSQL |
| **Elasticsearch** | Extension | HNSW | Full Lucene | Yes/Self | Hybrid search (BM25 + vector) |

### Choosing a Vector DB

```
Already using PostgreSQL? ──→ pgvector (simplest migration)
     │
     No
     │
Need managed + simple? ──→ Pinecone
     │
     No
     │
Need hybrid search? ──→ Elasticsearch with vectors
     │
     No
     │
Need rich filtering? ──→ Qdrant
     │
     No
     │
Need massive scale (100M+)? ──→ Milvus
     │
     No
     └──→ Weaviate (good default)
```

---

## ⚡ Performance Optimization

### Latency Breakdown (Typical RAG Query)

| Stage | Latency | Optimization |
|-------|---------|-------------|
| Query embedding | 10–50 ms | Batch, cache common queries |
| Vector search | 5–20 ms | Tune index params, limit Top-K |
| Reranking | 50–200 ms | Limit candidates, use lighter model |
| Prompt building | 1–5 ms | Pre-compute templates |
| LLM generation | 300–2000 ms | Streaming, model routing, caching |
| Safety filtering | 10–50 ms | Async where possible |
| **Total** | **400–2300 ms** | **Target: <1s for streaming TTFT** |

### Cost Optimization Strategies

| Strategy | Savings | Trade-off |
|----------|---------|-----------|
| Semantic caching | 30–60% | May serve slightly stale answers |
| Model routing (small → large) | 40–70% | Small model may be insufficient |
| Batch embedding | 20–40% | Slight ingestion delay |
| Reduce Top-K | 10–20% | May miss relevant context |
| Shorter prompts | 15–30% | Less context for generation |

---

## 📋 RAG Interview Quick Reference

### When Interviewer Asks About...

| Topic | Key Points to Cover |
|-------|--------------------|
| **Retrieval quality** | Hybrid search, reranking, evaluation metrics (recall@K, MRR) |
| **Hallucination** | Grounding, citation, faithfulness scoring, retrieval quality |
| **Scale** | Index partitioning, embedding pre-computation, caching |
| **Freshness** | Incremental indexing, TTL on embeddings, real-time vs batch |
| **Multi-tenant** | Namespace isolation, per-tenant indexes, access control |
| **Cost** | Caching, model routing, token budget management |
| **Latency** | Streaming, parallel retrieval, pre-computation |

### RAG Anti-Patterns to Avoid

| Anti-Pattern | Why It's Bad | What to Do Instead |
|-------------|-------------|-------------------|
| No reranking | Poor precision in final context | Add cross-encoder reranker |
| Too many chunks in prompt | Dilutes relevant info, high cost | Limit to 3–5 most relevant |
| Same embedding for all doc types | Poor retrieval for mixed content | Use specialized embeddings or metadata filtering |
| No caching | Unnecessary LLM calls | Add semantic cache layer |
| Ignoring chunk boundaries | Broken context, poor answers | Use document-aware chunking |

---

## 🔗 Related Resources

- [GenAI System Design One-Pager](genai-system-design-one-pager.md) — Full 5-step interview flow
- [HLD Components Map](hld-components-map.md) — Classical system components
- [Trade-offs Matrix](trade-offs-matrix.md) — General design trade-offs
- [GenAI Concepts](../../06-genai-systems/00-concepts/) — Deep theory
- [GenAI Concepts: RAG Architecture](../../06-genai-systems/00-concepts/rag-architecture/) — Full RAG reference

---

*RAG is the most commonly tested GenAI pattern — master this cheatsheet! 🔍*
