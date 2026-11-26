# Distributed Storage Consensus Flashcards

40 question-only flashcards for distributed storage consensus mechanisms.

---

## Raft Consensus (15 Cards)

### Card 1
Front: What are the three primary subproblems that the Raft consensus algorithm decomposes consensus into?

### Card 2
Front: In Raft, what are the three possible states a server can operate in at any given time?

### Card 3
Front: What condition must be met for a Follower to transition into a Candidate state in Raft?

### Card 4
Front: How does Raft utilize "Term numbers" during leader elections?

### Card 5
Front: Explain the role of randomized election timeouts in Raft's leader election process.

### Card 6
Front: What is the primary purpose of empty AppendEntries RPCs in Raft?

### Card 7
Front: In a Raft RequestVote RPC, how does a server determine if a candidate's log is "at least as up-to-date" as its own?

### Card 8
Front: What happens in Raft if a split vote occurs during an election term?

### Card 9
Front: Explain the concept of the "Log Matching Property" in Raft.

### Card 10
Front: How does a Raft leader handle log inconsistencies with a follower that has conflicting entries?

### Card 11
Front: In Raft, what does it mean for a log entry to be considered "committed"?

### Card 12
Front: How does Raft handle a network partition that isolates the current leader from the majority of the cluster?

### Card 13
Front: What mechanism does Raft use to ensure cluster membership changes (like adding or removing nodes) do not compromise safety?

### Card 14
Front: Describe the process of log compaction (snapshotting) in a Raft cluster.

### Card 15
Front: What is the significance of the `nextIndex` array maintained by the Raft leader?

---

## Paxos Consensus (15 Cards)

### Card 16
Front: What is the fundamental difference in the network model assumptions between Paxos and Byzantine Fault Tolerance (BFT) algorithms?

### Card 17
Front: Describe the three core mathematical guarantees (invariants) of any valid consensus algorithm like Paxos.

### Card 18
Front: In Classic Single-Decree Paxos, what are the three distinct logical roles that nodes can take?

### Card 19
Front: What happens during the "Prepare" phase (Phase 1) of Classic Paxos?

### Card 20
Front: In Paxos, what constraint is placed on a Proposer when selecting a value for the "Accept" phase (Phase 2)?

### Card 21
Front: Explain how Paxos resolves a scenario where multiple proposers attempt to propose values simultaneously (dueling proposers).

### Card 22
Front: What is Multi-Paxos, and how does it optimize the Classic Paxos protocol?

### Card 23
Front: Why is a distinguished "Leader" often elected in Multi-Paxos deployments?

### Card 24
Front: In Paxos, what is the significance of proposal numbers being globally unique and monotonically increasing?

### Card 25
Front: How does an Acceptor in Paxos decide whether to accept or reject a `Prepare` request?

### Card 26
Front: Can a decided value in Paxos ever be changed or overwritten? Why or why not?

### Card 27
Front: Compare the leader election dependency between Multi-Paxos and Raft.

### Card 28
Front: What is "Fast Paxos" and how does it reduce latency compared to Classic Paxos?

### Card 29
Front: What are the primary trade-offs of using Paxos over a two-phase commit (2PC) protocol for distributed transactions?

### Card 30
Front: Explain the concept of "liveness" in Paxos and how the FLP Impossibility Result impacts it.

---

## Quorum and General Consensus (10 Cards)

### Card 31
Front: What is a "quorum" in distributed consensus, and why is a strict majority typically required?

### Card 32
Front: In a 7-node consensus cluster, how many node failures can the system tolerate while maintaining availability?

### Card 33
Front: What is the split-brain problem in distributed storage, and how does consensus prevent it?

### Card 34
Front: How do distributed configuration stores like ZooKeeper (ZAB) or etcd (Raft) utilize consensus for linearizability?

### Card 35
Front: Describe the difference between strong consistency (linearizability) and eventual consistency in distributed storage.

### Card 36
Front: What role does a distributed consensus algorithm play in state machine replication (SMR)?

### Card 37
Front: Why might a distributed system choose to implement Leaderless consensus (like Dynamo) instead of Leader-based consensus (like Raft)?

### Card 38
Front: How does read latency differ between strongly consistent reads requiring consensus versus stale reads in a distributed storage system?

### Card 39
Front: What is the impact of network latency (e.g., cross-region deployments) on consensus algorithm performance?

### Card 40
Front: Explain the concept of an "epoch" or "term" in consensus protocols and its role in isolating stale leaders.
