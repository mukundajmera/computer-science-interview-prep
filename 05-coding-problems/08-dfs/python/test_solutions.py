import unittest
from solutions import Solutions, TreeNode

class TestSolutions(unittest.TestCase):
    def setUp(self):
        self.sol = Solutions()

    def test_maxDepth(self):
        root = TreeNode(3, TreeNode(9), TreeNode(20, TreeNode(15), TreeNode(7)))
        self.assertEqual(self.sol.maxDepth(root), 3)
        self.assertEqual(self.sol.maxDepth(None), 0)

    def test_isSameTree(self):
        p = TreeNode(1, TreeNode(2), TreeNode(3))
        q = TreeNode(1, TreeNode(2), TreeNode(3))
        self.assertTrue(self.sol.isSameTree(p, q))
        self.assertFalse(self.sol.isSameTree(TreeNode(1, TreeNode(2)), TreeNode(1, None, TreeNode(2))))

    def test_hasPathSum(self):
        root = TreeNode(1, TreeNode(2), TreeNode(3))
        self.assertTrue(self.sol.hasPathSum(root, 3))
        self.assertFalse(self.sol.hasPathSum(root, 5))
        self.assertFalse(self.sol.hasPathSum(None, 0))

    def test_floodFill(self):
        image = [[1,1,1],[1,1,0],[1,0,1]]
        expected = [[2,2,2],[2,2,0],[2,0,1]]
        self.assertEqual(self.sol.floodFill(image, 1, 1, 2), expected)

    def test_numIslands(self):
        grid = [
            ["1","1","0","0","0"],
            ["1","1","0","0","0"],
            ["0","0","1","0","0"],
            ["0","0","0","1","1"]
        ]
        self.assertEqual(self.sol.numIslands(grid), 3)
        
    def test_maxAreaOfIsland(self):
        grid = [[1,1],[1,0]]
        self.assertEqual(self.sol.maxAreaOfIsland(grid), 3)
        
    def test_validPath(self):
        self.assertTrue(self.sol.validPath(3, [[0,1],[1,2],[2,0]], 0, 2))
        self.assertFalse(self.sol.validPath(6, [[0,1],[0,2],[3,5],[5,4],[4,3]], 0, 5))
        
    def test_canVisitAllRooms(self):
        self.assertTrue(self.sol.canVisitAllRooms([[1],[2],[3],[]]))
        self.assertFalse(self.sol.canVisitAllRooms([[1,3],[3,0,1],[2],[0]]))

if __name__ == '__main__':
    unittest.main()
