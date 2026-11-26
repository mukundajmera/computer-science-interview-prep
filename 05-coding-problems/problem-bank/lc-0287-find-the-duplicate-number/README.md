# Find the Duplicate Number

## Clean-Room Summary

Given n+1 integers whose values are in the range 1..n, return the repeated value without relying on output order or mutation.

## Driver Signature

```java
class Solution {
    public int findDuplicate(int[] nums) {
        // implement
    }
}
```

```python
class Solution:
    def findDuplicate(self, nums: List[int]) -> int:
        # implement
```

## Repo-Authored Cases

- `duplicate in middle`
- `duplicate at start value`
- `two item array`
- `same duplicate repeated many times`
- `duplicate is largest value`

## Solution Ladder

| Tier | Strategy | Time | Space |
|---:|---|---|---|
| 1 | Seen set | `O(n)`. Each array element is checked once. | `O(n)`. The set can store every distinct value before the duplicate is found. |
| 2 | Value binary search | `O(n log n)`. Each value-range step counts across the full array. | `O(1)`. Only range boundaries and counters are stored. |
| 3 | Floyd cycle detection | `O(n)`. The tortoise and hare pointers traverse a linear number of links. | `O(1)`. Only two pointer values are stored. |

## Pitfalls

- The cycle-detection solution depends on values being valid indices in the 1..n range.
- Sorting or sign-marking approaches mutate the input, so they are not used here.
