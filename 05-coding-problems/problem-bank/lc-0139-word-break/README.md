# Word Break

## Clean-Room Summary

Given a string and a dictionary of words, decide whether the string can be segmented into one or more dictionary words.

## Driver Signature

```java
class Solution {
    public boolean wordBreak(String s, List<String> wordDict) {
        // implementation
    }
}
```

```python
class Solution:
    def wordBreak(self, s: str, wordDict: List[str]) -> bool:
        # implementation
```

## Repo-Authored Examples

| Input | Output |
| --- | --- |
| `s="blueprint", words=["blue","print","blueprint"]` | `true` |
| `s="codepath", words=["code","pat","paths"]` | `false` |

## Solution Ladder

| Tier | Strategy | Time | Space |
|---:|---|---|---|
| 1 | Memoized prefix search | `O(n*w*l)`. Each string position may try `w` distinct dictionary words, and each prefix comparison can inspect up to `l` characters. | `O(n + w)`. Memo entries and recursion depth are bounded by string positions, and the distinct word list supports iteration. |
| 2 | Bottom-up DP | `O(n*w*l)`. Each reachable start position tries `w` dictionary words with prefix checks up to length `l`. | `O(n + w)`. One boolean is stored per prefix length, plus the distinct word list. |

## Pitfalls

- Reusing dictionary words is allowed.
- The empty prefix is reachable and seeds the DP.
- A dictionary membership set avoids repeated linear lookup.
