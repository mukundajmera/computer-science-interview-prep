import unittest
import sys
import os

# Manipulate sys.path to allow importing solutions
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
from solutions import Solutions

class TestBacktracking(unittest.TestCase):
    def setUp(self):
        self.sol = Solutions()
        
    def test_subsets(self):
        res = self.sol.subsets([1,2,3])
        self.assertEqual(len(res), 8)
        self.assertIn([], res)
        self.assertIn([1,2,3], res)
        
    def test_combinationSum(self):
        res = self.sol.combinationSum([2,3,6,7], 7)
        self.assertEqual(len(res), 2)
        # Verify elements sum to 7
        for r in res:
            self.assertEqual(sum(r), 7)
            
    def test_combine(self):
        res = self.sol.combine(4, 2)
        self.assertEqual(len(res), 6)
        self.assertIn([1,2], res)
        
    def test_permute(self):
        res = self.sol.permute([1,2,3])
        self.assertEqual(len(res), 6)
        self.assertIn([1,2,3], res)
        self.assertIn([3,2,1], res)
        
    def test_generateParenthesis(self):
        res = self.sol.generateParenthesis(3)
        self.assertEqual(len(res), 5)
        self.assertIn("((()))", res)
        
    def test_exist(self):
        board = [["A","B","C","E"],["S","F","C","S"],["A","D","E","E"]]
        self.assertTrue(self.sol.exist(board, "ABCCED"))
        self.assertFalse(self.sol.exist(board, "ABCB"))
        
    def test_solveNQueens(self):
        res = self.sol.solveNQueens(4)
        self.assertEqual(len(res), 2)
        
    def test_letterCombinations(self):
        res = self.sol.letterCombinations("23")
        self.assertEqual(len(res), 9)
        self.assertIn("ad", res)
        self.assertEqual(self.sol.letterCombinations(""), [])

if __name__ == '__main__':
    unittest.main()
