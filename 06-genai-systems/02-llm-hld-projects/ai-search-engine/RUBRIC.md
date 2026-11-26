# RUBRIC for AI Search Engine (Perplexity-style)

This document provides substantive, problem-specific design guidance for building a multi-tenant AI search engine.

### Deep Dive: Query Decomposition

- **Criteria:** Candidate designs robust query decomposition.
  - *Excellent (5/5):* Mentions User queries in AI search are often complex and multi-faceted. The query decomposition module breaks these down into simpler, atomic sub-queries that can be executed independently against the search index.
  - *Adequate (3/5):* Uses basic implementation.
  - *Poor (1/5):* Ignores query decomposition entirely.

- **Criteria:** Candidate designs robust query decomposition.
  - *Excellent (5/5):* Mentions For example, a query like 'What is the capital of France and its population?' is split into 'What is the capital of France?' and 'What is the population of the capital of France?'. This improves retrieval recall.
  - *Adequate (3/5):* Uses basic implementation.
  - *Poor (1/5):* Ignores query decomposition entirely.

- **Criteria:** Candidate designs robust query decomposition.
  - *Excellent (5/5):* Mentions We use a lightweight LLM (e.g., Llama 3 8B) for decomposition to minimize latency. The prompt instructs the model to output a JSON array of sub-queries.
  - *Adequate (3/5):* Uses basic implementation.
  - *Poor (1/5):* Ignores query decomposition entirely.

- **Criteria:** Candidate designs robust query decomposition.
  - *Excellent (5/5):* Mentions Decomposition must handle temporal constraints. 'Who won the World Series last year?' needs entity resolution for 'last year' based on the current timestamp.
  - *Adequate (3/5):* Uses basic implementation.
  - *Poor (1/5):* Ignores query decomposition entirely.

- **Criteria:** Candidate designs robust query decomposition.
  - *Excellent (5/5):* Mentions A critical trade-off is latency vs. recall. More sub-queries mean better recall but higher retrieval latency and more tokens sent to the final generation model.
  - *Adequate (3/5):* Uses basic implementation.
  - *Poor (1/5):* Ignores query decomposition entirely.

- **Criteria:** Candidate designs robust query decomposition.
  - *Excellent (5/5):* Mentions To mitigate latency, sub-queries are executed concurrently in a scatter-gather pattern.
  - *Adequate (3/5):* Uses basic implementation.
  - *Poor (1/5):* Ignores query decomposition entirely.

- **Criteria:** Candidate designs robust query decomposition.
  - *Excellent (5/5):* Mentions Query rewriting is also performed here. Typos are corrected, and synonyms are expanded. 'nyc pop' becomes 'New York City population'.
  - *Adequate (3/5):* Uses basic implementation.
  - *Poor (1/5):* Ignores query decomposition entirely.

- **Criteria:** Candidate designs robust query decomposition.
  - *Excellent (5/5):* Mentions We maintain a cache of common query decompositions using Redis. If a query matches perfectly, we bypass the LLM.
  - *Adequate (3/5):* Uses basic implementation.
  - *Poor (1/5):* Ignores query decomposition entirely.

- **Criteria:** Candidate designs robust query decomposition.
  - *Excellent (5/5):* Mentions Some queries don't need decomposition (e.g., 'weather in Tokyo'). A fast classifier (e.g., a small BERT model or prompt routing) decides if decomposition is necessary.
  - *Adequate (3/5):* Uses basic implementation.
  - *Poor (1/5):* Ignores query decomposition entirely.

- **Criteria:** Candidate designs robust query decomposition.
  - *Excellent (5/5):* Mentions The system sets a hard limit (e.g., max 5 sub-queries) to bound downstream computational costs.
  - *Adequate (3/5):* Uses basic implementation.
  - *Poor (1/5):* Ignores query decomposition entirely.

### Deep Dive: Web Retrieval

- **Criteria:** Candidate designs robust web retrieval.
  - *Excellent (5/5):* Mentions The web retrieval component is responsible for finding the most relevant documents for each sub-query.
  - *Adequate (3/5):* Uses basic implementation.
  - *Poor (1/5):* Ignores web retrieval entirely.

- **Criteria:** Candidate designs robust web retrieval.
  - *Excellent (5/5):* Mentions We use a hybrid search approach, combining sparse retrieval (BM25) and dense retrieval (vector embeddings).
  - *Adequate (3/5):* Uses basic implementation.
  - *Poor (1/5):* Ignores web retrieval entirely.

- **Criteria:** Candidate designs robust web retrieval.
  - *Excellent (5/5):* Mentions BM25 is excellent for exact keyword matches, such as specific product names or error codes, which embeddings might struggle with.
  - *Adequate (3/5):* Uses basic implementation.
  - *Poor (1/5):* Ignores web retrieval entirely.

- **Criteria:** Candidate designs robust web retrieval.
  - *Excellent (5/5):* Mentions Dense retrieval captures semantic meaning, allowing us to find relevant documents even if the exact keywords are missing.
  - *Adequate (3/5):* Uses basic implementation.
  - *Poor (1/5):* Ignores web retrieval entirely.

- **Criteria:** Candidate designs robust web retrieval.
  - *Excellent (5/5):* Mentions We index billions of web pages. This requires a distributed search engine like Elasticsearch or a specialized vector database like Milvus or Pinecone.
  - *Adequate (3/5):* Uses basic implementation.
  - *Poor (1/5):* Ignores web retrieval entirely.

- **Criteria:** Candidate designs robust web retrieval.
  - *Excellent (5/5):* Mentions Document chunking is crucial. Web pages are parsed, cleaned of HTML boilerplate, and split into 512-token chunks.
  - *Adequate (3/5):* Uses basic implementation.
  - *Poor (1/5):* Ignores web retrieval entirely.

- **Criteria:** Candidate designs robust web retrieval.
  - *Excellent (5/5):* Mentions Each chunk is embedded using a model like text-embedding-3-small or a fine-tuned BGE model.
  - *Adequate (3/5):* Uses basic implementation.
  - *Poor (1/5):* Ignores web retrieval entirely.

- **Criteria:** Candidate designs robust web retrieval.
  - *Excellent (5/5):* Mentions To handle the massive scale, we use Approximate Nearest Neighbor (ANN) algorithms like HNSW (Hierarchical Navigable Small World) for vector search.
  - *Adequate (3/5):* Uses basic implementation.
  - *Poor (1/5):* Ignores web retrieval entirely.

- **Criteria:** Candidate designs robust web retrieval.
  - *Excellent (5/5):* Mentions Retrieval latency is a major bottleneck. We aggressively cache retrieval results for popular queries using Memcached.
  - *Adequate (3/5):* Uses basic implementation.
  - *Poor (1/5):* Ignores web retrieval entirely.

- **Criteria:** Candidate designs robust web retrieval.
  - *Excellent (5/5):* Mentions Freshness is critical for news queries. We maintain a separate, smaller 'real-time' index that is updated continuously, bypassing the slower batch processing pipeline.
  - *Adequate (3/5):* Uses basic implementation.
  - *Poor (1/5):* Ignores web retrieval entirely.

### Deep Dive: Reranking

- **Criteria:** Candidate designs robust reranking.
  - *Excellent (5/5):* Mentions The initial retrieval phase might return 100s of documents per sub-query. Reranking identifies the top 5-10 most relevant ones for the generator.
  - *Adequate (3/5):* Uses basic implementation.
  - *Poor (1/5):* Ignores reranking entirely.

- **Criteria:** Candidate designs robust reranking.
  - *Excellent (5/5):* Mentions A cross-encoder model (e.g., a fine-tuned DeBERTa) is typically used for reranking. It takes the query and document chunk as a pair and scores their relevance.
  - *Adequate (3/5):* Uses basic implementation.
  - *Poor (1/5):* Ignores reranking entirely.

- **Criteria:** Candidate designs robust reranking.
  - *Excellent (5/5):* Mentions Cross-encoders are computationally expensive. To meet our <100ms latency budget, we use a relatively small model (e.g., 200M parameters) or deploy on GPUs with TensorRT.
  - *Adequate (3/5):* Uses basic implementation.
  - *Poor (1/5):* Ignores reranking entirely.

- **Criteria:** Candidate designs robust reranking.
  - *Excellent (5/5):* Mentions We can also use LLM-as-a-judge for reranking (e.g., RankLLaMA), but this is usually too slow for real-time consumer search and is reserved for offline evaluation.
  - *Adequate (3/5):* Uses basic implementation.
  - *Poor (1/5):* Ignores reranking entirely.

- **Criteria:** Candidate designs robust reranking.
  - *Excellent (5/5):* Mentions The reranker considers multiple signals: semantic relevance, document freshness (critical for news), domain authority (favoring reputable sites), and user engagement metrics.
  - *Adequate (3/5):* Uses basic implementation.
  - *Poor (1/5):* Ignores reranking entirely.

- **Criteria:** Candidate designs robust reranking.
  - *Excellent (5/5):* Mentions Documents are often grouped by domain to ensure source diversity. We don't want all 10 citations coming from the same website.
  - *Adequate (3/5):* Uses basic implementation.
  - *Poor (1/5):* Ignores reranking entirely.

- **Criteria:** Candidate designs robust reranking.
  - *Excellent (5/5):* Mentions Reranking helps mitigate the 'lost in the middle' phenomenon of LLMs by ensuring the absolute best information is placed at the beginning or end of the context window.
  - *Adequate (3/5):* Uses basic implementation.
  - *Poor (1/5):* Ignores reranking entirely.

- **Criteria:** Candidate designs robust reranking.
  - *Excellent (5/5):* Mentions We truncate the list of reranked documents dynamically based on a confidence threshold to save tokens in the generation phase.
  - *Adequate (3/5):* Uses basic implementation.
  - *Poor (1/5):* Ignores reranking entirely.

- **Criteria:** Candidate designs robust reranking.
  - *Excellent (5/5):* Mentions For long queries, we might use ColBERT, a late-interaction model, which offers a good balance between the speed of bi-encoders and the accuracy of cross-encoders.
  - *Adequate (3/5):* Uses basic implementation.
  - *Poor (1/5):* Ignores reranking entirely.

- **Criteria:** Candidate designs robust reranking.
  - *Excellent (5/5):* Mentions We must handle duplicate or near-duplicate documents retrieved from different sources. The reranker includes a deduplication step based on content hashing or embedding similarity.
  - *Adequate (3/5):* Uses basic implementation.
  - *Poor (1/5):* Ignores reranking entirely.

### Deep Dive: Grounded Generation with Citations

- **Criteria:** Candidate designs robust grounded generation with citations.
  - *Excellent (5/5):* Mentions The generator (e.g., GPT-4o or a fine-tuned Llama 3 70B) synthesizes the final answer using the retrieved and reranked documents.
  - *Adequate (3/5):* Uses basic implementation.
  - *Poor (1/5):* Ignores grounded generation with citations entirely.

- **Criteria:** Candidate designs robust grounded generation with citations.
  - *Excellent (5/5):* Mentions The prompt instructs the model to answer the query *only* using the provided context and to cite its sources using a specific format (e.g., [1], [2]).
  - *Adequate (3/5):* Uses basic implementation.
  - *Poor (1/5):* Ignores grounded generation with citations entirely.

- **Criteria:** Candidate designs robust grounded generation with citations.
  - *Excellent (5/5):* Mentions This 'grounding' significantly reduces hallucinations, as the model's generation is constrained by empirical evidence.
  - *Adequate (3/5):* Uses basic implementation.
  - *Poor (1/5):* Ignores grounded generation with citations entirely.

- **Criteria:** Candidate designs robust grounded generation with citations.
  - *Excellent (5/5):* Mentions However, hallucinations can still occur if the model misinterprets the context or combines information incorrectly. This requires rigorous evaluation.
  - *Adequate (3/5):* Uses basic implementation.
  - *Poor (1/5):* Ignores grounded generation with citations entirely.

- **Criteria:** Candidate designs robust grounded generation with citations.
  - *Excellent (5/5):* Mentions To enforce citation accuracy, we can use a post-processing verification step. A smaller model checks if the generated sentence is actually supported by the cited document.
  - *Adequate (3/5):* Uses basic implementation.
  - *Poor (1/5):* Ignores grounded generation with citations entirely.

- **Criteria:** Candidate designs robust grounded generation with citations.
  - *Excellent (5/5):* Mentions If a citation is invalid, the system can attempt to fix it or strip the sentence entirely.
  - *Adequate (3/5):* Uses basic implementation.
  - *Poor (1/5):* Ignores grounded generation with citations entirely.

- **Criteria:** Candidate designs robust grounded generation with citations.
  - *Excellent (5/5):* Mentions The prompt must also instruct the model to handle contradictory information. If Source A says X and Source B says Y, the model should explain the discrepancy.
  - *Adequate (3/5):* Uses basic implementation.
  - *Poor (1/5):* Ignores grounded generation with citations entirely.

- **Criteria:** Candidate designs robust grounded generation with citations.
  - *Excellent (5/5):* Mentions Context window management is crucial. We must ensure the query, system prompt, and all retrieved chunks fit within the model's limit (e.g., 32k or 128k tokens).
  - *Adequate (3/5):* Uses basic implementation.
  - *Poor (1/5):* Ignores grounded generation with citations entirely.

- **Criteria:** Candidate designs robust grounded generation with citations.
  - *Excellent (5/5):* Mentions We prioritize chunks based on their reranker score when packing the context window.
  - *Adequate (3/5):* Uses basic implementation.
  - *Poor (1/5):* Ignores grounded generation with citations entirely.

- **Criteria:** Candidate designs robust grounded generation with citations.
  - *Excellent (5/5):* Mentions The generated response must be formatted in Markdown, seamlessly integrating the inline citations which are then rendered as clickable links in the frontend.
  - *Adequate (3/5):* Uses basic implementation.
  - *Poor (1/5):* Ignores grounded generation with citations entirely.

### Deep Dive: Streaming

- **Criteria:** Candidate designs robust streaming.
  - *Excellent (5/5):* Mentions Streaming is non-negotiable for AI search. Users will not wait 5-10 seconds for a full answer to generate.
  - *Adequate (3/5):* Uses basic implementation.
  - *Poor (1/5):* Ignores streaming entirely.

- **Criteria:** Candidate designs robust streaming.
  - *Excellent (5/5):* Mentions We use Server-Sent Events (SSE) or WebSockets to stream the response token-by-token from the LLM to the client.
  - *Adequate (3/5):* Uses basic implementation.
  - *Poor (1/5):* Ignores streaming entirely.

- **Criteria:** Candidate designs robust streaming.
  - *Excellent (5/5):* Mentions Time-To-First-Token (TTFT) is our primary latency metric. It includes the time for decomposition, retrieval, reranking, and the initial LLM forward pass.
  - *Adequate (3/5):* Uses basic implementation.
  - *Poor (1/5):* Ignores streaming entirely.

- **Criteria:** Candidate designs robust streaming.
  - *Excellent (5/5):* Mentions We aim for a TTFT of under 1 second. This requires aggressive optimization of the pre-generation pipeline.
  - *Adequate (3/5):* Uses basic implementation.
  - *Poor (1/5):* Ignores streaming entirely.

- **Criteria:** Candidate designs robust streaming.
  - *Excellent (5/5):* Mentions Streaming citations presents a UI challenge. The citation number (e.g., [1]) might be generated before the actual source URL is fully resolved or mapped in the frontend.
  - *Adequate (3/5):* Uses basic implementation.
  - *Poor (1/5):* Ignores streaming entirely.

- **Criteria:** Candidate designs robust streaming.
  - *Excellent (5/5):* Mentions We send the list of sources as a separate JSON payload *before* starting the text stream, so the frontend can immediately render the citation links as they arrive.
  - *Adequate (3/5):* Uses basic implementation.
  - *Poor (1/5):* Ignores streaming entirely.

- **Criteria:** Candidate designs robust streaming.
  - *Excellent (5/5):* Mentions If the generator model supports speculative decoding, we can significantly increase the streaming token rate (tokens per second).
  - *Adequate (3/5):* Uses basic implementation.
  - *Poor (1/5):* Ignores streaming entirely.

- **Criteria:** Candidate designs robust streaming.
  - *Excellent (5/5):* Mentions Connection drops during streaming must be handled gracefully. The client should be able to resume or retry the generation.
  - *Adequate (3/5):* Uses basic implementation.
  - *Poor (1/5):* Ignores streaming entirely.

- **Criteria:** Candidate designs robust streaming.
  - *Excellent (5/5):* Mentions We must ensure that the safety filters (checking for toxicity or PII) operate effectively on streamed tokens, often using a sliding window approach.
  - *Adequate (3/5):* Uses basic implementation.
  - *Poor (1/5):* Ignores streaming entirely.

- **Criteria:** Candidate designs robust streaming.
  - *Excellent (5/5):* Mentions Load balancing for streaming connections is stateful. We use consistent hashing or specific routing rules to keep the connection pinned to the correct inference server.
  - *Adequate (3/5):* Uses basic implementation.
  - *Poor (1/5):* Ignores streaming entirely.

### Deep Dive: Caching

- **Criteria:** Candidate designs robust caching.
  - *Excellent (5/5):* Mentions Caching occurs at multiple layers: exact query match, sub-query retrieval, and semantic similarity.
  - *Adequate (3/5):* Uses basic implementation.
  - *Poor (1/5):* Ignores caching entirely.

- **Criteria:** Candidate designs robust caching.
  - *Excellent (5/5):* Mentions Exact Query Cache (Redis): If a user asks exactly the same question as a recent query, we return the cached final response instantly (TTFT < 50ms).
  - *Adequate (3/5):* Uses basic implementation.
  - *Poor (1/5):* Ignores caching entirely.

- **Criteria:** Candidate designs robust caching.
  - *Excellent (5/5):* Mentions This cache must have a short TTL (e.g., 1 hour) for queries related to news or real-time events, but can be longer for evergreen queries (e.g., 'history of Rome').
  - *Adequate (3/5):* Uses basic implementation.
  - *Poor (1/5):* Ignores caching entirely.

- **Criteria:** Candidate designs robust caching.
  - *Excellent (5/5):* Mentions Sub-query Cache: We cache the retrieval and reranking results for common sub-queries. 'What is the population of Paris?' is useful across many complex queries.
  - *Adequate (3/5):* Uses basic implementation.
  - *Poor (1/5):* Ignores caching entirely.

- **Criteria:** Candidate designs robust caching.
  - *Excellent (5/5):* Mentions Semantic Cache (Vector DB): We can use a fast vector search on incoming queries against recently answered queries. If the semantic similarity is >0.95, we reuse the answer.
  - *Adequate (3/5):* Uses basic implementation.
  - *Poor (1/5):* Ignores caching entirely.

- **Criteria:** Candidate designs robust caching.
  - *Excellent (5/5):* Mentions Semantic caching is risky. 'How to fix a flat tire on a bike' and 'How to fix a flat tire on a car' are semantically similar but require vastly different answers.
  - *Adequate (3/5):* Uses basic implementation.
  - *Poor (1/5):* Ignores caching entirely.

- **Criteria:** Candidate designs robust caching.
  - *Excellent (5/5):* Mentions We use a fast verification model to double-check semantic cache hits before serving them to the user.
  - *Adequate (3/5):* Uses basic implementation.
  - *Poor (1/5):* Ignores caching entirely.

- **Criteria:** Candidate designs robust caching.
  - *Excellent (5/5):* Mentions Cache invalidation is tricky. When a major news event breaks, we must proactively invalidate caches related to that topic.
  - *Adequate (3/5):* Uses basic implementation.
  - *Poor (1/5):* Ignores caching entirely.

- **Criteria:** Candidate designs robust caching.
  - *Excellent (5/5):* Mentions We use edge caching (CDN) for static assets, but the dynamic AI search responses are cached at the application layer in the data center.
  - *Adequate (3/5):* Uses basic implementation.
  - *Poor (1/5):* Ignores caching entirely.

- **Criteria:** Candidate designs robust caching.
  - *Excellent (5/5):* Mentions The caching strategy dramatically reduces API costs (OpenAI/Anthropic) and compute requirements for self-hosted models.
  - *Adequate (3/5):* Uses basic implementation.
  - *Poor (1/5):* Ignores caching entirely.

### Deep Dive: Freshness and Cost

- **Criteria:** Candidate designs robust freshness and cost.
  - *Excellent (5/5):* Mentions Freshness is the defining feature of AI search compared to static knowledge bases.
  - *Adequate (3/5):* Uses basic implementation.
  - *Poor (1/5):* Ignores freshness and cost entirely.

- **Criteria:** Candidate designs robust freshness and cost.
  - *Excellent (5/5):* Mentions Our crawler pipeline constantly monitors RSS feeds, news sites, and social media for new content.
  - *Adequate (3/5):* Uses basic implementation.
  - *Poor (1/5):* Ignores freshness and cost entirely.

- **Criteria:** Candidate designs robust freshness and cost.
  - *Excellent (5/5):* Mentions We use an incremental indexing strategy. New documents are added to a fast-update memory-mapped index before being merged into the main disk-based index.
  - *Adequate (3/5):* Uses basic implementation.
  - *Poor (1/5):* Ignores freshness and cost entirely.

- **Criteria:** Candidate designs robust freshness and cost.
  - *Excellent (5/5):* Mentions Cost management is a primary architectural driver. A single AI search query can cost 10x to 100x more than a traditional keyword search.
  - *Adequate (3/5):* Uses basic implementation.
  - *Poor (1/5):* Ignores freshness and cost entirely.

- **Criteria:** Candidate designs robust freshness and cost.
  - *Excellent (5/5):* Mentions We employ a cascade of models. Simple queries might be handled entirely by an 8B parameter model, while complex reasoning requires a 70B or proprietary model.
  - *Adequate (3/5):* Uses basic implementation.
  - *Poor (1/5):* Ignores freshness and cost entirely.

- **Criteria:** Candidate designs robust freshness and cost.
  - *Excellent (5/5):* Mentions We dynamically adjust the number of retrieved documents based on the query complexity. Simple queries get 3 docs; complex ones get 20. This saves tokens.
  - *Adequate (3/5):* Uses basic implementation.
  - *Poor (1/5):* Ignores freshness and cost entirely.

- **Criteria:** Candidate designs robust freshness and cost.
  - *Excellent (5/5):* Mentions Context caching (if supported by the LLM provider, like Anthropic's prompt caching) is used extensively for the system prompt and common instructions.
  - *Adequate (3/5):* Uses basic implementation.
  - *Poor (1/5):* Ignores freshness and cost entirely.

- **Criteria:** Candidate designs robust freshness and cost.
  - *Excellent (5/5):* Mentions We track the cost per query and aggregate it by user and tenant. This data is fed into our billing system and alerting pipelines.
  - *Adequate (3/5):* Uses basic implementation.
  - *Poor (1/5):* Ignores freshness and cost entirely.

- **Criteria:** Candidate designs robust freshness and cost.
  - *Excellent (5/5):* Mentions To handle spikes in traffic without breaking the bank, we implement dynamic rate limiting and graceful degradation (e.g., disabling the most expensive reasoning steps under high load).
  - *Adequate (3/5):* Uses basic implementation.
  - *Poor (1/5):* Ignores freshness and cost entirely.

- **Criteria:** Candidate designs robust freshness and cost.
  - *Excellent (5/5):* Mentions We heavily utilize spot instances for offline batch processing and evaluation to reduce cloud compute costs.
  - *Adequate (3/5):* Uses basic implementation.
  - *Poor (1/5):* Ignores freshness and cost entirely.

### Deep Dive: Evaluation

- **Criteria:** Candidate designs robust evaluation.
  - *Excellent (5/5):* Mentions Evaluating AI search requires a multi-faceted approach, moving beyond simple accuracy metrics.
  - *Adequate (3/5):* Uses basic implementation.
  - *Poor (1/5):* Ignores evaluation entirely.

- **Criteria:** Candidate designs robust evaluation.
  - *Excellent (5/5):* Mentions We use the RAG Triad for automated evaluation: Context Relevance, Answer Relevance, and Groundedness.
  - *Adequate (3/5):* Uses basic implementation.
  - *Poor (1/5):* Ignores evaluation entirely.

- **Criteria:** Candidate designs robust evaluation.
  - *Excellent (5/5):* Mentions Context Relevance checks if the retrieved documents actually contain the answer to the query.
  - *Adequate (3/5):* Uses basic implementation.
  - *Poor (1/5):* Ignores evaluation entirely.

- **Criteria:** Candidate designs robust evaluation.
  - *Excellent (5/5):* Mentions Answer Relevance ensures the final generated text directly addresses the user's question, without going off on tangents.
  - *Adequate (3/5):* Uses basic implementation.
  - *Poor (1/5):* Ignores evaluation entirely.

- **Criteria:** Candidate designs robust evaluation.
  - *Excellent (5/5):* Mentions Groundedness is paramount. We measure the hallucination rate by checking if every claim in the generated answer is supported by a citation.
  - *Adequate (3/5):* Uses basic implementation.
  - *Poor (1/5):* Ignores evaluation entirely.

- **Criteria:** Candidate designs robust evaluation.
  - *Excellent (5/5):* Mentions We employ 'LLM-as-a-judge' pipelines running continuously on a sample of production traffic. GPT-4 evaluates the outputs of our production models.
  - *Adequate (3/5):* Uses basic implementation.
  - *Poor (1/5):* Ignores evaluation entirely.

- **Criteria:** Candidate designs robust evaluation.
  - *Excellent (5/5):* Mentions Human evaluation remains essential. We have a team of domain experts who grade responses based on a detailed rubric (accuracy, tone, helpfulness).
  - *Adequate (3/5):* Uses basic implementation.
  - *Poor (1/5):* Ignores evaluation entirely.

- **Criteria:** Candidate designs robust evaluation.
  - *Excellent (5/5):* Mentions A/B testing is used for every change. We route 5% of traffic to a new reranker model and compare engagement metrics (session length, follow-up queries, explicit thumbs up/down).
  - *Adequate (3/5):* Uses basic implementation.
  - *Poor (1/5):* Ignores evaluation entirely.

- **Criteria:** Candidate designs robust evaluation.
  - *Excellent (5/5):* Mentions We specifically test for adversarial inputs and jailbreak attempts to ensure our safety filters are robust.
  - *Adequate (3/5):* Uses basic implementation.
  - *Poor (1/5):* Ignores evaluation entirely.

- **Criteria:** Candidate designs robust evaluation.
  - *Excellent (5/5):* Mentions Latency and cost metrics are tracked alongside quality metrics. A model that is 2% more accurate but 5x slower and 10x more expensive might not be deployed.
  - *Adequate (3/5):* Uses basic implementation.
  - *Poor (1/5):* Ignores evaluation entirely.

### Deep Dive: Query Decomposition

- **Criteria:** Candidate designs robust query decomposition.
  - *Excellent (5/5):* Mentions User queries in AI search are often complex and multi-faceted. The query decomposition module breaks these down into simpler, atomic sub-queries that can be executed independently against the search index.
  - *Adequate (3/5):* Uses basic implementation.
  - *Poor (1/5):* Ignores query decomposition entirely.

