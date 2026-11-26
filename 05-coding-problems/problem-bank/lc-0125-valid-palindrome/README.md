# Valid Palindrome

## Clean-Room Summary

Decide whether a string reads the same forward and backward after ignoring non-alphanumeric characters and comparing letters case-insensitively.

## Driver Signature

```java
class Solution {
    public boolean isPalindrome(String s) {
        // implementation
    }
}
```

```python
class Solution:
    def isPalindrome(self, s: str) -> bool:
        # implementation
```

## Repo-Authored Examples

| Input | Expected | Notes |
|---|---|---|
| `"Level-X-level!"` | `true` | Punctuation and case do not affect the comparison. |
| `"system design"` | `false` | The cleaned text is not symmetric. |

## Solution Ladder

| Tier | Strategy | Time | Space |
|---:|---|---|---|
| 1 | Build a normalized character list and compare it to its reverse | `O(n)` because the input and cleaned list are scanned. | `O(n)` for the normalized characters. |
| 2 | Two pointers skipping ignored characters | `O(n)` because each character is inspected at most once by a pointer. | `O(1)` because no normalized copy is built. |
