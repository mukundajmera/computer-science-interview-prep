# Two Sum

## Source Tracking

| Source | Group | Order | Link |
|---|---:|---:|---|
| LeetCode Top Interview 150 | Hashmap | 44 | [LeetCode problem](https://leetcode.com/problems/two-sum) |
| Grind | array | 1 | [Grind source problem](https://leetcode.com/problems/two-sum) |
| NeetCode All | Arrays & Hashing | 36 | [NeetCode-aligned problem](https://leetcode.com/problems/two-sum) |

This page is authored from general algorithmic knowledge. Source lists are used only for metadata and outbound links.

## Clean-Room Question Summary

Given an integer array and a target value, return the indices of two different elements whose values add up to the target. Assume the caller expects one valid pair when a pair exists.

## Driver Signature

```java
class Solution {
    public int[] twoSum(int[] nums, int target) {
        // implementation
    }
}
```

```python
from typing import List


class Solution:
    def twoSum(self, nums: List[int], target: int) -> List[int]:
        # implementation
```

## Repo-Authored Examples

| Input | Expected output | Notes |
|---|---|---|
| `nums = [4, 6, 10]`, `target = 10` | `[0, 1]` | First two values form the target. |
| `nums = [5, -2, 11, 7]`, `target = 5` | `[1, 3]` | A negative value can be part of the answer. |

## Repo-Authored Edge Cases

- The same index cannot be used twice.
- Duplicate values at different indices are valid.
- Negative numbers and zero can appear.
- The returned pair is index-based, not value-based.

## Recognition Cues

- Need two values that combine to a target.
- Need original indices.
- A one-pass memory structure can remember previously seen complements.

## Solution Ladder

| Tier | Strategy | When to discuss |
|---:|---|---|
| 1 | Brute force pair scan | Baseline correctness and edge-case clarity. |
| 2 | One-pass complement map | Best standard interview answer for expected linear time. |

## Complexity Summary

| Tier | Time | Space | Reasoning |
|---:|---|---|---|
| 1 | `O(n^2)` | `O(1)` | The nested scan checks each index against later indices. Only counters and the returned pair are stored. |
| 2 | Expected `O(n)` | `O(n)` | Each element performs expected constant-time hash lookup and insertion. In the worst case, the map stores values for most of the array before finding a pair. |

## Correctness Notes

- The brute force solution directly checks every allowed pair, so it finds an answer if one exists.
- The hash-map solution checks whether the current value completes a pair with a previously seen value before storing the current index. That ordering prevents reusing the same index.

## Common Pitfalls

- Returning values instead of indices.
- Reusing the same element when `target` is twice a value.
- Inserting the current element before checking its complement.

## Follow-Ups

1. Return all index pairs.
2. Return all unique value pairs.
3. Handle streaming input where values arrive one at a time.

## Related System Design Uses

- Complement lookup is the local version of building an index for fast reverse lookup.
- The memory/time trade-off mirrors cache and index choices in larger systems.
