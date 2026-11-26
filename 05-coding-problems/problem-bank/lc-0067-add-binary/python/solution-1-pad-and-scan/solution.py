class Solution:
    def addBinary(self, a: str, b: str) -> str:
        max_length = max(len(a), len(b))
        left = a.zfill(max_length)
        right = b.zfill(max_length)
        carry = 0
        reversed_bits = []
        for i in range(max_length - 1, -1, -1):
            total = carry + int(left[i]) + int(right[i])
            reversed_bits.append(str(total % 2))
            carry = total // 2
        if carry:
            reversed_bits.append("1")
        return "".join(reversed(reversed_bits))
