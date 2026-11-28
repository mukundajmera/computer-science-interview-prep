# Brokerage Platform — Common Interview Pitfalls

## 1. Designing an Exchange Instead of a Brokerage
A brokerage routes orders and tracks state; it does not own market matching logic.

## 2. Eventual Consistency for Final Order State
Order completion/cancellation must be strongly correct for user trust and compliance.

## 3. No Idempotency for Order Commands
Retries without idempotency create duplicate submissions and inconsistent balances.

## 4. Coupling Quote Fanout With Order Mutation
High-frequency market data can starve command processing if paths are not isolated.

## 5. Missing Reconciliation Loop
External acks can be delayed or dropped; periodic reconciliation is mandatory.

## 6. Ignoring Backpressure on Stream Subscribers
Without bounded queues and drop/degrade rules, websocket hubs fail under bursts.

## 7. No Explicit Order State Machine
Ad-hoc string updates create illegal transitions and debugging dead ends.

## 8. Running Pre-Trade Risk Checks Against the Relational Order DB
Querying PostgreSQL row locks for margin and buying-power math on every order adds 10–20 ms of contention during 10,000 req/sec market-open bursts and misses the sub-1 ms pre-trade risk budget. Keep active buying power and price collars in an in-memory Redis Lua engine, and rebuild state from the durable order ledger on shard restart.

## 9. Using Mutable Balance Updates Instead of a Double-Entry Ledger
Overwriting `cash_balance` and share counts in place makes partial fills, fees, and T+1 settlement discrepancies impossible to audit or reconcile. Record every fill as balanced append-only `LedgerEntries` rows whose amounts sum to zero per `transaction_id` and asset inside an ACID transaction.

## 10. Ignoring FIX Sequence Gaps and Duplicate Execution Reports
When a FIX 4.4 session drops, the exchange replays missed fills with `PossDupFlag=Y` after a `ResendRequest`, which double-credits shares if processed naively. Track FIX sequence numbers in the Exchange Adapter and enforce idempotent deduplication on exchange `fill_id` in the database.

## 11. Leaving Locked Buying Power Orphaned After Rejections or Mid-Flight Crashes
If the Order Service crashes after reserving buying power or writing `PENDING_SUBMIT` before sending `NewOrderSingle`, client cash stays permanently locked or orders duplicate on retry. Roll back risk reservations immediately on rejection and run a background sweeper to reconcile stuck `PENDING_SUBMIT` orders against the Exchange Adapter.

## 12. Failing to Isolate System Clearing Account Hot Keys in the Ledger
Because every settled trade debits or credits the central system clearing account, funneling all settlement rows into one account creates severe write contention during peak fills. Partition user ledgers by `account_id` and distribute clearing writes across multiple internal sweep accounts or batched aggregations.

---

## Quick Self-Check

- Did I separate fanout read path and command write path?
- Did I include idempotency and replay behavior?
- Did I define order transitions and reconciliation ownership?
- Did I keep pre-trade buying power and collar checks under 1 ms in memory rather than on RDBMS row locks?
- Did I enforce double-entry bookkeeping invariants for cash and position settlement?
- Did I handle FIX sequence-number gap fills and idempotent `fill_id` deduplication?
- Did I define rollback and sweeper recovery for stuck `PENDING_SUBMIT` orders and locked cash?
- Did I mitigate hot-key contention on internal clearing accounts during peak fills?
