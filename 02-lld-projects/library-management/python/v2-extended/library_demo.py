"""
Library Management System - V2 Extended

Complete implementation with Book, BookCopy, Member, and BorrowingRecord.
"""
from abc import ABC, abstractmethod
from datetime import datetime, date, timedelta
from enum import Enum
from typing import Dict, List, Optional
import uuid



# ============ Observer Pattern ============

class Observer(ABC):
    @abstractmethod
    def update(self, event_type: str, data: dict) -> None:
        pass

class Subject(ABC):
    def __init__(self):
        self._observers: List[Observer] = []
        
    def attach(self, observer: Observer) -> None:
        if observer not in self._observers:
            self._observers.append(observer)
            
    def detach(self, observer: Observer) -> None:
        if observer in self._observers:
            self._observers.remove(observer)
            
    def notify(self, event_type: str, data: dict) -> None:
        for observer in self._observers:
            observer.update(event_type, data)


# ============ Enumerations ============

class BookCategory(Enum):
    FICTION = "FICTION"
    NON_FICTION = "NON_FICTION"
    SCIENCE = "SCIENCE"
    TECHNOLOGY = "TECHNOLOGY"
    HISTORY = "HISTORY"
    BIOGRAPHY = "BIOGRAPHY"
    CHILDREN = "CHILDREN"
    REFERENCE = "REFERENCE"


class CopyStatus(Enum):
    AVAILABLE = "AVAILABLE"
    BORROWED = "BORROWED"
    RESERVED = "RESERVED"
    LOST = "LOST"
    UNDER_REPAIR = "UNDER_REPAIR"


class MemberType(Enum):
    STUDENT = ("STUDENT", 3, 14)
    TEACHER = ("TEACHER", 5, 30)
    GENERAL = ("GENERAL", 3, 14)
    
    def __init__(self, name: str, borrow_limit: int, loan_days: int):
        self._name = name
        self._borrow_limit = borrow_limit
        self._loan_days = loan_days
    
    @property
    def borrow_limit(self) -> int:
        return self._borrow_limit
    
    @property
    def loan_days(self) -> int:
        return self._loan_days


# ============ Book Classes ============

class Book(Subject):
    """Represents a book in the library catalog."""
    
    def __init__(self, isbn: str, title: str, author: str, 
                 category: BookCategory, publication_year: int):
        super().__init__()
        self._isbn = isbn
        self._title = title
        self._author = author
        self._category = category
        self._publication_year = publication_year
        self._copies: List['BookCopy'] = []
    
    def add_copy(self) -> 'BookCopy':
        copy_id = f"{self._isbn}-{len(self._copies) + 1:03d}"
        copy = BookCopy(copy_id, self)
        self._copies.append(copy)
        return copy
    
    def get_available_copies(self) -> List['BookCopy']:
        return [c for c in self._copies if c.is_available]
    
    def has_available_copy(self) -> bool:
        return len(self.get_available_copies()) > 0
    
    def get_copy(self, copy_id: str) -> Optional['BookCopy']:
        for copy in self._copies:
            if copy.copy_id == copy_id:
                return copy
        return None
    
    @property
    def isbn(self) -> str:
        return self._isbn
    
    @property
    def title(self) -> str:
        return self._title
    
    @property
    def author(self) -> str:
        return self._author
    
    @property
    def category(self) -> BookCategory:
        return self._category
    
    @property
    def copies(self) -> List['BookCopy']:
        return self._copies.copy()
    
    @property
    def total_copies(self) -> int:
        return len(self._copies)
    
    def __str__(self) -> str:
        avail = len(self.get_available_copies())
        return f'Book[{self._isbn}, "{self._title}" by {self._author}, {avail}/{len(self._copies)} available]'


class BookCopy:
    """Represents a physical copy of a book."""
    
    def __init__(self, copy_id: str, book: Book):
        self._copy_id = copy_id
        self._book = book
        self._status = CopyStatus.AVAILABLE
        self._rack_location = "Rack-A1"
    
    def borrow(self) -> bool:
        if self._status != CopyStatus.AVAILABLE:
            return False
        self._status = CopyStatus.BORROWED
        return True
    
    def return_book(self) -> None:
        self._status = CopyStatus.AVAILABLE
    
    @property
    def is_available(self) -> bool:
        return self._status == CopyStatus.AVAILABLE
    
    def mark_lost(self) -> None:
        self._status = CopyStatus.LOST
    
    @property
    def copy_id(self) -> str:
        return self._copy_id
    
    @property
    def book(self) -> Book:
        return self._book
    
    @property
    def status(self) -> CopyStatus:
        return self._status
    
    def __str__(self) -> str:
        return f"Copy[{self._copy_id}, {self._status.value}]"


# ============ Member Class ============

class Member(Observer):
    """Represents a library member."""
    
    def __init__(self, member_id: str, name: str, email: str, member_type: MemberType):
        self._member_id = member_id
        self._name = name
        self._email = email
        self._member_type = member_type
        self._registration_date = date.today()
        self._borrowed_records: List['BorrowingRecord'] = []
        
    def update(self, event_type: str, data: dict) -> None:
        if event_type == "BOOK_AVAILABLE":
            print(f"Notification to {self._name}: Book '{data.get('book_title')}' is now available!")
        elif event_type == "MEMBERSHIP_RENEWAL":
            print(f"Notification to {self._name}: Your membership is up for renewal on {data.get('renewal_date')}.")
    def can_borrow(self) -> bool:
        return self.active_borrowed_count < self._member_type.borrow_limit
    
    @property
    def active_borrowed_count(self) -> int:
        return sum(1 for r in self._borrowed_records if not r.is_returned)
    
    def add_borrowing_record(self, record: 'BorrowingRecord') -> None:
        self._borrowed_records.append(record)
    
    @property
    def member_id(self) -> str:
        return self._member_id
    
    @property
    def name(self) -> str:
        return self._name
    
    @property
    def email(self) -> str:
        return self._email
    
    @property
    def member_type(self) -> MemberType:
        return self._member_type
    
    @property
    def borrow_limit(self) -> int:
        return self._member_type.borrow_limit
    
    @property
    def loan_days(self) -> int:
        return self._member_type.loan_days
    
    def __str__(self) -> str:
        return f"Member[{self._member_id}, {self._name}, {self._member_type.name}, {self.active_borrowed_count}/{self.borrow_limit} borrowed]"


# ============ Borrowing Record ============

class BorrowingRecord:
    """Represents a borrowing transaction."""
    
    def __init__(self, member: Member, book_copy: BookCopy):
        self._record_id = f"BR-{uuid.uuid4().hex[:8].upper()}"
        self._member = member
        self._book_copy = book_copy
        self._issue_date = date.today()
        self._due_date = self._issue_date + timedelta(days=member.loan_days)
        self._return_date: Optional[date] = None
        self._fine_amount = 0.0
    
    @property
    def is_overdue(self) -> bool:
        end_date = self._return_date or date.today()
        return end_date > self._due_date
    
    @property
    def days_overdue(self) -> int:
        if not self.is_overdue:
            return 0
        end_date = self._return_date or date.today()
        return (end_date - self._due_date).days
    
    @property
    def is_returned(self) -> bool:
        return self._return_date is not None
    
    def process_return(self, fine_per_day: float = 1.0) -> float:
        self._return_date = date.today()
        if self.is_overdue:
            self._fine_amount = self.days_overdue * fine_per_day
        return self._fine_amount
    
    @property
    def record_id(self) -> str:
        return self._record_id
    
    @property
    def member(self) -> Member:
        return self._member
    
    @property
    def book_copy(self) -> BookCopy:
        return self._book_copy
    
    @property
    def due_date(self) -> date:
        return self._due_date
    
    @property
    def fine_amount(self) -> float:
        return self._fine_amount
    
    def __str__(self) -> str:
        status = "Returned" if self.is_returned else ("Overdue" if self.is_overdue else "Active")
        return f"Record[{self._record_id}, {self._member.name}, {self._book_copy.book.title}, Due: {self._due_date}, {status}]"


# ============ Library (Singleton) ============

class Library:
    """Library management system using Singleton pattern."""
    
    _instance: Optional['Library'] = None
    
    def __new__(cls, name: str = "Main Library"):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self, name: str = "Main Library"):
        if self._initialized:
            return
        
        self._name = name
        self._books: Dict[str, Book] = {}
        self._members: Dict[str, Member] = {}
        self._active_records: Dict[str, BorrowingRecord] = {}
        self._initialized = True
    
    @classmethod
    def get_instance(cls, name: str = "Main Library") -> 'Library':
        return cls(name)
    
    @classmethod
    def reset_instance(cls) -> None:
        cls._instance = None
    
    # Book Management
    def add_book(self, book: Book) -> None:
        if book is None or book.isbn is None:
            raise ValueError("Book or ISBN cannot be None")
        self._books[book.isbn] = book
    
    def get_book(self, isbn: str) -> Optional[Book]:
        return self._books.get(isbn)
    
    def remove_book(self, isbn: str) -> bool:
        return self._books.pop(isbn, None) is not None
    
    def search_by_title(self, title: str) -> List[Book]:
        search_term = title.lower()
        return [b for b in self._books.values() if search_term in b.title.lower()]
    
    def search_by_author(self, author: str) -> List[Book]:
        search_term = author.lower()
        return [b for b in self._books.values() if search_term in b.author.lower()]
    
    
    def check_membership_renewals(self) -> None:
        # Simulate checking renewals
        for member in self._members.values():
            # In a real system, we'd check if the registration_date is close to expiration
            # We'll just notify them all for demonstration
            renewal_date = member._registration_date + timedelta(days=365)
            member.update("MEMBERSHIP_RENEWAL", {"renewal_date": renewal_date})
            
    # Member Management
    def register_member(self, member: Member) -> None:
        if member is None or member.member_id is None:
            raise ValueError("Member or ID cannot be None")
        self._members[member.member_id] = member
    
    def get_member(self, member_id: str) -> Optional[Member]:
        return self._members.get(member_id)
    
    def remove_member(self, member_id: str) -> bool:
        return self._members.pop(member_id, None) is not None
    
    # Borrowing Operations
    def issue_book(self, member_id: str, copy_id: str) -> Optional[BorrowingRecord]:
        member = self._members.get(member_id)
        if member is None:
            print(f"Member not found: {member_id}")
            return None
        
        if not member.can_borrow():
            print("Member has reached borrowing limit")
            return None
        
        # Find the book copy
        book_copy = None
        for book in self._books.values():
            book_copy = book.get_copy(copy_id)
            if book_copy:
                break
        
        if book_copy is None:
            print(f"Book copy not found: {copy_id}")
            return None
        
        if not book_copy.is_available:
            print("Book copy is not available")
            return None
        
        if book_copy.borrow():
            record = BorrowingRecord(member, book_copy)
            member.add_borrowing_record(record)
            self._active_records[record.record_id] = record
            print(f"Book issued successfully: {record}")
            return record
        
        return None
    
    def return_book(self, record_id: str) -> float:
        record = self._active_records.get(record_id)
        if record is None:
            print(f"Record not found: {record_id}")
            return -1
        
        if record.is_returned:
            print("Book already returned")
            return 0
        
        fine = record.process_return()
        record.book_copy.return_book()
        del self._active_records[record_id]
        
        print(f"Book returned. Fine: ${fine:.2f}")
        
        # Notify members who might be waiting for this book
        book = record.book_copy.book
        book.notify("BOOK_AVAILABLE", {"book_title": book.title})
        
        return fine

    def display_status(self) -> None:
        print(f"\n=== {self._name} Status ===")
        print(f"Total Books: {len(self._books)}")
        print(f"Total Members: {len(self._members)}")
        print(f"Active Loans: {len(self._active_records)}")
    
    def display_books(self) -> None:
        print("\n--- Book Catalog ---")
        for book in self._books.values():
            print(book)
    
    @property
    def name(self) -> str:
        return self._name
    
    @property
    def book_count(self) -> int:
        return len(self._books)
    
    @property
    def member_count(self) -> int:
        return len(self._members)
    
    @property
    def active_loan_count(self) -> int:
        return len(self._active_records)


# ============ Demo ============

if __name__ == "__main__":
    print("=== Library Management System Demo ===\n")
    
    Library.reset_instance()
    library = Library.get_instance("City Public Library")
    
    # Add books
    book1 = Book("978-0-13-468599-1", "Clean Code", "Robert C. Martin", 
                 BookCategory.TECHNOLOGY, 2008)
    book1.add_copy()
    book1.add_copy()
    
    book2 = Book("978-0-14-028329-7", "1984", "George Orwell", 
                 BookCategory.FICTION, 1949)
    book2.add_copy()
    
    library.add_book(book1)
    library.add_book(book2)
    
    # Register members
    member1 = Member("M001", "John Doe", "john@email.com", MemberType.STUDENT)
    member2 = Member("M002", "Jane Smith", "jane@email.com", MemberType.TEACHER)
    
    library.register_member(member1)
    library.register_member(member2)
    
    library.display_status()
    library.display_books()
    
    # Issue books
    print("\n--- Issuing Books ---")
    record1 = library.issue_book("M001", "978-0-13-468599-1-001")
    record2 = library.issue_book("M002", "978-0-14-028329-7-001")
    
    # Search books
    print("\n--- Searching Books ---")
    results = library.search_by_author("Robert")
    print(f"Found {len(results)} books by 'Robert'")
    
    # Reserve book by attaching member as observer
    book1.attach(member2)
    
    print("\n--- Membership Renewal Check ---")
    library.check_membership_renewals()
    
    # Return book

    print("\n--- Returning Book ---")
    if record1:
        fine = library.return_book(record1.record_id)
    
    library.display_status()
    
    print("\n=== Demo Complete ===")
