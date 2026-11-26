import unittest
from solutions import Solution

class TestTwoPointers(unittest.TestCase):
    def setUp(self):
        self.sol = Solution()

    def test_maxArea(self):
        self.assertEqual(self.sol.maxArea([1,8,6,2,5,4,8,3,7]), 49)
        self.assertEqual(self.sol.maxArea([1,1]), 1)
        self.assertEqual(self.sol.maxArea([4,3,2,1,4]), 16)
        self.assertEqual(self.sol.maxArea([1,2,1]), 2)
        self.assertEqual(self.sol.maxArea([0,0]), 0)
        self.assertEqual(self.sol.maxArea([10,9,8,7,6,5,4,3,2,1]), 25)

    def test_twoSum(self):
        self.assertEqual(self.sol.twoSum([2,7,11,15], 9), [1,2])
        self.assertEqual(self.sol.twoSum([2,3,4], 6), [1,3])
        self.assertEqual(self.sol.twoSum([-1,0], -1), [1,2])
        self.assertEqual(self.sol.twoSum([1,2,3,4,4,9,56,90], 8), [4,5])
        self.assertEqual(self.sol.twoSum([1,1], 2), [1,2])
        self.assertEqual(self.sol.twoSum([-5,-2,-1,0,3], -2), [1,5])

    def test_threeSum(self):
        self.assertEqual(self.sol.threeSum([-1,0,1,2,-1,-4]), [[-1,-1,2], [-1,0,1]])
        self.assertEqual(self.sol.threeSum([0,1,1]), [])
        self.assertEqual(self.sol.threeSum([0,0,0]), [[0,0,0]])
        self.assertEqual(self.sol.threeSum([-2,0,0,2,2]), [[-2,0,2]])
        self.assertEqual(self.sol.threeSum([0,0,0,0]), [[0,0,0]])
        self.assertEqual(self.sol.threeSum([-1,0,1,0]), [[-1,0,1]])

    def test_triangleNumber(self):
        self.assertEqual(self.sol.triangleNumber([2,2,3,4]), 3)
        self.assertEqual(self.sol.triangleNumber([4,2,3,4]), 4)
        self.assertEqual(self.sol.triangleNumber([0,0,0]), 0)
        self.assertEqual(self.sol.triangleNumber([1,1,1,1]), 4)
        self.assertEqual(self.sol.triangleNumber([1,2,3,4,5,6]), 7)
        self.assertEqual(self.sol.triangleNumber([7,0,0,0]), 0)

    def test_moveZeroes(self):
        arr1 = [0,1,0,3,12]; self.sol.moveZeroes(arr1); self.assertEqual(arr1, [1,3,12,0,0])
        arr2 = [0]; self.sol.moveZeroes(arr2); self.assertEqual(arr2, [0])
        arr3 = [1,2,3]; self.sol.moveZeroes(arr3); self.assertEqual(arr3, [1,2,3])
        arr4 = [0,0,1]; self.sol.moveZeroes(arr4); self.assertEqual(arr4, [1,0,0])
        arr5 = [1,0,0]; self.sol.moveZeroes(arr5); self.assertEqual(arr5, [1,0,0])
        arr6 = [4,2,4,0,0,3,0,5,1,0]; self.sol.moveZeroes(arr6); self.assertEqual(arr6, [4,2,4,3,5,1,0,0,0,0])

    def test_sortColors(self):
        arr1 = [2,0,2,1,1,0]; self.sol.sortColors(arr1); self.assertEqual(arr1, [0,0,1,1,2,2])
        arr2 = [2,0,1]; self.sol.sortColors(arr2); self.assertEqual(arr2, [0,1,2])
        arr3 = [0]; self.sol.sortColors(arr3); self.assertEqual(arr3, [0])
        arr4 = [1]; self.sol.sortColors(arr4); self.assertEqual(arr4, [1])
        arr5 = [2]; self.sol.sortColors(arr5); self.assertEqual(arr5, [2])
        arr6 = [2,2,2,1,1,1,0,0,0]; self.sol.sortColors(arr6); self.assertEqual(arr6, [0,0,0,1,1,1,2,2,2])

    def test_trap(self):
        self.assertEqual(self.sol.trap([0,1,0,2,1,0,1,3,2,1,2,1]), 6)
        self.assertEqual(self.sol.trap([4,2,0,3,2,5]), 9)
        self.assertEqual(self.sol.trap([0,0,0]), 0)
        self.assertEqual(self.sol.trap([3,0,3]), 3)
        self.assertEqual(self.sol.trap([1,2,3,4]), 0)
        self.assertEqual(self.sol.trap([4,3,2,1]), 0)

if __name__ == '__main__':
    unittest.main()
