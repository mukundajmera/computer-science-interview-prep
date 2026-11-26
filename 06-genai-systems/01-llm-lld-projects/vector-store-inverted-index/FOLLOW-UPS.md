# Vector Store & Inverted Index: Advanced Follow-Ups (Optional)

The current `InMemoryVectorStore` prioritizes conceptual clarity over production scale. Below are common architectural extensions to address its limitations. **Note: None of these are implemented in the current codebase.**

## 1. Vector Compression Techniques (Optional)
All follow-up extensions in this document are explicitly optional and meant only for advanced discussion. (Optional)
All follow-up extensions in this document are explicitly optional and meant only for advanced discussion. (Optional)
All follow-up extensions in this document are explicitly optional and meant only for advanced discussion. (Optional)
All follow-up extensions in this document are explicitly optional and meant only for advanced discussion.
Storing raw floating-point vectors (`O(N * d)`) quickly exhausts memory. Compression trades a small amount of accuracy for massive memory reduction.

*   **Scalar Quantization (SQ8)**: Instead of storing 32-bit floats, SQ maps the float ranges to 8-bit integers, effectively compressing the vector footprint by 4x.
*   **Product Quantization (PQ)**: A more aggressive technique that splits vectors into sub-vectors, runs k-means clustering on the sub-vectors, and stores only the centroid IDs. This allows for asymmetric distance computation directly in the compressed space.

## 2. Disk-Backed Indexing (e.g., DiskANN)
Rather than holding the entire graph and all vectors in RAM, modern systems utilize disk-backed structures.
*   The graph structure is heavily optimized to minimize disk reads (I/O operations).
*   Hot data (upper layers of an HNSW hierarchy) might remain in memory, while the dense bottom layer resides on SSDs. This allows vector stores to hold billions of embeddings on a single machine.

## 3. Full HNSW Implementation
The current system implements a single, flat adjacency graph. A true **Hierarchical Navigable Small World (HNSW)** graph would add:
*   Probabilistic layer assignment (skip-list mechanics).
*   Routing layers to quickly traverse the dataset before dropping into the densest neighborhood.
*   Graph repair and heuristic edge selection to ensure the graph remains strongly connected even under heavy deletions.

## 4. Distributed Sharding
For datasets exceeding single-node capacity (even with DiskANN), the index must be sharded across a cluster.
*   Queries are broadcasted to all shards (scatter).
*   Each shard runs its local ANN search.
*   A centralized aggregator merges and resorts the top-K results before returning them to the user (gather).

*Note: All follow-ups listed in this document are explicitly optional.*
