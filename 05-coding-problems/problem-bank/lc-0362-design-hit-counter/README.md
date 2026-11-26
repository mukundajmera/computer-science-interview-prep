# Design Hit Counter

## Clean-Room Summary

Maintain hit timestamps and return how many hits happened in the trailing 300-second window ending at a query timestamp.

## Driver Signature

```java
class HitCounter {
    public HitCounter() {}
    public void hit(int timestamp) {}
    public int getHits(int timestamp) { return 0; }
}
```

```python
class HitCounter:
    def __init__(self) -> None: ...
    def hit(self, timestamp: int) -> None: ...
    def getHits(self, timestamp: int) -> int: ...
```

## Repo-Authored Cases

- `empty query`
- `duplicate hits and boundary`
- `interleaved hits expire`

## Solution Ladder

| Tier | Strategy | Time | Space |
|---:|---|---|---|
| 1 | Timestamp queue | `O(H)`. A query may remove many stale hits. | `O(H)`. Every hit in the active window can be stored. |
| 2 | Rolling buckets | `O(300)`. Each query sums a fixed number of buckets. | `O(300)`. The bucket arrays have fixed size. |

## Pitfalls

- Multiple hits can share the same timestamp.
- A hit older than the trailing 300-second window must be excluded.
