# Word Ladder

## Clean-Room Summary

Given a start word, a target word, and a dictionary, return the number of words in the shortest transformation sequence where each step changes exactly one character and every intermediate word is in the dictionary.

## Driver Signature

```java
class Solution {
    public int ladderLength(String beginWord, String endWord, List<String> wordList) {
        // implementation
    }
}
```

```python
class Solution:
    def ladderLength(self, beginWord: str, endWord: str, wordList: List[str]) -> int:
        # implementation
```

## Repo-Authored Examples

| Input | Output |
| --- | --- |
| `begin="cold", end="warm", words=["cord","card","ward","warm","worm","word"]` | `5` |
| `begin="talk", end="tail", words=["tall","tail","bail"]` | `3` |

## Solution Ladder

| Tier | Strategy | Time | Space |
|---:|---|---|---|
| 1 | BFS with dictionary scan | `O(n^2*l)`. Each visited word may compare with every dictionary word across `l` characters. | `O(n)`. The queue and visited set store dictionary words. |
| 2 | BFS with wildcard pattern index | `O(n*l^2)`. Building and probing `l` wildcard patterns per word costs string construction work. | `O(n*l)`. The pattern map stores each word under each wildcard pattern. |

## Pitfalls

- BFS level count returns sequence length including the start and end words.
- The target must be reachable through dictionary words.
- Mark words visited when enqueued to avoid duplicate frontier growth.
