# Longest Repeating Character Replacement

## Clean-Room Summary

Find the longest substring that can be made of one repeated character after replacing at most k characters.

## Driver Signature

```java
class Solution {
    public int characterReplacement(String s, int k) {
        // implement
    }
}
```

```python
class Solution:
    def characterReplacement(self, s: str, k: int) -> int:
        # implement
```

## Repo-Authored Cases

- `alternating can all match`
- `classic shrinking window`
- `already repeated`
- `one replacement only`
- `whole string after replacements`

## Solution Ladder

| Tier | Strategy | Time | Space |
|---:|---|---|---|
| 1 | Check every window | `O(n^2)`. Every start can extend across the remaining string. | `O(a)`. A fixed alphabet frequency array is stored. |
| 2 | Sliding window | `O(n)`. Each boundary moves only to the right. | `O(a)`. Counts are stored for the alphabet. |

## Pitfalls

- The number of replacements needed is window length minus the most frequent character count.
- The stored max-frequency may be stale after shrinking; that is safe because it only delays shrinking without missing the best length.
