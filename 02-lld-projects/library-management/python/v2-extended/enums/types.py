"""Library Management Enums."""
from enum import Enum


class BookStatus(Enum):
    AVAILABLE = "AVAILABLE"
    BORROWED = "BORROWED"
    RESERVED = "RESERVED"
    LOST = "LOST"


class MemberType(Enum):
    STUDENT = ("STUDENT", 5, 14)
    FACULTY = ("FACULTY", 10, 30)
    PUBLIC = ("PUBLIC", 3, 7)
    
    def __init__(self, name, borrow_limit, loan_days):
        self._borrow_limit = borrow_limit
        self._loan_days = loan_days
    
    @property
    def borrow_limit(self): return self._borrow_limit
    @property
    def loan_days(self): return self._loan_days
