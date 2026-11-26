import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
from solutions import Solutions

class TestSolutions(unittest.TestCase):
    def setUp(self):
        self.sol = Solutions()

    def test_isValidSudoku(self):
        board1 = [["5","3",".",".","7",".",".",".","."]
                 ,["6",".",".","1","9","5",".",".","."]
                 ,[".","9","8",".",".",".",".","6","."]
                 ,["8",".",".",".","6",".",".",".","3"]
                 ,["4",".",".","8",".","3",".",".","1"]
                 ,["7",".",".",".","2",".",".",".","6"]
                 ,[".","6",".",".",".",".","2","8","."]
                 ,[".",".",".","4","1","9",".",".","5"]
                 ,[".",".",".",".","8",".",".","7","9"]]
        self.assertTrue(self.sol.isValidSudoku(board1))
        
        board2 = [["8","3",".",".","7",".",".",".","."]
                 ,["6",".",".","1","9","5",".",".","."]
                 ,[".","9","8",".",".",".",".","6","."]
                 ,["8",".",".",".","6",".",".",".","3"]
                 ,["4",".",".","8",".","3",".",".","1"]
                 ,["7",".",".",".","2",".",".",".","6"]
                 ,[".","6",".",".",".",".","2","8","."]
                 ,[".",".",".","4","1","9",".",".","5"]
                 ,[".",".",".",".","8",".",".","7","9"]]
        self.assertFalse(self.sol.isValidSudoku(board2))
        
        board3 = [["."]*9 for _ in range(9)]
        self.assertTrue(self.sol.isValidSudoku(board3))
        
        board4 = board3[:]
        board4[0][0] = "1"
        board4[1][8] = "1"
        self.assertTrue(self.sol.isValidSudoku(board4))
        
        board5 = [["."]*9 for _ in range(9)]
        board5[0][0] = "2"
        board5[0][8] = "2"
        self.assertFalse(self.sol.isValidSudoku(board5))
        
        board6 = [["."]*9 for _ in range(9)]
        board6[0][0] = "3"
        board6[8][0] = "3"
        self.assertFalse(self.sol.isValidSudoku(board6))

    def test_spiralOrder(self):
        self.assertEqual(self.sol.spiralOrder([[1,2,3],[4,5,6],[7,8,9]]), [1,2,3,6,9,8,7,4,5])
        self.assertEqual(self.sol.spiralOrder([[1,2,3,4],[5,6,7,8],[9,10,11,12]]), [1,2,3,4,8,12,11,10,9,5,6,7])
        self.assertEqual(self.sol.spiralOrder([]), [])
        self.assertEqual(self.sol.spiralOrder([[1]]), [1])
        self.assertEqual(self.sol.spiralOrder([[1,2],[3,4]]), [1,2,4,3])
        self.assertEqual(self.sol.spiralOrder([[1],[2],[3]]), [1,2,3])

    def test_rotate(self):
        m1 = [[1,2,3],[4,5,6],[7,8,9]]
        self.sol.rotate(m1)
        self.assertEqual(m1, [[7,4,1],[8,5,2],[9,6,3]])
        
        m2 = [[5,1,9,11],[2,4,8,10],[13,3,6,7],[15,14,12,16]]
        self.sol.rotate(m2)
        self.assertEqual(m2, [[15,13,2,5],[14,3,4,1],[12,6,8,9],[16,7,10,11]])
        
        m3 = [[1]]
        self.sol.rotate(m3)
        self.assertEqual(m3, [[1]])
        
        m4 = [[1,2],[3,4]]
        self.sol.rotate(m4)
        self.assertEqual(m4, [[3,1],[4,2]])
        
        m5 = [[1,2,3,4,5],[6,7,8,9,10],[11,12,13,14,15],[16,17,18,19,20],[21,22,23,24,25]]
        self.sol.rotate(m5)
        self.assertEqual(m5, [[21,16,11,6,1],[22,17,12,7,2],[23,18,13,8,3],[24,19,14,9,4],[25,20,15,10,5]])
        
        m6 = [[0,0],[0,0]]
        self.sol.rotate(m6)
        self.assertEqual(m6, [[0,0],[0,0]])

    def test_setZeroes(self):
        m1 = [[1,1,1],[1,0,1],[1,1,1]]
        self.sol.setZeroes(m1)
        self.assertEqual(m1, [[1,0,1],[0,0,0],[1,0,1]])
        
        m2 = [[0,1,2,0],[3,4,5,2],[1,3,1,5]]
        self.sol.setZeroes(m2)
        self.assertEqual(m2, [[0,0,0,0],[0,4,5,0],[0,3,1,0]])
        
        m3 = [[1]]
        self.sol.setZeroes(m3)
        self.assertEqual(m3, [[1]])
        
        m4 = [[0]]
        self.sol.setZeroes(m4)
        self.assertEqual(m4, [[0]])
        
        m5 = [[1,0]]
        self.sol.setZeroes(m5)
        self.assertEqual(m5, [[0,0]])
        
        m6 = [[1,1],[1,1]]
        self.sol.setZeroes(m6)
        self.assertEqual(m6, [[1,1],[1,1]])

    def test_gameOfLife(self):
        m1 = [[0,1,0],[0,0,1],[1,1,1],[0,0,0]]
        self.sol.gameOfLife(m1)
        self.assertEqual(m1, [[0,0,0],[1,0,1],[0,1,1],[0,1,0]])
        
        m2 = [[1,1],[1,0]]
        self.sol.gameOfLife(m2)
        self.assertEqual(m2, [[1,1],[1,1]])
        
        m3 = [[0]]
        self.sol.gameOfLife(m3)
        self.assertEqual(m3, [[0]])
        
        m4 = [[1]]
        self.sol.gameOfLife(m4)
        self.assertEqual(m4, [[0]])
        
        m5 = [[1,1],[1,1]]
        self.sol.gameOfLife(m5)
        self.assertEqual(m5, [[1,1],[1,1]])
        
        m6 = [[0,0],[0,0]]
        self.sol.gameOfLife(m6)
        self.assertEqual(m6, [[0,0],[0,0]])

    def test_searchMatrix(self):
        m1 = [[1,3,5,7],[10,11,16,20],[23,30,34,60]]
        self.assertTrue(self.sol.searchMatrix(m1, 3))
        self.assertFalse(self.sol.searchMatrix(m1, 13))
        self.assertTrue(self.sol.searchMatrix(m1, 60))
        self.assertFalse(self.sol.searchMatrix(m1, 61))
        
        m2 = [[1]]
        self.assertTrue(self.sol.searchMatrix(m2, 1))
        self.assertFalse(self.sol.searchMatrix(m2, 0))
        
        m3 = [[1,1]]
        self.assertTrue(self.sol.searchMatrix(m3, 1))
        
        self.assertFalse(self.sol.searchMatrix([], 1))

if __name__ == '__main__':
    unittest.main()
