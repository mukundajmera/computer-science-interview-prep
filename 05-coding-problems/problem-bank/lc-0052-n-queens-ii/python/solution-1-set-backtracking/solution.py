class Solution:
    def totalNQueens(self, n: int) -> int:
        columns = set()
        diag = set()
        anti = set()

        def backtrack(row: int) -> int:
            if row == n:
                return 1
            count = 0
            for col in range(n):
                d = row - col
                a = row + col
                if col in columns or d in diag or a in anti:
                    continue
                columns.add(col)
                diag.add(d)
                anti.add(a)
                count += backtrack(row + 1)
                columns.remove(col)
                diag.remove(d)
                anti.remove(a)
            return count

        return backtrack(0)
