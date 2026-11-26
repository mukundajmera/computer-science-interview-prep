# Ransom Note

## Clean-Room Summary

Decide whether every character needed by a target string can be supplied by another string, using each supplied character at most once.

## Driver Signature

```java
class Solution {
    public boolean canConstruct(String ransomNote, String magazine) {
        // implementation
    }
}
```

```python
class Solution:
    def canConstruct(self, ransomNote: str, magazine: str) -> bool:
        # implementation
```

## Repo-Authored Examples

| Target | Supply | Expected |
|---|---|---|
| `"moon"` | `"onomatopoeia"` | `true` |
| `"balloon"` | `"balon"` | `false` |

## Solution Ladder

| Tier | Strategy | Time | Space |
|---:|---|---|---|
| 1 | Mark used magazine positions while searching for each needed character | `O(r * m)` in the worst case because each target character can scan the supply. | `O(m)` for the used-position flags. |
| 2 | Count available characters, then spend counts | `O(r + m)` because both strings are scanned once. | `O(k)` for `k` distinct supplied characters. |
