# Strong Answer: Instagram Core

**Pacing Target:** 45 minutes

## 1. Introduction & Requirements Gathering (0-5 minutes)

**Say:** "To design the Instagram Core, I will focus on modeling the core entities for a photo/video posting and feed composition system, defining the interfaces, and ensuring thread-safe operations under high concurrency. I'll begin by outlining the core data models for the follow-graph and media posts, then progress to the feed composition architecture, and finally address scale and synchronization. Our primary goal is to ensure consistency for feed generation and deterministic behavior for timeline views."

By establishing these constraints early, we frame the discussion around concrete engineering trade-offs. The high-level requirements dictate a system capable of handling substantial follow-graph reads while maintaining precise state transitions for posts, unfollows, and privacy changes.

## 2. Entity Modeling & Core Components (5-15 minutes)

**Say:** "Let's discuss the entity modeling. The core entities I have identified include User, Post, FollowGraph, and FeedComposer. Each of these entities is designed to encapsulate both state and behavior. For instance, we ensure that mutable state like a user's follow list or privacy settings is properly encapsulated and accessed only via concurrent wrappers where necessary to maintain isolation."

When modeling these entities, the system relies on clear separation of concerns. Post and FollowGraph must maintain referential integrity, especially when unfollow/delete/privacy transitions remove unauthorized posts. The relationships between these entities are carefully managed using robust data access layers. We also define clear boundaries and interfaces so that different subdomains can interact without tight coupling.

## 3. Design Pattern Justifications (15-25 minutes)

**Say:** "In terms of design patterns, I've incorporated the Strategy Pattern for feed ranking algorithms and the Observer Pattern to notify feed composers of new posts from followed users. This choice allows for maximum extensibility. By leveraging these patterns, we decouple the behavioral logic from the structural representation, meaning future iterations can introduce new timeline rules without modifying the existing stable core codebase."

Using Strategy Pattern for text tokenization and relevance scoring provides us with the necessary flexibility. For example, if we need to add a new timeline ranking variant, we can implement a new class adhering to the interface without breaking the Open-Closed Principle. This ensures the design remains resilient against changing requirements and enables comprehensive unit testing through dependency injection.

## 4. Thread-Safety Details (25-30 minutes)

**Say:** "Handling concurrency is critical. For thread-safety, concurrent updates to the follow graph or user feed require lock-free data structures like ConcurrentHashMap or read-write locks to allow high read throughput for feed generation without blocking on new posts. We cannot rely on basic synchronization due to performance bottlenecks. By carefully orchestrating lock acquisition, we prevent deadlocks while maximizing throughput for fanout-read."

Additionally, immutable data structures are used where possible for read-heavy operations, minimizing the need for explicit locking. For state that must be mutated concurrently, we utilize mechanisms like `ConcurrentHashMap` and `ReentrantLock`. This guarantees that threads do not block indefinitely, preserving system responsiveness even during localized resource contention when processing updates.

## 5. Scaling Limits & Architecture (30-35 minutes)

**Say:** "When we push this system to its scaling limits, scaling limits occur due to massive fanout sizes exceeding processing time for celebrities. We handle this through hybrid fanout approaches—fanout-write for regular users and fanout-read for celebrities. The celebrity threshold is an explicit configurable teaching assumption here. As vertical scaling becomes cost-prohibitive, we transition to horizontal partitioning. This introduces complexities like distributed transactions."

The current architecture is bounded by the memory constraints of a single node and the CPU limits for concurrent feed compilations. We handle this through hybrid fanout approaches—fanout-write for regular users and fanout-read for celebrities. Addressing these limits requires transitioning state management to an external distributed cache and implementing intelligent load balancing based on data locality to minimize latency for feed views.

## 6. Feed Composition Trade-offs (35-40 minutes)

**Say:** "To support efficient feed views, we must consider feed composition trade-offs. Small follow graph yields deterministic fanout-write/read feeds with stable cursor ordering and no duplicate posts between pages. Storing pre-computed timelines in memory speeds up reads dramatically but increases storage costs and slows down writes during fanout, but is essential for low-latency feed loading. While adding secondary indexes speeds up our read path significantly, it comes with a non-trivial storage cost."

We have to balance the read-heavy versus write-heavy nature of the application. Small follow graph yields deterministic fanout-write/read feeds with stable cursor ordering and no duplicate posts between pages. By carefully selecting pre-computed cache sizes based on our most frequent query access patterns, we avoid full database scans during feed generation, though we acknowledge the associated memory overhead and maintenance penalties during peak write throughput.

## 7. State Synchronization (40-45 minutes)

**Say:** "Finally, state synchronization is essential across distributed components. Unfollow/delete/privacy transitions remove unauthorized posts, ensuring eventual consistency while offloading heavy feed pruning tasks from the critical path. We must ensure that a node failure does not result in split-brain scenarios or inconsistent timeline reads."

Using event-driven synchronization or a distributed consensus protocol in our coordination layer, unfollow/delete/privacy transitions remove unauthorized posts, ensuring eventual consistency while offloading heavy feed pruning tasks from the critical path. This guarantees that transient network partitions won't compromise the global state of the Instagram Core timeline, ensuring high availability and fault tolerance across data centers."
