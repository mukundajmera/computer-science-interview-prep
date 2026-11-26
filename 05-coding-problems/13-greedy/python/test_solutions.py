import unittest
from solutions import Solution

class TestGreedy(unittest.TestCase):
    def setUp(self):
        self.sol = Solution()

    def test_maxSubArray(self):
        self.assertEqual(self.sol.maxSubArray([-2,1,-3,4,-1,2,1,-5,4]), 6)
        self.assertEqual(self.sol.maxSubArray([1]), 1)
        self.assertEqual(self.sol.maxSubArray([5,4,-1,7,8]), 23)
        self.assertEqual(self.sol.maxSubArray([-1]), -1)
        self.assertEqual(self.sol.maxSubArray([-2,-1]), -1)
        self.assertEqual(self.sol.maxSubArray([2,1]), 3)

    def test_maxSubarraySumCircular(self):
        self.assertEqual(self.sol.maxSubarraySumCircular([1,-2,3,-2]), 3)
        self.assertEqual(self.sol.maxSubarraySumCircular([5,-3,5]), 10)
        self.assertEqual(self.sol.maxSubarraySumCircular([-3,-2,-3]), -2)
        self.assertEqual(self.sol.maxSubarraySumCircular([3,-1,2,-1]), 4)
        self.assertEqual(self.sol.maxSubarraySumCircular([3,-2,2,-3]), 3)
        self.assertEqual(self.sol.maxSubarraySumCircular([-2,-3,-1]), -1)

    def test_canJump(self):
        self.assertTrue(self.sol.canJump([2,3,1,1,4]))
        self.assertFalse(self.sol.canJump([3,2,1,0,4]))
        self.assertTrue(self.sol.canJump([0]))
        self.assertTrue(self.sol.canJump([1,2]))
        self.assertTrue(self.sol.canJump([2,0,0]))
        self.assertFalse(self.sol.canJump([0,2,3]))

    def test_jump(self):
        self.assertEqual(self.sol.jump([2,3,1,1,4]), 2)
        self.assertEqual(self.sol.jump([2,3,0,1,4]), 2)
        self.assertEqual(self.sol.jump([0]), 0)
        self.assertEqual(self.sol.jump([1,2]), 1)
        self.assertEqual(self.sol.jump([2,1,1,1,4]), 3)
        self.assertEqual(self.sol.jump([1,1,1,1]), 3)

    def test_canCompleteCircuit(self):
        self.assertEqual(self.sol.canCompleteCircuit([1,2,3,4,5], [3,4,5,1,2]), 3)
        self.assertEqual(self.sol.canCompleteCircuit([2,3,4], [3,4,3]), -1)
        self.assertEqual(self.sol.canCompleteCircuit([5,1,2,3,4], [4,4,1,5,1]), 4)
        self.assertEqual(self.sol.canCompleteCircuit([3,1,1], [1,2,2]), 0)
        self.assertEqual(self.sol.canCompleteCircuit([1,1,3], [2,2,1]), 2)
        self.assertEqual(self.sol.canCompleteCircuit([2], [2]), 0)

    def test_candy(self):
        self.assertEqual(self.sol.candy([1,0,2]), 5)
        self.assertEqual(self.sol.candy([1,2,2]), 4)
        self.assertEqual(self.sol.candy([1,3,2,2,1]), 7)
        self.assertEqual(self.sol.candy([1,2,87,87,87,2,1]), 13)
        self.assertEqual(self.sol.candy([1,2,3,4,5]), 15)
        self.assertEqual(self.sol.candy([5,4,3,2,1]), 15)

    def test_nextPermutation(self):
        nums = [1,2,3]
        self.sol.nextPermutation(nums)
        self.assertEqual(nums, [1,3,2])
        
        nums = [3,2,1]
        self.sol.nextPermutation(nums)
        self.assertEqual(nums, [1,2,3])
        
        nums = [1,1,5]
        self.sol.nextPermutation(nums)
        self.assertEqual(nums, [1,5,1])
        
        nums = [1,3,2]
        self.sol.nextPermutation(nums)
        self.assertEqual(nums, [2,1,3])
        
        nums = [1]
        self.sol.nextPermutation(nums)
        self.assertEqual(nums, [1])
        
        nums = [2,3,1]
        self.sol.nextPermutation(nums)
        self.assertEqual(nums, [3,1,2])

if __name__ == '__main__':
    unittest.main()
