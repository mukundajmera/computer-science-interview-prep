# Pascal's Triangle

## Clean-Room Summary

Given an integer `numRows`, generate the first `numRows` of Pascal's triangle where each number is the sum of the two numbers directly above it.

## Driver Signature

```java
class Solution {
    public List<List<Integer>> generate(int numRows) {
        // implementation
    }
}
```

```python
class Solution:
    def generate(self, numRows: int) -> List[List[int]]:
        # implementation
```

## Repo-Authored Examples

| Input | Output |
| --- | --- |
| `numRows = 5` | `[[1],[1,1],[1,2,1],[1,3,3,1],[1,4,6,4,1]]` |
| `numRows = 1` | `[[1]]` |

## Solution Ladder

| Tier | Strategy | Time | Space |
|---:|---|---|---|
| 1 | Iterative row construction | `O(n^2)`. Constructing $n$ rows computes $n(n+1)/2$ total elements. | `O(1)`. Extra space excluding output. |

## Pitfalls

- The first and last elements of each row are always `1`.
- Row `i` (0-indexed) has length `i + 1`.
