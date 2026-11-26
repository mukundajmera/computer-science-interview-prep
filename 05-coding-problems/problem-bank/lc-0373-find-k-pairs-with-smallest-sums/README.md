# Find K Pairs with Smallest Sums

## Clean-Room Summary

Return up to k pairs, one value from each sorted input array, with the smallest pair sums.

## Driver Signature

```java
class Solution {
    public List<List<Integer>> kSmallestPairs(int[] nums1, int[] nums2, int k) {
        // implementation
    }
}
```

```python
class Solution:
    def kSmallestPairs(self, nums1: List[int], nums2: List[int], k: int) -> List[List[int]]:
        # implementation
```

## Repo-Authored Examples

| Input | Output |
| --- | --- |
| `nums1 = [1, 4], nums2 = [2, 6], k = 3` | `[[1, 2], [4, 2], [1, 6]]` |

## Solution Ladder

| Tier | Strategy | Time | Space |
|---:|---|---|---|
| 1 | Enumerate and sort | `O(nm log(nm))`. All n times m pairs are sorted by sum. | `O(nm)`. Every candidate pair is stored before truncation. |
| 2 | Frontier min-heap | `O(min(n,k) + k log min(n,k))`. At most min(n,k) rows are seeded and each emitted pair performs one heap pop and maybe one push. | `O(min(n,k))`. The heap stores one frontier pair per seeded nums1 index. |

## Pitfalls

- The input arrays are sorted, so each row of fixed nums1 value can be advanced incrementally.
- Return fewer than k pairs when the Cartesian product is smaller.
- Use deterministic tie handling when exact output order is validated.
