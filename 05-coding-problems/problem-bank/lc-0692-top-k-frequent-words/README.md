# Top K Frequent Words

## Clean-Room Summary

Return the k most frequent words, ordering ties by lexicographically smaller words first.

## Driver Signature

```java
class Solution {
    public List<String> topKFrequent(String[] words, int k) {
        // implement
    }
}
```

```python
class Solution:
    def topKFrequent(self, words: List[str], k: int) -> List[str]:
        # implement
```

## Repo-Authored Cases

- `two clear leaders`
- `frequency then lexical order`
- `all words tied`
- `bounded heap tie eviction`

## Solution Ladder

| Tier | Strategy | Time | Space |
|---:|---|---|---|
| 1 | Count and sort | `O(n + u log u)`. Counting scans n words and sorting orders u unique words. | `O(u)`. The frequency map and unique-word list store u entries. |
| 2 | Size-k min heap | `O(n + u log k)`. Counting scans all words and each unique word performs a heap operation bounded by k. | `O(u + k)`. The frequency map stores u words and the heap stores k candidates. |

## Pitfalls

- Tie-breaking is part of the output contract; frequency alone is not enough.
- The bounded heap comparator must evict lexicographically larger words first when frequencies tie.
