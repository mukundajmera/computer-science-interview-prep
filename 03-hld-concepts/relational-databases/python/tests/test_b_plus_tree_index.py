import pytest
import sys
import os

# Add to sys.path to resolve imports correctly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'v1-simple')))

from b_plus_tree_index import BPlusTreeIndex

def test_insert_and_search():
    tree = BPlusTreeIndex(order=4)
    tree.insert(10, "A")
    tree.insert(20, "B")
    tree.insert(5, "C")

    assert tree.search(10) == "A"
    assert tree.search(20) == "B"
    assert tree.search(5) == "C"
    assert tree.search(15) is None

def test_update_existing_key():
    tree = BPlusTreeIndex(order=3)
    tree.insert(1, "Old")
    tree.insert(1, "New")

    assert tree.search(1) == "New"

def test_node_split():
    tree = BPlusTreeIndex(order=3)
    for i in range(1, 11):
        tree.insert(i, f"Val_{i}")

    for i in range(1, 11):
        assert tree.search(i) == f"Val_{i}"

def test_range_scan():
    tree = BPlusTreeIndex(order=4)
    data = [(10, "A"), (20, "B"), (30, "C"), (40, "D"), (50, "E")]
    for k, v in data:
        tree.insert(k, v)

    res = tree.range_scan(20, 45)
    assert res == [(20, "B"), (30, "C"), (40, "D")]

def test_range_scan_empty():
    tree = BPlusTreeIndex(order=4)
    data = [(10, "A"), (20, "B")]
    for k, v in data:
        tree.insert(k, v)

    res = tree.range_scan(30, 50)
    assert res == []

def test_large_insertions():
    tree = BPlusTreeIndex(order=5)
    for i in range(100):
        tree.insert(i, str(i))
    for i in range(100):
        assert tree.search(i) == str(i)
