import sys
import os
import tempfile
import pytest
import math

# Use sys.path to handle hyphenated directory names for importing
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'v1-basic')))

from simple_vector_store import SimpleVectorStore, VectorRecord

def test_distance_metrics():
    """Test Cosine similarity, Euclidean distance, and Dot product scoring."""
    store = SimpleVectorStore(dimension=3)

    # A vector along x-axis
    store.insert("doc1", [1.0, 0.0, 0.0], {"name": "doc1"})
    # A vector along y-axis
    store.insert("doc2", [0.0, 1.0, 0.0], {"name": "doc2"})
    # A vector somewhere in between
    store.insert("doc3", [0.5, 0.5, 0.0], {"name": "doc3"})

    query = [1.0, 0.0, 0.0]

    # Test Cosine Similarity
    # doc1 should be 1.0 (parallel), doc2 should be 0.0 (orthogonal), doc3 should be somewhere in between (sqrt(2)/2 = 0.707)
    res_cosine = store.search(query, metric="cosine", top_k=3)

    assert res_cosine[0][0] == "doc1"
    assert math.isclose(res_cosine[0][1], 1.0)
    assert res_cosine[1][0] == "doc3"
    assert math.isclose(res_cosine[1][1], 1.0 / math.sqrt(2))
    assert res_cosine[2][0] == "doc2"
    assert math.isclose(res_cosine[2][1], 0.0)

    # Test Euclidean Distance
    # -distance (higher score is better/closer)
    # distance(query, doc1) = 0 => score = 0
    # distance(query, doc3) = sqrt((1-0.5)^2 + (-0.5)^2) = sqrt(0.5) = 0.707 => score = -0.707
    # distance(query, doc2) = sqrt((1-0)^2 + (-1)^2) = sqrt(2) = 1.414 => score = -1.414
    res_euclidean = store.search(query, metric="euclidean", top_k=3)

    assert res_euclidean[0][0] == "doc1"
    assert math.isclose(res_euclidean[0][1], 0.0)
    assert res_euclidean[1][0] == "doc3"
    assert math.isclose(res_euclidean[1][1], -math.sqrt(0.5))
    assert res_euclidean[2][0] == "doc2"
    assert math.isclose(res_euclidean[2][1], -math.sqrt(2))

    # Test Dot Product
    # dot(query, doc1) = 1*1 = 1.0
    # dot(query, doc3) = 1*0.5 = 0.5
    # dot(query, doc2) = 1*0 = 0.0
    res_dot = store.search(query, metric="dot_product", top_k=3)

    assert res_dot[0][0] == "doc1"
    assert math.isclose(res_dot[0][1], 1.0)
    assert res_dot[1][0] == "doc3"
    assert math.isclose(res_dot[1][1], 0.5)
    assert res_dot[2][0] == "doc2"
    assert math.isclose(res_dot[2][1], 0.0)

    # Test unknown metric
    with pytest.raises(ValueError):
        store.search(query, metric="unknown_metric")

def test_metadata_filtering():
    """Test metadata pre-filtering and post-filtering."""
    store = SimpleVectorStore(dimension=2)

    store.insert("doc1", [1.0, 0.0], {"category": "tech", "year": 2023, "author": "Alice"})
    store.insert("doc2", [0.9, 0.1], {"category": "health", "year": 2023, "author": "Bob"})
    store.insert("doc3", [0.8, 0.2], {"category": "tech", "year": 2022, "author": "Alice"})
    store.insert("doc4", [0.7, 0.3], {"category": "finance", "year": 2023, "author": "Charlie"})

    query = [1.0, 0.0]

    # Pre-filtering
    res_pre = store.search(query, top_k=5, filters={"category": "tech"})
    assert len(res_pre) == 2
    assert set([r[0] for r in res_pre]) == {"doc1", "doc3"}

    res_pre_multiple = store.search(query, top_k=5, filters={"category": "tech", "year": 2023})
    assert len(res_pre_multiple) == 1
    assert res_pre_multiple[0][0] == "doc1"

    # Post-filtering
    # After sorting all documents by score (doc1, doc2, doc3, doc4),
    # post_filtering retains those matching the filter (doc1, doc3),
    # then slices top_k=2, returning doc1 and doc3.
    res_post = store.search(query, top_k=2, post_filters={"category": "tech"})
    assert len(res_post) == 2
    assert res_post[0][0] == "doc1"
    assert res_post[1][0] == "doc3"

    # Combined pre and post
    # Pre-filter by year 2023 (returns doc1, doc2, doc4)
    # Sorting will order them: doc1, doc2, doc4
    # With top_k=2, we get doc1, doc2
    # Post-filter by author Alice
    res_combined = store.search(query, top_k=2, filters={"year": 2023}, post_filters={"author": "Alice"})
    assert len(res_combined) == 1
    assert res_combined[0][0] == "doc1"

def test_top_k_ranking_accuracy():
    """Test that top-k ranking correctly orders by similarity."""
    store = SimpleVectorStore(dimension=2)

    store.insert("doc_far", [0.0, 1.0], {"name": "far"})
    store.insert("doc_close", [0.9, 0.1], {"name": "close"})
    store.insert("doc_exact", [1.0, 0.0], {"name": "exact"})
    store.insert("doc_mid", [0.5, 0.5], {"name": "mid"})

    query = [1.0, 0.0]

    # Top 1
    res1 = store.search(query, top_k=1)
    assert len(res1) == 1
    assert res1[0][0] == "doc_exact"

    # Top 3
    res3 = store.search(query, top_k=3)
    assert len(res3) == 3
    assert res3[0][0] == "doc_exact"
    assert res3[1][0] == "doc_close"
    assert res3[2][0] == "doc_mid"

    # Top 10 (more than available)
    res_all = store.search(query, top_k=10)
    assert len(res_all) == 4
    assert res_all[0][0] == "doc_exact"
    assert res_all[-1][0] == "doc_far"

def test_persistence_serialization():
    """Test index persistence (save and load)."""
    store = SimpleVectorStore(dimension=3)

    store.insert("doc1", [1.0, 2.0, 3.0], {"category": "A"})
    store.insert("doc2", [4.0, 5.0, 6.0], {"category": "B"})

    with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
        tmp_path = tmp_file.name

    try:
        # Save to disk
        store.save(tmp_path)

        # Load from disk
        loaded_store = SimpleVectorStore.load(tmp_path)

        # Verify dimension
        assert loaded_store.dimension == store.dimension

        # Verify size
        assert loaded_store.size() == store.size()

        # Verify individual records
        doc1 = loaded_store.get("doc1")
        assert doc1 is not None
        assert doc1.vector == [1.0, 2.0, 3.0]
        assert doc1.metadata == {"category": "A"}

        doc2 = loaded_store.get("doc2")
        assert doc2 is not None
        assert doc2.vector == [4.0, 5.0, 6.0]
        assert doc2.metadata == {"category": "B"}

        # Search against loaded store
        res = loaded_store.search([1.0, 2.0, 3.0], top_k=1)
        assert res[0][0] == "doc1"

    finally:
        os.remove(tmp_path)

def test_empty_or_mismatch_dimension_handling():
    """Test handling of empty index or mismatch dimension vectors."""
    store = SimpleVectorStore(dimension=3)

    # Mismatch dimension on insert
    with pytest.raises(ValueError, match="dimensions"):
        store.insert("doc1", [1.0, 2.0], {}) # 2 dims instead of 3

    with pytest.raises(ValueError, match="dimensions"):
        store.insert("doc1", [1.0, 2.0, 3.0, 4.0], {}) # 4 dims instead of 3

    # Search on empty store
    res = store.search([1.0, 1.0, 1.0])
    assert len(res) == 0

    # Mismatch dimension on search
    with pytest.raises(ValueError, match="dimensions"):
        store.search([1.0, 2.0]) # 2 dims

    store.insert("doc1", [1.0, 1.0, 1.0], {})

    # Duplicate ID insert
    with pytest.raises(ValueError, match="already exists"):
        store.insert("doc1", [0.0, 0.0, 0.0], {})
