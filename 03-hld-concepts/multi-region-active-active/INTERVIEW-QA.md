# Multi-Region Active-Active Replication - Interview Q&A

## Q1: What is the primary motivation for adopting a multi-region active-active architecture?
**A:** The primary motivations are reducing latency for a globally distributed user base and maximizing availability/fault tolerance. By having active data centers in multiple regions, users can be routed to the closest region, minimizing network round trips. Additionally, if an entire region experiences an outage, traffic can seamlessly fail over to other active regions without service interruption.

## Q2: How does Active-Active replication differ from Active-Passive (Single-Leader) replication?
**A:** 
*   **Active-Active (Multi-Leader or Master-Master):** All regions can accept both read and write requests concurrently. Writes are asynchronously replicated to other regions. This provides low latency for writes everywhere but introduces the challenge of conflict resolution and eventual consistency.
*   **Active-Passive (Single-Leader):** Only one region (the leader/active node) accepts writes. All other regions (followers/passive nodes) only accept reads. Writes must be routed to the leader region, which can introduce high latency for users far away from the leader. However, it avoids write conflicts since there is only a single source of truth for writes.

## Q3: What is a "split-brain" scenario, and why is it dangerous in an active-active setup?
**A:** A split-brain scenario occurs during a network partition where two or more active regions lose communication with each other. Because they are active-active, they continue to independently accept reads and writes from users in their respective areas. This causes the data states in the disconnected regions to diverge. It is dangerous because when the network partition is resolved, the system must merge these divergent states. Without robust conflict resolution mechanisms, this merge can result in massive data corruption or data loss.

## Q4: Describe the LWW (Last-Write-Wins) conflict resolution strategy and its primary drawback.
**A:** LWW resolves concurrent updates to the same data record by comparing the timestamps of the conflicting writes. The write with the most recent (highest) timestamp "wins" and overwrites the others. 
Its primary drawback is data loss. The "losing" writes are completely discarded, even if they contained distinct, valuable updates. Furthermore, it relies heavily on synchronized clocks across regions; clock drift (e.g., due to NTP synchronization issues) can lead to older writes unfairly overwriting newer ones.

## Q5: What is a CRDT (Conflict-free Replicated Data Type) and how does it solve LWW's issues?
**A:** A CRDT is a specialized data structure designed such that concurrent updates can be merged deterministically without requiring coordination or causing data loss. Unlike LWW, which drops conflicting writes, CRDTs merge the state or operations mathematically. 
For example, if two regions concurrently add different items to a shopping cart (represented by an OR-Set CRDT), the merge operation guarantees that both items will exist in the final state, preserving all data rather than discarding one update based on a timestamp.

## Q6: Is an active-active architecture suitable for all types of applications? Why or why not?
**A:** No, it is not suitable for all applications. Active-active architectures inherently rely on eventual consistency due to the asynchronous nature of replication. Applications that require strict serializability or strong consistency (e.g., core financial ledgers, double-entry bookkeeping, inventory systems preventing overselling) are usually better suited for single-leader or distributed consensus architectures (like Paxos or Raft-based systems, e.g., Spanner). Active-active is ideal for applications where availability and low latency outweigh strict consistency, such as user profiles, social media feeds, or shopping carts.
