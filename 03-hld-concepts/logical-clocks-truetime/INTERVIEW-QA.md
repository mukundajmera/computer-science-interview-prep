# Logical Clocks & TrueTime - Interview Q&A

### 1. The LWW Data Loss Problem
**Question:** In a distributed key-value store using Last-Write-Wins (LWW) with physical timestamps, how can data be silently lost, and how do logical clocks prevent this?

**Say:** "If Node A processes a write but its physical clock is lagging behind Node B's clock, a subsequent causal update to the same key on Node A might be assigned an older timestamp than Node B's previous write. LWW will silently discard Node A's new write. Logical clocks, like Vector Clocks, prevent this by explicitly tracking causal history. Instead of blindly overwriting based on time, the system detects concurrent divergence and surfaces both values to the client for deterministic conflict resolution."

### 2. Lamport Clocks vs Vector Clocks
**Question:** If Lamport timestamps guarantee a total ordering of events, why do systems like Dynamo use Vector Clocks instead?

**Say:** "Lamport clocks provide a total ordering, but they cannot detect concurrency. If L(A) < L(B), we don't know if A causally preceded B or if they occurred concurrently in different partitions. Vector Clocks maintain an array of counters, allowing us to perform a component-wise comparison. This explicit comparison allows the system to definitively identify whether two writes are causally sequential or if they represent a concurrent conflict that requires sibling resolution."

### 3. Spanner's External Consistency
**Question:** Google Spanner claims 'External Consistency'. How does this differ from standard serializability, and how does TrueTime enable it?

**Say:** "Standard serializability guarantees that concurrent transactions appear to execute in *some* sequential order, but that order doesn't have to match real-world physical time. External consistency (or linearizability) guarantees that if Transaction 1 commits before Transaction 2 begins in absolute wall-clock time, Transaction 2 will see Transaction 1's writes. TrueTime enables this via the 'commit wait' protocol: a transaction chooses a commit timestamp and blocks until it is absolutely certain that real time has passed that timestamp, ensuring no future transaction can overlap its timestamp."

### 4. TrueTime Hardware Architecture
**Question:** Why does TrueTime rely on both GPS and Atomic clocks? Why not just use one?

**Say:** "They have different failure domains. GPS receivers provide excellent global synchronization but are vulnerable to antenna failures, atmospheric interference, or spoofing. Atomic clocks are highly reliable and immune to external interference, but they slowly drift over time. By combining them, Spanner cross-checks the sources: the atomic clock bounds the drift if the GPS signal is temporarily lost, and the GPS corrects the long-term drift of the atomic clock."

### 5. Managing Vector Clock Bloat
**Question:** A major criticism of Vector Clocks is that the vector size grows with the number of nodes or clients. How do systems like Riak or Dynamo mitigate this bloat?

**Say:** "Vector clock bloat is mitigated through pruning strategies. Systems limit the size of the vector by evicting the oldest entries based on a physical timestamp threshold or a maximum vector length. Additionally, modern implementations often use Dotted Version Vectors (DVVs) or server-side ID mapping, which track causality at the replica level rather than the client level, strictly bounding the vector size to the replication factor."

### 6. Causal Consistency vs Linearizability
**Question:** How does Causal Consistency differ from Linearizability, and when would you choose one over the other?

**Say:** "Linearizability is a strong, single-system-image guarantee where every read sees the absolute latest write, requiring synchronous coordination (like Spanner) and sacrificing availability during partitions (CAP theorem). Causal Consistency is weaker; it only guarantees that operations causally related are seen in that order, but concurrent operations can be seen in any order. I would choose Causal Consistency for highly available, multi-region systems like social feeds, and Linearizability for financial ledgers or inventory systems."

### 7. Spanner's Commit Wait Latency
**Question:** Spanner's Commit Wait rule requires transactions to block for the duration of the uncertainty window (epsilon). Doesn't this ruin write latency?

**Say:** "It does add a latency floor to writes, typically between 1 to 7 milliseconds. However, Spanner overlaps this wait time with the network round-trips required for Two-Phase Commit and Paxos replication. In many cases, the time taken to achieve consensus and durability exceeds the epsilon wait time, effectively hiding the commit wait latency from the client."

### 8. Handling TrueTime Outages
**Question:** What happens to Google Spanner if the TrueTime uncertainty window (epsilon) spikes massively due to hardware failure?

**Say:** "If epsilon spikes, Spanner prioritizes safety over latency. The system will continue to guarantee external consistency, but the commit wait times will increase proportionally to the uncertainty window. Write latency will degrade significantly, and if epsilon exceeds a safety threshold, Spanner nodes may self-fence or reject writes until accurate timekeeping is restored, effectively degrading into unavailability rather than serving inconsistent data."

### 9. Clock Slew vs Step
**Question:** When running a distributed database like Cassandra, why is it critical that NTP is configured to 'slew' the clock rather than 'step' it?

**Say:** "Stepping the clock forces an immediate jump to the correct time, which can move the clock backwards. This violates the assumption of monotonic time progression and can cause major issues: scheduled background tasks might fire repeatedly or not at all, and LWW resolution might incorrectly drop newer data. Slewing slowly adjusts the tick rate to catch up or slow down, ensuring the clock remains monotonic and preventing disruptive jumps."

### 10. The Sibling Explosion Problem
**Question:** What is the 'sibling explosion' problem in standard Version Vectors, and how do Dotted Version Vectors (DVV) solve it?

**Say:** "In standard Version Vectors, if clients perform concurrent writes during a network partition, the system may struggle to merge them later, falsely generating massive numbers of conflicting versions (siblings). Dotted Version Vectors solve this by explicitly separating the causal history (the context) from the specific new update (the dot). This precise tracking prevents the system from conflating causally sequential updates as concurrent conflicts, drastically reducing false siblings."