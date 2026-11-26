# LRU Cache

## Clean-Room Summary

Build a fixed-size key-value store that returns `-1` for missing keys and evicts the least recently touched entry when inserting beyond capacity.

## Driver Signature

```java
class LRUCache {
    public LRUCache(int capacity) {}
    public int get(int key) { return 0; }
    public void put(int key, int value) {}
}
```

```python
class LRUCache:
    def __init__(self, capacity: int) -> None:
        pass
    def get(self, key: int) -> int:
        return 0
    def put(self, key: int, value: int) -> None:
        pass
```

## Repo-Authored Examples

| Operations | Results |
| --- | --- |
| `LRUCache(2), put(4,40), put(9,90), get(4), put(12,120), get(9)` | `null, null, null, 40, null, -1` |

## Solution Ladder

| Tier | Strategy | Time | Space |
|---:|---|---|---|
| 1 | Timestamped map with eviction scan | `O(n)` worst-case `put`, `O(1)` `get`. Eviction scans the map to find the oldest access. | `O(n)`. Store one value and timestamp per cached key. |
| 2 | Hash map plus recency order | `O(1)` per operation. Access-order movement and oldest-key removal are constant time. | `O(n)`. Store cached values plus recency links. |

## Pitfalls

- A successful `get` must refresh recency, not only return the value.
- Updating an existing key should refresh recency without increasing size.
- Eviction must happen after inserting or updating enough state to know the true least-recent key.
