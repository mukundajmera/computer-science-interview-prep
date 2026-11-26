
import unittest
from solutions import Solutions

class TestSolutions(unittest.TestCase):
    def setUp(self):
        self.sol = Solutions()
        
    def test_canFinish(self):
        self.assertTrue(self.sol.canFinish(2, [[1, 0]]))
        self.assertFalse(self.sol.canFinish(2, [[1, 0], [0, 1]]))
        
    def test_findOrder(self):
        self.assertEqual(self.sol.findOrder(2, [[1, 0]]), [0, 1])
        self.assertEqual(self.sol.findOrder(2, [[1, 0], [0, 1]]), [])
        
    def test_validTree(self):
        self.assertTrue(self.sol.validTree(5, [[0,1],[0,2],[0,3],[1,4]]))
        self.assertFalse(self.sol.validTree(5, [[0,1],[1,2],[2,3],[1,3],[1,4]]))
        
    def test_alienOrder(self):
        self.assertEqual(self.sol.alienOrder(["wrt","wrf","er","ett","rftt"]), "wertf")
        self.assertEqual(self.sol.alienOrder(["z","x"]), "zx")
        self.assertEqual(self.sol.alienOrder(["z","x","z"]), "")
        
    def test_networkDelayTime(self):
        self.assertEqual(self.sol.networkDelayTime([[2,1,1],[2,3,1],[3,4,1]], 4, 2), 2)
        self.assertEqual(self.sol.networkDelayTime([[1,2,1]], 2, 1), 1)
        self.assertEqual(self.sol.networkDelayTime([[1,2,1]], 2, 2), -1)
        
    def test_findCheapestPrice(self):
        self.assertEqual(self.sol.findCheapestPrice(3, [[0,1,100],[1,2,100],[0,2,500]], 0, 2, 1), 200)
        self.assertEqual(self.sol.findCheapestPrice(3, [[0,1,100],[1,2,100],[0,2,500]], 0, 2, 0), 500)
        
    def test_minCostConnectPoints(self):
        self.assertEqual(self.sol.minCostConnectPoints([[0,0],[2,2],[3,10],[5,2],[7,0]]), 20)
        self.assertEqual(self.sol.minCostConnectPoints([[3,12],[-2,5],[-4,1]]), 18)
