# Digital Wallet & Transactional Ledger - System Design

Use this document to explore the high-level design of a digital wallet and transactional ledger system.

---

## 1. 📝 Requirements and Constraints

### Problem Statement
- System to design: A digital wallet and transactional ledger.
- Core user value: Securely store funds and transfer balances between accounts with absolute correctness.

### Functional Requirements
- [ ] FR1: Transfer balance between wallets (`from_account`, `to_account`, `amount`, `idempotency_key`).
- [ ] FR2: Strict double-entry bookkeeping ($\sum \text{Debits} == \sum \text{Credits}$).
- [ ] FR3: Balance hold / pending authorization.
- [ ] FR4: Full auditability and state replay from event history.

### Non-Functional Requirements

| Requirement | Target |
|---|---|
| Availability | 99.99% |
| Read latency | < 50ms |
| Write latency | < 100ms |
| Throughput | $10,000\text{ avg TPS, } 50,000\text{ peak TPS}$ |
| Consistency | Strong consistency (linearizability, no money creation/loss) |
| Durability | Absolute (no data loss under any failure mode) |

### Constraints
- Partition tolerance with Raft consensus per shard group.
- Strict consistency guardrails preventing double spending.

### Out of Scope
- Integration with external clearing networks (ACH/Visa/Mastercard)
- KYC/AML identity verification
- Complex currency exchange

---

## 2. 📊 Back-of-Envelope Estimation (Only What Changes Design)

### Traffic

| Metric | Value | Formula |
|---|---|---|
| Peak TPS | $50,000$ | input |

### Storage

| Data Type | Avg Size | Daily Volume | 1-Year |
|---|---|---|---|
| Ledger Entries | $200\text{ bytes} \times 2$ | $20\text{ MB/sec (peak)} = \sim 1.7\text{ TB/day}$ | $\sim 630\text{ TB/year}$ |

### Decision Notes
- **Throughput Bottleneck:** A single standard RDBMS cloud node handles $\approx 1,000\text{ to }3,000\text{ TPS}$. A naive 2PC RDBMS approach would require roughly 20-50 database nodes with heavy lock contention to handle peaks, which is unfeasible and highly brittle.
- **Architecture Shift:** High-performance event sourcing (append-only WAL + LSM state via RocksDB) achieves $10,000\text{--}50,000\text{ TPS}$ per node. This requires sharding into a few Raft partition groups (e.g., 5-10) to easily handle peak load with massive headroom.

---

## 3. 🔌 API / System Interface

### External Contract
- Protocol choice: gRPC (internal service-to-service) and REST (external API gateway).
- Auth model: Mutual TLS and OAuth2 tokens.

### Core Endpoints
```http
POST /api/v1/transfers
{
  "from_account": "uuid",
  "to_account": "uuid",
  "amount": "100.00",
  "currency": "USD",
  "idempotency_key": "unique-request-id"
}

POST /api/v1/accounts/{id}/holds
{
  "amount": "50.00",
  "currency": "USD",
  "idempotency_key": "unique-request-id"
}

GET /api/v1/accounts/{id}/balance
```

### Error Model
- `400` invalid input (e.g., negative amount)
- `402` insufficient funds
- `409` conflict/concurrency (e.g., idempotency key collision)
- `5xx` internal dependency failure

---

## 4. 🗄️ Core Entities and Data Model

### Core Entities
- Account: The wallet holding the balance.
- Ledger Entry: Individual debit or credit lines.
- Transaction Phase: State tracker for cross-shard transfers.

### Schema Design

```sql
CREATE TABLE accounts (
    account_id UUID PRIMARY KEY,
    currency VARCHAR(3) NOT NULL,
    balance DECIMAL(18, 4) NOT NULL,
    held_balance DECIMAL(18, 4) NOT NULL DEFAULT 0.0000,
    status VARCHAR(20) NOT NULL DEFAULT 'ACTIVE'
);

CREATE TABLE ledger_entries (
    entry_id UUID PRIMARY KEY,
    transaction_id UUID NOT NULL,
    account_id UUID NOT NULL,
    entry_type VARCHAR(10) NOT NULL, -- 'DEBIT' or 'CREDIT'
    amount DECIMAL(18, 4) NOT NULL,
    currency VARCHAR(3) NOT NULL,
    created_at TIMESTAMP NOT NULL,
    INDEX idx_tx (transaction_id),
    INDEX idx_acc (account_id)
);

CREATE TABLE tcc_phase_status (
    transaction_id UUID PRIMARY KEY,
    from_account UUID NOT NULL,
    to_account UUID NOT NULL,
    amount DECIMAL(18, 4) NOT NULL,
    phase VARCHAR(10) NOT NULL, -- 'TRY', 'CONFIRM', 'CANCEL'
    status VARCHAR(20) NOT NULL,
    out_of_order_flag BOOLEAN DEFAULT FALSE,
    updated_at TIMESTAMP NOT NULL
);
```

### Storage Choices
- Primary DB: Distributed Key-Value Store over Raft (e.g., RocksDB-backed custom data engine or CockroachDB/TiDB depending on team expertise).
- Partitioning: Accounts are sharded by `account_id` hash. Ledger entries are co-located with their respective accounts.

---

## 5. 🏗️ High-Level Architecture

### Component List
- **API Gateway:** Handles authentication, rate limiting, and request routing.
- **Transfer Orchestrator:** Manages the Saga/TC/C distributed transaction process.
- **Idempotency Store:** Fast KV store (Redis or DynamoDB) to catch immediate duplicate requests.
- **Raft Shard Groups:** Replicated state machines managing `accounts` and `ledger_entries`.

### Read Path (Balance Check)
1. Gateway routes request to Account Service.
2. Account Service calculates shard routing using `hash(account_id)`.
3. Read directed to Raft leader of the specific shard to ensure strict linearizability.

### Write Path (Intra-Shard Transfer)
1. Gateway routes transfer request to Transfer Orchestrator.
2. Orchestrator verifies `idempotency_key`.
3. Orchestrator detects both accounts are on the same shard.
4. Single atomic append to the shard's WAL updates both balances and creates two ledger entries.

### Failure-aware Path (Cross-Shard Transfer via TC/C)
1. Orchestrator records "TRY" phase for transaction.
2. **TRY (Source):** Send `hold` command to source shard (moves amount to `held_balance` and validates funds).
3. **TRY (Destination):** Send `validate` command to destination shard (ensures account exists and can receive funds).
4. **CONFIRM:** If both TRY operations succeed, send `confirm` to source shard (deducts from `held_balance`) and `add` to destination shard (credits balance).
5. **CANCEL:** If either TRY fails or times out, send `cancel` to source shard (moves `held_balance` back to `balance`).
- Symmetrical Guard: Both source and destination must execute TRY (reserving funds and validating destination account state) before any CONFIRM is sent to either shard. This prevents infinite money duplication if a credit was processed but the network timed out before confirming.

---

## 6. 🔍 Deep Dives

### Deep Dive A: Transaction Pattern & Concurrency
- Bottleneck: Standard RDBMS node lock contention.
- Chosen pattern: Raft-partitioned event sourcing.
- Alternative considered: 2-Phase Commit (2PC).
- Trade-off accepted: High complexity in cross-shard transaction orchestration (TC/C) to achieve massive horizontal scalability without database-level distributed locks.

### Deep Dive B: Double-Entry Bookkeeping and Auditability
- Consistency model: The WAL is the absolute source of truth.
- State materialization: The `accounts` table is merely a materialized view (snapshot) over the `ledger_entries` log.
- Auditability: Any corruption in `accounts` can be instantly detected and rebuilt by replaying the immutable WAL from offset 0, ensuring no money is ever created or destroyed.

---

## 7. ⚖️ Trade-offs and Decisions

| Decision | Option Chosen | Alternative | Why Chosen Now | Revisit Trigger |
|---|---|---|---|---|
| Distributed Tx | TC/C / Sagas | 2-Phase Commit | 2PC locking fails at 50k peak TPS; Sagas allow high throughput. | If cross-shard transaction failure rates cause excessive manual intervention. |
| Consistency | Strong (Raft) | Eventual | Financial ledgers cannot tolerate reading stale balances. | Never. |
| Storage | Event Log + LSM | B-Tree SQL | Append-only logs with RocksDB handle 400MB/sec ingest efficiently. | Storage costs exceed budget. |

---

## 8. 🔗 Cross-Links
- [Problem Statement](PROBLEM.md)
- [Approach](APPROACH.md)
- [Architecture Diagram](diagrams/architecture.mmd)
- [Rubric](RUBRIC.md)
- [Pitfalls](PITFALLS.md)
- [Follow-ups](FOLLOW-UPS.md)
- [Comparison](COMPARISON.md)
- [Strong Answer](STRONG-ANSWER.md)

---
**Real-world reference**: See how Stripe solved this in the [Stripe case study](../../case-studies/stripe-ledger-engine/)
