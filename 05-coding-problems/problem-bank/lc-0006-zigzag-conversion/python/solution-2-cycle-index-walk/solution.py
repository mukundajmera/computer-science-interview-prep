class Solution:
    def convert(self, s: str, numRows: int) -> str:
        if numRows == 1 or numRows >= len(s):
            return s
        cycle = 2 * numRows - 2
        result = []
        for row in range(numRows):
            i = row
            while i < len(s):
                result.append(s[i])
                diagonal = i + cycle - 2 * row
                if row not in (0, numRows - 1) and diagonal < len(s):
                    result.append(s[diagonal])
                i += cycle
        return ''.join(result)
