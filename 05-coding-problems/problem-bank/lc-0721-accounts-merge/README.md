# Accounts Merge

## Clean-Room Summary

Merge accounts that share at least one email address; each output row keeps the account name followed by sorted emails.

## Driver Signature

```java
class Solution {
    public List<List<String>> accountsMerge(List<List<String>> accounts) {
        // implement
    }
}
```

```python
class Solution:
    def accountsMerge(self, accounts: List[List[str]]) -> List[List[str]]:
        # implement
```

## Repo-Authored Cases

- `transitive merge and isolated account`
- `same name disconnected`
- `bridge account arrives late`

## Solution Ladder

| Tier | Strategy | Time | Space |
|---:|---|---|---|
| 1 | Email graph DFS | `O(N log N)`. Each email edge is traversed and component emails are sorted. | `O(N)`. The graph, visited set, and output components store the emails. |
| 2 | Union find | `O(N alpha(N) + N log N)`. Union/find is near-constant and each group is sorted. | `O(N)`. Parent maps and grouped component lists store every email. |

## Pitfalls

- Rows can be returned in any order, but emails inside a row should be sorted.
- Accounts with the same display name are not automatically connected.
