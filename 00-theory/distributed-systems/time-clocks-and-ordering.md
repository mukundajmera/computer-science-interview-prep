# Time, Clocks, and Ordering in Distributed Systems

In a single-node system, a single hardware clock and shared memory make it straightforward to order events. In a distributed system, independent machines run separate clocks and exchange messages over networks with variable latency. Because physical clocks drift and cannot be synchronized instantaneously, establishing a consistent global order of events requires combining logical causality with bounded physical time.

## The Challenge with Physical Time

Physical clocks rely on quartz crystal oscillators whose frequency varies with temperature, age, and manufacturing tolerances. This causes **clock drift** (clocks ticking at slightly different rates) and **clock skew** (the instantaneous offset between two clocks).

- **Wall-clock (time-of-day) clocks** are synchronized via the Network Time Protocol (NTP). Because network round-trip times are asymmetric and variable, NTP over a LAN typically achieves single-digit millisecond accuracy, and over the public internet can drift by tens of milliseconds.
- **Clock steps vs. slewing:** When NTP detects a large offset, it may jump the wall clock backward or forward. Backward jumps break duration measurements, lease expirations, and timestamp-ordered writes.
- **Monotonic clocks** (such as `CLOCK_MONOTONIC`) never jump backward and are suitable for measuring local elapsed intervals, but their absolute values are meaningless across different machines.

Because skew often exceeds network round-trip time inside a datacenter, ordering events by raw physical timestamps can record an effect with an earlier timestamp than its cause.

## Logical Time and Lamport Clocks

To order events without trusting physical clocks, Leslie Lamport defined the **happens-before** relation ($a \to b$):

1. If $a$ and $b$ occur on the same process and $a$ precedes $b$, then $a \to b$.
2. If $a$ is the sending of a message and $b$ is the receipt of that message, then $a \to b$.
3. Transitivity: if $a \to b$ and $b \to c$, then $a \to c$.

If neither $a \to b$ nor $b \to a$, the events are **concurrent** ($a \parallel b$).

### How Lamport Clocks Work:

1. Each node maintains an integer counter $L$, initialized to `0`.
2. Before executing a local event or sending a message, the node sets $L \leftarrow L + 1$.
3. Every outgoing message carries the sender's current value $L$.
4. Upon receiving a message with timestamp $t$, the receiver updates $L \leftarrow \max(L, t) + 1$.

Lamport clocks satisfy the **clock condition**: $a \to b \implies L(a) < L(b)$. Breaking ties with a unique node identifier `(L(e), node_id)` produces a deterministic total order. However, the converse does **not** hold: $L(a) < L(b)$ does not tell you whether $a$ caused $b$ or whether $a$ and $b$ were concurrent.

## Vector Clocks

Vector clocks capture exact causality by tracking what each node knows about every other node's progress.

### How Vector Clocks Work:

Each of $N$ nodes maintains an array $V$ of length $N$, initialized to all zeros:

1. Before a local event or message send, node $i$ increments its own entry: $V[i] \leftarrow V[i] + 1$.
2. Every outgoing message carries the sender's full vector $V$.
3. Upon receiving a message carrying $V_{\text{msg}}$, node $i$ merges element-wise ($V[k] \leftarrow \max(V[k], V_{\text{msg}}[k])$ for all $k$) and then increments $V[i] \leftarrow V[i] + 1$.

For two vectors $V(a)$ and $V(b)$:
- **$a \to b$** if and only if $\forall k, V(a)[k] \le V(b)[k]$ and $\exists j, V(a)[j] < V(b)[j]$.
- **$a \parallel b$** (concurrent) if neither $V(a) \le V(b)$ nor $V(b) \le V(a)$ holds.

### Worked Example: Three-Node Vector Clock Trace

Consider nodes `A`, `B`, and `C` with vectors formatted as `[A, B, C]`, all starting at `[0, 0, 0]`:

| Step | Node | Event | Vector After Event |
| :--- | :--- | :--- | :--- |
| 1 | A | Local write $e_1$ | `[1, 0, 0]` |
| 2 | A | Send $m_1$ to B ($e_2$) | `[2, 0, 0]` |
| 3 | C | Local write $e_3$ | `[0, 0, 1]` |
| 4 | B | Receive $m_1$ from A ($e_4$): `max([0,0,0],[2,0,0])`, inc B | `[2, 1, 0]` |
| 5 | B | Send $m_2$ to C ($e_5$) | `[2, 2, 0]` |
| 6 | C | Receive $m_2$ from B ($e_6$): `max([0,0,1],[2,2,0])`, inc C | `[2, 2, 2]` |

Comparing vectors confirms:
- $e_1$ (`[1, 0, 0]`) $\to$ $e_4$ (`[2, 1, 0]`) because every coordinate is $\le$ and at least one is strictly smaller.
- $e_2$ (`[2, 0, 0]`) $\parallel$ $e_3$ (`[0, 0, 1]`) because `2 > 0` at index A while `0 < 1` at index C; these writes are concurrent conflicts.
- $e_3$ (`[0, 0, 1]`) $\to$ $e_6$ (`[2, 2, 2]`) and $e_5$ (`[2, 2, 0]`) $\to$ $e_6$ (`[2, 2, 2]`).

## Hybrid Logical Clocks (HLC)

Pure logical clocks cannot answer wall-clock queries ("read state as of 12:00:00 UTC"), while vector clocks grow as $O(N)$ with node count. **Hybrid Logical Clocks** pair a physical component $l$ with a bounded logical counter $c$ in a fixed-size timestamp `(l, c)`:

- On a local event or send, $l' \leftarrow \max(l, pt)$ where $pt$ is local physical time. If $l' = l$, increment $c$; otherwise reset $c \leftarrow 0$.
- On receiving `(l_m, c_m)`, set $l' \leftarrow \max(l, l_m, pt)$. If $l' = l = l_m$, set $c \leftarrow \max(c, c_m) + 1$; if $l' = l$, increment $c$; if $l' = l_m$, set $c \leftarrow c_m + 1$; otherwise reset $c \leftarrow 0$.

HLC preserves Lamport's causal ordering ($a \to b \implies \text{HLC}(a) < \text{HLC}(b)$), fits in 64 bits, and stays closely aligned with physical time for distributed snapshots (used in CockroachDB and YugabyteDB).

## Advanced Concepts: TrueTime

Google Spanner bridges physical and logical ordering with **TrueTime**, an API backed by redundant GPS receivers and atomic clocks in every datacenter. Instead of a single timestamp, `TT.now()` returns a bounded interval `[earliest, latest]` whose half-width $\epsilon$ is typically 1–7 ms.

To guarantee **external consistency** (strict serializability), Spanner assigns a commit timestamp $s = \text{TT.now().latest}$ and performs a **commit wait** until `TT.after(s)` is true (waiting up to $2\epsilon$). Because the transaction does not release locks or report completion until real time has passed $s$, any later transaction $T_2$ that starts after $T_1$ finishes is guaranteed to receive a strictly larger timestamp $s_2 > s_1$.

## Failure Cases

- **NTP backward jump:** Last-Write-Wins (LWW) storage silently drops a newer write whose wall-clock timestamp is smaller than an older write from a faster node.
- **Vector clock metadata explosion:** Dynamic clusters with ephemeral nodes or client-side IDs cause vectors to grow unboundedly unless pruned (which risks losing conflict detection).
- **HLC max-offset breach:** A rogue node with a clock far in the future drags other nodes' $l$ forward; production systems reject messages whose $l_m - pt$ exceeds a configured `max_offset` threshold.
- **TrueTime uncertainty spike:** If GPS antennas fail and atomic clocks drift, $\epsilon$ widens, directly increasing write latency via longer commit waits.

## Trade-offs

| Mechanism | Size | Detects Concurrency | Wall-Clock Alignment | Primary Cost |
| :--- | :--- | :--- | :--- | :--- |
| Physical / NTP | $O(1)$ | No | Yes (skewed) | Silent causality violations |
| Lamport Clock | $O(1)$ | No | No | Cannot distinguish causal vs. concurrent |
| Vector Clock | $O(N)$ | Yes | No | Metadata grows with actors/nodes |
| Hybrid Logical Clock | $O(1)$ | No | Yes (bounded) | Requires bounded clock skew (`max_offset`) |
| TrueTime + Commit Wait | $O(1)$ | External order | Yes ($\pm\epsilon$) | Specialized hardware + $2\epsilon$ write wait |

## Interview Traps

- **Claiming Lamport clocks detect concurrency:** They only guarantee $a \to b \implies L(a) < L(b)$, never the reverse.
- **Using wall-clock time for leases or timeouts:** Always specify a monotonic clock for local elapsed durations; wall clocks can jump backward.
- **Confusing vector clocks with version vectors:** Vector clocks track all events across nodes; version vectors track replica state versions for conflict detection in key-value stores (see [`quorum-consistency-and-anti-entropy.md`](./quorum-consistency-and-anti-entropy.md)).
- **Assuming TrueTime eliminates clock skew:** TrueTime does not make skew zero; it *bounds* skew and trades commit latency ($2\epsilon$) for strict ordering.

## Self-Check Questions

1. Why can two events have $L(a) < L(b)$ in a Lamport clock yet still be causally independent?
2. In the worked vector clock example, what would `C`'s vector be if `C` received $m_2$ *before* executing its local write $e_3$, and how would that change the relationship between $e_2$ and $e_3$?
3. Why does an HLC node crash or reject messages when a peer's physical timestamp exceeds `local_pt + max_offset`?
4. How does Spanner's commit wait enforce external consistency without requiring a global coordinator for every read?
