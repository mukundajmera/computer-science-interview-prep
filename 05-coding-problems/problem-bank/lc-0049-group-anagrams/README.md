# Group Anagrams

## Clean-Room Summary

Given a list of words, group together words that contain the same characters with the same counts. Return every group once; the order of groups is not important.

## Driver Signature

```java
class Solution {
    public List<List<String>> groupAnagrams(String[] strs) {
        // implementation
    }
}
```

```python
class Solution:
    def groupAnagrams(self, strs: List[str]) -> List[List[str]]:
        # implementation
```

## Repo-Authored Examples

| Input | Output |
| --- | --- |
| `["arc","car","rat","tar","star"]` | `[["arc","car"],["rat","tar"],["star"]]` |

## Solution Ladder

| Tier | Strategy | Time | Space |
|---:|---|---|---|
| 1 | Sort each word to build the grouping key | `O(n * k log k)`. There are `n` words and each key sorts up to `k` characters. | `O(n * k)`. Groups and keys store the input characters. |
| 2 | Count characters and use the count vector as the key | `O(n * (k + a))`. Each word is scanned once and `a = 26` counts are serialized. | `O(n * k + n * a)`. Groups store words and keys store fixed-size count vectors. |

## Pitfalls

- The grouping key must include character counts, not only character presence.
- Sorting groups before returning keeps driver comparisons deterministic without changing the grouping contract.
- The count-vector tier assumes lowercase English letters; use the sorted-key tier for broader alphabets.
