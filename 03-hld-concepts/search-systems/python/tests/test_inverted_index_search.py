import os
import sys

# Support dynamic sys.path for test execution from repo root
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'v1-simple')))

from inverted_index_search import InvertedIndexSearch

def test_single_term_search():
    search_engine = InvertedIndexSearch()
    search_engine.add_document(1, "The quick brown fox jumps over the lazy dog.")
    search_engine.add_document(2, "Fast foxes run quickly.")

    # "fox" should match doc 1
    results = search_engine.search("fox")
    assert len(results) == 1
    assert results[0][0] == 1

def test_multiple_term_or_search():
    search_engine = InvertedIndexSearch()
    search_engine.add_document(1, "The quick brown fox")
    search_engine.add_document(2, "The lazy dog")
    search_engine.add_document(3, "Quick brown dogs")

    # "quick dog" OR search should match doc 1 (quick), doc 2 (dog), doc 3 (quick)
    # wait, doc 2 has "dog", doc 3 has "dogs" but no stemming in simple version
    results = search_engine.search("quick dog", operator="OR")
    docs = [doc_id for doc_id, _ in results]
    assert 1 in docs
    assert 2 in docs
    assert 3 in docs

def test_multiple_term_and_search():
    search_engine = InvertedIndexSearch()
    search_engine.add_document(1, "The quick brown fox")
    search_engine.add_document(2, "The lazy dog")
    search_engine.add_document(3, "Quick brown dogs")

    # "quick brown" AND search should match doc 1 and doc 3
    results = search_engine.search("quick brown", operator="AND")
    assert len(results) == 2
    docs = [doc_id for doc_id, _ in results]
    assert 1 in docs
    assert 3 in docs

def test_tf_idf_scoring_ranking():
    search_engine = InvertedIndexSearch()
    search_engine.add_document(1, "Machine learning is a subset of AI. Machine learning is great.")
    search_engine.add_document(2, "Introduction to databases and machine systems.")
    search_engine.add_document(3, "Learning how to bake a cake.")

    # Search for "machine learning"
    results = search_engine.search("machine learning")

    # doc 1 should have highest score because it has "machine" (twice) and "learning" (twice) in a short doc
    assert len(results) == 3
    # top result should be doc 1
    assert results[0][0] == 1
    # doc 3 only has learning
    # doc 2 only has machine
    # We just ensure it runs and sorts properly.
    assert results[0][1] > results[1][1]
