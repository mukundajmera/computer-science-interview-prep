# Largest Rectangle in Histogram

## Clean-Room Summary

Find the maximum rectangular area that can be formed by contiguous histogram bars.

## Driver Signature

```java
class Solution {
    public int largestRectangleArea(int[] heights) {
        // implement
    }
}
```

```python
class Solution:
    def largestRectangleArea(self, heights: List[int]) -> int:
        # implement
```

## Repo-Authored Cases

- `best spans middle bars`
- `increasing bars`
- `all equal bars`
- `single bar`

## Solution Ladder

| Tier | Strategy | Time | Space |
|---:|---|---|---|
| 1 | Expand each start | `O(n^2)`. There are O(n^2) contiguous spans to evaluate. | `O(1)`. Only the running minimum and best area are stored. |
| 2 | Monotonic stack | `O(n)`. Each bar is pushed and popped at most once. | `O(n)`. The stack can hold all increasing indices. |

## Pitfalls

- A sentinel height of zero flushes remaining bars.
- When popping, width spans between the new stack top and the current index.
- Equal heights can remain stacked; the final area still computes correctly.
