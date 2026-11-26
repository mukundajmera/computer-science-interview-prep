# Code Walkthrough: Library Management

## Overview

CRUD operations with borrowing logic. Tests entity relationships.

---

## File Structure

```
java/v1-basic/
├── Book.java           # Book entity
├── Member.java         # Library member
├── Librarian.java      # Staff operations
├── Library.java        # Main controller
└── LibraryDemo.java
```

---

## Core Operations

| Operation | Flow |
|-----------|------|
| Borrow | Check availability → Check member limit → Create loan |
| Return | Find loan → Calculate fine → Update book status |
| Search | By title/author/ISBN |
| Reserve | Add to waitlist if unavailable |

---

## Interview Questions

### 1. "How to handle book reservation queue?"

```java
class Book {
    Queue<Member> reservationQueue;
    
    void onReturn() {
        if (!reservationQueue.isEmpty()) {
            Member next = reservationQueue.poll();
            notifyAvailable(next);
        }
    }
}
```

### 2. "How to calculate late fees?"

```java
double calculateFine(Loan loan) {
    long daysLate = ChronoUnit.DAYS.between(loan.dueDate, LocalDate.now());
    return Math.max(0, daysLate * DAILY_FINE);
}
```

### 3. "How to handle multiple copies?"

Add `Copy` entity between `Book` and `Loan`.

---

## Design Patterns

| Pattern | Usage |
|---------|-------|
| **Factory** | Create different member types |
| **Observer** | Notify on book availability |
| **Strategy** | Fine calculation rules |

## Compilation and Execution

To compile and run the project for any version (e.g., v1-basic), use the following commands from the root directory of the project:

### Compile
```bash
find java/v1-basic -name '*.java' | xargs javac -encoding UTF-8 -d out
```

### Run
```bash
java -cp out LibraryDemo
```
