# ATM System — Common Interview Pitfalls

Common failure patterns and what to do instead.

> Related: [PROBLEM](./PROBLEM.md) · [DESIGN](./DESIGN.md) · [RUBRIC](./RUBRIC.md) · [FOLLOW-UPS](./FOLLOW-UPS.md)

---

## 1. Mixing UI and Hardware with Core Logic
- **Pitfall**: Putting cash dispenser, card reader, and screen output in the same class as transaction processing.
- **Why it hurts**: Violates SRP; makes it impossible to unit test core logic without hardware stubs.
- **Better**: Abstract hardware behind interfaces and use controllers to orchestrate interactions.

## 2. Incomplete State Machine
- **Pitfall**: Using a series of if-statements for ATM states (Idle, HasCard, Authenticated).
- **Why it hurts**: Hard to maintain, prone to bugs (e.g., withdrawing without authentication).
- **Better**: Implement the State Design Pattern to enforce valid state transitions clearly.

## 3. Ignoring Concurrency in Cash Inventory
- **Pitfall**: Updating ATM cash inventory without locks.
- **Why it hurts**: Two concurrent transactions could dispense the same physical cash.
- **Better**: Use proper locking or transactional database updates for cash inventory management.

## 4. Poor Handling of Partial Failures
- **Pitfall**: Deducting account balance before dispensing cash, but failing to rollback if dispense fails.
- **Why it hurts**: Customer loses money without receiving cash.
- **Better**: Implement a two-phase commit protocol or a robust saga pattern for compensating transactions.

## 5. Hardcoding Denominations
- **Pitfall**: Hardcoding $20, $50, $100 bill logic into the cash dispenser.
- **Why it hurts**: Difficult to deploy ATMs in different countries or with different cassette configurations.
- **Better**: Make denominations configurable and use the Chain of Responsibility pattern for dispensing.

## 6. Overlooking Security and Authentication
- **Pitfall**: Passing plaintext PINs around or failing to implement maximum retry limits.
- **Why it hurts**: Creates significant security vulnerabilities.
- **Better**: Hash PINs, implement strict retry limits (e.g., card capture after 3 attempts), and secure communication channels.

## 7. Lack of Transaction Logging
- **Pitfall**: Relying only on current balance without an append-only transaction log.
- **Why it hurts**: Cannot audit discrepancies or resolve customer disputes.
- **Better**: Maintain a robust, immutable transaction log for every operation.

## 8. Missing Idempotency
- **Pitfall**: Allowing the same withdrawal request to be processed multiple times.
- **Why it hurts**: Customer gets charged twice for one physical cash dispense.
- **Better**: Ensure all mutating operations require a unique transaction ID and handle retries idempotently.
