# Vector Store & Inverted Index: System Design

This document details the internal components of the `InMemoryVectorStore` system designed for handling vector embeddings and approximate nearest neighbor search.

## 1. Public APIs

The system exposes the following core APIs for interaction, ensuring complete logic parity across both Java and Python standard libraries:

*   `add_vector` / `addVector(id, vector, metadata)`: Inserts a new vector. Dynamically links the new vector to `M` nearest neighbors to maintain the HNSW-inspired graph.
*   `delete_vector` / `deleteVector(id)`: Removes a vector from storage and naively severs connections in the graph, without performing graph re-healing.
*   `query_similarity` / `querySimilarity(query_vector, top_k, filter_meta)`: Performs a brute-force exact KNN scan across all stored vectors.
*   `approximate_search` / `approximateSearch(query_vector, top_k, filter_meta)`: Performs a greedy walk over the HNSW-inspired single-layer graph for fast, approximate retrieval.

## 2. Memory Structures

The vector store is held entirely in memory using standard language data structures.

### The Vector Entry Wrapper
Each document/embedding ingested into the system is wrapped in a dedicated structure/class.
*   `id`: A unique string identifier.
*   `vector`: A list/array of floats representing the high-dimensional embedding.
*   `metadata`: A dictionary/map holding arbitrary key-value pairs used for filtering.

### Core Storage
The core storage mechanism is a dictionary/map (e.g., `self.vectors`), mapping the vector `id` to its corresponding entry object. This allows for `O(1)` access to any vector given its ID.

## 3. Navigable Small World (NSW) Adjacency Graph

To facilitate fast Approximate Nearest Neighbor (ANN) search, the system maintains a single-layer adjacency graph, inspired by HNSW (Hierarchical Navigable Small World) graphs. 

### Adjacency Graph Storage
This is represented by a dictionary/map (e.g., `self.graph`) mapping a vector `id` to a list of neighbor `id`s. 
*   **Insertion**: When a new vector is added, it queries the graph for its `M` nearest neighbors and connects to them.
*   **Entry Point**: `self.entry_point` keeps track of a starting node to begin graph traversals.

[HNSW Graph (Mermaid source)](diagrams/vector-store-hnsw.mmd)

## 4. Search Operations

The system implements two distinct strategies for retrieving relevant vectors.

### Exact KNN Search (`query_similarity`)
This method implements a brute-force exact K-Nearest Neighbors search. 
1.  It iterates over *every* entry in `self.vectors`.
2.  If `filter_meta` is provided, it evaluates the metadata. If it doesn't match, the vector is skipped.
3.  It calculates the exact `cosine_similarity`.
4.  It maintains the top `K` results using a max-heap (`heapq.nlargest`).
*   **Trade-off**: Guarantees 100% recall but is prohibitively slow for large datasets `O(N * d + N log K)`.

### Approximate Graph Search (`approximate_search`)
This method performs a greedy walk on the adjacency graph.
1.  It starts at `self.entry_point`.
2.  It evaluates the similarity of the current node and its connected neighbors (from `self.graph`).
3.  It maintains a min-heap of candidates to explore, prioritizing those that are closer to the query vector.
4.  Metadata filtering is evaluated *during* the traversal. When a node is popped, the filter is checked before adding it to the `best_results`.
*   **Trade-off**: Much faster `O(log N * d)` on average, but may miss the true nearest neighbors if the graph is poorly connected or if filtering heavily restricts valid paths (post-filtering degradation).

## 5. Metadata Evaluation (`filter_meta`)

Both search implementations accept a `filter_meta` dictionary. 
*   In `query_similarity`, the filter acts as a **pre-filter**. The similarity is never calculated if the metadata doesn't match, saving computation.
*   In `approximate_search`, the filter acts as an **in-traversal filter**. The traversal must still calculate the similarity to navigate the graph structure, but nodes are excluded from the final result set if they fail the metadata check.

*Note: All public APIs described above must be identical in both their Java and Python implementations (e.g., `add_vector`/`addVector`).*
