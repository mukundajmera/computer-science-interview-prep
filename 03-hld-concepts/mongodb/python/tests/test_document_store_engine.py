import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'v1-simple')))
from document_store_engine import DocumentStoreEngine

@pytest.fixture
def engine():
    return DocumentStoreEngine()

def test_insert_and_simple_query(engine):
    coll = "test_coll"
    engine.insert(coll, {"name": "Alice", "age": 25})
    engine.insert(coll, {"name": "Bob", "age": 30})

    results = engine.find(coll, {"name": "Alice"})
    assert len(results) == 1
    assert results[0]["name"] == "Alice"
    assert results[0]["age"] == 25
    assert "_id" in results[0]

def test_query_operators(engine):
    coll = "test_coll"
    engine.insert(coll, {"name": "A", "score": 10})
    engine.insert(coll, {"name": "B", "score": 20})
    engine.insert(coll, {"name": "C", "score": 30})

    # Test $gt
    gt_results = engine.find(coll, {"score": {"$gt": 15}})
    assert len(gt_results) == 2

    # Test $in
    in_results = engine.find(coll, {"name": {"$in": ["A", "C"]}})
    assert len(in_results) == 2

    # Test $elemMatch
    engine.insert(coll, {"name": "D", "tags": [{"k": "v1"}, {"k": "v2"}]})
    elem_match_results = engine.find(coll, {"tags": {"$elemMatch": {"k": "v2"}}})
    assert len(elem_match_results) == 1
    assert elem_match_results[0]["name"] == "D"

def test_projection(engine):
    coll = "test_coll"
    engine.insert(coll, {"name": "Alice", "age": 25, "city": "NY"})

    # Inclusion projection
    results_include = engine.find(coll, {"name": "Alice"}, {"name": 1, "_id": 0})
    assert len(results_include) == 1
    assert "name" in results_include[0]
    assert "age" not in results_include[0]
    assert "city" not in results_include[0]
    assert "_id" not in results_include[0]

    # Exclusion projection
    results_exclude = engine.find(coll, {"name": "Alice"}, {"age": 0})
    assert len(results_exclude) == 1
    assert "name" in results_exclude[0]
    assert "age" not in results_exclude[0]
    assert "city" in results_exclude[0]
    assert "_id" in results_exclude[0]

def test_secondary_index(engine):
    coll = "test_coll"
    engine.create_index(coll, "age")

    engine.insert(coll, {"name": "A", "age": 20})
    engine.insert(coll, {"name": "B", "age": 30})

    # Indexed query ($eq is implicit)
    results = engine.find(coll, {"age": 30})
    assert len(results) == 1
    assert results[0]["name"] == "B"

    # Add document after index creation
    engine.insert(coll, {"name": "C", "age": 30})
    results_after = engine.find(coll, {"age": 30})
    assert len(results_after) == 2
