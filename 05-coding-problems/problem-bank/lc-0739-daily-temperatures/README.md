# Daily Temperatures

## Clean-Room Summary

For each day, return how many later positions must be skipped to find a warmer temperature, or zero if none exists.

## Driver Signature

```java
class Solution {
    public int[] dailyTemperatures(int[] temperatures) {
        // implement
    }
}
```

```python
class Solution:
    def dailyTemperatures(self, temperatures: List[int]) -> List[int]:
        # implement
```

## Repo-Authored Cases

- `mixed warmer waits`
- `strictly decreasing`
- `equal temperatures wait for warmer`
- `single day`
- `late warmer for many days`

## Solution Ladder

| Tier | Strategy | Time | Space |
|---:|---|---|---|
| 1 | Forward scan | `O(n^2)`. In the worst case each day scans nearly every later day. | `O(1)`. Only the output array and loop counters are used. |
| 2 | Monotonic stack | `O(n)`. Each index is pushed once and popped at most once. | `O(n)`. The stack can hold all indices when temperatures never rise. |

## Pitfalls

- Equal temperatures do not count as warmer.
- Store indices, not values, because the answer is a distance.
