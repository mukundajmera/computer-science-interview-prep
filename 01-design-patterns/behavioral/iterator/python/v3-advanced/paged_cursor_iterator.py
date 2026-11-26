"""v3-advanced: Paged Cursor-Based Streaming Iterator.

Encapsulates lazy, chunked remote API prefetching behind Python's native iterator protocol,
providing bounded memory streaming for massive result sets.
"""
from typing import Callable, Generic, List, Optional, TypeVar

T = TypeVar("T")


class Page(Generic[T]):
    def __init__(self, items: List[T], next_cursor: Optional[str]) -> None:
        self.items: List[T] = list(items)
        self.next_cursor: Optional[str] = next_cursor

    @property
    def has_next(self) -> bool:
        return bool(self.next_cursor)


class PagedCursorIterator(Generic[T]):
    """Streams items one-by-one while batching requests behind the scenes."""

    def __init__(self, fetcher: Callable[[Optional[str], int], Page[T]], page_size: int = 10) -> None:
        if page_size <= 0:
            raise ValueError("Page size must be positive")
        self._fetcher = fetcher
        self._page_size = page_size
        self._cursor: Optional[str] = None
        self._buffer: List[T] = []
        self._buffer_idx: int = 0
        self._is_exhausted: bool = False

    def __iter__(self) -> "PagedCursorIterator[T]":
        return self

    def _ensure_buffered(self) -> None:
        if self._buffer_idx < len(self._buffer):
            return
        if self._is_exhausted:
            return

        page = self._fetcher(self._cursor, self._page_size)
        if not page or not page.items:
            self._is_exhausted = True
            return

        self._buffer = page.items
        self._buffer_idx = 0
        self._cursor = page.next_cursor
        if not page.has_next:
            self._is_exhausted = True

    def __next__(self) -> T:
        self._ensure_buffered()
        if self._buffer_idx >= len(self._buffer):
            raise StopIteration
        item = self._buffer[self._buffer_idx]
        self._buffer_idx += 1
        return item
