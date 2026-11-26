"""Library Management Models."""
from datetime import date
from typing import List, Optional


class Book:
    def __init__(self, isbn: str, title: str, author: str):
        from enums import BookStatus
        self.isbn = isbn
        self.title = title
        self.author = author
        self.status = BookStatus.AVAILABLE
    
    def __str__(self): return f"Book[{self.isbn}: {self.title} by {self.author}]"


class Loan:
    DAILY_FINE = 0.50
    
    def __init__(self, loan_id: str, book: 'Book', member: 'Member'):
        self.loan_id = loan_id
        self.book = book
        self.member = member
        self.borrow_date = date.today()
        self.due_date = date.today()  # Set by member type
        self.return_date: Optional[date] = None
    
    def return_book(self):
        self.return_date = date.today()
    
    def calculate_fine(self) -> float:
        check = self.return_date or date.today()
        days_late = (check - self.due_date).days
        return max(0, days_late * self.DAILY_FINE)
    
    def __str__(self): return f"Loan[{self.loan_id}: {self.book.title}]"


class Member:
    def __init__(self, member_id: str, name: str, member_type):
        self.member_id = member_id
        self.name = name
        self.member_type = member_type
        self._active_loans: List[Loan] = []
    
    def can_borrow(self) -> bool:
        return len(self._active_loans) < self.member_type.borrow_limit
    
    def add_loan(self, loan: Loan): self._active_loans.append(loan)
    def remove_loan(self, loan: Loan): self._active_loans.remove(loan)
    
    def __str__(self): return f"Member[{self.member_id}: {self.name}]"
