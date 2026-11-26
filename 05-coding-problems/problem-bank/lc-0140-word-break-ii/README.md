# Word Break II

## Clean-Room Summary

Given a string `s` and a dictionary of strings `wordDict`, add spaces in `s` to construct valid sentences where each word is a valid dictionary word. Return all such possible sentences in any order.

## Driver Signature

```java
class Solution {
    public List<String> wordBreak(String s, List<String> wordDict) {
        // implementation
    }
}
```

```python
class Solution:
    def wordBreak(self, s: str, wordDict: List[str]) -> List[str]:
        # implementation
```

## Repo-Authored Examples

| Input | Output |
| --- | --- |
| `s = "catsanddog"`, `wordDict = ["cat","cats","and","sand","dog"]` | `["cats and dog","cat sand dog"]` |
| `s = "catsandog"`, `wordDict = ["cats","dog","sand","and","cat"]` | `[]` |

## Solution Ladder

| Tier | Strategy | Time | Space |
|---:|---|---|---|
| 1 | Memoized DFS suffix decomposition | `O(2^n)`. Explores prefix matches and memoizes sentence lists per suffix index. | `O(2^n)`. Stores generated sentence variants across suffix positions. |

## Pitfalls

- Multiple words may share common prefixes; memoizing by suffix index avoids redundant branches.
- If a suffix cannot be segmented into dictionary words, cache the empty result to prune further exploration.
