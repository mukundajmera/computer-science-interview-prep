# First Missing Positive

## Clean-Room Summary

Return the smallest positive integer that is absent from an unsorted integer array.

## Driver Signature

```java
class Solution {
    public int firstMissingPositive(int[] nums) {
        // implement
    }
}
```

```python
class Solution:
    def firstMissingPositive(self, nums: List[int]) -> int:
        # implement
```

## Repo-Authored Cases

- `zero fills first gap`
- `negative and large noise`
- `all above range`
- `single one`
- `single two missing one`
- `one two order reversed`
- `duplicate one`
- `duplicate blocks middle gap`
- `full prefix out of order`
- `large noise with prefix`
## Solution Ladder

| Tier | Strategy | Time | Space |
|---:|---|---|---|
| 1 | Seen set | `O(n)`. Building the set and scanning candidate values are linear in the array length. | `O(n)`. The set can store every input value. |
| 2 | Index placement | `O(n)`. Every successful swap places at least one value into its final slot. | `O(1)`. The input array is rearranged in place by the driver-isolated call. |

## Pitfalls

- Values outside 1..n cannot affect the smallest missing positive in an n-element array.
- Duplicate values must not trigger infinite swapping.
