# LLM-Powered Document Q&A (RAG System) - Interview Scoring Rubric

Use this rubric to evaluate design quality and implementation thinking consistently for the LLM-Powered Document Q&A (RAG System) project.

> Related: [PROBLEM](./PROBLEM.md) · [APPROACH](./APPROACH.md) · [DESIGN](./DESIGN.md)

---

## Scoring rubric

| Dimension | Weight | Strong signal |
|---|---:|---|
| Requirements & Scope | 10% | Clarifies document formats, corpus size, access control requirements, latency SLAs (especially streaming), and explicitly scopes out features like real-time sync. |
| Back-of-Envelope Math | 10% | Estimates embedding storage requirements, query volume, LLM token counts per query, and calculates cost per query (including reranking, LLM, and embeddings). |
| Document Ingestion & Chunking | 15% | Outlines an async ingestion pipeline. Defines a robust chunking strategy (e.g., 512 tokens with overlap) preserving document metadata (page, section). |
| Retrieval Strategy | 20% | Proposes a hybrid retrieval approach (vector + BM25) and reciprocal rank fusion (RRF) followed by a cross-encoder reranker for enterprise precision. |
| Prompting, Citations & Guardrails | 20% | Explicitly requires the LLM to cite sources using retrieved chunk metadata. Includes fallback mechanisms ("I don't know") and hallucination checks. |
| Architecture & Performance | 15% | Separates ingestion from querying. Proposes SSE for streaming responses to meet perceived latency targets. Implements semantic caching to reduce costs. |
| Trade-offs & Evaluation | 10% | Weighs hybrid vs pure vector search, dedicated Vector DB vs pgvector, streaming vs batch. Defines metrics like answer relevance, faithfulness, and citation accuracy. |

## Performance bands

- `1/5`: Trivial implementation treating the system like a direct prompt to an LLM without RAG. No chunking strategy, no vector database, and no mechanism for citing sources.
- `3/5`: Basic RAG pipeline with a vector database. Understands the need for chunking and prompt context injection, but misses advanced enterprise requirements like hybrid search, reranking, or access control filtering.
- `5/5`: Enterprise-grade RAG architecture. Includes hybrid retrieval with reranking, strong metadata handling for access control, accurate source citations, asynchronous ingestion, and robust cost/latency optimization (e.g., streaming, semantic caching).

## Cross-links

- [Problem statement](./PROBLEM.md)
- [Approach](./APPROACH.md)
- [Design](./DESIGN.md)
