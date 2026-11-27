# Atomic Commit Protocols in Distributed Systems

An **atomic commit protocol** guarantees that a distributed transaction spanning multiple shards or databases either commits on **every** participant or aborts on **every** participant, preserving all-or-nothing atomicity across machines.

The core intuition is the difference between **atomic commit** and **consensus** (see [`paxos-consensus-family.md`](./paxos-consensus-family.md)): consensus chooses *some* proposed value using a majority quorum, whereas atomic commit requires **unanimous** agreement to commit—any single participant can veto and force an abort.

Formally, an atomic commit protocol satisfies:
- **Agreement:** No two participants decide differently (one commits while another aborts).
- **Validity:** Commit is decided only if every participant voted `YES`; abort is decided if any participant voted `NO`.
- **Termination:** Every non-failed participant eventually reaches a decision (weakened under coordinator crashes in blocking protocols).

## Two-Phase Commit (2PC)

Two-Phase Commit (2PC) coordinates a single **coordinator** and $N$ **participants**, using Write-Ahead Logging (WAL) on every node so decisions survive restarts.

### Protocol Steps

1. **Phase 1: Prepare Phase (Voting)**
   - Coordinator logs `BEGIN` and sends `PREPARE(tx)` to all participants.
   - Each participant executes the local work, acquires locks, verifies constraints, and **flushes `PREPARED` to its WAL** before replying `VOTE_COMMIT` (`YES`). If it cannot guarantee commit (constraint violation, deadlock, disk error), it logs `ABORT`, releases locks, and replies `VOTE_ABORT` (`NO`).
   - Once a participant replies `VOTE_COMMIT`, it surrenders the right to abort unilaterally—it is now **in-doubt**.

2. **Phase 2: Commit Phase (Decision)**
   - If the coordinator receives `VOTE_COMMIT` from **all** participants, it **flushes `COMMIT(tx)` to its WAL** (this disk flush is the atomic commit point) and sends `COMMIT(tx)` to all participants.
   - If any participant votes `VOTE_ABORT` or times out, the coordinator logs `ABORT(tx)` and sends `ABORT(tx)` to all participants.
   - Each participant applies the decision, logs completion, releases its locks, and replies `ACK`. Once all `ACK`s arrive, the coordinator logs `END`.

### Worked Example: 2PC Transfer Walkthrough

Suppose transaction `T1` transfers `$100` from Account A (Shard 1) to Account B (Shard 2) via Coordinator `C`:

| Step | Actor | Action | Durable WAL Entry | Lock State |
| :--- | :--- | :--- | :--- | :--- |
| 1 | C | Send `PREPARE(T1)` to Shard 1, Shard 2 | `BEGIN(T1)` | — |
| 2 | Shard 1 | Debit A (`-$100`), reply `VOTE_COMMIT` | `PREPARED(T1)` | Row A locked |
| 3 | Shard 2 | Credit B (`+$100`), reply `VOTE_COMMIT` | `PREPARED(T1)` | Row B locked |
| 4 | C | All votes `YES`; send `COMMIT(T1)` | `COMMIT(T1)` (commit point) | — |
| 5 | Shards 1 & 2 | Finalize, release locks, reply `ACK` | `COMMITTED(T1)` | Unlocked |

**Coordinator-crash blocking scenario:** Suppose `C` crashes immediately after Step 3 (before Step 4 reaches the shards). Shard 1 and Shard 2 both logged `PREPARED(T1)` and hold exclusive locks on Rows A and B. Neither shard knows whether `C` flushed `COMMIT(T1)` before crashing or died before deciding. If Shard 1 unilaterally aborts while `C` had already logged `COMMIT`, atomicity is violated upon `C`'s recovery. Both shards must **block**—holding locks and stalling other transactions on Accounts A and B—until `C` recovers.

### Vulnerabilities and Blocking

- **Blocking on coordinator failure:** Between sending `VOTE_COMMIT` and receiving the Phase 2 decision, participants cannot release locks or resolve the transaction without the coordinator.
- **Double failure:** If the coordinator and a participant that already received `COMMIT` both crash, surviving participants cannot infer the decision by polling each other.
- **Latency and lock duration:** Two full network round trips plus two synchronous WAL flushes (participant prepare + coordinator commit) keep locks held across the network.

## Three-Phase Commit (3PC)

Three-Phase Commit (3PC) attempts to eliminate blocking by splitting the commit decision into two steps and assuming a **synchronous network** (bounded message delay and accurate failure detection).

### Protocol Steps

1. **Phase 1: CanCommit Phase (Voting)** — Coordinator sends `CAN_COMMIT`; participants vote `YES` or `NO` without irreversibly committing.
2. **Phase 2: PreCommit Phase (Preparation)** — If all vote `YES`, coordinator logs `PRE_COMMIT` and sends `PRE_COMMIT`. Participants acknowledge and enter the `PRE_COMMITTED` state, knowing a unanimous `YES` occurred.
3. **Phase 3: DoCommit Phase (Finalization)** — After receiving all `PRE_COMMIT` acknowledgments, coordinator sends `DO_COMMIT`; participants finalize, release locks, and reply `ACK`.

### How 3PC Prevents Blocking

3PC maintains an invariant: no participant is in `COMMIT` while another is still in `WAITING` (pre-`PRE_COMMIT`). If the coordinator crashes in a crash-stop model without partitions:
- Participants still in `WAITING` safely **abort** on timeout.
- Participants in `PRE_COMMITTED` elect a new coordinator and safely **commit**, because every alive participant must have at least voted `YES`.

**Why 3PC fails in practice:** Real networks are **asynchronous** and experience partitions. If a partition isolates the coordinator and one `PRE_COMMITTED` participant from a `WAITING` participant after Phase 1, the `WAITING` side times out and aborts while the `PRE_COMMITTED` side times out and commits—causing **split-brain** and violating atomicity. 3PC also adds an extra round trip and WAL flush.

## Why Consensus-Based Commit and Sagas Replaced Raw 2PC/3PC

1. **Consensus-Based Commit (2PC over Raft/Paxos):** Modern distributed SQL databases (Google Spanner, CockroachDB) still run 2PC across shards, but **replicate both the coordinator and every participant shard as Raft or Paxos groups**. If the coordinator leader crashes mid-transaction, its Raft group elects a new leader in milliseconds with the same replicated decision log, eliminating the single point of blocking without 3PC's partition bugs.
2. **Sagas (Long-Running Workflows):** Across independent microservices, holding database locks over network calls destroys throughput and violates service autonomy. A **Saga** breaks a workflow into local ACID transactions ($T_1, T_2, \dots, T_n$), each paired with a **compensating transaction** ($C_1, C_2, \dots, C_{n-1}$) that semantically undoes it on failure (via an orchestrator or event choreography). Sagas trade strict **isolation** (intermediate states are visible, requiring countermeasures like semantic locks or pending statuses) for high availability.

## Failure Cases

- **In-doubt lock pileup in 2PC:** A coordinator outage during peak traffic leaves thousands of prepared rows locked, cascading into connection-pool exhaustion.
- **Heuristic decision divergence:** An operator manually forcing an in-doubt participant to abort while the coordinator later replays `COMMIT` permanently corrupts cross-shard state.
- **3PC split-brain:** Network delay exceeding timeout thresholds causes one partition to commit and another to abort.
- **Failed Saga compensation:** A compensating action (such as refunding a payment) can itself fail and must be retried idempotently until it succeeds (backward recovery cannot be abandoned halfway).

## Trade-offs

| Protocol | Blocking? | Partition-Safe Atomicity | Isolation | Round Trips | Best Fit |
| :--- | :--- | :--- | :--- | :--- | :--- |
| Classic 2PC | Yes (coordinator crash) | Yes | Full ACID | 2 RTT | Single-DC XA transactions |
| 3PC | No (crash-stop only) | No (split-brain) | Full ACID | 3 RTT | Theoretical study; rarely deployed |
| 2PC + Raft/Paxos | No (replicated coord.) | Yes | Strict ACID | 2+ RTT | Distributed SQL (Spanner, CockroachDB) |
| Saga | No | Eventual (ACD) | No (dirty/intermediate reads) | Async per step | Cross-microservice business workflows |

## Interview Traps

- **Calling 2PC a consensus protocol:** 2PC cannot tolerate coordinator failure without blocking and requires unanimity, not a majority quorum.
- **Claiming 3PC solves 2PC's problems in real networks:** 3PC requires synchronous timing bounds; under real network partitions it breaks safety (atomicity).
- **Saying Sagas give you distributed ACID:** Sagas preserve Atomicity (eventually, via compensation) and Durability, but sacrifice **Isolation**—always mention semantic locks or idempotent compensations.
- **Forgetting the WAL flush order:** A participant must flush `PREPARED` to disk *before* sending `VOTE_COMMIT`, and the coordinator must flush `COMMIT` *before* sending Phase 2 `COMMIT` messages.

## Self-Check Questions

1. In 2PC, why is it unsafe for an in-doubt participant to abort unilaterally after a coordinator timeout?
2. Which exact WAL write marks the point of no return (commit point) in 2PC, and what happens if the coordinator crashes right before vs. right after it?
3. Construct a two-partition scenario where 3PC leaves Shard 1 committed and Shard 2 aborted.
4. Why do Spanner and CockroachDB combine 2PC with Paxos/Raft instead of replacing 2PC with Raft alone?
5. What anomaly can a user observe mid-Saga that would be impossible under 2PC, and how do you mitigate it?
