# Database Isolation Levels - Interview Q&A

**Q1: How does a Dirty Read differ from a Non-Repeatable Read?**
**A1:** A Dirty Read occurs when Transaction A reads data modified by Transaction B before Transaction B has committed. If B rolls back, A has read data that "never existed." A Non-Repeatable Read occurs when Transaction A reads data, Transaction B modifies and *commits* the change, and then A reads the same data again and sees the new committed value. Dirty Reads involve uncommitted data; Non-Repeatable reads involve committed data changing during a transaction.

**Q2: What is Lock Escalation, and why does a database perform it?**
**A2:** Lock escalation is the process of converting many fine-grained locks (like row locks) into fewer coarse-grained locks (like a table lock). Databases do this to save memory and reduce the overhead of managing thousands of individual lock structures. However, escalation reduces concurrency because a table lock blocks other transactions from accessing *any* row in the table, not just the previously locked ones.

**Q3: Describe a scenario where a Deadlock occurs and how a database engine resolves it.**
**A3:** Deadlock scenario: Transaction A locks Row 1. Concurrently, Transaction B locks Row 2. Then, Transaction A tries to lock Row 2, and waits for B. B tries to lock Row 1, and waits for A. Neither can proceed.
Resolution: The database engine detects this cycle using a waits-for graph or a timeout mechanism. It selects one transaction as the "victim" (often the one that has done the least amount of work or the younger transaction), aborts and rolls it back, thereby releasing its locks and allowing the other transaction to proceed. The application must catch the deadlock exception and retry the aborted transaction.

**Q4: How do you perform a high-concurrency balance transfer between two accounts safely without causing deadlocks?**
**A4:**
1.  **Consistent Ordering:** Always acquire locks (e.g., via `SELECT FOR UPDATE` or `UPDATE`) in a consistent order, such as by Account ID (e.g., smallest ID first). This prevents the classic A->B, B->A deadlock.
2.  **Appropriate Isolation Level:** Use Read Committed to minimize lock duration, relying on atomic `UPDATE accounts SET balance = balance + X WHERE id = Y` statements.
3.  **Retry Logic:** Always wrap the transaction block in a retry loop to handle transient deadlock exceptions gracefully.

**Q5: What is Write Skew, and why doesn't Snapshot Isolation prevent it?**
**A5:** Write Skew occurs when two concurrent transactions read the same data set, make independent decisions based on that read, and write to *different* overlapping data, violating a constraint. Snapshot Isolation (SI) doesn't prevent it because SI only detects write-write conflicts (two transactions updating the *same* row). Since Write Skew involves updating different rows, the first-committer-wins rule is not triggered, and both transactions commit.

**Q6: Explain how Serializable Snapshot Isolation (SSI) detects conflicts.**
**A6:** SSI extends Snapshot Isolation by tracking read dependencies (rw-dependencies). It monitors when a transaction reads a version that is later overwritten by a concurrent transaction, and when it overwrites a version read by a concurrent transaction. If SSI detects a cycle of these rw-dependencies (specifically, a "dangerous structure" of two consecutive rw-dependencies), it aborts one of the transactions to maintain serializability, effectively preventing Write Skew without traditional pessimistic locking.

**Q7: In MVCC, how is a Read View constructed?**
**A7:** A Read View is a snapshot of the active transaction state. It is typically constructed by capturing:
1.  `min_trx_id`: The lowest transaction ID among active transactions.
2.  `max_trx_id`: The ID that will be assigned to the next new transaction.
3.  `active_trx_ids`: A list/set of all transaction IDs currently active.
When evaluating tuple visibility, a transaction can see a tuple if its creation ID is less than `min_trx_id`, or if its ID is less than `max_trx_id` and *not* in the `active_trx_ids` list.

**Q8: Why might a long-running transaction in PostgreSQL cause database performance degradation?**
**A8:** PostgreSQL implements MVCC by appending new row versions directly to the table pages. Old row versions (dead tuples) must be retained as long as *any* active transaction might need to read them. A long-running transaction prevents the Vacuum process from cleaning up these dead tuples. This leads to "table bloat" (wasted disk space) and slower queries because sequential scans must read through the dead tuples.

**Q9: What is Next-Key Locking in MySQL InnoDB?**
**A9:** Next-Key Locking is a combination of a record lock on an index record and a gap lock on the gap before the index record. InnoDB uses it primarily under the Repeatable Read isolation level to prevent Phantom Reads. By locking the gaps between existing index values, it prevents concurrent transactions from inserting new rows that would match a query's range condition.

**Q10: Compare the default isolation levels of PostgreSQL and MySQL InnoDB.**
**A10:**
-   **PostgreSQL:** Defaults to `Read Committed`. It does not use gap locks by default. To prevent phantom reads, you must explicitly use `Repeatable Read` (which is actually SI) or `Serializable`.
-   **MySQL InnoDB:** Defaults to `Repeatable Read`. Because it utilizes Next-Key locks, InnoDB's Repeatable Read prevents both non-repeatable reads *and* phantom reads, making it stricter than the ANSI SQL-92 definition.
