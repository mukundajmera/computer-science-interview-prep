class Solution:
    def totalNQueens(self, n: int) -> int:
        mask = (1 << n) - 1

        def backtrack(columns: int, diag: int, anti: int) -> int:
            if columns == mask:
                return 1
            count = 0
            available = mask & ~(columns | diag | anti)
            while available:
                bit = available & -available
                available -= bit
                count += backtrack(columns | bit, (diag | bit) << 1, (anti | bit) >> 1)
            return count

        return backtrack(0, 0, 0)
