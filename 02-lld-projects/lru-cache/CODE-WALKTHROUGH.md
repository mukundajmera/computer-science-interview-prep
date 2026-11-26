# Code Walkthrough: LRU Cache

## Overview

Classic data structure interview question. Implements O(1) get/put with capacity limit.

---

## File Structure

```
java/v1-basic/
├── LRUCache.java     # Main cache with Doubly Linked List + HashMap
├── Node.java         # DLL node for ordering
└── CacheDemo.java    # Demo entry point
```

---

## Key Data Structure

### Why HashMap + Doubly Linked List?

| Operation | HashMap Only | DLL Only | HashMap + DLL |
|-----------|-------------|----------|---------------|
| Get by key | O(1) | O(n) | **O(1)** |
| Update order | O(n) | O(1) | **O(1)** |
| Evict LRU | O(n) | O(1) | **O(1)** |

The combination achieves O(1) for all operations!

---

## Algorithm

### get(key)

```
1. If key not in map → return -1
2. Get node from map
3. Move node to front (most recent)
4. Return value
```

### put(key, value)

```
1. If key exists → update value, move to front
2. Else:
   a. If at capacity → remove LRU (tail)
   b. Create new node
   c. Add to front
   d. Add to map
```

---

## Design Pattern: Proxy/Decorator

LRU Cache wraps underlying data access with caching logic:
```
Client → LRUCache → Actual Data Store (if cache miss)
```

---

## Interview Questions

### 1. "Why doubly linked list, not singly?"

Need O(1) removal. DLL allows removing node without traversing from head.

### 2. "How to make thread-safe?"

Options:
- `Collections.synchronizedMap()` - simple but coarse
- `ConcurrentHashMap` + `ReentrantLock` - fine-grained
- `ReadWriteLock` - concurrent reads

### 3. "How to add TTL (expiration)?"

Add `timestamp` to Node, lazy eviction on access or background thread.

### 4. "How does Redis LRU differ?"

Redis uses approximate LRU (random sampling) for memory efficiency.

---

## Complexity

| Operation | Time | Space |
|-----------|------|-------|
| get() | O(1) | O(1) |
| put() | O(1) | O(1) |
| Total space | - | O(capacity) |
