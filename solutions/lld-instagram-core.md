# 🏆 Coach Answer: Instagram Core — LLD

> **Type:** Low-Level Design  
> **Difficulty:** Intermediate  
> **Time Target:** 50 minutes

---

## Phase 1 — Requirements Clarification

### Functional
1. Support core operations for Instagram Core (photo/video posting and feed composition).
2. Small follow graph yields deterministic fanout-write/read feeds with stable cursor ordering and no duplicate posts between pages.
3. Unfollow/delete/privacy transitions remove unauthorized posts; celebrity threshold is an explicit configurable teaching assumption.

### Non-Functional
- Deterministic behavior in tests for repeated requests.
- High performance and thread safety.
- Standard-library-only implementation (Java 11+ SE and Python 3.8+).

---

## Phase 2 — Core Entities

| Entity | Responsibility |
|---|---|
| `MediaPostService` | Handles photo/video posting |
| `FollowGraphService` | Manages follow/unfollow and user relationships |
| `FeedComposer` | Generates deterministic fanout-write/read feeds with stable cursor ordering |
| `MediaStorageGateway` | Gateway for media assets |

---

## Phase 3 — API Contract

- `MediaPostService.createPost(userId, media) -> postId`
- `FollowGraphService.follow(followerId, followeeId)`
- `FollowGraphService.unfollow(followerId, followeeId)`
- `FeedComposer.getTimeline(userId, cursor) -> timelinePage`

---

## Phase 4 — Design Notes

1. Keep lifecycle explicit. Unfollow/delete/privacy transitions remove unauthorized posts.
2. Ensure modularity and swappable components for feed ranking.
3. Optimize critical paths for performance. Celebrity threshold is an explicit configurable teaching assumption to handle large fanouts.

### Complexity
- Processing: `O(1)` or `O(log N)` based on data structure for feed reads.
- Space: `O(N)` where N is number of active entities in the timeline cache.

---

## Phase 5 — Follow-Up Hooks

1. Distributed execution support for fanout workers.
2. Advanced monitoring and metrics for celebrity fanout latency.
3. Integration with external persistence stores for media.

---

## What Strong Answers Emphasize

1. Explicit state management and deterministic fanout-write/read feeds with stable cursor ordering and no duplicate posts between pages.
2. Thread safety with concurrent accesses for follow graph.
3. Safe extension paths for ranking algorithms.

---
*For the complete canonical explanation and code trace, see the [Instagram Core Strong Answer](../02-lld-projects/instagram-core/STRONG-ANSWER.md).*
