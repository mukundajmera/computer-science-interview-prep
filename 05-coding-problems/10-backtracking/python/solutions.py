from typing import List

class Solutions:
    def subsets(self, nums: List[int]) -> List[List[int]]:
        res = []
        path = []
        def backtrack(i):
            if i == len(nums):
                res.append(path.copy())
                return
            # choose to include
            path.append(nums[i])
            backtrack(i + 1)
            # choose not to include (unchoose)
            path.pop()
            backtrack(i + 1)
        backtrack(0)
        return res

    def combinationSum(self, candidates: List[int], target: int) -> List[List[int]]:
        res = []
        path = []
        candidates.sort() # optional but helps prune
        def backtrack(i, cur_sum):
            if cur_sum == target:
                res.append(path.copy())
                return
            if cur_sum > target or i == len(candidates):
                return
            # choose candidates[i]
            path.append(candidates[i])
            backtrack(i, cur_sum + candidates[i])
            # unchoose and move to next
            path.pop()
            backtrack(i + 1, cur_sum)
        backtrack(0, 0)
        return res

    def combine(self, n: int, k: int) -> List[List[int]]:
        res = []
        path = []
        def backtrack(start):
            if len(path) == k:
                res.append(path.copy())
                return
            for i in range(start, n + 1):
                path.append(i)
                backtrack(i + 1)
                path.pop()
        backtrack(1)
        return res

    def permute(self, nums: List[int]) -> List[List[int]]:
        res = []
        path = []
        used = [False] * len(nums)
        def backtrack():
            if len(path) == len(nums):
                res.append(path.copy())
                return
            for i in range(len(nums)):
                if not used[i]:
                    used[i] = True
                    path.append(nums[i])
                    backtrack()
                    path.pop()
                    used[i] = False
        backtrack()
        return res

    def generateParenthesis(self, n: int) -> List[str]:
        res = []
        path = []
        def backtrack(open_c, close_c):
            if open_c == close_c == n:
                res.append("".join(path))
                return
            if open_c < n:
                path.append("(")
                backtrack(open_c + 1, close_c)
                path.pop()
            if close_c < open_c:
                path.append(")")
                backtrack(open_c, close_c + 1)
                path.pop()
        backtrack(0, 0)
        return res

    def exist(self, board: List[List[str]], word: str) -> bool:
        ROWS, COLS = len(board), len(board[0])
        def backtrack(r, c, i):
            if i == len(word):
                return True
            if r < 0 or c < 0 or r >= ROWS or c >= COLS or board[r][c] != word[i]:
                return False
            
            tmp = board[r][c]
            board[r][c] = "#"
            res = (backtrack(r + 1, c, i + 1) or
                   backtrack(r - 1, c, i + 1) or
                   backtrack(r, c + 1, i + 1) or
                   backtrack(r, c - 1, i + 1))
            board[r][c] = tmp
            return res
            
        for r in range(ROWS):
            for c in range(COLS):
                if backtrack(r, c, 0):
                    return True
        return False

    def solveNQueens(self, n: int) -> List[List[str]]:
        cols = set()
        posDiag = set() # r+c
        negDiag = set() # r-c
        res = []
        board = [["."] * n for _ in range(n)]

        def backtrack(r):
            if r == n:
                res.append(["".join(row) for row in board])
                return
            for c in range(n):
                if c in cols or (r + c) in posDiag or (r - c) in negDiag:
                    continue
                
                cols.add(c)
                posDiag.add(r + c)
                negDiag.add(r - c)
                board[r][c] = "Q"

                backtrack(r + 1)

                cols.remove(c)
                posDiag.remove(r + c)
                negDiag.remove(r - c)
                board[r][c] = "."
        
        backtrack(0)
        return res

    def letterCombinations(self, digits: str) -> List[str]:
        if not digits:
            return []
        
        digitToChar = {
            "2": "abc", "3": "def", "4": "ghi", "5": "jkl",
            "6": "mno", "7": "pqrs", "8": "tuv", "9": "wxyz"
        }
        res = []
        path = []
        
        def backtrack(i):
            if i == len(digits):
                res.append("".join(path))
                return
            for c in digitToChar[digits[i]]:
                path.append(c)
                backtrack(i + 1)
                path.pop()
                
        backtrack(0)
        return res
