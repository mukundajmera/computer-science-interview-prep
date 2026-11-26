# LRU Cache

## Problem Statement

Design and implement a Least Recently Used (LRU) cache with O(1) time complexity for both get and put operations.

---

## Functional Requirements

1. **Get Operation**: Retrieve value by key in O(1) time
2. **Put Operation**: Insert or update key-value pair in O(1) time
3. **Capacity Management**: Evict least recently used entry when capacity is exceeded
4. **LRU Tracking**: Maintain access order to identify least recently used items
5. **Key Existence Check**: Check if key exists in cache
6. **Remove Operation**: Explicitly remove a key from cache
7. **Size Query**: Get current number of entries in cache
8. **Clear Cache**: Remove all entries

---

## Non-Functional Requirements

1. **O(1) Operations**: Both get and put must be constant time
2. **Thread Safety**: Support concurrent access (v3)
3. **Memory Efficiency**: Minimize overhead per cached entry
4. **TTL Support**: Optional time-to-live for cache entries (v2)
5. **Cache Statistics**: Track hit/miss ratios (v2)

---

## Constraints & Assumptions

- Capacity is fixed at cache creation
- Keys and values are non-null
- Key equality uses equals() / __eq__
- Cache starts empty
- Capacity must be at least 1

---

## Sample Interactions

```
LRUCache cache = new LRUCache(3);

cache.put("a", 1);  // cache: [a=1]
cache.put("b", 2);  // cache: [a=1, b=2]
cache.put("c", 3);  // cache: [a=1, b=2, c=3]

cache.get("a");     // returns 1, cache: [b=2, c=3, a=1] (a moved to end)

cache.put("d", 4);  // cache: [c=3, a=1, d=4] (b evicted as LRU)

cache.get("b");     // returns null (b was evicted)
cache.get("c");     // returns 3, cache: [a=1, d=4, c=3]
```

---

## Clarifying Questions to Ask

1. "What is the expected cache capacity?"
2. "What types of keys and values need to be supported?"
3. "Is thread-safety required?"
4. "Do we need TTL (time-to-live) support?"
5. "Should we track cache statistics (hits/misses)?"
6. "What happens on capacity of 0?"
7. "Do we need to support null values?"
8. "Is there a maximum key or value size?"

---

## Entities to Identify

| Entity | Responsibility |
|--------|---------------|
| LRUCache | Main cache interface |
| CacheEntry | Node in doubly linked list |
| DoublyLinkedList | Maintains access order |
| CacheStatistics | Tracks hits, misses, evictions |
| EvictionPolicy | Strategy for eviction (LRU, LFU) |

---

## Data Structure Choice

The LRU Cache requires two data structures working together:

1. **HashMap**: O(1) key lookup
2. **Doubly Linked List**: O(1) order maintenance

```
HashMap<Key, Node>  +  DoublyLinkedList
     ↓                      ↓
   O(1) lookup         O(1) move to front
                       O(1) remove from tail
```

---

## Version Roadmap

| Version | Features |
|---------|----------|
| v1-basic | HashMap + Doubly Linked List, basic LRU |
| v2-extended | TTL support, cache statistics, eviction callbacks |
| v3-optimized | Thread-safe with read-write locks, concurrent access |
