import os
import sys
from pathlib import Path
import importlib.util
import pytest

PATTERN_DIR = Path(__file__).resolve().parents[2]


def load_module(name: str, rel_path: str):
    spec = importlib.util.spec_from_file_location(name, PATTERN_DIR / rel_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


it_v1 = load_module("it_v1", "python/v1-basic/iterator_demo.py")
tree_it = load_module("tree_it", "python/v2-variant/tree_iterator.py")
cursor_it = load_module("cursor_it", "python/v3-advanced/paged_cursor_iterator.py")


def test_book_iteration():
    collection = it_v1.BookCollection()
    collection.add_book("Book A")
    collection.add_book("Book B")

    items = list(collection)
    assert items == ["Book A", "Book B"]


def test_reverse_iterator():
    collection = it_v1.BookCollection()
    collection.add_book("Alpha")
    collection.add_book("Beta")
    collection.add_book("Gamma")

    reverse_items = list(collection.reverse_iterator())
    assert reverse_items == ["Gamma", "Beta", "Alpha"]


def test_filtered_books_generator():
    collection = it_v1.BookCollection()
    collection.add_book("Design Patterns in Java")
    collection.add_book("Clean Architecture")
    collection.add_book("Patterns of Enterprise Software")

    filtered = list(it_v1.filtered_books(collection, "patterns"))
    assert len(filtered) == 2
    assert "Design Patterns in Java" in filtered
    assert "Patterns of Enterprise Software" in filtered


# --- v2-variant Tests ---

def test_tree_iterator_dfs_and_bfs_traversals():
    root = tree_it.TreeNode("A")
    b = tree_it.TreeNode("B")
    c = tree_it.TreeNode("C")
    root.add_child(b).add_child(c)
    d = tree_it.TreeNode("D")
    e = tree_it.TreeNode("E")
    b.add_child(d).add_child(e)

    # DFS (Pre-Order): A -> B -> D -> E -> C
    dfs_names = [node.name for node in root.dfs_iterator()]
    assert dfs_names == ["A", "B", "D", "E", "C"]

    # BFS (Level-Order): A -> B -> C -> D -> E
    bfs_names = [node.name for node in root.bfs_iterator()]
    assert bfs_names == ["A", "B", "C", "D", "E"]


# --- v3-advanced Tests ---

def test_paged_cursor_iterator_streams_seamlessly():
    # Mock database/API with 7 items across page_size 3
    all_data = [f"Item-{i}" for i in range(7)]

    def mock_fetcher(cursor, page_size):
        start = int(cursor) if cursor else 0
        if start >= len(all_data):
            return cursor_it.Page([], None)
        end = min(start + page_size, len(all_data))
        next_c = str(end) if end < len(all_data) else None
        return cursor_it.Page(all_data[start:end], next_c)

    stream = cursor_it.PagedCursorIterator(mock_fetcher, page_size=3)
    streamed_items = list(stream)

    assert streamed_items == all_data
    assert len(streamed_items) == 7
