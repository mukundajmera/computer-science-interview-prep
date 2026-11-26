# In-Memory Multi-Policy Cache - Problem Statement

## Introduction
Design and implement an in-memory caching system that supports multiple eviction policies (LRU, LFU, FIFO) and allows for dynamic runtime swapping of these policies without dropping the existing cached data. The cache must also support time-to-live (TTL) based passive and active expiration.

## Requirements

### Core Features
- **Key-Value Store:** Standard `put(key, value)` and `get(key)` methods.
- **Capacity:** A configurable maximum number of elements before eviction triggers.
- **Eviction Policies:**
    - **LRU (Least Recently Used):** Evicts the item that has not been accessed for the longest time.
    - **LFU (Least Frequently Used):** Evicts the item with the lowest access frequency. In case of a tie, standard LFU tie-breaking (e.g., LRU) is applied implicitly. Implementation must use an O(1) doubly linked frequency bucket approach.
    - **FIFO (First In, First Out):** Evicts the oldest inserted item.
- **TTL Expiration:**
    - Support assigning a time-to-live (`ttl`) duration for each entry.
    - **Passive Expiration:** Upon a `get()`, if the item is expired, return `null` and remove it.
    - **Active Expiration:** A background thread must periodically scan and remove expired items.
- **Runtime Policy Swapping:**
    - Provide a method `changePolicy(EvictionPolicy)` to switch the current eviction strategy on the fly.
    - Existing cached items must be retained and re-indexed into the new strategy's tracking structures based on their historical access metadata (e.g., swapping to FIFO orders by creation time, swapping to LRU orders by last access time).
- **Concurrency:**
    - All read and write operations, as well as policy swaps, must be thread-safe.

### Constraints
- The solution must use Java 11+ and Python 3.8+ standard libraries exclusively. No external dependencies (e.g., Guava, Redis).
- Thread safety should be achieved using standard lock primitives (`ReentrantReadWriteLock` in Java, `threading.RLock` in Python).
- O(1) average time complexity for `get` and `put` operations.
