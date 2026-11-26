# ATM System - Strong Answer

> **Type:** Low-Level Design  
> **Difficulty:** Intermediate/Hard  
> **Time Target:** 45 minutes

## 1. Explicit Clarifications & Assumptions

Before jumping into the design, it is critical to clarify assumptions with the interviewer. For this ATM system, based on standard problem constraints, we establish the following:

- **Single Currency:** The system strictly handles a single currency (e.g., USD) to simplify currency conversion complexities.
- **Exact Denominations:** The ATM holds a finite cash inventory with specific denominations ($100, $50, $20, $10). Dispensing should use a greedy algorithm (preferring larger denominations) while bounding dispensing to internal stock.
- **Data Types for Currency:** All monetary amounts must be handled precisely. While standard floating-point `double` might be used for simplicity in sketches, a production system must use `BigDecimal` (Java) or integer minor units/Decimal (Python, e.g., cents) to prevent rounding errors.
- **Failure Scenarios:** Network partitions, authentication failures (e.g., locking out after 3 incorrect attempts), and cash dispenser hardware faults (e.g., inventory shortage leading to a rollback) must be addressed explicitly.
- **Transfers:** Funds can be transferred between accounts.
- **Security:** PINs are assumed encrypted; authentication limits apply.

## 2. Core Entities & APIs

### Models

*   **Account:** Holds user balances and state.
    *   Fields: `accountNumber`, `accountType` (CHECKING/SAVINGS), `balance`, `pin`, `isLocked`, `failedAttempts`, `lock` (ReentrantLock).
    *   Methods: `validatePin(pin)`, `withdraw(amount)`, `deposit(amount)`.
*   **Card:** Represents the physical card inserted into the machine.
    *   Fields: `cardNumber`, `linkedAccount`.
*   **CashDispenser / Inventory:** Manages the internal physical bills.
    *   Fields: `cashInventory` (Map of Denomination -> Count).
    *   Methods: `canDispense(amount)`, `dispenseCash(amount)`.
*   **Transaction:** Abstract base class for operations.
    *   Subtypes: `WithdrawalTransaction`, `DepositTransaction`, `TransferTransaction`, `BalanceInquiryTransaction`.
    *   Fields: `transactionId`, `accountId`, `status`, `amount`.

### The ATM State Machine (State Pattern)

The ATM lifecycle is highly controlled to prevent out-of-order execution (e.g., withdrawing before PIN validation).

1.  **IDLE**: Waiting for card insertion.
2.  **CARD_INSERTED**: Card read, waiting for PIN.
3.  **AUTHENTICATING**: Validating PIN (3 attempts max).
4.  **SELECT_ACTION**: PIN valid; user selects withdraw, deposit, transfer, or balance.
5.  **PROCESSING**: Executing transaction, interfacing with Bank/Dispenser.
6.  **TRANSACTION_COMPLETE**: Transaction finished; eject card or loop back to SELECT_ACTION.

## 3. Design Alternatives: Locking & Concurrency

### Why ReentrantLocks?
Handling concurrency is the most critical aspect of the ATM system. If two ATMs try to withdraw from the same account simultaneously, a race condition could allow double-spending.

*   **Alternative 1: Synchronized Methods / Global Lock:** A simple `synchronized` block on the account or a global lock. This is too coarse and destroys throughput.
*   **Alternative 2: Database Transactions (ACID):** In reality, the central banking database handles the lock via `SELECT ... FOR UPDATE`.
*   **Chosen Approach (Memory/LLD Simulation):** We use fine-grained `ReentrantLock` (Java) or `threading.Lock` (Python) instantiated per `Account`. Every mutating operation (`withdraw`, `deposit`) must acquire this lock, perform validation (e.g., check `balance >= amount`), mutate, and release.

## 4. Correctness & Complexity: The Transfer Concurrency Problem

### Concrete Failure Scenario: Concurrent Opposite-Direction Transfers

Consider a `TransferTransaction` where Account A transfers $50 to Account B, and simultaneously, Account B transfers $50 to Account A. 
A naive locking strategy would do:
```java
// Thread 1 (A -> B)
lock(A);
lock(B); // DEADLOCK! Thread 2 holds B

// Thread 2 (B -> A)
lock(B);
lock(A); // DEADLOCK! Thread 1 holds A
```

### The Solution: Stable Account-ID Ordering

To preserve the total account money and never overdraw while preventing deadlocks, the transfer logic must acquire locks in a **collision-free stable total order**. By always locking the account with the lexicographically smaller (or hash-based smaller) account ID first, we ensure threads never hold locks in a cycle.

**Java Implementation (Thread-Safe Transfer):**
```java
public static boolean transferBetweenAccounts(Account from, Account to, double amount) {
    if (amount <= 0) return false;
    
    // Determine lock order based on hash or Account ID
    int hash1 = from.getAccountNumber().hashCode();
    int hash2 = to.getAccountNumber().hashCode();
    Account first = hash1 < hash2 ? from : to;
    Account second = first == from ? to : from;
    
    // Tie-breaker if hashes collide
    if (hash1 == hash2) {
        first = from.getAccountNumber().compareTo(to.getAccountNumber()) < 0 ? from : to;
        second = first == from ? to : from;
    }
    
    first.getLock().lock();
    try {
        second.getLock().lock();
        try {
            // Strict positive-amount checks and balance verification
            if (from.getBalance() < amount) return false;
            
            // Execute transfer
            from.withdraw(amount);
            to.deposit(amount);
            return true;
        } finally {
            second.getLock().unlock();
        }
    } finally {
        first.getLock().unlock();
    }
}
```

This ensures that concurrent opposite-direction transfers preserve total account money and never overdraw; locks use a collision-free stable total account-ID order, completely avoiding deadlocks.

## 5. Reference Contracts & Edge Cases

The system explicitly defines reference contracts across both Java and Python to handle critical edge cases:

*   **Normal Use-Case:** A valid PIN authentication followed by a transaction within balance limits executes smoothly.
*   **Empty/Invalid Input (Positive-Amount Checks):** All mutating operations (withdraw, deposit, transfer) enforce strict positive-amount checks. Negative or zero values fail predictably and return `false` or raise an error without locking resources.
*   **Duplicate Operations:** To handle network retries, duplicate operations should use idempotency keys (duplicate operation IDs) to ensure they are processed exactly once.
*   **Capacity Bounds (Cash Inventory Shortage):** The machine checks physical inventory bounds via `canDispense(amount)` *before* issuing a `withdraw` against the ledger.
*   **Failure Rollbacks:** In case of a cash dispenser hardware fault or inventory shortage after deduction, a failure rollback is executed. Rollback failure tests must verify that balances are fully restored if dispensing fails.
*   **Same-Account Behavior:** Transferring money to the same account (`from == to`) will no-op or gracefully exit, avoiding re-entrant lock complexities.

## 6. Version-Specific Implementations

The provided source code is structured into three evolutionary versions, demonstrating a progression in complexity:
*   **`v1-basic`:** A simplified initial implementation focusing on the core state machine, basic authentication, and simple withdrawals/deposits without complex concurrency handling.
*   **`v2-extended`:** Adds more robust transaction models, basic error handling, and introduces interfaces for cleaner separation.
*   **`v3-optimized`:** The production-ready design demonstrating thread-safety using fine-grained locks (like `ReentrantLock`), complex concurrent transfer mechanisms, and robust failure rollbacks.

*Note: When running focused tests or verifying behavior, ensure you target the exact version's package (e.g., `v3-optimized`) rather than silently importing `v1-basic`, as only the later versions fully implement the concurrency defenses and advanced edge cases.*
