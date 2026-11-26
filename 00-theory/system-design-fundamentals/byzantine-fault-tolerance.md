# Byzantine Fault Tolerance (BFT) vs Crash-Fault Tolerance (CFT)

In distributed systems, components can fail. The *manner* in which they fail determines the complexity of achieving consensus (agreement among nodes). This guide covers the evolution from Crash-Fault Tolerance (CFT) to Byzantine Fault Tolerance (BFT), explaining the fundamental math and modern protocols.

---

## 1. Failure Models

Understanding distributed consensus begins with defining what a "failure" actually means. We classify failures into three primary models:

### Fail-Stop
- **Definition:** A node halts completely and permanently. Other nodes in the network can reliably detect that the node has stopped.
- **Example:** A server loses power and a hardware watchdog immediately broadcasts a failure signal.
- **Complexity:** Easiest to handle. If a node is gone, the rest simply proceed without it.

### Crash-Recovery (CFT)
- **Definition:** A node crashes, halts execution, and loses its volatile state, but it might recover later (potentially with intact persistent storage). The system must reach consensus despite these temporary or permanent crashes. Crucially, crashed nodes *do not lie or send malicious messages*.
- **Example:** A database node crashes due to an out-of-memory error and restarts seconds later.
- **Complexity:** Harder than fail-stop. Algorithms like Paxos and Raft are designed for this. They ensure consistency as long as a quorum of honest, non-faulty nodes is available.

### Byzantine / Arbitrary (BFT)
- **Definition:** A node can fail in *any conceivable way*. It might crash, it might send conflicting messages to different peers, it might forge responses, or it might actively collude with other faulty nodes to break the system. The term originates from the "Byzantine Generals Problem" (Lamport, Pease, and Shostak).
- **Example:** A compromised server in a blockchain network sends malicious transactions, or a faulty router flips random bits in packets.
- **Complexity:** The hardest model. Reaching consensus requires sophisticated protocols that can tolerate active malice or completely unpredictable hardware corruption.

---

## 2. Mathematical Proof of Bounds: CFT vs BFT

The fault tolerance of a system is defined by $f$, the maximum number of faulty nodes the system can tolerate out of a total of $N$ nodes.

### Crash-Fault Tolerance (CFT): $N \ge 2f + 1$
In a CFT system (like Raft or Paxos), we need a **simple majority** (quorum) to make decisions.
- If $f$ nodes crash, we need to ensure the remaining nodes can still form a majority to make progress.
- The remaining nodes must be at least $f + 1$ to form a majority over the $f$ failed nodes.
- Therefore, the total number of nodes required is $N = f + (f + 1) = 2f + 1$.
- **Proof intuition:** Any two quorums of size $f + 1$ must intersect by at least one node. Since nodes do not lie, this single overlapping node guarantees that the newest state is preserved across quorums.

### Byzantine Fault Tolerance (BFT): $N \ge 3f + 1$
In a BFT system, we cannot rely on simple majorities because faulty nodes can lie. Pease, Shostak, and Lamport proved that no solution exists for $N \le 3f$.
- Assume a system with $N$ nodes. A client waits for a quorum of responses to confirm an action.
- Since $f$ nodes might simply crash or remain silent, the client can only wait for $N - f$ responses to avoid waiting forever.
- Out of these $N - f$ responses, up to $f$ could be from malicious Byzantine nodes that are actively lying.
- To ensure the truth prevails, the number of *honest* responses in the received quorum must strictly outnumber the *malicious* responses.
- Honest responses in quorum = $(N - f) - f = N - 2f$.
- We require: Honest > Malicious $\implies N - 2f > f \implies N > 3f$.
- Therefore, the minimum number of nodes is $N = 3f + 1$.
- **Proof intuition:** Any two quorums of size $2f + 1$ must intersect by at least $f + 1$ nodes. Even if all $f$ faulty nodes are part of this intersection and lie, the $1$ remaining honest node in the intersection guarantees safety.

---

## 3. Practical Byzantine Fault Tolerance (PBFT)

Proposed by Miguel Castro and Barbara Liskov in 1999, PBFT was the first protocol to make BFT practical for asynchronous systems (like the internet) by reducing the overhead to polynomial time.

### Core Mechanics
PBFT operates through a sequence of **views**. In each view, one node is the **primary** (leader), and the others are **backups**. If the primary fails or acts maliciously, the system executes a **view change** to elect a new primary.

### The 3-Phase Consensus Protocol
To agree on a request (e.g., a client transaction), PBFT uses a three-phase exchange:

1. **Pre-Prepare Phase:**
   - The primary receives a request, assigns it a sequence number, and multicasts a `<<PRE-PREPARE>>` message to all backups.
   - *Goal:* Propose an ordering.

2. **Prepare Phase:**
   - A backup receives a valid `<<PRE-PREPARE>>`. It accepts it and multicasts a `<<PREPARE>>` message to all other nodes.
   - Each node waits until it collects $2f$ matching `<<PREPARE>>` messages from different nodes (including its own).
   - *Goal:* Achieve a consistent ordering globally. Once a node has $2f$ matching prepares, it has a **prepared certificate**. This guarantees that no other valid request can commit with the same sequence number in the current view.

3. **Commit Phase:**
   - Upon obtaining a prepared certificate, a node multicasts a `<<COMMIT>>` message.
   - Each node waits until it collects $2f + 1$ matching `<<COMMIT>>` messages (including its own).
   - *Goal:* Ensure durability across view changes. Once a node has $2f + 1$ commits (a **commit certificate**), the request is definitively ordered and the node executes the operation, replying to the client.

The client waits for $f + 1$ matching replies from different nodes to ensure the result is correct (even if $f$ nodes lied, at least one is honest).

---

## 4. Modern Evolutions & Comparisons

While PBFT was a breakthrough, its heavy communication overhead made it difficult to scale to hundreds or thousands of nodes. Modern blockchains and decentralized systems have evolved BFT significantly.

### Communication Complexity: CFT vs PBFT
- **CFT (e.g., Raft):** The leader dictates state. Followers simply ack. Complexity is **$O(N)$**.
- **PBFT:** Every node talks to every other node in the Prepare and Commit phases (all-to-all broadcast). Complexity is **$O(N^2)$**. This limits classic PBFT networks to small sizes (typically $N < 100$).

### Tendermint BFT
- Created for the Cosmos ecosystem.
- Simplifies PBFT by merging the leader election and block commitment processes.
- Uses a round-robin leader selection. If a leader fails, a fast timeout triggers the next leader's turn.
- Trades liveness for safety: it will halt rather than fork if the network partitions.

### HotStuff (Pipelined Consensus)
- Used in systems like Aptos and Sui (formerly Facebook's Libra/Diem).
- **Key Innovation:** Introduces a rotating leader model and linearizes the communication. Instead of all-to-all broadcast, nodes send their votes to the next leader, who aggregates them into a **Quorum Certificate (QC)** using threshold signatures.
- **Complexity:** Reduces communication complexity from $O(N^2)$ to **$O(N)$**.
- Pipelining allows phases of different proposals to overlap, drastically increasing throughput.

---

## Summary Trade-offs

| Feature | Crash-Fault Tolerance (CFT) | Byzantine Fault Tolerance (BFT) |
|---------|-----------------------------|---------------------------------|
| **Adversary** | Nodes crash but do not lie. | Nodes can act maliciously and collude. |
| **Node Requirement** | $N \ge 2f + 1$ | $N \ge 3f + 1$ |
| **Primary Use Case** | Internal corporate systems, databases (Raft, Paxos). | Public networks, Blockchains, untrusted environments. |
| **Complexity** | $O(N)$ typically. | Historically $O(N^2)$ (PBFT), modernly $O(N)$ (HotStuff). |
