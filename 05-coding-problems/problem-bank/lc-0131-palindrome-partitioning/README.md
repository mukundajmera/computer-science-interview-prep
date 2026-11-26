# Palindrome Partitioning

## Clean-Room Summary

Given a string `s`, partition `s` such that every substring of the partition is a palindrome. Return all possible palindrome partitionings of `s`.

## Driver Signature

```java
class Solution {
    public List<List<String>> partition(String s) {
        // implementation
    }
}
```

```python
class Solution:
    def partition(self, s: str) -> List[List[str]]:
        # implementation
```

## Repo-Authored Examples

| Input | Output |
| --- | --- |
| `s = "aab"` | `[["a","a","b"],["aa","b"]]` |
| `s = "a"` | `[["a"]]` |

## Solution Ladder

| Tier | Strategy | Time | Space |
|---:|---|---|---|
| 1 | Backtracking with palindrome verification | `O(n * 2^n)`. Explores all $2^{n-1}$ partition cuts, verifying palindrome slices. | `O(n)`. Call stack depth and current branch state. |

## Pitfalls

- The partition preserves the original sequence order of characters; do not reorder substrings.
- Single characters are always valid palindromes of length 1.
