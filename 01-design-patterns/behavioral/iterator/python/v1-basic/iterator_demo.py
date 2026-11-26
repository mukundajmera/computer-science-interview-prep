"""
Iterator Pattern - Custom Collection

Python has built-in iterator support via __iter__ and __next__
"""
from typing import TypeVar, Generic, List, Iterator as TypingIterator
from collections.abc import Iterator, Iterable

import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')


T = TypeVar('T')


# Custom Iterator
class BookIterator(Iterator[str]):
    def __init__(self, books: List[str]):
        self._books = books
        self._index = 0
    
    def __next__(self) -> str:
        if self._index < len(self._books):
            book = self._books[self._index]
            self._index += 1
            return book
        raise StopIteration


# Custom Collection
class BookCollection(Iterable[str]):
    def __init__(self):
        self._books: List[str] = []
    
    def add_book(self, book: str) -> None:
        self._books.append(book)
    
    def __iter__(self) -> BookIterator:
        return BookIterator(self._books.copy())
    
    def reverse_iterator(self) -> TypingIterator[str]:
        """Return a reverse iterator"""
        return iter(reversed(self._books))


# Generator-based iterator (Pythonic)
def filtered_books(collection: BookCollection, keyword: str) -> TypingIterator[str]:
    """Generator that filters books by keyword"""
    for book in collection:
        if keyword.lower() in book.lower():
            yield book


if __name__ == "__main__":
    collection = BookCollection()
    collection.add_book("Design Patterns")
    collection.add_book("Clean Code")
    collection.add_book("Refactoring")
    
    print("=== Forward Iteration ===")
    for book in collection:
        print(f"{book}")
    
    print("\n=== Reverse Iteration ===")
    for book in collection.reverse_iterator():
        print(f"{book}")
    
    print("\n=== Filtered Iteration ===")
    for book in filtered_books(collection, "code"):
        print(f"{book}")
