# Insert Delete GetRandom O(1)

## Clean-Room Summary

Design a set-like container that reports whether insertions and removals changed membership, then returns one currently stored value when asked for a random item.

## Driver Signature

```java
class RandomizedSet {
    public RandomizedSet() {}
    public boolean insert(int val) { return false; }
    public boolean remove(int val) { return false; }
    public int getRandom() { return 0; }
}
```

```python
class RandomizedSet:
    def __init__(self) -> None:
        pass
    def insert(self, val: int) -> bool:
        return False
    def remove(self, val: int) -> bool:
        return False
    def getRandom(self) -> int:
        return 0
```

## Repo-Authored Examples

| Operations | Results |
| --- | --- |
| `RandomizedSet(), insert(10), insert(20), insert(10), getRandom(), remove(10), getRandom()` | `null, true, true, false, one of {10,20}, true, 20` |

## Solution Ladder

| Tier | Strategy | Time | Space |
|---:|---|---|---|
| 1 | Hash set with snapshot sampling | `O(1)` average insert/remove, `O(n)` getRandom. Sampling builds an indexed view. | `O(n)`. Store all active values and a temporary snapshot. |
| 2 | Indexed array plus value positions | `O(1)` average per operation. Removal swaps with the last array item. | `O(n)`. Store values and their indices. |

## Pitfalls

- Removing from the middle of the optimized array must update the swapped value's index.
- Duplicate inserts return `false` and must not add another copy.
- The driver validates `getRandom()` membership, not statistical distribution.
