# INTERVIEW-QA for AI Search Engine (Perplexity-style)

This document provides substantive, problem-specific design guidance for building a multi-tenant AI search engine.

## Interview Guide
This section contains rigorous Q&A for candidate evaluation.

### Deep Dive: Query Decomposition

**Q: How does the system handle query decomposition at scale?**
**Weak Answer:** It uses a basic algorithm without caching.
**Strong Answer:** User queries in AI search are often complex and multi-faceted. The query decomposition module breaks these down into simpler, atomic sub-queries that can be executed independently against the search index. Furthermore, we implement rigorous monitoring for latency. For example, a query like 'What is the capital of France and its population?' is split into 'What is the capital of France?' and 'What is the population of the capital of France?'. This improves retrieval recall. This ensures the P99 latency remains within budget.

**Q: How does the system handle query decomposition at scale?**
**Weak Answer:** It uses a basic algorithm without caching.
**Strong Answer:** For example, a query like 'What is the capital of France and its population?' is split into 'What is the capital of France?' and 'What is the population of the capital of France?'. This improves retrieval recall. Furthermore, we implement rigorous monitoring for latency. We use a lightweight LLM (e.g., Llama 3 8B) for decomposition to minimize latency. The prompt instructs the model to output a JSON array of sub-queries. This ensures the P99 latency remains within budget.

**Q: How does the system handle query decomposition at scale?**
**Weak Answer:** It uses a basic algorithm without caching.
**Strong Answer:** We use a lightweight LLM (e.g., Llama 3 8B) for decomposition to minimize latency. The prompt instructs the model to output a JSON array of sub-queries. Furthermore, we implement rigorous monitoring for latency. Decomposition must handle temporal constraints. 'Who won the World Series last year?' needs entity resolution for 'last year' based on the current timestamp. This ensures the P99 latency remains within budget.

**Q: How does the system handle query decomposition at scale?**
**Weak Answer:** It uses a basic algorithm without caching.
**Strong Answer:** Decomposition must handle temporal constraints. 'Who won the World Series last year?' needs entity resolution for 'last year' based on the current timestamp. Furthermore, we implement rigorous monitoring for latency. A critical trade-off is latency vs. recall. More sub-queries mean better recall but higher retrieval latency and more tokens sent to the final generation model. This ensures the P99 latency remains within budget.

**Q: How does the system handle query decomposition at scale?**
**Weak Answer:** It uses a basic algorithm without caching.
**Strong Answer:** A critical trade-off is latency vs. recall. More sub-queries mean better recall but higher retrieval latency and more tokens sent to the final generation model. Furthermore, we implement rigorous monitoring for latency. To mitigate latency, sub-queries are executed concurrently in a scatter-gather pattern. This ensures the P99 latency remains within budget.

**Q: How does the system handle query decomposition at scale?**
**Weak Answer:** It uses a basic algorithm without caching.
**Strong Answer:** To mitigate latency, sub-queries are executed concurrently in a scatter-gather pattern. Furthermore, we implement rigorous monitoring for latency. Query rewriting is also performed here. Typos are corrected, and synonyms are expanded. 'nyc pop' becomes 'New York City population'. This ensures the P99 latency remains within budget.

**Q: How does the system handle query decomposition at scale?**
**Weak Answer:** It uses a basic algorithm without caching.
**Strong Answer:** Query rewriting is also performed here. Typos are corrected, and synonyms are expanded. 'nyc pop' becomes 'New York City population'. Furthermore, we implement rigorous monitoring for latency. We maintain a cache of common query decompositions using Redis. If a query matches perfectly, we bypass the LLM. This ensures the P99 latency remains within budget.

**Q: How does the system handle query decomposition at scale?**
**Weak Answer:** It uses a basic algorithm without caching.
**Strong Answer:** We maintain a cache of common query decompositions using Redis. If a query matches perfectly, we bypass the LLM. Furthermore, we implement rigorous monitoring for latency. Some queries don't need decomposition (e.g., 'weather in Tokyo'). A fast classifier (e.g., a small BERT model or prompt routing) decides if decomposition is necessary. This ensures the P99 latency remains within budget.

**Q: How does the system handle query decomposition at scale?**
**Weak Answer:** It uses a basic algorithm without caching.
**Strong Answer:** Some queries don't need decomposition (e.g., 'weather in Tokyo'). A fast classifier (e.g., a small BERT model or prompt routing) decides if decomposition is necessary. Furthermore, we implement rigorous monitoring for latency. The system sets a hard limit (e.g., max 5 sub-queries) to bound downstream computational costs. This ensures the P99 latency remains within budget.

**Q: How does the system handle query decomposition at scale?**
**Weak Answer:** It uses a basic algorithm without caching.
**Strong Answer:** The system sets a hard limit (e.g., max 5 sub-queries) to bound downstream computational costs. Furthermore, we implement rigorous monitoring for latency. User queries in AI search are often complex and multi-faceted. The query decomposition module breaks these down into simpler, atomic sub-queries that can be executed independently against the search index. This ensures the P99 latency remains within budget.

### Deep Dive: Web Retrieval

**Q: How does the system handle web retrieval at scale?**
**Weak Answer:** It uses a basic algorithm without caching.
**Strong Answer:** The web retrieval component is responsible for finding the most relevant documents for each sub-query. Furthermore, we implement rigorous monitoring for latency. We use a hybrid search approach, combining sparse retrieval (BM25) and dense retrieval (vector embeddings). This ensures the P99 latency remains within budget.

**Q: How does the system handle web retrieval at scale?**
**Weak Answer:** It uses a basic algorithm without caching.
**Strong Answer:** We use a hybrid search approach, combining sparse retrieval (BM25) and dense retrieval (vector embeddings). Furthermore, we implement rigorous monitoring for latency. BM25 is excellent for exact keyword matches, such as specific product names or error codes, which embeddings might struggle with. This ensures the P99 latency remains within budget.

**Q: How does the system handle web retrieval at scale?**
**Weak Answer:** It uses a basic algorithm without caching.
**Strong Answer:** BM25 is excellent for exact keyword matches, such as specific product names or error codes, which embeddings might struggle with. Furthermore, we implement rigorous monitoring for latency. Dense retrieval captures semantic meaning, allowing us to find relevant documents even if the exact keywords are missing. This ensures the P99 latency remains within budget.

**Q: How does the system handle web retrieval at scale?**
**Weak Answer:** It uses a basic algorithm without caching.
**Strong Answer:** Dense retrieval captures semantic meaning, allowing us to find relevant documents even if the exact keywords are missing. Furthermore, we implement rigorous monitoring for latency. We index billions of web pages. This requires a distributed search engine like Elasticsearch or a specialized vector database like Milvus or Pinecone. This ensures the P99 latency remains within budget.

**Q: How does the system handle web retrieval at scale?**
**Weak Answer:** It uses a basic algorithm without caching.
**Strong Answer:** We index billions of web pages. This requires a distributed search engine like Elasticsearch or a specialized vector database like Milvus or Pinecone. Furthermore, we implement rigorous monitoring for latency. Document chunking is crucial. Web pages are parsed, cleaned of HTML boilerplate, and split into 512-token chunks. This ensures the P99 latency remains within budget.

**Q: How does the system handle web retrieval at scale?**
**Weak Answer:** It uses a basic algorithm without caching.
**Strong Answer:** Document chunking is crucial. Web pages are parsed, cleaned of HTML boilerplate, and split into 512-token chunks. Furthermore, we implement rigorous monitoring for latency. Each chunk is embedded using a model like text-embedding-3-small or a fine-tuned BGE model. This ensures the P99 latency remains within budget.

**Q: How does the system handle web retrieval at scale?**
**Weak Answer:** It uses a basic algorithm without caching.
**Strong Answer:** Each chunk is embedded using a model like text-embedding-3-small or a fine-tuned BGE model. Furthermore, we implement rigorous monitoring for latency. To handle the massive scale, we use Approximate Nearest Neighbor (ANN) algorithms like HNSW (Hierarchical Navigable Small World) for vector search. This ensures the P99 latency remains within budget.

**Q: How does the system handle web retrieval at scale?**
**Weak Answer:** It uses a basic algorithm without caching.
**Strong Answer:** To handle the massive scale, we use Approximate Nearest Neighbor (ANN) algorithms like HNSW (Hierarchical Navigable Small World) for vector search. Furthermore, we implement rigorous monitoring for latency. Retrieval latency is a major bottleneck. We aggressively cache retrieval results for popular queries using Memcached. This ensures the P99 latency remains within budget.

**Q: How does the system handle web retrieval at scale?**
**Weak Answer:** It uses a basic algorithm without caching.
**Strong Answer:** Retrieval latency is a major bottleneck. We aggressively cache retrieval results for popular queries using Memcached. Furthermore, we implement rigorous monitoring for latency. Freshness is critical for news queries. We maintain a separate, smaller 'real-time' index that is updated continuously, bypassing the slower batch processing pipeline. This ensures the P99 latency remains within budget.

**Q: How does the system handle web retrieval at scale?**
**Weak Answer:** It uses a basic algorithm without caching.
**Strong Answer:** Freshness is critical for news queries. We maintain a separate, smaller 'real-time' index that is updated continuously, bypassing the slower batch processing pipeline. Furthermore, we implement rigorous monitoring for latency. The web retrieval component is responsible for finding the most relevant documents for each sub-query. This ensures the P99 latency remains within budget.

### Deep Dive: Reranking

**Q: How does the system handle reranking at scale?**
**Weak Answer:** It uses a basic algorithm without caching.
**Strong Answer:** The initial retrieval phase might return 100s of documents per sub-query. Reranking identifies the top 5-10 most relevant ones for the generator. Furthermore, we implement rigorous monitoring for latency. A cross-encoder model (e.g., a fine-tuned DeBERTa) is typically used for reranking. It takes the query and document chunk as a pair and scores their relevance. This ensures the P99 latency remains within budget.

**Q: How does the system handle reranking at scale?**
**Weak Answer:** It uses a basic algorithm without caching.
**Strong Answer:** A cross-encoder model (e.g., a fine-tuned DeBERTa) is typically used for reranking. It takes the query and document chunk as a pair and scores their relevance. Furthermore, we implement rigorous monitoring for latency. Cross-encoders are computationally expensive. To meet our <100ms latency budget, we use a relatively small model (e.g., 200M parameters) or deploy on GPUs with TensorRT. This ensures the P99 latency remains within budget.

**Q: How does the system handle reranking at scale?**
**Weak Answer:** It uses a basic algorithm without caching.
**Strong Answer:** Cross-encoders are computationally expensive. To meet our <100ms latency budget, we use a relatively small model (e.g., 200M parameters) or deploy on GPUs with TensorRT. Furthermore, we implement rigorous monitoring for latency. We can also use LLM-as-a-judge for reranking (e.g., RankLLaMA), but this is usually too slow for real-time consumer search and is reserved for offline evaluation. This ensures the P99 latency remains within budget.

**Q: How does the system handle reranking at scale?**
**Weak Answer:** It uses a basic algorithm without caching.
**Strong Answer:** We can also use LLM-as-a-judge for reranking (e.g., RankLLaMA), but this is usually too slow for real-time consumer search and is reserved for offline evaluation. Furthermore, we implement rigorous monitoring for latency. The reranker considers multiple signals: semantic relevance, document freshness (critical for news), domain authority (favoring reputable sites), and user engagement metrics. This ensures the P99 latency remains within budget.

**Q: How does the system handle reranking at scale?**
**Weak Answer:** It uses a basic algorithm without caching.
**Strong Answer:** The reranker considers multiple signals: semantic relevance, document freshness (critical for news), domain authority (favoring reputable sites), and user engagement metrics. Furthermore, we implement rigorous monitoring for latency. Documents are often grouped by domain to ensure source diversity. We don't want all 10 citations coming from the same website. This ensures the P99 latency remains within budget.

**Q: How does the system handle reranking at scale?**
**Weak Answer:** It uses a basic algorithm without caching.
**Strong Answer:** Documents are often grouped by domain to ensure source diversity. We don't want all 10 citations coming from the same website. Furthermore, we implement rigorous monitoring for latency. Reranking helps mitigate the 'lost in the middle' phenomenon of LLMs by ensuring the absolute best information is placed at the beginning or end of the context window. This ensures the P99 latency remains within budget.

**Q: How does the system handle reranking at scale?**
**Weak Answer:** It uses a basic algorithm without caching.
**Strong Answer:** Reranking helps mitigate the 'lost in the middle' phenomenon of LLMs by ensuring the absolute best information is placed at the beginning or end of the context window. Furthermore, we implement rigorous monitoring for latency. We truncate the list of reranked documents dynamically based on a confidence threshold to save tokens in the generation phase. This ensures the P99 latency remains within budget.

**Q: How does the system handle reranking at scale?**
**Weak Answer:** It uses a basic algorithm without caching.
**Strong Answer:** We truncate the list of reranked documents dynamically based on a confidence threshold to save tokens in the generation phase. Furthermore, we implement rigorous monitoring for latency. For long queries, we might use ColBERT, a late-interaction model, which offers a good balance between the speed of bi-encoders and the accuracy of cross-encoders. This ensures the P99 latency remains within budget.

**Q: How does the system handle reranking at scale?**
**Weak Answer:** It uses a basic algorithm without caching.
**Strong Answer:** For long queries, we might use ColBERT, a late-interaction model, which offers a good balance between the speed of bi-encoders and the accuracy of cross-encoders. Furthermore, we implement rigorous monitoring for latency. We must handle duplicate or near-duplicate documents retrieved from different sources. The reranker includes a deduplication step based on content hashing or embedding similarity. This ensures the P99 latency remains within budget.

**Q: How does the system handle reranking at scale?**
**Weak Answer:** It uses a basic algorithm without caching.
**Strong Answer:** We must handle duplicate or near-duplicate documents retrieved from different sources. The reranker includes a deduplication step based on content hashing or embedding similarity. Furthermore, we implement rigorous monitoring for latency. The initial retrieval phase might return 100s of documents per sub-query. Reranking identifies the top 5-10 most relevant ones for the generator. This ensures the P99 latency remains within budget.

### Deep Dive: Grounded Generation with Citations

**Q: How does the system handle grounded generation with citations at scale?**
**Weak Answer:** It uses a basic algorithm without caching.
**Strong Answer:** The generator (e.g., GPT-4o or a fine-tuned Llama 3 70B) synthesizes the final answer using the retrieved and reranked documents. Furthermore, we implement rigorous monitoring for latency. The prompt instructs the model to answer the query *only* using the provided context and to cite its sources using a specific format (e.g., [1], [2]). This ensures the P99 latency remains within budget.

**Q: How does the system handle grounded generation with citations at scale?**
**Weak Answer:** It uses a basic algorithm without caching.
**Strong Answer:** The prompt instructs the model to answer the query *only* using the provided context and to cite its sources using a specific format (e.g., [1], [2]). Furthermore, we implement rigorous monitoring for latency. This 'grounding' significantly reduces hallucinations, as the model's generation is constrained by empirical evidence. This ensures the P99 latency remains within budget.

**Q: How does the system handle grounded generation with citations at scale?**
**Weak Answer:** It uses a basic algorithm without caching.
**Strong Answer:** This 'grounding' significantly reduces hallucinations, as the model's generation is constrained by empirical evidence. Furthermore, we implement rigorous monitoring for latency. However, hallucinations can still occur if the model misinterprets the context or combines information incorrectly. This requires rigorous evaluation. This ensures the P99 latency remains within budget.

**Q: How does the system handle grounded generation with citations at scale?**
**Weak Answer:** It uses a basic algorithm without caching.
**Strong Answer:** However, hallucinations can still occur if the model misinterprets the context or combines information incorrectly. This requires rigorous evaluation. Furthermore, we implement rigorous monitoring for latency. To enforce citation accuracy, we can use a post-processing verification step. A smaller model checks if the generated sentence is actually supported by the cited document. This ensures the P99 latency remains within budget.

**Q: How does the system handle grounded generation with citations at scale?**
**Weak Answer:** It uses a basic algorithm without caching.
**Strong Answer:** To enforce citation accuracy, we can use a post-processing verification step. A smaller model checks if the generated sentence is actually supported by the cited document. Furthermore, we implement rigorous monitoring for latency. If a citation is invalid, the system can attempt to fix it or strip the sentence entirely. This ensures the P99 latency remains within budget.

**Q: How does the system handle grounded generation with citations at scale?**
**Weak Answer:** It uses a basic algorithm without caching.
**Strong Answer:** If a citation is invalid, the system can attempt to fix it or strip the sentence entirely. Furthermore, we implement rigorous monitoring for latency. The prompt must also instruct the model to handle contradictory information. If Source A says X and Source B says Y, the model should explain the discrepancy. This ensures the P99 latency remains within budget.

**Q: How does the system handle grounded generation with citations at scale?**
**Weak Answer:** It uses a basic algorithm without caching.
**Strong Answer:** The prompt must also instruct the model to handle contradictory information. If Source A says X and Source B says Y, the model should explain the discrepancy. Furthermore, we implement rigorous monitoring for latency. Context window management is crucial. We must ensure the query, system prompt, and all retrieved chunks fit within the model's limit (e.g., 32k or 128k tokens). This ensures the P99 latency remains within budget.

**Q: How does the system handle grounded generation with citations at scale?**
**Weak Answer:** It uses a basic algorithm without caching.
**Strong Answer:** Context window management is crucial. We must ensure the query, system prompt, and all retrieved chunks fit within the model's limit (e.g., 32k or 128k tokens). Furthermore, we implement rigorous monitoring for latency. We prioritize chunks based on their reranker score when packing the context window. This ensures the P99 latency remains within budget.

**Q: How does the system handle grounded generation with citations at scale?**
**Weak Answer:** It uses a basic algorithm without caching.
**Strong Answer:** We prioritize chunks based on their reranker score when packing the context window. Furthermore, we implement rigorous monitoring for latency. The generated response must be formatted in Markdown, seamlessly integrating the inline citations which are then rendered as clickable links in the frontend. This ensures the P99 latency remains within budget.

**Q: How does the system handle grounded generation with citations at scale?**
**Weak Answer:** It uses a basic algorithm without caching.
**Strong Answer:** The generated response must be formatted in Markdown, seamlessly integrating the inline citations which are then rendered as clickable links in the frontend. Furthermore, we implement rigorous monitoring for latency. The generator (e.g., GPT-4o or a fine-tuned Llama 3 70B) synthesizes the final answer using the retrieved and reranked documents. This ensures the P99 latency remains within budget.

### Deep Dive: Streaming

**Q: How does the system handle streaming at scale?**
**Weak Answer:** It uses a basic algorithm without caching.
**Strong Answer:** Streaming is non-negotiable for AI search. Users will not wait 5-10 seconds for a full answer to generate. Furthermore, we implement rigorous monitoring for latency. We use Server-Sent Events (SSE) or WebSockets to stream the response token-by-token from the LLM to the client. This ensures the P99 latency remains within budget.

**Q: How does the system handle streaming at scale?**
**Weak Answer:** It uses a basic algorithm without caching.
**Strong Answer:** We use Server-Sent Events (SSE) or WebSockets to stream the response token-by-token from the LLM to the client. Furthermore, we implement rigorous monitoring for latency. Time-To-First-Token (TTFT) is our primary latency metric. It includes the time for decomposition, retrieval, reranking, and the initial LLM forward pass. This ensures the P99 latency remains within budget.

**Q: How does the system handle streaming at scale?**
**Weak Answer:** It uses a basic algorithm without caching.
**Strong Answer:** Time-To-First-Token (TTFT) is our primary latency metric. It includes the time for decomposition, retrieval, reranking, and the initial LLM forward pass. Furthermore, we implement rigorous monitoring for latency. We aim for a TTFT of under 1 second. This requires aggressive optimization of the pre-generation pipeline. This ensures the P99 latency remains within budget.

**Q: How does the system handle streaming at scale?**
**Weak Answer:** It uses a basic algorithm without caching.
**Strong Answer:** We aim for a TTFT of under 1 second. This requires aggressive optimization of the pre-generation pipeline. Furthermore, we implement rigorous monitoring for latency. Streaming citations presents a UI challenge. The citation number (e.g., [1]) might be generated before the actual source URL is fully resolved or mapped in the frontend. This ensures the P99 latency remains within budget.

**Q: How does the system handle streaming at scale?**
**Weak Answer:** It uses a basic algorithm without caching.
**Strong Answer:** Streaming citations presents a UI challenge. The citation number (e.g., [1]) might be generated before the actual source URL is fully resolved or mapped in the frontend. Furthermore, we implement rigorous monitoring for latency. We send the list of sources as a separate JSON payload *before* starting the text stream, so the frontend can immediately render the citation links as they arrive. This ensures the P99 latency remains within budget.

**Q: How does the system handle streaming at scale?**
**Weak Answer:** It uses a basic algorithm without caching.
**Strong Answer:** We send the list of sources as a separate JSON payload *before* starting the text stream, so the frontend can immediately render the citation links as they arrive. Furthermore, we implement rigorous monitoring for latency. If the generator model supports speculative decoding, we can significantly increase the streaming token rate (tokens per second). This ensures the P99 latency remains within budget.

**Q: How does the system handle streaming at scale?**
**Weak Answer:** It uses a basic algorithm without caching.
**Strong Answer:** If the generator model supports speculative decoding, we can significantly increase the streaming token rate (tokens per second). Furthermore, we implement rigorous monitoring for latency. Connection drops during streaming must be handled gracefully. The client should be able to resume or retry the generation. This ensures the P99 latency remains within budget.

**Q: How does the system handle streaming at scale?**
**Weak Answer:** It uses a basic algorithm without caching.
**Strong Answer:** Connection drops during streaming must be handled gracefully. The client should be able to resume or retry the generation. Furthermore, we implement rigorous monitoring for latency. We must ensure that the safety filters (checking for toxicity or PII) operate effectively on streamed tokens, often using a sliding window approach. This ensures the P99 latency remains within budget.

**Q: How does the system handle streaming at scale?**
**Weak Answer:** It uses a basic algorithm without caching.
**Strong Answer:** We must ensure that the safety filters (checking for toxicity or PII) operate effectively on streamed tokens, often using a sliding window approach. Furthermore, we implement rigorous monitoring for latency. Load balancing for streaming connections is stateful. We use consistent hashing or specific routing rules to keep the connection pinned to the correct inference server. This ensures the P99 latency remains within budget.

**Q: How does the system handle streaming at scale?**
**Weak Answer:** It uses a basic algorithm without caching.
**Strong Answer:** Load balancing for streaming connections is stateful. We use consistent hashing or specific routing rules to keep the connection pinned to the correct inference server. Furthermore, we implement rigorous monitoring for latency. Streaming is non-negotiable for AI search. Users will not wait 5-10 seconds for a full answer to generate. This ensures the P99 latency remains within budget.

### Deep Dive: Caching

**Q: How does the system handle caching at scale?**
**Weak Answer:** It uses a basic algorithm without caching.
**Strong Answer:** Caching occurs at multiple layers: exact query match, sub-query retrieval, and semantic similarity. Furthermore, we implement rigorous monitoring for latency. Exact Query Cache (Redis): If a user asks exactly the same question as a recent query, we return the cached final response instantly (TTFT < 50ms). This ensures the P99 latency remains within budget.

**Q: How does the system handle caching at scale?**
**Weak Answer:** It uses a basic algorithm without caching.
**Strong Answer:** Exact Query Cache (Redis): If a user asks exactly the same question as a recent query, we return the cached final response instantly (TTFT < 50ms). Furthermore, we implement rigorous monitoring for latency. This cache must have a short TTL (e.g., 1 hour) for queries related to news or real-time events, but can be longer for evergreen queries (e.g., 'history of Rome'). This ensures the P99 latency remains within budget.

**Q: How does the system handle caching at scale?**
**Weak Answer:** It uses a basic algorithm without caching.
**Strong Answer:** This cache must have a short TTL (e.g., 1 hour) for queries related to news or real-time events, but can be longer for evergreen queries (e.g., 'history of Rome'). Furthermore, we implement rigorous monitoring for latency. Sub-query Cache: We cache the retrieval and reranking results for common sub-queries. 'What is the population of Paris?' is useful across many complex queries. This ensures the P99 latency remains within budget.

**Q: How does the system handle caching at scale?**
**Weak Answer:** It uses a basic algorithm without caching.
**Strong Answer:** Sub-query Cache: We cache the retrieval and reranking results for common sub-queries. 'What is the population of Paris?' is useful across many complex queries. Furthermore, we implement rigorous monitoring for latency. Semantic Cache (Vector DB): We can use a fast vector search on incoming queries against recently answered queries. If the semantic similarity is >0.95, we reuse the answer. This ensures the P99 latency remains within budget.

**Q: How does the system handle caching at scale?**
**Weak Answer:** It uses a basic algorithm without caching.
**Strong Answer:** Semantic Cache (Vector DB): We can use a fast vector search on incoming queries against recently answered queries. If the semantic similarity is >0.95, we reuse the answer. Furthermore, we implement rigorous monitoring for latency. Semantic caching is risky. 'How to fix a flat tire on a bike' and 'How to fix a flat tire on a car' are semantically similar but require vastly different answers. This ensures the P99 latency remains within budget.

**Q: How does the system handle caching at scale?**
**Weak Answer:** It uses a basic algorithm without caching.
**Strong Answer:** Semantic caching is risky. 'How to fix a flat tire on a bike' and 'How to fix a flat tire on a car' are semantically similar but require vastly different answers. Furthermore, we implement rigorous monitoring for latency. We use a fast verification model to double-check semantic cache hits before serving them to the user. This ensures the P99 latency remains within budget.

**Q: How does the system handle caching at scale?**
**Weak Answer:** It uses a basic algorithm without caching.
**Strong Answer:** We use a fast verification model to double-check semantic cache hits before serving them to the user. Furthermore, we implement rigorous monitoring for latency. Cache invalidation is tricky. When a major news event breaks, we must proactively invalidate caches related to that topic. This ensures the P99 latency remains within budget.

**Q: How does the system handle caching at scale?**
**Weak Answer:** It uses a basic algorithm without caching.
**Strong Answer:** Cache invalidation is tricky. When a major news event breaks, we must proactively invalidate caches related to that topic. Furthermore, we implement rigorous monitoring for latency. We use edge caching (CDN) for static assets, but the dynamic AI search responses are cached at the application layer in the data center. This ensures the P99 latency remains within budget.

**Q: How does the system handle caching at scale?**
**Weak Answer:** It uses a basic algorithm without caching.
**Strong Answer:** We use edge caching (CDN) for static assets, but the dynamic AI search responses are cached at the application layer in the data center. Furthermore, we implement rigorous monitoring for latency. The caching strategy dramatically reduces API costs (OpenAI/Anthropic) and compute requirements for self-hosted models. This ensures the P99 latency remains within budget.

**Q: How does the system handle caching at scale?**
**Weak Answer:** It uses a basic algorithm without caching.
**Strong Answer:** The caching strategy dramatically reduces API costs (OpenAI/Anthropic) and compute requirements for self-hosted models. Furthermore, we implement rigorous monitoring for latency. Caching occurs at multiple layers: exact query match, sub-query retrieval, and semantic similarity. This ensures the P99 latency remains within budget.

### Deep Dive: Freshness and Cost

**Q: How does the system handle freshness and cost at scale?**
**Weak Answer:** It uses a basic algorithm without caching.
**Strong Answer:** Freshness is the defining feature of AI search compared to static knowledge bases. Furthermore, we implement rigorous monitoring for latency. Our crawler pipeline constantly monitors RSS feeds, news sites, and social media for new content. This ensures the P99 latency remains within budget.

**Q: How does the system handle freshness and cost at scale?**
**Weak Answer:** It uses a basic algorithm without caching.
**Strong Answer:** Our crawler pipeline constantly monitors RSS feeds, news sites, and social media for new content. Furthermore, we implement rigorous monitoring for latency. We use an incremental indexing strategy. New documents are added to a fast-update memory-mapped index before being merged into the main disk-based index. This ensures the P99 latency remains within budget.

**Q: How does the system handle freshness and cost at scale?**
**Weak Answer:** It uses a basic algorithm without caching.
**Strong Answer:** We use an incremental indexing strategy. New documents are added to a fast-update memory-mapped index before being merged into the main disk-based index. Furthermore, we implement rigorous monitoring for latency. Cost management is a primary architectural driver. A single AI search query can cost 10x to 100x more than a traditional keyword search. This ensures the P99 latency remains within budget.

**Q: How does the system handle freshness and cost at scale?**
**Weak Answer:** It uses a basic algorithm without caching.
**Strong Answer:** Cost management is a primary architectural driver. A single AI search query can cost 10x to 100x more than a traditional keyword search. Furthermore, we implement rigorous monitoring for latency. We employ a cascade of models. Simple queries might be handled entirely by an 8B parameter model, while complex reasoning requires a 70B or proprietary model. This ensures the P99 latency remains within budget.

**Q: How does the system handle freshness and cost at scale?**
**Weak Answer:** It uses a basic algorithm without caching.
**Strong Answer:** We employ a cascade of models. Simple queries might be handled entirely by an 8B parameter model, while complex reasoning requires a 70B or proprietary model. Furthermore, we implement rigorous monitoring for latency. We dynamically adjust the number of retrieved documents based on the query complexity. Simple queries get 3 docs; complex ones get 20. This saves tokens. This ensures the P99 latency remains within budget.

**Q: How does the system handle freshness and cost at scale?**
**Weak Answer:** It uses a basic algorithm without caching.
**Strong Answer:** We dynamically adjust the number of retrieved documents based on the query complexity. Simple queries get 3 docs; complex ones get 20. This saves tokens. Furthermore, we implement rigorous monitoring for latency. Context caching (if supported by the LLM provider, like Anthropic's prompt caching) is used extensively for the system prompt and common instructions. This ensures the P99 latency remains within budget.

**Q: How does the system handle freshness and cost at scale?**
**Weak Answer:** It uses a basic algorithm without caching.
**Strong Answer:** Context caching (if supported by the LLM provider, like Anthropic's prompt caching) is used extensively for the system prompt and common instructions. Furthermore, we implement rigorous monitoring for latency. We track the cost per query and aggregate it by user and tenant. This data is fed into our billing system and alerting pipelines. This ensures the P99 latency remains within budget.

**Q: How does the system handle freshness and cost at scale?**
**Weak Answer:** It uses a basic algorithm without caching.
**Strong Answer:** We track the cost per query and aggregate it by user and tenant. This data is fed into our billing system and alerting pipelines. Furthermore, we implement rigorous monitoring for latency. To handle spikes in traffic without breaking the bank, we implement dynamic rate limiting and graceful degradation (e.g., disabling the most expensive reasoning steps under high load). This ensures the P99 latency remains within budget.

**Q: How does the system handle freshness and cost at scale?**
**Weak Answer:** It uses a basic algorithm without caching.
**Strong Answer:** To handle spikes in traffic without breaking the bank, we implement dynamic rate limiting and graceful degradation (e.g., disabling the most expensive reasoning steps under high load). Furthermore, we implement rigorous monitoring for latency. We heavily utilize spot instances for offline batch processing and evaluation to reduce cloud compute costs. This ensures the P99 latency remains within budget.

**Q: How does the system handle freshness and cost at scale?**
**Weak Answer:** It uses a basic algorithm without caching.
**Strong Answer:** We heavily utilize spot instances for offline batch processing and evaluation to reduce cloud compute costs. Furthermore, we implement rigorous monitoring for latency. Freshness is the defining feature of AI search compared to static knowledge bases. This ensures the P99 latency remains within budget.

### Deep Dive: Evaluation

**Q: How does the system handle evaluation at scale?**
**Weak Answer:** It uses a basic algorithm without caching.
**Strong Answer:** Evaluating AI search requires a multi-faceted approach, moving beyond simple accuracy metrics. Furthermore, we implement rigorous monitoring for latency. We use the RAG Triad for automated evaluation: Context Relevance, Answer Relevance, and Groundedness. This ensures the P99 latency remains within budget.

**Q: How does the system handle evaluation at scale?**
**Weak Answer:** It uses a basic algorithm without caching.
**Strong Answer:** We use the RAG Triad for automated evaluation: Context Relevance, Answer Relevance, and Groundedness. Furthermore, we implement rigorous monitoring for latency. Context Relevance checks if the retrieved documents actually contain the answer to the query. This ensures the P99 latency remains within budget.

**Q: How does the system handle evaluation at scale?**
**Weak Answer:** It uses a basic algorithm without caching.
**Strong Answer:** Context Relevance checks if the retrieved documents actually contain the answer to the query. Furthermore, we implement rigorous monitoring for latency. Answer Relevance ensures the final generated text directly addresses the user's question, without going off on tangents. This ensures the P99 latency remains within budget.

**Q: How does the system handle evaluation at scale?**
**Weak Answer:** It uses a basic algorithm without caching.
**Strong Answer:** Answer Relevance ensures the final generated text directly addresses the user's question, without going off on tangents. Furthermore, we implement rigorous monitoring for latency. Groundedness is paramount. We measure the hallucination rate by checking if every claim in the generated answer is supported by a citation. This ensures the P99 latency remains within budget.

**Q: How does the system handle evaluation at scale?**
**Weak Answer:** It uses a basic algorithm without caching.
**Strong Answer:** Groundedness is paramount. We measure the hallucination rate by checking if every claim in the generated answer is supported by a citation. Furthermore, we implement rigorous monitoring for latency. We employ 'LLM-as-a-judge' pipelines running continuously on a sample of production traffic. GPT-4 evaluates the outputs of our production models. This ensures the P99 latency remains within budget.

**Q: How does the system handle evaluation at scale?**
**Weak Answer:** It uses a basic algorithm without caching.
**Strong Answer:** We employ 'LLM-as-a-judge' pipelines running continuously on a sample of production traffic. GPT-4 evaluates the outputs of our production models. Furthermore, we implement rigorous monitoring for latency. Human evaluation remains essential. We have a team of domain experts who grade responses based on a detailed rubric (accuracy, tone, helpfulness). This ensures the P99 latency remains within budget.

**Q: How does the system handle evaluation at scale?**
**Weak Answer:** It uses a basic algorithm without caching.
**Strong Answer:** Human evaluation remains essential. We have a team of domain experts who grade responses based on a detailed rubric (accuracy, tone, helpfulness). Furthermore, we implement rigorous monitoring for latency. A/B testing is used for every change. We route 5% of traffic to a new reranker model and compare engagement metrics (session length, follow-up queries, explicit thumbs up/down). This ensures the P99 latency remains within budget.

**Q: How does the system handle evaluation at scale?**
**Weak Answer:** It uses a basic algorithm without caching.
**Strong Answer:** A/B testing is used for every change. We route 5% of traffic to a new reranker model and compare engagement metrics (session length, follow-up queries, explicit thumbs up/down). Furthermore, we implement rigorous monitoring for latency. We specifically test for adversarial inputs and jailbreak attempts to ensure our safety filters are robust. This ensures the P99 latency remains within budget.

**Q: How does the system handle evaluation at scale?**
**Weak Answer:** It uses a basic algorithm without caching.
**Strong Answer:** We specifically test for adversarial inputs and jailbreak attempts to ensure our safety filters are robust. Furthermore, we implement rigorous monitoring for latency. Latency and cost metrics are tracked alongside quality metrics. A model that is 2% more accurate but 5x slower and 10x more expensive might not be deployed. This ensures the P99 latency remains within budget.

**Q: How does the system handle evaluation at scale?**
**Weak Answer:** It uses a basic algorithm without caching.
**Strong Answer:** Latency and cost metrics are tracked alongside quality metrics. A model that is 2% more accurate but 5x slower and 10x more expensive might not be deployed. Furthermore, we implement rigorous monitoring for latency. Evaluating AI search requires a multi-faceted approach, moving beyond simple accuracy metrics. This ensures the P99 latency remains within budget.

### Deep Dive: Query Decomposition

**Q: How does the system handle query decomposition at scale?**
**Weak Answer:** It uses a basic algorithm without caching.
**Strong Answer:** User queries in AI search are often complex and multi-faceted. The query decomposition module breaks these down into simpler, atomic sub-queries that can be executed independently against the search index. Furthermore, we implement rigorous monitoring for latency. For example, a query like 'What is the capital of France and its population?' is split into 'What is the capital of France?' and 'What is the population of the capital of France?'. This improves retrieval recall. This ensures the P99 latency remains within budget.

**Q: How does the system handle degraded LLM API performance during 0 peak events?**
**Weak Answer:** It just retries the request.
**Strong Answer:** We implement a circuit breaker pattern combined with a graceful degradation strategy. If the primary generation model latency exceeds our 800ms budget, we seamlessly route queries to a smaller, faster local fallback model (e.g., Llama-3-8B). This ensures the user still receives a response, albeit with potentially lower reasoning depth, rather than a timeout error.

**Q: How does the system handle degraded LLM API performance during 1 peak events?**
**Weak Answer:** It just retries the request.
**Strong Answer:** We implement a circuit breaker pattern combined with a graceful degradation strategy. If the primary generation model latency exceeds our 800ms budget, we seamlessly route queries to a smaller, faster local fallback model (e.g., Llama-3-8B). This ensures the user still receives a response, albeit with potentially lower reasoning depth, rather than a timeout error.

**Q: How does the system handle degraded LLM API performance during 2 peak events?**
**Weak Answer:** It just retries the request.
**Strong Answer:** We implement a circuit breaker pattern combined with a graceful degradation strategy. If the primary generation model latency exceeds our 800ms budget, we seamlessly route queries to a smaller, faster local fallback model (e.g., Llama-3-8B). This ensures the user still receives a response, albeit with potentially lower reasoning depth, rather than a timeout error.

**Q: How does the system handle degraded LLM API performance during 3 peak events?**
**Weak Answer:** It just retries the request.
**Strong Answer:** We implement a circuit breaker pattern combined with a graceful degradation strategy. If the primary generation model latency exceeds our 800ms budget, we seamlessly route queries to a smaller, faster local fallback model (e.g., Llama-3-8B). This ensures the user still receives a response, albeit with potentially lower reasoning depth, rather than a timeout error.

**Q: How does the system handle degraded LLM API performance during 4 peak events?**
**Weak Answer:** It just retries the request.
**Strong Answer:** We implement a circuit breaker pattern combined with a graceful degradation strategy. If the primary generation model latency exceeds our 800ms budget, we seamlessly route queries to a smaller, faster local fallback model (e.g., Llama-3-8B). This ensures the user still receives a response, albeit with potentially lower reasoning depth, rather than a timeout error.

**Q: How does the system handle degraded LLM API performance during 5 peak events?**
**Weak Answer:** It just retries the request.
**Strong Answer:** We implement a circuit breaker pattern combined with a graceful degradation strategy. If the primary generation model latency exceeds our 800ms budget, we seamlessly route queries to a smaller, faster local fallback model (e.g., Llama-3-8B). This ensures the user still receives a response, albeit with potentially lower reasoning depth, rather than a timeout error.

**Q: How does the system handle degraded LLM API performance during 6 peak events?**
**Weak Answer:** It just retries the request.
**Strong Answer:** We implement a circuit breaker pattern combined with a graceful degradation strategy. If the primary generation model latency exceeds our 800ms budget, we seamlessly route queries to a smaller, faster local fallback model (e.g., Llama-3-8B). This ensures the user still receives a response, albeit with potentially lower reasoning depth, rather than a timeout error.

**Q: How does the system handle degraded LLM API performance during 7 peak events?**
**Weak Answer:** It just retries the request.
**Strong Answer:** We implement a circuit breaker pattern combined with a graceful degradation strategy. If the primary generation model latency exceeds our 800ms budget, we seamlessly route queries to a smaller, faster local fallback model (e.g., Llama-3-8B). This ensures the user still receives a response, albeit with potentially lower reasoning depth, rather than a timeout error.

**Q: How does the system handle degraded LLM API performance during 8 peak events?**
**Weak Answer:** It just retries the request.
**Strong Answer:** We implement a circuit breaker pattern combined with a graceful degradation strategy. If the primary generation model latency exceeds our 800ms budget, we seamlessly route queries to a smaller, faster local fallback model (e.g., Llama-3-8B). This ensures the user still receives a response, albeit with potentially lower reasoning depth, rather than a timeout error.

**Q: How does the system handle degraded LLM API performance during 9 peak events?**
**Weak Answer:** It just retries the request.
**Strong Answer:** We implement a circuit breaker pattern combined with a graceful degradation strategy. If the primary generation model latency exceeds our 800ms budget, we seamlessly route queries to a smaller, faster local fallback model (e.g., Llama-3-8B). This ensures the user still receives a response, albeit with potentially lower reasoning depth, rather than a timeout error.

**Q: How does the system handle degraded LLM API performance during 10 peak events?**
**Weak Answer:** It just retries the request.
**Strong Answer:** We implement a circuit breaker pattern combined with a graceful degradation strategy. If the primary generation model latency exceeds our 800ms budget, we seamlessly route queries to a smaller, faster local fallback model (e.g., Llama-3-8B). This ensures the user still receives a response, albeit with potentially lower reasoning depth, rather than a timeout error.

**Q: How does the system handle degraded LLM API performance during 11 peak events?**
**Weak Answer:** It just retries the request.
**Strong Answer:** We implement a circuit breaker pattern combined with a graceful degradation strategy. If the primary generation model latency exceeds our 800ms budget, we seamlessly route queries to a smaller, faster local fallback model (e.g., Llama-3-8B). This ensures the user still receives a response, albeit with potentially lower reasoning depth, rather than a timeout error.

**Q: How does the system handle degraded LLM API performance during 12 peak events?**
**Weak Answer:** It just retries the request.
**Strong Answer:** We implement a circuit breaker pattern combined with a graceful degradation strategy. If the primary generation model latency exceeds our 800ms budget, we seamlessly route queries to a smaller, faster local fallback model (e.g., Llama-3-8B). This ensures the user still receives a response, albeit with potentially lower reasoning depth, rather than a timeout error.

**Q: How does the system handle degraded LLM API performance during 13 peak events?**
**Weak Answer:** It just retries the request.
**Strong Answer:** We implement a circuit breaker pattern combined with a graceful degradation strategy. If the primary generation model latency exceeds our 800ms budget, we seamlessly route queries to a smaller, faster local fallback model (e.g., Llama-3-8B). This ensures the user still receives a response, albeit with potentially lower reasoning depth, rather than a timeout error.

**Q: How does the system handle degraded LLM API performance during 14 peak events?**
**Weak Answer:** It just retries the request.
**Strong Answer:** We implement a circuit breaker pattern combined with a graceful degradation strategy. If the primary generation model latency exceeds our 800ms budget, we seamlessly route queries to a smaller, faster local fallback model (e.g., Llama-3-8B). This ensures the user still receives a response, albeit with potentially lower reasoning depth, rather than a timeout error.

