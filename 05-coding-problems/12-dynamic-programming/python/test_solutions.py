import unittest
from solutions import Solutions

class TestSolutions(unittest.TestCase):
    def setUp(self):
        self.sol = Solutions()

    def test_climbStairs(self):
        self.assertEqual(self.sol.climbStairs(2), 2)
        self.assertEqual(self.sol.climbStairs(3), 3)
        self.assertEqual(self.sol.climbStairs(4), 5)
        self.assertEqual(self.sol.climbStairs(1), 1)
        self.assertEqual(self.sol.climbStairs(5), 8)
        self.assertEqual(self.sol.climbStairs(10), 89)

    def test_rob(self):
        self.assertEqual(self.sol.rob([1,2,3,1]), 4)
        self.assertEqual(self.sol.rob([2,7,9,3,1]), 12)
        self.assertEqual(self.sol.rob([0]), 0)
        self.assertEqual(self.sol.rob([2,1,1,2]), 4)
        self.assertEqual(self.sol.rob([10, 0, 0, 10]), 20)
        self.assertEqual(self.sol.rob([5, 1, 1, 5]), 10)

    def test_wordBreak(self):
        self.assertTrue(self.sol.wordBreak("leetcode", ["leet","code"]))
        self.assertTrue(self.sol.wordBreak("applepenapple", ["apple","pen"]))
        self.assertFalse(self.sol.wordBreak("catsandog", ["cats","dog","sand","and","cat"]))
        self.assertTrue(self.sol.wordBreak("a", ["a"]))
        self.assertFalse(self.sol.wordBreak("a", ["b"]))
        self.assertTrue(self.sol.wordBreak("aaaaaaa", ["aaaa","aaa"]))

    def test_coinChange(self):
        self.assertEqual(self.sol.coinChange([1,2,5], 11), 3)
        self.assertEqual(self.sol.coinChange([2], 3), -1)
        self.assertEqual(self.sol.coinChange([1], 0), 0)
        self.assertEqual(self.sol.coinChange([1], 1), 1)
        self.assertEqual(self.sol.coinChange([1], 2), 2)
        self.assertEqual(self.sol.coinChange([186,419,83,408], 6249), 20)

    def test_lengthOfLIS(self):
        self.assertEqual(self.sol.lengthOfLIS([10,9,2,5,3,7,101,18]), 4)
        self.assertEqual(self.sol.lengthOfLIS([0,1,0,3,2,3]), 4)
        self.assertEqual(self.sol.lengthOfLIS([7,7,7,7,7,7,7]), 1)
        self.assertEqual(self.sol.lengthOfLIS([1]), 1)
        self.assertEqual(self.sol.lengthOfLIS([1, 2, 3]), 3)
        self.assertEqual(self.sol.lengthOfLIS([3, 2, 1]), 1)

    def test_minPathSum(self):
        self.assertEqual(self.sol.minPathSum([[1,3,1],[1,5,1],[4,2,1]]), 7)
        self.assertEqual(self.sol.minPathSum([[1,2,3],[4,5,6]]), 12)
        self.assertEqual(self.sol.minPathSum([[1]]), 1)
        self.assertEqual(self.sol.minPathSum([[1, 2], [3, 4]]), 7)
        self.assertEqual(self.sol.minPathSum([[1, 2, 3]]), 6)
        self.assertEqual(self.sol.minPathSum([[1], [2], [3]]), 6)

    def test_minDistance(self):
        self.assertEqual(self.sol.minDistance("horse", "ros"), 3)
        self.assertEqual(self.sol.minDistance("intention", "execution"), 5)
        self.assertEqual(self.sol.minDistance("", ""), 0)
        self.assertEqual(self.sol.minDistance("a", ""), 1)
        self.assertEqual(self.sol.minDistance("", "a"), 1)
        self.assertEqual(self.sol.minDistance("abc", "abc"), 0)

    def test_maximalSquare(self):
        self.assertEqual(self.sol.maximalSquare([["1","0","1","0","0"],["1","0","1","1","1"],["1","1","1","1","1"],["1","0","0","1","0"]]), 4)
        self.assertEqual(self.sol.maximalSquare([["0","1"],["1","0"]]), 1)
        self.assertEqual(self.sol.maximalSquare([["0"]]), 0)
        self.assertEqual(self.sol.maximalSquare([["1"]]), 1)
        self.assertEqual(self.sol.maximalSquare([["1", "1"], ["1", "1"]]), 4)
        self.assertEqual(self.sol.maximalSquare([["0", "0"], ["0", "0"]]), 0)

if __name__ == '__main__':
    unittest.main()
