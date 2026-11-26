import unittest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
from solutions import Solution

class TestSolutions(unittest.TestCase):
    def setUp(self):
        self.sol = Solution()

    def test_findCircleNum_1(self):
        self.assertEqual(self.sol.findCircleNum([[1,1,0],[1,1,0],[0,0,1]]), 2)
    def test_findCircleNum_2(self):
        self.assertEqual(self.sol.findCircleNum([[1,0,0],[0,1,0],[0,0,1]]), 3)
    def test_findCircleNum_3(self):
        self.assertEqual(self.sol.findCircleNum([[1]]), 1)
    def test_findCircleNum_4(self):
        self.assertEqual(self.sol.findCircleNum([[1,1],[1,1]]), 1)
    def test_findCircleNum_5(self):
        self.assertEqual(self.sol.findCircleNum([[1,0,1],[0,1,0],[1,0,1]]), 2)
    def test_findCircleNum_6(self):
        self.assertEqual(self.sol.findCircleNum([[1,1,1],[1,1,1],[1,1,1]]), 1)

    def test_findRedundantConnection_1(self):
        self.assertEqual(self.sol.findRedundantConnection([[1,2],[1,3],[2,3]]), [2,3])
    def test_findRedundantConnection_2(self):
        self.assertEqual(self.sol.findRedundantConnection([[1,2],[2,3],[3,4],[1,4],[1,5]]), [1,4])
    def test_findRedundantConnection_3(self):
        self.assertEqual(self.sol.findRedundantConnection([[1,2],[2,3],[1,3]]), [1,3])
    def test_findRedundantConnection_4(self):
        self.assertEqual(self.sol.findRedundantConnection([[1,2],[1,3],[3,4],[2,4]]), [2,4])
    def test_findRedundantConnection_5(self):
        self.assertEqual(self.sol.findRedundantConnection([[1,2],[1,3],[3,4],[4,5],[1,5]]), [1,5])
    def test_findRedundantConnection_6(self):
        self.assertEqual(self.sol.findRedundantConnection([[1,2],[2,3],[3,4],[4,5],[2,5]]), [2,5])

    def test_countComponents_1(self):
        self.assertEqual(self.sol.countComponents(5, [[0,1],[1,2],[3,4]]), 2)
    def test_countComponents_2(self):
        self.assertEqual(self.sol.countComponents(5, [[0,1],[1,2],[2,3],[3,4]]), 1)
    def test_countComponents_3(self):
        self.assertEqual(self.sol.countComponents(4, [[0,1],[2,3]]), 2)
    def test_countComponents_4(self):
        self.assertEqual(self.sol.countComponents(3, []), 3)
    def test_countComponents_5(self):
        self.assertEqual(self.sol.countComponents(1, []), 1)
    def test_countComponents_6(self):
        self.assertEqual(self.sol.countComponents(6, [[0,1],[1,2],[2,3],[4,5]]), 2)

    def test_validTree_1(self):
        self.assertTrue(self.sol.validTree(5, [[0,1],[0,2],[0,3],[1,4]]))
    def test_validTree_2(self):
        self.assertFalse(self.sol.validTree(5, [[0,1],[1,2],[2,3],[1,3],[1,4]]))
    def test_validTree_3(self):
        self.assertFalse(self.sol.validTree(4, [[0,1],[2,3]]))
    def test_validTree_4(self):
        self.assertTrue(self.sol.validTree(1, []))
    def test_validTree_5(self):
        self.assertTrue(self.sol.validTree(3, [[0,1],[0,2]]))
    def test_validTree_6(self):
        self.assertFalse(self.sol.validTree(3, [[0,1],[1,2],[0,2]]))

    def test_accountsMerge_1(self):
        res = self.sol.accountsMerge([["John","a@m.com","b@m.com"],["John","c@m.com"],["John","a@m.com","d@m.com"]])
        self.assertEqual(len(res), 2)
    def test_accountsMerge_2(self):
        self.assertEqual(len(self.sol.accountsMerge([["Gabe","g@m.com"]])), 1)
    def test_accountsMerge_3(self):
        self.assertEqual(len(self.sol.accountsMerge([["A","1@m.com"],["A","2@m.com"],["A","3@m.com"]])), 3)
    def test_accountsMerge_4(self):
        self.assertEqual(len(self.sol.accountsMerge([["A","1@m.com","2@m.com"],["A","2@m.com","3@m.com"]])), 1)
    def test_accountsMerge_5(self):
        self.assertEqual(len(self.sol.accountsMerge([["A","1@m.com","2@m.com"],["A","3@m.com","4@m.com"],["A","2@m.com","4@m.com"]])), 1)
    def test_accountsMerge_6(self):
        self.assertEqual(len(self.sol.accountsMerge([["A","1@m.com"],["B","2@m.com"]])), 2)

    def test_longestConsecutive_1(self):
        self.assertEqual(self.sol.longestConsecutive([100,4,200,1,3,2]), 4)
    def test_longestConsecutive_2(self):
        self.assertEqual(self.sol.longestConsecutive([0,3,7,2,5,8,4,6,0,1]), 9)
    def test_longestConsecutive_3(self):
        self.assertEqual(self.sol.longestConsecutive([]), 0)
    def test_longestConsecutive_4(self):
        self.assertEqual(self.sol.longestConsecutive([1]), 1)
    def test_longestConsecutive_5(self):
        self.assertEqual(self.sol.longestConsecutive([1,2,0,1]), 3)
    def test_longestConsecutive_6(self):
        self.assertEqual(self.sol.longestConsecutive([9,1,4,7,3,-1,0,5,8,-1,6]), 7)

if __name__ == '__main__':
    unittest.main()
