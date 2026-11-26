import unittest
from solutions import Solutions

class TestSolutions(unittest.TestCase):
    def setUp(self):
        self.sol = Solutions()

    def test_search(self):
        self.assertEqual(self.sol.search([-1,0,3,5,9,12], 9), 4)
        self.assertEqual(self.sol.search([-1,0,3,5,9,12], 2), -1)
        self.assertEqual(self.sol.search([5], 5), 0)
        self.assertEqual(self.sol.search([5], -5), -1)
        self.assertEqual(self.sol.search([], 5), -1)
        self.assertEqual(self.sol.search([2, 5], 5), 1)

    def test_lowerBound(self):
        self.assertEqual(self.sol.lowerBound([1, 2, 2, 2, 3], 2), 1)
        self.assertEqual(self.sol.lowerBound([1, 2, 2, 2, 3], 4), 5)
        self.assertEqual(self.sol.lowerBound([1, 2, 2, 2, 3], 0), 0)
        self.assertEqual(self.sol.lowerBound([2, 2, 2], 2), 0)
        self.assertEqual(self.sol.lowerBound([], 2), 0)
        self.assertEqual(self.sol.lowerBound([1], 2), 1)

    def test_searchInsert(self):
        self.assertEqual(self.sol.searchInsert([1,3,5,6], 5), 2)
        self.assertEqual(self.sol.searchInsert([1,3,5,6], 2), 1)
        self.assertEqual(self.sol.searchInsert([1,3,5,6], 7), 4)
        self.assertEqual(self.sol.searchInsert([1,3,5,6], 0), 0)
        self.assertEqual(self.sol.searchInsert([1], 0), 0)
        self.assertEqual(self.sol.searchInsert([], 0), 0)

    def test_searchRotated(self):
        self.assertEqual(self.sol.searchRotated([4,5,6,7,0,1,2], 0), 4)
        self.assertEqual(self.sol.searchRotated([4,5,6,7,0,1,2], 3), -1)
        self.assertEqual(self.sol.searchRotated([1], 0), -1)
        self.assertEqual(self.sol.searchRotated([1], 1), 0)
        self.assertEqual(self.sol.searchRotated([2, 1], 1), 1)
        self.assertEqual(self.sol.searchRotated([2, 1], 2), 0)

    def test_findMin(self):
        self.assertEqual(self.sol.findMin([3,4,5,1,2]), 1)
        self.assertEqual(self.sol.findMin([4,5,6,7,0,1,2]), 0)
        self.assertEqual(self.sol.findMin([11,13,15,17]), 11)
        self.assertEqual(self.sol.findMin([1]), 1)
        self.assertEqual(self.sol.findMin([2, 1]), 1)
        self.assertEqual(self.sol.findMin([1, 2]), 1)

    def test_minEatingSpeed(self):
        self.assertEqual(self.sol.minEatingSpeed([3,6,7,11], 8), 4)
        self.assertEqual(self.sol.minEatingSpeed([30,11,23,4,20], 5), 30)
        self.assertEqual(self.sol.minEatingSpeed([30,11,23,4,20], 6), 23)
        self.assertEqual(self.sol.minEatingSpeed([1], 1), 1)
        self.assertEqual(self.sol.minEatingSpeed([1, 1], 2), 1)
        self.assertEqual(self.sol.minEatingSpeed([10], 1), 10)

    def test_searchMatrix(self):
        self.assertTrue(self.sol.searchMatrix([[1,3,5,7],[10,11,16,20],[23,30,34,60]], 3))
        self.assertFalse(self.sol.searchMatrix([[1,3,5,7],[10,11,16,20],[23,30,34,60]], 13))
        self.assertFalse(self.sol.searchMatrix([], 0))
        self.assertFalse(self.sol.searchMatrix([[]], 0))
        self.assertTrue(self.sol.searchMatrix([[1]], 1))
        self.assertFalse(self.sol.searchMatrix([[1]], 0))

if __name__ == '__main__':
    unittest.main()
