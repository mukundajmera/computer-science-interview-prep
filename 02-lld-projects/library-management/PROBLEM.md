# Library Management System

## Problem Statement

Design a library management system that handles book inventory, member management, and borrowing/returning of books.

---

## Functional Requirements

1. **Book Management**: Add, remove, update, and search for books
2. **Member Management**: Register members, track borrowing history
3. **Borrowing System**: Issue books to members with due dates
4. **Return System**: Process book returns, handle late returns
5. **Search Functionality**: Search by title, author, ISBN, or category
6. **Fine Calculation**: Calculate fines for late returns
7. **Reservation System**: Reserve books that are currently borrowed
8. **Multiple Copies**: Track multiple copies of the same book

---

## Non-Functional Requirements

1. **Concurrency**: Handle multiple checkouts/returns simultaneously
2. **Data Consistency**: Prevent double-booking of the same book copy
3. **Performance**: Fast search across large book collections
4. **Scalability**: Support growing library with 100,000+ books
5. **Availability**: System should be accessible during library hours

---

## Constraints & Assumptions

- Each member can borrow up to 5 books at a time
- Borrowing period is 14 days by default
- Fine rate is $1 per day for late returns
- A book can have multiple copies, each tracked separately
- Members must be registered before borrowing
- Books can be reserved only if all copies are borrowed

---

## Sample Interactions

```
1. Librarian adds new book to catalog
2. Member searches for a book
3. If available:
   - Librarian issues book to member
   - System creates borrowing record with due date
   - Book copy marked as borrowed
4. On return:
   - System calculates any fine
   - Member pays fine if applicable
   - Book copy marked as available
5. If book not available:
   - Member can place reservation
   - System notifies when book becomes available
```

---

## Clarifying Questions to Ask

1. "How many books can a member borrow at once?"
2. "What is the borrowing period?"
3. "How are fines calculated?"
4. "Can members reserve books?"
5. "Do we track multiple copies of the same book?"
6. "Is there a renewal feature?"
7. "Do we need librarian vs member roles?"
8. "Should we track book condition?"

---

## Entities to Identify

| Entity | Responsibility |
|--------|---------------|
| Library | Main system, manages catalog and members |
| Book | Book metadata (title, author, ISBN) |
| BookCopy | Physical copy of a book |
| Member | Library member who can borrow |
| Librarian | Staff who manages library |
| BorrowingRecord | Tracks who borrowed what and when |
| Reservation | Queue for reserved books |
| Fine | Late return penalty |

---

## Version Roadmap

| Version | Features |
|---------|----------|
| v1-basic | Core entities, issue/return, simple search |
| v2-extended | Fines, reservations, notifications, categories |
| v3-optimized | Thread-safe, concurrent access, optimized search |
