#!/usr/bin/env python3
"""Library Management Demo."""
import sys
sys.path.insert(0, '.')
from enums import MemberType
from models import Book, Member
from library import Library


def main():
    print("=== Library Management Demo ===\n")
    
    lib = Library("City Library")
    lib.add_book(Book("978-0-13-468599-1", "Clean Code", "Robert Martin"))
    lib.add_book(Book("978-0-201-63361-0", "Design Patterns", "GoF"))
    
    student = Member("M001", "John Doe", MemberType.STUDENT)
    lib.register_member(student)
    
    loan = lib.borrow_book("M001", "978-0-13-468599-1")
    if loan:
        lib.return_book(loan.loan_id)
    
    print("\n=== Demo Complete ===")


if __name__ == "__main__":
    main()
