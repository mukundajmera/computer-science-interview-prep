# Find Median from Data Stream

## Clean-Room Summary

Maintain a growing numeric stream and return the current median after any insertion.

## Driver Signature

```java
class MedianFinder {
    public MedianFinder() {}
    public void addNum(int num) {}
    public double findMedian() { return 0.0; }
}
```

```python
class MedianFinder:
    def __init__(self) -> None:
        pass
    def addNum(self, num: int) -> None:
        pass
    def findMedian(self) -> float:
        return 0.0
```

## Repo-Authored Examples

| Operations | Results |
| --- | --- |
| `MedianFinder(), addNum(8), findMedian(), addNum(2), findMedian(), addNum(10), findMedian()` | `null, null, 8.0, null, 5.0, null, 8.0` |

## Solution Ladder

| Tier | Strategy | Time | Space |
|---:|---|---|---|
| 1 | Sorted dynamic array | `O(n)` insertion, `O(1)` median. Inserting may shift many values. | `O(n)`. Store every stream value. |
| 2 | Two balanced heaps | `O(log n)` insertion, `O(1)` median. Heap balancing keeps middle values at the roots. | `O(n)`. Store every value across two heaps. |

## Pitfalls

- Even-length streams require averaging the two middle values as floating-point data.
- Duplicates and negative values should not receive special-case logic.
- The lower heap must not exceed the upper heap by more than one item.
