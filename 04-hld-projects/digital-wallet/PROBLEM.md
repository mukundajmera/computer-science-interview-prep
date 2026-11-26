# Digital Wallet & Transactional Ledger - Problem Statement

## Problem Context
Design a digital wallet system and transactional ledger that allows users to securely store funds and transfer balances between accounts. This system forms the financial core of payment gateways, banking apps, and e-commerce platforms. 

The system must handle an exceptionally high volume of transactions while maintaining absolute correctness. Because it deals with money, data loss, double-spending, and inconsistent states are strictly unacceptable.

## Functional Requirements (FR)
- **Balance Transfer:** Users can transfer balances between wallets (`from_account`, `to_account`, `amount`, `idempotency_key`).
- **Double-Entry Bookkeeping:** Strict accounting where the sum of all debits must equal the sum of all credits ($\sum \text{Debits} == \sum \text{Credits}$).
- **Balance Holds:** Support placing a hold on a balance / pending authorizations (e.g., locking funds during an ongoing external payment capture).
- **Auditability:** Full auditability and exact state replay from an immutable event history.

## Non-Functional Requirements (NFR)
- **Consistency:** Strong consistency (linearizability) is required. The system must strictly guarantee no money creation, deletion, or loss.
- **Throughput:** Capable of handling massive scale, with a target of $10,000\text{ avg TPS}$ and $50,000\text{ peak TPS}$ (Transactions Per Second).
- **Availability:** $99.99\%$ uptime guarantee.
- **Fault Tolerance:** Partition tolerance with Raft consensus per shard group to survive node failures without compromising correctness.

## Sizing & Scale Estimations
- **Throughput:** $10,000\text{ avg TPS}, 50,000\text{ peak TPS}$.
- **RDBMS Bottleneck:** A single standard RDBMS cloud node handles $\approx 1,000\text{ to }3,000\text{ TPS}$. Thus, a naive 2-Phase Commit (2PC) RDBMS approach would require roughly 20-50 database nodes with heavy, contention-prone locking to handle peaks.
- **Event Sourcing Alternative:** High-performance event sourcing (append-only Write-Ahead Log [WAL] + Log-Structured Merge-tree [LSM] state via RocksDB) achieves $10,000\text{--}50,000\text{ TPS}$ per node.
- **Partitioning:** The event sourcing setup is sharded into a few Raft partition groups (e.g., 5-10), with each group containing 3 or 5 replicas for high availability and fault tolerance.
- **Storage Profile:**
  - $50,000\text{ peak TPS} \times 2\text{ entries}$ (debit & credit) $\times 200\text{ bytes per entry} \approx 20\text{ MB/sec (peak)}$.
  - Daily ledger storage grows by roughly $1.7\text{ TB/day}$.
