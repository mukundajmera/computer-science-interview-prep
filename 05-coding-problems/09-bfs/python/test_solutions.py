import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'python')))
from solutions import Solution, TreeNode

class TestBFS(unittest.TestCase):
    def setUp(self):
        self.sol = Solution()
        
    def build_tree(self, values):
        if not values: return None
        root = TreeNode(values[0])
        queue = [root]
        i = 1
        while i < len(values):
            curr = queue.pop(0)
            if values[i] is not None:
                curr.left = TreeNode(values[i])
                queue.append(curr.left)
            i += 1
            if i < len(values) and values[i] is not None:
                curr.right = TreeNode(values[i])
                queue.append(curr.right)
            i += 1
        return root

    def test_levelOrder(self):
        self.assertEqual(self.sol.levelOrder(self.build_tree([3,9,20,None,None,15,7])), [[3],[9,20],[15,7]])
        self.assertEqual(self.sol.levelOrder(self.build_tree([1])), [[1]])
        self.assertEqual(self.sol.levelOrder(self.build_tree([])), [])
        self.assertEqual(self.sol.levelOrder(self.build_tree([1,2,3,4,5,6,7])), [[1],[2,3],[4,5,6,7]])
        self.assertEqual(self.sol.levelOrder(self.build_tree([1,None,2,None,3])), [[1],[2],[3]])
        self.assertEqual(self.sol.levelOrder(self.build_tree([1,2,None,3,None,4,None])), [[1],[2],[3],[4]])

    def test_minDepth(self):
        self.assertEqual(self.sol.minDepth(self.build_tree([3,9,20,None,None,15,7])), 2)
        self.assertEqual(self.sol.minDepth(self.build_tree([2,None,3,None,4,None,5,None,6])), 5)
        self.assertEqual(self.sol.minDepth(self.build_tree([])), 0)
        self.assertEqual(self.sol.minDepth(self.build_tree([1])), 1)
        self.assertEqual(self.sol.minDepth(self.build_tree([1,2,3])), 2)
        self.assertEqual(self.sol.minDepth(self.build_tree([1,2,3,4,None,None,5])), 3)

    def test_rightSideView(self):
        self.assertEqual(self.sol.rightSideView(self.build_tree([1,2,3,None,5,None,4])), [1,3,4])
        self.assertEqual(self.sol.rightSideView(self.build_tree([1,None,3])), [1,3])
        self.assertEqual(self.sol.rightSideView(self.build_tree([])), [])
        self.assertEqual(self.sol.rightSideView(self.build_tree([1,2,3,4])), [1,3,4])
        self.assertEqual(self.sol.rightSideView(self.build_tree([1,2])), [1,2])
        self.assertEqual(self.sol.rightSideView(self.build_tree([1,2,3,4,5,6,7])), [1,3,7])

    def test_numIslands(self):
        self.assertEqual(self.sol.numIslands([["1","1","1","1","0"],["1","1","0","1","0"],["1","1","0","0","0"],["0","0","0","0","0"]]), 1)
        self.assertEqual(self.sol.numIslands([["1","1","0","0","0"],["1","1","0","0","0"],["0","0","1","0","0"],["0","0","0","1","1"]]), 3)
        self.assertEqual(self.sol.numIslands([["0"]]), 0)
        self.assertEqual(self.sol.numIslands([["1"]]), 1)
        self.assertEqual(self.sol.numIslands([["1","0","1"],["0","1","0"],["1","0","1"]]), 5)
        self.assertEqual(self.sol.numIslands([["1","1"],["1","1"]]), 1)

    def test_orangesRotting(self):
        self.assertEqual(self.sol.orangesRotting([[2,1,1],[1,1,0],[0,1,1]]), 4)
        self.assertEqual(self.sol.orangesRotting([[2,1,1],[0,1,1],[1,0,1]]), -1)
        self.assertEqual(self.sol.orangesRotting([[0,2]]), 0)
        self.assertEqual(self.sol.orangesRotting([[0]]), 0)
        self.assertEqual(self.sol.orangesRotting([[1]]), -1)
        self.assertEqual(self.sol.orangesRotting([[2,2],[1,1],[0,0],[2,0]]), 1)

    def test_shortestPathBinaryMatrix(self):
        self.assertEqual(self.sol.shortestPathBinaryMatrix([[0,1],[1,0]]), 2)
        self.assertEqual(self.sol.shortestPathBinaryMatrix([[0,0,0],[1,1,0],[1,1,0]]), 4)
        self.assertEqual(self.sol.shortestPathBinaryMatrix([[1,0,0],[1,1,0],[1,1,0]]), -1)
        self.assertEqual(self.sol.shortestPathBinaryMatrix([[0]]), 1)
        self.assertEqual(self.sol.shortestPathBinaryMatrix([[1]]), -1)
        self.assertEqual(self.sol.shortestPathBinaryMatrix([[0,0,0],[0,0,0],[0,0,0]]), 3)

    def test_ladderLength(self):
        self.assertEqual(self.sol.ladderLength("hit", "cog", ["hot","dot","dog","lot","log","cog"]), 5)
        self.assertEqual(self.sol.ladderLength("hit", "cog", ["hot","dot","dog","lot","log"]), 0)
        self.assertEqual(self.sol.ladderLength("a", "c", ["a","b","c"]), 2)
        self.assertEqual(self.sol.ladderLength("a", "b", ["c"]), 0)
        self.assertEqual(self.sol.ladderLength("a", "b", ["b"]), 2)
        self.assertEqual(self.sol.ladderLength("qa", "sq", ["si","go","se","cm","so","ph","mt","db","mb","sb","kr","ln","tm","le","av","sm","ar","ci","ca","br","ti","ba","to","ra","fa","yo","ow","sn","ya","cr","po","fe","ho","ma","re","or","rn","au","ur","rh","sr","tc","lt","lo","as","fr","nb","yb","if","pb","ge","th","pm","rb","sh","co","ga","li","ha","hz","no","bi","di","hi","qa","pi","os","uh","wm","an","me","mo","na","la","st","er","sc","ne","mn","mi","am","ex","pt","io","be","fm","ta","tb","ni","mr","pa","he","lr","sq","ye"]), 5)

    def test_canFinish(self):
        self.assertEqual(self.sol.canFinish(2, [[1,0]]), True)
        self.assertEqual(self.sol.canFinish(2, [[1,0],[0,1]]), False)
        self.assertEqual(self.sol.canFinish(1, []), True)
        self.assertEqual(self.sol.canFinish(3, [[0,1],[1,2],[2,0]]), False)
        self.assertEqual(self.sol.canFinish(3, [[0,1],[0,2],[1,2]]), True)
        self.assertEqual(self.sol.canFinish(4, [[1,0],[2,0],[3,1],[3,2]]), True)

if __name__ == '__main__':
    unittest.main()
