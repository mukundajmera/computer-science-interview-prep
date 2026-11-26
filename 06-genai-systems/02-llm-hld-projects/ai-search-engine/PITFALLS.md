# PITFALLS for AI Search Engine (Perplexity-style)

This document provides substantive, problem-specific design guidance for building a multi-tenant AI search engine.

### Deep Dive: Query Decomposition

**Pitfall:** Ignoring query decomposition bottlenecks.
**Impact:** User queries in AI search are often complex and multi-faceted. The query decomposition module breaks these down into simpler, atomic sub-queries that can be executed independently against the search index. This causes cascading failures.
**Mitigation:** We use a lightweight LLM (e.g., Llama 3 8B) for decomposition to minimize latency. The prompt instructs the model to output a JSON array of sub-queries. We also deploy circuit breakers.

**Pitfall:** Ignoring query decomposition bottlenecks.
**Impact:** For example, a query like 'What is the capital of France and its population?' is split into 'What is the capital of France?' and 'What is the population of the capital of France?'. This improves retrieval recall. This causes cascading failures.
**Mitigation:** Decomposition must handle temporal constraints. 'Who won the World Series last year?' needs entity resolution for 'last year' based on the current timestamp. We also deploy circuit breakers.

**Pitfall:** Ignoring query decomposition bottlenecks.
**Impact:** We use a lightweight LLM (e.g., Llama 3 8B) for decomposition to minimize latency. The prompt instructs the model to output a JSON array of sub-queries. This causes cascading failures.
**Mitigation:** A critical trade-off is latency vs. recall. More sub-queries mean better recall but higher retrieval latency and more tokens sent to the final generation model. We also deploy circuit breakers.

**Pitfall:** Ignoring query decomposition bottlenecks.
**Impact:** Decomposition must handle temporal constraints. 'Who won the World Series last year?' needs entity resolution for 'last year' based on the current timestamp. This causes cascading failures.
**Mitigation:** To mitigate latency, sub-queries are executed concurrently in a scatter-gather pattern. We also deploy circuit breakers.

**Pitfall:** Ignoring query decomposition bottlenecks.
**Impact:** A critical trade-off is latency vs. recall. More sub-queries mean better recall but higher retrieval latency and more tokens sent to the final generation model. This causes cascading failures.
**Mitigation:** Query rewriting is also performed here. Typos are corrected, and synonyms are expanded. 'nyc pop' becomes 'New York City population'. We also deploy circuit breakers.

**Pitfall:** Ignoring query decomposition bottlenecks.
**Impact:** To mitigate latency, sub-queries are executed concurrently in a scatter-gather pattern. This causes cascading failures.
**Mitigation:** We maintain a cache of common query decompositions using Redis. If a query matches perfectly, we bypass the LLM. We also deploy circuit breakers.

**Pitfall:** Ignoring query decomposition bottlenecks.
**Impact:** Query rewriting is also performed here. Typos are corrected, and synonyms are expanded. 'nyc pop' becomes 'New York City population'. This causes cascading failures.
**Mitigation:** Some queries don't need decomposition (e.g., 'weather in Tokyo'). A fast classifier (e.g., a small BERT model or prompt routing) decides if decomposition is necessary. We also deploy circuit breakers.

**Pitfall:** Ignoring query decomposition bottlenecks.
**Impact:** We maintain a cache of common query decompositions using Redis. If a query matches perfectly, we bypass the LLM. This causes cascading failures.
**Mitigation:** The system sets a hard limit (e.g., max 5 sub-queries) to bound downstream computational costs. We also deploy circuit breakers.

**Pitfall:** Ignoring query decomposition bottlenecks.
**Impact:** Some queries don't need decomposition (e.g., 'weather in Tokyo'). A fast classifier (e.g., a small BERT model or prompt routing) decides if decomposition is necessary. This causes cascading failures.
**Mitigation:** User queries in AI search are often complex and multi-faceted. The query decomposition module breaks these down into simpler, atomic sub-queries that can be executed independently against the search index. We also deploy circuit breakers.

**Pitfall:** Ignoring query decomposition bottlenecks.
**Impact:** The system sets a hard limit (e.g., max 5 sub-queries) to bound downstream computational costs. This causes cascading failures.
**Mitigation:** For example, a query like 'What is the capital of France and its population?' is split into 'What is the capital of France?' and 'What is the population of the capital of France?'. This improves retrieval recall. We also deploy circuit breakers.

### Deep Dive: Web Retrieval

**Pitfall:** Ignoring web retrieval bottlenecks.
**Impact:** The web retrieval component is responsible for finding the most relevant documents for each sub-query. This causes cascading failures.
**Mitigation:** BM25 is excellent for exact keyword matches, such as specific product names or error codes, which embeddings might struggle with. We also deploy circuit breakers.

**Pitfall:** Ignoring web retrieval bottlenecks.
**Impact:** We use a hybrid search approach, combining sparse retrieval (BM25) and dense retrieval (vector embeddings). This causes cascading failures.
**Mitigation:** Dense retrieval captures semantic meaning, allowing us to find relevant documents even if the exact keywords are missing. We also deploy circuit breakers.

**Pitfall:** Ignoring web retrieval bottlenecks.
**Impact:** BM25 is excellent for exact keyword matches, such as specific product names or error codes, which embeddings might struggle with. This causes cascading failures.
**Mitigation:** We index billions of web pages. This requires a distributed search engine like Elasticsearch or a specialized vector database like Milvus or Pinecone. We also deploy circuit breakers.

**Pitfall:** Ignoring web retrieval bottlenecks.
**Impact:** Dense retrieval captures semantic meaning, allowing us to find relevant documents even if the exact keywords are missing. This causes cascading failures.
**Mitigation:** Document chunking is crucial. Web pages are parsed, cleaned of HTML boilerplate, and split into 512-token chunks. We also deploy circuit breakers.

**Pitfall:** Ignoring web retrieval bottlenecks.
**Impact:** We index billions of web pages. This requires a distributed search engine like Elasticsearch or a specialized vector database like Milvus or Pinecone. This causes cascading failures.
**Mitigation:** Each chunk is embedded using a model like text-embedding-3-small or a fine-tuned BGE model. We also deploy circuit breakers.

**Pitfall:** Ignoring web retrieval bottlenecks.
**Impact:** Document chunking is crucial. Web pages are parsed, cleaned of HTML boilerplate, and split into 512-token chunks. This causes cascading failures.
**Mitigation:** To handle the massive scale, we use Approximate Nearest Neighbor (ANN) algorithms like HNSW (Hierarchical Navigable Small World) for vector search. We also deploy circuit breakers.

**Pitfall:** Ignoring web retrieval bottlenecks.
**Impact:** Each chunk is embedded using a model like text-embedding-3-small or a fine-tuned BGE model. This causes cascading failures.
**Mitigation:** Retrieval latency is a major bottleneck. We aggressively cache retrieval results for popular queries using Memcached. We also deploy circuit breakers.

**Pitfall:** Ignoring web retrieval bottlenecks.
**Impact:** To handle the massive scale, we use Approximate Nearest Neighbor (ANN) algorithms like HNSW (Hierarchical Navigable Small World) for vector search. This causes cascading failures.
**Mitigation:** Freshness is critical for news queries. We maintain a separate, smaller 'real-time' index that is updated continuously, bypassing the slower batch processing pipeline. We also deploy circuit breakers.

**Pitfall:** Ignoring web retrieval bottlenecks.
**Impact:** Retrieval latency is a major bottleneck. We aggressively cache retrieval results for popular queries using Memcached. This causes cascading failures.
**Mitigation:** The web retrieval component is responsible for finding the most relevant documents for each sub-query. We also deploy circuit breakers.

**Pitfall:** Ignoring web retrieval bottlenecks.
**Impact:** Freshness is critical for news queries. We maintain a separate, smaller 'real-time' index that is updated continuously, bypassing the slower batch processing pipeline. This causes cascading failures.
**Mitigation:** We use a hybrid search approach, combining sparse retrieval (BM25) and dense retrieval (vector embeddings). We also deploy circuit breakers.

### Deep Dive: Reranking

**Pitfall:** Ignoring reranking bottlenecks.
**Impact:** The initial retrieval phase might return 100s of documents per sub-query. Reranking identifies the top 5-10 most relevant ones for the generator. This causes cascading failures.
**Mitigation:** Cross-encoders are computationally expensive. To meet our <100ms latency budget, we use a relatively small model (e.g., 200M parameters) or deploy on GPUs with TensorRT. We also deploy circuit breakers.

**Pitfall:** Ignoring reranking bottlenecks.
**Impact:** A cross-encoder model (e.g., a fine-tuned DeBERTa) is typically used for reranking. It takes the query and document chunk as a pair and scores their relevance. This causes cascading failures.
**Mitigation:** We can also use LLM-as-a-judge for reranking (e.g., RankLLaMA), but this is usually too slow for real-time consumer search and is reserved for offline evaluation. We also deploy circuit breakers.

**Pitfall:** Ignoring reranking bottlenecks.
**Impact:** Cross-encoders are computationally expensive. To meet our <100ms latency budget, we use a relatively small model (e.g., 200M parameters) or deploy on GPUs with TensorRT. This causes cascading failures.
**Mitigation:** The reranker considers multiple signals: semantic relevance, document freshness (critical for news), domain authority (favoring reputable sites), and user engagement metrics. We also deploy circuit breakers.

**Pitfall:** Ignoring reranking bottlenecks.
**Impact:** We can also use LLM-as-a-judge for reranking (e.g., RankLLaMA), but this is usually too slow for real-time consumer search and is reserved for offline evaluation. This causes cascading failures.
**Mitigation:** Documents are often grouped by domain to ensure source diversity. We don't want all 10 citations coming from the same website. We also deploy circuit breakers.

**Pitfall:** Ignoring reranking bottlenecks.
**Impact:** The reranker considers multiple signals: semantic relevance, document freshness (critical for news), domain authority (favoring reputable sites), and user engagement metrics. This causes cascading failures.
**Mitigation:** Reranking helps mitigate the 'lost in the middle' phenomenon of LLMs by ensuring the absolute best information is placed at the beginning or end of the context window. We also deploy circuit breakers.

**Pitfall:** Ignoring reranking bottlenecks.
**Impact:** Documents are often grouped by domain to ensure source diversity. We don't want all 10 citations coming from the same website. This causes cascading failures.
**Mitigation:** We truncate the list of reranked documents dynamically based on a confidence threshold to save tokens in the generation phase. We also deploy circuit breakers.

**Pitfall:** Ignoring reranking bottlenecks.
**Impact:** Reranking helps mitigate the 'lost in the middle' phenomenon of LLMs by ensuring the absolute best information is placed at the beginning or end of the context window. This causes cascading failures.
**Mitigation:** For long queries, we might use ColBERT, a late-interaction model, which offers a good balance between the speed of bi-encoders and the accuracy of cross-encoders. We also deploy circuit breakers.

**Pitfall:** Ignoring reranking bottlenecks.
**Impact:** We truncate the list of reranked documents dynamically based on a confidence threshold to save tokens in the generation phase. This causes cascading failures.
**Mitigation:** We must handle duplicate or near-duplicate documents retrieved from different sources. The reranker includes a deduplication step based on content hashing or embedding similarity. We also deploy circuit breakers.

**Pitfall:** Ignoring reranking bottlenecks.
**Impact:** For long queries, we might use ColBERT, a late-interaction model, which offers a good balance between the speed of bi-encoders and the accuracy of cross-encoders. This causes cascading failures.
**Mitigation:** The initial retrieval phase might return 100s of documents per sub-query. Reranking identifies the top 5-10 most relevant ones for the generator. We also deploy circuit breakers.

**Pitfall:** Ignoring reranking bottlenecks.
**Impact:** We must handle duplicate or near-duplicate documents retrieved from different sources. The reranker includes a deduplication step based on content hashing or embedding similarity. This causes cascading failures.
**Mitigation:** A cross-encoder model (e.g., a fine-tuned DeBERTa) is typically used for reranking. It takes the query and document chunk as a pair and scores their relevance. We also deploy circuit breakers.

### Deep Dive: Grounded Generation with Citations

**Pitfall:** Ignoring grounded generation with citations bottlenecks.
**Impact:** The generator (e.g., GPT-4o or a fine-tuned Llama 3 70B) synthesizes the final answer using the retrieved and reranked documents. This causes cascading failures.
**Mitigation:** This 'grounding' significantly reduces hallucinations, as the model's generation is constrained by empirical evidence. We also deploy circuit breakers.

**Pitfall:** Ignoring grounded generation with citations bottlenecks.
**Impact:** The prompt instructs the model to answer the query *only* using the provided context and to cite its sources using a specific format (e.g., [1], [2]). This causes cascading failures.
**Mitigation:** However, hallucinations can still occur if the model misinterprets the context or combines information incorrectly. This requires rigorous evaluation. We also deploy circuit breakers.

**Pitfall:** Ignoring grounded generation with citations bottlenecks.
**Impact:** This 'grounding' significantly reduces hallucinations, as the model's generation is constrained by empirical evidence. This causes cascading failures.
**Mitigation:** To enforce citation accuracy, we can use a post-processing verification step. A smaller model checks if the generated sentence is actually supported by the cited document. We also deploy circuit breakers.

**Pitfall:** Ignoring grounded generation with citations bottlenecks.
**Impact:** However, hallucinations can still occur if the model misinterprets the context or combines information incorrectly. This requires rigorous evaluation. This causes cascading failures.
**Mitigation:** If a citation is invalid, the system can attempt to fix it or strip the sentence entirely. We also deploy circuit breakers.

**Pitfall:** Ignoring grounded generation with citations bottlenecks.
**Impact:** To enforce citation accuracy, we can use a post-processing verification step. A smaller model checks if the generated sentence is actually supported by the cited document. This causes cascading failures.
**Mitigation:** The prompt must also instruct the model to handle contradictory information. If Source A says X and Source B says Y, the model should explain the discrepancy. We also deploy circuit breakers.

**Pitfall:** Ignoring grounded generation with citations bottlenecks.
**Impact:** If a citation is invalid, the system can attempt to fix it or strip the sentence entirely. This causes cascading failures.
**Mitigation:** Context window management is crucial. We must ensure the query, system prompt, and all retrieved chunks fit within the model's limit (e.g., 32k or 128k tokens). We also deploy circuit breakers.

**Pitfall:** Ignoring grounded generation with citations bottlenecks.
**Impact:** The prompt must also instruct the model to handle contradictory information. If Source A says X and Source B says Y, the model should explain the discrepancy. This causes cascading failures.
**Mitigation:** We prioritize chunks based on their reranker score when packing the context window. We also deploy circuit breakers.

**Pitfall:** Ignoring grounded generation with citations bottlenecks.
**Impact:** Context window management is crucial. We must ensure the query, system prompt, and all retrieved chunks fit within the model's limit (e.g., 32k or 128k tokens). This causes cascading failures.
**Mitigation:** The generated response must be formatted in Markdown, seamlessly integrating the inline citations which are then rendered as clickable links in the frontend. We also deploy circuit breakers.

**Pitfall:** Ignoring grounded generation with citations bottlenecks.
**Impact:** We prioritize chunks based on their reranker score when packing the context window. This causes cascading failures.
**Mitigation:** The generator (e.g., GPT-4o or a fine-tuned Llama 3 70B) synthesizes the final answer using the retrieved and reranked documents. We also deploy circuit breakers.

**Pitfall:** Ignoring grounded generation with citations bottlenecks.
**Impact:** The generated response must be formatted in Markdown, seamlessly integrating the inline citations which are then rendered as clickable links in the frontend. This causes cascading failures.
**Mitigation:** The prompt instructs the model to answer the query *only* using the provided context and to cite its sources using a specific format (e.g., [1], [2]). We also deploy circuit breakers.

### Deep Dive: Streaming

**Pitfall:** Ignoring streaming bottlenecks.
**Impact:** Streaming is non-negotiable for AI search. Users will not wait 5-10 seconds for a full answer to generate. This causes cascading failures.
**Mitigation:** Time-To-First-Token (TTFT) is our primary latency metric. It includes the time for decomposition, retrieval, reranking, and the initial LLM forward pass. We also deploy circuit breakers.

**Pitfall:** Ignoring streaming bottlenecks.
**Impact:** We use Server-Sent Events (SSE) or WebSockets to stream the response token-by-token from the LLM to the client. This causes cascading failures.
**Mitigation:** We aim for a TTFT of under 1 second. This requires aggressive optimization of the pre-generation pipeline. We also deploy circuit breakers.

**Pitfall:** Ignoring streaming bottlenecks.
**Impact:** Time-To-First-Token (TTFT) is our primary latency metric. It includes the time for decomposition, retrieval, reranking, and the initial LLM forward pass. This causes cascading failures.
**Mitigation:** Streaming citations presents a UI challenge. The citation number (e.g., [1]) might be generated before the actual source URL is fully resolved or mapped in the frontend. We also deploy circuit breakers.

**Pitfall:** Ignoring streaming bottlenecks.
**Impact:** We aim for a TTFT of under 1 second. This requires aggressive optimization of the pre-generation pipeline. This causes cascading failures.
**Mitigation:** We send the list of sources as a separate JSON payload *before* starting the text stream, so the frontend can immediately render the citation links as they arrive. We also deploy circuit breakers.

**Pitfall:** Ignoring streaming bottlenecks.
**Impact:** Streaming citations presents a UI challenge. The citation number (e.g., [1]) might be generated before the actual source URL is fully resolved or mapped in the frontend. This causes cascading failures.
**Mitigation:** If the generator model supports speculative decoding, we can significantly increase the streaming token rate (tokens per second). We also deploy circuit breakers.

**Pitfall:** Ignoring streaming bottlenecks.
**Impact:** We send the list of sources as a separate JSON payload *before* starting the text stream, so the frontend can immediately render the citation links as they arrive. This causes cascading failures.
**Mitigation:** Connection drops during streaming must be handled gracefully. The client should be able to resume or retry the generation. We also deploy circuit breakers.

**Pitfall:** Ignoring streaming bottlenecks.
**Impact:** If the generator model supports speculative decoding, we can significantly increase the streaming token rate (tokens per second). This causes cascading failures.
**Mitigation:** We must ensure that the safety filters (checking for toxicity or PII) operate effectively on streamed tokens, often using a sliding window approach. We also deploy circuit breakers.

**Pitfall:** Ignoring streaming bottlenecks.
**Impact:** Connection drops during streaming must be handled gracefully. The client should be able to resume or retry the generation. This causes cascading failures.
**Mitigation:** Load balancing for streaming connections is stateful. We use consistent hashing or specific routing rules to keep the connection pinned to the correct inference server. We also deploy circuit breakers.

**Pitfall:** Ignoring streaming bottlenecks.
**Impact:** We must ensure that the safety filters (checking for toxicity or PII) operate effectively on streamed tokens, often using a sliding window approach. This causes cascading failures.
**Mitigation:** Streaming is non-negotiable for AI search. Users will not wait 5-10 seconds for a full answer to generate. We also deploy circuit breakers.

**Pitfall:** Ignoring streaming bottlenecks.
**Impact:** Load balancing for streaming connections is stateful. We use consistent hashing or specific routing rules to keep the connection pinned to the correct inference server. This causes cascading failures.
**Mitigation:** We use Server-Sent Events (SSE) or WebSockets to stream the response token-by-token from the LLM to the client. We also deploy circuit breakers.

### Deep Dive: Caching

**Pitfall:** Ignoring caching bottlenecks.
**Impact:** Caching occurs at multiple layers: exact query match, sub-query retrieval, and semantic similarity. This causes cascading failures.
**Mitigation:** This cache must have a short TTL (e.g., 1 hour) for queries related to news or real-time events, but can be longer for evergreen queries (e.g., 'history of Rome'). We also deploy circuit breakers.

**Pitfall:** Ignoring caching bottlenecks.
**Impact:** Exact Query Cache (Redis): If a user asks exactly the same question as a recent query, we return the cached final response instantly (TTFT < 50ms). This causes cascading failures.
**Mitigation:** Sub-query Cache: We cache the retrieval and reranking results for common sub-queries. 'What is the population of Paris?' is useful across many complex queries. We also deploy circuit breakers.

**Pitfall:** Ignoring caching bottlenecks.
**Impact:** This cache must have a short TTL (e.g., 1 hour) for queries related to news or real-time events, but can be longer for evergreen queries (e.g., 'history of Rome'). This causes cascading failures.
**Mitigation:** Semantic Cache (Vector DB): We can use a fast vector search on incoming queries against recently answered queries. If the semantic similarity is >0.95, we reuse the answer. We also deploy circuit breakers.

**Pitfall:** Ignoring caching bottlenecks.
**Impact:** Sub-query Cache: We cache the retrieval and reranking results for common sub-queries. 'What is the population of Paris?' is useful across many complex queries. This causes cascading failures.
**Mitigation:** Semantic caching is risky. 'How to fix a flat tire on a bike' and 'How to fix a flat tire on a car' are semantically similar but require vastly different answers. We also deploy circuit breakers.

**Pitfall:** Ignoring caching bottlenecks.
**Impact:** Semantic Cache (Vector DB): We can use a fast vector search on incoming queries against recently answered queries. If the semantic similarity is >0.95, we reuse the answer. This causes cascading failures.
**Mitigation:** We use a fast verification model to double-check semantic cache hits before serving them to the user. We also deploy circuit breakers.

**Pitfall:** Ignoring caching bottlenecks.
**Impact:** Semantic caching is risky. 'How to fix a flat tire on a bike' and 'How to fix a flat tire on a car' are semantically similar but require vastly different answers. This causes cascading failures.
**Mitigation:** Cache invalidation is tricky. When a major news event breaks, we must proactively invalidate caches related to that topic. We also deploy circuit breakers.

**Pitfall:** Ignoring caching bottlenecks.
**Impact:** We use a fast verification model to double-check semantic cache hits before serving them to the user. This causes cascading failures.
**Mitigation:** We use edge caching (CDN) for static assets, but the dynamic AI search responses are cached at the application layer in the data center. We also deploy circuit breakers.

**Pitfall:** Ignoring caching bottlenecks.
**Impact:** Cache invalidation is tricky. When a major news event breaks, we must proactively invalidate caches related to that topic. This causes cascading failures.
**Mitigation:** The caching strategy dramatically reduces API costs (OpenAI/Anthropic) and compute requirements for self-hosted models. We also deploy circuit breakers.

**Pitfall:** Ignoring caching bottlenecks.
**Impact:** We use edge caching (CDN) for static assets, but the dynamic AI search responses are cached at the application layer in the data center. This causes cascading failures.
**Mitigation:** Caching occurs at multiple layers: exact query match, sub-query retrieval, and semantic similarity. We also deploy circuit breakers.

**Pitfall:** Ignoring caching bottlenecks.
**Impact:** The caching strategy dramatically reduces API costs (OpenAI/Anthropic) and compute requirements for self-hosted models. This causes cascading failures.
**Mitigation:** Exact Query Cache (Redis): If a user asks exactly the same question as a recent query, we return the cached final response instantly (TTFT < 50ms). We also deploy circuit breakers.

### Deep Dive: Freshness and Cost

**Pitfall:** Ignoring freshness and cost bottlenecks.
**Impact:** Freshness is the defining feature of AI search compared to static knowledge bases. This causes cascading failures.
**Mitigation:** We use an incremental indexing strategy. New documents are added to a fast-update memory-mapped index before being merged into the main disk-based index. We also deploy circuit breakers.

**Pitfall:** Ignoring freshness and cost bottlenecks.
**Impact:** Our crawler pipeline constantly monitors RSS feeds, news sites, and social media for new content. This causes cascading failures.
**Mitigation:** Cost management is a primary architectural driver. A single AI search query can cost 10x to 100x more than a traditional keyword search. We also deploy circuit breakers.

**Pitfall:** Ignoring freshness and cost bottlenecks.
**Impact:** We use an incremental indexing strategy. New documents are added to a fast-update memory-mapped index before being merged into the main disk-based index. This causes cascading failures.
**Mitigation:** We employ a cascade of models. Simple queries might be handled entirely by an 8B parameter model, while complex reasoning requires a 70B or proprietary model. We also deploy circuit breakers.

**Pitfall:** Ignoring freshness and cost bottlenecks.
**Impact:** Cost management is a primary architectural driver. A single AI search query can cost 10x to 100x more than a traditional keyword search. This causes cascading failures.
**Mitigation:** We dynamically adjust the number of retrieved documents based on the query complexity. Simple queries get 3 docs; complex ones get 20. This saves tokens. We also deploy circuit breakers.

**Pitfall:** Ignoring freshness and cost bottlenecks.
**Impact:** We employ a cascade of models. Simple queries might be handled entirely by an 8B parameter model, while complex reasoning requires a 70B or proprietary model. This causes cascading failures.
**Mitigation:** Context caching (if supported by the LLM provider, like Anthropic's prompt caching) is used extensively for the system prompt and common instructions. We also deploy circuit breakers.

**Pitfall:** Ignoring freshness and cost bottlenecks.
**Impact:** We dynamically adjust the number of retrieved documents based on the query complexity. Simple queries get 3 docs; complex ones get 20. This saves tokens. This causes cascading failures.
**Mitigation:** We track the cost per query and aggregate it by user and tenant. This data is fed into our billing system and alerting pipelines. We also deploy circuit breakers.

**Pitfall:** Ignoring freshness and cost bottlenecks.
**Impact:** Context caching (if supported by the LLM provider, like Anthropic's prompt caching) is used extensively for the system prompt and common instructions. This causes cascading failures.
**Mitigation:** To handle spikes in traffic without breaking the bank, we implement dynamic rate limiting and graceful degradation (e.g., disabling the most expensive reasoning steps under high load). We also deploy circuit breakers.

**Pitfall:** Ignoring freshness and cost bottlenecks.
**Impact:** We track the cost per query and aggregate it by user and tenant. This data is fed into our billing system and alerting pipelines. This causes cascading failures.
**Mitigation:** We heavily utilize spot instances for offline batch processing and evaluation to reduce cloud compute costs. We also deploy circuit breakers.

**Pitfall:** Ignoring freshness and cost bottlenecks.
**Impact:** To handle spikes in traffic without breaking the bank, we implement dynamic rate limiting and graceful degradation (e.g., disabling the most expensive reasoning steps under high load). This causes cascading failures.
**Mitigation:** Freshness is the defining feature of AI search compared to static knowledge bases. We also deploy circuit breakers.

**Pitfall:** Ignoring freshness and cost bottlenecks.
**Impact:** We heavily utilize spot instances for offline batch processing and evaluation to reduce cloud compute costs. This causes cascading failures.
**Mitigation:** Our crawler pipeline constantly monitors RSS feeds, news sites, and social media for new content. We also deploy circuit breakers.

### Deep Dive: Evaluation

**Pitfall:** Ignoring evaluation bottlenecks.
**Impact:** Evaluating AI search requires a multi-faceted approach, moving beyond simple accuracy metrics. This causes cascading failures.
**Mitigation:** Context Relevance checks if the retrieved documents actually contain the answer to the query. We also deploy circuit breakers.

**Pitfall:** Ignoring evaluation bottlenecks.
**Impact:** We use the RAG Triad for automated evaluation: Context Relevance, Answer Relevance, and Groundedness. This causes cascading failures.
**Mitigation:** Answer Relevance ensures the final generated text directly addresses the user's question, without going off on tangents. We also deploy circuit breakers.

**Pitfall:** Ignoring evaluation bottlenecks.
**Impact:** Context Relevance checks if the retrieved documents actually contain the answer to the query. This causes cascading failures.
**Mitigation:** Groundedness is paramount. We measure the hallucination rate by checking if every claim in the generated answer is supported by a citation. We also deploy circuit breakers.

**Pitfall:** Ignoring evaluation bottlenecks.
**Impact:** Answer Relevance ensures the final generated text directly addresses the user's question, without going off on tangents. This causes cascading failures.
**Mitigation:** We employ 'LLM-as-a-judge' pipelines running continuously on a sample of production traffic. GPT-4 evaluates the outputs of our production models. We also deploy circuit breakers.

**Pitfall:** Ignoring evaluation bottlenecks.
**Impact:** Groundedness is paramount. We measure the hallucination rate by checking if every claim in the generated answer is supported by a citation. This causes cascading failures.
**Mitigation:** Human evaluation remains essential. We have a team of domain experts who grade responses based on a detailed rubric (accuracy, tone, helpfulness). We also deploy circuit breakers.

**Pitfall:** Ignoring evaluation bottlenecks.
**Impact:** We employ 'LLM-as-a-judge' pipelines running continuously on a sample of production traffic. GPT-4 evaluates the outputs of our production models. This causes cascading failures.
**Mitigation:** A/B testing is used for every change. We route 5% of traffic to a new reranker model and compare engagement metrics (session length, follow-up queries, explicit thumbs up/down). We also deploy circuit breakers.

**Pitfall:** Ignoring evaluation bottlenecks.
**Impact:** Human evaluation remains essential. We have a team of domain experts who grade responses based on a detailed rubric (accuracy, tone, helpfulness). This causes cascading failures.
**Mitigation:** We specifically test for adversarial inputs and jailbreak attempts to ensure our safety filters are robust. We also deploy circuit breakers.

**Pitfall:** Ignoring evaluation bottlenecks.
**Impact:** A/B testing is used for every change. We route 5% of traffic to a new reranker model and compare engagement metrics (session length, follow-up queries, explicit thumbs up/down). This causes cascading failures.
**Mitigation:** Latency and cost metrics are tracked alongside quality metrics. A model that is 2% more accurate but 5x slower and 10x more expensive might not be deployed. We also deploy circuit breakers.

**Pitfall:** Ignoring evaluation bottlenecks.
**Impact:** We specifically test for adversarial inputs and jailbreak attempts to ensure our safety filters are robust. This causes cascading failures.
**Mitigation:** Evaluating AI search requires a multi-faceted approach, moving beyond simple accuracy metrics. We also deploy circuit breakers.

**Pitfall:** Ignoring evaluation bottlenecks.
**Impact:** Latency and cost metrics are tracked alongside quality metrics. A model that is 2% more accurate but 5x slower and 10x more expensive might not be deployed. This causes cascading failures.
**Mitigation:** We use the RAG Triad for automated evaluation: Context Relevance, Answer Relevance, and Groundedness. We also deploy circuit breakers.

### Deep Dive: Query Decomposition

**Pitfall:** Ignoring query decomposition bottlenecks.
**Impact:** User queries in AI search are often complex and multi-faceted. The query decomposition module breaks these down into simpler, atomic sub-queries that can be executed independently against the search index. This causes cascading failures.
**Mitigation:** We use a lightweight LLM (e.g., Llama 3 8B) for decomposition to minimize latency. The prompt instructs the model to output a JSON array of sub-queries. We also deploy circuit breakers.

**Pitfall:** Ignoring query decomposition bottlenecks.
**Impact:** For example, a query like 'What is the capital of France and its population?' is split into 'What is the capital of France?' and 'What is the population of the capital of France?'. This improves retrieval recall. This causes cascading failures.
**Mitigation:** Decomposition must handle temporal constraints. 'Who won the World Series last year?' needs entity resolution for 'last year' based on the current timestamp. We also deploy circuit breakers.

**Pitfall:** Ignoring query decomposition bottlenecks.
**Impact:** We use a lightweight LLM (e.g., Llama 3 8B) for decomposition to minimize latency. The prompt instructs the model to output a JSON array of sub-queries. This causes cascading failures.
**Mitigation:** A critical trade-off is latency vs. recall. More sub-queries mean better recall but higher retrieval latency and more tokens sent to the final generation model. We also deploy circuit breakers.

**Pitfall:** Ignoring query decomposition bottlenecks.
**Impact:** Decomposition must handle temporal constraints. 'Who won the World Series last year?' needs entity resolution for 'last year' based on the current timestamp. This causes cascading failures.
**Mitigation:** To mitigate latency, sub-queries are executed concurrently in a scatter-gather pattern. We also deploy circuit breakers.

**Pitfall:** Ignoring query decomposition bottlenecks.
**Impact:** A critical trade-off is latency vs. recall. More sub-queries mean better recall but higher retrieval latency and more tokens sent to the final generation model. This causes cascading failures.
**Mitigation:** Query rewriting is also performed here. Typos are corrected, and synonyms are expanded. 'nyc pop' becomes 'New York City population'. We also deploy circuit breakers.

**Pitfall:** Ignoring query decomposition bottlenecks.
**Impact:** To mitigate latency, sub-queries are executed concurrently in a scatter-gather pattern. This causes cascading failures.
**Mitigation:** We maintain a cache of common query decompositions using Redis. If a query matches perfectly, we bypass the LLM. We also deploy circuit breakers.

**Pitfall:** Ignoring query decomposition bottlenecks.
**Impact:** Query rewriting is also performed here. Typos are corrected, and synonyms are expanded. 'nyc pop' becomes 'New York City population'. This causes cascading failures.
**Mitigation:** Some queries don't need decomposition (e.g., 'weather in Tokyo'). A fast classifier (e.g., a small BERT model or prompt routing) decides if decomposition is necessary. We also deploy circuit breakers.

**Pitfall:** Ignoring query decomposition bottlenecks.
**Impact:** We maintain a cache of common query decompositions using Redis. If a query matches perfectly, we bypass the LLM. This causes cascading failures.
**Mitigation:** The system sets a hard limit (e.g., max 5 sub-queries) to bound downstream computational costs. We also deploy circuit breakers.

**Pitfall:** Ignoring query decomposition bottlenecks.
**Impact:** Some queries don't need decomposition (e.g., 'weather in Tokyo'). A fast classifier (e.g., a small BERT model or prompt routing) decides if decomposition is necessary. This causes cascading failures.
**Mitigation:** User queries in AI search are often complex and multi-faceted. The query decomposition module breaks these down into simpler, atomic sub-queries that can be executed independently against the search index. We also deploy circuit breakers.

**Pitfall:** Ignoring query decomposition bottlenecks.
**Impact:** The system sets a hard limit (e.g., max 5 sub-queries) to bound downstream computational costs. This causes cascading failures.
**Mitigation:** For example, a query like 'What is the capital of France and its population?' is split into 'What is the capital of France?' and 'What is the population of the capital of France?'. This improves retrieval recall. We also deploy circuit breakers.

### Deep Dive: Web Retrieval

**Pitfall:** Ignoring web retrieval bottlenecks.
**Impact:** The web retrieval component is responsible for finding the most relevant documents for each sub-query. This causes cascading failures.
**Mitigation:** BM25 is excellent for exact keyword matches, such as specific product names or error codes, which embeddings might struggle with. We also deploy circuit breakers.

**Pitfall:** Ignoring web retrieval bottlenecks.
**Impact:** We use a hybrid search approach, combining sparse retrieval (BM25) and dense retrieval (vector embeddings). This causes cascading failures.
**Mitigation:** Dense retrieval captures semantic meaning, allowing us to find relevant documents even if the exact keywords are missing. We also deploy circuit breakers.

**Pitfall:** Ignoring web retrieval bottlenecks.
**Impact:** BM25 is excellent for exact keyword matches, such as specific product names or error codes, which embeddings might struggle with. This causes cascading failures.
**Mitigation:** We index billions of web pages. This requires a distributed search engine like Elasticsearch or a specialized vector database like Milvus or Pinecone. We also deploy circuit breakers.

**Pitfall:** Ignoring web retrieval bottlenecks.
**Impact:** Dense retrieval captures semantic meaning, allowing us to find relevant documents even if the exact keywords are missing. This causes cascading failures.
**Mitigation:** Document chunking is crucial. Web pages are parsed, cleaned of HTML boilerplate, and split into 512-token chunks. We also deploy circuit breakers.

**Pitfall:** Ignoring web retrieval bottlenecks.
**Impact:** We index billions of web pages. This requires a distributed search engine like Elasticsearch or a specialized vector database like Milvus or Pinecone. This causes cascading failures.
**Mitigation:** Each chunk is embedded using a model like text-embedding-3-small or a fine-tuned BGE model. We also deploy circuit breakers.

**Pitfall:** Ignoring web retrieval bottlenecks.
**Impact:** Document chunking is crucial. Web pages are parsed, cleaned of HTML boilerplate, and split into 512-token chunks. This causes cascading failures.
**Mitigation:** To handle the massive scale, we use Approximate Nearest Neighbor (ANN) algorithms like HNSW (Hierarchical Navigable Small World) for vector search. We also deploy circuit breakers.

**Pitfall:** Ignoring web retrieval bottlenecks.
**Impact:** Each chunk is embedded using a model like text-embedding-3-small or a fine-tuned BGE model. This causes cascading failures.
**Mitigation:** Retrieval latency is a major bottleneck. We aggressively cache retrieval results for popular queries using Memcached. We also deploy circuit breakers.

**Pitfall:** Ignoring web retrieval bottlenecks.
**Impact:** To handle the massive scale, we use Approximate Nearest Neighbor (ANN) algorithms like HNSW (Hierarchical Navigable Small World) for vector search. This causes cascading failures.
**Mitigation:** Freshness is critical for news queries. We maintain a separate, smaller 'real-time' index that is updated continuously, bypassing the slower batch processing pipeline. We also deploy circuit breakers.

**Pitfall:** Ignoring web retrieval bottlenecks.
**Impact:** Retrieval latency is a major bottleneck. We aggressively cache retrieval results for popular queries using Memcached. This causes cascading failures.
**Mitigation:** The web retrieval component is responsible for finding the most relevant documents for each sub-query. We also deploy circuit breakers.

**Pitfall:** Ignoring web retrieval bottlenecks.
**Impact:** Freshness is critical for news queries. We maintain a separate, smaller 'real-time' index that is updated continuously, bypassing the slower batch processing pipeline. This causes cascading failures.
**Mitigation:** We use a hybrid search approach, combining sparse retrieval (BM25) and dense retrieval (vector embeddings). We also deploy circuit breakers.

### Deep Dive: Reranking

**Pitfall:** Ignoring reranking bottlenecks.
**Impact:** The initial retrieval phase might return 100s of documents per sub-query. Reranking identifies the top 5-10 most relevant ones for the generator. This causes cascading failures.
**Mitigation:** Cross-encoders are computationally expensive. To meet our <100ms latency budget, we use a relatively small model (e.g., 200M parameters) or deploy on GPUs with TensorRT. We also deploy circuit breakers.

