# Approach for Instagram Core

## Overview and Core Strategy
The core functionality of Instagram requires solving two fundamentally opposing engineering challenges: ingesting and reliably storing a massive volume of binary media files, while simultaneously generating highly personalized, chronologically ordered feeds for millions of concurrent users with sub-second latency. The system must handle the complexities of a dense, directed social graph where a single user might have millions of followers.

Our approach explicitly avoids external frameworks, using only Java 11+ SE and Python 3.8+ standard libraries (e.g., `java.util.concurrent`, `asyncio`). We orchestrate the feed generation path favoring aggressive denormalization, standard library in-memory thread-safe maps, and multi-tiered concurrent queues. We decouple the heavy lifting of media processing from the critical path of user interaction, ensuring the API remains highly responsive.

Each assigned document describes actual supported versions:
- `v1-basic`: In-memory baseline focusing on basic structures.
- `v2-extended`: Abstraction boundaries and state transition safety (e.g., deterministic pagination and deletion).
- `v3-optimized`: Distributed-friendly interfaces with idempotency hooks.

### Beginner Intuition
Imagine a magazine subscription (Push model). When a new issue is printed, a copy is directly pushed to your mailbox. For most users, we use a Fan-out on Write (Push) model, directly placing new posts into the followers' pre-computed lists using standard library structures. 
However, if a celebrity prints a magazine for a million people, placing it in every single mailbox at once is impossible. Instead, for celebrities, we use a Fan-out on Read (Pull) model: users fetch the celebrity's posts directly when they open their feed. The celebrity threshold is an explicit configurable teaching assumption to decide between push and pull.

## Feed Generation (Hybrid Fan-out)
Small follow graph yields deterministic fanout-write/read feeds with stable cursor ordering and no duplicate posts between pages. Generating a user's feed on-the-fly via graph traversal is computationally impossible at scale. We approach this using pre-computation.

1. **Push Model (Fan-out on Write):** For the vast majority of users, when a user creates a post, an asynchronous worker queries the social graph. It pushes the new `post_id` into a pre-computed list maintained for each follower. This makes reading the feed an O(1) operation.
2. **Pull Model (Fan-out on Read):** For high-follower accounts, pushing one post to millions of queues would cause massive delays. Their posts are *not* pushed. When a follower requests their feed, the system dynamically merges the pre-computed timeline with recent posts from followed celebrities.

### Worked Trace
**Premise**: User A follows User B (non-celebrity). User B creates two posts.
1. **Push**: User B creates P1 (t=100) and P2 (t=200). They are pushed into User A's concurrent deque.
2. **First Page Read**: User A fetches their feed with no cursor. The system reads the deque, sorts descending, and returns `[P2, P1]`.
3. **Cursor Read**: User A passes cursor=200. The system filters `post.timestamp < 200`, returning only `[P1]`. This guarantees stable cursor ordering and no duplicate posts between pages.

### Counterexample / Boundary Condition
If an integer offset were used instead of a timestamp cursor, a new post arriving between page requests would shift the elements down. A user requesting offset=10 (page 2) would see a duplicate post that was previously at offset=9 on page 1. Timestamp cursors avoid this boundary condition entirely.

## State Transitions and Authorization
Unfollow/delete/privacy transitions remove unauthorized posts; celebrity threshold is an explicit configurable teaching assumption. When a post is deleted or a user unfollows another, the system explicitly purges unauthorized elements from the follower's feed list to enforce authorization and privacy.

### Staff Extension
In `v3-optimized`, we can enhance idempotency for feed publishing using distributed-friendly interfaces. By storing deduplication keys for publish events in a `ConcurrentHashMap`, we ensure that retried post creations from clients do not result in duplicate posts being broadcasted to follower feeds.
