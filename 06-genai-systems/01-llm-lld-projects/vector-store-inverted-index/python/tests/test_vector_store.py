import sys
import os
import pytest

# Insert the versioned module to python path using absolute path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'v1-basic')))

from vector_store import InMemoryVectorStore, cosine_similarity, VectorEntry

def test_cosine_similarity_orthogonal_and_parallel():
    v1 = [1.0, 0.0]
    v2 = [0.0, 1.0]
    v3 = [2.0, 0.0]
    v4 = [-1.0, 0.0]
    
    # Orthogonal
    assert abs(cosine_similarity(v1, v2)) < 1e-6
    # Parallel (same direction)
    assert abs(cosine_similarity(v1, v3) - 1.0) < 1e-6
    # Anti-parallel
    assert abs(cosine_similarity(v1, v4) - (-1.0)) < 1e-6
    # Zero vector
    assert cosine_similarity(v1, [0.0, 0.0]) == 0.0

def test_add_and_query_top_k():
    store = InMemoryVectorStore(dimension=2)
    store.add_vector("1", [1.0, 0.0], {"type": "A"})
    store.add_vector("2", [0.9, 0.1], {"type": "B"})
    store.add_vector("3", [0.0, 1.0], {"type": "A"})
    
    results = store.query_similarity([1.0, 0.0], top_k=2)
    assert len(results) == 2
    # Result should be sorted by similarity descending
    assert results[0][0].id == "1"
    assert results[1][0].id == "2"
    
def test_metadata_filtering():
    store = InMemoryVectorStore(dimension=2)
    store.add_vector("1", [1.0, 0.0], {"type": "A", "color": "red"})
    store.add_vector("2", [1.0, 0.0], {"type": "B", "color": "blue"})
    store.add_vector("3", [1.0, 0.0], {"type": "A", "color": "blue"})
    
    results = store.query_similarity([1.0, 0.0], top_k=5, filter_meta={"type": "A"})
    assert len(results) == 2
    assert set(res[0].id for res in results) == {"1", "3"}
    
    results = store.query_similarity([1.0, 0.0], top_k=5, filter_meta={"type": "A", "color": "blue"})
    assert len(results) == 1
    assert results[0][0].id == "3"

def test_dimension_mismatch_validation():
    store = InMemoryVectorStore(dimension=3)
    
    with pytest.raises(ValueError, match="Vector dimension must be 3"):
        store.add_vector("1", [1.0, 0.0], {})
        
    store.add_vector("1", [1.0, 0.0, 0.0], {})
    
    with pytest.raises(ValueError, match="Query vector dimension must be 3"):
        store.query_similarity([1.0, 0.0], top_k=1)
        
    with pytest.raises(ValueError, match="Dimensions do not match"):
        cosine_similarity([1.0, 0.0], [1.0, 0.0, 0.0])
