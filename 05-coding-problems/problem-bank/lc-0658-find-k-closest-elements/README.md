# Find K Closest Elements

## Clean-Room Summary

Return k sorted values from a sorted array that are closest to x, preferring smaller values when distances tie.

## Driver Signature

```java
class Solution {
    public List<Integer> findClosestElements(int[] arr, int k, int x) {
        // implement
    }
}
```

```python
class Solution:
    def findClosestElements(self, arr: List[int], k: int, x: int) -> List[int]:
        # implement
```

## Repo-Authored Cases

- `center target`
- `target below range`
- `target near right edge`
- `duplicates at target`
- `tie prefers smaller values`

## Solution Ladder

| Tier | Strategy | Time | Space |
|---:|---|---|---|
| 1 | Sort by distance | `O(n log n)`. Sorting all n values dominates the work. | `O(n)`. A boxed copy of the input values is sorted. |
| 2 | Shrink window | `O(n-k)`. Each step discards exactly one endpoint. | `O(k)`. The returned list stores k values. |
| 3 | Binary search window | `O(log(n-k) + k)`. The boundary search is logarithmic and copying the answer costs k. | `O(k)`. The returned list stores k values. |

## Pitfalls

- The output must remain sorted by value, not by distance.
- When distances tie, discard the larger endpoint or choose the smaller value.
