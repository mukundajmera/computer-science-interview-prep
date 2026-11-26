"""Library Singleton Controller."""
from typing import Dict, List
from enums import BookStatus
from models import Book, Member, Loan


class Library:
    _instance = None
    _loan_counter = 0
    
    def __new__(cls, name: str = "Library"):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.name = name
            cls._instance.books: Dict[str, Book] = {}
            cls._instance.members: Dict[str, Member] = {}
            cls._instance.loans: Dict[str, Loan] = {}
        return cls._instance
    
    def add_book(self, book: Book): self.books[book.isbn] = book
    def register_member(self, member: Member): self.members[member.member_id] = member
    
    def borrow_book(self, member_id: str, isbn: str):
        member = self.members.get(member_id)
        book = self.books.get(isbn)
        
        if not member or not book:
            print("Invalid member or book")
            return None
        if not member.can_borrow():
            print("Borrow limit reached")
            return None
        if book.status != BookStatus.AVAILABLE:
            print("Book not available")
            return None
        
        Library._loan_counter += 1
        loan = Loan(f"LOAN-{Library._loan_counter}", book, member)
        loan.due_date = loan.borrow_date.replace(day=loan.borrow_date.day + member.member_type.loan_days)
        
        self.loans[loan.loan_id] = loan
        member.add_loan(loan)
        book.status = BookStatus.BORROWED
        print(f"Borrowed: {book.title}")
        return loan
    
    def return_book(self, loan_id: str) -> float:
        loan = self.loans.get(loan_id)
        if not loan or loan.return_date:
            print("Invalid loan")
            return 0
        
        loan.return_book()
        loan.book.status = BookStatus.AVAILABLE
        loan.member.remove_loan(loan)
        fine = loan.calculate_fine()
        print(f"Returned: {loan.book.title}" + (f" - Fine: ${fine}" if fine > 0 else ""))
        return fine
