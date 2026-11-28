import importlib.util
import os
import sys
import threading

import pytest

# Insert the versioned module to python path using absolute path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'v2-extended')))

from vector_store_v2 import InMemoryVectorStore, cosine_similarity, VectorEntry


def load_v1():
    """Loads the v1 module under a distinct sys.modules key for parity probes."""
    module_path = os.path.abspath(os.path.join(
        os.path.dirname(__file__), '..', 'v1-basic', 'vector_store.py'))
    spec = importlib.util.spec_from_file_location("vector_store_v1", module_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules["vector_store_v1"] = module
    spec.loader.exec_module(module)
    return module


def build_chain_store():
    """Entry A -- X -- Z graph where X is a greedy dead end for query [1, 0]."""
    store = InMemoryVectorStore(dimension=2, M=2)
    store.add_vector("A", [0.98, 0.02], {})
    store.add_vector("X", [0.7, 0.3], {})
    store.add_vector("Z", [0.99, 0.01], {})
    # White-box: force the exact chain topology under test.
    store.graph["A"] = ["X"]
    store.graph["X"] = ["A", "Z"]
    store.graph["Z"] = ["X"]
    store.entry_point = "A"
    return store


def test_cosine_similarity_parity():
    v1 = [1.0, 0.0]
    v2 = [0.0, 1.0]
    v3 = [2.0, 0.0]
    assert abs(cosine_similarity(v1, v2)) < 1e-6
    assert abs(cosine_similarity(v1, v3) - 1.0) < 1e-6
    assert cosine_similarity(v1, [0.0, 0.0]) == 0.0
    with pytest.raises(ValueError, match="Dimensions do not match"):
        cosine_similarity([1.0, 0.0], [1.0, 0.0, 0.0])


def test_add_query_filter_dimension_parity():
    store = InMemoryVectorStore(dimension=2)
    store.add_vector("1", [1.0, 0.0], {"type": "A", "color": "red"})
    store.add_vector("2", [1.0, 0.0], {"type": "B", "color": "blue"})
    store.add_vector("3", [0.0, 1.0], {"type": "A", "color": "blue"})

    results = store.query_similarity([1.0, 0.0], top_k=5, filter_meta={"type": "A"})
    assert set(res[0].id for res in results) == {"1", "3"}

    with pytest.raises(ValueError, match="Vector dimension must be 2"):
        store.add_vector("4", [1.0, 0.0, 0.0], {})
    with pytest.raises(ValueError, match="Query vector dimension must be 2"):
        store.query_similarity([1.0], top_k=1)


def test_v1_v2_behavioral_parity_without_deletes():
    v1 = load_v1()
    fixture = [
        ("1", [1.0, 0.0], {"type": "A"}),
        ("2", [0.9, 0.1], {"type": "B"}),
        ("3", [0.0, 1.0], {"type": "A"}),
        ("4", [0.1, 0.9], {"type": "B"}),
    ]
    old = v1.InMemoryVectorStore(dimension=2, M=2)
    new = InMemoryVectorStore(dimension=2, M=2)
    for vid, vec, meta in fixture:
        old.add_vector(vid, vec, meta)
        new.add_vector(vid, vec, meta)

    assert old.graph == new.graph
    assert old.entry_point == new.entry_point

    exact_old = [e.id for e, _ in old.query_similarity([1.0, 0.0], top_k=3)]
    exact_new = [e.id for e, _ in new.query_similarity([1.0, 0.0], top_k=3)]
    assert exact_old == exact_new

    approx_old = [e.id for e, _ in old.approximate_search([1.0, 0.0], top_k=3)]
    approx_new = [e.id for e, _ in new.approximate_search([1.0, 0.0], top_k=3)]
    assert approx_old == approx_new


def test_graph_healing_preserves_reachability_and_recall():
    # The documented PITFALLS-1 counterexample: B is the only bridge A <-> C.
    # (M=2 so links form: with M=1 the insertion scan's top-1 is always the
    # vector itself and the graph stays empty, in v1 as well.)
    store = InMemoryVectorStore(dimension=2, M=2)
    store.add_vector("A", [1.0, 0.0], {})
    store.add_vector("B", [1.0, 0.1], {})
    store.add_vector("C", [1.0, 0.2], {})
    assert store.graph["C"] == ["B"]  # C hangs off B only

    assert store.delete_vector("B") is True

    # Healed: A and C are re-linked, no partition, capacity respected.
    assert "C" in store.graph["A"]
    assert "A" in store.graph["C"]
    assert all(len(neighbors) <= store.M for neighbors in store.graph.values())

    results = store.approximate_search([1.0, 0.2], top_k=1)
    assert results[0][0].id == "C"


def test_delete_cleans_dangling_references():
    # Asymmetric links leave a dangling reference to the deleted id in v1
    # (a node whose back-link was blocked by the M cap); v2 scrubs every list.
    store = InMemoryVectorStore(dimension=2, M=2)
    store.add_vector("A", [1.0, 0.0], {})
    store.add_vector("B", [1.0, 0.1], {})
    store.add_vector("C", [1.0, 0.2], {})
    # White-box: make the C -> B link one-way, as a capped back-link would.
    store.graph["B"] = ["A"]

    store.delete_vector("B")

    for node_id, neighbors in store.graph.items():
        for neighbor in neighbors:
            assert neighbor in store.vectors, "dangling reference to deleted id"
    # The walk must not raise on the healed graph.
    results = store.approximate_search([1.0, 0.0], top_k=2)
    assert {entry.id for entry, _ in results} == {"A", "C"}


def test_ef_search_escapes_greedy_local_optimum():
    # Chain A - X - Z, query [1, 0]: sim(A)=0.9998, sim(Z)=0.9998+ (true
    # nearest), but sim(X)=0.9191 so the v1 pruning rule never expands X.
    store = build_chain_store()

    default_results = store.approximate_search([1.0, 0.0], top_k=1)
    assert [e.id for e, _ in default_results] == ["A"]  # v1 parity by default

    v1 = load_v1()
    old = v1.InMemoryVectorStore(dimension=2, M=2)
    old.add_vector("A", [0.98, 0.02], {})
    old.add_vector("X", [0.7, 0.3], {})
    old.add_vector("Z", [0.99, 0.01], {})
    old.graph["A"] = ["X"]
    old.graph["X"] = ["A", "Z"]
    old.graph["Z"] = ["X"]
    old.entry_point = "A"
    assert [e.id for e, _ in old.approximate_search([1.0, 0.0], top_k=1)] == ["A"]

    widened = store.approximate_search([1.0, 0.0], top_k=1, ef_search=10)
    assert [e.id for e, _ in widened] == ["Z"]


def test_strict_recall_falls_back_to_exact_scan():
    store = InMemoryVectorStore(dimension=2)
    store.add_vector("A", [1.0, 0.0], {"tag": "x"})
    store.add_vector("B", [0.0, 1.0], {"tag": "y"})
    store.add_vector("C", [0.1, 1.0], {"tag": "y"})
    # White-box: fully disconnected components, entry in the non-matching one.
    store.graph["A"] = []
    store.graph["B"] = []
    store.graph["C"] = []
    store.entry_point = "A"

    plain = store.approximate_search([0.0, 1.0], top_k=2, filter_meta={"tag": "y"})
    assert plain == []

    strict = store.approximate_search([0.0, 1.0], top_k=2, filter_meta={"tag": "y"},
                                      strict_recall=True)
    assert {entry.id for entry, _ in strict} == {"B", "C"}
    assert strict[0][0].id == "B"  # exact nearest first


def test_thread_safe_concurrent_adds():
    store = InMemoryVectorStore(dimension=2, M=3)

    def worker(tag):
        for i in range(25):
            store.add_vector("t%d-%d" % (tag, i), [float(i % 7), 1.0], {"t": tag})

    threads = [threading.Thread(target=worker, args=(t,)) for t in range(4)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    assert len(store.vectors) == 100
    for node_id, neighbors in store.graph.items():
        assert node_id in store.vectors
        for neighbor in neighbors:
            assert neighbor in store.vectors
    results = store.query_similarity([1.0, 1.0], top_k=5)
    assert len(results) == 5


def test_constructor_validation_and_clean_replacement():
    with pytest.raises(ValueError, match="dimension must be a positive integer"):
        InMemoryVectorStore(dimension=0)
    with pytest.raises(ValueError, match="M must be a positive integer"):
        InMemoryVectorStore(dimension=2, M=0)

    store = InMemoryVectorStore(dimension=2, M=2)
    store.add_vector("A", [1.0, 0.0], {})
    store.add_vector("B", [1.0, 0.1], {})
    # Re-adding an existing id replaces it cleanly (v1 duplicated the links).
    store.add_vector("A", [0.0, 1.0], {})
    assert store.graph["B"].count("A") == 1
    assert store.vectors["A"].vector == [0.0, 1.0]


def test_ef_search_must_be_positive():
    store = build_chain_store()
    with pytest.raises(ValueError, match="ef_search must be a positive integer"):
        store.approximate_search([1.0, 0.0], top_k=1, ef_search=0)


def test_entry_point_and_empty_store_edges():
    store = InMemoryVectorStore(dimension=2)
    assert store.approximate_search([1.0, 0.0]) == []
    assert store.delete_vector("missing") is False

    store.add_vector("A", [1.0, 0.0], {})
    store.add_vector("B", [0.0, 1.0], {})
    assert store.entry_point == "A"
    store.delete_vector("A")
    assert store.entry_point == "B"
    store.delete_vector("B")
    assert store.entry_point is None
    assert store.approximate_search([1.0, 0.0]) == []
