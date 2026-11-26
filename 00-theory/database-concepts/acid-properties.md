# ACID Properties

The foundation of reliable database transactions. Essential knowledge for any system design interview.

---

## 📖 What is ACID?

ACID is a set of properties that guarantee database transactions are processed reliably.

```
┌────────────────────────────────────────────────────────┐
│                    TRANSACTION                         │
│  BEGIN                                                 │
│    1. Debit Account A: $100                           │
│    2. Credit Account B: $100                          │
│  COMMIT                                               │
│                                                       │
│  Either BOTH happen, or NEITHER happens               │
└────────────────────────────────────────────────────────┘
```

---

## ⚛️ A - Atomicity

> **All operations in a transaction succeed, or all fail. No partial execution.**

### Example

```sql
BEGIN TRANSACTION;
  UPDATE accounts SET balance = balance - 100 WHERE id = 1;
  UPDATE accounts SET balance = balance + 100 WHERE id = 2;
COMMIT;
```

**Without Atomicity:**
```
Step 1: Debit $100 from Account A ✓
Step 2: System crash! ❌
Result: Money disappeared! Account A lost $100, Account B never received it.
```

**With Atomicity:**
```
Step 1: Debit $100 from Account A
Step 2: System crash! ❌
Result: Entire transaction rolled back. Account A still has original balance.
```

### Implementation

Databases use **Write-Ahead Logging (WAL)**:
1. Write intentions to log
2. Execute operations
3. On crash, use log to rollback incomplete transactions

---

## 🔒 C - Consistency

> **Transaction brings database from one valid state to another valid state.**

### Example

```sql
-- Constraint: Account balance must be >= 0
ALTER TABLE accounts ADD CONSTRAINT positive_balance CHECK (balance >= 0);

-- This transaction maintains consistency
BEGIN TRANSACTION;
  UPDATE accounts SET balance = balance - 100 WHERE id = 1;  
  -- If this makes balance < 0, transaction fails
COMMIT;
```

**Consistency ensures:**
- All constraints are satisfied
- Referential integrity maintained
- Business rules enforced

### Note

Consistency in ACID ≠ Consistency in CAP theorem
- ACID: Data validity rules
- CAP: All nodes see same data

---

## 🔐 I - Isolation

> **Concurrent transactions don't interfere with each other.**

### The Problem

```
Transaction A                Transaction B
─────────────                ─────────────
Read balance: $100
                             Read balance: $100
                             Update balance: $100 + $50 = $150
                             Commit
Update balance: $100 - $30 = $70
Commit

Expected: $100 + $50 - $30 = $120
Actual: $70 (Transaction B's update lost!)
```

### Isolation Levels

| Level | Dirty Read | Non-Repeatable Read | Phantom Read |
|-------|------------|---------------------|--------------|
| **Read Uncommitted** | ✓ Possible | ✓ Possible | ✓ Possible |
| **Read Committed** | ✗ Prevented | ✓ Possible | ✓ Possible |
| **Repeatable Read** | ✗ Prevented | ✗ Prevented | ✓ Possible |
| **Serializable** | ✗ Prevented | ✗ Prevented | ✗ Prevented |

### Trade-off

```
Higher Isolation ◀──────────────────▶ Higher Performance
(More locking)                        (Less locking)
```

---

## 💾 D - Durability

> **Once a transaction is committed, it survives system failures.**

### How It Works

```
1. Transaction commits
2. Data written to non-volatile storage (disk)
3. System crash
4. System restart
5. Committed data is still there ✓
```

### Implementation Techniques

1. **Write-Ahead Logging (WAL)**
   - Write to log before data files
   - Replay log on recovery

2. **Checkpointing**
   - Periodic snapshots to disk
   - Reduces recovery time

3. **Replication**
   - Copy data to multiple nodes
   - Survives single machine failure

---

## 🔧 Practical Example

```java
@Transactional  // Spring annotation - ensures ACID
public void transferMoney(Long fromId, Long toId, BigDecimal amount) {
    Account from = accountRepo.findById(fromId);
    Account to = accountRepo.findById(toId);
    
    if (from.getBalance().compareTo(amount) < 0) {
        throw new InsufficientFundsException();  // Consistency
    }
    
    from.setBalance(from.getBalance().subtract(amount));
    to.setBalance(to.getBalance().add(amount));
    
    accountRepo.save(from);
    accountRepo.save(to);
    // Atomicity: Both saves commit together or neither does
    // Durability: Once method returns, changes are permanent
}
```

---

## ⚖️ ACID vs BASE

| ACID (SQL) | BASE (NoSQL) |
|------------|--------------|
| Strong consistency | Eventual consistency |
| Pessimistic (lock-based) | Optimistic |
| Vertical scaling | Horizontal scaling |
| Single node preferred | Distributed by design |
| Banking, inventory | Social media, caching |

### BASE Explained

- **B**asically **A**vailable: System always responds
- **S**oft state: State may change over time
- **E**ventual consistency: Data will converge eventually

---

## 🎯 Interview Questions

### Q1: "Why can't distributed systems easily provide ACID?"

**Answer**:
"Distributed systems face network partitions. When nodes can't communicate:
- **Atomicity**: Hard to coordinate commit across nodes
- **Consistency**: Different nodes may have different data
- **Isolation**: Requires distributed locking (expensive)
- **Durability**: Usually achievable with replication

This is why distributed DBs often use BASE model - sacrificing strong consistency for availability and partition tolerance (CAP theorem)."

### Q2: "Which isolation level would you use for a banking app?"

**Answer**:
"For financial transactions, I'd use **Serializable** or **Repeatable Read**:
- Prevents lost updates (concurrent transfers)
- Prevents dirty reads (reading uncommitted changes)
- Prevents phantom reads (new rows appearing)

The performance hit is acceptable for correctness in financial systems."

### Q3: "How does a database ensure Durability?"

**Answer**:
"Through multiple mechanisms:
1. **Write-Ahead Logging**: Changes logged before applied
2. **Fsync**: Force flush to disk on commit
3. **Replication**: Copy to multiple disks/nodes
4. **Battery-backed cache**: Survive power failures

On crash, the database replays the transaction log to recover committed transactions."

---

## 📋 Quick Reference

```
┌──────────────────────────────────────────────────────┐
│  ATOMICITY     │  All or nothing                    │
├──────────────────────────────────────────────────────┤
│  CONSISTENCY   │  Valid state to valid state        │
├──────────────────────────────────────────────────────┤
│  ISOLATION     │  Transactions don't interfere      │
├──────────────────────────────────────────────────────┤
│  DURABILITY    │  Committed = permanent             │
└──────────────────────────────────────────────────────┘
```

---

## 🔗 Cross-References

- **CAP Theorem**: Trade-offs in distributed systems
- **SQL vs NoSQL**: When ACID matters
- **Database Sharding**: ACID challenges when distributed
- **Distributed Transactions**: Saga pattern, 2PC

---

*💡 Pro Tip: Know the isolation levels well. Interviewers love asking about the trade-offs between consistency and performance.*
