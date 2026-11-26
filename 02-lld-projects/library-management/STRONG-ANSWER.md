# Strong Interview Answer: Library Management System

## 1. 45-Minute Pacing Guide
*   **0-5 mins: Clarifications & Scope.** Establish assumptions (member limits, fine calculations, multiple copies).
*   **5-15 mins: Core Entities & APIs.** Define `Library`, `Book`, `Member`, `Loan`. Define APIs for `borrowBook`, `returnBook`, `searchByTitle`.
*   **15-25 mins: Data Models & Relationships.** Discuss Singleton (Library), one-to-many (Member to Loans), and strategy pattern (Fines).
*   **25-35 mins: Implementation & Trade-offs.** Discuss naive vs optimized search, memory constraints, and thread safety.
*   **35-45 mins: Concurrency & Failure Scenarios.** Dive into race conditions during checkout and failure rollbacks.

## 2. Explicit Clarifications
*   **Member Limits:** Members have a strict borrow limit based on their type (e.g., STUDENT: 3, TEACHER: 5).
*   **Borrowing Period:** Standard 14 days, fines calculated at $0.50/day overdue.
*   **Capacity Boundary:** System must reject loans gracefully if the member limit is reached or no available copies exist.

## 3. Entities & APIs (Actual Source Code Version)
*   `Library` (Singleton Controller)
*   `Book` (Metadata: ISBN, Title, Author)
*   `Member` (Borrower details, limits)
*   `Loan` (Transaction state, due dates, fines)
*   **APIs (v3-optimized):**
    *   `public Loan borrowBook(String memberId, String isbn)` (Java) / `def borrow_book(self, member_id: str, isbn: str)` (Python)
    *   `public double returnBook(String loanId)` (Java) / `def return_book(self, loan_id: str) -> float` (Python)
    *   `public List<Book> searchByTitle(String title)` (Java)

## 4. Version-Specific Feature Deltas
*   **v1-basic:** Core entities, sequential simple logic, no concurrency. Tests target single-thread workflows.
*   **v2-extended:** Added enums for member types and book status, logic for maximum borrow limits and loan periods.
*   **v3-optimized:** Introduces thread safety and concurrent data structures to handle race conditions during checkouts.

## 5. Design Alternatives
*   **Database vs In-Memory:** In a real deployment, replace `HashMap` with an RDBMS (e.g., PostgreSQL) for transactional guarantees (ACID) during checkout.
*   **Fine Strategy:** Naive flat rate vs `StrategyPattern` allowing dynamic fine calculation (e.g., weekend waivers).

## 6. Correctness & Complexity
*   **Time Complexity:** `borrowBook` is $O(1)$ using HashMap lookups. `searchByTitle` is $O(N)$ natively, optimized to $O(\log N)$ or $O(1)$ with Trie/Inverted Index.
*   **Space Complexity:** $O(B + M + L)$ where $B$ is books, $M$ is members, and $L$ is active loans.

## 7. Failure & Concurrency Trace (Acceptance Cases)
*   **Normal Use-case:** Member borrows an available book; a `Loan` is created and the book status changes to `BORROWED`.
*   **Empty/Invalid Input:** The `borrowBook` API immediately returns `null` if `memberId` or `isbn` is missing or not found in registries.
*   **Duplicate Operation:** Returning an already returned loan ignores the operation gracefully (idempotent; returning 0).
*   **Capacity Boundary:** If a student tries to borrow a 4th book (limit is 3), the system evaluates the limit (`canBorrow()`) and rejects the operation without mutating state, returning `null`.
*   **Failure Rollback / Concurrency:** In `v3-optimized`, thread-safety is critical. If two members concurrently try to borrow the final copy, without synchronization, both might succeed. 
    *   **Trace:** Thread A reads `status == AVAILABLE`. Thread B reads `status == AVAILABLE`. Thread A creates Loan. Thread B creates Loan. 
    *   **Fix:** Use `ConcurrentHashMap` and lock the specific `Book` object during the checkout transaction. If a failure occurs mid-transaction (e.g., database network drop), rollback the `Loan` creation and restore the `Book` status to `AVAILABLE`.
