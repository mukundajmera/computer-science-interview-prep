# Smallest Range Covering Elements from K Lists

## Clean-Room Summary

Return the shortest inclusive integer range containing at least one value from each sorted input list; ties choose the smaller left boundary.

## Driver Signature

```java
class Solution {
    public int[] smallestRange(List<List<Integer>> nums) {
        // implement
    }
}
```

```python
class Solution:
    def smallestRange(self, nums: List[List[int]]) -> List[int]:
        # implement
```

## Repo-Authored Cases

- `overlapping middle range`
- `duplicate zero width range`
- `negative values`
- `all singleton lists`

## Solution Ladder

| Tier | Strategy | Time | Space |
|---:|---|---|---|
| 1 | Flatten sliding window | `O(N log N)`. All N values are sorted before the window pass. | `O(N)`. The flattened array and frequency map are stored. |
| 2 | Min heap | `O(N log k)`. Each value is pushed and popped at most once from a heap of k lists. | `O(k)`. The heap stores one active value per list. |

## Pitfalls

- Every input list must contribute at least one value to the chosen range.
- When two ranges have the same width, keep the one with the smaller left endpoint.
