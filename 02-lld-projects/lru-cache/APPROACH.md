# Design Approach for LRU Cache

A step-by-step thought process for designing the LRU cache.

---

## Step 1: Identify Core Entities

Extract nouns from the problem statement:

| Noun | Entity? | Reasoning |
|------|---------|-----------|
| Cache | ✅ Yes | Main container |
| Entry/Node | ✅ Yes | Individual cached item |
| Key | ❌ No | Attribute of entry |
| Value | ❌ No | Attribute of entry |
| Capacity | ❌ No | Configuration value |
| Linked List | ✅ Yes | Internal data structure |

**Final Entities**: LRUCache, CacheNode, DoublyLinkedList

---

## Step 2: Define Relationships

```
LRUCache (1) ──contains──> (1) HashMap<K, CacheNode>
LRUCache (1) ──contains──> (1) DoublyLinkedList
DoublyLinkedList (1) ──contains──> (n) CacheNode
CacheNode ──links──> CacheNode (prev/next)
```

### Relationship Types:

| Relationship | Type | Description |
|--------------|------|-------------|
| LRUCache → HashMap | Composition | For O(1) key lookup |
| LRUCache → LinkedList | Composition | For access order |
| CacheNode → CacheNode | Association | Linked structure |

---

## Step 3: Choose Design Patterns

### Pattern Analysis:

| Pattern | Apply? | Justification |
|---------|--------|---------------|
| **Strategy** | ✅ v2 | Different eviction policies (LRU, LFU) |
| **Observer** | ✅ v2 | Eviction callbacks |
| **Template Method** | ❌ No | Operations are straightforward |
| **Decorator** | ❌ No | Not needed for basic cache |

### Pattern Application:

1. **Strategy Pattern** (v2) - EvictionPolicy
   - LRUEvictionPolicy
   - LFUEvictionPolicy
   - Swap eviction strategies without changing cache code

2. **Observer Pattern** (v2) - EvictionListener
   - Notify when entries are evicted
   - Useful for cleanup, logging, or cascading invalidation

---

## Step 4: Design Classes

### Core Classes:

#### LRUCache<K, V>
- **Attributes**: 
  - `capacity: int`
  - `cache: Map<K, CacheNode<K, V>>`
  - `list: DoublyLinkedList<K, V>`
- **Methods**:
  - `get(key: K): V`
  - `put(key: K, value: V): void`
  - `remove(key: K): V`
  - `containsKey(key: K): boolean`
  - `size(): int`
  - `clear(): void`

#### CacheNode<K, V>
- **Attributes**:
  - `key: K`
  - `value: V`
  - `prev: CacheNode<K, V>`
  - `next: CacheNode<K, V>`
  - `createdAt: long` (v2)
  - `expiresAt: long` (v2)
- **Methods**:
  - `isExpired(): boolean` (v2)

#### DoublyLinkedList<K, V>
- **Attributes**:
  - `head: CacheNode<K, V>` (dummy head)
  - `tail: CacheNode<K, V>` (dummy tail)
  - `size: int`
- **Methods**:
  - `addToFront(node: CacheNode): void`
  - `moveToFront(node: CacheNode): void`
  - `removeLast(): CacheNode`
  - `remove(node: CacheNode): void`

---

## Step 5: Handle Edge Cases

### Input Validation:
- Null key
- Null value
- Zero or negative capacity

### Boundary Cases:
- Get on empty cache
- Put on full cache (eviction)
- Update existing key (move to front, don't evict)
- Remove non-existent key
- Single capacity cache

### Concurrency (v3):
- Concurrent get and put
- Concurrent eviction
- Read-write lock for better concurrency

---

## Step 6: Optimization Opportunities

### Data Structures:
| Operation | Naive | Optimized |
|-----------|-------|-----------|
| Get | O(n) list scan | O(1) HashMap lookup |
| Put | O(n) scan + O(n) move | O(1) HashMap + O(1) list |
| Evict | O(n) find oldest | O(1) remove tail |

### Why Doubly Linked List?

- **Insert at head**: O(1)
- **Remove from anywhere**: O(1) (with node reference)
- **Remove from tail**: O(1)

Single linked list would require O(n) to find node before the one to remove.

### Sentinel Nodes (Dummy Head/Tail):

Using sentinel nodes simplifies edge cases:
- No null checks for head/tail
- Uniform insert/remove operations
- head.next is first real element
- tail.prev is last real element

---

## Step 7: Version Progression

### v1-basic
- HashMap + Doubly Linked List
- get, put, remove, size, clear
- Simple implementation
- Single-threaded
- ~150-250 lines

### v2-extended
- TTL support per entry
- Cache statistics (hits, misses, evictions)
- Eviction callbacks
- Optional capacity expansion
- ~300-450 lines

### v3-optimized
- Thread-safe with ReadWriteLock
- Concurrent get operations
- Synchronized modifications
- Expiration cleanup thread
- ~450-600 lines

---

## Code Organization

```
lru-cache/
├── java/
│   ├── v1-basic/
│   │   ├── LRUCache.java          # Main cache class
│   │   ├── CacheNode.java         # Linked list node
│   │   └── LRUCacheDemo.java      # Usage example
│   ├── v2-extended/
│   │   ├── LRUCache.java          # Enhanced cache
│   │   ├── CacheEntry.java        # Entry with TTL
│   │   ├── CacheStatistics.java   # Hit/miss tracking
│   │   └── EvictionListener.java  # Callback interface
│   └── v3-optimized/
│       └── ConcurrentLRUCache.java # Thread-safe version
└── python/
    └── [Same structure]
```

---

## Interview Discussion Points

1. **Why HashMap + Linked List?**
   - HashMap: O(1) lookup by key
   - Linked List: O(1) order maintenance
   - Together: O(1) for all operations

2. **Why Doubly Linked vs Singly Linked?**
   - Need to remove nodes from middle of list
   - Singly linked requires O(n) to find previous node
   - Doubly linked has direct prev reference

3. **Why Sentinel Nodes?**
   - Eliminate null checks at boundaries
   - Uniform handling of all insertions/removals
   - Cleaner code, fewer edge cases

4. **How to handle TTL efficiently?**
   - Lazy expiration: check on access
   - Background cleanup thread
   - Trade-off: memory vs CPU

5. **Thread-safe approaches?**
   - Synchronized methods (simple but slow)
   - ReadWriteLock (multiple readers)
   - ConcurrentHashMap + fine-grained locks
   - Lock striping for high concurrency
