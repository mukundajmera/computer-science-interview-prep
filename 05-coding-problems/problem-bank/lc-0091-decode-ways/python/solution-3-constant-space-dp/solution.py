class Solution:
    def numDecodings(self, s: str) -> int:
        next_count = 1
        next_next = 0
        for index in range(len(s) - 1, -1, -1):
            current = 0
            if s[index] != "0":
                current = next_count
                if index + 1 < len(s) and int(s[index:index + 2]) <= 26:
                    current += next_next
            next_next = next_count
            next_count = current
        return next_count
