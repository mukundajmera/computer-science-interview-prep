# Reverse Integer

## Clean-Room Summary

Reverse the decimal digits of a signed 32-bit integer and return zero if the reversed value would fall outside that range.

## Driver Signature

```java
class Solution {
    public int reverse(int x) {
        // implement
    }
}
```

```python
class Solution:
    def reverse(self, x: int) -> int:
        # implement
```

## Repo-Authored Cases

- `positive number`
- `negative number`
- `trailing zero`
- `positive overflow`
- `negative boundary valid`
- `negative overflow`

## Solution Ladder

| Tier | Strategy | Time | Space |
|---:|---|---|---|
| 1 | String reversal | `O(d)`. The d decimal digits are copied and reversed. | `O(d)`. Digit strings are stored. |
| 2 | Pop and push digits | `O(d)`. Each decimal digit is processed once. | `O(1)`. Only numeric accumulators are stored. |

## Pitfalls

- Modulo behavior for negative numbers differs by language; normalize sign explicitly in Python.
- Check overflow before multiplying by ten and adding the next digit.
