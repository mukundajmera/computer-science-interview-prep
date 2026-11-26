# Next Permutation

## Clean-Room Summary

Transform the array in-place into the next lexicographic permutation, or the smallest permutation when it is already last.

## Driver Signature

```java
class Solution {
    public void nextPermutation(int[] nums) {
        // implement
    }
}
```

```python
class Solution:
    def nextPermutation(self, nums: List[int]) -> None:
        # implement
```

## Repo-Authored Cases

- `simple increase at end`
- `wraps descending order`
- `duplicate values`
- `pivot before descending suffix`

## Solution Ladder

| Tier | Strategy | Time | Space |
|---:|---|---|---|
| 1 | Suffix pivot swap and reverse | `O(n)`. The pivot search, successor search, and suffix reversal are each linear. | `O(1)`. All work is done in-place. |

## Pitfalls

- Search the pivot from the right.
- The suffix is descending before the swap, so reversing it makes the smallest suffix.
- The method mutates `nums` and returns nothing.
