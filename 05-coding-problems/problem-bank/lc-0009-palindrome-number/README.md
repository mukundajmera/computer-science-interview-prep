# Palindrome Number

## Clean-Room Summary

Return whether the decimal digits of an integer read the same forward and backward.

## Driver Signature

```java
class Solution {
    public boolean isPalindrome(int x) {
        // implementation
    }
}
```

```python
class Solution:
    def isPalindrome(self, x: int) -> bool:
        # implementation
```

## Repo-Authored Examples

| Input | Output |
| --- | --- |
| `x = 1221` | `true` |

## Solution Ladder

| Tier | Strategy | Time | Space |
|---:|---|---|---|
| 1 | String check | `O(d)`. The d decimal digits are read at most once. | `O(d)`. The decimal string stores all digits. |
| 2 | Reverse half the digits | `O(d)`. Only about half of the d digits are moved into the reversed half. | `O(1)`. Only numeric accumulators are stored. |

## Pitfalls

- Negative signs are not mirrored digits, so negative inputs are false.
- Numbers ending in zero cannot be palindromes unless the number is zero.
- Reversing only half the number avoids full reversal overflow risk in Java.
