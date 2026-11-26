# Atomic Commit Protocols in Distributed Systems

In distributed systems, an atomic commit protocol is a mechanism that ensures a transaction is either applied across all participating nodes or applied on none at all, thus preserving the ACID (Atomicity, Consistency, Isolation, Durability) properties, particularly Atomicity. In this document, we discuss the Two-Phase Commit (2PC) and Three-Phase Commit (3PC) protocols, highlighting their mechanisms, failure handling, and operational differences.

## Two-Phase Commit (2PC)

The Two-Phase Commit (2PC) protocol is the foundational distributed consensus algorithm used by databases and transaction coordinators to commit a transaction across multiple participants safely. It involves a coordinator node and several participant nodes.

### Protocol Steps
As the name suggests, the protocol operates in two primary phases:

1. **Phase 1: Prepare Phase (Voting)**
   - The coordinator sends a `PREPARE` request to all participants involved in the transaction.
   - Each participant evaluates if it can safely commit the transaction (e.g., checking locks, writing records to its Write-Ahead Log).
   - If a participant can commit, it responds with a `YES` (or `VOTE_COMMIT`).
   - If a participant encounters an issue and cannot commit, it responds with a `NO` (or `VOTE_ABORT`).

2. **Phase 2: Commit Phase (Decision)**
   - If the coordinator receives a `YES` from **all** participants, it records the decision in its log and sends a `COMMIT` request to all participants.
   - If the coordinator receives at least one `NO` vote, or if a timeout occurs waiting for votes, it decides to abort and sends an `ABORT` message to all participants.
   - The participants then execute the final decision (either committing or rolling back) and send an `ACK` (acknowledgment) to the coordinator. The coordinator finally marks the transaction as complete.

### Vulnerabilities and Blocking
The most significant limitation of 2PC is that it is a **blocking** protocol. 
- If the coordinator crashes after sending the `PREPARE` message and the participants have voted `YES`, the participants must remain in a waiting state (blocked) until the coordinator recovers. During this blocked state, the participants are holding locks on the resources, reducing the system's availability.
- There is a critical window where if the coordinator and a single participant fail simultaneously during the commit phase, the remaining participants cannot determine whether to commit or abort, requiring manual intervention or waiting indefinitely.

## Three-Phase Commit (3PC)

To mitigate the blocking nature of 2PC, the Three-Phase Commit (3PC) protocol was introduced. 3PC is designed to be non-blocking in the event of site failures (except in the case of widespread concurrent network partitions).

### Protocol Steps
3PC introduces an intermediate phase between the Prepare and Commit phases, resulting in three distinct phases:

1. **Phase 1: CanCommit Phase (Voting)**
   - The coordinator sends a `CAN_COMMIT` message to the participants.
   - Participants vote `YES` if they are ready and willing to commit; otherwise, they vote `NO`. This phase ensures that all nodes are available before proceeding.

2. **Phase 2: PreCommit Phase (Preparation)**
   - If the coordinator receives `YES` votes from all participants, it logs a pre-commit state and sends a `PRE_COMMIT` message.
   - Participants acknowledge the `PRE_COMMIT` message. Crucially, at this point, participants *know* that a unanimous `YES` decision was reached. They transition to a prepared state but do not yet commit the transaction permanently.

3. **Phase 3: DoCommit Phase (Finalization)**
   - Upon receiving acknowledgments for the `PRE_COMMIT` from all participants, the coordinator sends the final `DO_COMMIT` message.
   - Participants finally apply the transaction permanently, release any locks, and acknowledge the completion.

### How 3PC Prevents Blocking
The intermediate PreCommit phase allows 3PC to avoid the indefinite blocking flaw of 2PC. 
- In 3PC, if the coordinator fails before the PreCommit phase is acknowledged, the participants will safely abort the transaction upon a timeout.
- If the coordinator fails after the PreCommit phase has been acknowledged by participants, a newly elected coordinator (or the participants themselves) can safely deduce that a commit was intended, and the system can progress to commit the transaction without being blocked indefinitely.

While 3PC provides better fault tolerance by removing the blocking behavior under certain failure scenarios, it incurs higher latency due to the extra round trips of communication. As a result, 3PC is less commonly used in practice compared to consensus algorithms like Paxos or Raft, which provide more robust fault tolerance in modern distributed systems.
