# Is Subsequence

## Clean-Room Summary

Determine whether all characters of a candidate string can be matched in order inside another string without reordering the larger string.

## Driver Signature

```java
class Solution {
    public boolean isSubsequence(String s, String t) {
        // implementation
    }
}
```

```python
class Solution:
    def isSubsequence(self, s: str, t: str) -> bool:
        # implementation
```

## Repo-Authored Examples

| Candidate | Text | Expected |
|---|---|---|
| `"lamp"` | `"la-m-p"` | `true` |
| `"stone"` | `"sotne"` | `false` |

## Solution Ladder

| Tier | Strategy | Time | Space |
|---:|---|---|---|
| 1 | Recursive include/skip search | `O(2^m)` worst case because matching branches can split while scanning the text. | `O(m)` recursion depth. |
| 2 | Two pointers | `O(n + m)` because each pointer only moves forward. | `O(1)` auxiliary storage. |
