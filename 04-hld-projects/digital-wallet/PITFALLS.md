# Digital Wallet & Transactional Ledger - Common Pitfalls

## 1. The "Single RDBMS" Trap
- **Signal:** The candidate designs the entire ledger around a single Postgres or MySQL instance with standard ACID transactions.
- **Root Cause:** Failing to compute or understand the implications of the 50,000 peak TPS requirement. Standard cloud SQL instances bottleneck at ~1,000 to ~3,000 write TPS depending on lock contention.
- **Mitigation:** Explicitly do the math upfront. Demonstrate that heavy locking over distributed resources fundamentally caps throughput.
- **Validation:** Ask "What happens when your database hits 100% CPU lock wait time?"

## 2. Eventual Consistency Money Creation (Asymmetrical TC/C)
- **Signal:** The candidate describes a flow where source TRY is executed, followed immediately by a destination credit, and then a source cancel if the destination network request times out.
- **Root Cause:** Treating the destination credit as part of the TRY phase or executing it before the system has achieved consensus on the transaction. If the destination successfully processed the credit but the network timed out returning the response, the orchestrator will cancel the source (unholding the balance), leading to infinite money duplication.
- **Mitigation:** Implement a strict symmetrical TRY phase: **Both source and destination must execute TRY (reserving funds and validating account state) before any CONFIRM is sent.** If any TRY fails or times out, the system can safely CANCEL the source hold because no funds have been actually credited yet.
- **Validation:** Ask "What happens if the 'add to destination' network call succeeds on the destination database, but the ACK response drops due to a network timeout?"

## 3. Ignoring Idempotency
- **Signal:** The API lacks an idempotency key, or the system only checks the database for duplicates (which is too slow).
- **Root Cause:** Not accounting for mobile network retries. Users hitting "Send" twice when their connection drops.
- **Mitigation:** Mandate `idempotency_key` on all write APIs. Use a fast KV store (like Redis) for a quick reject layer, backed by deterministic database constraints.
- **Validation:** Ask "What happens if the client sends the exact same POST request three times in 50 milliseconds?"

## 4. Mutable Balance Tables
- **Signal:** Updating the balance via `UPDATE accounts SET balance = balance + amount` without an immutable log.
- **Root Cause:** Treating the materialized view as the source of truth rather than the event log.
- **Mitigation:** The Write-Ahead Log (WAL) of ledger entries is the absolute source of truth. The account balance table is merely a performance optimization.
- **Validation:** Ask "If a bad code deployment corrupted your accounts table overnight, how do you recover the exact balances to the penny?"
