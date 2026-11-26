# Vector Store & Inverted Index: Problem Definition

In modern generative AI and retrieval-augmented generation (RAG) systems, efficiently retrieving relevant context is critical. Models convert documents into dense, high-dimensional vector embeddings. A **Vector Store** must handle storing these embeddings, performing rapid similarity searches, and accommodating metadata filtering. 

## 1. Vector Embedding Storage Requirements
A vector database must accept dynamically inserted vector representations of data along with accompanying metadata. The primary operations required are:
- Storing vectors in high-dimensional space (e.g., `dimension=2`, `dimension=1536`, etc.) using `add_vector` / `addVector`.
- Binding arbitrary key-value metadata to these vectors (e.g., `{"type": "A", "color": "red"}`).
- Removing vectors when they are no longer needed or if the underlying document changes using `delete_vector` / `deleteVector`.

The system exposes two primary query methods: `query_similarity` / `querySimilarity` for exact search, and `approximate_search` / `approximateSearch` for faster graph-based approximations.

In the current implementation, this is achieved through an in-memory dictionary-backed store with vectors constrained to a fixed `dimension`.

## 2. High-Dimensional Similarity Metrics
To evaluate "relevance" between a query vector and the stored embeddings, the vector store uses similarity metrics.

*   **Cosine Similarity**: Measures the cosine of the angle between two multi-dimensional vectors. It is highly effective for normalized text embeddings as it focuses on the direction (semantic meaning) rather than magnitude. The current system explicitly implements and relies on `cosine_similarity(v1, v2)`.

### Normal Fixture Example: Cosine Similarity
As tested in the `test_cosine_similarity_orthogonal_and_parallel` fixture:
*   Given `v1 = [1.0, 0.0]` and `v2 = [0.0, 1.0]` (Orthogonal vectors).
*   The system correctly computes the cosine similarity as `0.0`.
*   Given `v1 = [1.0, 0.0]` and `v3 = [2.0, 0.0]` (Parallel vectors).
*   The system computes the cosine similarity as `1.0`.

## 3. Metadata-Filtered Search
A common requirement in vector stores is isolating a search to a subset of data using metadata (e.g., "Find the nearest vectors, but only those authored by 'Alice'"). This filtering can be executed as a pre-filter (before vector search) or a post-filter (after vector search). 

### Normal Fixture Example: Metadata Filtering
As seen in `test_metadata_filtering`:
1.  Store adds `id="1"` with `{"type": "A", "color": "red"}`
2.  Store adds `id="2"` with `{"type": "B", "color": "blue"}`
3.  Store adds `id="3"` with `{"type": "A", "color": "blue"}`

When querying for `top_k=5` and passing `filter_meta={"type": "A"}`, the system filters out entry `2` completely, returning only vectors `"1"` and `"3"`.

### Error Fixture Example: Dimension Mismatch Validation
As seen in `test_dimension_mismatch_validation`:
*   Initializing a store with `dimension=3`.
*   Adding a vector `[1.0, 0.0]` or querying with `[1.0, 0.0]` correctly raises a `ValueError` indicating the dimensions do not match.
*   Directly calling `cosine_similarity` with vectors of different lengths also raises a `ValueError`.

## 4. Exact vs. Approximate Nearest Neighbor (ANN) Search
Finding the exact nearest neighbors (Exact KNN) requires an exhaustive scan of the entire dataset. While this guarantees finding the closest embeddings, it scales linearly `O(N * d)` and becomes prohibitively slow for millions of vectors. 
To counteract this, systems use **Approximate Nearest Neighbor (ANN)** search algorithms, which trade a small degree of accuracy for significant speedups.
