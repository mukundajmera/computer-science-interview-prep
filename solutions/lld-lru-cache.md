# 🏆 Coach Answer: LRU Cache — LLD

> **Type:** Low-Level Design  
> **Difficulty:** Intermediate  
> **Time Target:** 45 minutes

---

## Canonical Interview Answer

This project has a definitive canonical interview answer that thoroughly explains the entity modeling, O(1) data structure rationale, thread-safety mechanisms (lock striping), and failure scenarios.

Please refer to the full canonical answer here:
[LRU Cache - Strong Answer](../02-lld-projects/lru-cache/STRONG-ANSWER.md)

---

## Key Takeaways

1. **O(1) Data Structures**: The core of LRU is combining a `HashMap` for O(1) lookups with a `DoublyLinkedList` for O(1) access order maintenance (using sentinel nodes).
2. **Thread Safety & Lock Striping**: While a single lock guarantees exact global LRU, it limits throughput. Using lock striping (segments) dramatically improves concurrency at the cost of strict global LRU ordering.
3. **Correctness Under Concurrency**: Both map modifications and linked list pointer updates must be strictly synchronized (via segment `ReentrantLock`) to prevent broken pointers or orphaned nodes.
