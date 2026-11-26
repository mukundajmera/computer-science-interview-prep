"""
Tests for Library Management System
"""
import unittest
import sys
import threading
from pathlib import Path


TEST_DIR = Path(__file__).resolve().parent
HELPER_DIR = TEST_DIR.parents[2] / "test_helpers"
if str(HELPER_DIR) not in sys.path:
    sys.path.insert(0, str(HELPER_DIR))

from imports import import_modules_from


LIBRARY_MODULES = ["library", "library_demo", "library_demo_new"]


def version_path(version: str) -> Path:
    return TEST_DIR.parent / version


def library_demo(version: str):
    return import_modules_from(
        version_path(version),
        ["library_demo"],
        purge_modules=LIBRARY_MODULES,
    )["library_demo"]


class TestLibraryBasic(unittest.TestCase):
    """Tests for V1 Basic Library"""
    
    def setUp(self):
        self.lib_module = library_demo("v1-basic")
        self.lib_module.Library.reset_instance()
    
    def tearDown(self):
        self.lib_module.Library.reset_instance()
    
    def test_singleton(self):
        """Library should be a singleton"""
        Library = self.lib_module.Library
        lib1 = Library.get_instance()
        lib2 = Library.get_instance()
        self.assertIs(lib1, lib2)
    
    def test_add_book(self):
        """Should add book to library"""
        Library = self.lib_module.Library
        Book = self.lib_module.Book
        BookCategory = self.lib_module.BookCategory
        library = Library.get_instance()
        book = Book("978-0-13-468599-1", "Clean Code", "Robert Martin", 
                   BookCategory.TECHNOLOGY, 2008)
        library.add_book(book)
        self.assertEqual(library.book_count, 1)
        self.assertIsNotNone(library.get_book("978-0-13-468599-1"))
    
    def test_add_copies(self):
        """Should add copies to book"""
        Book = self.lib_module.Book
        BookCategory = self.lib_module.BookCategory
        book = Book("ISBN-1", "Test", "Author", BookCategory.FICTION, 2020)
        book.add_copy()
        book.add_copy()
        book.add_copy()
        self.assertEqual(book.total_copies, 3)
    
    def test_register_member(self):
        """Should register member"""
        Library = self.lib_module.Library
        Member = self.lib_module.Member
        MemberType = self.lib_module.MemberType
        library = Library.get_instance()
        member = Member("M001", "John Doe", "john@email.com", MemberType.STUDENT)
        library.register_member(member)
        self.assertEqual(library.member_count, 1)
    
    def test_issue_book(self):
        """Should issue book to member"""
        Library = self.lib_module.Library
        Book = self.lib_module.Book
        BookCategory = self.lib_module.BookCategory
        Member = self.lib_module.Member
        MemberType = self.lib_module.MemberType
        library = Library.get_instance()
        
        book = Book("ISBN-1", "Test", "Author", BookCategory.FICTION, 2020)
        copy = book.add_copy()
        library.add_book(book)
        
        member = Member("M001", "John", "j@email.com", MemberType.STUDENT)
        library.register_member(member)
        
        record = library.issue_book("M001", copy.copy_id)
        self.assertIsNotNone(record)
        self.assertFalse(copy.is_available)
    
    def test_borrowing_limit(self):
        """Should enforce borrowing limit"""
        Library = self.lib_module.Library
        Book = self.lib_module.Book
        BookCategory = self.lib_module.BookCategory
        Member = self.lib_module.Member
        MemberType = self.lib_module.MemberType
        library = Library.get_instance()
        
        book = Book("ISBN-1", "Test", "Author", BookCategory.FICTION, 2020)
        for _ in range(5):
            book.add_copy()
        library.add_book(book)
        
        member = Member("M001", "John", "j@email.com", MemberType.STUDENT)  # Limit: 3
        library.register_member(member)
        
        # Borrow 3 books
        for i in range(3):
            record = library.issue_book("M001", book.copies[i].copy_id)
            self.assertIsNotNone(record)
        
        # 4th should fail
        record = library.issue_book("M001", book.copies[3].copy_id)
        self.assertIsNone(record)
    
    def test_return_book(self):
        """Should return book and calculate fine"""
        Library = self.lib_module.Library
        Book = self.lib_module.Book
        BookCategory = self.lib_module.BookCategory
        Member = self.lib_module.Member
        MemberType = self.lib_module.MemberType
        library = Library.get_instance()
        
        book = Book("ISBN-1", "Test", "Author", BookCategory.FICTION, 2020)
        copy = book.add_copy()
        library.add_book(book)
        
        member = Member("M001", "John", "j@email.com", MemberType.STUDENT)
        library.register_member(member)
        
        record = library.issue_book("M001", copy.copy_id)
        fine = library.return_book(record.record_id)
        
        self.assertEqual(fine, 0)  # No overdue
        self.assertTrue(copy.is_available)
    
    def test_search_by_title(self):
        """Should search books by title"""
        Library = self.lib_module.Library
        Book = self.lib_module.Book
        BookCategory = self.lib_module.BookCategory
        library = Library.get_instance()
        
        library.add_book(Book("ISBN-1", "Clean Code", "Martin", BookCategory.TECHNOLOGY, 2008))
        library.add_book(Book("ISBN-2", "Clean Architecture", "Martin", BookCategory.TECHNOLOGY, 2017))
        library.add_book(Book("ISBN-3", "1984", "Orwell", BookCategory.FICTION, 1949))
        
        results = library.search_by_title("clean")
        self.assertEqual(len(results), 2)
    
    def test_search_by_author(self):
        """Should search books by author"""
        Library = self.lib_module.Library
        Book = self.lib_module.Book
        BookCategory = self.lib_module.BookCategory
        library = Library.get_instance()
        
        library.add_book(Book("ISBN-1", "Clean Code", "Robert Martin", BookCategory.TECHNOLOGY, 2008))
        library.add_book(Book("ISBN-2", "Clean Architecture", "Robert Martin", BookCategory.TECHNOLOGY, 2017))
        library.add_book(Book("ISBN-3", "1984", "George Orwell", BookCategory.FICTION, 1949))
        
        results = library.search_by_author("Martin")
        self.assertEqual(len(results), 2)


class TestLibraryConcurrent(unittest.TestCase):
    """Tests for V3 Concurrent Library"""
    
    def test_concurrent_borrowing(self):
        """Multiple threads should be able to borrow concurrently"""
        lib_module = library_demo("v3-optimized")
        
        lib_module.Library.reset_instance()
        library = lib_module.Library.get_instance()
        
        book = lib_module.Book("ISBN-1", "Test", "Author", lib_module.BookCategory.TECHNOLOGY, 2024)
        for _ in range(30):
            book.add_copy()
        library.add_book(book)
        
        for i in range(10):
            library.register_member(lib_module.Member(f"M{i:03d}", f"Member {i}", 
                                                      f"m{i}@email.com", lib_module.MemberType.STUDENT))
        
        records = []
        lock = threading.Lock()
        
        def borrow_worker(thread_id):
            for i in range(3):
                record = library.issue_book(f"M{thread_id:03d}", f"ISBN-1-{thread_id * 3 + i + 1:03d}")
                if record:
                    with lock:
                        records.append(record)
        
        threads = []
        for t in range(10):
            thread = threading.Thread(target=borrow_worker, args=(t,))
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        # All 30 loans should succeed (10 threads x 3 books each)
        self.assertEqual(len(records), 30)
        self.assertEqual(library.active_loan_count, 30)
        
        lib_module.Library.reset_instance()


if __name__ == "__main__":
    unittest.main()
