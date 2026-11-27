# Conflict-free Replicated Data Types (CRDTs)

Conflict-free Replicated Data Types (CRDTs) are replicated data structures that guarantee **Strong Eventual Consistency (SEC)**: any two replicas that have received the same unordered set of updates are mathematically guaranteed to hold the exact same state, without coordination, locks, or consensus round-trips.

The core intuition is to restrict updates and merges to algebraic structures where order and duplication cannot create divergence. Replicas remain writable during network partitions and merge deterministically once connectivity returns.

## Core Concepts

CRDTs fall into two primary replication models depending on whether peers exchange full states or discrete operations.

### 1. State-based CRDTs (CvRDT)

In a **Convergent Replicated Data Type (CvRDT)**, each replica mutates its local state and periodically ships its state to peers (often via gossip). To guarantee convergence, the state space $(S, \le, \sqcup)$ must form a **bounded join-semilattice**, where updates move monotonically upward ($s \le s'$) and the merge operator $\sqcup$ (least upper bound) satisfies:

- **Commutativity:** $A \sqcup B = B \sqcup A$ (delivery order does not matter).
- **Associativity:** $(A \sqcup B) \sqcup C = A \sqcup (B \sqcup C)$ (grouping of merges does not matter).
- **Idempotence:** $A \sqcup A = A$ (duplicate deliveries are harmless).

Because merge tolerates dropped, reordered, and duplicated messages, CvRDTs work over unreliable networks. Their downside is payload size when shipping full state; **Delta-state CRDTs ($\delta$-CRDTs)** mitigate this by shipping only compact recent state deltas that still merge via $\sqcup$.

### 2. Operation-based CRDTs (CmRDT)

In a **Commutative Replicated Data Type (CmRDT)**, each update runs in two steps: a local `prepare` phase that inspects local state and produces a small operation message, followed by an `effect` phase broadcast to all replicas.

- Concurrent operations must **commute** so applying them in any order yields the same state.
- Bandwidth is much lower than full-state shipping, but the messaging layer must guarantee **exactly-once** (or idempotent) delivery and, for many types, **causal broadcast** order.

## Common CRDT Data Structures

### G-Set (Grow-only Set)
A set supporting only `add(e)` (never removal).
- **State:** A set $S$.
- **Merge:** Set union ($S_1 \cup S_2$), which is naturally commutative, associative, and idempotent.

### G-Counter (Grow-only Counter)
A counter supporting only non-negative increments across $N$ replicas.
- **State:** An array $P$ of length $N$, initialized to zeros. Replica $i$ increments only $P[i] \leftarrow P[i] + 1$.
- **Value:** $\sum_{k=0}^{N-1} P[k]$.
- **Merge:** Element-wise maximum: $P_{\text{merged}}[k] = \max(P_1[k], P_2[k])$.

### PN-Counter (Positive-Negative Counter)
Supports both increment and decrement by pairing two G-Counters: $P$ (increments) and $N$ (decrements).
- **Increment at replica $i$:** $P[i] \leftarrow P[i] + 1$; **Decrement at replica $i$:** $N[i] \leftarrow N[i] + 1$.
- **Value:** $\sum_k P[k] - \sum_k N[k]$.
- **Merge:** Element-wise maximum on both $P$ and $N$ independently.

### OR-Set (Observed-Remove Set)
Supports both `add` and `remove` with deterministic **add-wins** semantics.
- **State:** A set of `(element, unique_tag)` pairs (plus a tombstone set of removed tags in state-based form, or causal version vectors in optimized variants).
- **Add(`e`):** Generates a fresh globally unique tag $t$ and inserts `(e, t)`.
- **Remove(`e`):** Marks all tags for `e` currently *observed* on the local replica as removed.
- **Lookup:** Element `e` is present iff at least one active `(e, t)` tag remains unremoved.

### LWW-Register (Last-Write-Wins Register)
Stores a single value alongside a totally ordered timestamp `(ts, replica_id)`.
- **Update(`v`):** Replaces the local pair with `(v, now(), self_id)`.
- **Merge:** Keeps the pair with the higher timestamp (breaking ties deterministically by `replica_id`).
- Simple and fixed-size, but concurrent writes silently discard the losing value—and wall-clock skew can let an older write overwrite a newer one.

### RGA (Replicated Growable Array) Sequence CRDT
Used in collaborative text editors to maintain an ordered sequence of characters under concurrent edits.
- Each element gets a unique ID (typically `(timestamp, replica_id)`) and is inserted immediately after a predecessor anchor.
- Concurrent inserts at the same anchor are ordered deterministically by their IDs.
- Deletions mark elements with **tombstones** rather than physically removing them so concurrent inserts referencing that anchor still land in the right position.

## Worked Example: PN-Counter and OR-Set Concurrent Merge

**1. PN-Counter across replicas `R1` and `R2`** (vectors `[R1, R2]`):
- Start: `R1` has `P=[0,0], N=[0,0]`; `R2` has `P=[0,0], N=[0,0]`.
- During a partition: `R1` increments twice (`P=[2,0], N=[0,0]`, value `2`). `R2` increments once and decrements once (`P=[0,1], N=[0,1]`, value `0`).
- Merge: `P = max([2,0], [0,1]) = [2,1]`, `N = max([0,0], [0,1]) = [0,1]`.
- Converged value: $(2 + 1) - (0 + 1) = 2$ on both replicas (total: +3 increments, -1 decrement).

**2. OR-Set concurrent add and remove:**
- Both `R1` and `R2` start with `{("apple", t1)}`.
- During a partition: `R1` calls `remove("apple")` (tombstones `t1`), while `R2` calls `add("apple")` (generates fresh tag `t2`, state `{("apple", t1), ("apple", t2)}`).
- Merge: union of adds `{t1, t2}` minus union of tombstones `{t1}` leaves `{("apple", t2)}`. `"apple"` survives because `R1` had not observed `t2`.

## Failure Cases

- **Tombstone bloat:** OR-Sets and RGAs accumulate tombstones indefinitely, inflating memory and merge cost unless causal stability garbage collection prunes tags known to all replicas.
- **Clock skew in LWW-Registers:** A replica with a fast physical clock can silently overwrite newer updates from peers (use HLCs to reduce risk; see [`time-clocks-and-ordering.md`](./time-clocks-and-ordering.md)).
- **Broken transport assumptions in CmRDTs:** Delivering a non-idempotent increment twice over an at-least-once queue permanently corrupts a CmRDT counter.
- **Unenforceable global invariants:** CRDTs cannot prevent two partitioned replicas from each decrementing a bank balance of `$100` by `$80`, resulting in `-$60` after merge.

## Trade-offs

| Approach | Network Requirement | Payload Size | Strong Invariants | Typical Use Case |
| :--- | :--- | :--- | :--- | :--- |
| State-based (CvRDT) | Unreliable / gossip | Large (full state) | No | Dynamo-style counters, shopping carts |
| Delta-state ($\delta$-CRDT) | Unreliable / gossip | Small (deltas) | No | Geo-replicated caches, Riak/Redis CRDTs |
| Op-based (CmRDT) | Reliable + causal | Small (ops) | No | Collaborative editors (Yjs, Automerge) |
| Consensus (Raft/Paxos) | Majority quorum | Log entries | Yes | Ledger balances, unique username claims |

## Interview Traps

- **Claiming CRDTs eliminate all conflicts:** CRDTs only make conflict resolution *automatic and deterministic*; semantic intent can still be lost (e.g., LWW dropping a concurrent edit).
- **Using a CRDT for strict uniqueness or non-negative balances:** Enforcing global invariants requires coordination (consensus or escrow/reservation quotas), not just convergence.
- **Forgetting replica churn in G/PN-Counters:** If ephemeral pods create new replica IDs on every restart, counter vectors grow without bound.
- **Assuming CmRDTs work over plain UDP:** Without reliable, deduplicated, causally ordered delivery, operation-based CRDTs diverge.

## Self-Check Questions

1. Why must a state-based CRDT merge function be commutative, associative, and idempotent, and which network anomaly does each property neutralize?
2. How does a PN-Counter prevent lost updates when two replicas increment concurrently, compared to taking `max(v1, v2)` on a single integer?
3. In an OR-Set, why does a concurrent `add(x)` beat a concurrent `remove(x)`? How would you design a remove-wins set instead?
4. Give one concrete product requirement where a CRDT is a great fit and one where you must choose consensus instead.
