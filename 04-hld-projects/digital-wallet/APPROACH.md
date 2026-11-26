# Digital Wallet & Transactional Ledger - Approach

## High-Level Strategy

Designing a massive-scale digital wallet necessitates solving the distributed transaction problem. When a transfer occurs between accounts on different physical database nodes or partitions, we must guarantee atomicity—either the transfer fully succeeds or fully fails. 

The core challenge is balancing **throughput** with **strong consistency**.

## Transaction Pattern Comparisons

We must evaluate several patterns for handling distributed state changes: 2-Phase Commit (2PC), Try-Confirm/Cancel (TC/C), and Raft-Partitioned Event Sourcing.

### 1. Two-Phase Commit (2PC)
A traditional distributed database approach coordinated by a transaction manager.
- **Mechanism:** 
  - *Phase 1 (Prepare):* All participating nodes lock resources and vote to commit.
  - *Phase 2 (Commit/Rollback):* Based on votes, the manager commands all nodes to finalize or abort.
- **Trade-offs:**
  - *Pros:* Strict ACID guarantees, conceptually simple.
  - *Cons:* Extremely poor throughput due to long-held locks during network round-trips. A single slow node blocks the entire transaction. At our required scale, heavy distributed lock holding causes a single point of failure and restricts throughput to $<1,000\text{ TPS}$ per node. It scales terribly.

### 2. Try-Confirm/Cancel (TC/C)
A pattern that implements a distributed transaction in the application layer, avoiding long-lived database locks.
- **Mechanism:**
  - *Try:* Reserve resources and validate state symmetrically. In a wallet, this means moving source funds into a `held_balance` and validating the destination account exists and can receive funds.
  - *Confirm:* If *both* 'Try' steps succeed, finalize the operation (deduct the held balance on source and add to the target account).
  - *Cancel:* If *any* 'Try' fails or times out, revert the reservation (release the held balance back to available balance on source).
- **Trade-offs:**
  - *Pros:* Highly parallelizable, database-agnostic, no distributed database locks. Ideal for integrating disparate microservices.
  - *Cons:* Requires complex orchestrators to handle partial failures, out-of-order messages, and retries.

### 3. Raft-Partitioned Event Sourcing
An architecture that relies on immutable logs of events distributed across consensus groups.
- **Mechanism:**
  - Commands (e.g., `TransferMoneyCommand`) are appended to a Write-Ahead Log (WAL).
  - A consensus algorithm (Raft) ensures the WAL is strongly consistent across replicas (3-5 nodes per partition).
  - State machines (e.g., built on RocksDB) linearly process the WAL to project the current materialized state (account balances).
- **Trade-offs:**
  - *Pros:* Deterministic commands yield an immutable event log. The historical state can always be recomputed for perfect auditability. By sharding into 20-50 Raft groups, throughput can scale linearly without heavy cross-shard locking contention. Fast local SSD writes for append-only logs handle massive I/O.
  - *Cons:* Eventual consistency in materialized views (though the log itself is strictly consistent), requires handling cross-partition coordination if a transaction spans two Raft groups.

## Chosen Architecture Direction

To achieve the targeted $50,000\text{ peak TPS}$, we will adopt a hybrid approach: **Raft-Partitioned Event Sourcing** combined with application-level **Sagas or TC/C** for cross-shard transfers. 

1. **High Throughput Storage:** Core accounts and ledgers will use Event Sourcing over a Raft consensus layer backed by an LSM-tree storage engine (like RocksDB). This easily yields $10,000\text{--}50,000\text{ TPS}$ per node.
2. **Symmetrical Try-Confirm/Cancel (TC/C):** For cross-shard transactions, we apply a strict symmetrical TRY phase: both source and destination must successfully complete the TRY phase (reserving funds and validating destination account state) before any CONFIRM is sent to either shard. This prevents infinite money duplication if the destination processes a credit but a network timeout occurs.
3. **Idempotency & Replay:** Every operation is tagged with an `idempotency_key` ensuring safe retries, while the immutable event log provides native double-entry bookkeeping and exact state replay.
