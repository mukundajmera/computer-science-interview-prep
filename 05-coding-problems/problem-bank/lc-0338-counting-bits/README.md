# Counting Bits

## Clean-Room Summary

Return an array where each position i stores the number of set bits in the binary form of i for every value from 0 through n.

## Driver Signature

```java
class Solution {
    public int[] countBits(int n) {
        // implement
    }
}
```

```python
class Solution:
    def countBits(self, n: int) -> List[int]:
        # implement
```

## Repo-Authored Cases

- `zero only`
- `small range`
- `five values`
- `power boundary`

## Solution Ladder

| Tier | Strategy | Time | Space |
|---:|---|---|---|
| 1 | Count each number | `O(n log n)`. Each number can inspect up to its bit length. | `O(n)`. The output array stores one count for every value from 0 through n. |
| 2 | DP lowest bit | `O(n)`. Each output position is computed once in constant time. | `O(n)`. The output array doubles as the dynamic-programming table. |

## Pitfalls

- The result includes zero, so its length is n + 1.
- The DP recurrence reuses the count for i divided by two.
