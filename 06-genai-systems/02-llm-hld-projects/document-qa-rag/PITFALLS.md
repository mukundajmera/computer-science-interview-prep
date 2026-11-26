# LLM-Powered Document Q&A (RAG System) - Common Pitfalls

## Common pitfalls
1. **Blind Trust in Pure Vector Search:** Relying exclusively on vector (semantic) search for retrieval without incorporating keyword search (BM25) or reranking. This fails drastically in enterprise environments where exact keyword matches, specific acronyms, or serial numbers are critical.
2. **Ignoring Access Control (RBAC) at Retrieval:** Attempting to filter out unauthorized data *after* the LLM has generated a response, or assuming the LLM can securely filter out restricted data based on prompt instructions. The prompt or output filter will inevitably fail or leak information.
3. **Naïve Chunking Strategies:** Splitting documents by an arbitrary fixed character count without overlapping chunks or respecting document boundaries (paragraphs, sentences, headings). This severs context, splitting key concepts down the middle, causing the model to generate incomplete or wrong answers.
4. **Synchronous Batch Generation Over Streaming:** Waiting for the entire LLM response to complete before returning data to the client. For responses that take several seconds to generate, this leads to a poor user experience and perceived high latency.
5. **Lack of Hallucination Grounding:** Not explicitly requiring the LLM to ground its answers using provided citations, and not implementing a verification step to ensure citations map to actual retrieved chunks. This allows the model to inject plausible but entirely fabricated information into enterprise workflows.
6. **No Semantic Caching Strategy:** Caching responses based purely on exact string matches of the user's query rather than the semantic meaning of the query. This results in incredibly low cache hit rates and inflated LLM inference costs for frequently asked questions phrased slightly differently.

## Why these fail interviews
- **Breaks Security and Compliance:** Mishandling access controls in RAG is a massive red flag. Security must be enforced at the data retrieval layer, not the presentation or inference layer.
- **Shows Lack of Domain Expertise:** Proposing pure vector search or basic character splitting demonstrates a theoretical understanding of RAG rather than practical experience with its real-world limitations.
- **Ignores Non-Functional Requirements:** Failing to implement streaming significantly degrades perceived latency, violating user experience requirements.
- **High Operational Costs:** Without semantic caching or proper model routing, LLM API costs will scale linearly and unsustainably with query volume.

## Mitigations
- **Hybrid Retrieval & Reranking:** Implement a hybrid retrieval strategy combining Vector Search (for semantic similarity) and BM25 (for keyword matching), merged via Reciprocal Rank Fusion (RRF), and reordered using a Cross-Encoder reranker.
- **Pre-Retrieval Access Control:** Store document permissions directly as metadata in the vector database and enforce user access filters directly in the vector search query.
- **Semantic Chunking:** Use recursive character splitting that respects logical document structures (headings, paragraphs, sentences) with an overlap (e.g., 512 tokens with 64-token overlap) and preserves metadata like document source, title, and page numbers.
- **Server-Sent Events (SSE) for Streaming:** Stream the LLM response token-by-token back to the client using SSE or WebSockets to reduce perceived first-token latency to under 1 second.
- **Strict Grounding Prompts & Output Verification:** Structure the prompt to mandate citations (e.g., "[Source N]") and implement a post-generation verification step that cross-references output citations against the retrieved context chunks.
- **Semantic Caching:** Cache responses in Redis using the embedded representation of the user query, and serve the cached response for subsequent queries with a high cosine similarity score (e.g., > 0.95).

## Cross-links
- [Problem Statement](PROBLEM.md)
- [Design Document](DESIGN.md)
- [Approach & Trade-offs](APPROACH.md)
