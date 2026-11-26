# Distributed Consensus: Raft Protocol - Interview Q&A

**1. How does Raft ensure Election Safety, meaning only one leader can be elected in a given term?**
Raft guarantees election safety through a combination of mechanisms. First, a candidate must secure votes from a strict majority of the cluster to win an election. Second, each node is allowed to cast at most one vote per term, granted on a first-come, first-served basis. Because a majority is required and each node votes only once, it is mathematically impossible for two different candidates to both secure a majority in the same term.

**2. Explain the "Split Vote" problem in leader election and how Raft mitigates it.**
A split vote occurs when multiple followers become candidates simultaneously, dividing the votes such that no single candidate achieves a majority. If left unaddressed, this could lead to repeated failed elections and loss of availability. Raft mitigates this using randomized election timeouts. By randomly assigning timeouts (e.g., between 150ms and 300ms), it's highly probable that one node will time out and start an election before the others. This node will likely gather the majority of votes before other nodes' timers expire.

**3. What is the role of `prevLogIndex` and `prevLogTerm` in the `AppendEntries` RPC?**
These fields serve as an consistency check. When a leader sends new entries, it includes the index and term of the log entry immediately preceding the new ones. The follower checks its own log; if it doesn't have an entry with `prevLogIndex` matching `prevLogTerm`, it rejects the request. This induction step guarantees that if the new entries are appended, the follower's log is identical to the leader's up through the new entries (Log Matching property).

**4. A network partition isolates a follower. It repeatedly times out and increments its term. When the partition heals, its term is much higher than the current leader's term. What happens, and how can this disruption be prevented?**
When the partitioned node rejoins, its high term will force the current legitimate leader to step down and revert to a follower, causing an unnecessary election and brief unavailability. This is prevented by the **Pre-Vote extension**. In Pre-Vote, before a node increments its term to start a real election, it asks others if they *would* vote for it. Since the isolated node cannot reach a majority, the pre-vote fails, and it never increments its term, preventing disruption when it rejoins.

**5. Why can't a Raft leader safely commit entries from a previous term simply by counting replicas? (The "Figure 8" problem)**
A leader might replicate an entry from a previous term to a majority, but if it crashes before committing it, a new leader could emerge and overwrite that entry with its own. If the first leader assumed the entry was safe just by counting replicas, it would violate safety. Therefore, a leader is only permitted to count replicas for entries created in its *current* term. Once a current-term entry is committed, the Log Matching property implicitly ensures all preceding entries (even from older terms) are also safely committed.

**6. How does Raft handle a follower whose log is inconsistent with the leader's log?**
The leader maintains a `nextIndex` for each follower, initialized to the leader's next log index. If a follower rejects an `AppendEntries` RPC (due to the consistency check failing), the leader decrements the `nextIndex` for that follower and retries the RPC with the preceding entries. This process repeats until the logs match. The leader then forces the follower to overwrite any conflicting entries with the leader's authoritative entries.

**7. Compare the log structure of Raft and Multi-Paxos. What are the trade-offs?**
Raft enforces a strictly contiguous log sequence; entries must be appended and committed in order, leaving no "holes". This simplifies reasoning and implementation but can create a bottleneck if a single entry is delayed. Multi-Paxos allows consensus on instances out-of-order, potentially creating holes in the log. While this can offer higher concurrency for independent operations, it significantly complicates the state machine application, as it must wait for holes to be filled before processing subsequent entries.

**8. How does Raft perform log compaction to prevent infinite disk growth?**
Raft uses snapshotting. Each server independently takes a snapshot of its state machine's current state up to a certain committed index and discards the log entries prior to that index. If a follower is very slow or restarts and needs entries the leader has already discarded, the leader sends an `InstallSnapshot` RPC to bring the follower up to date in one large step.

**9. Explain how Joint Consensus is used for cluster membership changes in Raft.**
Transitioning directly from an old configuration to a new one is unsafe, as disjoint majorities could elect two leaders. Joint Consensus introduces an intermediate configuration where decisions require majorities from *both* the old and the new configurations. The leader appends this `C_old,new` configuration to the log. Once committed, the cluster uses joint consensus. Then, the leader appends the final `C_new` configuration. This two-phase approach ensures safety during the transition without halting client requests.

**10. What is "Leader Completeness" and why is it critical for Raft's safety?**
Leader Completeness is the property that if a log entry is committed in a given term, that entry will absolutely be present in the logs of the leaders for all higher-numbered terms. This is guaranteed by the voting rules: a candidate must have a log at least as up-to-date as the voters, and a committed entry exists on a majority. Since majorities intersect, any new leader must have received a vote from at least one node containing the committed entry. This ensures committed data is never lost or overwritten.

**11. Why does serving reads directly from a Raft leader's local memory potentially violate linearizability?**
If a leader is partitioned from the majority of the cluster, the majority may elect a new leader and commit new writes. The partitioned, old leader might not realize it has been deposed. If it serves read requests directly from its local state machine, it will return stale data that does not reflect the newly committed writes, violating the linearizability guarantee that a read must observe the latest completed write.

**12. How does the naive approach solve the linearizable read problem in Raft, and what is its major drawback?**
The naive approach treats every read request as a write. The leader appends a "read command" to the Raft log, replicates it to the majority via `AppendEntries`, and waits for it to be committed before returning the result from its state machine. While this guarantees linearizability, its major drawback is high latency and significant disk write overhead (fsyncing to stable storage) for purely read-only operations, severely limiting read throughput.

**13. Explain the ReadIndex protocol and how it achieves linearizable reads without disk writes.**
The ReadIndex protocol avoids disk writes by relying on network communication. When a leader receives a read request, it records its current `commitIndex` as `read_index`. It then sends a round of empty heartbeat `AppendEntries` to a majority to confirm it is still the authoritative leader. Once confirmed, it waits until its local state machine's `lastApplied` index reaches or exceeds the `read_index`. Finally, it executes the read against its state machine. This guarantees the read observes all writes committed prior to the request, satisfying linearizability with zero disk I/O.

**14. What is the LeaseRead protocol, and what trade-off does it introduce compared to ReadIndex?**
LeaseRead further optimizes reads by eliminating the network roundtrip required by ReadIndex to confirm leadership. When a leader receives heartbeat acknowledgments from a majority, it establishes a time-based lease (shorter than the election timeout). During this lease, it assumes it is the sole leader and serves reads immediately from memory (after ensuring its state machine is up to the `commitIndex`). The crucial trade-off is that it relies on bounded physical clock drift. If the leader's clock skews and runs slower than others, it might serve stale reads after a new leader has been elected, breaking linearizability.

**15. How can a Raft cluster support linearizable Follower Reads to scale read throughput?**
To safely read from a follower, the follower must ensure it has the latest state. When a client sends a read to a follower, the follower requests the current safe `commitIndex` (the `read_index`) from the leader (which the leader obtains via ReadIndex or LeaseRead). The follower then waits until its own local state machine applies up to that `read_index`. Only then does it execute the read locally. This distributes read execution while preventing stale reads from lagging followers.

**16. Why is transitioning cluster membership directly from a 3-node to a 5-node configuration unsafe in Raft?**
A direct transition is unsafe because it can lead to a disjoint majority. During the transition, some nodes might be operating under the old 3-node configuration ($C_{old}$) while others operate under the new 5-node configuration ($C_{new}$). A subset of 2 nodes could form a majority under $C_{old}$ and elect Leader A, while a different subset of 3 nodes could form a majority under $C_{new}$ and elect Leader B. These two leaders could commit conflicting entries, violating safety.

**17. How does Joint Consensus ensure safety during dynamic membership changes?**
Joint Consensus introduces an intermediate configuration ($C_{old,new}$) where decisions require majorities from *both* the old and the new configurations. The leader appends this joint configuration to the log. Once a node has this entry, it requires both majorities for elections and commits. This makes it impossible for independent majorities to form. Once the $C_{old,new}$ entry is committed, the leader safely transitions the cluster to the final $C_{new}$ configuration.

**18. What are the benefits of batching and pipelining in a production Raft implementation?**
Batching groups multiple concurrent client requests into a single `AppendEntries` RPC, amortizing network overhead and significantly reducing the number of expensive disk fsync operations required per request. Pipelining allows a leader to send multiple `AppendEntries` RPCs to a follower simultaneously without waiting for acknowledgments. This circumvents the network latency bottleneck of a stop-and-wait approach, drastically increasing the overall throughput of log replication.
