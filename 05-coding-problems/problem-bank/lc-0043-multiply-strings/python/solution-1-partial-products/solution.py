class Solution:
    def multiply(self, num1: str, num2: str) -> str:
        if num1 == "0" or num2 == "0":
            return "0"
        result = "0"
        zeros = ""
        for digit in reversed(num2):
            result = self._add(result, self._multiply_by_digit(num1, ord(digit) - ord('0')) + zeros)
            zeros += "0"
        return result.lstrip("0") or "0"

    def _multiply_by_digit(self, value: str, digit: int) -> str:
        carry = 0
        out = []
        for char in reversed(value):
            product = (ord(char) - ord('0')) * digit + carry
            out.append(str(product % 10))
            carry = product // 10
        if carry:
            out.append(str(carry))
        return ''.join(reversed(out))

    def _add(self, a: str, b: str) -> str:
        i, j, carry = len(a) - 1, len(b) - 1, 0
        out = []
        while i >= 0 or j >= 0 or carry:
            total = carry
            if i >= 0:
                total += ord(a[i]) - ord('0')
                i -= 1
            if j >= 0:
                total += ord(b[j]) - ord('0')
                j -= 1
            out.append(str(total % 10))
            carry = total // 10
        return ''.join(reversed(out))
