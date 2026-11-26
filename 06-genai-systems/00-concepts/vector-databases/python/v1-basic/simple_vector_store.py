"""
Simple in-memory vector database implementation for educational purposes.

This module demonstrates core concepts of vector databases:
- Storing high-dimensional vectors with metadata
- Similarity search using distance metrics
- Approximate Nearest Neighbor (ANN) search patterns

Production systems use: Pinecone, Weaviate, Milvus, Chroma, Qdrant, etc.

Time Complexity:
- Brute-force search: O(n × d) where n = vectors, d = dimensions
- Real vector DBs use ANN indexes (HNSW, IVF) for O(log n) or O(√n) search

Space Complexity: O(n × d)
"""

from typing import List, Tuple, Optional, Dict, Any
from dataclasses import dataclass
import math
import json


@dataclass
class VectorRecord:
    """Represents a stored vector with metadata."""
    id: str
    vector: List[float]
    metadata: Dict[str, Any]


class SimpleVectorStore:
    """
    In-memory vector database with similarity search.

    Real vector DBs optimize with:
    - Approximate Nearest Neighbor (ANN) algorithms (HNSW, IVF)
    - Quantization for memory efficiency
    - Distributed sharding for scale
    - Persistent storage with indexing

    This implementation uses brute-force search for clarity.
    """

    def __init__(self, dimension: int):
        """
        Initialize vector store.

        Args:
            dimension: Vector dimensionality (e.g., 1536 for OpenAI embeddings)
        """
        self.dimension = dimension
        self.vectors: List[VectorRecord] = []
        self._id_index: Dict[str, int] = {}  # Fast lookup by ID

    def insert(self, id: str, vector: List[float], metadata: Optional[Dict[str, Any]] = None):
        """
        Insert a vector into the store.

        Args:
            id: Unique identifier
            vector: Embedding vector
            metadata: Optional metadata (tags, text, etc.)

        Raises:
            ValueError: If vector dimension doesn't match

        Time Complexity: O(1)
        Space Complexity: O(d) where d = dimension
        """
        if len(vector) != self.dimension:
            raise ValueError(f"Vector must have {self.dimension} dimensions, got {len(vector)}")

        if id in self._id_index:
            raise ValueError(f"Vector with id '{id}' already exists")

        record = VectorRecord(
            id=id,
            vector=vector,
            metadata=metadata or {}
        )
        self._id_index[id] = len(self.vectors)
        self.vectors.append(record)

    def search(
        self,
        query_vector: List[float],
        top_k: int = 5,
        metric: str = "cosine",
        filters: Optional[Dict[str, Any]] = None,
        post_filters: Optional[Dict[str, Any]] = None
    ) -> List[Tuple[str, float, Dict[str, Any]]]:
        """
        Search for most similar vectors.

        Args:
            query_vector: Query embedding
            top_k: Number of results to return
            metric: Distance metric ('cosine', 'euclidean', 'dot_product')
            filters: Optional metadata filters (e.g., {'category': 'tech'})

        Returns:
            List of (id, similarity_score, metadata) tuples, sorted by similarity

        Time Complexity: O(n × d) where n = number of vectors, d = dimension
        Note: Real vector DBs use ANN for O(log n) or O(√n) search

        Example:
            >>> store.search([0.1, 0.2, 0.3], top_k=3, metric='cosine')
            [('doc1', 0.95, {}), ('doc2', 0.87, {}), ('doc3', 0.82, {})]
        """
        if len(query_vector) != self.dimension:
            raise ValueError(f"Query vector must have {self.dimension} dimensions")

        # Calculate similarity for all vectors (brute force)
        similarities = []
        for record in self.vectors:
            # Apply metadata filters (pre-filtering)
            if filters and not self._matches_filters(record.metadata, filters):
                continue

            # Calculate similarity based on metric
            if metric == "cosine":
                score = self._cosine_similarity(query_vector, record.vector)
            elif metric == "euclidean":
                score = -self._euclidean_distance(query_vector, record.vector)  # Negate for ranking
            elif metric == "dot_product":
                score = self._dot_product(query_vector, record.vector)
            else:
                raise ValueError(f"Unknown metric: {metric}")

            similarities.append((record.id, score, record.metadata))

        # Sort by similarity (descending)
        similarities.sort(key=lambda x: x[1], reverse=True)

        # Apply post-filtering
        if post_filters:
            similarities = [
                sim for sim in similarities
                if self._matches_filters(sim[2], post_filters)
            ]

        return similarities[:top_k]

    def get(self, id: str) -> Optional[VectorRecord]:
        """
        Retrieve vector by ID.

        Time Complexity: O(1)
        """
        if id not in self._id_index:
            return None
        idx = self._id_index[id]
        return self.vectors[idx]

    def delete(self, id: str) -> bool:
        """
        Delete vector by ID.

        Time Complexity: O(n) (due to list deletion)
        Note: Production DBs use tombstones for O(1) deletes
        """
        if id not in self._id_index:
            return False

        idx = self._id_index[id]
        del self.vectors[idx]
        del self._id_index[id]

        # Rebuild index (expensive - production DBs use better data structures)
        self._id_index = {rec.id: i for i, rec in enumerate(self.vectors)}
        return True

    def size(self) -> int:
        """Return number of vectors in store."""
        return len(self.vectors)


    def save(self, file_path: str) -> None:
        """
        Serialize and save the index to disk.
        """
        data = {
            "dimension": self.dimension,
            "vectors": [
                {
                    "id": rec.id,
                    "vector": rec.vector,
                    "metadata": rec.metadata
                }
                for rec in self.vectors
            ]
        }
        with open(file_path, "w") as f:
            json.dump(data, f)

    @classmethod
    def load(cls, file_path: str) -> 'SimpleVectorStore':
        """
        Load the index from disk.
        """
        with open(file_path, "r") as f:
            data = json.load(f)

        store = cls(dimension=data["dimension"])
        for vec_data in data["vectors"]:
            store.insert(
                id=vec_data["id"],
                vector=vec_data["vector"],
                metadata=vec_data.get("metadata")
            )
        return store

    # Distance metric implementations

    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """
        Calculate cosine similarity: cos(θ) = (A·B) / (||A|| ||B||)

        Range: [-1, 1] where 1 = identical, 0 = orthogonal, -1 = opposite

        Time Complexity: O(d) where d = dimension

        Use for: Text embeddings (most common), any normalized vectors
        """
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        magnitude1 = math.sqrt(sum(a * a for a in vec1))
        magnitude2 = math.sqrt(sum(b * b for b in vec2))

        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0

        return dot_product / (magnitude1 * magnitude2)

    def _euclidean_distance(self, vec1: List[float], vec2: List[float]) -> float:
        """
        Calculate Euclidean distance: sqrt(sum((a_i - b_i)^2))

        Range: [0, ∞) where 0 = identical

        Time Complexity: O(d)

        Use for: Image embeddings, spatial data, when magnitude matters
        """
        return math.sqrt(sum((a - b) ** 2 for a, b in zip(vec1, vec2)))

    def _dot_product(self, vec1: List[float], vec2: List[float]) -> float:
        """
        Calculate dot product: sum(a_i * b_i)

        Range: (-∞, +∞)

        Time Complexity: O(d)

        Use for: Recommendation systems (popularity + relevance),
                 normalized vectors (equivalent to cosine)

        Note: For L2-normalized vectors, dot product = cosine similarity
        """
        return sum(a * b for a, b in zip(vec1, vec2))

    def _matches_filters(self, metadata: Dict[str, Any], filters: Dict[str, Any]) -> bool:
        """
        Check if metadata matches all filters.

        Simple equality check. Production DBs support:
        - Range queries: {'age': {'$gt': 18, '$lt': 65}}
        - Array contains: {'tags': {'$in': ['python', 'rust']}}
        - Text search: {'description': {'$text': 'machine learning'}}
        """
        return all(metadata.get(key) == value for key, value in filters.items())


class HybridVectorStore(SimpleVectorStore):
    """
    Vector store with keyword search capabilities (hybrid search).

    Combines:
    - Semantic search (vector similarity)
    - Keyword search (BM25-like text matching)

    Production hybrid search: Weaviate, Elasticsearch 8.0+, Qdrant
    """

    def __init__(self, dimension: int):
        """Initialize hybrid store with vector and keyword indexes."""
        super().__init__(dimension)
        self._keyword_index: Dict[str, set] = {}

    def insert(self, id: str, vector: List[float], metadata: Optional[Dict[str, Any]] = None):
        """Insert vector and build keyword index."""
        super().insert(id, vector, metadata)
        record = self.get(id)
        if record:
            self._index_keywords(id, record.metadata or {})

    def _index_keywords(self, id: str, metadata: Dict[str, Any]):
        """
        Build simple keyword index for text fields.

        Production systems use inverted indexes (Elasticsearch/BM25).
        """
        # Simplified: Extract 'text' field for keyword indexing
        text = metadata.get('text', '')
        words = text.lower().split()
        for word in words:
            if word not in self._keyword_index:
                self._keyword_index[word] = set()
            self._keyword_index[word].add(id)

    def hybrid_search(
        self,
        query_vector: List[float],
        query_text: str,
        top_k: int = 5,
        alpha: float = 0.5
    ) -> List[Tuple[str, float, Dict[str, Any]]]:
        """
        Hybrid search combining semantic and keyword relevance.

        Args:
            query_vector: Semantic query embedding
            query_text: Keyword query string
            top_k: Number of results
            alpha: Weight for vector search (1-alpha for keyword)
                   alpha=1.0 → pure vector search
                   alpha=0.0 → pure keyword search
                   alpha=0.5 → balanced

        Returns:
            Combined ranked results

        Algorithm: Reciprocal Rank Fusion (RRF) or weighted score combination
        """
        # Vector search results
        vector_results = self.search(query_vector, top_k=top_k * 2)

        # Keyword search results
        keyword_results = self._keyword_search(query_text, top_k=top_k * 2)

        # Combine using weighted scores
        combined_scores: Dict[str, float] = {}

        # Add vector scores (normalized)
        for id, score, _ in vector_results:
            combined_scores[id] = alpha * score

        # Add keyword scores (normalized)
        for id, score, _ in keyword_results:
            combined_scores[id] = combined_scores.get(id, 0) + (1 - alpha) * score

        # Sort and retrieve full records
        ranked_ids = sorted(combined_scores.items(), key=lambda x: x[1], reverse=True)
        results = []
        for id, score in ranked_ids[:top_k]:
            record = self.get(id)
            if record:
                results.append((id, score, record.metadata))

        return results

    def _keyword_search(self, query_text: str, top_k: int) -> List[Tuple[str, float, Dict[str, Any]]]:
        """
        Simple keyword search using term frequency.

        Production systems use BM25 or TF-IDF.
        """
        words = query_text.lower().split()
        doc_scores: Dict[str, int] = {}

        # Count matching terms
        for word in words:
            if word in self._keyword_index:
                for doc_id in self._keyword_index[word]:
                    doc_scores[doc_id] = doc_scores.get(doc_id, 0) + 1

        # Normalize scores
        max_score = max(doc_scores.values()) if doc_scores else 1
        normalized = [(id, score / max_score) for id, score in doc_scores.items()]
        normalized.sort(key=lambda x: x[1], reverse=True)

        # Retrieve full records
        results = []
        for id, score in normalized[:top_k]:
            record = self.get(id)
            if record:
                results.append((id, score, record.metadata))

        return results


# Demonstration
if __name__ == "__main__":
    print("=== Simple Vector Store Demo ===\n")

    # Create vector store for 3-dimensional vectors (toy example)
    store = SimpleVectorStore(dimension=3)

    # Insert documents as vectors (in reality, these would be from an embedding model)
    store.insert("doc1", [1.0, 0.0, 0.0], {"text": "Machine learning basics", "category": "AI"})
    store.insert("doc2", [0.9, 0.1, 0.0], {"text": "Deep learning tutorial", "category": "AI"})
    store.insert("doc3", [0.0, 1.0, 0.0], {"text": "Database systems", "category": "DB"})
    store.insert("doc4", [0.0, 0.9, 0.1], {"text": "SQL databases", "category": "DB"})
    store.insert("doc5", [0.5, 0.5, 0.0], {"text": "AI for databases", "category": "AI"})

    print(f"Inserted {store.size()} documents\n")

    # Search 1: Find similar documents (semantic search)
    query = [0.95, 0.05, 0.0]  # Similar to "Machine learning"
    print("Query 1: Vector similar to 'Machine learning'")
    print(f"Query vector: {query}\n")

    results = store.search(query, top_k=3, metric="cosine")
    print("Top 3 similar documents (cosine similarity):")
    for doc_id, similarity, metadata in results:
        print(f"  {doc_id}: {metadata['text']:<30} (similarity: {similarity:.4f})")
    print()

    # Search 2: With metadata filter
    print("Query 2: Similar to 'Database' + filter by category='DB'")
    query2 = [0.0, 0.95, 0.05]
    results_filtered = store.search(
        query2,
        top_k=2,
        metric="cosine",
        filters={"category": "DB"}
    )
    print("Results:")
    for doc_id, similarity, metadata in results_filtered:
        print(f"  {doc_id}: {metadata['text']:<30} (similarity: {similarity:.4f})")
    print()

    # Search 3: Different distance metrics
    print("Query 3: Comparing distance metrics")
    query3 = [0.7, 0.3, 0.0]
    print(f"Query vector: {query3}\n")

    for metric in ["cosine", "euclidean", "dot_product"]:
        results_metric = store.search(query3, top_k=2, metric=metric)
        print(f"{metric.capitalize()} metric:")
        for doc_id, score, metadata in results_metric:
            print(f"  {doc_id}: {score:.4f}")
    print()

    # Demonstration: Hybrid search
    print("\n=== Hybrid Vector Store Demo ===\n")

    hybrid_store = HybridVectorStore(dimension=3)

    # Insert same documents
    hybrid_store.insert("doc1", [1.0, 0.0, 0.0], {"text": "Machine learning basics", "category": "AI"})
    hybrid_store.insert("doc2", [0.9, 0.1, 0.0], {"text": "Deep learning tutorial", "category": "AI"})
    hybrid_store.insert("doc3", [0.0, 1.0, 0.0], {"text": "Database systems overview", "category": "DB"})
    hybrid_store.insert("doc4", [0.0, 0.9, 0.1], {"text": "SQL database tutorial", "category": "DB"})

    # Hybrid search: Combine semantic + keyword
    print("Hybrid search: 'database tutorial'")
    hybrid_results = hybrid_store.hybrid_search(
        query_vector=[0.0, 0.8, 0.2],
        query_text="database tutorial",
        top_k=3,
        alpha=0.5  # 50% semantic, 50% keyword
    )

    print("Results (combined semantic + keyword):")
    for doc_id, score, metadata in hybrid_results:
        print(f"  {doc_id}: {metadata['text']:<30} (combined score: {score:.4f})")
    print()

    # Compare with pure vector search
    print("Pure vector search (alpha=1.0):")
    vector_only = hybrid_store.hybrid_search(
        query_vector=[0.0, 0.8, 0.2],
        query_text="database tutorial",
        top_k=3,
        alpha=1.0  # Pure vector
    )
    for doc_id, score, metadata in vector_only:
        print(f"  {doc_id}: {metadata['text']:<30} (score: {score:.4f})")
    print()

    print("Pure keyword search (alpha=0.0):")
    keyword_only = hybrid_store.hybrid_search(
        query_vector=[0.0, 0.8, 0.2],
        query_text="database tutorial",
        top_k=3,
        alpha=0.0  # Pure keyword
    )
    for doc_id, score, metadata in keyword_only:
        print(f"  {doc_id}: {metadata['text']:<30} (score: {score:.4f})")
    print()

    print("\n=== Key Takeaways ===")
    print("1. Vector search finds semantically similar items (not exact matches)")
    print("2. Distance metrics matter: cosine for text, L2 for images")
    print("3. Metadata filtering enables precise queries")
    print("4. Hybrid search combines semantic + keyword for best results")
    print("5. Production vector DBs use ANN indexes (HNSW, IVF) for scale")
    print("\nFor production use: Pinecone, Weaviate, Milvus, Chroma, Qdrant, pgvector")
