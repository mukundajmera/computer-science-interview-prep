# Find All Anagrams in a String

## Clean-Room Summary

Given two strings, return the starting indices where a window in the first string is a permutation of the second string.

## Driver Signature

```java
class Solution {
    public List<Integer> findAnagrams(String s, String p) {
        // implement
    }
}
```

```python
class Solution:
    def findAnagrams(self, s: str, p: str) -> List[int]:
        # implement
```

## Repo-Authored Cases

- `two separated matches`
- `overlapping matches`
- `pattern longer than text`
- `repeated letters`
- `all windows match`

## Solution Ladder

| Tier | Strategy | Time | Space |
|---:|---|---|---|
| 1 | Sorted windows | `O((n-m+1) * m log m)`. Each of the n-m+1 windows of length m is sorted before comparison. | `O(m)`. A sorted copy of one window and the pattern are stored during comparison. |
| 2 | Sliding frequency | `O(n + a)`. The scan touches each text character a constant number of times, with a fixed alphabet-size comparison. | `O(a)`. Two frequency arrays store counts for the alphabet. |

## Pitfalls

- Return indices in ascending order as they are discovered by the left-to-right scan.
- A window must match character multiplicity, not just contain the same distinct letters.
