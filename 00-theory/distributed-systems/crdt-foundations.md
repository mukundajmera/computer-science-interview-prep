# Conflict-free Replicated Data Types (CRDTs)

Conflict-free Replicated Data Types (CRDTs) are a family of data structures designed for distributed systems to provide strong eventual consistency. In distributed environments where network partitions, high latency, and concurrent modifications are common, CRDTs enable replicas to diverge temporarily and then merge back together deterministically without requiring centralized coordination or distributed locking. When all replicas have processed the same set of updates, they are mathematically guaranteed to converge to the same state.

## Core Concepts

CRDTs are broadly categorized into two fundamental approaches based on how updates are propagated across the network:

### 1. State-based CRDTs (CvRDT)
Also known as Convergent Replicated Data Types (CvRDT). In this model, each replica maintains its local state. When an update occurs, the replica applies it locally. Periodically, replicas exchange their entire state (or a delta of the state) with each other. Upon receiving a state from a peer, a replica merges it with its own state using a designated merge function.
To guarantee convergence, the merge function must mathematically form a **join semilattice**. This means the merge operation must be:
- **Commutative**: A ∪ B = B ∪ A
- **Associative**: (A ∪ B) ∪ C = A ∪ (B ∪ C)
- **Idempotent**: A ∪ A = A
Because of these properties, the order in which state updates are received and merged does not matter; the final state will always be the same.

### 2. Operation-based CRDTs (CmRDT)
Also known as Commutative Replicated Data Types (CmRDT). Instead of transmitting the entire state, replicas transmit the specific operations (e.g., "add element X", "increment by 5") to other replicas. 
For CmRDTs to converge, the operations themselves must be commutative. Additionally, the messaging infrastructure must guarantee exactly-once delivery (or operations must be idempotent) and sometimes causal ordering, depending on the specific data type. 

## Common CRDT Data Structures

### G-Set (Grow-only Set)
A G-Set is one of the simplest CRDTs. It is a set where elements can only be added, never removed.
- **State**: A standard set data structure.
- **Operation (Add)**: Simply adds the element to the local set.
- **Merge**: The mathematical union of two sets. Since set union is naturally commutative, associative, and idempotent, convergence is guaranteed.
Once an element is added to a G-Set, it remains there forever.

### PN-Counter (Positive-Negative Counter)
A PN-Counter supports both increment and decrement operations. A naive integer counter cannot simply merge values because if two replicas increment simultaneously, choosing the maximum value would lose one increment.
Instead, a PN-Counter is constructed using two Grow-only Counters (G-Counters).
- One G-Counter tracks the increments (P).
- One G-Counter tracks the decrements (N).
Each G-Counter maintains a separate tally for each replica in the system. To find the current value of the PN-Counter, the system calculates the sum of all P values and subtracts the sum of all N values. Merging PN-Counters involves taking the element-wise maximum for both the P and N vectors.

### OR-Set (Observed-Remove Set)
An OR-Set allows both the addition and removal of elements while correctly handling concurrent modifications. 
When an element is added, it is assigned a unique tag (e.g., a UUID). 
- **Add**: Inserts the element along with a newly generated unique tag.
- **Remove**: Removes all tags associated with that element that the removing replica has currently *observed*.
If an element is added by Replica A, and concurrently removed by Replica B, Replica B's removal will only target the tags it knew about. Since Replica A's new tag was not observed by B, the new addition survives the concurrent removal. This provides an "add-wins" semantic.

### RGA (Replicated Growable Array) Sequence CRDT
RGA is a sequence CRDT commonly used in collaborative text editing (where characters form a sequence). It ensures that concurrent inserts and deletes maintain intended relative ordering.
- Each element (or character) is assigned a unique identifier, often containing a timestamp and a replica ID.
- The structure is typically a linked list or tree. Elements are inserted immediately after a specified predecessor (the "reference" element).
- When a concurrent insertion happens at the same position, RGA uses the element identifiers to deterministically break the tie, ensuring all replicas order the elements identically.
- Deletions in RGA are handled by placing a "tombstone" on the element, marking it as removed without physically deleting the node, preserving it as an anchor for past and future operations.
